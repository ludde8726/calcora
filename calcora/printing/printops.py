from __future__ import annotations

from calcora.globals import BaseOps
from calcora.types import CalcoraNumber

from mpmath import log, pi

from calcora.core.expression import Expr
from calcora.core.ops import Add, Mul, Neg

class PrintableOp(Expr):
  def __init__(self, *args: Expr, name: str) -> None:
    self.args = args
    self.fxn = BaseOps.NoOp
    self.print_name = name

  def __eq__(self, other: object) -> bool:
    return type(self) is type(other) and self.args == other.args # type: ignore
  
  def _print_repr(self) -> str: raise NotImplementedError()
  def _print_latex(self) -> str: raise NotImplementedError()
  def __repr__(self) -> str: return self._print_repr()

class PrintableSub(PrintableOp): 
  def __init__(self, x: Expr, y: Expr, type_cast: bool = True) -> None:
    self.x = x
    self.y = y
    self.priority = 1
    super().__init__(x, y, name='Sub')
  
  def _print_repr(self) -> str:
    x = self.x._print_repr()
    y = self.y._print_repr()
    if self.x.priority < self.priority and not isinstance(self.x, Neg): x = f'({x})'
    if self.y.priority < self.priority or isinstance(self.y, PrintableSub) or isinstance(self.y, Neg) or isinstance(self.y, Add): y = f'({y})'
    return f'{x} - {y}'
  
  def _print_latex(self) -> str:
    x = self.x._print_latex()
    y = self.y._print_latex()
    if self.x.priority < self.priority and not isinstance(self.x, Neg): x = f'\\left({x}\\right)'
    if self.y.priority < self.priority or isinstance(self.y, PrintableSub) or isinstance(self.y, Neg) or isinstance(self.y, Add): y = f'\\left({y}\\right)'
    return f'{x} - {y}'
  
  def _eval(self, **kwargs: Expr) -> CalcoraNumber:
    return self.x._eval(**kwargs) + (-self.y._eval(**kwargs))

class PrintableDiv(PrintableOp):
  def __init__(self, x: Expr, y: Expr, type_cast: bool = True) -> None:
    self.x = x
    self.y = y
    self.priority = 2
    super().__init__(x, y, name='Div')
  
  def _print_repr(self) -> str:
    x = self.x._print_repr()
    y = self.y._print_repr()
    if self.x.priority < self.priority or isinstance(self.x, PrintableDiv): x = f'({x})'
    if self.y.priority < self.priority or isinstance(self.y, PrintableDiv) or isinstance(self.y, Mul): y = f'({y})'
    return f'{x}/{y}'
  
  def _print_latex(self) -> str:
    x = self.x._print_latex()
    y = self.y._print_latex()
    return f'\\frac{{{x}}}{{{y}}}'
  
  def _eval(self, **kwargs: Expr) -> CalcoraNumber:
    return self.x._eval(**kwargs) * (self.y._eval(**kwargs) ** (-1))
  
class PrintableLn(PrintableOp):
  def __init__(self, x: Expr, type_cast: bool = True) -> None:
    self.x = x
    self.priority = 4
    super().__init__(x, name='Ln')
  
  def _print_repr(self) -> str:
    x = self.x._print_repr()
    return f'ln({x})'
  
  def _print_latex(self) -> str:
    x = self.x._print_latex()
    return f'\\ln\\left({x}\\right)'
  
  def _eval(self, **kwargs: Expr) -> CalcoraNumber:
    return log(self.x._eval(**kwargs), pi)
  
class PrintableSqrt(PrintableOp):
  def __init__(self, x: Expr, type_cast: bool = True) -> None:
    self.x = x
    self.priority = 4
    super().__init__(x, name='Sqrt')
  
  def _print_repr(self) -> str:
    x = self.x._print_repr()
    return f'sqrt({x})'
  
  def _print_latex(self) -> str:
    x = self.x._print_latex()
    return f'\\sqrt{{{x}}}'
  
  def _eval(self, **kwargs: Expr) -> CalcoraNumber:
    return self.x._eval(**kwargs) ** 0.5