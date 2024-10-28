import calcora as c
from calcora.expression import Expr, BaseOps
from calcora.printing.printops import PrintableDiv, PrintableLn, PrintableSub

class Repr:
  @staticmethod
  def _print(expression: Expr) -> str:
    method = getattr(Repr, f'_print_{expression.__class__.__name__}', None)
    if not method: raise NameError(f'Missing print function for op of type {type(expression)}')
    return method(expression)

  @staticmethod
  def _print_Add(op: c.Add) -> str:
    x = Repr._print(op.x)
    y = Repr._print(op.y)
    if op.x.priority < op.priority: x = f'({x})'
    if op.y.priority < op.priority: y = f'({y})'
    return f'{x} + {y}'
  
  @staticmethod
  def _print_PrintableSub(op: PrintableSub) -> str:
    x = Repr._print(op.x)
    y = Repr._print(op.y)
    if op.x.priority < op.priority and not op.x.fxn == BaseOps.Neg: x = f'({x})'
    if op.y.priority < op.priority or isinstance(op.y, PrintableSub) or op.y.fxn == BaseOps.Neg or op.y.fxn == BaseOps.Add: y = f'({y})'
    return f'{x} - {y}'
  
  @staticmethod
  def _print_Neg(op: c.Neg) -> str:
    x = Repr._print(op.x)
    if op.x.fxn != BaseOps.Const and op.fxn != BaseOps.Var: x = f'({x})'
    return f'-{x}'
  
  @staticmethod
  def _print_Mul(op: c.Mul) -> str:
    x = Repr._print(op.x)
    y = Repr._print(op.y)
    if op.x.priority < op.priority: x = f'({x})'
    if op.y.priority < op.priority: y = f'({y})'
    return f'{x}*{y}'
  
  @staticmethod
  def _print_PrintableDiv(op: PrintableDiv) -> str:
    x = Repr._print(op.x)
    y = Repr._print(op.y)
    if op.x.priority < op.priority or isinstance(op.x, PrintableDiv): x = f'({x})'
    if op.y.priority < op.priority or isinstance(op.y, PrintableDiv) or isinstance(op.y, c.Mul): y = f'({y})'
    return f'{x}/{y}'

  @staticmethod
  def _print_Pow(op: c.Pow) -> str:
    x = Repr._print(op.x)
    y = Repr._print(op.y)
    if op.x.priority < op.priority or isinstance(op.x, c.Pow): x = f'({x})'
    if op.y.priority < op.priority or isinstance(op.x, c.Pow): y = f'({y})'
    return f'{x}^{y}'
  
  @staticmethod
  def _print_Log(op: c.Log) -> str:
    x = Repr._print(op.x)
    y = Repr._print(op.base)
    return f'Log_{y}({x})'
  
  @staticmethod
  def _print_PrintableLn(op: PrintableLn) -> str:
    x = Repr._print(op.x)
    return f'Ln({x})'
  
  @staticmethod
  def _print_Const(op: c.Const) -> str:
    return f'{float(op.x)}'
  
  @staticmethod
  def _print_Var(op: c.Var) -> str:
    return f'{op.name}'