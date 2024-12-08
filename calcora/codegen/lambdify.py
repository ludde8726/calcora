from __future__ import annotations

from typing import Callable, Dict, Iterable, Literal, Optional, overload, Union
from typing import TYPE_CHECKING

from enum import Enum, auto

from calcora.core.stringops import *
from calcora.utils import is_op_type
from calcora.types import CalcoraNumber

if TYPE_CHECKING:
  from calcora.core.expression import Expr
  from calcora.core.ops import Add, Complex, Const, Constant, Cos, Log, Mul, Neg, Pow, Sin, Var

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
  if is_op_type(expression, Var): return f'{expression.name}'
  elif is_op_type(expression, Const): return f'{expression.x}'
  elif is_op_type(expression, Constant): return f''
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
  'complex': 'complex',
  'log': 'math.log',
  'sin': 'math.sin',
  'cos': 'math.cos',
}

mpmath_function_map = {
  'complex': 'mpmath.mpc',
  'log': 'mpmath.log',
  'sin': 'mpmath.sin',
  'cos': 'mpmath.cos',
}

def global_import(name: str) -> None: globals()[name] = __import__(name)

@overload
def lambdify(expression: Expr, backend: Literal["mpmath"] = "mpmath", automatic_vars: bool = True, vars: Optional[Iterable[str]] = None) -> Callable[..., CalcoraNumber]: ... 
@overload
def lambdify(expression: Expr, backend: Literal["python"] = "python", automatic_vars: bool = True, vars: Optional[Iterable[str]] = None) -> Callable[..., float]: ...

def lambdify(expression: Expr, backend: Literal["mpmath", "numpy", "python"] = "mpmath", automatic_vars: bool = True, vars: Optional[Iterable[str]] = None) -> Callable[..., Union[float, CalcoraNumber]]:
  if vars and automatic_vars: raise RuntimeError("Both automatic vars and specified vars cannot be selected!")
  lambda_map = mpmath_function_map if backend == "mpmath" else python_function_map
  if backend == "mpmath": global_import('mpmath')
  elif backend == "python": global_import('math')
  else: raise ValueError(f"Invalid backend {backend}, must be mpmath, python or numpy")
  lambda_string = generate_lambda_string_wrapper(expression, lambda_map)
  if automatic_vars: vars = find_expression_vars(expression)
  if vars: vars = ",".join(sorted(vars))
  lambda_fxn : Callable[..., Union[float, CalcoraNumber]] = eval(f'lambda {vars}: {lambda_string}') if vars else eval(f'lambda: {lambda_string}')
  return lambda_fxn