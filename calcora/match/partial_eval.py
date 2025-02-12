from __future__ import annotations

from typing import Callable, Dict, Tuple
from typing import TYPE_CHECKING

from calcora.globals import BaseOps
from calcora.utils import has_constant, is_const_like, reconstruct_op

from calcora.match.pattern import NamedAny
from calcora.match.pattern import Pattern

from calcora.core.constants import E, NegOne
from calcora.core.ops import Add, Const, Log, Mul, Neg, Pow
from calcora.core.registry import Dispatcher
from calcora.core.numeric import Numeric

if TYPE_CHECKING:
  from calcora.core.expression import Expr

SubOpPattern : Callable[[Expr], Tuple[bool, Dict[str, Expr]]] = lambda x: Pattern.match_static(x, Add(NamedAny('x'), Neg(NamedAny('y'))))
DivOpPattern : Callable[[Expr], Tuple[bool, Dict[str, Expr]]] = lambda x: Pattern.match_static(x, Mul(NamedAny('x'), Pow(NamedAny('y'), Neg(Const(Numeric(1))))))
LnOpPattern : Callable[[Expr], Tuple[bool, Dict[str, Expr]]] = lambda x: Pattern.match_static(x, Log(NamedAny('x'), E))

Sub : Callable[[Expr, Expr], Expr] = lambda x,y: Add(x, Neg(y))
Div : Callable[[Expr, Expr], Expr] = lambda x,y: Mul(x, Pow(y, NegOne))
Ln : Callable[[Expr], Expr] = lambda x: Log(x, E)

def partial_eval(x: Expr) -> Expr:
  if not (x.fxn == BaseOps.Const or x.fxn == BaseOps.Var or x.fxn == BaseOps.Constant):
    is_sub = SubOpPattern(x) # keys: x, y
    is_div = DivOpPattern(x) # keys: x, y
    is_ln = LnOpPattern(x)   # keys: x
    if is_sub[0]: 
      new_args = [partial_eval(arg) for arg in (is_sub[1]['x'], is_sub[1]['y'])]
      x = Sub(new_args[0], new_args[1])
    elif is_div[0]: 
      new_args = [partial_eval(arg) for arg in (is_div[1]['x'], is_div[1]['y'])]
      x = Div(new_args[0], new_args[1])
    elif is_ln[0]: 
      new_args = [partial_eval(arg) for arg in (is_ln[1]['x'],)]
      x = Ln(new_args[0])
    else: 
      new_args = [partial_eval(arg) for arg in x.args]
      x = reconstruct_op(x, *new_args)
  if is_const_like(x) and not has_constant(x): return Dispatcher.typecast(x._eval())
  return x