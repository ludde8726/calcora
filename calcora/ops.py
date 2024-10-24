from __future__ import annotations
import math

from calcora.expression import Expr
from calcora.printing import Printer

class Var(Expr):
  def __init__(self, name: str) -> None:
    self.name = name
    super().__init__(name)
  
  def differentiate(self, var: Var) -> Expr: 
    return Const(1) if self == var else Const(0)
  
  def eval(self, **kwargs: Expr) -> float:
    if self.name in kwargs: return kwargs[self.name].eval()
    raise ValueError(f"Specified value for type var is required for evaluation, no value for var with name '{self.name}'")

  def __repr__(self) -> str: return Printer._print(self)
  
class Const(Expr):
  def __init__(self, x: float) -> None:
    assert x >= 0
    self.x = x
    super().__init__(x)
  
  def eval(self, **kwargs: Expr) -> float:
    return self.x
  
  def differentiate(self, var: Var) -> Expr: return Const(0)
  
  def __repr__(self) -> str: return Printer._print(self)
  
class Add(Expr):
  def __init__(self, x: Expr, y: Expr) -> None:
    self.x = x
    self.y = y
    super().__init__(x, y)

  def eval(self, **kwargs: Expr):
    return self.x.eval(**kwargs) + self.y.eval(**kwargs)
  
  def differentiate(self, var: Var) -> Expr:
    return Add(self.x.differentiate(var), self.y.differentiate(var))
  
  def __repr__(self) -> str: return Printer._print(self)

class Neg(Expr):
  def __init__(self, x: Expr) -> None:
    self.x = x
    super().__init__(x)

  def eval(self, **kwargs: Expr) -> float:
    return -self.x.eval(**kwargs)
  
  def differentiate(self, var: Var) -> Expr:
    return Neg(self.x.differentiate(var))
  
  def __repr__(self) -> str: return Printer._print(self)
  
class Mul(Expr):
  def __init__(self, x: Expr, y: Expr) -> None:
    self.x = x
    self.y = y
    super().__init__(x, y)

  def eval(self, **kwargs: Expr) -> float:
    return self.x.eval(**kwargs) * self.y.eval(**kwargs)
  
  def differentiate(self, var: Var) -> Expr:
    return Add(Mul(self.x.differentiate(var), self.y), Mul(self.x, self.y.differentiate(var)))
  
  def __repr__(self) -> str: return Printer._print(self)

class Log(Expr):
  def __init__(self, x: Expr, base: Expr = Const(10)) -> None:
    self.x = x
    self.base = base
    super().__init__(x, base)
  
  def eval(self, **kwargs: Expr) -> float:
    return math.log(self.x.eval(**kwargs), self.base.eval(**kwargs))
  
  def differentiate(self, var: Var) -> Expr:
    return Div(
              Sub(
                Div(Mul(self.x.differentiate(var), Ln(self.base)), self.x), 
                Div(Mul(self.base.differentiate(var), Ln(self.x)), self.base)), 
              Pow(Ln(self.base), Const(2))
            )
  
  def __repr__(self) -> str: return Printer._print(self)
  
class Pow(Expr):
  def __init__(self, x: Expr, y: Expr) -> None:
    self.x = x
    self.y = y
    super().__init__(x, y)

  def eval(self, **kwargs) -> float:
    return self.x.eval(**kwargs) ** self.y.eval(**kwargs)
  
  def differentiate(self, var: Var) -> Expr:
    return Add(Mul(Mul(self.y, Pow(self.x, Sub(self.y, Const(1)))), self.x.differentiate(var)),
               Mul(Mul(Pow(self.x, self.y), Ln(self.x)), self.y.differentiate(var)))
  
  def __repr__(self) -> str: return Printer._print(self)
  
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
  print(expr.eval(x=Const(.2)))