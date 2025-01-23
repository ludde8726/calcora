from __future__ import annotations

from typing import Any, Callable, Generic, Optional, Type, TypeGuard, TypeVar, ParamSpec
from typing import TYPE_CHECKING

from calcora.core.registry import ConstantRegistry, FunctionRegistry

T = TypeVar('T')
P = ParamSpec('P')

if TYPE_CHECKING:
  from calcora.core.expression import Expr
  from calcora.core.ops import Complex, Const, Var
  from calcora.core.ops import Add, Mul, Neg, Log, Pow
  from calcora.core.ops import Sin, Cos
  from calcora.core.ops import Div, Sub, Ln, Sqrt
  from calcora.core.ops import AnyOp

class LazyOp(Generic[T, P]):
  def __init__(self, fxn: Callable[[], Type[T]]) -> None:
    self._fxn = fxn
    self._value: Optional[Type[T]] = None
    self._evaluated = False

  def _is_evaluated(self, value: Optional[Type[T]]) -> TypeGuard[Type[T]]: return self._evaluated

  def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
    if self._is_evaluated(self._value): return self._value(*args)
    self._value = self._fxn()
    self._evaluated = True
    return self._value(*args, **kwargs)
  
LazyVar = LazyOp['Var', 'Var._init'](lambda: FunctionRegistry.get('Var'))             # type: ignore
LazyConst = LazyOp['Const', 'Const._init'](lambda: FunctionRegistry.get('Const'))       # type: ignore
LazyComplex = LazyOp['Complex', 'Complex._init'](lambda: FunctionRegistry.get('Complex')) # type: ignore
LazyAdd = LazyOp['Add', 'Add._init'](lambda: FunctionRegistry.get('Add'))             # type: ignore
LazyNeg = LazyOp['Neg', 'Neg._init'](lambda: FunctionRegistry.get('Neg'))             # type: ignore
LazyMul = LazyOp['Mul', 'Mul._init'](lambda: FunctionRegistry.get('Mul'))             # type: ignore
LazyLog = LazyOp['Log', 'Log._init'](lambda: FunctionRegistry.get('Log'))             # type: ignore
LazyPow = LazyOp['Pow', 'Pow._init'](lambda: FunctionRegistry.get('Pow'))             # type: ignore
LazySin = LazyOp['Sin', 'Sin._init'](lambda: FunctionRegistry.get('Sin'))             # type: ignore
LazyCos = LazyOp['Cos', 'Cos._init'](lambda: FunctionRegistry.get('Cos'))             # type: ignore

LazyDiv = LazyOp['Div', 'Div._init'](lambda: FunctionRegistry.get('Div'))             # type: ignore
LazySub = LazyOp['Sub', 'Sub._init'](lambda: FunctionRegistry.get('Sub'))             # type: ignore
LazyLn = LazyOp['Ln', 'Ln._init'](lambda: FunctionRegistry.get('Ln'))                # type: ignore
LazyLn = LazyOp['Sqrt', 'Sqrt._init'](lambda: FunctionRegistry.get('Sqrt'))         # type: ignore       

LazyAnyOp = LazyOp['AnyOp', 'AnyOp._init'](lambda: FunctionRegistry.get('AnyOp'))       # type: ignore