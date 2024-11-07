from typing import Union

from mpmath import mpf, mpc

NumberLike = Union[int, float, str, complex, mpf, mpc]
RealNumberLike = Union[int, float, str, mpf]
CalcoraNumber = Union[mpc, mpf]