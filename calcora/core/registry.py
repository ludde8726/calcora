from __future__ import annotations

from typing import Any, Callable, Dict, Literal, Tuple, Type, TypeGuard, TYPE_CHECKING, Union

from calcora.core.numeric import Numeric
from calcora.types import NumericType

from mpmath import mpf, mpc

if TYPE_CHECKING:
  from calcora.core.expression import Expr
  from calcora.core.ops import Constant

type ExprArgTypes = Union[NumericType, Numeric, Expr]

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

def is_expr(x: Any) -> TypeGuard[Expr]:
  return hasattr(x, "_eval")

class Dispatcher:
  _callback_fxn : Callable[[Expr], Expr] = lambda x: x

  @staticmethod
  def typecast(x: ExprArgTypes) -> Expr:
    if is_expr(x): return x
    elif isinstance(x, Numeric): return FunctionRegistry.get("Const")(x) if x >= 0 else FunctionRegistry.get("Neg")(FunctionRegistry.get("Const")(abs(x)))
    elif isinstance(x, (float, int)): 
      n = Numeric(x)
      return FunctionRegistry.get("Const")(n) if n >= 0 else FunctionRegistry.get("Neg")(FunctionRegistry.get("Const")(abs(n)))
    elif isinstance(x, (FunctionRegistry.get("Neg"), str, mpf, mpc)): 
      num = Numeric(x)
      if num.imag: return FunctionRegistry.get("Neg")(num.real if num.real >= 0 else FunctionRegistry.get("Neg")(abs(num.real)), num.imag if num.imag >= 0 else FunctionRegistry.get("Neg")(abs(num.imag)))
      else: return FunctionRegistry.get("Const")(num) if num >= 0 else FunctionRegistry.get("Const")(abs(num))
    else: raise TypeError(f"Invalid type {type(x)} for conversion to type Const")

  @staticmethod
  def op_creator(name: str, *args: ExprArgTypes, run_callback: bool = True, type_cast: bool = True) -> Expr:
    def validate(x: ExprArgTypes) -> Expr:
      if not is_expr(x): raise TypeError(f"Creation of op with arg of type {x.__class__.__name__} is not allowed unless type_cast is set to True.")
      return x
    arguments = [Dispatcher.typecast(x) if type_cast else validate(x) for x in args]
    op = FunctionRegistry.get(name)(*arguments)
    return Dispatcher._callback_fxn(op) if run_callback else op

  # Special ops
  @staticmethod
  def const(x: Union[NumericType, Numeric], run_callback: bool = True, type_cast: bool = True) -> Expr: 
    if type_cast: x = Numeric.numeric_cast(x)
    op = FunctionRegistry.get("Const")(x)
    return Dispatcher._callback_fxn(op) if run_callback else op
  @staticmethod
  def var(name: str) -> Expr: return FunctionRegistry.get("Var")(name)
  @staticmethod
  def complex(real: ExprArgTypes, imag: ExprArgTypes, representation: Literal["Rectangular", "Polar", "Exponential"] = "Rectangular", run_callback: bool = True, type_cast: bool = True) -> Expr:
    if type_cast: real, imag = Dispatcher.typecast(real), Dispatcher.typecast(imag)
    if not (is_expr(real) and is_expr(imag)): raise TypeError(f"Creation of complex with arg of types '{real.__class__.__name__}' and '{imag.__class__.__name__}' is not allowed unless type_cast is set to True.")
    op = FunctionRegistry.get("Complex")(real, imag, representation=representation)
    return Dispatcher._callback_fxn(op) if run_callback else op
  
  # One arg ops
  @staticmethod
  def neg(x: ExprArgTypes, run_callback: bool = True, type_cast: bool = True) -> Expr: return Dispatcher.op_creator("Neg", x, run_callback=run_callback, type_cast=type_cast)

  # Two arg ops
  @staticmethod
  def add(x: ExprArgTypes, y: ExprArgTypes, run_callback: bool = True, type_cast: bool = True) -> Expr: return Dispatcher.op_creator("Add", x, y, run_callback=run_callback, type_cast=type_cast)
  @staticmethod
  def mul(x: ExprArgTypes, y: ExprArgTypes, run_callback: bool = True, type_cast: bool = True) -> Expr: return Dispatcher.op_creator("Mul", x, y, run_callback=run_callback, type_cast=type_cast)
  @staticmethod
  def log(x: ExprArgTypes, base: ExprArgTypes, run_callback: bool = True, type_cast: bool = True) -> Expr: return Dispatcher.op_creator("Log", x, base, run_callback=run_callback, type_cast=type_cast)
  @staticmethod
  def pow(x: ExprArgTypes, y: ExprArgTypes, run_callback: bool = True, type_cast: bool = True) -> Expr: return Dispatcher.op_creator("Pow", x, y, run_callback=run_callback, type_cast=type_cast)
  @staticmethod
  def sin(x: ExprArgTypes, run_callback: bool = True, type_cast: bool = True) -> Expr: return Dispatcher.op_creator("Sin", x, run_callback=run_callback, type_cast=type_cast)
  @staticmethod
  def cos(x: ExprArgTypes, run_callback: bool = True, type_cast: bool = True) -> Expr: return Dispatcher.op_creator("Cos", x, run_callback=run_callback, type_cast=type_cast)
  
  # "Fake" ops
  @staticmethod
  def div(x: ExprArgTypes, y: ExprArgTypes, run_callback: bool = True, type_cast: bool = True) -> Expr: return Dispatcher.mul(x, Dispatcher.pow(y, Dispatcher.neg(1, run_callback=run_callback), run_callback=run_callback, type_cast=type_cast), run_callback=run_callback, type_cast=type_cast)
  @staticmethod
  def sub(x: ExprArgTypes, y: ExprArgTypes, run_callback: bool = True, type_cast: bool = True) -> Expr: return Dispatcher.add(x, Dispatcher.neg(y, run_callback=run_callback, type_cast=type_cast), run_callback=run_callback, type_cast=type_cast)
  @staticmethod
  def ln(x: ExprArgTypes, run_callback: bool = True, type_cast: bool = True) -> Expr: return Dispatcher.log(x, ConstantRegistry.get("E"), run_callback=run_callback, type_cast=type_cast)
  @staticmethod
  def sqrt(x: ExprArgTypes, run_callback: bool = True, type_cast: bool = True) -> Expr: return Dispatcher.pow(x, Dispatcher.const(0.5, run_callback=run_callback), run_callback=run_callback, type_cast=type_cast)