from __future__ import annotations

from typing import Tuple, Union, TYPE_CHECKING

from calcora.globals import BaseOps
from calcora.printing.printing import Printer
from calcora.types import CalcoraNumber
from calcora.core.registry import FunctionRegistry

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
  def const_cast(x: Union[Expr, int, float]) -> Expr:
    if not isinstance(x, Expr) and not isinstance(x, int) and not isinstance(x, float): raise ValueError(f'Cannot cast type {type(x)} to type Const') # Note: This is not optional
    if isinstance(x, Expr): return x
    return FunctionRegistry.get('Const')(x)
  
  def add(self, x: Union[Expr, int, float]) -> Expr:
    x = Expr.const_cast(x)
    return FunctionRegistry.get('Add')(self, x)

  def sub(self, x: Union[Expr, int, float]) -> Expr: 
    x = Expr.const_cast(x)
    return FunctionRegistry.get('Sub')(self, x)
  def mul(self, x: Union[Expr, int, float]) -> Expr: 
    x = Expr.const_cast(x)
    return FunctionRegistry.get('Mul')(self, x)
  def div(self, x: Union[Expr, int, float]) -> Expr:
    x = Expr.const_cast(x)
    return FunctionRegistry.get('Div')(self, x)
  def neg(self) -> Expr: return FunctionRegistry.get('Mul')(self)
  def pow(self, x: Union[Expr, int, float]) -> Expr: 
    x = Expr.const_cast(x)
    return FunctionRegistry.get('Pow')(self, x)
  def log(self, x: Union[Expr, int, float]) -> Expr: 
    x = Expr.const_cast(x)
    return FunctionRegistry.get('Log')(self, x)
  def ln(self) -> Expr: 
    return FunctionRegistry.get('Ln')(self)
  
  def __add__(self, x: Union[Expr, int, float]) -> Expr: return self.add(x)
  def __neg__(self) -> Expr: return self.neg()
  def __sub__(self, x: Union[Expr, int, float]) -> Expr: return self.sub(x)
  def __mul__(self, x: Union[Expr, int, float]) -> Expr: return self.mul(x)
  def __truediv__(self, x: Union[Expr, int, float]) -> Expr: return self.div(x)
  def __pow__(self, x: Union[Expr, int, float]) -> Expr: return self.pow(x)
  __radd__ = __add__
  __rmul__ = __mul__
  
  def __rsub__(self, x: Union[Expr, int, float]) -> Expr:
    x = Expr.const_cast(x)
    return FunctionRegistry.get('Sub')(x, self)
  
  def __rtruediv__(self, x: Union[Expr, int, float]) -> Expr:
    x = Expr.const_cast(x)
    return FunctionRegistry.get('Div')(x, self)

  def __rpow__(self, x: Union[Expr, int, float]) -> Expr:
    x = Expr.const_cast(x)
    return FunctionRegistry.get('Pow')(x, self)
  
  def differentiate(self, var: Var) -> Expr: raise NotImplementedError()

  def eval(self, **kwargs: Expr) -> CalcoraNumber: raise NotImplementedError()

  def _print_repr(self) -> str: raise NotImplementedError()

  def __repr__(self) -> str: 
    return Printer._print(self) 