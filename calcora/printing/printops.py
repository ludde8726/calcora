from __future__ import annotations
from typing import TYPE_CHECKING

from calcora.globals import BaseOps

if TYPE_CHECKING:
  from calcora.expression import Expr

class PrintableOp:
  def __init__(self, *args: Expr) -> None:
    self.args = args
    self.fxn = BaseOps.NoOp

  def __eq__(self, other):
    return type(self) is type(other) and self.args == other.args

class PrintableSub(PrintableOp): 
  def __init__(self, x: Expr, y: Expr) -> None:
    self.x = x
    self.y = y
    self.priority = 1
    super().__init__(x, y)

class PrintableDiv(PrintableOp):
  def __init__(self, x: Expr, y: Expr) -> None:
    self.x = x
    self.y = y
    self.priority = 2
    super().__init__(x, y)
  
class PrintableLn(PrintableOp):
  def __init__(self, x: Expr) -> None:
    self.x = x
    self.priority = 4
    super().__init__(x)