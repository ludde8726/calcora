from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Union

from enum import Enum, auto

from calcora.types import CalcoraNumber, RealNumberLike, NumericType

from calcora.core.expression import Expr
from calcora.core.numeric import Numeric
from calcora.core.registry import ConstantRegistry, FunctionRegistry

from calcora.printing.printops import PrintableOp

from mpmath import mpf, mpc, log, sin, cos

if TYPE_CHECKING:
  from mpmath.ctx_mp_python import _constant

ExprArgTypes = Union[NumericType, Numeric, Expr]

# Note: There should proboably be some sort of argument on the ops that specify if typecast should be called
def typecast(x: Union[NumericType, Numeric, Expr, PrintableOp]) -> Expr:
  if isinstance(x, Expr): return x
  elif isinstance(x, PrintableOp): return x # type: ignore
  elif isinstance(x, Numeric): return Const(x)
  elif isinstance(x, (float, int)): return Const(Numeric(x))
  elif isinstance(x, (complex, str, mpf, mpc)): 
    num = Numeric(x)
    if num.imag: return Complex(num.real, num.imag)
    else: return Const(num)
  else: raise TypeError(f"Invalid type {type(x)} for conversion to type Const")

class Var(Expr):
  def __init__(self, name: str) -> None:
    self.name = name
    super().__init__(name)
    self.priority = 999

  @staticmethod
  def _init(name: str) -> None: pass
  
  def differentiate(self, var: Var) -> Expr: 
    return Const(1) if self == var else Const(0)
  
  def _eval(self, **kwargs: Expr) -> CalcoraNumber:
    if self.name in kwargs: return kwargs[self.name]._eval()
    raise ValueError(f"Specified value for type var is required for evaluation, no value for var with name '{self.name}'")
  
  def _print_repr(self) -> str: return f'{self.name}'
  def _print_latex(self) -> str: return f'{self.name}'
  
class Const(Expr):
  def __init__(self, x: Union[NumericType, Numeric]) -> None:
    self.x = Numeric.numeric_cast(x)
    if self.x.real < 0 or self.x.imag: raise ValueError("Const value must be a real, positive value!")
    super().__init__(self.x)
    self.priority = 999
  
  @staticmethod
  def _init(x: Union[NumericType, Numeric]) -> None: pass
  
  def _eval(self, **kwargs: Expr) -> CalcoraNumber: return self.x.value
  def differentiate(self, var: Var) -> Expr: return Const(0)
  def _print_repr(self) -> str: return f'{self.x}'
  def _print_latex(self) -> str: return f'{self.x}'
  
class Constant(Expr):
  def __init__(self, x: _constant, name: str) -> None: 
    self.x = x
    self.name = name
    super().__init__(self.x, name)
    self.priority = 999
  
  @staticmethod
  def _init(x: _constant, name: str) -> None: pass

  def _eval(self, **kwargs: Expr) -> CalcoraNumber: return self.x()
  def differentiate(self, var: Var) -> Expr: return Const(0)
  def _print_repr(self) -> str: return self.name
  def _print_latex(self) -> str: return f'\\{self.name}' # Note: Works only for pi...

class ComplexForm(Enum):
  Rectangular = auto()
  Polar = auto()
  Exponential = auto()

class Complex(Expr):  # TODO: Add support for polar and exponential representation, aswell as fix printing order.
  def __init__(self, real: ExprArgTypes, imag: ExprArgTypes, form: ComplexForm = ComplexForm.Rectangular) -> None:
    self.real = typecast(real)
    self.imag = typecast(imag)
    super().__init__(self.real, self.imag)
  
  @staticmethod
  def _init(real: ExprArgTypes, imag: ExprArgTypes, form: ComplexForm = ComplexForm.Rectangular) -> None: pass
  
  def _eval(self, **kwargs: Expr) -> CalcoraNumber: 
    return mpc(real=self.real._eval(**kwargs), imag=self.imag._eval(**kwargs))
  
  def differentiate(self, var: Var) -> Expr:
    if self.imag != 0: raise ValueError('Cannot differentiate imaginary numbers (for now)')
    return Const(0)
  
  def _print_repr(self) -> str:
    if isinstance(self.imag, Neg):
      imag = f'{self.imag.x._print_repr()}i'
      if self.imag == Const(1): imag = '-i'
      if self.real == Const(0): return f'{imag}'
      return f'{self.real._print_repr()} - {imag}'
    else:
      imag = f'{self.imag._print_repr()}i'
      if self.imag == Const(1): imag = 'i'
      if self.real == Const(0): return f'{imag}'
      return f'{self.real._print_repr()} + {imag}'
  
  def _print_latex(self) -> str:
    if isinstance(self.imag, Neg):
      imag = f'{self.imag.x._print_latex()}i'
      if self.imag == Const(1): imag = '-i'
      if self.real == Const(0): return f'{imag}'
      return f'{self.real._print_latex()} - {imag}'
    else:
      imag = f'{self.imag._print_latex()}i'
      if self.imag == Const(1): imag = 'i'
      if self.real == Const(0): return f'{imag}'
      return f'{self.real._print_latex()} + {imag}'

class Add(Expr):
  def __init__(self, x: ExprArgTypes, y: ExprArgTypes) -> None:
    self.x = typecast(x)
    self.y = typecast(y)
    super().__init__(self.x, self.y, commutative=True)
    self.priority = 1

  @staticmethod
  def _init(x: ExprArgTypes, y: ExprArgTypes) -> None: pass

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
  def __init__(self, x: ExprArgTypes) -> None:
    self.x = typecast(x)
    super().__init__(self.x)
    self.priority = 0

  @staticmethod
  def _init(x: ExprArgTypes) -> None: pass

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
  def __init__(self, x: ExprArgTypes, y: ExprArgTypes) -> None:
    self.x = typecast(x)
    self.y = typecast(y)
    super().__init__(self.x, self.y, commutative=True)
    self.priority = 2
  
  @staticmethod
  def _init(x: ExprArgTypes, y: ExprArgTypes) -> None: pass

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
  def __init__(self, x: ExprArgTypes, base: ExprArgTypes) -> None:
    self.x = typecast(x)
    self.base = typecast(base)
    super().__init__(self.x, self.base)
    self.priority = 4
  
  @staticmethod
  def _init(x: ExprArgTypes, base: ExprArgTypes) -> None: pass
  
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
    return f'log_{base}({x})'
  
  def _print_latex(self) -> str:
    x = self.x._print_latex()
    base = self.base._print_latex()
    return f'\\log_{{{base}}}\\left({x}\\right)'

class Pow(Expr):
  def __init__(self, x: ExprArgTypes, y: ExprArgTypes) -> None:
    self.x = typecast(x)
    self.y = typecast(y)
    super().__init__(self.x, self.y)
    self.priority = 3
  
  @staticmethod
  def _init(x: ExprArgTypes, y: ExprArgTypes) -> None: pass

  def _eval(self, **kwargs: Expr) -> CalcoraNumber:
    return self.x._eval(**kwargs) ** self.y._eval(**kwargs)
  
  def differentiate(self, var: Var) -> Expr:
    return Mul(Pow(self.x, self.y), Add(Mul(self.y, Div(self.x.differentiate(var), self.x)), Mul(self.y.differentiate(var), Ln(self.x))))
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
  def __init__(self, x: ExprArgTypes) -> None:
    self.x = typecast(x)
    super().__init__(self.x)
    self.priority = 4
  
  @staticmethod
  def _init(x: ExprArgTypes) -> None: pass
  
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
  def __init__(self, x: ExprArgTypes) -> None:
    self.x = typecast(x)
    super().__init__(self.x)
    self.priority = 4
  
  @staticmethod
  def _init(x: ExprArgTypes) -> None: pass
  
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
  def __new__(cls, x: ExprArgTypes, y: ExprArgTypes) -> Expr: # type: ignore
    if y == Const(0): raise ZeroDivisionError('Denominator cannot be zero!')
    return Mul(x, Pow(y, Neg(Const(1))))
  
  @staticmethod
  def _init(x: ExprArgTypes, y: ExprArgTypes) -> None: pass
  
class Sub(Expr):
  def __new__(cls, x: ExprArgTypes, y: ExprArgTypes) -> Expr: # type: ignore
    return Add(x, Neg(y))
  
  @staticmethod
  def _init(x: ExprArgTypes, y: ExprArgTypes) -> None: pass
  
class Ln(Expr):
  def __new__(cls, x: ExprArgTypes) -> Expr: # type: ignore
    return Log(x, ConstantRegistry.get('e'))
  
  @staticmethod
  def _init(x: ExprArgTypes) -> None: pass

class AnyOp(Expr):
  def __init__(self, match: bool = False, name: str = "x", assert_const_like: bool = False) -> None:
    self.match = match
    self.name = name
    self.assert_const_like = assert_const_like
    super().__init__()
  
  @staticmethod
  def _init(match: bool = False, name: str = "x", assert_const_like: bool = False) -> None: pass

  def _eval(self, **kwargs: Expr) -> CalcoraNumber:
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