from calcora.core.ops import Constant, Const, Complex, Neg
from calcora.core.registry import ConstantRegistry

from mpmath import mp

E = Constant(mp.e, name='e')
PI = Constant(mp.pi, name='π', latex_name='\\pi')
I = Complex(Const(0), Const(1))
Zero = Const(0)
One = Const(1)
NegOne = Neg(Const(1))

ConstantRegistry.register(E)
ConstantRegistry.register(PI)