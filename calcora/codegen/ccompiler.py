from __future__ import annotations

from typing import Any, List, Optional, TypeGuard, Union
from typing import TYPE_CHECKING

import ctypes
import pathlib
import random
import string
import subprocess
import tempfile

from calcora.codegen.ccode import generate_expression_string, find_includes
from calcora.codegen.lambdify import find_expression_vars

if TYPE_CHECKING:
  from calcora.core.expression import Expr

class LongDoubleComplex(ctypes.Structure):
  _fields_ = [("real", ctypes.c_longdouble),
              ("imag", ctypes.c_longdouble)]
  
  @staticmethod
  def from_python(number: Union[float, complex]) -> LongDoubleComplex:
    if isinstance(number, (int, float)): return LongDoubleComplex(float(number), 0)
    elif isinstance(number, complex): return LongDoubleComplex(number.real, number.imag)
    else: raise TypeError(f"Cannot create LongDoubleComplex from type: {type(number)} only float or complex allowed!")

def is_expr(val: Any) -> TypeGuard[Expr]:
  return hasattr(val, '_eval')

class ClangProgram:
  def __init__(self, expression: Expr, name: Optional[str] = None) -> None:
    self.fxn_name : str = name or ''.join(random.choices(string.ascii_letters + '_', k=16))
    self.fxn_vars : List[str] = sorted(find_expression_vars(expression))
    self.includes : set[str] = find_includes(expression, assume_complex=True)
    self.fxn_code : str = ''.join(f'#include <{inc}>\n' for inc in self.includes)
    self.fxn_code += '\ntypedef struct {\n  long double real;\n  long double imag;\n} LongDoubleComplex;\n\n'
    self.fxn_code += f'void {self.fxn_name}(' + ', '.join(f'{"LongDoubleComplex"} {var}s' for var in self.fxn_vars) + ', LongDoubleComplex* res) {\n'
    for var in self.fxn_vars: self.fxn_code += f'  long double complex {var} = {var}s.real + {var}s.imag*I;\n'
    self.fxn_code += f'  long double complex result = {generate_expression_string(expression)};\n\n'
    self.fxn_code += f'  res->real = creal(result);\n'
    self.fxn_code += f'  res->imag = cimag(result);\n'
    self.fxn_code += '}'
    self.compiled : Optional[bytes] = None
    self.function : Optional[ctypes.CDLL]

  def compile(self) -> None:
    with tempfile.NamedTemporaryFile(delete=True) as output_file:
      arguments = f"clang -x c - -shared -O2 -o {output_file.name}".split()
      try: subprocess.check_output(args=arguments, input=self.fxn_code.encode("utf-8"), stderr=subprocess.PIPE)
      except subprocess.CalledProcessError as e: print(f"Error during compilation: {e.stderr.decode()}")
      self.compiled = pathlib.Path(output_file.name).read_bytes()
      self.function = ctypes.CDLL(str(output_file.name))
      getattr(self.function, self.fxn_name).argtypes = [LongDoubleComplex] * len(self.fxn_vars) + [ctypes.POINTER(LongDoubleComplex)]
      getattr(self.function, self.fxn_name).restype = None

  def _longdoublecomplexcast(self, *vals: Union[float, complex, Expr, LongDoubleComplex]) -> List[LongDoubleComplex]:
    res = []
    for val in vals:
      if is_expr(val): 
        value = val._eval()
        if value.imag: res.append(LongDoubleComplex.from_python(complex(value)))
        else: res.append(LongDoubleComplex.from_python(float(value)))
      elif isinstance(val, LongDoubleComplex): res.append(val)
      elif isinstance(val, (int, float, complex)): res.append(LongDoubleComplex.from_python(val))
      else: raise TypeError(f"Cannot create LongDoubleComplex from type: {type(val)}")
    return res
        
  def __call__(self, *args: Union[int, float, complex, Expr, LongDoubleComplex]) -> complex:
    new_args = self._longdoublecomplexcast(*args)
    if len(args) != len(self.fxn_vars): raise TypeError(f"Function requires {len(self.fxn_vars)} arguments ({','.join(self.fxn_vars)}) but {len(args)} were given")
    if self.compiled:
      res_var = LongDoubleComplex()
      getattr(self.function, self.fxn_name)(*new_args, ctypes.byref(res_var))
      print(type(self.function))
      return complex(res_var.real, res_var.imag)
    else: self.compile(); return self.__call__(*new_args)
