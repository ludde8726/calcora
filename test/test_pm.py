from __future__ import annotations

import os
import random
import unittest

from typing import List, Type
from typing import TYPE_CHECKING

from calcora.core.ops import Add, Complex, Const, Div, Log, Mul, Neg, Pow, Sub, Var
from calcora.globals import ec
from calcora.match.match import SymbolicPatternMatcher

if TYPE_CHECKING:
  from calcora.core.expression import Expr

x = Var('x')
ec.precision = int(os.getenv("PREC", 16))

def generate_random_expression(depth: int) -> Expr:
  if depth == 1: return Const(random.uniform(1, 10))
  else:
    operation = random.choice([Add, Sub, Mul, Div, Neg])
    left_expr = generate_random_expression(depth - 1)
    if operation is Add or operation is Sub or operation is Div:
      right_expr = generate_random_expression(depth - 1)
      return operation(left_expr, right_expr)
    else: return Neg(left_expr)

class TestSymbolicPatternMatcher(unittest.TestCase):
  def setUp(self) -> None:
    self.pm = SymbolicPatternMatcher
  
  def test_addition_of_zero(self) -> None:
    expr = Add(x, Const(0))
    self.assertEqual(self.pm.match(expr), x)
    expr = Add(Const(0), x)
    self.assertEqual(self.pm.match(expr), x)

  def test_negation_of_negation(self) -> None:
    expr = Neg(Neg(x))
    self.assertEqual(self.pm.match(expr), x)

  def test_negation_of_zero(self) -> None:
    expr = Neg(Const(0))
    self.assertEqual(self.pm.match(expr), Const(0))

  def test_multiplication_by_one(self) -> None:
    expr = Mul(x, Const(1))
    self.assertEqual(self.pm.match(expr), x)
    expr = Mul(Const(1), x)
    self.assertEqual(self.pm.match(expr), x)

  def test_multiplication_by_zero(self) -> None:
    expr = Mul(x, Const(0))
    self.assertEqual(self.pm.match(expr), Const(0))
    expr = Mul(Const(0), x)
    self.assertEqual(self.pm.match(expr), Const(0))

  def test_power_of_zero(self) -> None:
    expr = Pow(Const(0), x)
    self.assertEqual(self.pm.match(expr), Const(0))

  def test_x_to_the_power_of_zero(self) -> None:
    expr = Pow(x, Const(0))
    self.assertEqual(self.pm.match(expr), Const(1))

  def test_power_of_one(self) -> None:
    expr = Pow(Const(1), x)
    self.assertEqual(self.pm.match(expr), Const(1))

  def test_x_to_the_power_of_one(self) -> None:
    expr = Pow(x, Const(1))
    self.assertEqual(self.pm.match(expr), x)

  def test_multiplication_by_neg_one(self) -> None:
    expr = Mul(x, Neg(Const(1)))
    self.assertEqual(self.pm.match(expr), Neg(x))

  def test_log_of_x_base_x(self) -> None:
    expr = Log(Const(2), Const(2))
    self.assertEqual(self.pm.match(expr), Const(1))

  def test_addition_of_opposite_terms(self) -> None:
    expr = Add(x, Neg(x))
    self.assertEqual(self.pm.match(expr), Const(0))

  def test_multiplication_by_inverse(self) -> None:
    expr = Mul(x, Pow(x, Neg(Const(1))))
    self.assertEqual(self.pm.match(expr), Const(1))

  def test_square_of_x(self) -> None:
    expr = Mul(x, x)
    self.assertEqual(self.pm.match(expr), Pow(x, Const(2)))

  def test_addition_of_scaled_x(self) -> None:
    expr = Add(x, Mul(Const(2), x))
    self.assertEqual(self.pm.match(expr), Mul(Const(3), x))
    expr = Add(x, Mul(x, Const(2)))
    self.assertEqual(self.pm.match(expr), Mul(Const(3), x))
    expr = Add(Mul(Const(2), x), x)
    self.assertEqual(self.pm.match(expr), Mul(Const(3), x))
    expr = Add(Mul(x, Const(2)), x)
    self.assertEqual(self.pm.match(expr), Mul(Const(3), x))

  def test_addition_of_several_x_terms(self) -> None:
    expr = Add(Mul(Const(2), x), Mul(Const(3), x))
    self.assertEqual(self.pm.match(expr), Mul(Const(5), x))
    expr = Add(Mul(x, Const(2)), Mul(Const(3), x))
    self.assertEqual(self.pm.match(expr), Mul(Const(5), x))
    expr = Add(Mul(Const(2), x), Mul(x, Const(3)))
    self.assertEqual(self.pm.match(expr), Mul(Const(5), x))
    expr = Add(Mul(x, Const(2)), Mul(x, Const(3)))
    self.assertEqual(self.pm.match(expr), Mul(Const(5), x))

  def test_multiplication_with_power(self) -> None:
    expr = Mul(x, Pow(x, Const(2)))
    self.assertEqual(self.pm.match(expr), Pow(x, Const(3)))
    expr = Mul(Pow(x, Const(2)), x)

  def test_multiplication_of_two_powers(self) -> None:
    expr = Mul(Pow(x, Const(3)), Pow(x, Const(2)))
    self.assertEqual(self.pm.match(expr), Pow(x, Add(Const(3), Const(2))))
    expr = Mul(Pow(x, Const(2)), Pow(x, Const(3)))
    self.assertEqual(self.pm.match(expr), Pow(x, Add(Const(2), Const(3))))

  def test_nested_power(self) -> None:
    expr = Pow(Pow(x, Const(2)), Const(3))
    self.assertEqual(self.pm.match(expr), Pow(x, Mul(Const(2), Const(3))))

  def test_complex_number_with_zero_imaginary_part(self) -> None:
    expr = Complex(x, Const(0))
    self.assertEqual(self.pm.match(expr), x)

  def test_correct_eval_on_patterns(self) -> None:
    for _ in range(500):
      expr = generate_random_expression(random.randint(1, 7))
      matched_expr = self.pm.match(expr)
      self.assertEqual(matched_expr._eval(), expr._eval())

if __name__ == '__main__':
  unittest.main()