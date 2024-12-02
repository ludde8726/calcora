from __future__ import annotations

import unittest

from calcora.core.ops import Complex, Const, Neg
from calcora.core.number import Number

from mpmath import mpc, mpf

class TestNumberCreation(unittest.TestCase):
  def test_complex_from_string(self) -> None:
    self.assertEqual(Number('4+9j'), Complex(Const(4), Const(9)))
    self.assertEqual(Number('4 + 9j'), Complex(Const(4), Const(9)))
    self.assertEqual(Number('4+9i'), Complex(Const(4), Const(9)))
    self.assertEqual(Number('4 + 9i'), Complex(Const(4), Const(9)))

  def test_negative_complex_from_string(self) -> None:
    self.assertEqual(Number('4-9j'), Complex(Const(4), Neg(Const(9))))
    self.assertEqual(Number('4 - 9j'), Complex(Const(4), Neg(Const(9))))
    self.assertEqual(Number('4-9i'), Complex(Const(4), Neg(Const(9))))
    self.assertEqual(Number('4 - 9i'), Complex(Const(4), Neg(Const(9))))

  def test_const_from_string(self) -> None:
    self.assertEqual(Number('1'), Const(1))
    self.assertEqual(Number('13'), Const(13))
    self.assertEqual(Number('011'), Const(11))

  def test_negative_const_from_string(self) -> None:
    self.assertEqual(Number('-1'), Neg(Const(1)))
    self.assertEqual(Number('-13'), Neg(Const(13)))
    self.assertEqual(Number('-011'), Neg(Const(11)))

  def test_complex_from_python_complex(self) -> None:
    self.assertEqual(Number(complex(4, 9)), Complex(Const(4), Const(9)))
    self.assertEqual(Number(4 + 9j), Complex(Const(4), Const(9)))
    self.assertEqual(Number(complex(0, 10)), Complex(Const(0), Const(10)))

  def test_negative_complex_from_python_complex(self) -> None:
    self.assertEqual(Number(complex(-4, -9)), Complex(Neg(Const(4)), Neg(Const(9))))
    self.assertEqual(Number(4 - 9j), Complex(Const(4), Neg(Const(9))))
    self.assertEqual(Number(complex(-0, -10)), Complex(Const(0), Neg(Const(10))))

  def test_const_from_python_complex(self) -> None:
    self.assertEqual(Number(complex(1)), Const(1))
    self.assertEqual(Number(complex(1, 0)), Const(1))
    self.assertEqual(Number(1 + 0j), Const(1))
    self.assertEqual(Number(0 + 0j), Const(0))

  def test_negative_const_from_python_complex(self) -> None:
    self.assertEqual(Number(complex(-1)), Neg(Const(1)))
    self.assertEqual(Number(complex(-1, 0)), Neg(Const(1)))
    self.assertEqual(Number(-1 + 0j), Neg(Const(1)))
    self.assertEqual(Number(-0 + 0j), Const(0))

  def test_complex_from_mpmath_mpc(self) -> None:
    self.assertEqual(Number(mpc(4, 9)), Complex(Const(4), Const(9)))

  def test_negative_complex_from_mpmath_mpc(self) -> None:
    self.assertEqual(Number(mpc(-4, -9)), Complex(Neg(Const(4)), Neg(Const(9))))

  def test_const_from_mpmath_mpf(self) -> None:
    self.assertEqual(Number(mpf(4)), Const(4))

  def test_negative_const_from_mpmath_mpf(self) -> None:
    self.assertEqual(Number(mpf(-4)), Neg(Const(4)))

  def test_const_from_python_float(self) -> None:
    self.assertEqual(Number(4.0), Const(4))
    self.assertEqual(Number(float(4)), Const(4))

  def test_negative_const_from_python_float(self) -> None:
    self.assertEqual(Number(-4.0), Neg(Const(4)))
    self.assertEqual(Number(float(-4)), Neg(Const(4)))

  def test_const_from_python_int(self) -> None:
    self.assertEqual(Number(4), Const(4))
    self.assertEqual(Number(int(4.0)), Const(4))

  def test_negative_const_from_python_int(self) -> None:
    self.assertEqual(Number(-4), Neg(Const(4)))
    self.assertEqual(Number(int(-4.0)), Neg(Const(4)))


if __name__ == '__main__':
  unittest.main()
