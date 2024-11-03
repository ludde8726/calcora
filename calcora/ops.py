from __future__ import annotations

import math
from typing import Union

from calcora.expression import Expr
from calcora.types import NumberLike, CalcoraNumber

from mpmath import mpf, mpc, log

class Var(Expr):
  def __init__(self, name: str) -> None:
    self.name = name
    super().__init__(name)
    self.priority = 999
  
  def differentiate(self, var: Var) -> Expr: 
    return Const(1) if self == var else Const(0)
  
  def eval(self, **kwargs: Expr) -> CalcoraNumber:
    if self.name in kwargs: return kwargs[self.name].eval()
    raise ValueError(f"Specified value for type var is required for evaluation, no value for var with name '{self.name}'")
  
class Const(Expr):
  def __init__(self, x: NumberLike) -> None:
    if isinstance(x, (int, float, str, complex)): self.x = mpc(x)
    elif isinstance(x, (mpf, mpc)): self.x = x
    else: raise TypeError("Const must be initialized with an int, float, str, complex, mpf, or mpc.")
    super().__init__(self.x)
    self.priority = 999
  
  def eval(self, **kwargs: Expr) -> CalcoraNumber: return self.x
  
  def differentiate(self, var: Var) -> Expr: return Const(0)
  
class Add(Expr):
  def __init__(self, x: Expr, y: Expr) -> None:
    self.x = x
    self.y = y
    super().__init__(x, y)
    self.priority = 1

  def eval(self, **kwargs: Expr) -> CalcoraNumber:
    return self.x.eval(**kwargs) + self.y.eval(**kwargs)
  
  def differentiate(self, var: Var) -> Expr:
    return Add(self.x.differentiate(var), self.y.differentiate(var))

class Neg(Expr):
  def __init__(self, x: Expr) -> None:
    self.x = x
    super().__init__(x)
    self.priority = 0

  def eval(self, **kwargs: Expr) -> CalcoraNumber:
    return -self.x.eval(**kwargs)
  
  def differentiate(self, var: Var) -> Expr:
    return Neg(self.x.differentiate(var))
  
class Mul(Expr):
  def __init__(self, x: Expr, y: Expr) -> None:
    self.x = x
    self.y = y
    super().__init__(x, y)
    self.priority = 2

  def eval(self, **kwargs: Expr) -> CalcoraNumber:
    return self.x.eval(**kwargs) * self.y.eval(**kwargs)
  
  def differentiate(self, var: Var) -> Expr:
    return Add(Mul(self.x.differentiate(var), self.y), Mul(self.x, self.y.differentiate(var)))

class Log(Expr):
  def __init__(self, x: Expr, base: Expr = Const(10)) -> None:
    self.x = x
    self.base = base
    super().__init__(x, base)
    self.priority = 4
  
  def eval(self, **kwargs: Expr) -> CalcoraNumber: 
    return math.log(self.x.eval(**kwargs), self.base.eval(**kwargs))
  
  def differentiate(self, var: Var) -> Expr:
    return Div(
              Sub(
                Div(Mul(self.x.differentiate(var), Ln(self.base)), self.x), 
                Div(Mul(self.base.differentiate(var), Ln(self.x)), self.base)), 
              Pow(Ln(self.base), Const(2))
            )
  
class Pow(Expr):
  def __init__(self, x: Expr, y: Expr) -> None:
    self.x = x
    self.y = y
    super().__init__(x, y)
    self.priority = 3

  def eval(self, **kwargs) -> CalcoraNumber:
    return self.x.eval(**kwargs) ** self.y.eval(**kwargs)
  
  def differentiate(self, var: Var) -> Expr:
    return Add(Mul(Mul(self.y, Pow(self.x, Sub(self.y, Const(1)))), self.x.differentiate(var)),
               Mul(Mul(Pow(self.x, self.y), Ln(self.x)), self.y.differentiate(var)))
  
class Div(Expr):
  def __new__(cls, x: Expr, y: Expr) -> Expr:
    if y == Const(0): raise ZeroDivisionError('Denominator cannot be zero!')
    return Mul(x, Pow(y, Neg(Const(1))))
  
class Sub(Expr):
  def __new__(cls, x: Expr, y: Expr) -> Expr:
    return Add(x, Neg(y))
  
class Ln(Expr):
  def __new__(cls, x: Expr) -> Expr:
    return Log(x, Const(math.e))   
  
class AnyOp(Expr):
  def __init__(self, match: bool = False, name: str="x", assert_const_like=False) -> None:
    self.match = match
    self.name = name
    self.assert_const_like = assert_const_like
    super().__init__()

if __name__ == "__main__":
  x = Var('x')
  expr = x / 2 + 4
  print(Const(expr.eval(x=Const(1j))))