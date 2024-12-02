from enum import auto, Enum
import os

from mpmath import mp

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
  Constant = auto()
  Complex = auto()
  Var = auto()

  # Base ops
  Neg = auto()
  Add = auto()
  Mul = auto()
  Pow = auto()
  Log = auto()
  Sin = auto()
  Cos = auto()

  # NoOps
  AnyOp = auto()
  NoOp = auto()

class GlobalCounter:
  num_ops: int = 0
  matches: int = 0

  @staticmethod
  def decrement_ops() -> None: GlobalCounter.num_ops -= 1

class _EvalContext:
  def __init__(self, default: int = 16, always_simplify: bool = True): 
    self._precision = default
    self._always_simplify = always_simplify
  @property
  def precision(self) -> int: return self._precision
  @property
  def always_simplify(self) -> int: return self._precision
  @precision.setter
  def precision(self, value: int):
    if not isinstance(value, int): raise TypeError(f"Invalid type {type(value)} for precision, must be of type int")
    self._precision = value
    mp.dps = self._precision
  @always_simplify.setter
  def always_simplify(self, value: bool): 
    if not isinstance(value, bool): raise TypeError(f"Invalid type {type(value)} for should simplify value, must be of type bool")
    self._always_simplify = value
  

class _PrintingContext:
  def __init__(self):
    self._print_type = PrintOptions.Regular
    self._rewrite = True
    self._simplify = False
  @property
  def print_type(self) -> PrintOptions: return self._print_type
  @print_type.setter
  def print_type(self, value: PrintOptions):
    if not isinstance(value, PrintOptions): raise TypeError(f"Invalid type {type(value)} for print type, must be of type PrintOptions")
    self._print_type = value

  @property
  def rewrite(self) -> bool: return self._rewrite
  @rewrite.setter
  def rewrite(self, value: bool): 
    if not isinstance(value, bool): raise TypeError(f"Invalid type {type(value)} for rewrite value, must be of type bool")
    self._rewrite = value

  @property
  def simplify(self) -> bool: return self._simplify
  @simplify.setter
  def simplify(self, value: bool): 
    if not isinstance(value, bool): raise TypeError(f"Invalid type {type(value)} for simplify value, must be of type bool")
    self._simplify = value

class _DebugContext:
  def __init__(self, default: int = 0): 
    self._debug_level = default
    self.in_debug = False
  @property
  def level(self) -> int: return self._debug_level
  @level.setter
  def level(self, value: int):
    if not isinstance(value, int): raise TypeError(f"Invalid type {type(value)} for debug level, must be of type int")
    self._debug_level = value
  def __eq__(self, other) -> bool: return self._debug_level == other
  def __gt__(self, other: int) -> bool: return self._debug_level > other
  def __lt__(self, other: int) -> bool: return self._debug_level < other
  def __ge__(self, other: int) -> bool: return self._debug_level >= other
  def __le__(self, other: int) -> bool: return self._debug_level <= other

ec = _EvalContext()
pc = _PrintingContext()
dc = _DebugContext(default=int(os.getenv('DEBUG', 0)))
