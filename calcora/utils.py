from __future__ import annotations

from typing import Any, Iterable, Optional, Type, TypeGuard, TypeVar, Union
from typing import TYPE_CHECKING

import re

from calcora.globals import BaseOps, PrintOptions
from calcora.globals import ec, dc, pc
from calcora.types import CalcoraNumber, NumberLike

from mpmath import mpf, mpc, workdps

if TYPE_CHECKING:
  from calcora.core.expression import Expr
  from calcora.core.ops import AnyOp, Var
  T = TypeVar('T', bound=Expr)

class TerminalColors:
  # Text colors
  black = '\033[30m'
  red = '\033[31m'
  green = '\033[32m'
  yellow = '\033[33m'
  blue = '\033[34m'
  magenta = '\033[35m'
  cyan = '\033[36m'
  white = '\033[37m'
  
  # Bright text colors
  bright_black = '\033[90m'
  bright_red = '\033[91m'
  bright_green = '\033[92m'
  bright_yellow = '\033[93m'
  bright_blue = '\033[94m'
  bright_magenta = '\033[95m'
  bright_cyan = '\033[96m'
  bright_white = '\033[97m'
  
  # Background colors
  bg_black = '\033[40m'
  bg_red = '\033[41m'
  bg_green = '\033[42m'
  bg_yellow = '\033[43m'
  bg_blue = '\033[44m'
  bg_magenta = '\033[45m'
  bg_cyan = '\033[46m'
  bg_white = '\033[47m'
  
  # Bright background colors
  bg_bright_black = '\033[100m'
  bg_bright_red = '\033[101m'
  bg_bright_green = '\033[102m'
  bg_bright_yellow = '\033[103m'
  bg_bright_blue = '\033[104m'
  bg_bright_magenta = '\033[105m'
  bg_bright_cyan = '\033[106m'
  bg_bright_white = '\033[107m'
  
  # Text styles
  reset = '\033[0m'
  bold = '\033[1m'
  dim = '\033[2m'
  italic = '\033[3m'
  underline = '\033[4m'
  blink = '\033[5m'
  reverse = '\033[7m'
  hidden = '\033[8m'

def is_op_type(op: Expr, op_type: Type[T]) -> TypeGuard[T]: 
  if not isinstance(op_type, str): raise TypeError("This function should only be called with string ops and is mainly used for type checkers!")
  return op.fxn == BaseOps(op_type)
def is_any_op(op: Expr) -> TypeGuard[AnyOp]: return op.fxn == BaseOps.AnyOp

def has_constant(op: Expr) -> bool:
  if op.fxn == BaseOps.Constant: return True
  if op.fxn == BaseOps.Const or op.fxn == BaseOps.Var: return False
  return any(has_constant(arg) for arg in op.args)

def is_const_like(op: Expr) -> bool:
  if op.fxn == BaseOps.Const or op.fxn == BaseOps.Constant: return True
  elif op.fxn == BaseOps.Var: return False
  return all(is_const_like(arg) for arg in op.args)

def reconstruct_op(op: Expr, *args: Any) -> Expr:
  if op.fxn == BaseOps.Complex: return op.__class__(*args, representation=op.representation) # type: ignore
  return op.__class__(*args)

def colored(string: str, color: Union[str, Iterable[str]]) -> str:
  colors = [color] if isinstance(color, str) else color
  invalid_colors = [c for c in colors if not hasattr(TerminalColors, c)]
  if invalid_colors: raise ValueError(f"Invalid color(s): {', '.join(invalid_colors)}")
  color_codes = ''.join(getattr(TerminalColors, c) for c in colors)
  return f"{color_codes}{string}{TerminalColors.reset}"

def mpmathcast(x: NumberLike, precision: Optional[int] = None) -> CalcoraNumber:
  precision = precision if precision else ec.precision
  with workdps(precision):
    if isinstance(x, (float, int, complex)): return mpc(x)
    elif isinstance(x, str):
      x = x.strip().lower().replace('i', 'j')
      x = re.sub(r'([+-])j$', r'\g<1>1j', x, flags=re.IGNORECASE)
      x = re.sub(r'^j', '1j', x, flags=re.IGNORECASE)
      x = re.sub(r'([+-])j', r'\g<1>1j', x, flags=re.IGNORECASE)

      complex_match = re.match(r'^(?P<real>[-+]?\d*\.?\d+)?(?P<imag>[-+]?\d*\.?\d+)[ij]$', x)
      if complex_match:
          real = complex_match.group('real') or '0'
          imag = complex_match.group('imag')
          return mpc(real, imag)
      if re.match(r'^[-+]?\d*\.?\d+$', x):
          return mpc(x, '0')
      raise ValueError(f"Invalid number format: '{x}'")
    elif isinstance(x, (mpf, mpc)): return mpc(x)
    else: raise TypeError(f"Invalid type {type(x)} for type conversion to mpmath mpc")



def dprint(message: str, min_level: int, color: Union[str, Iterable[str]], *args: Any, rewrite: bool = True) -> None:
  if not (dc >= min_level) or dc.in_debug: return
  original_settings = (pc.print_type, pc.simplify, pc.rewrite)
  pc.print_type, pc.simplify, pc.rewrite, dc.in_debug = PrintOptions.Regular, False, rewrite, True
  for arg in args: message = message.replace("$", str(arg), 1)
  print(colored(message, color))
  pc.print_type, pc.simplify, pc.rewrite, dc.in_debug = *original_settings, False