from __future__ import annotations

from typing import Callable, Optional, Type, TypeGuard
from typing import TYPE_CHECKING

from calcora.core.registry import ConstantRegistry, FunctionRegistry

if TYPE_CHECKING:
  from calcora.core.expression import Expr
  from calcora.core.ops import Constant

class LazyOp:
  def __init__(self, fxn: Callable[[], Type[Expr]]) -> None:
    self._fxn = fxn
    self._value: Optional[Type[Expr]] = None
    self._evaluated = False

  def _is_evaluated(self, value) -> TypeGuard[Type[Expr]]: return self._evaluated

  def __call__(self, *args) -> Expr:
    if self._is_evaluated(self._value): return self._value(*args)
    self._value = self._fxn()
    self._evaluated = True
    return self._value(*args)
  
Var = LazyOp(lambda: FunctionRegistry.get('Var'))
Const = LazyOp(lambda: FunctionRegistry.get('Const'))
Complex = LazyOp(lambda: FunctionRegistry.get('Complex'))
Add = LazyOp(lambda: FunctionRegistry.get('Add'))
Neg = LazyOp(lambda: FunctionRegistry.get('Neg'))
Mul = LazyOp(lambda: FunctionRegistry.get('Mul'))
Log = LazyOp(lambda: FunctionRegistry.get('Log'))
Pow = LazyOp(lambda: FunctionRegistry.get('Pow'))
Sin = LazyOp(lambda: FunctionRegistry.get('Sin'))
Cos = LazyOp(lambda: FunctionRegistry.get('Cos'))

Div = LazyOp(lambda: FunctionRegistry.get('Div'))
Sub = LazyOp(lambda: FunctionRegistry.get('Sub'))
Ln = LazyOp(lambda: FunctionRegistry.get('Ln'))