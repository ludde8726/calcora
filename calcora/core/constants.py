from calcora.core.ops import Complex, Const, Constant, Neg
from calcora.core.registry import ConstantRegistry
from calcora.core.numeric import Numeric

from mpmath import mp

E = Constant(mp.e, name='e')
PI = Constant(mp.pi, name='π', latex_name='\\pi')

Zero = Const(Numeric(0))
One = Const(Numeric(1))
Two = Const(Numeric(2))
Three = Const(Numeric(3))
Four = Const(Numeric(4))
Five = Const(Numeric(5))
Six = Const(Numeric(6))
Seven = Const(Numeric(7))
Eight = Const(Numeric(8))
Nine = Const(Numeric(9))

NegOne = Neg(One)
OneHalf = Const(Numeric(0.5))

I = Complex(Zero, One)

ConstantRegistry.register(E)
ConstantRegistry.register(PI)