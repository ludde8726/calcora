from __future__ import annotations

from typing import TYPE_CHECKING

from calcora.globals import ec

from calcora.match.simplify import simplify

if TYPE_CHECKING:
  from calcora.core.expression import Expr
  from calcora.core.ops import Var

def diff(op: Expr, var: Var, degree: int = 1) -> Expr:
  for _ in range(degree): 
    op = op.differentiate(var)
    if ec.always_simplify: op = simplify(op)
  return op