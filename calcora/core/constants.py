from calcora.core.ops import Constant
from calcora.core.registry import ConstantRegistry

from mpmath import mp

E = Constant(mp.e, name='e')
PI = Constant(mp.pi, name='π')

ConstantRegistry.register(E)
ConstantRegistry.register(PI)