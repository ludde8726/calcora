from __future__ import annotations

import random

from typing import List, Type
from typing import TYPE_CHECKING
import unittest

from calcora.globals import pc
from calcora.match.match import SymbolicPatternMatcher
from calcora.match.partial_eval import partial_eval
from calcora.utils import is_const_like
from calcora.core.ops import Const, Add, Div, Pow, Ln, Log, Mul, Neg, Sub, Var

if TYPE_CHECKING:
  from calcora.core.expression import Expr

def generate_random_expression(depth: int, exponents: bool = False) -> Expr:
  if depth == 1:
    return Const(random.uniform(1, 10))
  else:
    operations : List[Type[Expr]] = [Add, Sub, Mul, Div, Neg]
    if exponents: operations.append(Pow)
    operation = random.choice(operations)
    if operation in [Add, Sub, Mul, Div]:
      left_expr = generate_random_expression(depth - 1, exponents=exponents)
      right_expr = generate_random_expression(depth - 1, exponents=exponents)
      return operation(left_expr, right_expr)
    elif operation == Pow:
      base = generate_random_expression(depth - 1, exponents=exponents)
      exponent = Const(random.randint(1, 10))
      return Pow(base, exponent)
    else:
      expr = generate_random_expression(depth - 1, exponents=exponents)
      return Neg(expr)

class TestPatternMatcher(unittest.TestCase):
  def setUp(self) -> None:
    self.pm = SymbolicPatternMatcher

  def test_addition_with_zero(self) -> None:
    self.assertEqual(self.pm.match(Add(Const(5), Const(0))), Const(5))
      
  def test_addition_with_zero_reversed(self) -> None:
    self.assertEqual(self.pm.match(Add(Const(0), Const(5))), Const(5))

  def test_negation_of_negation(self) -> None:
    self.assertEqual(self.pm.match(Neg(Neg(Const(3)))), Const(3))

  def test_negation_of_zero(self) -> None:
    self.assertEqual(self.pm.match(Neg(Const(0))), Const(0))

  def test_multiplication_by_one(self) -> None:
    self.assertEqual(self.pm.match(Mul(Const(1), Const(10))), Const(10))

  def test_multiplication_by_one_reversed(self) -> None:
    self.assertEqual(self.pm.match(Mul(Const(10), Const(1))), Const(10))

  def test_multiplication_by_zero(self) -> None:
    self.assertEqual(self.pm.match(Mul(Const(5), Const(0))), Const(0))

  def test_multiplication_by_zero_reversed(self) -> None:
    self.assertEqual(self.pm.match(Mul(Const(0), Const(5))), Const(0))

  def test_exponentiation_to_zero(self) -> None:
    self.assertEqual(self.pm.match(Pow(Const(2), Const(0))), Const(1))

  def test_exponentiation_of_zero(self) -> None:
    self.assertEqual(self.pm.match(Pow(Const(0), Const(3))), Const(0))

  def test_exponentiation_of_one(self) -> None:
    self.assertEqual(self.pm.match(Pow(Const(1), Const(3))), Const(1))

  def test_logarithm_with_same_base_and_value(self) -> None:
    self.assertEqual(self.pm.match(Log(Const(2), Const(2))), Const(1))

  def test_inverse_multiplication(self) -> None:
    self.assertEqual(self.pm.match(Mul(Const(2), Pow(Const(2), Neg(Const(1))))), Const(1))

  def test_constant_zero_in_different_context(self) -> None:
    self.assertEqual(self.pm.match(Add(Const(0), Add(Const(3), Const(4)))), Add(Const(3), Const(4)))

  def test_variable_addition_with_zero(self) -> None:
    self.assertEqual(self.pm.match(Add(Var('x'), Const(0))), Var('x'))
    
  def test_variable_addition_with_zero_reversed(self) -> None:
    self.assertEqual(self.pm.match(Add(Const(0), Var('y'))), Var('y'))

  def test_nested_negations_with_variables(self) -> None:
    self.assertEqual(self.pm.match(Neg(Neg(Var('z')))), Var('z'))

  def test_negation_of_zero_with_variable(self) -> None:
    self.assertEqual(self.pm.match(Neg(Add(Var('x'), Const(0)))), Neg(Var('x')))

  def test_variable_multiplication_by_one(self) -> None:
    self.assertEqual(self.pm.match(Mul(Var('a'), Const(1))), Var('a'))

  def test_variable_multiplication_by_one_reversed(self) -> None:
    self.assertEqual(self.pm.match(Mul(Const(1), Var('b'))), Var('b'))

  def test_variable_multiplication_by_zero(self) -> None:
    self.assertEqual(self.pm.match(Mul(Var('c'), Const(0))), Const(0))

  def test_variable_multiplication_by_zero_reversed(self) -> None:
    self.assertEqual(self.pm.match(Mul(Const(0), Var('d'))), Const(0))

  def test_exponentiation_with_variables(self) -> None:
    self.assertEqual(self.pm.match(Pow(Var('x'), Const(0))), Const(1))

  def test_exponentiation_of_zero_with_variable(self) -> None:
    self.assertEqual(self.pm.match(Pow(Const(0), Var('y'))), Const(0))

  def test_inverse_multiplication_with_variables(self) -> None:
    self.assertEqual(self.pm.match(Mul(Var('x'), Pow(Var('x'), Neg(Const(1))))), Const(1))

  def test_complex_expression_simplification(self) -> None:
    self.assertEqual(self.pm.match(Add(Mul(Var('a'), Const(1)), Const(0))), Var('a'))

  def test_nested_additions_with_variables(self) -> None:
    self.assertEqual(self.pm.match(Add(Add(Var('x'), Var('y')), Const(0))), Add(Var('x'), Var('y')))

  def test_combining_multiplication_and_addition(self) -> None:
    self.assertEqual(self.pm.match(Add(Mul(Var('a'), Const(0)), Var('b'))), Var('b'))

  def test_expression_with_multiple_variables(self) -> None:
    self.assertEqual(self.pm.match(Add(Mul(Var('x'), Var('y')), Add(Const(0), Var('z')))), Add(Mul(Var('x'), Var('y')), Var('z')))

  def test_pattern_x_plus_yx(self) -> None:
    # Test: x + 3x = (3 + 1)x = 4x
    self.assertEqual(self.pm.match(Add(Var('x'), Mul(Const(3), Var('x')))), Mul(Const(4), Var('x')))
  
  def test_pattern_x_plus_xy(self) -> None:
    # Test: x + x3 = (3 + 1)x = 4x
    self.assertEqual(self.pm.match(Add(Var('x'), Mul(Var('x'), Const(3)))), Mul(Const(4), Var('x')))

  def test_pattern_yx_plus_x(self) -> None:
    # Test: 3x + x = (3 + 1)x = 4x
    self.assertEqual(self.pm.match(Add(Mul(Const(3), Var('x')), Var('x'))), Mul(Const(4), Var('x')))

  def test_pattern_xy_plus_x(self) -> None:
    # Test: x3 + x = (3 + 1)x = 4x
    self.assertEqual(self.pm.match(Add(Mul(Var('x'), Const(3)), Var('x'))), Mul(Const(4), Var('x')))

  def test_pattern_yx_plus_zx(self) -> None:
    # Test: 2x + 3x = (2 + 3)x = 5x
    self.assertEqual(self.pm.match(Add(Mul(Const(2), Var('x')), Mul(Const(3), Var('x')))), Mul(Const(5), Var('x')))

  def test_pattern_xy_plus_zx(self) -> None:
    # Test: x2 + 3x = (2 + 3)x = 5x
    self.assertEqual(self.pm.match(Add(Mul(Var('x'), Const(2)), Mul(Const(3), Var('x')))), Mul(Const(5), Var('x')))

  def test_pattern_yx_plus_xz(self) -> None:
    # Test: 2x + x3 = (2 + 3)x = 5x
    self.assertEqual(self.pm.match(Add(Mul(Const(2), Var('x')), Mul(Var('x'), Const(3)))), Mul(Const(5), Var('x')))

  def test_pattern_xy_plus_xz(self) -> None:
    # Test: x2 + x3 = (2 + 3)x = 5x
    self.assertEqual(self.pm.match(Add(Mul(Var('x'), Const(2)), Mul(Var('x'), Const(3)))), Mul(Const(5), Var('x')))

  def test_exponential_add_with_no_exponent(self) -> None:
    self.assertEqual(self.pm.match(Mul(Var('x'), Pow(Var('x'), Const(3)))), Pow(Var('x'), Const(4)))
    self.assertEqual(self.pm.match(Mul(Pow(Var('x'), Const(3)), Var('x'))), Pow(Var('x'), Const(4)))

  def test_exponential_add(self) -> None:
    self.assertEqual(self.pm.match(Mul(Pow(Var('x'), Const(2)), Pow(Var('x'), Const(3)))), Pow(Var('x'), Add(Const(2), Const(3))))

  def test_exponential_multiply(self) -> None:
    self.assertEqual(self.pm.match(Pow(Pow(Var('x'), Const(2)), Const(3))), Pow(Var('x'), Mul(Const(2), Const(3))))

  def test_is_const_like(self) -> None:
    self.assertTrue(is_const_like(Sub(Mul(Div(Const(2), Const(4)), Const(8)), Neg(Const(3)))))
    self.assertFalse(is_const_like(Sub(Mul(Div(Const(2), Const(4)), Const(8)), Neg(Var('x')))))
    self.assertFalse(is_const_like(Mul(Div(Const(2), Const(4)), Ln(Neg(Pow(Var('x'), Const(3)))))))

  def test_partial_eval(self) -> None:
    self.assertEqual(partial_eval(Sub(Mul(Div(Const(2), Const(4)), Const(8)), Neg(Const(3)))), Const(7))
    self.assertEqual(partial_eval(Sub(Mul(Div(Const(2), Const(4)), Const(8)), Neg(Var('x')))), Add(Const(4), Neg(Neg(Var('x')))))

  def test_complex_nested_expression(self) -> None:
    # (x + 0 + 1) * (0 + y)(1 * z) + x * x^(-1) + -(-0) + -(-x)
    # = ((x * (y * z)) + (1 + x)) = x * y * z + 1 + x
    test_expression = Add(Mul(Mul(Add(Var('x'), Const(0)), Const(1)), Mul(Add(Const(0), Var('y')), Mul(Const(1), Var('z')))), 
                          Add(Mul(Var('x'), Pow(Var('x'), Neg(Const(1)))), Add(Neg(Neg(Const(0))), Neg(Neg(Var('x'))))))
    expected =  Add(Mul(Var('x'), Mul(Var('y'), Var('z'))), Add(Const(1), Var('x')))
    self.assertEqual(self.pm.match(test_expression), expected)

  def test_all_rules_complex_expression(self) -> None:
    # ((x + 0)(y * 1) + (0 + z)(1 * (a + b))) ((c + d^0) * ((e * 1 + (-(-f))) (g * 0))) + (h*h^(-1) + (-(-0)) * (i + j)) 
    # = 1
    test_expression = Add(Mul(Add(Mul(Add(Var('x'), Const(0)), Mul(Var('y'), Const(1))), 
                                  Mul(Add(Const(0), Var('z')), Mul(Const(1), Add(Var('a'), Var('b'))))), 
                                  Mul(Add(Var('c'), Pow(Var('d'), Const(0))), Mul(Add(Mul(Var('e'), Const(1)), Neg(Neg(Var('f')))), Mul(Var('g'), Const(0))))),
                                  Add(Mul(Var('h'), Pow(Var('h'), Neg(Const(1)))), Mul(Neg(Neg(Const(0))), Add(Var('i'), Var('j')))))
    expected =  Const(1)
    self.assertEqual(self.pm.match(test_expression), expected)

  def test_simplify_random_expressions_and_compare_values(self) -> None:
    for _ in range(50):
      expr = generate_random_expression(random.randint(1, 12), exponents=False)
      simplified_expr = self.pm.match(expr)
      self.assertEqual(expr._eval(), simplified_expr._eval())

class TestOpClasses(unittest.TestCase):
  def test_equals_operator(self) -> None:
    add_op_1 = Add(Const(5), Const(10))
    add_op_2 = Add(Const(5), Const(10))
    self.assertEqual(add_op_1, add_op_2)
    add_op_3 = Add(Const(10), Const(5))
    self.assertNotEqual(add_op_1, add_op_3)

  def test_div_operation(self) -> None:
    self.assertEqual(Div(Const(10), Const(2)), Mul(Const(10), Pow(Const(2), Neg(Const(1)))))
    self.assertEqual(Div(Const(10), Const(2))._eval(), 5)

  def test_sub_operation(self) -> None:
    self.assertEqual(Sub(Const(10), Const(2)), Add(Const(10), Neg(Const(2))))
    self.assertEqual(Sub(Const(10), Const(2))._eval(), 8)

  def test_magic_method_add(self) -> None:
    self.assertEqual(Var('x') + 3, Add(Var('x'), Const(3)))
  
  def test_magic_method_sub(self) -> None:
    self.assertEqual(Var('x') - 3, Sub(Var('x'), Const(3)))

  def test_magic_method_mul(self) -> None:
    self.assertEqual(Var('x') * 3, Mul(Var('x'), Const(3)))

  def test_magic_method_div(self) -> None:
    self.assertEqual(Var('x') / 3, Div(Var('x'), Const(3)))

  def test_magic_method_pow(self) -> None:
    self.assertEqual(Var('x') ** 3, Pow(Var('x'), Const(3)))

  def test_magic_method_rsub(self) -> None:
    self.assertEqual(3 - Var('x'), Sub(Const(3), Var('x')))

  def test_magic_method_rdiv(self) -> None:
    self.assertEqual(3 / Var('x'), Div(Const(3), Var('x')))

  def test_magic_method_rpow(self) -> None:
    self.assertEqual(3 ** Var('x'), Pow(Const(3), Var('x')))

  def test_complex_magic_method_expression(self) -> None:
    expr = Var('x') + Const(2) * (Var('y') - 4)
    expected = Add(Var('x'), Mul(Const(2), Sub(Var('y'), Const(4))))
    self.assertEqual(expr, expected)

  def test_nested_magic_method_expression(self) -> None:
    expr = (Var('x') + 1) * (Var('y') - 2)
    expected = Mul(Add(Var('x'), Const(1)), Sub(Var('y'), Const(2)))
    self.assertEqual(expr, expected)

  def test_magic_method_order_of_operations(self) -> None:
    expr = Const(2) + Const(3) * Const(4) - Const(5) / Const(5)
    expected = Sub(Add(Const(2), Mul(Const(3), Const(4))), Div(Const(5), Const(5)))
    self.assertEqual(expr, expected)

  def test_magic_method_multiple_operations(self) -> None:
    expr = (Var('x') ** 2 + Var('y')) * (Var('z') - 3)
    expected = Mul(Add(Pow(Var('x'), Const(2)), Var('y')), Sub(Var('z'), Const(3)))
    self.assertEqual(expr, expected)

  def test_random_expressions_without_exponents_with_rewrite(self) -> None:
    for _ in range(200):
      pc.rewrite = True
      expr = generate_random_expression(random.randint(1, 7), exponents=False)
      self.assertAlmostEqual(eval(repr(expr).replace('^', '**')), expr._eval(), delta=1e-5)

  def test_random_expressions_without_exponents_without_rewrite(self) -> None:
    for _ in range(200):
      pc.rewrite = False
      expr = generate_random_expression(random.randint(1, 7), exponents=False)
      self.assertAlmostEqual(eval(repr(expr).replace('^', '**')), expr._eval(), delta=1e-5)

if __name__ == '__main__':
  unittest.main()