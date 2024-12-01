from __future__ import annotations

from typing import Callable, Dict
from typing import TYPE_CHECKING

from itertools import permutations

from calcora.globals import BaseOps, PrintOptions
from calcora.globals import pc

from calcora.printing.printops import PrintableDiv, PrintableLn, PrintableSub

from calcora.core.lazy import LazyNeg, LazyMul, LazyAdd, LazyLog, LazyConst, LazyPow
from calcora.core.registry import ConstantRegistry, FunctionRegistry

if TYPE_CHECKING:
  from calcora.core.expression import Expr
  
class Printer:
  @staticmethod
  def _print_classes(expression: Expr) -> str:
    if expression.fxn == BaseOps.Const: return f'Const({expression.x})' # type: ignore
    if expression.fxn == BaseOps.Constant: return f'Constant({expression.name})' # type: ignore
    elif expression.fxn == BaseOps.Var: return f'Var({expression.name})' # type: ignore
    elif expression.fxn == BaseOps.AnyOp: return f'Any({expression.name}, match={expression.match}, const={expression.assert_const_like})' # type: ignore
    args = ', '.join([Printer._print_classes(arg) for arg in expression.args])
    return f'{expression.__class__.__name__}({args})'

  @staticmethod
  def _print(expression: Expr) -> str:
    if pc.simplify:
      from calcora.match.simplify import simplify
      expression = simplify(expression)
    if pc.rewrite: 
      from calcora.match.match import Pattern, PatternMatcher, NamedAny

      E = ConstantRegistry.get('e')

      RewriteOpsPatternMatcher = PatternMatcher([
        Pattern(LazyAdd(NamedAny('x'), LazyNeg(NamedAny('y'))), lambda x,y: PrintableSub(x, y)), # type: ignore
        Pattern(LazyMul(NamedAny('x'), LazyPow(NamedAny('y'), LazyNeg(LazyConst(1)))), lambda x,y: PrintableDiv(x, y)), # type: ignore
        Pattern(LazyLog(NamedAny('x'), E), lambda x: PrintableLn(x)), # type: ignore
      ])
      expression = RewriteOpsPatternMatcher.match(expression)
    if pc.print_type == PrintOptions.Class: return Printer._print_classes(expression)
    elif pc.print_type == PrintOptions.Latex: return expression._print_latex()
    else: return expression._print_repr()
