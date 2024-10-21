from __future__ import annotations

from enum import auto, Enum
from typing import Any, Optional, Tuple, Union

import calcora.ops as Op

class BaseOps(Enum):
  @staticmethod
  def _generate_next_value_(name, start, count, last_values):
    return name
  
  # Special ops
  Const = auto()
  Var = auto()

  # Base ops
  Neg = auto()
  Add = auto()
  Mul = auto()
  Pow = auto()
  Log = auto()

  # NoOps
  AnyOp = auto()

class Expr:
  def __init__(self, *args) -> None:
    self.args: Tuple[Expr, ...] = args
    assert self.__class__.__name__ in [op.value for op in BaseOps], f"Invalid op type {type(self.__class__.__name__)}"
    self.fxn: BaseOps = BaseOps(self.__class__.__name__)

  def __eq__(self, other):
    return isinstance(other, Expr) and self.fxn == other.fxn and self.args == other.args
  
  @staticmethod
  def const_cast(x: Union[Expr, int, float]) -> Expr:
    if not isinstance(x, Expr) and not isinstance(x, int) and not isinstance(x, float): raise ValueError(f'Cannot cast type {type(x)} to type {type(Const(0))}') # Note: This is not optional
    if isinstance(x, Expr): return x
    return Op.Const(x)
  
  def add(self, x: Union[Expr, int, float]) -> Expr:
    x = Expr.const_cast(x)
    return Op.Add(self, x)
  def sub(self, x: Union[Expr, int, float]) -> Expr: 
    x = Expr.const_cast(x)
    return Op.Sub(self, x)
  def mul(self, x: Union[Expr, int, float]) -> Expr: 
    x = Expr.const_cast(x)
    return Op.Mul(self, x)
  def div(self, x: Union[Expr, int, float]) -> Expr:
    x = Expr.const_cast(x)
    return Op.Div(self, x)
  def neg(self) -> Expr: return Op.Neg(self)
  def pow(self, x: Union[Expr, int, float]) -> Expr: 
    x = Expr.const_cast(x)
    return Op.Pow(self, x)
  def log(self, x: Union[Expr, int, float]) -> Expr: 
    x = Expr.const_cast(x)
    return Op.Log(self, x)
  def ln(self) -> Expr: 
    return Op.Ln(self)
  
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
    return Op.Sub(x, self)
  
  def __rtruediv__(self, x: Union[Expr, int, float]) -> Expr:
    x = Expr.const_cast(x)
    return Op.Div(x, self)

  def __rpow__(self, x: Union[Expr, int, float]) -> Expr:
    x = Expr.const_cast(x)
    return Op.Pow(x, self)
  
  def differentiate(self, var: Op.Var) -> Expr: raise NotImplementedError() # type: ignore

  def eval(self, **kwargs: Expr) -> float: raise NotImplementedError()