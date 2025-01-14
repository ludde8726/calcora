from __future__ import annotations

from typing import Iterable, Optional
from typing import TYPE_CHECKING

import random
import string

from calcora.core.stringops import *
from calcora.utils import is_op_type
from calcora.globals import BaseOps
from calcora.codegen.lambdify import find_expression_vars

if TYPE_CHECKING:
  from calcora.core.expression import Expr
  from calcora.core.ops import Add, Complex, Const, Constant, Cos, Log, Mul, Neg, Pow, Sin, Var

def find_includes(expression: Expr, assume_complex: bool = True) -> set[str]:
  includes : set[str] = set()
  def inner(expression: Expr) -> None:
    if expression.fxn in [BaseOps.Pow, BaseOps.Log, BaseOps.Sin, BaseOps.Cos]: includes.add('math.h')
    elif expression.fxn == BaseOps.Complex: includes.add('complex.h')
    if not (is_op_type(expression, Const) or is_op_type(expression, Constant) or is_op_type(expression, Var)):
      for arg in expression.args: inner(arg)
  if assume_complex: includes.add('complex.h')
  inner(expression)
  return includes

C_CONSTANTS_MAP = {
  'e': 'M_E',
  'π': 'M_PI'
}

def generate_expression_string(expression: Expr) -> str:
  if is_op_type(expression, Var): return f'{expression.name}'
  elif is_op_type(expression, Const): return f'{expression.x}'
  elif is_op_type(expression, Constant): return f'{C_CONSTANTS_MAP[expression.name]}'
  elif is_op_type(expression, Complex): 
    real = generate_expression_string(expression.real)
    imag = generate_expression_string(expression.imag)
    return f'({real} + {imag}*I)'
  elif is_op_type(expression, Add):
    x = generate_expression_string(expression.x)
    y = generate_expression_string(expression.y)
    return f'({x}+{y})'
  elif is_op_type(expression, Neg):
    x = generate_expression_string(expression.x)
    return f'(-{x})'
  elif is_op_type(expression, Mul):
    x = generate_expression_string(expression.x)
    y = generate_expression_string(expression.y)
    return f'({x}*{y})'
  elif is_op_type(expression, Log):
    x = generate_expression_string(expression.x)
    base = generate_expression_string(expression.base)
    return f'(clog({x})/clog({base}))'
  elif is_op_type(expression, Pow):
    x = generate_expression_string(expression.x)
    y = generate_expression_string(expression.y)
    return f'cpow({x}, {y})'
  elif is_op_type(expression, Sin): 
    x = generate_expression_string(expression.x)
    return f'csin({x})'
  elif is_op_type(expression, Cos):
    x = generate_expression_string(expression.x)
    return f'ccos({x})'
  else: raise TypeError(f'Invalid op {type(expression)} cannot be converted to c code!')

def c_function(expression: Expr, name: Optional[str] = None, automatic_vars: bool = True, vars: Optional[Iterable[str]] = None, custom_type: Optional[str] = None) -> str:
  if vars and automatic_vars: raise RuntimeError("Both automatic vars and specified vars cannot be selected!")
  includes = ''.join(f'#include <{inc}>\n' for inc in find_includes(expression, assume_complex=True))
  expression_str = generate_expression_string(expression)
  fxn_name = name or ''.join(random.choices(string.ascii_letters + '_', k=16))
  vars = find_expression_vars(expression) if automatic_vars else vars
  res_vars = ', '.join(f'{custom_type or "long double complex*"} {var}' for var in vars) if vars else ''
  return f"""
{includes}
{custom_type or 'long double complex'} {fxn_name}({res_vars}) {{
  return {expression_str};
}}"""