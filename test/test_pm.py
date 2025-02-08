from __future__ import annotations

import os
import random
import unittest

from typing import List, Type
from typing import TYPE_CHECKING

from calcora.core.ops import Add, Complex, Const, Log, Mul, Neg, Pow, Var
from calcora.core.numeric import Numeric
from calcora.core.constants import Zero, One, Two, Three, Five
from calcora.globals import ec
from calcora.match.match import SymbolicPatternMatcher

if TYPE_CHECKING:
  from calcora.core.expression import Expr

x = Var('x')
ec.precision = int(os.getenv("PREC", 16))

def generate_random_expression(depth: int) -> Expr:
  if depth == 1: return Const(Numeric(random.uniform(1, 10)))
  else:
    operation : Type[Expr] = random.choice([Add, Mul, Neg])
    left_expr = generate_random_expression(depth - 1)
    if operation is Add or operation is Mul:
      right_expr = generate_random_expression(depth - 1)
      return operation(left_expr, right_expr)
    else: return Neg(left_expr)

class TestSymbolicPatternMatcher(unittest.TestCase):
  def setUp(self) -> None:
    self.pm = SymbolicPatternMatcher
  
  def test_addition_of_zero(self) -> None:
    expr = Add(x, Zero)
    self.assertEqual(self.pm.match(expr), x)
    expr = Add(Zero, x)
    self.assertEqual(self.pm.match(expr), x)

  def test_negation_of_negation(self) -> None:
    expr = Neg(Neg(x))
    self.assertEqual(self.pm.match(expr), x)

  def test_negation_of_zero(self) -> None:
    expr = Neg(Zero)
    self.assertEqual(self.pm.match(expr), Zero)

  def test_multiplication_by_one(self) -> None:
    expr = Mul(x, One)
    self.assertEqual(self.pm.match(expr), x)
    expr = Mul(One, x)
    self.assertEqual(self.pm.match(expr), x)

  def test_multiplication_by_zero(self) -> None:
    expr = Mul(x, Zero)
    self.assertEqual(self.pm.match(expr), Zero)
    expr = Mul(Zero, x)
    self.assertEqual(self.pm.match(expr), Zero)

  def test_power_of_zero(self) -> None:
    expr = Pow(Zero, x)
    self.assertEqual(self.pm.match(expr), Zero)

  def test_x_to_the_power_of_zero(self) -> None:
    expr = Pow(x, Zero)
    self.assertEqual(self.pm.match(expr), One)

  def test_power_of_one(self) -> None:
    expr = Pow(One, x)
    self.assertEqual(self.pm.match(expr), One)

  def test_x_to_the_power_of_one(self) -> None:
    expr = Pow(x, One)
    self.assertEqual(self.pm.match(expr), x)

  def test_multiplication_by_neg_one(self) -> None:
    expr = Mul(x, Neg(One))
    self.assertEqual(self.pm.match(expr), Neg(x))

  def test_log_of_x_base_x(self) -> None:
    expr = Log(Two, Two)
    self.assertEqual(self.pm.match(expr), One)

  def test_addition_of_opposite_terms(self) -> None:
    expr = Add(x, Neg(x))
    self.assertEqual(self.pm.match(expr), Zero)

  def test_multiplication_by_inverse(self) -> None:
    expr = Mul(x, Pow(x, Neg(One)))
    self.assertEqual(self.pm.match(expr), One)

  def test_square_of_x(self) -> None:
    expr = Mul(x, x)
    self.assertEqual(self.pm.match(expr), Pow(x, Two))

  def test_addition_of_scaled_x(self) -> None:
    expr = Add(x, Mul(Two, x))
    self.assertEqual(self.pm.match(expr), Mul(Three, x))
    expr = Add(x, Mul(x, Two))
    self.assertEqual(self.pm.match(expr), Mul(Three, x))
    expr = Add(Mul(Two, x), x)
    self.assertEqual(self.pm.match(expr), Mul(Three, x))
    expr = Add(Mul(x, Two), x)
    self.assertEqual(self.pm.match(expr), Mul(Three, x))

  def test_addition_of_several_x_terms(self) -> None:
    expr = Add(Mul(Two, x), Mul(Three, x))
    self.assertEqual(self.pm.match(expr), Mul(Five, x))
    expr = Add(Mul(x, Two), Mul(Three, x))
    self.assertEqual(self.pm.match(expr), Mul(Five, x))
    expr = Add(Mul(Two, x), Mul(x, Three))
    self.assertEqual(self.pm.match(expr), Mul(Five, x))
    expr = Add(Mul(x, Two), Mul(x, Three))
    self.assertEqual(self.pm.match(expr), Mul(Five, x))

  def test_multiplication_with_power(self) -> None:
    expr = Mul(x, Pow(x, Two))
    self.assertEqual(self.pm.match(expr), Pow(x, Three))
    expr = Mul(Pow(x, Two), x)

  def test_multiplication_of_two_powers(self) -> None:
    expr = Mul(Pow(x, Three), Pow(x, Two))
    self.assertEqual(self.pm.match(expr), Pow(x, Add(Three, Two)))
    expr = Mul(Pow(x, Two), Pow(x, Three))
    self.assertEqual(self.pm.match(expr), Pow(x, Add(Two, Three)))

  def test_nested_power(self) -> None:
    expr = Pow(Pow(x, Two), Three)
    self.assertEqual(self.pm.match(expr), Pow(x, Mul(Two, Three)))

  def test_complex_number_with_zero_imaginary_part(self) -> None:
    expr = Complex(x, Zero)
    self.assertEqual(self.pm.match(expr), x)

  def test_correct_eval_on_patterns(self) -> None:
    for _ in range(500):
      expr = generate_random_expression(random.randint(1, 7))
      matched_expr = self.pm.match(expr)
      self.assertEqual(matched_expr._eval(), expr._eval())

if __name__ == '__main__':
  unittest.main()