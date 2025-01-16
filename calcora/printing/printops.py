from __future__ import annotations

from typing import Callable, Type
from typing import TYPE_CHECKING

from calcora.globals import BaseOps

from calcora.core.registry import FunctionRegistry

if TYPE_CHECKING:
  from calcora.core.expression import Expr

Neg : Callable[[], Type[Expr]] = lambda: FunctionRegistry.get('Neg')
Mul : Callable[[], Type[Expr]] = lambda: FunctionRegistry.get('Mul')
Add : Callable[[], Type[Expr]] = lambda: FunctionRegistry.get('Add')

class PrintableOp:
  def __init__(self, *args: Expr) -> None:
    self.args = args
    self.fxn = BaseOps.NoOp

  def __eq__(self, other: object) -> bool:
    return type(self) is type(other) and self.args == other.args # type: ignore
  
  def _print_repr(self) -> str: raise NotImplementedError()
  def _print_latex(self) -> str: raise NotImplementedError()
  def __repr__(self) -> str: return self._print_repr()

class PrintableSub(PrintableOp): 
  def __init__(self, x: Expr, y: Expr, type_cast: bool = False) -> None:
    self.x = x
    self.y = y
    self.priority = 1
    super().__init__(x, y)
  
  def _print_repr(self) -> str:
    x = self.x._print_repr()
    y = self.y._print_repr()
    if self.x.priority < self.priority and not isinstance(self.x, Neg()): x = f'({x})'
    if self.y.priority < self.priority or isinstance(self.y, PrintableSub) or isinstance(self.y, Neg()) or isinstance(self.y, Add()): y = f'({y})'
    return f'{x} - {y}'
  
  def _print_latex(self) -> str:
    x = self.x._print_latex()
    y = self.y._print_latex()
    if self.x.priority < self.priority and not isinstance(self.x, Neg()): x = f'\\left({x}\\right)'
    if self.y.priority < self.priority or isinstance(self.y, PrintableSub) or isinstance(self.y, Neg()) or isinstance(self.y, Add()): y = f'\\left({y}\\right)'
    return f'{x} - {y}'

class PrintableDiv(PrintableOp):
  def __init__(self, x: Expr, y: Expr, type_cast: bool = False) -> None:
    self.x = x
    self.y = y
    self.priority = 2
    super().__init__(x, y)
  
  def _print_repr(self) -> str:
    x = self.x._print_repr()
    y = self.y._print_repr()
    if self.x.priority < self.priority or isinstance(self.x, PrintableDiv): x = f'({x})'
    if self.y.priority < self.priority or isinstance(self.y, PrintableDiv) or isinstance(self.y, Mul()): y = f'({y})'
    return f'{x}/{y}'
  
  def _print_latex(self) -> str:
    x = self.x._print_latex()
    y = self.y._print_latex()
    return f'\\frac{{{x}}}{{{y}}}'
  
class PrintableLn(PrintableOp):
  def __init__(self, x: Expr, type_cast: bool = False) -> None:
    self.x = x
    self.priority = 4
    super().__init__(x)
  
  def _print_repr(self) -> str:
    x = self.x._print_repr()
    return f'ln({x})'
  
  def _print_latex(self) -> str:
    x = self.x._print_latex()
    return f'\\ln\\left({x}\\right)'