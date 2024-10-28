from calcora.expression import Expr, BaseOps

class PrintableSub(Expr): 
  def __init__(self, x: Expr, y: Expr) -> None:
    self.x = x
    self.y = y
    self.args = (x,y,)
    self.fxn = BaseOps.NoOp
    self.priority = 1

class PrintableDiv(Expr):
  def __init__(self, x: Expr, y: Expr) -> None:
    self.x = x
    self.y = y
    self.args = (x,y,)
    self.fxn = BaseOps.NoOp
    self.priority = 2
  
class PrintableLn(Expr):
  def __init__(self, x: Expr) -> None:
    self.x = x
    self.args = (x,)
    self.fxn = BaseOps.NoOp
    self.priority = 4