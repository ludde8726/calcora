from __future__ import annotations

from typing import Any, Callable, Generic, Optional, Type, TypeGuard, TypeVar
from typing import TYPE_CHECKING

from calcora.core.registry import ConstantRegistry, FunctionRegistry

T = TypeVar('T')
if TYPE_CHECKING:
  from calcora.core.expression import Expr
  from calcora.core.ops import Complex, Const, Var
  from calcora.core.ops import Add, Mul, Neg, Log, Pow
  from calcora.core.ops import Sin, Cos
  from calcora.core.ops import Div, Sub, Ln
  from calcora.core.ops import AnyOp

class LazyOp(Generic[T]):
  def __init__(self, fxn: Callable[[], Type[T]]) -> None:
    self._fxn = fxn
    self._value: Optional[Type[T]] = None
    self._evaluated = False

  def _is_evaluated(self, value: Optional[Type[T]]) -> TypeGuard[Type[T]]: return self._evaluated

  def __call__(self, *args: Any, **kwargs: Any) -> T:
    if self._is_evaluated(self._value): return self._value(*args)
    self._value = self._fxn()
    self._evaluated = True
    return self._value(*args, **kwargs)
  
LazyVar = LazyOp['Var'](lambda: FunctionRegistry.get('Var'))             # type: ignore
LazyConst = LazyOp['Const'](lambda: FunctionRegistry.get('Const'))       # type: ignore
LazyComplex = LazyOp['Complex'](lambda: FunctionRegistry.get('Complex')) # type: ignore
LazyAdd = LazyOp['Add'](lambda: FunctionRegistry.get('Add'))             # type: ignore
LazyNeg = LazyOp['Neg'](lambda: FunctionRegistry.get('Neg'))             # type: ignore
LazyMul = LazyOp['Mul'](lambda: FunctionRegistry.get('Mul'))             # type: ignore
LazyLog = LazyOp['Log'](lambda: FunctionRegistry.get('Log'))             # type: ignore
LazyPow = LazyOp['Pow'](lambda: FunctionRegistry.get('Pow'))             # type: ignore
LazySin = LazyOp['Sin'](lambda: FunctionRegistry.get('Sin'))             # type: ignore
LazyCos = LazyOp['Cos'](lambda: FunctionRegistry.get('Cos'))             # type: ignore

LazyDiv = LazyOp['Div'](lambda: FunctionRegistry.get('Div'))             # type: ignore
LazySub = LazyOp['Sub'](lambda: FunctionRegistry.get('Sub'))             # type: ignore
LazyLn = LazyOp['Ln'](lambda: FunctionRegistry.get('Ln'))                # type: ignore

LazyAnyOp = LazyOp['AnyOp'](lambda: FunctionRegistry.get('AnyOp'))       # type: ignore