from ops import BaseOps
from ops import Op, Add, Const, Exp, Ln, Log, Mul, Neg, Var

from typing import Callable, Dict, Iterable, List, Optional, TypeGuard

class AnyOp(Op):
  def __init__(self, match: bool = False, name: str="x", assert_const_like=False) -> None:
    self.match = match
    self.name = name
    self.assert_const_like = assert_const_like
    super().__init__()

def is_any_op(op: Op) -> TypeGuard[AnyOp]:
  return op.fxn == BaseOps.AnyOp

def is_log_op(op: Op) -> TypeGuard[Log]:
  return op.fxn == BaseOps.Log

def is_const_like(op: Op) -> bool:
  if op.fxn == BaseOps.Const: return True
  if op.fxn == BaseOps.Neg and op.args[0].fxn == BaseOps.Const: return True
  return False

def reconstruct_op(op: Op, *args):
  if is_log_op(op) and op.natural:
    return Ln(args[0])
  return op.__class__(*args)

ConstLike = lambda name: AnyOp(name=name, assert_const_like=True)
NamedAny = lambda name: AnyOp(name=name)
MatchedSymbol = lambda name: AnyOp(name=name, match=True)

class Pattern:
  def __init__(self, pattern: Op, replacement: Callable[..., Op]) -> None:
    self.pattern = pattern
    self.replacement = replacement
    self._binding: Dict[str, Op] = {}

  def match(self, op: Op) -> Op:
    self._binding = {}
    new_args = [self.match(arg) for arg in op.args] if op.fxn != BaseOps.Const and op.fxn != BaseOps.Var else op.args
    if op.fxn == BaseOps.Const: return op
    op = reconstruct_op(op, *new_args)
    if op.fxn == self.pattern.fxn and len(op.args) == len(self.pattern.args):
      if self._match(op, self.pattern):
        return self.replacement(**self._binding)
    return reconstruct_op(op, *new_args)
  
  def _match(self, op: Op, subpattern: Op) -> bool:
    if not (len(op.args) == len(subpattern.args)) and not subpattern.fxn == BaseOps.AnyOp: return False
    
    if is_any_op(subpattern):
      if subpattern.assert_const_like and not is_const_like(op): return False
      if subpattern.match and subpattern.name in self._binding:
        return self._binding[subpattern.name] == op
      self._binding[subpattern.name] = op
      return True
  
    if op.fxn == subpattern.fxn and len(op.args) == len(subpattern.args):
      if op.fxn == BaseOps.Const: return op.args == subpattern.args
      if subpattern.args:
        return all(self._match(op_arg, sub_arg) for op_arg, sub_arg in zip(op.args, subpattern.args))
      
    return False

class PatternMatcher:
  def __init__(self, patterns: Optional[List[Pattern]] = None) -> None:
    self.patterns = patterns if patterns else list()
  
  def add_rules(self, patterns: List[Pattern]):
    self.patterns.extend(patterns)
  
  def match(self, expression: Op):
    simplified_expr: Op = expression
    for pattern in self.patterns:
      simplified_expr = pattern.match(simplified_expr)
    if simplified_expr != expression: simplified_expr = self.match(simplified_expr)
    return simplified_expr
  
def multi_flatten(args: Iterable[Op], op_type: BaseOps):
  new_args = []
  for arg in args: 
    if arg.fxn == op_type: new_args.extend(multi_flatten(arg.args, op_type))
    else: new_args.append(arg)
  return new_args

def simplify(op: Op) -> Op:
  simplified_args = [simplify(arg) for arg in op.args]

  if op.fxn == BaseOps.Const: return op
  elif op.fxn == BaseOps.Add:
    simplified_args = multi_flatten(simplified_args, BaseOps.Add)
    const_sum = sum([arg.eval() for arg in simplified_args if arg.fxn == BaseOps.Const])
    non_const_args = [arg for arg in simplified_args if arg.fxn != BaseOps.Const]
    simplified_args = [Const(const_sum), *non_const_args]
  elif op.fxn == BaseOps.Neg:
    inner = simplified_args[0]
    if inner.fxn == BaseOps.Neg: return simplify(inner.args[0])

  if op.fxn in [BaseOps.Add, BaseOps.Mul] and len(simplified_args) < 2:
    return Const(*[arg.eval() for arg in simplified_args])
  return op.__class__(*simplified_args)

SymbolicPatternMatcher = PatternMatcher([
  Pattern(Add(AnyOp(), Const(0)), lambda x: x), # x + 0 = x
  Pattern(Add(Const(0), AnyOp()), lambda x: x), # 0 + x = x

  Pattern(Neg(Neg(AnyOp())), lambda x: x), # -(-x) = x
  Pattern(Neg(Const(0)), lambda: Const(0)), # -(0) = 0

  Pattern(Mul(AnyOp(), Const(1)), lambda x: x), # 1 * x = x
  Pattern(Mul(Const(1), AnyOp()), lambda x: x), # x * 1 = x

  Pattern(Mul(AnyOp(), Const(0)), lambda x: Const(0)), # x * 1 = x
  Pattern(Mul(Const(0), AnyOp()), lambda x: Const(0)), # x * 1 = x

  Pattern(Exp(Const(0), AnyOp()), lambda x: Const(0)),
  Pattern(Exp(AnyOp(), Const(0)), lambda x: Const(1)),

  Pattern(Mul(MatchedSymbol('x'), Exp(MatchedSymbol(name='x'), 
                                                Neg(Const(1)))), lambda x: Const(1)), # x * x^(-1) = x/x = 1
  
  Pattern(Add(MatchedSymbol('x'), Mul(ConstLike('y'), MatchedSymbol('x'))), lambda x,y: Mul(Const(Add(y, Const(1)).eval()), x)), # x + yx = (y+1)x where y is a constant
  Pattern(Add(MatchedSymbol('x'), Mul(MatchedSymbol('x'), ConstLike('y'))), lambda x,y: Mul(Const(Add(y, Const(1)).eval()), x)), # x + xy = (y+1)x where y is a constant
  Pattern(Add(Mul(ConstLike('y'), MatchedSymbol('x')), MatchedSymbol('x')), lambda x,y: Mul(Const(Add(y, Const(1)).eval()), x)), # yx + x = (y+1)x where y is a constant
  Pattern(Add(Mul(MatchedSymbol('x'), ConstLike('y')), MatchedSymbol('x')), lambda x,y: Mul(Const(Add(y, Const(1)).eval()), x)), # xy + x = (y+1)x where y is a constant

  Pattern(Add(Mul(ConstLike('y'), MatchedSymbol('x')), Mul(ConstLike('z'), MatchedSymbol('x'))), lambda x,y,z: Mul(Const(Add(y, z).eval()), x)), # yx + zx = (y+z)x where y and z are constants
  Pattern(Add(Mul(MatchedSymbol('x'), ConstLike('y')), Mul(ConstLike('z'), MatchedSymbol('x'))), lambda x,y,z: Mul(Const(Add(y, z).eval()), x)), # xy + zx = (y+z)x where y and z are constants
  Pattern(Add(Mul(ConstLike('y'), MatchedSymbol('x')), Mul(MatchedSymbol('x'), ConstLike('z'))), lambda x,y,z: Mul(Const(Add(y, z).eval()), x)), # yx + xz = (y+z)x where y and z are constants
  Pattern(Add(Mul(MatchedSymbol('x'), ConstLike('y')), Mul(MatchedSymbol('x'), ConstLike('z'))), lambda x,y,z: Mul(Const(Add(y, z).eval()), x)), # xy + xz = (y+z)x where y and z are constants

  Pattern(Mul(MatchedSymbol('x'), Exp(MatchedSymbol('x'), ConstLike('y'))), lambda x,y: Exp(x, Const(Add(y, Const(1)).eval()))),    # x * x^y = x^(y+1) where y is a constant
  Pattern(Mul(Exp(MatchedSymbol('x'), ConstLike('y')), MatchedSymbol('x')), lambda x,y: Exp(x, Const(Add(y, Const(1)).eval()))),    # x^y * x = x^(y+1) where y is a constant
  Pattern(Mul(Exp(MatchedSymbol('x'), NamedAny('y')), Exp(MatchedSymbol('x'), NamedAny('z'))), lambda x,y,z: Exp(x, Add(y, z))),    # x^y * x^z = x^(y+z)
  Pattern(Exp(Exp(NamedAny('x'), NamedAny('y')), NamedAny('z')), lambda x,y,z: Exp(x, Mul(y, z))),                                  # (x^y)^z = x^(y*z)
])
if __name__ == '__main__':
  pm = SymbolicPatternMatcher

  test_expression = Add(
    Add(Mul(Const(1), Neg(Neg(Const(5)))), Const(0)),  # Should simplify to 5
    Add(Mul(Const(0), Const(10)), Mul(Const(7), Const(1)))  # Should simplify to 7
  )

  test_expression = Add(
                      Mul(
                        Add(
                          Mul(
                            Add(Var('x'), Const(0)),            # (x + 0)
                            Mul(Var('y'), Const(1))              # * (y * 1)
                          ),
                          Mul(
                            Add(Const(0), Var('z')),              # (0 + z)
                            Mul(Const(1), Add(Var('a'), Var('b')))  # * (1 * (a + b))
                          )
                        ),
                        Mul(
                          Add(
                            Var('c'),                             # c
                            Exp(Var('d'), Const(0))                # + (d^0) = 1
                          ),
                          Mul(
                            Add(
                              Mul(Var('e'), Const(1)),            # (e * 1)
                              Neg(Neg(Var('f')))                   # + (-(-f)) = f
                            ),
                            Mul(Var('g'), Const(0))                 # * (g * 0) = 0
                          )
                        )
                      ),
                      Add(
                        Mul(
                          Var('h'),                              # h
                          Exp(Var('h'), Neg(Const(1)))          # * (h^(-1))
                        ),
                        Mul(
                          Neg(Neg(Const(0))),                    # + (-(-0)) = 0
                          Add(
                            Var('i'),                            # i
                            Var('j')                             # + j
                          )
                        )
                      )
                    )
  
  test_expression = Add(Var('x'), Mul(Const(2), Var('x')))
  test_expression = Add(Mul(Const(234), Var('x')), Mul(Const(2), Var('x')))
  test_expression = Add(
                      Add(
                        Add(
                          Add(Var('x'), Const(0)),  # (x + 0)
                          Mul(Mul(Var('y'), Var('z')), Const(1))  # y * z * 1
                        ),
                        Add(
                          Neg(Neg(Mul(Var('a'), Var('b')))),  # -(-(a * b))
                          Mul(Var('c'), Exp(Var('c'), Neg(Const(1))))  # c * c^(-1)
                        )
                      ),

                      Add(
                        Add(
                          Add(Var('x'), Mul(Const(2), Var('x'))),  # x + 2x
                          Add(
                            Mul(Var('x'), Const(3)),  # x * 3
                            Mul(Var('x'), Const(2))   # x * 2
                          )
                        ),
                        Add(
                          Exp(Const(0), Var('x')),  # 0^x
                          Exp(Var('x'), Const(0))   # x^0
                        )
                      )
                    )


  print(f"Original expression: {test_expression}")
  print(f"Original expression eval: {test_expression}")
  simplified_expr = pm.match(test_expression)
  # simplified_expr = pm.match(simplified_expr)
  print(f"Simplified expression: {simplified_expr}")
  print(f"Simplified expression eval: {simplified_expr}") # 1+Var('i')+Var('j)