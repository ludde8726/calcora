from __future__ import annotations

from enum import auto, Enum
import math
from typing import Tuple, Union


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

def ln_repr(self):
  return f'ln({self.x})'

class Op:
  def __init__(self, *args) -> None:
    self.args: Tuple[Op, ...] = args
    assert self.__class__.__name__ in [op.value for op in BaseOps]
    self.fxn: BaseOps = BaseOps(self.__class__.__name__)

  def __eq__(self, other):
    return isinstance(other, Op) and self.fxn == other.fxn and self.args == other.args
  
  @staticmethod
  def cast(x: Union[Op, int, float]) -> Op:
    if not isinstance(x, Op) and not isinstance(x, int) and not isinstance(x, float): raise ValueError(f'Cannot cast type {type(x)} to Op')
    if isinstance(x, Op): return x
    return Const(x)
  
  def __add__(self, other: Union[Op, int, float]) -> Op:
    other = Op.cast(other)
    return Add(self, other)
  
  def __sub__(self, other: Union[Op, int, float]) -> Op:
    other = Op.cast(other)
    return Sub(self, other)
  
  def __mul__(self, other: Union[Op, int, float]) -> Op:
    other = Op.cast(other)
    return Mul(self, other)
  
  def __truediv__(self, other: Union[Op, int, float]) -> Op:
    other = Op.cast(other)
    return Div(self, other)
  
  def __pow__(self, other: Union[Op, int, float]) -> Op:
    other = Op.cast(other)
    return Exp(self, other)
  
  __radd__ = __add__
  __rmul__ = __mul__
  
  def __rsub__(self, other: Union[Op, int, float]) -> Op:
    other = Op.cast(other)
    return Sub(other, self)
  
  def __rtruediv__(self, other: Union[Op, int, float]) -> Op:
    other = Op.cast(other)
    return Div(other, self)

  def __rpow__(self, other: Union[Op, int, float]) -> Op:
    other = Op.cast(other)
    return Exp(other, self)
  
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
  def __init__(self, x: Op, base: Op = Const(10), natrual: bool = False) -> None:
    self.x = x
    self.base = base
    self.natural = natrual
    super().__init__(x, base)
  
  def eval(self) -> float:
    return math.log(self.x.eval(), self.base.eval())
  
  def differentiate(self, var: Var) -> Op:
    return Div(
              Sub(
                Div(
                  Mul(self.x.differentiate(var), Ln(self.base)), 
                  self.x
                ), 
                Div(
                  Mul(self.base.differentiate(var), Ln(self.x)), 
                  self.base)
                ), 
              Exp(Ln(self.base), Const(2))
            )
  
  def __repr__(self) -> str:
    return f'log_{self.base}({self.x})' if not self.natural else f'ln({self.x})'
  
class Exp(Op):
  def __init__(self, x: Op, y: Op) -> None:
    self.x = x
    self.y = y
    super().__init__(x, y)

  def eval(self) -> float:
    return self.x.eval() ** self.y.eval()
  
  def differentiate(self, var: Var) -> Op:
    return Add(Mul(Mul(self.y, Exp(self.x, Sub(self.y, Const(1)))), self.x.differentiate(var)),
               Mul(Mul(Exp(self.x, self.y), Ln(self.x)), self.y.differentiate(var)))
  
  def __repr__(self) -> str:
    return f'({self.x})^({self.y})'
  
class Div(Op):
  def __new__(cls, x: Op, y: Op) -> Op:
    if y == Const(0): raise ZeroDivisionError('Denominator cannot be zero!')
    return Mul(x, Exp(y, Neg(Const(1))))
  
class Sub(Op):
  def __new__(cls, x: Op, y: Op) -> Op:
    return Add(x, Neg(y))
  
class Ln(Op):
  def __new__(cls, x: Op) -> Op:
    return Log(x, Const(math.e), natrual=True)
  
if __name__ == '__main__':
  x = Var('x')
  y = Var('y')

  expr = ((x + 3) / y) * 3 + x * 9
  print(expr)
