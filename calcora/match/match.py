from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

from calcora.match.partial_eval import partial_eval
from calcora.match.pattern import Pattern, MatchedConstLike, MatchedSymbol, ConstLike, NamedAny

from calcora.core.ops import Add, AnyOp, Complex, Const, Pow, Log, Mul, Neg

if TYPE_CHECKING:
  from calcora.core.expression import Expr

class PatternMatcher:
  def __init__(self, patterns: Optional[List[Pattern]] = None) -> None:
    self.patterns = patterns if patterns else list()
  
  def add_rules(self, patterns: List[Pattern]) -> None:
    self.patterns.extend(patterns)
  
  def match(self, expression: Expr) -> Expr:
    simplified_expr: Expr = expression
    for pattern in self.patterns:
      simplified_expr = pattern.match(simplified_expr)
    if simplified_expr != expression: simplified_expr = self.match(simplified_expr)
    return simplified_expr
  
SymbolicPatternMatcher = PatternMatcher([
  Pattern(Add(AnyOp(), Const(0)), lambda x: x), # x + 0 = x
  Pattern(Add(Const(0), AnyOp()), lambda x: x), # 0 + x = x

  Pattern(Neg(Neg(AnyOp())), lambda x: x), # -(-x) = x
  Pattern(Neg(Const(0)), lambda: Const(0)), # -(0) = 0

  Pattern(Mul(AnyOp(), Const(1)), lambda x: x), # 1 * x = x
  Pattern(Mul(Const(1), AnyOp()), lambda x: x), # x * 1 = x

  Pattern(Mul(AnyOp(), Const(0)), lambda x: Const(0)), # x * 0 = 0
  Pattern(Mul(Const(0), AnyOp()), lambda x: Const(0)), # 0 * x = 0

  Pattern(Pow(Const(0), AnyOp()), lambda x: Const(0)), # 0 ^ x = 0
  Pattern(Pow(AnyOp(), Const(0)), lambda x: Const(1)), # x ^ 0 = 1

  Pattern(Pow(Const(1), AnyOp()), lambda x: Const(1)), # 1 ^ x = 1
  Pattern(Pow(AnyOp(), Const(1)), lambda x: x), # x ^ 1 = x

  Pattern(Mul(AnyOp(), Neg(Const(1))), lambda x: Neg(x)), # x * (-1) = -x
  Pattern(Mul(Neg(Const(1)), AnyOp()), lambda x: Neg(x)), # (-1) * x = -x

  Pattern(Log(MatchedConstLike('x'), MatchedConstLike('x')), lambda x: Const(1)), # Log_x(x) = 1

  Pattern(Add(MatchedSymbol('x'), Neg(MatchedSymbol('x'))), lambda x: Const(0)), # x - x = 0

  Pattern(Mul(MatchedSymbol('x'), Pow(MatchedSymbol(name='x'), 
                                                Neg(Const(1)))), lambda x: Const(1)), # x * x^(-1) = x/x = 1
  
  Pattern(Mul(MatchedSymbol('x'), MatchedSymbol('x')), lambda x: Pow(x, Const(2))), # x * x = x^2
  
  Pattern(Add(MatchedSymbol('x'), Mul(ConstLike('y'), MatchedSymbol('x'))), lambda x,y: Mul(partial_eval(Add(y, Const(1))), x)), # x + yx = (y+1)x where y is a constant
  Pattern(Add(MatchedSymbol('x'), Mul(MatchedSymbol('x'), ConstLike('y'))), lambda x,y: Mul(partial_eval(Add(y, Const(1))), x)), # x + xy = (y+1)x where y is a constant
  Pattern(Add(Mul(ConstLike('y'), MatchedSymbol('x')), MatchedSymbol('x')), lambda x,y: Mul(partial_eval(Add(y, Const(1))), x)), # yx + x = (y+1)x where y is a constant
  Pattern(Add(Mul(MatchedSymbol('x'), ConstLike('y')), MatchedSymbol('x')), lambda x,y: Mul(partial_eval(Add(y, Const(1))), x)), # xy + x = (y+1)x where y is a constant

  Pattern(Add(Mul(ConstLike('y'), MatchedSymbol('x')), Mul(ConstLike('z'), MatchedSymbol('x'))), lambda x,y,z: Mul(partial_eval(Add(y, z)), x)), # yx + zx = (y+z)x where y and z are constants
  Pattern(Add(Mul(MatchedSymbol('x'), ConstLike('y')), Mul(ConstLike('z'), MatchedSymbol('x'))), lambda x,y,z: Mul(partial_eval(Add(y, z)), x)), # xy + zx = (y+z)x where y and z are constants
  Pattern(Add(Mul(ConstLike('y'), MatchedSymbol('x')), Mul(MatchedSymbol('x'), ConstLike('z'))), lambda x,y,z: Mul(partial_eval(Add(y, z)), x)), # yx + xz = (y+z)x where y and z are constants
  Pattern(Add(Mul(MatchedSymbol('x'), ConstLike('y')), Mul(MatchedSymbol('x'), ConstLike('z'))), lambda x,y,z: Mul(partial_eval(Add(y, z)), x)), # xy + xz = (y+z)x where y and z are constants

  Pattern(Mul(MatchedSymbol('x'), Pow(MatchedSymbol('x'), ConstLike('y'))), lambda x,y: Pow(x, partial_eval(Add(y, Const(1))))),    # x * x^y = x^(y+1) where y is a constant
  Pattern(Mul(Pow(MatchedSymbol('x'), ConstLike('y')), MatchedSymbol('x')), lambda x,y: Pow(x, partial_eval(Add(y, Const(1))))),    # x^y * x = x^(y+1) where y is a constant
  Pattern(Mul(Pow(MatchedSymbol('x'), NamedAny('y')), Pow(MatchedSymbol('x'), NamedAny('z'))), lambda x,y,z: Pow(x, Add(y, z))),    # x^y * x^z = x^(y+z)
  Pattern(Pow(Pow(NamedAny('x'), NamedAny('y')), NamedAny('z')), lambda x,y,z: Pow(x, Mul(y, z))),                                  # (x^y)^z = x^(y*z)

  Pattern(Complex(NamedAny('x'), Const(0)), lambda x: x) # x + 0i = x
])