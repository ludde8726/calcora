from __future__ import annotations

from enum import Enum, auto
import math
from typing import Tuple

import calcora as c
from calcora import globals
from calcora.expression import Expr, BaseOps
from calcora.utils import NamedAny, is_op_type


class PrintRegular:
  @staticmethod
  def _print_Add(op: c.Add) -> str:
    x = Printer._print_regular(op.x)
    y = Printer._print_regular(op.y)
    if op.x.priority < op.priority: x = f'({x})'
    if op.y.priority < op.priority: y = f'({y})'
    return f'{x} + {y}'
  
  @staticmethod
  def _print_PrintableSub(op: PrintableSub) -> str:
    x = Printer._print_regular(op.x)
    y = Printer._print_regular(op.y)
    if op.x.priority < op.priority and not op.x.fxn == BaseOps.Neg: x = f'({x})'
    if op.y.priority < op.priority or isinstance(op.y, PrintableSub) or op.y.fxn == BaseOps.Neg or op.y.fxn == BaseOps.Add: y = f'({y})'
    return f'{x} - {y}'
  
  @staticmethod
  def _print_Neg(op: c.Neg) -> str:
    x = Printer._print_regular(op.x)
    if op.x.fxn != BaseOps.Const and op.fxn != BaseOps.Var: x = f'({x})'
    return f'-{x}'
  
  @staticmethod
  def _print_Mul(op: c.Mul) -> str:
    x = Printer._print_regular(op.x)
    y = Printer._print_regular(op.y)
    if op.x.priority < op.priority: x = f'({x})'
    if op.y.priority < op.priority: y = f'({y})'
    return f'{x}*{y}'
  
  @staticmethod
  def _print_PrintableDiv(op: PrintableDiv) -> str:
    x = Printer._print_regular(op.x)
    y = Printer._print_regular(op.y)
    if op.x.priority < op.priority or isinstance(op.x, PrintableDiv): x = f'({x})'
    if op.y.priority < op.priority or isinstance(op.y, PrintableDiv) or isinstance(op.y, c.Mul): y = f'({y})'
    return f'{x}/{y}'

  @staticmethod
  def _print_Pow(op: c.Pow) -> str:
    x = Printer._print_regular(op.x)
    y = Printer._print_regular(op.y)
    if op.x.priority < op.priority or isinstance(op.x, c.Pow): x = f'({x})'
    if op.y.priority < op.priority or isinstance(op.x, c.Pow): y = f'({y})'
    return f'{x}^{y}'
  
  @staticmethod
  def _print_Log(op: c.Log) -> str:
    x = Printer._print_regular(op.x)
    y = Printer._print_regular(op.base)
    return f'Log_{y}({x})'
  
  @staticmethod
  def _print_PrintableLn(op: PrintableLn) -> str:
    x = Printer._print_regular(op.x)
    return f'Ln({x})'
  
  @staticmethod
  def _print_Const(op: c.Const) -> str:
    return f'{float(op.x)}'
  
  @staticmethod
  def _print_Var(op: c.Var) -> str:
    return f'{op.name}'

class PrintableSub(Expr): 
  def __init__(self, x: Expr, y: Expr) -> None:
    self.x = x
    self.y = y
    self.args = (x,y,)
    self.fxn = BaseOps.NoOp
    self.priority = 1

class PrintableDiv(Expr):
  def __init__(self, x: Expr, y: Expr) -> None:
    self.x = x
    self.y = y
    self.args = (x,y,)
    self.fxn = BaseOps.NoOp
    self.priority = 2
  
class PrintableLn(Expr):
  def __init__(self, x: Expr) -> None:
    self.x = x
    self.args = (x,)
    self.fxn = BaseOps.NoOp
    self.priority = 4

class Printer(Expr):
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
  def _print_regular(expression: Expr) -> str:
    print_method = getattr(PrintRegular, f'_print_{expression.__class__.__name__}', None)
    
    if not print_method: raise NameError(f'Missing print options for op of type {type(expression)}')
    return print_method(expression)
    # def format_argument(arg, expr_priority):
    #   arg_str = Printer._print_regular(arg) if isinstance(arg, Expr) else arg
    #   return f'({arg_str})' if expr_priority > arg.priority else f'{arg_str}'
    
    # if is_op_type(expression, c.Const): return f'{float(expression.x)}'
    # if is_op_type(expression, c.Var): return f'{expression.name}'

    # argument_one = format_argument(expression.args[0], expression.priority)
    # if is_op_type(expression, c.Log): argument_one = Printer._print_regular(expression.args[0])
    # if is_op_type(expression, c.Neg): 
    #   argument_one = f'{Printer._print_regular(expression.args[0])}'
    #   argument_one = f'({argument_one})' if not expression.args[0].fxn in [BaseOps.Const, BaseOps.Var] else f'{argument_one}'
    # if len(expression.args) == 2:
    #   argument_two = format_argument(expression.args[1], expression.priority)
    #   if isinstance(expression, PrintableSub):
    #     return f'{argument_one} - {argument_two}'
    #   elif isinstance(expression, PrintableDiv):
    #     return f'{argument_one}/{argument_two}'
    #   elif is_op_type(expression, c.Add):
    #     return f'{argument_one} + {argument_two}'
    #   elif is_op_type(expression, c.Mul):
    #     return f'{argument_one}*{argument_two}'
    #   elif is_op_type(expression, c.Pow):
    #     return f'{argument_one}^{argument_two}'
    #   elif is_op_type(expression, c.Log):
    #     return f'log_{argument_one}({argument_two})'
    # if isinstance(expression, PrintableLn):
    #   return f'ln({argument_one})'
    # elif is_op_type(expression, c.Neg):
    #   return f'-{argument_one}'

    raise AttributeError(f'Missing print options for op of type {type(expression)}')

  @staticmethod
  def _print(expression: Expr) -> str:
    if Printer.Settings.Simplify:
      from calcora.match import SymbolicPatternMatcher
      expression = SymbolicPatternMatcher.match(expression)
    if Printer.Settings.Rewrite: 
      from calcora.match import Pattern, PatternMatcher
      RewriteOpsPatternMatcher = PatternMatcher([
        Pattern(c.Add(NamedAny('x'), c.Neg(NamedAny('y'))), lambda x,y: PrintableSub(x, y)),
        Pattern(c.Mul(NamedAny('x'), c.Pow(NamedAny('y'), c.Neg(c.Const(1)))), lambda x,y: PrintableDiv(x, y)),
        Pattern(c.Log(NamedAny('x'), c.Const(math.e)), lambda x: PrintableLn(x)),
      ])
      expression = RewriteOpsPatternMatcher.match(expression)
    if globals.Settings.Printing == globals.PrintOptions.Class: return Printer._print_classes(expression)
    elif globals.Settings.Printing == globals.PrintOptions.Latex: return Printer._print_latex(expression)
    else: return Printer._print_regular(expression)
