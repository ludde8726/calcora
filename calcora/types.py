from typing import Union
from mpmath import mpc, mpf

NumberLike = Union[int, float, str, complex, mpf, mpc]
CalcoraNumber = Union[mpc, mpf]