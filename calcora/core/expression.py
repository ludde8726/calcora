from __future__ import annotations

from itertools import permutations
from typing import Any, Tuple, Union, Hashable
from typing import TYPE_CHECKING
import weakref

from calcora.globals import BaseOps, GlobalCounter
from calcora.types import CalcoraNumber, NumericType

from calcora.core.numeric import Numeric
from calcora.core.registry import FunctionRegistry, Dispatcher, ExprArgTypes

from calcora.utils import dprint

from mpmath import mpc, mpf

if TYPE_CHECKING:
  from calcora.core.ops import Var

class Expr:
  _finalizer_refs : set[weakref.finalize] = set() # Static sets of all finalizers to make sure they don't get garbage collected before instance is deleted.
  _initialized_printing = False

  def __init__(self, *args: Any, commutative: bool = False, **kwargs: Any) -> None:
    self.args: Tuple[Expr, ...] = args
    assert self.__class__.__name__ in [op.value for op in BaseOps], f"Invalid op type {type(self.__class__.__name__)}"
    self.fxn: BaseOps = BaseOps(self.__class__.__name__)
    self.priority : int = 0 # higher equals higher priority, ex multiplication before addition, etc.
    self.commutative = commutative
    GlobalCounter.num_ops += 1
    finalizer = weakref.finalize(self, GlobalCounter.decrement_ops)
    Expr._finalizer_refs.add(finalizer)
    dprint(f'Op \'{self.fxn.name}\' created with args $', 4, 'yellow', self.args)

  def __eq__(self, other: object) -> bool:
    return isinstance(other, Expr) and self.fxn == other.fxn and \
      (self.args == other.args if not self.commutative else any(other.args == op_args for op_args in permutations(self.args)))
  
  def __hash__(self) -> int: return hash((self.fxn.name, frozenset(self.args) if self.commutative else self.args))
  
  def add(self, x: ExprArgTypes) -> Expr: return Dispatcher.add(self, x)
  def sub(self, x: ExprArgTypes) -> Expr: return Dispatcher.sub(self, x)
  def mul(self, x: ExprArgTypes) -> Expr: return Dispatcher.mul(self, x)
  def div(self, x: ExprArgTypes) -> Expr: return Dispatcher.div(self, x)
  def neg(self) -> Expr: return Dispatcher.neg(self)
  def pow(self, x: ExprArgTypes) -> Expr: return Dispatcher.pow(self, x)
  def log(self, base: ExprArgTypes) -> Expr: return Dispatcher.log(self, base)
  def ln(self) -> Expr: return Dispatcher.ln(self)
  def sin(self) -> Expr: return Dispatcher.sin(self)
  def cos(self) -> Expr: return Dispatcher.cos(self)
  
  def __add__(self, x: ExprArgTypes) -> Expr: return self.add(x)
  def __neg__(self) -> Expr: return self.neg()
  def __sub__(self, x: ExprArgTypes) -> Expr: return self.sub(x)
  def __mul__(self, x: ExprArgTypes) -> Expr: return self.mul(x)
  def __truediv__(self, x: ExprArgTypes) -> Expr: return self.div(x)
  def __pow__(self, x: ExprArgTypes) -> Expr: return self.pow(x)

  def __radd__(self, x: ExprArgTypes) -> Expr: return Dispatcher.add(x, self)
  def __rmul__(self, x: ExprArgTypes) -> Expr: return Dispatcher.mul(x, self)
  def __rsub__(self, x: ExprArgTypes) -> Expr: return Dispatcher.sub(x, self)
  def __rtruediv__(self, x: ExprArgTypes) -> Expr: return Dispatcher.div(x, self)
  def __rpow__(self, x: ExprArgTypes) -> Expr: return Dispatcher.pow(x, self)
  
  def __int__(self) -> int: return int(self._eval())
  def __float__(self) -> float: return float(self._eval())
  def __bool__(self) -> bool: return self != Dispatcher.const(0)
  
  def differentiate(self, var: Var) -> Expr: raise NotImplementedError()

  # Note: Might not be the best option?
  def evalf(self, **kwargs: Expr) -> Numeric:
    result = Numeric(self._eval(**kwargs))
    dprint(f'Evaluating $ -> $', 1, 'green', self, result)
    return result
  
  def eval(self, **kwargs: Expr) -> Numeric: return self.evalf(**kwargs)
  
  def _eval(self, **kwargs: Expr) -> CalcoraNumber: raise NotImplementedError(f"Op {self.__class__.__name__} does not implement the eval method.")

  def _print_self(self) -> str: raise NotImplementedError("Printing has not been initialized, please import calcora.printing.printing to initialize the printer.")
  def _print_repr(self) -> str: raise NotImplementedError(f"Op {self.__class__.__name__} has no regular print implementation.")
  def _print_latex(self) -> str: raise NotImplementedError(f"Op {self.__class__.__name__} has no latex print implementation.")
  def __repr__(self) -> str: return self._print_self() #Printer._print(self) 
  def __str__(self) -> str: return repr(self)