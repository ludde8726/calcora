from __future__ import annotations

from calcora.globals import PrintOptions
from calcora.globals import pc

from calcora.printing.printops import PrintableDiv, PrintableLn, PrintableSub, PrintableSqrt, PrintableOp

from calcora.core.constants import E, OneHalf, NegOne
from calcora.core.expression import Expr
from calcora.core.ops import Add, AnyOp, Const, Constant, Log, Mul, Neg, Pow, Var

from calcora.match.match import PatternMatcher
from calcora.match.pattern import Pattern
from calcora.match.pattern import NamedAny
from calcora.match.simplify import simplify

RewriteOpsPatternMatcher = PatternMatcher([
  Pattern(Add(NamedAny('x'), Neg(NamedAny('y'))), lambda x,y: PrintableSub(x, y)),
  Pattern(Mul(NamedAny('x'), Pow(NamedAny('y'), NegOne)), lambda x,y: PrintableDiv(x, y)),
  Pattern(Log(NamedAny('x'), E), lambda x: PrintableLn(x)), 
  Pattern(Pow(NamedAny('x'), OneHalf), lambda x: PrintableSqrt(x))
])

class Printer:
  @staticmethod
  def _print_classes(expression: Expr) -> str:
    if isinstance(expression, Const): return f'Const({expression.x})'
    elif isinstance(expression, Constant): return f'Constant({expression.name})'
    elif isinstance(expression, Var): return f'Var({expression.name})'
    elif isinstance(expression, AnyOp): return f'Any({expression.name}, match={expression.match}, const={expression.assert_const_like})'
    args = ', '.join([Printer._print_classes(arg) for arg in expression.args])
    if isinstance(expression, PrintableOp): return f'{expression.print_name}({args})'
    return f'{expression.__class__.__name__}({args})'

  @staticmethod
  def _print(expression: Expr) -> str:
    if pc.simplify:
      expression = simplify(expression)
    if pc.rewrite: 
      expression = RewriteOpsPatternMatcher.match(expression, print_debug=False)
    if pc.print_type == PrintOptions.Class: return Printer._print_classes(expression)
    elif pc.print_type == PrintOptions.Latex: return expression._print_latex()
    else: return expression._print_repr()

if not Expr._initialized_printing:
  setattr(Expr, '_print_self', lambda self: Printer._print(self))
  Expr._initialized_printing = True