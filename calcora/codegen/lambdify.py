from __future__ import annotations

from typing import Any, Callable, Dict, Generic, Iterable, Literal, Optional, overload, Union, Protocol, TypeVar
from typing import TYPE_CHECKING

from enum import Enum, auto

from calcora.core.stringops import *
from calcora.utils import is_op_type
from calcora.types import CalcoraNumber

from mpmath import mpf, mpc

if TYPE_CHECKING:
  from calcora.core.expression import Expr
  from calcora.core.ops import Add, Complex, Const, Constant, Cos, Log, Mul, Neg, Pow, Sin, Var
  import numpy
  from numpy.typing import NDArray
  PYTHON_CONVERT_TYPES = Union[int, str, float, complex, mpf, mpc]
  MPMATH_CONVERT_TYPES = Union[int, str, float, complex, mpf, mpc]
  NUMPY_CONVERT_TYPES = Union[numpy.floating, numpy.integer, numpy.cdouble, NDArray[numpy.floating], NDArray[numpy.cdouble], float, int, complex, str]

class Backend(Enum):
  PYTHON = auto()
  MPMATH = auto()

def find_expression_vars(expression: Expr) -> set[str]:
  found_vars = set()
  def inner(expression: Expr) -> None:
    if is_op_type(expression, Var): found_vars.add(expression.name)
    elif not (is_op_type(expression, Const) or is_op_type(expression, Constant)):
      for arg in expression.args: inner(arg)
  inner(expression)
  return found_vars

def generate_lambda_string_wrapper(expression: Expr, function_map: Dict[str, str]) -> str:
  if is_op_type(expression, Var): return f'{expression.name}' if not "var" in function_map else f'{function_map["var"]}({expression.name})'
  elif is_op_type(expression, Const): return f'{function_map["const"]}({expression.x})'
  elif is_op_type(expression, Constant): return function_map[expression.name]
  elif is_op_type(expression, Complex): 
    real = generate_lambda_string_wrapper(expression.real, function_map)
    imag = generate_lambda_string_wrapper(expression.imag, function_map)
    return f'{function_map["complex"]}({real}, {imag})'
  elif is_op_type(expression, Add):
    x = generate_lambda_string_wrapper(expression.x, function_map)
    y = generate_lambda_string_wrapper(expression.y, function_map)
    return f'({x}+{y})'
  elif is_op_type(expression, Neg):
    x = generate_lambda_string_wrapper(expression.x, function_map)
    return f'(-{x})'
  elif is_op_type(expression, Mul):
    x = generate_lambda_string_wrapper(expression.x, function_map)
    y = generate_lambda_string_wrapper(expression.y, function_map)
    return f'({x}*{y})'
  elif is_op_type(expression, Log):
    x = generate_lambda_string_wrapper(expression.x, function_map)
    base = generate_lambda_string_wrapper(expression.base, function_map)
    if function_map['log'] == 'numpy.emath.logn': return f'{function_map["log"]}({base}, {x})' # Hack since numpy log takes arguments in different order
    return f'{function_map["log"]}({x}, {base})'
  elif is_op_type(expression, Pow):
    x = generate_lambda_string_wrapper(expression.x, function_map)
    y = generate_lambda_string_wrapper(expression.y, function_map)
    return f'({x}**{y})' if not "pow" in function_map else f'{function_map["pow"]}({x}, {y})'
  elif is_op_type(expression, Sin): 
    x = generate_lambda_string_wrapper(expression.x, function_map)
    return f'{function_map["sin"]}({x})'
  elif is_op_type(expression, Cos):
    x = generate_lambda_string_wrapper(expression.x, function_map)
    return f'{function_map["cos"]}({x})'
  else: raise TypeError(f'Invalid op {type(expression)} cannot be lambdified!')

python_function_map = {
  'const': 'float',
  'complex': 'complex',
  'log': 'math.log',
  'sin': 'math.sin',
  'cos': 'math.cos',
  'e': 'math.e',
  'π': 'math.pi'
}

mpmath_function_map = {
  'const': 'mpmath.mpf',
  'complex': 'mpmath.mpc',
  'log': 'mpmath.log',
  'sin': 'mpmath.sin',
  'cos': 'mpmath.cos',
  'e': 'mpmath.e',
  'π': 'mpmath.pi'
}

numpy_function_map = {
  'const': 'numpy.float64',
  'complex': 'numpy.complex128',
  'log': 'numpy.emath.logn',
  'sin': 'numpy.sin',
  'cos': 'numpy.cos',
  'e': 'numpy.e',
  'π': 'numpy.pi'
}

def global_import(name: str) -> None: globals()[name] = __import__(name)

@overload
def convert_type(value: PYTHON_CONVERT_TYPES, to: Literal['python']) -> Union[float, complex]: ...
@overload
def convert_type(value: MPMATH_CONVERT_TYPES, to: Literal['mpmath']) -> CalcoraNumber: ...
@overload
def convert_type(value: NUMPY_CONVERT_TYPES, to: Literal['numpy']) -> Union[numpy.float64, numpy.complex128, NDArray[numpy.float64 | numpy.complex128]]: ...

def convert_type(value: Any, to: str) -> Any:
  if to == 'numpy':
    if not 'numpy' in globals(): global_import('numpy')
    if isinstance(value, (numpy.floating, numpy.integer, numpy.ndarray, float, int, complex, str)):
      if isinstance(value, str):
        x = numpy.complex128(''.join(value.split()).replace('i', 'j'))
        return x.real if not x.imag else x
      return numpy.float64(value) if isinstance(value, (numpy.floating, float, int)) else numpy.complex128(value) if isinstance(value, (complex, numpy.integer)) else value
    else: raise ValueError("Invalid type for 'numpy' conversion")
  elif to == 'python':
    if isinstance(value, (int, str, float, complex, mpc, mpf)):
      if isinstance(value, str): return complex(''.join(value.split()).replace('i', 'j')).real if not complex(''.join(value.split()).replace('i', 'j')).imag else complex(''.join(value.split()).replace('i', 'j'))
      if isinstance(value, (complex, mpc, str)): return complex(value).real if not complex(value).imag else complex(value)
      else: return float(value)
    else: raise ValueError("Invalid type for 'python' conversion")
  elif to == 'mpmath':
    if isinstance(value, (int, str, float, complex, mpc, mpf)): return mpc(value)
    else: raise ValueError("Invalid type for 'mpmath' conversion")
  else: raise ValueError("Invalid 'to' argument. Must be 'python', 'mpmath', or 'numpy'.")

T = TypeVar('T')
class MpmathCallable(Protocol):
  def __call__(self, *args: CalcoraNumber, **kwargs: CalcoraNumber) -> CalcoraNumber: ...
class PythonCallable(Protocol):
  def __call__(self, *args: Union[float, complex], **kwargs: Union[float, complex]) -> Union[float, complex]: ...
class NumpyCallable(Protocol):
  def __call__(self, *args: Any, **kwargs: Any) -> Union[numpy.float64, numpy.complex128, NDArray[numpy.float64 | numpy.complex128]]: ...

class TypesafeMpmathCallable(Protocol):
  def __call__(self, *args: MPMATH_CONVERT_TYPES, **kwargs: MPMATH_CONVERT_TYPES) -> CalcoraNumber: ...
class TypesafePythonCallable(Protocol):
  def __call__(self, *args: PYTHON_CONVERT_TYPES, **kwargs: PYTHON_CONVERT_TYPES) -> Union[float, complex]: ...
class TypesafeNumpyCallable(Protocol):
  def __call__(self, *args: NUMPY_CONVERT_TYPES, **kwargs: NUMPY_CONVERT_TYPES) -> Union[numpy.float64, numpy.complex128, NDArray[numpy.float64 | numpy.complex128]]: ...

@overload
def lambdify(expression: Expr, backend: Literal["mpmath"], type_conversion: Literal[False] = ..., automatic_vars: bool = True, vars: Optional[Iterable[str]] = None) -> MpmathCallable: ... 
@overload
def lambdify(expression: Expr, backend: Literal["python"], type_conversion: Literal[False] = ..., automatic_vars: bool = True, vars: Optional[Iterable[str]] = None) -> PythonCallable: ... 
@overload
def lambdify(expression: Expr, backend: Literal["numpy"], type_conversion: Literal[False] = ..., automatic_vars: bool = True, vars: Optional[Iterable[str]] = None) -> NumpyCallable: ...

@overload
def lambdify(expression: Expr, backend: Literal["mpmath"], type_conversion: Literal[True], automatic_vars: bool = True, vars: Optional[Iterable[str]] = None) -> TypesafeMpmathCallable: ... 
@overload
def lambdify(expression: Expr, backend: Literal["python"], type_conversion: Literal[True], automatic_vars: bool = True, vars: Optional[Iterable[str]] = None) -> TypesafePythonCallable: ...
@overload
def lambdify(expression: Expr, backend: Literal["numpy"], type_conversion: Literal[True], automatic_vars: bool = True, vars: Optional[Iterable[str]] = None) -> TypesafeNumpyCallable: ...

def lambdify(expression: Expr, backend: Literal["mpmath", "numpy", "python"] = "mpmath", type_conversion: Literal[True, False] = False, automatic_vars: bool = True, vars: Optional[Iterable[str]] = None) -> Union[MpmathCallable, PythonCallable, NumpyCallable, TypesafeMpmathCallable, TypesafePythonCallable, TypesafeNumpyCallable]:
  if vars and automatic_vars: raise RuntimeError("Both automatic vars and specified vars cannot be selected!")
  if backend == "mpmath": 
    global_import('mpmath')
    lambda_map = mpmath_function_map
  elif backend == "python": 
    global_import('math')
    lambda_map = python_function_map
  elif backend == "numpy": 
    global_import('numpy')
    lambda_map = numpy_function_map
  else: raise ValueError(f"Invalid backend {backend}, must be mpmath, python or numpy")
  lambda_string = generate_lambda_string_wrapper(expression, lambda_map)
  if automatic_vars: vars = find_expression_vars(expression)
  if vars: vars = ",".join(sorted(vars))
  if type_conversion and vars: lambda_fxn : Callable[..., Union[MpmathCallable, PythonCallable, NumpyCallable]] = eval(f"lambda {vars}: (lambda {vars}: {lambda_string})(**{{var:convert_type(var_val, '{backend}') for var, var_val in zip('{vars}'.split(','), [{vars}])}})")
  else: lambda_fxn = eval(f'lambda {vars}: {lambda_string}') if vars else eval(f'lambda: {lambda_string}')
  return lambda_fxn

def string_lambda(expression: Expr, backend: Literal["mpmath", "numpy", "python"] = "mpmath", automatic_vars: bool = True, vars: Optional[Iterable[str]] = None) -> str:
  if vars and automatic_vars: raise RuntimeError("Both automatic vars and specified vars cannot be selected!")
  if backend == 'mpmath': lambda_map = mpmath_function_map
  elif backend == 'python': lambda_map = python_function_map
  elif backend == 'numpy': lambda_map = numpy_function_map
  else: raise ValueError(f"Invalid backend {backend}, must be mpmath, python or numpy")
  lambda_string = generate_lambda_string_wrapper(expression, lambda_map)
  if automatic_vars: vars = find_expression_vars(expression)
  if vars: vars = ",".join(sorted(vars))
  return f'lambda {vars}: {lambda_string}' if vars else f'lambda: {lambda_string}'