from __future__ import annotations

from typing import Callable, Dict, Tuple
from typing import TYPE_CHECKING

from calcora.globals import BaseOps
from calcora.utils import is_const_like, is_op_type, reconstruct_op

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
      if op.fxn == BaseOps.Const or op.fxn == BaseOps.Constant: return op.args == subpattern.args
      if subpattern.args:
        return all(self._match(op_arg, sub_arg) for op_arg, sub_arg in zip(op.args, subpattern.args))
      
    return False
  
  @staticmethod
  def match_static(op: Expr, subpattern: Expr, binding: Dict[str, Expr] = {}) -> Tuple[bool, Dict[str, Expr]]:
    _binding = binding
    if not (len(op.args) == len(subpattern.args)) and not subpattern.fxn == BaseOps.AnyOp: return (False, _binding)
    if is_op_type(subpattern, AnyOp):
      if subpattern.assert_const_like and not is_const_like(op): return (False, _binding)
      if subpattern.match and subpattern.name in _binding:
        return (_binding[subpattern.name] == op, _binding)
      _binding[subpattern.name] = op
      return (True, _binding)
    
    if op.fxn == subpattern.fxn and len(op.args) == len(subpattern.args):
      if op.fxn == BaseOps.Const or op.fxn == BaseOps.Constant: return (op.args == subpattern.args, _binding)
      if subpattern.args:
        return (all(Pattern.match_static(op_arg, sub_arg, _binding)[0] for op_arg, sub_arg in zip(op.args, subpattern.args)), _binding)
      
    return (False, _binding)

ConstLike = lambda name: AnyOp(name=name, assert_const_like=True)
MatchedConstLike = lambda name: AnyOp(name=name, match=True, assert_const_like=True)
NamedAny = lambda name: AnyOp(name=name)
MatchedSymbol = lambda name: AnyOp(name=name, match=True)