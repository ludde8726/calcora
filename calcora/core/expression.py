from __future__ import annotations

from typing import Tuple, Union, TYPE_CHECKING

from calcora.globals import BaseOps
from calcora.printing.printing import Printer
from calcora.types import CalcoraNumber, NumberLike
from calcora.core.registry import FunctionRegistry
from calcora.core.number import Number

from mpmath import mpf, mpc

if TYPE_CHECKING:
  from calcora.core.ops import Var

class Expr:
  def __init__(self, *args) -> None:
    self.args: Tuple[Expr, ...] = args
    assert self.__class__.__name__ in [op.value for op in BaseOps], f"Invalid op type {type(self.__class__.__name__)}"
    self.fxn: BaseOps = BaseOps(self.__class__.__name__)
    self.priority : int = 0 # higher equals higher priority, ex multiplication before addition, etc.

  def __eq__(self, other):
    return isinstance(other, Expr) and self.fxn == other.fxn and self.args == other.args
  
  @staticmethod
  def const_cast(x: Union[NumberLike, Expr]) -> Expr:
    if not isinstance(x, (int, float, mpc, mpf, str, Expr)): raise ValueError(f'Cannot cast type {type(x)} to type Number')
    if isinstance(x, Expr): return x
    return Number(x)
  
  def add(self, x: Union[NumberLike, Expr]) -> Expr:
    x = Expr.const_cast(x)
    return FunctionRegistry.get('Add')(self, x)

  def sub(self, x: Union[NumberLike, Expr]) -> Expr: 
    x = Expr.const_cast(x)
    return FunctionRegistry.get('Sub')(self, x)
  def mul(self, x: Union[NumberLike, Expr]) -> Expr: 
    x = Expr.const_cast(x)
    return FunctionRegistry.get('Mul')(self, x)
  def div(self, x: Union[NumberLike, Expr]) -> Expr:
    x = Expr.const_cast(x)
    return FunctionRegistry.get('Div')(self, x)
  def neg(self) -> Expr: return FunctionRegistry.get('Mul')(self)
  def pow(self, x: Union[NumberLike, Expr]) -> Expr: 
    x = Expr.const_cast(x)
    return FunctionRegistry.get('Pow')(self, x)
  def log(self, x: Union[NumberLike, Expr]) -> Expr: 
    x = Expr.const_cast(x)
    return FunctionRegistry.get('Log')(self, x)
  def ln(self) -> Expr: 
    return FunctionRegistry.get('Ln')(self)
  
  def __add__(self, x: Union[NumberLike, Expr]) -> Expr: return self.add(x)
  def __neg__(self) -> Expr: return self.neg()
  def __sub__(self, x: Union[NumberLike, Expr]) -> Expr: return self.sub(x)
  def __mul__(self, x: Union[NumberLike, Expr]) -> Expr: return self.mul(x)
  def __truediv__(self, x: Union[NumberLike, Expr]) -> Expr: return self.div(x)
  def __pow__(self, x: Union[NumberLike, Expr]) -> Expr: return self.pow(x)
  __radd__ = __add__
  __rmul__ = __mul__
  
  def __rsub__(self, x: Union[NumberLike, Expr]) -> Expr:
    x = Expr.const_cast(x)
    return FunctionRegistry.get('Sub')(x, self)
  
  def __rtruediv__(self, x: Union[NumberLike, Expr]) -> Expr:
    x = Expr.const_cast(x)
    return FunctionRegistry.get('Div')(x, self)

  def __rpow__(self, x: Union[NumberLike, Expr]) -> Expr:
    x = Expr.const_cast(x)
    return FunctionRegistry.get('Pow')(x, self)
  
  def differentiate(self, var: Var) -> Expr: raise NotImplementedError()

  def eval(self, **kwargs: Expr) -> CalcoraNumber: raise NotImplementedError()

  def _print_repr(self) -> str: raise NotImplementedError()

  def __repr__(self) -> str: 
    return Printer._print(self) 