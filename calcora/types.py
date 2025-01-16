from typing import Union

from mpmath import mpf, mpc

NumberLike = Union[int, float, str, complex, mpf, mpc]
RealNumberLike = Union[int, float, str, mpf]
CalcoraNumber = Union[mpc, mpf]
NumericType = Union[float, int, str, complex, mpf, mpc]
RealNumeric = Union[float, int, mpf]