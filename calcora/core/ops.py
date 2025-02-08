from __future__ import annotations

from typing import TYPE_CHECKING, overload
from typing import Callable, Literal, Optional, Tuple, TypeGuard, Union

from enum import Enum, auto

from calcora.types import CalcoraNumber, NumericType, RealNumeric
from calcora.utils import is_const_like, dprint

from calcora.core.expression import Expr
from calcora.core.numeric import Numeric
from calcora.core.registry import ConstantRegistry, FunctionRegistry, Dispatcher

from mpmath import mpf, mpc, log, sin, cos, fabs, atan, pi, almosteq, nint

if TYPE_CHECKING:
  from mpmath.ctx_mp_python import _constant

type ExprArgTypes = Union[NumericType, Numeric, Expr]

def should_not_numeric_cast(x: Union[Numeric, RealNumeric], should_c: bool) -> TypeGuard[Numeric]: return not should_c
def should_not_cast(x: ExprArgTypes, should_c: bool) -> TypeGuard[Expr]: return not should_c

class Var(Expr):
  def __init__(self, name: str) -> None:
    self.name = name
    super().__init__(name)
    self.priority = 999

  @staticmethod
  def _init(name: str) -> None: pass
  
  def differentiate(self, var: Var) -> Expr: 
    return Const(Numeric(1)) if self == var else Const(Numeric(0))
  
  def _eval(self, **kwargs: Expr) -> CalcoraNumber:
    if self.name in kwargs: return kwargs[self.name]._eval()
    raise ValueError(f"Specified value for type var is required for evaluation, no value for var with name '{self.name}'")
  
  def _print_repr(self) -> str: return f'{self.name}'
  def _print_latex(self) -> str: return f'{self.name}'
FunctionRegistry.register(Var)

class Const(Expr):
  def __init__(self, x: Numeric) -> None:
    self.x = x
    if self.x.real < 0 or self.x.imag: raise ValueError("Const value must be a real, positive value!")
    super().__init__(self.x)
    self.priority = 999
  
  @staticmethod
  def _init(x: Expr) -> None: pass
  def _eval(self, **kwargs: Expr) -> CalcoraNumber: return self.x.value.real
  def differentiate(self, var: Var) -> Expr: return Const(Numeric(0))
  def _print_repr(self) -> str: return f'{self.x}'
  def _print_latex(self) -> str: return f'{self.x}'
FunctionRegistry.register(Const)
  
class Constant(Expr):
  def __init__(self, x: _constant, name: str, latex_name: Optional[str] = None) -> None: 
    self.x = x
    self.name = name
    self.latex_name = latex_name if latex_name else name
    super().__init__(self.x, name, latex_name)
    self.priority = 999
  
  @staticmethod
  def _init(x: _constant, name: str) -> None: pass

  def _eval(self, **kwargs: Expr) -> CalcoraNumber: return self.x()
  def differentiate(self, var: Var) -> Expr: return Const(Numeric(0))
  def _print_repr(self) -> str: return self.name
  def _print_latex(self) -> str: return f'{self.latex_name}'
FunctionRegistry.register(Constant)

class ComplexForm(Enum):
  Rectangular = auto()
  Polar = auto()
  Exponential = auto()

class Add(Expr):
  def __init__(self, x: Expr, y: Expr) -> None:
    self.x = x
    self.y = y
    super().__init__(self.x, self.y, commutative=True)
    self.priority = 1

  @staticmethod
  def _init(x: Expr, y: Expr) -> None: pass

  def _eval(self, **kwargs: Expr) -> CalcoraNumber:
    return self.x._eval(**kwargs) + self.y._eval(**kwargs)
  
  def differentiate(self, var: Var) -> Expr:
    return self.x.differentiate(var) + self.y.differentiate(var)
  
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
  def __init__(self, x: Expr) -> None:
    self.x = x
    super().__init__(self.x)
    self.priority = 0

  @staticmethod
  def _init(x: ExprArgTypes) -> None: pass

  def _eval(self, **kwargs: Expr) -> CalcoraNumber:
    return -self.x._eval(**kwargs)
  
  def differentiate(self, var: Var) -> Expr:
    return -self.x.differentiate(var)
  
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
  def __init__(self, x: Expr, y: Expr) -> None:
    self.x = x
    self.y = y
    super().__init__(self.x, self.y, commutative=True)
    self.priority = 2
  
  @staticmethod
  def _init(x: Expr, y: Expr) -> None: pass

  def _eval(self, **kwargs: Expr) -> CalcoraNumber:
    return self.x._eval(**kwargs) * self.y._eval(**kwargs)
  
  def differentiate(self, var: Var) -> Expr:
    return self.x.differentiate(var)*self.y + self.x*self.y.differentiate(var)
  
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
  def __init__(self, x: Expr, base: Expr) -> None:
    self.x = x
    self.base = base
    super().__init__(self.x, self.base)
    self.priority = 4
  
  @staticmethod
  def _init(x: Expr, base: Expr) -> None: pass
  
  def _eval(self, **kwargs: Expr) -> CalcoraNumber: 
    return log(self.x._eval(**kwargs), self.base._eval(**kwargs))
  
  def differentiate(self, var: Var) -> Expr:
    return ((self.x.differentiate(var)*self.base.ln())/self.x-(self.base.differentiate(var)*self.x.ln())/self.base)/(self.base.ln()**2)
  
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
  def __init__(self, x: Expr, y: Expr) -> None:
    self.x = x
    self.y = y
    super().__init__(self.x, self.y)
    self.priority = 3
  
  @staticmethod
  def _init(x: Expr, y: Expr) -> None: pass

  def _eval(self, **kwargs: Expr) -> CalcoraNumber:
    return self.x._eval(**kwargs) ** self.y._eval(**kwargs)
  
  def differentiate(self, var: Var) -> Expr:
    return self.x.differentiate(var) * (self.y * ((self.x**self.y)/self.x)) + (self.x**self.y) * (self.y.differentiate(var) * self.x.ln())
  
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
  def __init__(self, x: Expr) -> None:
    self.x = x
    super().__init__(self.x)
    self.priority = 4
  
  @staticmethod
  def _init(x: Expr) -> None: pass
  
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
  def __init__(self, x: Expr) -> None:
    self.x = x
    super().__init__(self.x)
    self.priority = 4
  
  @staticmethod
  def _init(x: Expr) -> None: pass
  
  def _eval(self, **kwargs: Expr) -> CalcoraNumber:
    return cos(self.x._eval(**kwargs))
  
  def differentiate(self, var: Var) -> Expr:
    return (-Sin(self.x)) * self.x.differentiate(var)
  
  def _print_repr(self) -> str:
    x = self.x._print_repr()
    return f'cos({x})'
  
  def _print_latex(self) -> str:
    x = self.x._print_latex()
    return f'\\cos\\left({x}\\right)'
FunctionRegistry.register(Cos)

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
FunctionRegistry.register(AnyOp)

class Complex(Expr):
  def __init__(self, real: Expr, imag: Expr, type_cast: Literal[True, False] = True, representation: ComplexForm = ComplexForm.Rectangular) -> None:
    self.real = real
    self.imag = imag
    super().__init__(self.real, self.imag)
    if not is_const_like(self) and representation != ComplexForm.Rectangular: 
      dprint("Polar or exponential representation of complex number with variables is not allowed!", 0, "yellow")
      self._representation = ComplexForm.Rectangular
    else: self._representation = representation
    self.priority = 1 if self.real and self.imag else 999
  
  @staticmethod
  def _init(real: Expr, imag: Expr, form: ComplexForm = ComplexForm.Rectangular) -> None: pass
  
  def _eval(self, **kwargs: Expr) -> CalcoraNumber: 
    return mpc(real=self.real._eval(**kwargs), imag=self.imag._eval(**kwargs))
  
  def differentiate(self, var: Var) -> Expr:
    if self.imag != 0: raise ValueError('Cannot differentiate imaginary numbers (for now)')
    return Const(Numeric(0))
  
  Dispatcher._run_callbacks = False
  _pi = Constant(pi, name='π', latex_name='\\pi')
  KnownPolars : Tuple[
    Tuple[Expr, Callable[[], Tuple[Expr, Expr, Expr, Expr]]],
    Tuple[Expr, Callable[[], Tuple[Expr, Expr, Expr, Expr]]],
    Tuple[Expr, Callable[[], Tuple[Expr, Expr, Expr, Expr]]],
    Tuple[Expr, Callable[[], Tuple[Expr, Expr, Expr, Expr]]],
    Tuple[Expr, Callable[[], Tuple[Expr, Expr, Expr, Expr]]],
    Tuple[Expr, Callable[[], Tuple[Expr, Expr, Expr, Expr]]],
    Tuple[Expr, Callable[[], Tuple[Expr, Expr, Expr, Expr]]],
    Tuple[Expr, Callable[[], Tuple[Expr, Expr, Expr, Expr]]],
  ] = (
    (2 - Dispatcher.sqrt(3), lambda: (Complex._pi/12, (11*Complex._pi)/12, -((11*Complex._pi)/12), -(Complex._pi/12))), # 2 - sqrt(3)
    (Dispatcher.sqrt(3-2*Dispatcher.sqrt(2)), lambda: (Complex._pi/8, (7*Complex._pi)/8, -((7*Complex._pi)/8), -(Complex._pi/8))),
    (1/Dispatcher.sqrt(3), lambda: (Complex._pi/6, (5*Complex._pi)/6, -((5*Complex._pi)/6), -(Complex._pi/6))),
    (Dispatcher.sqrt(5 - 2*Dispatcher.sqrt(5)), lambda: (Complex._pi/5, (4*Complex._pi)/5, -((4*Complex._pi)/5), -(Complex._pi/5))),
    (Const(Numeric(1)), lambda: (Complex._pi/4, (3*Complex._pi)/4, -((3*Complex._pi)/4), -(Complex._pi/4))),
    (Dispatcher.sqrt(3), lambda: (Complex._pi/3, (2*Complex._pi)/3, -((2*Complex._pi)/3), -(Complex._pi/3))),
    (Dispatcher.sqrt(5 + 2*Dispatcher.sqrt(5)), lambda: ((2*Complex._pi)/5, (3*Complex._pi)/5, -((3*Complex._pi)/5), -((2*Complex._pi)/5))),
    (2 + Dispatcher.sqrt(3), lambda: ((5*Complex._pi)/12, (7*Complex._pi)/12, -((7*Complex._pi)/12), -((5*Complex._pi)/12))),
  )
  Dispatcher._run_callbacks = True
  
  quadrant_convert_functions : Tuple[Callable[[CalcoraNumber], Expr], Callable[[CalcoraNumber], Expr], Callable[[CalcoraNumber], Expr], Callable[[CalcoraNumber], Expr]] = (lambda x: Const(x), lambda x: Const(pi - x), lambda x: Neg(Const(pi - x)), lambda x: Neg(x))

  def get_polar(self) -> Tuple[Numeric, Expr]:
    real, imag = self.real._eval(), self.imag._eval()
    r = fabs(self._eval())
    if almosteq(r, nint(r)): r = nint(r)
    ratio_real, ratio_imag = real / r, imag / r

    if almosteq(ratio_real, 1) and almosteq(ratio_imag, 0): return Numeric(r, skip_conversion=True), Const(Numeric(0))
    elif almosteq(ratio_real, 0) and almosteq(ratio_imag, 1): return Numeric(r, skip_conversion=True), self._pi / 2
    elif almosteq(ratio_real, -1) and almosteq(ratio_imag, 0): return Numeric(r, skip_conversion=True), self._pi
    elif almosteq(ratio_real, 0) and almosteq(ratio_imag, -1): return Numeric(r, skip_conversion=True), -(self._pi / 2)

    abs_real, abs_imag = fabs(real) / r, fabs(imag) / r
    quadrant = [1, 4, 2, 3][((real < 0) << 1) | (imag < 0)]
    ratio = abs_imag/abs_real
    has_exact_angle = next((coordinate_fxn()[quadrant-1] for tan_value, coordinate_fxn in self.KnownPolars if almosteq(ratio, tan_value._eval())), None)
    if has_exact_angle: return Numeric(r, skip_conversion=True), has_exact_angle
    else: return Numeric(r, skip_conversion=True), self.quadrant_convert_functions[quadrant-1](atan(ratio))
  
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
        if self.imag.x == Const(Numeric(1)): imag = 'i'
        if not self.real: return f'-{imag}'
        return f'{self.real._print_repr()} - {imag}'
      else:
        imag = f'{self.imag._print_repr()}i'
        if self.imag == Const(Numeric(1)): imag = 'i'
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
        if self.imag == Const(Numeric(1)): imag = '-i'
        if self.real == Const(Numeric(0)): return f'{imag}'
        return f'{self.real._print_latex()} - {imag}'
      else:
        imag = f'{self.imag._print_latex()}i'
        if self.imag == Const(Numeric(1)): imag = 'i'
        if self.real == Const(Numeric(0)): return f'{imag}'
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