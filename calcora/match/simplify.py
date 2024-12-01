from __future__ import annotations

from typing import TYPE_CHECKING

from calcora.match.match import SymbolicPatternMatcher
from calcora.match.partial_eval import partial_eval

if TYPE_CHECKING:
  from calcora.core.expression import Expr

def simplify(expression: Expr):
  simplified_expr: Expr = expression
  simplified_expr = SymbolicPatternMatcher.match(expression)
  simplified_expr = partial_eval(simplified_expr)
  if simplified_expr != expression: simplified_expr = simplify(simplified_expr)
  return simplified_expr

