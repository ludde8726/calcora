from calcora.core.registry import FunctionRegistry

from calcora.core.composite_ops import Div, Ln, Sub
from calcora.core.baseops import Add, Const, Complex, Neg, Mul, Var, Log, Pow, AnyOp

FunctionRegistry.register(Var)
FunctionRegistry.register(Const)
FunctionRegistry.register(Complex)
FunctionRegistry.register(Add)
FunctionRegistry.register(Neg)
FunctionRegistry.register(Mul)
FunctionRegistry.register(Log)
FunctionRegistry.register(Pow)
FunctionRegistry.register(AnyOp)

FunctionRegistry.register(Div)
FunctionRegistry.register(Sub)
FunctionRegistry.register(Ln)

if __name__ == "__main__":
  x = Var('x')
  expr = x / 2 + 4
  print(Const(expr.eval(x=Const(1))))