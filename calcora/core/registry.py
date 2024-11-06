from typing import Type

class FunctionRegistry:
  _registry = {}

  @classmethod
  def register(cls, fxn: Type) -> None:
    if fxn.__name__ in cls._registry: return
    cls._registry[fxn.__name__] = fxn
  
  @classmethod
  def get(cls, name) -> Type:
    if name in cls._registry: return cls._registry[name]
    raise AttributeError(f"Function '{name}' is not registered")