from __future__ import annotations

from typing import TYPE_CHECKING

from calcora.types import CalcoraNumber, RealNumberLike

from calcora.core.expression import Expr
from calcora.core.registry import ConstantRegistry, FunctionRegistry

from mpmath import mpf, mpc, log, sin, cos

if TYPE_CHECKING:
  from mpmath.ctx_mp_python import _constant

class Var(Expr):
  def __init__(self, name: str) -> None:
    self.name = name
    super().__init__(name)
    self.priority = 999
  
  def differentiate(self, var: Var) -> Expr: 
    return Const(1) if self == var else Const(0)
  
  def _eval(self, **kwargs: Expr) -> CalcoraNumber:
    if self.name in kwargs: return kwargs[self.name]._eval()
    raise ValueError(f"Specified value for type var is required for evaluation, no value for var with name '{self.name}'")
  
  def _print_repr(self) -> str: return f'{self.name}'
  def _print_latex(self) -> str: return f'{self.name}'
  
class Const(Expr):
  def __init__(self, x: RealNumberLike) -> None:
    if isinstance(x, (int, float, str)): self.x = mpf(x)
    elif isinstance(x, mpf): self.x = x
    else: raise TypeError("Const must be initialized with an int, float, str, or mpf.")
    if not (self.x.real >= 0 and self.x.imag == 0): raise ValueError("Const value must be a real, positive value!")
    super().__init__(self.x)
    self.priority = 999
  
  def _eval(self, **kwargs: Expr) -> CalcoraNumber: return self.x
  def differentiate(self, var: Var) -> Expr: return Const(0)
  def _print_repr(self) -> str: return f'{self.x}'
  def _print_latex(self) -> str: return f'{self.x}'
  
class Constant(Expr):
  def __init__(self, x: _constant, name: str) -> None: 
    self.x = x
    self.name = name
    super().__init__(x, name)
    self.priority = 999

  def _eval(self, **kwargs: Expr) -> CalcoraNumber: return self.x()
  def differentiate(self, var: Var) -> Expr: return Const(0)
  def _print_repr(self) -> str: return self.name
  def _print_latex(self) -> str: return f'\\{self.name}' # Note: Works only for pi...

class Complex(Expr):
  def __init__(self, real: Expr, imag: Expr) -> None:
    self.real = real
    self.imag = imag
    super().__init__(real, imag)
  
  def _eval(self, **kwargs: Expr) -> CalcoraNumber: 
    return mpc(real=self.real._eval(**kwargs), imag=self.imag._eval(**kwargs))
  
  def differentiate(self, var: Var) -> Expr:
    if self.imag != 0: raise ValueError('Cannot differentiate imaginary numbers (for now)')
    return Const(0)
  
  def _print_repr(self) -> str:
    return f'{self.real._print_repr()} + {self.imag._print_repr()}i' if not isinstance(self.imag, Neg) else f'{self.real._print_repr()} - {self.imag.x._print_repr()}i'
  
  def _print_latex(self) -> str: 
    return f'{self.real._print_latex()} + {self.imag._print_latex()}i' if not isinstance(self.imag, Neg) else f'{self.real._print_latex()} - {self.imag.x._print_latex()}i'

class Add(Expr):
  def __init__(self, x: Expr, y: Expr) -> None:
    self.x = x
    self.y = y
    super().__init__(x, y, commutative=True)
    self.priority = 1

  def _eval(self, **kwargs: Expr) -> CalcoraNumber:
    return self.x._eval(**kwargs) + self.y._eval(**kwargs)
  
  def differentiate(self, var: Var) -> Expr:
    return Add(self.x.differentiate(var), self.y.differentiate(var))
  
  def _print_repr(self) -> str:
    x = self.x._print_repr()
    y = self.y._print_repr()
    if self.x.priority < self.priority: x = f'({x})'
    if self.y.priority < self.priority: y = f'({y})'
    return f'{x} + {y}'
  
  def _print_latex(self) -> str:
    x = self.x._print_latex()
    y = self.y._print_latex()
    if self.x.priority < self.priority: x = f'\\left({x}\\right)'
    if self.y.priority < self.priority: y = f'\\left({y}\\right)'
    return f'{x} + {y}'

class Neg(Expr):
  def __init__(self, x: Expr) -> None:
    self.x = x
    super().__init__(x)
    self.priority = 0

  def _eval(self, **kwargs: Expr) -> CalcoraNumber:
    return -self.x._eval(**kwargs)
  
  def differentiate(self, var: Var) -> Expr:
    return Neg(self.x.differentiate(var))
  
  def _print_repr(self) -> str:
    x = self.x._print_repr()
    if not (isinstance(self.x, (Const, Var, Constant))): x = f'({x})'
    return f'-{x}'
  
  def _print_latex(self) -> str:
    x = self.x._print_latex()
    if not (isinstance(self.x, (Const, Var, Constant))): x = f'\\left({x}\\right)'
    return f'-{x}'
  
class Mul(Expr):
  def __init__(self, x: Expr, y: Expr) -> None:
    self.x = x
    self.y = y
    super().__init__(x, y, commutative=True)
    self.priority = 2

  def _eval(self, **kwargs: Expr) -> CalcoraNumber:
    return self.x._eval(**kwargs) * self.y._eval(**kwargs)
  
  def differentiate(self, var: Var) -> Expr:
    return Add(Mul(self.x.differentiate(var), self.y), Mul(self.x, self.y.differentiate(var)))
  
  def _print_repr(self) -> str:
    x = self.x._print_repr()
    y = self.y._print_repr()
    if self.x.priority < self.priority: x = f'({x})'
    if self.y.priority < self.priority: y = f'({y})'
    return f'{x}*{y}'
  
  def _print_latex(self) -> str:
    x = self.x._print_latex()
    y = self.y._print_latex()
    if self.x.priority < self.priority: x = f'\\left({x}\\right)'
    if self.y.priority < self.priority: y = f'\\left({y}\\right)'
    return f'{x} \\cdot {y}'

class Log(Expr):
  def __init__(self, x: Expr, base: Expr = Const(10)) -> None:
    self.x = x
    self.base = base
    super().__init__(x, base)
    self.priority = 4
  
  def _eval(self, **kwargs: Expr) -> CalcoraNumber: 
    return log(self.x._eval(**kwargs), self.base._eval(**kwargs))
  
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
  
  def _print_latex(self) -> str:
    x = self.x._print_latex()
    base = self.base._print_latex()
    return f'\\log_{{{base}}}\\left({x}\\right)'

class Pow(Expr):
  def __init__(self, x: Expr, y: Expr) -> None:
    self.x = x
    self.y = y
    super().__init__(x, y)
    self.priority = 3

  def _eval(self, **kwargs) -> CalcoraNumber:
    return self.x._eval(**kwargs) ** self.y._eval(**kwargs)
  
  def differentiate(self, var: Var) -> Expr:
    return Add(Mul(Mul(self.y, Pow(self.x, Sub(self.y, Const(1)))), self.x.differentiate(var)),
               Mul(Mul(Pow(self.x, self.y), Ln(self.x)), self.y.differentiate(var)))
  
  def _print_repr(self) -> str:
    x = self.x._print_repr()
    y = self.y._print_repr()
    if self.x.priority < self.priority or isinstance(self.x, Pow): x = f'({x})'
    if self.y.priority < self.priority or isinstance(self.y, Pow): y = f'({y})'
    return f'{x}^{y}'
  
  def _print_latex(self) -> str:
    x = self.x._print_latex()
    y = self.y._print_latex()
    if self.x.priority < self.priority or isinstance(self.x, Pow): x = f'\\left({x}\\right)'
    if (self.y.priority < self.priority or isinstance(self.y, Pow)) and not isinstance(self.y, Neg): y = f'\\left({y}\\right)'
    return f'{{{x}}}^{{{y}}}'

class Sin(Expr):
  def __init__(self, x: Expr) -> None:
    self.x = x
    super().__init__(x)
    self.priority = 4
  
  def _eval(self, **kwargs: Expr) -> CalcoraNumber:
    return sin(self.x._eval(**kwargs))
  
  def differentiate(self, var: Var) -> Expr:
    return Cos(self.x) * self.x.differentiate(var)
  
  def _print_repr(self) -> str:
    x = self.x._print_repr()
    return f'sin({x})'
  
  def _print_latex(self) -> str:
    x = self.x._print_latex()
    return f'\\sin\\left({x}\\right)'
  
class Cos(Expr):
  def __init__(self, x: Expr) -> None:
    self.x = x
    super().__init__(x)
    self.priority = 4
  
  def _eval(self, **kwargs: Expr) -> CalcoraNumber:
    return cos(self.x._eval(**kwargs))
  
  def differentiate(self, var: Var) -> Expr:
    return Neg(Sin(self.x)) * self.x.differentiate(var)
  
  def _print_repr(self) -> str:
    x = self.x._print_repr()
    return f'cos({x})'
  
  def _print_latex(self) -> str:
    x = self.x._print_latex()
    return f'\\cos\\left({x}\\right)'

class Div(Expr):
  def __new__(cls, x: Expr, y: Expr) -> Expr: # type: ignore
    if y == Const(0): raise ZeroDivisionError('Denominator cannot be zero!')
    return Mul(x, Pow(y, Neg(Const(1))))
  
class Sub(Expr):
  def __new__(cls, x: Expr, y: Expr) -> Expr: # type: ignore
    return Add(x, Neg(y))
  
class Ln(Expr):
  def __new__(cls, x: Expr) -> Expr: # type: ignore
    return Log(x, ConstantRegistry.get('e'))

class AnyOp(Expr):
  def __init__(self, match: bool = False, name: str="x", assert_const_like=False) -> None:
    self.match = match
    self.name = name
    self.assert_const_like = assert_const_like
    super().__init__()

  def _eval(self, **kwargs) -> CalcoraNumber:
    print('Warning! AnyOp cannot be evaluated, returning 0')
    return 0
  
  def _print_repr(self) -> str:
    return f'Any(name={self.name}, match={self.match}, const={self.assert_const_like})'
  
  def _print_latex(self) -> str:
    return f'Any(name={self.name}, match={self.match}, const={self.assert_const_like})'

FunctionRegistry.register(Var)
FunctionRegistry.register(Const)
FunctionRegistry.register(Constant)
FunctionRegistry.register(Complex)
FunctionRegistry.register(Add)
FunctionRegistry.register(Neg)
FunctionRegistry.register(Mul)
FunctionRegistry.register(Log)
FunctionRegistry.register(Pow)
FunctionRegistry.register(Sin)
FunctionRegistry.register(Cos)
FunctionRegistry.register(AnyOp)

FunctionRegistry.register(Div)
FunctionRegistry.register(Sub)
FunctionRegistry.register(Ln)

if __name__ == "__main__":
  x = Var('x')
  expr = x / 2 + 4
  print(expr)
  print(Const(expr._eval(x=Const(1))))