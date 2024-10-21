from typing import Type, TypeGuard, TypeVar

from calcora.globals import Settings, PrintOptions

from calcora.expression import BaseOps, Expr
from calcora.ops import AnyOp, Add, Const, Log, Ln, Mul, Neg, Pow, Var


T = TypeVar('T', bound=Expr)
def is_op_type(op: Expr, op_type: Type[T]) -> TypeGuard[T]: return op.fxn == BaseOps(op_type.__name__)

def is_const_like(op: Expr):
  if op.fxn == BaseOps.Const: return True
  elif op.fxn == BaseOps.Var: return False
  return all(is_const_like(arg) for arg in op.args)

def reconstruct_op(op: Expr, *args):
  if is_op_type(op, Log) and op.natural: return Ln(args[0])
  return op.__class__(*args)

def partial_eval(op: Expr) -> Expr:
  if op.fxn != BaseOps.Const and op.fxn != BaseOps.Var:
    new_args = [partial_eval(arg) for arg in op.args]
    op = reconstruct_op(op, *new_args)
  if is_const_like(op): return Const(op.eval()) if op.eval() >= 0 else Neg(Const(abs(op.eval())))
  return op

def pretty_print(op: Expr) -> str:
  if Settings.Printing == PrintOptions.Class:
    if is_op_type(op, Add): return f'Add({pretty_print(op.x)}, {pretty_print(op.y)})'
    elif is_op_type(op, Neg): return f'Neg({pretty_print(op.x)})'
    elif is_op_type(op, Mul): return f'Mul({pretty_print(op.x)}, {pretty_print(op.y)})'
    elif is_op_type(op, Pow): return f'Pow({pretty_print(op.x)}, {pretty_print(op.y)})'
    elif is_op_type(op, Log): 
      return f'Log({pretty_print(op.x)}, {pretty_print(op.base)})' if not op.natural else f'Ln({pretty_print(op.x)})'
    elif is_op_type(op, Const): return f'Const({op.x})'
    elif is_op_type(op, Var): return f'Var({op.name})'
    return 'NoOp'
  else:
    return repr(op)

ConstLike = lambda name: AnyOp(name=name, assert_const_like=True)
NamedAny = lambda name: AnyOp(name=name)
MatchedSymbol = lambda name: AnyOp(name=name, match=True)