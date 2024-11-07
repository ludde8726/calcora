from __future__ import annotations

from typing import Dict, Type, TYPE_CHECKING

if TYPE_CHECKING:
  from calcora.core.expression import Expr
  from calcora.core.ops import Constant

class FunctionRegistry:
  _registry : Dict[str, Type[Expr]] = {}

  @classmethod
  def register(cls, fxn: Type[Expr]) -> None:
    if fxn.__name__ in cls._registry: return
    cls._registry[fxn.__name__] = fxn
  
  @classmethod
  def get(cls, name: str) -> Type[Expr]:
    if name in cls._registry: return cls._registry[name]
    raise KeyError(f"No function with name '{name}' registered")
  
class ConstantRegistry:
  _registry : Dict[str, Constant] = {}

  @classmethod
  def register(cls, fxn: Constant) -> None:
    if fxn.name in cls._registry: return
    cls._registry[fxn.name] = fxn
  
  @classmethod
  def get(cls, name: str) -> Constant:
    if name in cls._registry: return cls._registry[name]
    raise KeyError(f"No function with name '{name}' registered")
  