from __future__ import annotations

from typing import Type, TYPE_CHECKING

if TYPE_CHECKING:
  from calcora.core.expression import Expr

class FunctionRegistry:
  _registry = {}

  @classmethod
  def register(cls, fxn: Type[Expr]) -> None:
    if fxn.__name__ in cls._registry: return
    cls._registry[fxn.__name__] = fxn
  
  @classmethod
  def get(cls, name) -> Type:
    if name in cls._registry: return cls._registry[name]
    raise KeyError(f"No function with name '{name}' registered")