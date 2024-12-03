from __future__ import annotations

from typing import Callable, Optional
from typing import TYPE_CHECKING

import math
from enum import Enum, auto

from calcora.core.stringops import *
from calcora.utils import is_op_type

if TYPE_CHECKING:
  from calcora.core.expression import Expr
  from calcora.core.ops import Add, Complex, Const, Constant, Cos, Log, Mul, Neg, Pow, Sin, Var

class Backend(Enum):
  PYTHON = auto()
  MPMATH = auto()

class Lamdbdify:
  def __init__(self, expression: Expr, backend: Backend = Backend.PYTHON, instant_eval: bool = True) -> None:
    self.expression : Expr = expression
    self.backend = backend
    self.instant_eval = instant_eval
    self._lambda : Optional[Callable] = None
    if self.instant_eval: self._lambda = self._generate()
  
  def _generate(self) -> Callable:
    lambda_string = self._generate_lambda_string(self.expression)
    lambda_vars = ",".join(sorted(Lamdbdify._find_vars(self.expression)))
    print(lambda_string)
    return_lambda : Callable = eval(f'lambda {lambda_vars}: {lambda_string}')
    return return_lambda
  
  def _generate_lambda_string(self, expression: Expr) -> str:
    if is_op_type(expression, Var): return f'{expression.name}'
    elif is_op_type(expression, Const): return f'{expression.x}'
    elif is_op_type(expression, Constant): return f''
    elif is_op_type(expression, Complex): 
      real = self._generate_lambda_string(expression.real)
      imag = self._generate_lambda_string(expression.imag)
      return f'{expression.real}+{expression.imag}j'
    elif is_op_type(expression, Add):
      x = self._generate_lambda_string(expression.x)
      y = self._generate_lambda_string(expression.y)
      return f'({x}+{y})'
    elif is_op_type(expression, Neg):
      x = self._generate_lambda_string(expression.x)
      return f'(-{x})'
    elif is_op_type(expression, Mul):
      x = self._generate_lambda_string(expression.x)
      y = self._generate_lambda_string(expression.y)
      return f'({x}*{y})'
    elif is_op_type(expression, Log):
      x = self._generate_lambda_string(expression.x)
      base = self._generate_lambda_string(expression.base)
      return f'math.log({x}, {base})'
    elif is_op_type(expression, Pow):
      x = self._generate_lambda_string(expression.x)
      y = self._generate_lambda_string(expression.y)
      return f'({x}**{y})'
    elif is_op_type(expression, Sin): 
      x = self._generate_lambda_string(expression.x)
      return f'math.sin({x})'
    elif is_op_type(expression, Cos):
      x = self._generate_lambda_string(expression.x)
      return f'math.cos({x})'
    else: raise TypeError(f'Invalid op {type(expression)} cannot be lambdified!')
  
  @staticmethod
  def _find_vars(expression: Expr) -> set[str]:
    found_vars = set()
    def inner(expression: Expr):
      if is_op_type(expression, Var): found_vars.add(expression.name)
      elif not (is_op_type(expression, Const) or is_op_type(expression, Constant)):
        for arg in expression.args: inner(arg)
    inner(expression)
    return found_vars
    