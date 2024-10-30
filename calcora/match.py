from __future__ import annotations

from typing import Callable, Dict, List, Optional, TYPE_CHECKING

import calcora as c
from calcora.globals import BaseOps
from calcora.ops import Add, AnyOp, Const, Pow, Log, Mul, Neg
from calcora.utils import is_op_type, is_const_like, reconstruct_op, ConstLike, MatchedSymbol, NamedAny

if TYPE_CHECKING:
  from calcora.expression import Expr

class Pattern:
  def __init__(self, pattern: Expr, replacement: Callable[..., Expr]) -> None:
    self.pattern = pattern
    self.replacement = replacement
    self._binding: Dict[str, Expr] = {}

  def match(self, op: Expr) -> Expr:
    self._binding = {}
    new_args = [self.match(arg) for arg in op.args] if op.fxn != BaseOps.Const and op.fxn != BaseOps.Var else op.args
    if op.fxn == BaseOps.Const: return op
    op = reconstruct_op(op, *new_args)
    if op.fxn == self.pattern.fxn and len(op.args) == len(self.pattern.args):
      if self._match(op, self.pattern):
        return self.replacement(**self._binding)
    return reconstruct_op(op, *new_args)
  
  def _match(self, op: Expr, subpattern: Expr) -> bool:
    if not (len(op.args) == len(subpattern.args)) and not subpattern.fxn == BaseOps.AnyOp: return False
    
    if is_op_type(subpattern, AnyOp):
      if subpattern.assert_const_like and not is_const_like(op): return False
      if subpattern.match and subpattern.name in self._binding:
        return self._binding[subpattern.name] == op
      self._binding[subpattern.name] = op
      return True
  
    if op.fxn == subpattern.fxn and len(op.args) == len(subpattern.args):
      if op.fxn == BaseOps.Const: return op.args == subpattern.args
      if subpattern.args:
        return all(self._match(op_arg, sub_arg) for op_arg, sub_arg in zip(op.args, subpattern.args))
      
    return False

class PatternMatcher:
  def __init__(self, patterns: Optional[List[Pattern]] = None) -> None:
    self.patterns = patterns if patterns else list()
  
  def add_rules(self, patterns: List[Pattern]):
    self.patterns.extend(patterns)
  
  def match(self, expression: Expr):
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

  Pattern(Log(ConstLike('x'), ConstLike('x')), lambda x: Const(1)), # Log_x(x) = 1

  Pattern(Add(MatchedSymbol('x'), Neg(MatchedSymbol('x'))), lambda x: Const(0)), # x - x = 0

  Pattern(Mul(MatchedSymbol('x'), Pow(MatchedSymbol(name='x'), 
                                                Neg(Const(1)))), lambda x: Const(1)), # x * x^(-1) = x/x = 1
  
  Pattern(Mul(MatchedSymbol('x'), MatchedSymbol('x')), lambda x: Pow(x, Const(2))), # x * x = x^2
  
  Pattern(Add(MatchedSymbol('x'), Mul(ConstLike('y'), MatchedSymbol('x'))), lambda x,y: Mul(Const(Add(y, Const(1)).eval()), x)), # x + yx = (y+1)x where y is a constant
  Pattern(Add(MatchedSymbol('x'), Mul(MatchedSymbol('x'), ConstLike('y'))), lambda x,y: Mul(Const(Add(y, Const(1)).eval()), x)), # x + xy = (y+1)x where y is a constant
  Pattern(Add(Mul(ConstLike('y'), MatchedSymbol('x')), MatchedSymbol('x')), lambda x,y: Mul(Const(Add(y, Const(1)).eval()), x)), # yx + x = (y+1)x where y is a constant
  Pattern(Add(Mul(MatchedSymbol('x'), ConstLike('y')), MatchedSymbol('x')), lambda x,y: Mul(Const(Add(y, Const(1)).eval()), x)), # xy + x = (y+1)x where y is a constant

  Pattern(Add(Mul(ConstLike('y'), MatchedSymbol('x')), Mul(ConstLike('z'), MatchedSymbol('x'))), lambda x,y,z: Mul(Const(Add(y, z).eval()), x)), # yx + zx = (y+z)x where y and z are constants
  Pattern(Add(Mul(MatchedSymbol('x'), ConstLike('y')), Mul(ConstLike('z'), MatchedSymbol('x'))), lambda x,y,z: Mul(Const(Add(y, z).eval()), x)), # xy + zx = (y+z)x where y and z are constants
  Pattern(Add(Mul(ConstLike('y'), MatchedSymbol('x')), Mul(MatchedSymbol('x'), ConstLike('z'))), lambda x,y,z: Mul(Const(Add(y, z).eval()), x)), # yx + xz = (y+z)x where y and z are constants
  Pattern(Add(Mul(MatchedSymbol('x'), ConstLike('y')), Mul(MatchedSymbol('x'), ConstLike('z'))), lambda x,y,z: Mul(Const(Add(y, z).eval()), x)), # xy + xz = (y+z)x where y and z are constants

  Pattern(Mul(MatchedSymbol('x'), Pow(MatchedSymbol('x'), ConstLike('y'))), lambda x,y: Pow(x, Const(Add(y, Const(1)).eval()))),    # x * x^y = x^(y+1) where y is a constant
  Pattern(Mul(Pow(MatchedSymbol('x'), ConstLike('y')), MatchedSymbol('x')), lambda x,y: Pow(x, Const(Add(y, Const(1)).eval()))),    # x^y * x = x^(y+1) where y is a constant
  Pattern(Mul(Pow(MatchedSymbol('x'), NamedAny('y')), Pow(MatchedSymbol('x'), NamedAny('z'))), lambda x,y,z: Pow(x, Add(y, z))),    # x^y * x^z = x^(y+z)
  Pattern(Pow(Pow(NamedAny('x'), NamedAny('y')), NamedAny('z')), lambda x,y,z: Pow(x, Mul(y, z))),                                  # (x^y)^z = x^(y*z)
])