from __future__ import annotations

from typing import TYPE_CHECKING

from calcora.match.match import Pattern
from calcora.core.ops import Add, Neg, Mul, Pow, Log, Const, Div, Sub, Ln
from calcora.core.constants import E
from calcora.match.match import NamedAny
from calcora.globals import BaseOps
from calcora.utils import has_constant, is_const_like
from calcora.core.number import Number

if TYPE_CHECKING:
  from calcora.core.expression import Expr

SubOpPattern = lambda x: Pattern.match_static(x, Add(NamedAny('x'), Neg(NamedAny('y'))))
DivOpPattern = lambda x: Pattern.match_static(x, Mul(NamedAny('x'), Pow(NamedAny('y'), Neg(Const(1)))))
LnOpPattern = lambda x: Pattern.match_static(x, Log(NamedAny('x'), E))

def partial_eval(x: Expr) -> Expr:
  if not (x.fxn == BaseOps.Const or x.fxn == BaseOps.Var or x.fxn == BaseOps.Constant):
    is_sub = SubOpPattern(x) # keys: x, y
    is_div = DivOpPattern(x) # keys: x, y
    is_ln = LnOpPattern(x)   # keys: x
    if is_sub[0]: 
      new_args = [partial_eval(arg) for arg in (is_sub[1]['x'], is_sub[1]['y'])]
      x = Sub(*new_args)
    elif is_div[0]: 
      new_args = [partial_eval(arg) for arg in (is_sub[1]['x'], is_sub[1]['y'])]
      x = Div(*new_args)
    elif is_ln[0]: 
      new_args = [partial_eval(arg) for arg in (is_sub[1]['x'], )]
      x = Ln(*new_args)
    else: 
      new_args = [partial_eval(arg) for arg in x.args]
      x = x.__class__(*new_args)
    if is_const_like(x) and not has_constant(x): return Number(x.eval())
    return x
  return x