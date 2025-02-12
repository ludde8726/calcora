from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

from calcora.match.partial_eval import partial_eval
from calcora.match.pattern import Pattern, MatchedConstLike, MatchedSymbol, ConstLike, NamedAny

from calcora.core.ops import Add, AnyOp, Complex, Const, Pow, Log, Mul, Neg
from calcora.core.constants import Zero, One, NegOne, Two

from calcora.utils import dprint

if TYPE_CHECKING:
  from calcora.core.expression import Expr

class PatternMatcher:
  def __init__(self, patterns: Optional[List[Pattern]] = None) -> None:
    self.patterns = patterns if patterns else list()
  
  def add_rules(self, patterns: List[Pattern]) -> None:
    self.patterns.extend(patterns)
  
  def match(self, expression: Expr, depth: int = 0, print_debug: bool = True) -> Expr:
    simplified_expr: Expr = expression
    for pattern in self.patterns:
      simplified_expr = pattern.match(simplified_expr)
    if matched := (simplified_expr != expression): simplified_expr = self.match(simplified_expr, depth=depth+1, print_debug=print_debug)
    if depth == 0 and matched and print_debug: dprint(f'$ -> $', 2, 'blue', expression, simplified_expr)
    return simplified_expr
  
SymbolicPatternMatcher = PatternMatcher([
  Pattern(Add(AnyOp(), Zero), lambda x: x), # x + 0 = x

  Pattern(Neg(Neg(AnyOp())), lambda x: x), # -(-x) = x
  Pattern(Neg(Zero), lambda: Zero), # -(0) = 0

  Pattern(Mul(AnyOp(), One), lambda x: x), # 1 * x = x

  Pattern(Mul(AnyOp(), Zero), lambda x: Zero), # x * 0 = 0

  Pattern(Pow(Zero, AnyOp()), lambda x: Zero), # 0 ^ x = 0
  Pattern(Pow(AnyOp(), Zero), lambda x: One), # x ^ 0 = 1

  Pattern(Pow(One, AnyOp()), lambda x: One), # 1 ^ x = 1
  Pattern(Pow(AnyOp(), One), lambda x: x), # x ^ 1 = x

  Pattern(Mul(AnyOp(), NegOne), lambda x: Neg(x)), # x * (-1) = -x

  Pattern(Log(MatchedConstLike('x'), MatchedConstLike('x')), lambda x: One), # Log_x(x) = 1

  Pattern(Add(MatchedSymbol('x'), Neg(MatchedSymbol('x'))), lambda x: Zero), # x - x = 0

  Pattern(Mul(MatchedSymbol('x'), Pow(MatchedSymbol('x'), NegOne)), lambda x: One), # x * x^(-1) = x/x = 1
  
  Pattern(Mul(MatchedSymbol('x'), MatchedSymbol('x')), lambda x: Pow(x, Two)), # x * x = x^2
  
  Pattern(Add(MatchedSymbol('x'), Mul(ConstLike('y'), MatchedSymbol('x'))), lambda x,y: Mul(partial_eval(Add(y, One)), x)), # x + yx = (y+1)x where y is a constant

  Pattern(Add(Mul(ConstLike('y'), MatchedSymbol('x')), Mul(ConstLike('z'), MatchedSymbol('x'))), lambda x,y,z: Mul(partial_eval(Add(y, z)), x)), # yx + zx = (y+z)x where y and z are constants

  Pattern(Mul(MatchedSymbol('x'), Pow(MatchedSymbol('x'), NamedAny('y'))), lambda x,y: Pow(x, partial_eval(Add(y, One)))),    # x * x^y = x^(y+1) where y is a constant
  Pattern(Mul(Pow(MatchedSymbol('x'), NamedAny('y')), Pow(MatchedSymbol('x'), NamedAny('z'))), lambda x,y,z: Pow(x, Add(y, z))),    # x^y * x^z = x^(y+z)
  Pattern(Pow(Pow(NamedAny('x'), NamedAny('y')), NamedAny('z')), lambda x,y,z: Pow(x, Mul(y, z))),                                  # (x^y)^z = x^(y*z)

  Pattern(Complex(NamedAny('x'), Zero), lambda x: x) # x + 0i = x
])