from __future__ import annotations

import math

from calcora.core.expression import Expr
from calcora.core.registry import FunctionRegistry
from calcora.types import NumberLike, CalcoraNumber, RealNumberLike

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
  
  def _print_repr(self) -> str:
    return f'{self.name}'
  
class Const(Expr):
  def __init__(self, x: RealNumberLike) -> None:
    if isinstance(x, (int, float, str)): self.x = mpf(x)
    elif isinstance(x, mpf): self.x = x
    else: raise TypeError("Const must be initialized with an int, float, str, or mpf.")
    if not (self.x.real >= 0 and self.x.imag == 0): raise ValueError("Const value must be a real, positive value!")
    super().__init__(self.x)
    self.priority = 999
  
  def eval(self, **kwargs: Expr) -> CalcoraNumber: return self.x
  
  def differentiate(self, var: Var) -> Expr: return Const(0)

  def _print_repr(self) -> str:
    return f'{self.x}'

class Complex(Expr):
  def __init__(self, real: Expr, imag: Expr) -> None:
    self.real = real
    self.imag = imag
    super().__init__(real, imag)
  
  def eval(self, **kwargs: Expr) -> CalcoraNumber: 
    return mpc(real=self.real.eval(**kwargs), imag=self.imag.eval(**kwargs))
  
  def differentiate(self, var: Var) -> Expr:
    if self.imag != 0: raise ValueError('Cannot differentiate imaginary numbers (for now)')
    return Const(0)
  
  def _print_repr(self) -> str:
    return f'{self.real._print_repr()} + {self.imag._print_repr()}i' if not isinstance(self.imag, Neg) else f'{self.real._print_repr()} - {self.imag.x._print_repr()}i'

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
  
  def _print_repr(self) -> str:
    x = self.x._print_repr()
    y = self.y._print_repr()
    if self.x.priority < self.priority: x = f'({self.x})'
    if self.y.priority < self.priority: y = f'({self.y})'
    return f'{x} + {y}'

class Neg(Expr):
  def __init__(self, x: Expr) -> None:
    self.x = x
    super().__init__(x)
    self.priority = 0

  def eval(self, **kwargs: Expr) -> CalcoraNumber:
    return -self.x.eval(**kwargs)
  
  def differentiate(self, var: Var) -> Expr:
    return Neg(self.x.differentiate(var))
  
  def _print_repr(self) -> str:
    x = self.x._print_repr()
    if not (isinstance(self.x, Const) or isinstance(self.x, Var)): x = f'({x})'
    return f'-{x}'
  
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
  
  def _print_repr(self) -> str:
    x = self.x._print_repr()
    y = self.y._print_repr()
    if self.x.priority < self.priority: x = f'({x})'
    if self.y.priority < self.priority: y = f'({y})'
    return f'{x}*{y}'

class Log(Expr):
  def __init__(self, x: Expr, base: Expr = Const(10)) -> None:
    self.x = x
    self.base = base
    super().__init__(x, base)
    self.priority = 4
  
  def eval(self, **kwargs: Expr) -> CalcoraNumber: 
    return log(self.x.eval(**kwargs), self.base.eval(**kwargs))
  
  def differentiate(self, var: Var) -> Expr:
    return Div(
              Sub(
                Div(Mul(self.x.differentiate(var), Ln(self.base)), self.x), 
                Div(Mul(self.base.differentiate(var), Ln(self.x)), self.base)), 
              Pow(Ln(self.base), Const(2))
            )
  
  def _print_repr(self) -> str:
    x = self.x._print_repr()
    base = self.base._print_repr()
    return f'Log_{base}({x})'

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
  
  def _print_repr(self) -> str:
    x = self.x._print_repr()
    y = self.y._print_repr()
    if self.x.priority < self.priority or isinstance(self.x, Pow): x = f'({x})'
    if self.y.priority < self.priority or isinstance(self.y, Pow): y = f'({y})'
    return f'{x}^{y}'
  
class Div:
  def __new__(cls, x: Expr, y: Expr) -> Expr:
    if y == Const(0): raise ZeroDivisionError('Denominator cannot be zero!')
    return Mul(x, Pow(y, Neg(Const(1))))
  
class Sub:
  def __new__(cls, x: Expr, y: Expr) -> Expr:
    return Add(x, Neg(y))
  
class Ln:
  def __new__(cls, x: Expr) -> Expr:
    return Log(x, Const(math.e))

class AnyOp(Expr):
  def __init__(self, match: bool = False, name: str="x", assert_const_like=False) -> None:
    self.match = match
    self.name = name
    self.assert_const_like = assert_const_like
    super().__init__()

FunctionRegistry.register(Var)
FunctionRegistry.register(Const)
FunctionRegistry.register(Complex)
FunctionRegistry.register(Add)
FunctionRegistry.register(Neg)
FunctionRegistry.register(Mul)
FunctionRegistry.register(Log)
FunctionRegistry.register(Pow)
FunctionRegistry.register(AnyOp)

FunctionRegistry.register(Div)
FunctionRegistry.register(Sub)
FunctionRegistry.register(Ln)

if __name__ == "__main__":
  x = Var('x')
  expr = x / 2 + 4
  print(expr)
  print(Const(expr.eval(x=Const(1))))