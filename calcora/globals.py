from enum import auto, Enum

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

  # NoOps
  AnyOp = auto()
  NoOp = auto()

class _EvalContext:
  def __init__(self):
    self._precision = 16

  @property
  def precision(self) -> int:
    return self._precision
  
  @precision.setter
  def precision(self, value: int):
    if not isinstance(value, int): raise TypeError(f"Invalid type {type(value)} for precision, must be of type int")
    self._precision = value
    mp.dps = self._precision

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
    if not isinstance(value, bool): raise TypeError(f"Invalid type {type(bool)} for rewrite value, must be of type bool")
    self._rewrite = value

  @property
  def simplify(self) -> bool: return self._simplify
  
  @simplify.setter
  def simplify(self, value: bool): 
    if not isinstance(value, bool): raise TypeError(f"Invalid type {type(bool)} for simplify value, must be of type bool")
    self._simplify = value

class _DebugContext:
  def __init__(self):
    self._debug_level = 0

  @property
  def level(self) -> int:
    return self._debug_level
  
  @level.setter
  def level(self, value: int):
    if not isinstance(value, int): raise TypeError(f"Invalid type {type(value)} for debug level, must be of type int")
    self._debug_level = value

ec = _EvalContext()
pc = _PrintingContext()
dc = _DebugContext()
