from __future__ import annotations

from typing import TYPE_CHECKING, overload
from typing import Literal, TypeGuard, Union

from enum import Enum, auto

from calcora.types import CalcoraNumber, RealNumberLike, NumericType, RealNumeric
from calcora.utils import is_const_like, dprint

from calcora.core.expression import Expr
from calcora.core.numeric import Numeric
from calcora.core.registry import ConstantRegistry, FunctionRegistry

from calcora.printing.printops import PrintableOp


from mpmath import mpf, mpc, log, sin, cos, polar, sqrt

if TYPE_CHECKING:
  from mpmath.ctx_mp_python import _constant

ExprArgTypes = Union[NumericType, Numeric, Expr]

def should_not_numeric_cast(x: Union[Numeric, RealNumeric], should_c: bool) -> TypeGuard[Numeric]: return not should_c
def should_not_cast(x: ExprArgTypes, should_c: bool) -> TypeGuard[Expr]: return not should_c

# Note: There should proboably be some sort of argument on the ops that specify if typecast should be called
def typecast(x: Union[NumericType, Numeric, Expr, PrintableOp]) -> Expr:
  if isinstance(x, Expr): return x
  elif isinstance(x, PrintableOp): return x # type: ignore
  elif isinstance(x, Numeric): return Const(x) if x >= 0 else Neg(Const(abs(x)))
  elif isinstance(x, (float, int)): 
    n = Numeric(x)
    return Const(n) if n >= 0 else Neg(Const(abs(n)))
  elif isinstance(x, (complex, str, mpf, mpc)): 
    num = Numeric(x)
    if num.imag: return Complex(num.real if num.real >= 0 else Neg(abs(num.real)), num.imag if num.imag >= 0 else Neg(abs(num.imag)))
    else: return Const(num) if num >= 0 else Const(abs(num))
  else: raise TypeError(f"Invalid type {type(x)} for conversion to type Const")

class Var(Expr):
  def __init__(self, name: str, type_cast : Literal[True, False] = True) -> None:
    self.name = name
    super().__init__(name)
    self.priority = 999

  @staticmethod
  def _init(name: str) -> None: pass
  
  def differentiate(self, var: Var) -> Expr: 
    return Const(1) if self == var else Const(0)
  
  def _eval(self, **kwargs: Expr) -> CalcoraNumber:
    if self.name in kwargs: return typecast(kwargs[self.name])._eval()
    raise ValueError(f"Specified value for type var is required for evaluation, no value for var with name '{self.name}'")
  
  def _print_repr(self) -> str: return f'{self.name}'
  def _print_latex(self) -> str: return f'{self.name}'
  
class Const(Expr):
  @overload
  def __init__(self, x: Union[NumericType, Numeric], type_cast: Literal[True] = ...) -> None: ...
  @overload
  def __init__(self, x: Numeric, type_cast: Literal[False]) -> None: ...

  def __init__(self, x: Union[NumericType, Numeric], type_cast: Literal[True, False] = True) -> None:
    if should_not_numeric_cast(x, type_cast): self.x = x
    else: self.x = Numeric.numeric_cast(x)
    if self.x.real < 0 or self.x.imag: raise ValueError("Const value must be a real, positive value!")
    super().__init__(self.x)
    self.priority = 999
  
  @staticmethod
  def _init(x: Union[NumericType, Numeric]) -> None: pass
  
  def _eval(self, **kwargs: Expr) -> CalcoraNumber: return self.x.value.real
  def differentiate(self, var: Var) -> Expr: return Const(0)
  def _print_repr(self) -> str: return f'{self.x}'
  def _print_latex(self) -> str: return f'{self.x}'
  
class Constant(Expr):
  def __init__(self, x: _constant, name: str, type_cast: bool = True) -> None: 
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
  @overload
  def __init__(self, real: ExprArgTypes, imag: ExprArgTypes, type_cast: Literal[True] = ..., representation: ComplexForm = ComplexForm.Rectangular) -> None: ...
  @overload
  def __init__(self, real: Expr, imag: Expr, type_cast: Literal[False], representation: ComplexForm = ComplexForm.Rectangular) -> None: ...

  def __init__(self, real: ExprArgTypes, imag: ExprArgTypes, type_cast: Literal[True, False] = True, representation: ComplexForm = ComplexForm.Rectangular) -> None:
    if should_not_cast(real, type_cast): self.real = real
    else: self.real = typecast(real)
    if should_not_cast(imag, type_cast): self.imag = imag
    else: self.imag = typecast(imag)
    super().__init__(self.real, self.imag)
    if not is_const_like(self) and representation != ComplexForm.Rectangular: 
      dprint("Polar or exponential representation of complex number with variables is not allowed!", 0, "yellow")
      self._representation = ComplexForm.Rectangular
    else: self._representation = representation
    self.priority = 1 if self.real and self.imag else 999
  
  @staticmethod
  def _init(real: ExprArgTypes, imag: ExprArgTypes, form: ComplexForm = ComplexForm.Rectangular) -> None: pass
  
  def _eval(self, **kwargs: Expr) -> CalcoraNumber: 
    return mpc(real=self.real._eval(**kwargs), imag=self.imag._eval(**kwargs))
  
  def differentiate(self, var: Var) -> Expr:
    if self.imag != 0: raise ValueError('Cannot differentiate imaginary numbers (for now)')
    return Const(0)
  
  def _print_repr(self) -> str:
    if self._representation == ComplexForm.Polar:
      r, v = polar(self._eval())
      if r == 1: return f'cos({Numeric(v, skip_conversion=True)}) + isin({Numeric(v, skip_conversion=True)})'
      else: return f'{Numeric(r, skip_conversion=True)}(cos({Numeric(v, skip_conversion=True)}) + isin({Numeric(v, skip_conversion=True)}))'
    elif self._representation == ComplexForm.Exponential:
      r, v = polar(self._eval())
      if r == 1: return f'e^{Numeric(v, skip_conversion=True)}i'
      else: return f'{Numeric(r, skip_conversion=True)}e^{Numeric(v, skip_conversion=True)}i'
    else:
      if isinstance(self.imag, Neg):
        imag = f'{self.imag.x._print_repr()}i'
        if self.imag.x == Const(1): imag = 'i'
        if not self.real: return f'-{imag}'
        return f'{self.real._print_repr()} - {imag}'
      else:
        imag = f'{self.imag._print_repr()}i'
        if self.imag == Const(1): imag = 'i'
        if not self.real: return f'{imag}'
        return f'{self.real._print_repr()} + {imag}'
  
  def _print_latex(self) -> str:
    if self._representation == ComplexForm.Polar:
      r, v = polar(self._eval())
      if r == 1: return f'\\cos\\left({Numeric(v, skip_conversion=True)}\\right) + i\\sin\\left({Numeric(v, skip_conversion=True)}\\right)'
      else: return f'{Numeric(r, skip_conversion=True)}\\left(\\cos\\left({Numeric(v, skip_conversion=True)}\\right) + i\\sin\\left({Numeric(v, skip_conversion=True)}\\right)\\right)'
    elif self._representation == ComplexForm.Exponential:
      r, v = polar(self._eval())
      if r == 1: return f'e^{{{Numeric(v, skip_conversion=True)}i}}'
      else: return f'{Numeric(r, skip_conversion=True)}e^{{{Numeric(v, skip_conversion=True)}i}}'
    else:
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
  
  @property
  def representation(self) -> ComplexForm: return self._representation
  
  @representation.setter
  def representation(self, representation: ComplexForm) -> None:
    if not is_const_like(self) and representation != ComplexForm.Rectangular: dprint("Polar or exponential representation of complex number with variables is not allowed!", 0, "yellow")
    self._representation = representation
    if representation == ComplexForm.Polar or representation == ComplexForm.Exponential: self.priority = 2
    elif representation == ComplexForm.Rectangular and self.real and self.imag: self.priority = 1
    elif representation == ComplexForm.Rectangular and self.imag: self.priority = 999
    elif representation == ComplexForm.Rectangular and self.real: self.priority = 999

class Add(Expr):
  @overload
  def __init__(self, x: ExprArgTypes, y: ExprArgTypes, type_cast: Literal[True] = ...) -> None: ...
  @overload
  def __init__(self, x: Expr, y: Expr, type_cast: Literal[False]) -> None: ...

  def __init__(self, x: ExprArgTypes, y: ExprArgTypes, type_cast: Literal[True, False] = True) -> None:
    if should_not_cast(x, type_cast): self.x = x
    else: self.x = typecast(x)
    if should_not_cast(y, type_cast): self.y = y
    else: self.y = typecast(y)
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
  @overload
  def __init__(self, x: ExprArgTypes, type_cast: Literal[True] = ...) -> None: ...
  @overload
  def __init__(self, x: Expr, type_cast: Literal[False]) -> None: ...

  def __init__(self, x: ExprArgTypes, type_cast: Literal[True, False] = True) -> None:
    if should_not_cast(x, type_cast): self.x = x
    else: self.x = typecast(x)
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
  @overload
  def __init__(self, x: ExprArgTypes, y: ExprArgTypes, type_cast: Literal[True] = ...) -> None: ...
  @overload
  def __init__(self, x: Expr, y: Expr, type_cast: Literal[False]) -> None: ...

  def __init__(self, x: ExprArgTypes, y: ExprArgTypes, type_cast: Literal[True, False] = True) -> None:
    if should_not_cast(x, type_cast): self.x = x
    else: self.x = typecast(x)
    if should_not_cast(y, type_cast): self.y = y
    else: self.y = typecast(y)
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
  @overload
  def __init__(self, x: ExprArgTypes, base: ExprArgTypes, type_cast: Literal[True] = ...) -> None: ...
  @overload
  def __init__(self, x: Expr, base: Expr, type_cast: Literal[False]) -> None: ...

  def __init__(self, x: ExprArgTypes, base: ExprArgTypes, type_cast: Literal[True, False] = True) -> None:
    if should_not_cast(x, type_cast): self.x = x
    else: self.x = typecast(x)
    if should_not_cast(base, type_cast): self.base = base
    else: self.base = typecast(base)
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
  @overload
  def __init__(self, x: ExprArgTypes, y: ExprArgTypes, type_cast: Literal[True] = ...) -> None: ...
  @overload
  def __init__(self, x: Expr, y: Expr, type_cast: Literal[False]) -> None: ...

  def __init__(self, x: ExprArgTypes, y: ExprArgTypes, type_cast: Literal[True, False] = True) -> None:
    if should_not_cast(x, type_cast): self.x = x
    else: self.x = typecast(x)
    if should_not_cast(y, type_cast): self.y = y
    else: self.y = typecast(y)
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
  @overload
  def __init__(self, x: ExprArgTypes, type_cast: Literal[True] = ...) -> None: ...
  @overload
  def __init__(self, x: Expr, type_cast: Literal[False]) -> None: ...

  def __init__(self, x: ExprArgTypes, type_cast: Literal[True, False] = True) -> None:
    if should_not_cast(x, type_cast): self.x = x
    else: self.x = typecast(x)
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
  @overload
  def __init__(self, x: ExprArgTypes, type_cast: Literal[True] = ...) -> None: ...
  @overload
  def __init__(self, x: Expr, type_cast: Literal[False]) -> None: ...

  def __init__(self, x: ExprArgTypes, type_cast: Literal[True, False] = True) -> None:
    if should_not_cast(x, type_cast): self.x = x
    else: self.x = typecast(x)
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
  @overload
  def __new__(cls, x: ExprArgTypes, y: ExprArgTypes, type_cast: Literal[True] = ...) -> Expr: ... # type: ignore
  @overload
  def __new__(cls, x: Expr, y: Expr, type_cast: Literal[False]) -> Expr: ... # type: ignore

  def __new__(cls, x: ExprArgTypes, y: ExprArgTypes, type_cast: Literal[True, False] = True) -> Expr: # type: ignore
    if y == Const(0): raise ZeroDivisionError('Denominator cannot be zero!')
    return Mul(x, Pow(y, Neg(Const(1))))
  
  @staticmethod
  def _init(x: ExprArgTypes, y: ExprArgTypes) -> None: pass
  
class Sub(Expr):
  @overload
  def __new__(cls, x: ExprArgTypes, y: ExprArgTypes, type_cast: Literal[True] = ...) -> Expr: ... # type: ignore
  @overload
  def __new__(cls, x: Expr, y: Expr, type_cast: Literal[False]) -> Expr: ... # type: ignore

  def __new__(cls, x: ExprArgTypes, y: ExprArgTypes, type_cast: Literal[True, False] = True) -> Expr: # type: ignore
    return Add(x, Neg(y))
  
  @staticmethod
  def _init(x: ExprArgTypes, y: ExprArgTypes) -> None: pass
  
class Ln(Expr):
  @overload
  def __new__(cls, x: ExprArgTypes, type_cast: Literal[True] = ...) -> Expr: ... # type: ignore
  @overload
  def __new__(cls, x: Expr, type_cast: Literal[False]) -> Expr: ... # type: ignore

  def __new__(cls, x: ExprArgTypes, type_cast: Literal[True, False] = True) -> Expr: # type: ignore
    return Log(x, ConstantRegistry.get('e'))
  
  @staticmethod
  def _init(x: ExprArgTypes) -> None: pass

class AnyOp(Expr):
  def __init__(self, match: bool = False, name: str = "x", assert_const_like: bool = False, type_cast: Literal[True, False] = True) -> None:
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