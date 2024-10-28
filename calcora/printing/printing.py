from __future__ import annotations

import math

import calcora as c
from calcora.expression import Expr
from calcora.printing.printops import PrintableSub, PrintableDiv, PrintableLn
from calcora.printing.repr import Repr
from calcora.utils import NamedAny, is_op_type, partial_eval

class Printer():
  class Settings:
    Simplify = False
    Rewrite = True

  @staticmethod
  def _print_classes(expression: Expr) -> str:
    if isinstance(expression, PrintableSub): return f'Sub({Printer._print_classes(expression.x)}, {Printer._print_classes(expression.y)})'
    if isinstance(expression, PrintableDiv): return f'Div({Printer._print_classes(expression.x)}, {Printer._print_classes(expression.y)})'
    if isinstance(expression, PrintableLn): return f'Ln({Printer._print_classes(expression.x)})'
    elif is_op_type(expression, c.Add): return f'Add({Printer._print_classes(expression.x)}, {Printer._print_classes(expression.y)})'
    elif is_op_type(expression, c.Neg): return f'Neg({Printer._print_classes(expression.x)})'
    elif is_op_type(expression, c.Mul): return f'Mul({Printer._print_classes(expression.x)}, {Printer._print_classes(expression.y)})'
    elif is_op_type(expression, c.Pow): return f'Pow({Printer._print_classes(expression.x)}, {Printer._print_classes(expression.y)})'
    elif is_op_type(expression, c.Log): return f'Log({Printer._print_classes(expression.x)}, {Printer._print_classes(expression.base)})'
    elif is_op_type(expression, c.Const): return f'Const({float(expression.x)})'
    elif is_op_type(expression, c.Var): return f'Var({expression.name})'
    raise AttributeError(f'Missing print options for op of type {type(expression)}')

  @staticmethod
  def _print_latex(expression: Expr) -> str:
    raise NotImplementedError('Latex printing has not yet been implemented, try setting calcora.globals.Settings.Printing to either calcora.globals.PrintOptions.Class or calcora.globals.PrintOptions.Regular')

  @staticmethod
  def _print(expression: Expr) -> str:
    if Printer.Settings.Simplify:
      from calcora.match import SymbolicPatternMatcher
      while True:
        old_expression = expression
        expression = SymbolicPatternMatcher.match(expression)
        expression = partial_eval(expression)
        if expression == old_expression: break
    if Printer.Settings.Rewrite: 
      from calcora.match import Pattern, PatternMatcher
      RewriteOpsPatternMatcher = PatternMatcher([
        Pattern(c.Add(NamedAny('x'), c.Neg(NamedAny('y'))), lambda x,y: PrintableSub(x, y)),
        Pattern(c.Mul(NamedAny('x'), c.Pow(NamedAny('y'), c.Neg(c.Const(1)))), lambda x,y: PrintableDiv(x, y)),
        Pattern(c.Log(NamedAny('x'), c.Const(math.e)), lambda x: PrintableLn(x)),
      ])
      expression = RewriteOpsPatternMatcher.match(expression)
    if c.globals.Settings.Printing == c.globals.PrintOptions.Class: return Printer._print_classes(expression)
    elif c.globals.Settings.Printing == c.globals.PrintOptions.Latex: return Printer._print_latex(expression)
    else: return Repr._print(expression)
