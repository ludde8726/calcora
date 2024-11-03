from __future__ import annotations

from typing import Tuple, Union

import calcora as c
from calcora.globals import BaseOps
from calcora.printing.printing import Printer
from calcora.types import CalcoraNumber

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
    if not isinstance(x, Expr) and not isinstance(x, int) and not isinstance(x, float): raise ValueError(f'Cannot cast type {type(x)} to type {type(Const(0))}') # Note: This is not optional
    if isinstance(x, Expr): return x
    return c.Const(x)
  
  def add(self, x: Union[Expr, int, float]) -> Expr:
    x = Expr.const_cast(x)
    return c.Add(self, x)
  def sub(self, x: Union[Expr, int, float]) -> Expr: 
    x = Expr.const_cast(x)
    return c.Sub(self, x)
  def mul(self, x: Union[Expr, int, float]) -> Expr: 
    x = Expr.const_cast(x)
    return c.Mul(self, x)
  def div(self, x: Union[Expr, int, float]) -> Expr:
    x = Expr.const_cast(x)
    return c.Div(self, x)
  def neg(self) -> Expr: return c.Neg(self)
  def pow(self, x: Union[Expr, int, float]) -> Expr: 
    x = Expr.const_cast(x)
    return c.Pow(self, x)
  def log(self, x: Union[Expr, int, float]) -> Expr: 
    x = Expr.const_cast(x)
    return c.Log(self, x)
  def ln(self) -> Expr: 
    return c.Ln(self)
  
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
    return c.Sub(x, self)
  
  def __rtruediv__(self, x: Union[Expr, int, float]) -> Expr:
    x = Expr.const_cast(x)
    return c.Div(x, self)

  def __rpow__(self, x: Union[Expr, int, float]) -> Expr:
    x = Expr.const_cast(x)
    return c.Pow(x, self)
  
  def differentiate(self, var: c.Var) -> Expr: raise NotImplementedError()

  def eval(self, **kwargs: Expr) -> CalcoraNumber: raise NotImplementedError()

  def __repr__(self) -> str: 
    return Printer._print(self) 