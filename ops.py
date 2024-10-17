from __future__ import annotations

from enum import auto, Enum
import math
from typing import Tuple


class BaseOps(Enum):
  @staticmethod
  def _generate_next_value_(name, start, count, last_values):
    return name
  
  # Base ops
  Const = auto()
  Var = auto()
  Neg = auto()

  Add = auto()
  Mul = auto()
  Exp = auto()
  Log = auto()

  # Fake ops
  Sub = auto()
  Div = auto()

  # NoOps
  AnyOp = auto()


class DType(Enum):
  int = auto()
  float = auto()

class Op:
  def __init__(self, *args) -> None:
    self.args: Tuple[Op, ...] = args
    assert self.__class__.__name__ in [op.value for op in BaseOps]
    self.fxn: BaseOps = BaseOps(self.__class__.__name__)

  def __eq__(self, other):
    return isinstance(other, Op) and self.fxn == other.fxn and self.args == other.args
  
  def differentiate(self, var: Var) -> Op: raise NotImplementedError()

  def eval(self) -> float: raise NotImplementedError()
  
class Var(Op):
  def __init__(self, name: str) -> None:
    self.name = name
    super().__init__(name)
  
  def differentiate(self, var: Var) -> Op: 
    return Const(1) if self == var else Const(0)

  def __repr__(self) -> str:
    return self.name
  
class Const(Op):
  def __init__(self, x: float) -> None:
    assert x >= 0
    self.x = x
    super().__init__(x)
  
  def eval(self) -> float:
    return self.x
  
  def differentiate(self, var: Var) -> Op: return Const(0)
  
  def __repr__(self) -> str:
    return f'{self.x}'
  
class Add(Op):
  def __init__(self, x: Op, y: Op) -> None:
    self.x = x
    self.y = y
    super().__init__(x, y)

  def eval(self):
    return self.x.eval() + self.y.eval()
  
  def differentiate(self, var: Var) -> Op:
    return Add(self.x.differentiate(var), self.y.differentiate(var))
  
  def __repr__(self) -> str:
    return f'({self.x} + {self.y})'

class Neg(Op):
  def __init__(self, x: Op) -> None:
    self.x = x
    super().__init__(x)

  def eval(self) -> float:
    return -self.x.eval()
  
  def differentiate(self, var: Var) -> Op:
    return Neg(self.x.differentiate(var))
  
  def __repr__(self) -> str:
    return f'-({self.x})'
  
class Mul(Op):
  def __init__(self, x: Op, y: Op) -> None:
    self.x = x
    self.y = y
    super().__init__(x, y)

  def eval(self) -> float:
    return self.x.eval() * self.y.eval()
  
  def differentiate(self, var: Var) -> Op:
    return Add(Mul(self.x.differentiate(var), self.y), Mul(self.x, self.y.differentiate(var)))
  
  def __repr__(self) -> str:
    return f'({self.x} * {self.y})'

class Log(Op):
  def __init__(self, x: Op, base: Op) -> None:
    self.x = x
    self.base = base
    super().__init__(x, base)
  
  def eval(self) -> float:
    return math.log(self.x.eval(), self.base.eval())
  
  def differentiate(self, var: Var) -> Op:
    return Div(
              Sub(
                Div(
                  Mul(self.x.differentiate(var), Log(self.base, Const(math.e))), 
                  self.x
                ), 
                Div(
                  Mul(self.base.differentiate(var), Log(self.x, Const(math.e))), 
                  self.base)
                ), 
              Exp(Log(self.base, Const(math.e)), Const(2))
            )
  
  def __repr__(self) -> str:
    return f'log_{self.base}({self.x})'
  
class Exp(Op):
  def __init__(self, x: Op, y: Op) -> None:
    self.x = x
    self.y = y
    super().__init__(x, y)

  def eval(self) -> float:
    return self.x.eval() ** self.y.eval()
  
  def differentiate(self, var: Var) -> Op:
    return Add(Mul(Mul(self.y, Exp(self.x, Sub(self.y, Const(1)))), self.x.differentiate(var)),
               Mul(Mul(Exp(self.x, self.y), Log(self.x, Const(math.e))), self.y.differentiate(var)))
  
  def __repr__(self) -> str:
    return f'({self.x})^({self.y})'
  
class Div(Op):
  def __new__(cls, x: Op, y: Op) -> Op:
    if y == Const(0): raise ZeroDivisionError('Denominator cannot be zero!')
    return Mul(x, Exp(y, Neg(Const(1))))
  
class Sub(Op):
  def __new__(cls, x: Op, y: Op) -> Op:
    return Add(x, Neg(y))
  
if __name__ == '__main__':
  # Constants
  const_3 = Const(3) # 3
  const_5 = Const(5) # 5
  const_7 = Const(7) # 7
  const_2 = Const(2) # 2
  const_4 = Const(4) # 4

  # Negate 5
  neg_5 = Neg(const_5)

  # 3 * -5
  mul_3_neg5 = Mul(const_3, neg_5)

  # 7 + 2
  add_7_2 = Add(const_7, const_2)

  # (7 + 2) * 4
  mul_add4 = Mul(add_7_2, const_4)

  # Final expression: -((3 * -5) + ((7 + 2) * 4))
  complex_expr = Neg(Add(mul_3_neg5, mul_add4))

  # Print the expression
  print(f'Expression: {complex_expr}')

  # Evaluate the expression
  result = complex_expr.eval()
  print(f'Result: {result}')
