from __future__ import annotations

from typing import TYPE_CHECKING, overload
from typing import Callable, Dict, Literal, Optional, Tuple, TypeGuard, Union

from enum import Enum, auto
from itertools import compress

from calcora.types import CalcoraNumber, NumericType, RealNumeric
from calcora.utils import is_const_like, dprint

from calcora.core.expression import Expr
from calcora.core.numeric import Numeric
from calcora.core.registry import ConstantRegistry, FunctionRegistry

from mpmath import mpf, mpc, log, sin, cos, fabs, atan, pi, almosteq, nint

if TYPE_CHECKING:
  from mpmath.ctx_mp_python import _constant

type ExprArgTypes = Union[NumericType, Numeric, Expr]

def should_not_numeric_cast(x: Union[Numeric, RealNumeric], should_c: bool) -> TypeGuard[Numeric]: return not should_c
def should_not_cast(x: ExprArgTypes, should_c: bool) -> TypeGuard[Expr]: return not should_c

# Note: There should proboably be some sort of argument on the ops that specify if typecast should be called
def typecast(x: Union[NumericType, Numeric, Expr]) -> Expr:
  if isinstance(x, Expr): return x
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
FunctionRegistry.register(Var)
  
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
FunctionRegistry.register(Const)
  
class Constant(Expr):
  def __init__(self, x: _constant, name: str, latex_name: Optional[str] = None, type_cast: bool = True) -> None: 
    self.x = x
    self.name = name
    self.latex_name = latex_name if latex_name else name
    super().__init__(self.x, name, latex_name)
    self.priority = 999
  
  @staticmethod
  def _init(x: _constant, name: str) -> None: pass

  def _eval(self, **kwargs: Expr) -> CalcoraNumber: return self.x()
  def differentiate(self, var: Var) -> Expr: return Const(0)
  def _print_repr(self) -> str: return self.name
  def _print_latex(self) -> str: return f'{self.latex_name}'
FunctionRegistry.register(Constant)

class ComplexForm(Enum):
  Rectangular = auto()
  Polar = auto()
  Exponential = auto()

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
FunctionRegistry.register(Add)

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
FunctionRegistry.register(Neg)
  
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
  
  # TODO: if one is const and one is constant no mul sign
  #       if both are constant no mul sign
  #       if one is const and one is var no mul sign
  #       if both is var no mul sign
  #       if one is constant and one is var no mul sign
  #       if one is const, constant or var and other is lower priority op, no mul sign
  #       if one is const, constant or var and other is op with paren no mul sign
  #       if they are not both const then no mul sign is needed? Const with neg also counts

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
FunctionRegistry.register(Mul)

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
FunctionRegistry.register(Log)

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
FunctionRegistry.register(Pow)

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
FunctionRegistry.register(Sin)
  
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
FunctionRegistry.register(Cos)

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
FunctionRegistry.register(Div)
  
class Sub(Expr):
  @overload
  def __new__(cls, x: ExprArgTypes, y: ExprArgTypes, type_cast: Literal[True] = ...) -> Expr: ... # type: ignore
  @overload
  def __new__(cls, x: Expr, y: Expr, type_cast: Literal[False]) -> Expr: ... # type: ignore

  def __new__(cls, x: ExprArgTypes, y: ExprArgTypes, type_cast: Literal[True, False] = True) -> Expr: # type: ignore
    return Add(x, Neg(y))
  
  @staticmethod
  def _init(x: ExprArgTypes, y: ExprArgTypes) -> None: pass
FunctionRegistry.register(Sub)
  
class Ln(Expr):
  @overload
  def __new__(cls, x: ExprArgTypes, type_cast: Literal[True] = ...) -> Expr: ... # type: ignore
  @overload
  def __new__(cls, x: Expr, type_cast: Literal[False]) -> Expr: ... # type: ignore

  def __new__(cls, x: ExprArgTypes, type_cast: Literal[True, False] = True) -> Expr: # type: ignore
    return Log(x, ConstantRegistry.get('e'))
  
  @staticmethod
  def _init(x: ExprArgTypes) -> None: pass
FunctionRegistry.register(Ln)

class Sqrt(Expr):
  @overload
  def __new__(cls, x: ExprArgTypes, type_cast: Literal[True] = ...) -> Expr: ... # type: ignore
  @overload
  def __new__(cls, x: Expr, type_cast: Literal[False]) -> Expr: ... # type: ignore

  def __new__(cls, x: ExprArgTypes, type_cast: Literal[True, False] = True) -> Expr: # type: ignore
    return Pow(x, Const(0.5))
  
  @staticmethod
  def _init(x: ExprArgTypes) -> None: pass
FunctionRegistry.register(Sqrt)

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
FunctionRegistry.register(AnyOp)
  
class Complex(Expr):
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
  
  _pi = Constant(pi, name='π', latex_name='\\pi')
  KnownPolarsRatio : Tuple[
    Tuple[Expr, Callable[[], Tuple[Expr, Expr, Expr, Expr]]],
    Tuple[Expr, Callable[[], Tuple[Expr, Expr, Expr, Expr]]],
    Tuple[Expr, Callable[[], Tuple[Expr, Expr, Expr, Expr]]],
    Tuple[Expr, Callable[[], Tuple[Expr, Expr, Expr, Expr]]],
    Tuple[Expr, Callable[[], Tuple[Expr, Expr, Expr, Expr]]],
    Tuple[Expr, Callable[[], Tuple[Expr, Expr, Expr, Expr]]],
    Tuple[Expr, Callable[[], Tuple[Expr, Expr, Expr, Expr]]],
    Tuple[Expr, Callable[[], Tuple[Expr, Expr, Expr, Expr]]],
  ] = (
    (2 - Sqrt(3), lambda: (Complex._pi/12, (11*Complex._pi)/12, -((11*Complex._pi)/12), -(Complex._pi/12))),
    (Sqrt(3-2*Sqrt(2)), lambda: (Complex._pi/8, (7*Complex._pi)/8, -((7*Complex._pi)/8), -(Complex._pi/8))),
    (1/Sqrt(3), lambda: (Complex._pi/6, (5*Complex._pi)/6, -((5*Complex._pi)/6), -(Complex._pi/6))),
    (Sqrt(5 - 2*Sqrt(5)), lambda: (Complex._pi/5, (4 * Complex._pi)/5, -((4*Complex._pi)/5), -(Complex._pi/5))),
    (Const(1), lambda: (Complex._pi/4, (3*Complex._pi)/4, -((3*Complex._pi)/4), -(Complex._pi/4))),
    (Sqrt(3), lambda: (Complex._pi/3, (2*Complex._pi)/3, -((2*Complex._pi)/3), -(Complex._pi/3))),
    (Sqrt(5 + 2*Sqrt(5)), lambda: ((2*Complex._pi)/5, (3*Complex._pi)/5, -((3*Complex._pi)/5), -((2*Complex._pi)/5))),
    (2 + Sqrt(3), lambda: ((5*Complex._pi)/12, (7*Complex._pi)/12, -((7*Complex._pi)/12), -((5*Complex._pi)/12))),
  )

  def get_polar(self) -> Tuple[Numeric, Expr]:
    real, imag = self.real._eval(), self.imag._eval()
    r = fabs(self._eval())
    if almosteq(r, nint(r)): r = nint(r)
    ratio_real, ratio_imag = real / r, imag / r
    on_axles = (almosteq(ratio_real, 1) and almosteq(ratio_imag, 0)) * 1 or \
               (almosteq(ratio_real, 0) and almosteq(ratio_imag, 1)) * 2 or \
               (almosteq(ratio_real, -1) and almosteq(ratio_imag, 0)) * 3 or \
               (almosteq(ratio_real, 0) and almosteq(ratio_imag, -1)) * 4
    
    if on_axles: return Numeric(r, skip_conversion=True), [Const(0), self._pi/2, self._pi, -(self._pi/2)][on_axles-1]
    abs_real, abs_imag = fabs(real) / r, fabs(imag) / r
    quadrant = [1, 4, 2, 3][((real < 0) << 1) | (imag < 0)]
    quadrant_convert_functions : Tuple[Callable[[CalcoraNumber], Expr], Callable[[CalcoraNumber], Expr], Callable[[CalcoraNumber], Expr], Callable[[CalcoraNumber], Expr]] = (lambda x: Const(x), lambda x: Const(pi - x), lambda x: Neg(Const(pi - x)), lambda x: Neg(x))
    ratio = abs_imag/abs_real
    has_exact_angle = next((coordinate_fxn()[quadrant-1] for tan_value, coordinate_fxn in self.KnownPolarsRatio if almosteq(ratio, tan_value._eval())), None)
    if has_exact_angle: return Numeric(r, skip_conversion=True), has_exact_angle
    else: return Numeric(r, skip_conversion=True), quadrant_convert_functions[quadrant-1](atan(abs_imag/abs_real))
  
  def _print_repr(self) -> str:
    if self._representation == ComplexForm.Polar:
      r, v = self.get_polar()
      if r == 1: return f'cos({v}) + isin({v})'
      else: return f'{r}(cos({v}) + isin({v}))'
    elif self._representation == ComplexForm.Exponential:
      r, v = self.get_polar()
      if r == 1: return f'e^{v}i'
      else: return f'{r}e^{v}i'
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
      r, v = self.get_polar()
      if r == 1: return f'\\cos\\left({v}\\right) + i\\sin\\left({v}\\right)'
      else: return f'{r}\\left(\\cos\\left({v}\\right) + i\\sin\\left({v}\\right)\\right)'
    elif self._representation == ComplexForm.Exponential:
      r, v = self.get_polar()
      if r == 1: return f'e^{{{v}i}}'
      else: return f'{r}e^{{{v}i}}'
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
FunctionRegistry.register(Complex)

if __name__ == "__main__":
  x = Var('x')
  expr = x / 2 + 4
  print(expr)
  print(Const(expr._eval(x=Const(1))))