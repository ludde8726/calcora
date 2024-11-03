from __future__ import annotations

from typing import Type, TYPE_CHECKING, TypeGuard, TypeVar

import calcora as c
from calcora.globals import BaseOps

if TYPE_CHECKING:
  from calcora.expression import Expr
  T = TypeVar('T', bound=Expr)

def is_op_type(op: Expr, op_type: Type[T]) -> TypeGuard[T]: return op.fxn == BaseOps(op_type.__name__)

def is_const_like(op: Expr):
  if op.fxn == BaseOps.Const: return True
  elif op.fxn == BaseOps.Var: return False
  return all(is_const_like(arg) for arg in op.args)

def reconstruct_op(op: Expr, *args):
  return op.__class__(*args)

def partial_eval(op: Expr) -> Expr:
  if op.fxn != BaseOps.Const and op.fxn != BaseOps.Var:
    new_args = [partial_eval(arg) for arg in op.args]
    op = reconstruct_op(op, *new_args)
  if is_const_like(op): return c.Const(op.eval())
  return op


ConstLike = lambda name: c.AnyOp(name=name, assert_const_like=True)
NamedAny = lambda name: c.AnyOp(name=name)
MatchedSymbol = lambda name: c.AnyOp(name=name, match=True)