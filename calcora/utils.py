from __future__ import annotations

from typing import Type, TYPE_CHECKING, TypeGuard, TypeVar

from calcora.globals import BaseOps

if TYPE_CHECKING:
  from calcora.core.expression import Expr
  from calcora.core.ops import Var
  T = TypeVar('T', bound=Expr)

def is_op_type(op: Expr, op_type: Type[T]) -> TypeGuard[T]: return op.fxn == BaseOps(op_type.__name__)

def has_constant(op: Expr) -> bool:
  if op.fxn == BaseOps.Constant: return True
  if op.fxn == BaseOps.Const or op.fxn == BaseOps.Var: return False
  return any(has_constant(arg) for arg in op.args)

def is_const_like(op: Expr):
  if op.fxn == BaseOps.Const or op.fxn == BaseOps.Constant: return True
  elif op.fxn == BaseOps.Var: return False
  return all(is_const_like(arg) for arg in op.args)

def reconstruct_op(op: Expr, *args):
  return op.__class__(*args)

def diff(op: Expr, var: Var, degree: int = 1):
  for _ in range(degree): op = op.differentiate(var)
  return op