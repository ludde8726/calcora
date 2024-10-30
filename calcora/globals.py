from enum import Enum, auto
import os

class PrintOptions(Enum):
  Regular = auto()
  Class = auto()
  Latex = auto()

class BaseOps(Enum):
  @staticmethod
  def _generate_next_value_(name, start, count, last_values):
    return name
  
  # Special ops
  Const = auto()
  Var = auto()

  # Base ops
  Neg = auto()
  Add = auto()
  Mul = auto()
  Pow = auto()
  Log = auto()

  # NoOps
  AnyOp = auto()
  NoOp = auto()

class Settings:
  DebugLevel = int(os.getenv('DEBUG', 0))
  Printing = PrintOptions.Regular
  Precision = 10