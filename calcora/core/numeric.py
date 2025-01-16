from __future__ import annotations

from typing import Optional, Union

from calcora.globals import ec
from calcora.types import CalcoraNumber, NumericType, RealNumeric
from calcora.utils import mpmathcast

from mpmath import fabs, floor, ceil
from mpmath import mpf, mpc, nstr, workdps

class Numeric:
  def __init__(self, x: NumericType, precision: Optional[int] = None, skip_conversion: bool = False) -> None:
    self.precision = precision if precision else ec.precision # Note: This is the maximum precision the number is stored as
    self.value : CalcoraNumber = mpmathcast(x, precision=self.precision) if not skip_conversion else x

  @property
  def real(self) -> Numeric: return Numeric(mpc(self.value.real), precision=self.precision, skip_conversion=True)
  @property
  def imag(self) -> Optional[Numeric]: return Numeric(mpc(self.value.imag), precision=self.precision, skip_conversion=True) if self.value.imag else Numeric(mpc(0), precision=self.precision, skip_conversion=True)
  @property
  def re(self) -> Numeric: return self.real
  @property
  def im(self) -> Optional[Numeric]: return self.imag

  @staticmethod
  def numeric_cast(x: Union[NumericType, Numeric], precision: Optional[int] = None) -> Numeric:
    if isinstance(x, Numeric): return x
    return Numeric(x, precision=precision)

  def __str__(self) -> str:
    # Note: Casting to str does not do anything, it's just to keep mypy happy
    if self.imag: return self._print_complex()
    else: return str(nstr(self.value.real, self.precision))

  def __repr__(self) -> str:
    return f'Numeric[{"complex" if self.value.imag else "real"}]({str(self)})'

  def _print_complex(self) -> str:
    if self.value.imag == 1: return f"{nstr(self.value.real, self.precision)} + i" if self.value.real != 0 else "i"
    elif self.value.imag == -1: return f"{nstr(self.value.real, self.precision)} - i" if self.value.real != 0 else "-i"
    elif self.value.real == 0: return f"{nstr(self.value.imag, self.precision)}i" if self.value.imag != 0 else "0"
    else: return f"{nstr(self.value.real, self.precision)} + {nstr(self.value.imag, self.precision)}i" if self.value.imag > 0 else f"{self.value.real} - {-self.value.imag}i"

  def __bool__(self) -> bool:
    return bool(self.value)
  
  def __eq__(self, other: object) -> bool:
    # Note: Casting to bool does not do anything, it's just to keep mypy happy
    if isinstance(other, (int, float, complex, mpc, mpf, Numeric)): 
      if isinstance(other, Numeric): return bool(self.value == other.value)
      elif isinstance(other, (int, float, complex)): return bool(mpc(other) == self.value)
      else: return bool(self.value == other)
    else: return False

  def __gt__(self, other: Union[Numeric, RealNumeric]) -> bool:
    if self.value.imag: raise ValueError("Complex numbers have no ordering!")
    if not isinstance(other, Numeric): other = Numeric(other)
    return bool(self.value.real > other.value.real)

  def __lt__(self, other: Union[Numeric, RealNumeric]) -> bool:
    if self.value.imag: raise ValueError("Complex numbers have no ordering!")
    if not isinstance(other, Numeric): other = Numeric(other)
    return bool(self.value.real < other.value.real)
  
  def __ge__(self, other: Union[Numeric, RealNumeric]) -> bool:
    return self > other or self == other
  
  def __le__(self, other: Union[Numeric, RealNumeric]) -> bool:
    return self < other or self == other
  
  def __float__(self) -> float:
    return float(self.value.real)
  
  def get_dps(self, other: Union[NumericType, Numeric]) -> int:
    if isinstance(other, Numeric): return max(self.precision, other.precision)
    return self.precision
  
  def __pos__(self) -> Numeric: return self
  def __neg__(self) -> Numeric: 
    with workdps(self.precision): return Numeric(-self.value, precision=self.precision, skip_conversion=True)
  def __abs__(self) -> Numeric: 
    with workdps(self.precision): return Numeric(fabs(self.value), precision=self.precision, skip_conversion=True)
  def __floor__(self) -> Numeric: 
    with workdps(self.precision): return Numeric(floor(self.value), precision=self.precision, skip_conversion=True)
  def __ceil__(self) -> Numeric: 
    with workdps(self.precision): return Numeric(ceil(self.value), precision=self.precision, skip_conversion=True)
  
  def __add__(self, other: Union[NumericType, Numeric]) -> Numeric: 
    with workdps(work_dps := self.get_dps(other)): return Numeric(self.value + Numeric.numeric_cast(other).value, precision=work_dps, skip_conversion=True)
  def __sub__(self, other: Union[NumericType, Numeric]) -> Numeric:
    with workdps(work_dps := self.get_dps(other)): return Numeric(self.value - Numeric.numeric_cast(other).value, precision=work_dps, skip_conversion=True)
  def __mul__(self, other: Union[NumericType, Numeric]) -> Numeric:
    with workdps(work_dps := self.get_dps(other)): return Numeric(self.value * Numeric.numeric_cast(other).value, precision=work_dps, skip_conversion=True)
  def __truediv__(self, other: Union[NumericType, Numeric]) -> Numeric:
    with workdps(work_dps := self.get_dps(other)): return Numeric(self.value / Numeric.numeric_cast(other).value, precision=work_dps, skip_conversion=True)
  def __floordiv__(self, other: Union[NumericType, Numeric]) -> Numeric:
    with workdps(work_dps := self.get_dps(other)): return Numeric(self.value // Numeric.numeric_cast(other).value, precision=work_dps, skip_conversion=True)
  def __pow__(self, other: Union[NumericType, Numeric]) -> Numeric:
    with workdps(work_dps := self.get_dps(other)): return Numeric(self.value ** Numeric.numeric_cast(other).value, precision=work_dps, skip_conversion=True)

  def __radd__(self, other: Union[NumericType, Numeric]) -> Numeric: 
    with workdps(work_dps := self.get_dps(other)): return Numeric(Numeric.numeric_cast(other).value + self.value, precision=work_dps, skip_conversion=True)
  def __rsub__(self, other: Union[NumericType, Numeric]) -> Numeric:
    with workdps(work_dps := self.get_dps(other)): return Numeric(Numeric.numeric_cast(other).value - self.value, precision=work_dps, skip_conversion=True)
  def __rmul__(self, other: Union[NumericType, Numeric]) -> Numeric:
    with workdps(work_dps := self.get_dps(other)): return Numeric(Numeric.numeric_cast(other).value * self.value, precision=work_dps, skip_conversion=True)
  def __rtruediv__(self, other: Union[NumericType, Numeric]) -> Numeric:
    with workdps(work_dps := self.get_dps(other)): return Numeric(Numeric.numeric_cast(other).value / self.value, precision=work_dps, skip_conversion=True)
  def __rfloordiv__(self, other: Union[NumericType, Numeric]) -> Numeric:
    with workdps(work_dps := self.get_dps(other)): return Numeric(Numeric.numeric_cast(other).value // self.value, precision=work_dps, skip_conversion=True)
  def __rpow__(self, other: Union[NumericType, Numeric]) -> Numeric:
    with workdps(work_dps := self.get_dps(other)): return Numeric(Numeric.numeric_cast(other).value ** self.value, precision=work_dps, skip_conversion=True)