from __future__ import annotations

from itertools import permutations
from typing import Callable, Dict, Tuple
from typing import TYPE_CHECKING

from calcora.globals import BaseOps, GlobalCounter
from calcora.globals import dc
from calcora.utils import is_const_like, is_op_type, reconstruct_op, dprint

from calcora.core.ops import AnyOp

if TYPE_CHECKING:
  from calcora.core.expression import Expr

class Pattern:
  def __init__(self, pattern: Expr, replacement: Callable[..., Expr]) -> None:
    self.pattern = pattern
    self.replacement = replacement
    self._binding: Dict[str, Expr] = {}

  def match(self, op: Expr) -> Expr:
    self._binding = {}
    new_args = [self.match(arg) for arg in op.args] if op.fxn != BaseOps.Const and op.fxn != BaseOps.Var and op.fxn != BaseOps.Constant else op.args
    if op.fxn == BaseOps.Const or op.fxn == BaseOps.Constant: return op
    op = reconstruct_op(op, *new_args)
    if op.fxn == self.pattern.fxn and len(op.args) == len(self.pattern.args):
      if self._match(op, self.pattern):
        GlobalCounter.matches += 1
        new_op = self.replacement(**self._binding)
        if not dc.in_debug: dprint(f'$ -> $', 3, 'magenta', op, new_op)
        return new_op
    return reconstruct_op(op, *new_args)
  
  def _match(self, op: Expr, subpattern: Expr) -> bool:
    if not (len(op.args) == len(subpattern.args)) and not subpattern.fxn == BaseOps.AnyOp: return False
    
    if is_op_type(subpattern, AnyOp):
      if subpattern.assert_const_like and not is_const_like(op): return False
      if subpattern.match and subpattern.name in self._binding: 
        if self._binding[subpattern.name].commutative: 
          return any(self._binding[subpattern.name].args == op_args for op_args in permutations(op.args))
        return self._binding[subpattern.name] == op
      self._binding[subpattern.name] = op
      return True
  
    if op.fxn == subpattern.fxn and len(op.args) == len(subpattern.args):
      if op.fxn == BaseOps.Const or op.fxn == BaseOps.Constant: return op.args == subpattern.args
      if subpattern.commutative and subpattern.args:
        _temp_bind = self._binding.copy()
        for perm in permutations(subpattern.args):
          self._binding = _temp_bind.copy()
          if all(self._match(op_arg, sub_arg) for op_arg, sub_arg in zip(op.args, perm)): return True
        return False  
      if subpattern.args:
        return all(self._match(op_arg, sub_arg) for op_arg, sub_arg in zip(op.args, subpattern.args))
    return False
  
  @staticmethod
  def match_static(op: Expr, subpattern: Expr) -> Tuple[bool, Dict[str, Expr]]: # Note: This is an ugly hack
    p = Pattern(subpattern, lambda x: x)
    matched = p._match(op, subpattern)
    if matched: GlobalCounter.matches += 1
    return (matched, p._binding)

ConstLike = lambda name: AnyOp(name=name, assert_const_like=True)
MatchedConstLike = lambda name: AnyOp(name=name, match=True, assert_const_like=True)
NamedAny = lambda name: AnyOp(name=name)
MatchedSymbol = lambda name: AnyOp(name=name, match=True)