from __future__ import annotations

from typing import TYPE_CHECKING

from calcora.globals import BaseOps

from calcora.core.registry import FunctionRegistry

if TYPE_CHECKING:
  from calcora.core.expression import Expr

Neg = lambda: FunctionRegistry.get('Neg')
Mul = lambda: FunctionRegistry.get('Mul')
Add = lambda: FunctionRegistry.get('Add')

class PrintableOp:
  def __init__(self, *args: Expr) -> None:
    self.args = args
    self.fxn = BaseOps.NoOp

  def __eq__(self, other):
    return type(self) is type(other) and self.args == other.args
  
  def _print_repr(self) -> str: raise NotImplementedError()

class PrintableSub(PrintableOp): 
  def __init__(self, x: Expr, y: Expr) -> None:
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


class PrintableDiv(PrintableOp):
  def __init__(self, x: Expr, y: Expr) -> None:
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
  
class PrintableLn(PrintableOp):
  def __init__(self, x: Expr) -> None:
    self.x = x
    self.priority = 4
    super().__init__(x)
  
  def _print_repr(self) -> str:
    x = self.x._print_repr()
    return f'Ln({x})'