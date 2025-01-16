from __future__ import annotations

from typing import Callable, Dict
from typing import TYPE_CHECKING

from itertools import permutations

from calcora.globals import BaseOps, PrintOptions
from calcora.globals import pc
from calcora.utils import is_op_type

from calcora.printing.printops import PrintableDiv, PrintableLn, PrintableSub, PrintableOp

from calcora.core.lazy import LazyNeg, LazyMul, LazyAdd, LazyLog, LazyConst, LazyPow
from calcora.core.registry import ConstantRegistry, FunctionRegistry
from calcora.core.stringops import *

if TYPE_CHECKING:
  from calcora.core.expression import Expr
  from calcora.core.ops import Const, Constant, Var, AnyOp

class Printer:
  @staticmethod
  def _print_classes(expression: Expr) -> str:
    if is_op_type(expression, Const): return f'Const({expression.x})'
    elif is_op_type(expression, Constant): return f'Constant({expression.name})'
    elif is_op_type(expression, Var): return f'Var({expression.name})'
    elif is_op_type(expression, AnyOp): return f'Any({expression.name}, match={expression.match}, const={expression.assert_const_like})'
    args = ', '.join([Printer._print_classes(arg) for arg in expression.args])
    if isinstance(expression, PrintableOp): return f'{expression.print_name}({args})'
    return f'{expression.__class__.__name__}({args})'

  @staticmethod
  def _print(expression: Expr) -> str:
    if pc.simplify:
      from calcora.match.simplify import simplify
      expression = simplify(expression)
    if pc.rewrite: 
      from calcora.match.match import PatternMatcher
      from calcora.match.pattern import Pattern
      from calcora.match.pattern import NamedAny

      E = ConstantRegistry.get('e')

      RewriteOpsPatternMatcher = PatternMatcher([
        Pattern(LazyAdd(NamedAny('x'), LazyNeg(NamedAny('y'))), lambda x,y: PrintableSub(x, y)), # type: ignore
        Pattern(LazyMul(NamedAny('x'), LazyPow(NamedAny('y'), LazyNeg(LazyConst(1)))), lambda x,y: PrintableDiv(x, y)), # type: ignore
        Pattern(LazyLog(NamedAny('x'), E), lambda x: PrintableLn(x)), # type: ignore
      ])
      expression = RewriteOpsPatternMatcher.match(expression, print_debug=False)
    if pc.print_type == PrintOptions.Class: return Printer._print_classes(expression)
    elif pc.print_type == PrintOptions.Latex: return expression._print_latex()
    else: return expression._print_repr()
