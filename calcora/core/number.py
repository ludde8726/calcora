from __future__ import annotations

from typing import TYPE_CHECKING

from calcora.types import NumberLike, mpf, mpc

if TYPE_CHECKING:
  from .expression import Expr

class Number:
  def __new__(cls, x: NumberLike) -> Expr:
    from calcora.core.ops import Neg, Const, Complex
    if isinstance(x, complex):
      if x.imag: return Complex(Const(x.real) if x.real >= 0 else Neg(Const(abs(x.real))), Const(x.imag) if x.imag >= 0 else Neg(Const(abs(x.imag))))
      else: return Const(x.real) if x.real >= 0 else Neg(Const(abs(x.real)))
    elif isinstance(x, str):
      x = ''.join(x.split()).replace('i', 'j')
      x = complex(x)
      if x.imag: return Number(x)
      return Number(x.real) if x.real >= 0 else Neg(Number(abs(x.real)))
    elif isinstance(x, (int, float)): return Const(x) if x >= 0 else Neg(Const(abs(x)))
    elif isinstance(x, (mpf, mpc)): 
      if x.imag: return Complex(Const(x.real) if x.real >= 0 else Neg(Const(abs(x.real))), Const(x.imag) if x.imag >= 0 else Neg(Const(abs(x.imag))))
      return Const(x.real) if x.real >= 0 else Neg(Const(abs(x.real)))
    raise TypeError(f"Cannot create number from type {type(x)}, must be type int, float, str, complex, mpf, or mpc.")

