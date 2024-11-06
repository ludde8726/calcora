from __future__ import annotations

import math
from typing import TYPE_CHECKING

from calcora.globals import pc, PrintOptions, BaseOps
from calcora.printing.printops import PrintableDiv, PrintableLn, PrintableSub
from calcora.utils import partial_eval
from calcora.core.registry import FunctionRegistry

if TYPE_CHECKING:
  from calcora.core.expression import Expr

class Printer():
  @staticmethod
  def _print_classes(expression: Expr) -> str:
    if expression.fxn == BaseOps.Const: return f'Const({expression.x})' # type: ignore
    elif expression.fxn == BaseOps.Var: return f'Var({expression.name})' # type: ignore
    elif expression.fxn == BaseOps.AnyOp: return f'Any({expression.name}, match={expression.match}, const={expression.assert_const_like})' # type: ignore
    args = ', '.join([Printer._print_classes(arg) for arg in expression.args])
    return f'{expression.__class__.__name__}({args})'

  @staticmethod
  def _print_latex(expression: Expr) -> str:
    raise NotImplementedError('Latex printing has not yet been implemented, try setting calcora.globals.Settings.Printing to either calcora.globals.PrintOptions.Class or calcora.globals.PrintOptions.Regular')

  @staticmethod
  def _print(expression: Expr) -> str:
    if pc.simplify:
      from calcora.match.match import SymbolicPatternMatcher
      while True:
        old_expression = expression
        expression = SymbolicPatternMatcher.match(expression)
        expression = partial_eval(expression)
        if expression == old_expression: break
    if pc.rewrite: 
      from calcora.match.match import Pattern, PatternMatcher, NamedAny
      Neg = FunctionRegistry.get('Neg')
      Mul = FunctionRegistry.get('Mul')
      Add = FunctionRegistry.get('Add')
      Log = FunctionRegistry.get('Log')
      Const = FunctionRegistry.get('Const')
      Pow = FunctionRegistry.get('Pow')

      RewriteOpsPatternMatcher = PatternMatcher([
        Pattern(Add(NamedAny('x'), Neg(NamedAny('y'))), lambda x,y: PrintableSub(x, y)), # type: ignore
        Pattern(Mul(NamedAny('x'), Pow(NamedAny('y'), Neg(Const(1)))), lambda x,y: PrintableDiv(x, y)), # type: ignore
        Pattern(Log(NamedAny('x'), Const(math.e)), lambda x: PrintableLn(x)), # type: ignore
      ])
      expression = RewriteOpsPatternMatcher.match(expression)
    if pc.print_type == PrintOptions.Class: return Printer._print_classes(expression)
    elif pc.print_type == PrintOptions.Latex: return Printer._print_latex(expression)
    else: return expression._print_repr()
