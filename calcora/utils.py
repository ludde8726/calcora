from calcora.ops import Op
from calcora.ops import AnyOp, BaseOps, Const, Log, Ln, Neg

from typing import TypeGuard

def is_any_op(op: Op) -> TypeGuard[AnyOp]:
  return op.fxn == BaseOps.AnyOp

def is_log_op(op: Op) -> TypeGuard[Log]:
  return op.fxn == BaseOps.Log

def is_const_like(op: Op):
  if op.fxn == BaseOps.Const: return True
  if op.fxn == BaseOps.Var: return False
  return all(is_const_like(arg) for arg in op.args)

def reconstruct_op(op: Op, *args):
  if is_log_op(op) and op.natural: return Ln(args[0])
  return op.__class__(*args)

def partial_eval(op: Op) -> Op:
  if op.fxn != BaseOps.Const and op.fxn != BaseOps.Var:
    new_args = [partial_eval(arg) for arg in op.args]
    op = reconstruct_op(op, *new_args)
  if is_const_like(op): return Const(op.eval()) if op.eval() >= 0 else Neg(Const(abs(op.eval())))
  return op

ConstLike = lambda name: AnyOp(name=name, assert_const_like=True)
NamedAny = lambda name: AnyOp(name=name)
MatchedSymbol = lambda name: AnyOp(name=name, match=True)