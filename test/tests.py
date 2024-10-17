from ops import Op, Const, Add, Div, Exp, Mul, Neg, Sub, Var
from match import AnyConstLike, AnyOp, MatchedSymbol, Pattern, PatternMatcher, SymbolicPatternMatcher

import random
import unittest

def generate_random_expression(depth: int, exponents: bool = False) -> Op:
  if depth == 1:
    return Const(random.uniform(1, 10))
  else:
    operations = [Add, Sub, Mul, Div, Neg]
    if exponents: operations.append(Exp)
    operation = random.choice(operations)
    if operation in [Add, Sub, Mul, Div]:
      left_expr = generate_random_expression(depth - 1, exponents=exponents)
      right_expr = generate_random_expression(depth - 1, exponents=exponents)
      return operation(left_expr, right_expr)
    elif operation == Exp:
      base = generate_random_expression(depth - 1, exponents=exponents)
      exponent = Const(random.randint(1, 10))
      return Exp(base, exponent)
    else:
      expr = generate_random_expression(depth - 1, exponents=exponents)
      return Neg(expr)

class TestPatternMatcher(unittest.TestCase):
  def setUp(self):
    self.pm = SymbolicPatternMatcher

  def test_addition_with_zero(self):
    self.assertEqual(self.pm.match(Add(Const(5), Const(0))), Const(5))
      
  def test_addition_with_zero_reversed(self):
    self.assertEqual(self.pm.match(Add(Const(0), Const(5))), Const(5))

  def test_negation_of_negation(self):
    self.assertEqual(self.pm.match(Neg(Neg(Const(3)))), Const(3))

  def test_negation_of_zero(self):
    self.assertEqual(self.pm.match(Neg(Const(0))), Const(0))

  def test_multiplication_by_one(self):
    self.assertEqual(self.pm.match(Mul(Const(1), Const(10))), Const(10))

  def test_multiplication_by_one_reversed(self):
    self.assertEqual(self.pm.match(Mul(Const(10), Const(1))), Const(10))

  def test_multiplication_by_zero(self):
    self.assertEqual(self.pm.match(Mul(Const(5), Const(0))), Const(0))

  def test_multiplication_by_zero_reversed(self):
    self.assertEqual(self.pm.match(Mul(Const(0), Const(5))), Const(0))

  def test_exponentiation_to_zero(self):
    self.assertEqual(self.pm.match(Exp(Const(2), Const(0))), Const(1))

  def test_exponentiation_of_zero(self):
    self.assertEqual(self.pm.match(Exp(Const(0), Const(3))), Const(0))

  def test_inverse_multiplication(self):
    self.assertEqual(self.pm.match(Mul(Const(2), Exp(Const(2), Neg(Const(1))))), Const(1))

  def test_constant_zero_in_different_context(self):
    self.assertEqual(self.pm.match(Add(Const(0), Add(Const(3), Const(4)))), Add(Const(3), Const(4)))

  def test_variable_addition_with_zero(self):
    self.assertEqual(self.pm.match(Add(Var('x'), Const(0))), Var('x'))
    
  def test_variable_addition_with_zero_reversed(self):
    self.assertEqual(self.pm.match(Add(Const(0), Var('y'))), Var('y'))

  def test_nested_negations_with_variables(self):
    self.assertEqual(self.pm.match(Neg(Neg(Var('z')))), Var('z'))

  def test_negation_of_zero_with_variable(self):
    self.assertEqual(self.pm.match(Neg(Add(Var('x'), Const(0)))), Neg(Var('x')))

  def test_variable_multiplication_by_one(self):
    self.assertEqual(self.pm.match(Mul(Var('a'), Const(1))), Var('a'))

  def test_variable_multiplication_by_one_reversed(self):
    self.assertEqual(self.pm.match(Mul(Const(1), Var('b'))), Var('b'))

  def test_variable_multiplication_by_zero(self):
    self.assertEqual(self.pm.match(Mul(Var('c'), Const(0))), Const(0))

  def test_variable_multiplication_by_zero_reversed(self):
    self.assertEqual(self.pm.match(Mul(Const(0), Var('d'))), Const(0))

  def test_exponentiation_with_variables(self):
    self.assertEqual(self.pm.match(Exp(Var('x'), Const(0))), Const(1))

  def test_exponentiation_of_zero_with_variable(self):
    self.assertEqual(self.pm.match(Exp(Const(0), Var('y'))), Const(0))

  def test_inverse_multiplication_with_variables(self):
    self.assertEqual(self.pm.match(Mul(Var('x'), Exp(Var('x'), Neg(Const(1))))), Const(1))

  def test_complex_expression_simplification(self):
    self.assertEqual(self.pm.match(Add(Mul(Var('a'), Const(1)), Const(0))), Var('a'))

  def test_nested_additions_with_variables(self):
    self.assertEqual(self.pm.match(Add(Add(Var('x'), Var('y')), Const(0))), Add(Var('x'), Var('y')))

  def test_combining_multiplication_and_addition(self):
    self.assertEqual(self.pm.match(Add(Mul(Var('a'), Const(0)), Var('b'))), Var('b'))

  def test_expression_with_multiple_variables(self):
    self.assertEqual(self.pm.match(Add(Mul(Var('x'), Var('y')), Add(Const(0), Var('z')))), Add(Mul(Var('x'), Var('y')), Var('z')))

  def test_pattern_x_plus_yx(self):
    # Test: x + 3x = (3 + 1)x = 4x
    self.assertEqual(self.pm.match(Add(Var('x'), Mul(Const(3), Var('x')))), Mul(Const(4), Var('x')))
  
  def test_pattern_x_plus_xy(self):
    # Test: x + x3 = (3 + 1)x = 4x
    self.assertEqual(self.pm.match(Add(Var('x'), Mul(Var('x'), Const(3)))), Mul(Const(4), Var('x')))

  def test_pattern_yx_plus_x(self):
    # Test: 3x + x = (3 + 1)x = 4x
    self.assertEqual(self.pm.match(Add(Mul(Const(3), Var('x')), Var('x'))), Mul(Const(4), Var('x')))

  def test_pattern_xy_plus_x(self):
    # Test: x3 + x = (3 + 1)x = 4x
    self.assertEqual(self.pm.match(Add(Mul(Var('x'), Const(3)), Var('x'))), Mul(Const(4), Var('x')))

  def test_pattern_yx_plus_zx(self):
    # Test: 2x + 3x = (2 + 3)x = 5x
    self.assertEqual(self.pm.match(Add(Mul(Const(2), Var('x')), Mul(Const(3), Var('x')))), Mul(Const(5), Var('x')))

  def test_pattern_xy_plus_zx(self):
    # Test: x2 + 3x = (2 + 3)x = 5x
    self.assertEqual(self.pm.match(Add(Mul(Var('x'), Const(2)), Mul(Const(3), Var('x')))), Mul(Const(5), Var('x')))

  def test_pattern_yx_plus_xz(self):
    # Test: 2x + x3 = (2 + 3)x = 5x
    self.assertEqual(self.pm.match(Add(Mul(Const(2), Var('x')), Mul(Var('x'), Const(3)))), Mul(Const(5), Var('x')))

  def test_pattern_xy_plus_xz(self):
    # Test: x2 + x3 = (2 + 3)x = 5x
    self.assertEqual(self.pm.match(Add(Mul(Var('x'), Const(2)), Mul(Var('x'), Const(3)))), Mul(Const(5), Var('x')))

  def test_complex_nested_expression(self):
    # (x + 0 + 1) * (0 + y)(1 * z) + x * x^(-1) + -(-0) + -(-x)
    # = ((x * (y * z)) + (1 + x)) = x * y * z + 1 + x
    test_expression = Add(Mul(Mul(Add(Var('x'), Const(0)), Const(1)), Mul(Add(Const(0), Var('y')), Mul(Const(1), Var('z')))), 
                          Add(Mul(Var('x'), Exp(Var('x'), Neg(Const(1)))), Add(Neg(Neg(Const(0))), Neg(Neg(Var('x'))))))
    expected =  Add(Mul(Var('x'), Mul(Var('y'), Var('z'))), Add(Const(1), Var('x')))
    self.assertEqual(self.pm.match(test_expression), expected)

  def test_all_rules_complex_expression(self):
    # ((x + 0)(y * 1) + (0 + z)(1 * (a + b))) ((c + d^0) * ((e * 1 + (-(-f))) (g * 0))) + (h*h^(-1) + (-(-0)) * (i + j)) 
    # = 1
    test_expression = Add(Mul(Add(Mul(Add(Var('x'), Const(0)), Mul(Var('y'), Const(1))), 
                                  Mul(Add(Const(0), Var('z')), Mul(Const(1), Add(Var('a'), Var('b'))))), 
                                  Mul(Add(Var('c'), Exp(Var('d'), Const(0))), Mul(Add(Mul(Var('e'), Const(1)), Neg(Neg(Var('f')))), Mul(Var('g'), Const(0))))),
                                  Add(Mul(Var('h'), Exp(Var('h'), Neg(Const(1)))), Mul(Neg(Neg(Const(0))), Add(Var('i'), Var('j')))))
    expected =  Const(1)
    self.assertEqual(self.pm.match(test_expression), expected)

  def test_simplify_random_expressions(self):
    for _ in range(50):
      expr = generate_random_expression(random.randint(1, 12), exponents=True)
      self.pm.match(expr)

class TestOpClasses(unittest.TestCase):
  def test_const_init(self):
    with self.assertRaises(AssertionError):
      Const(-5)
  
  def test_equals_operatoe(self):
    add_op_1 = Add(Const(5), Const(10))
    add_op_2 = Add(Const(5), Const(10))
    self.assertEqual(add_op_1, add_op_2)
    add_op_3 = Add(Const(10), Const(5))
    self.assertNotEqual(add_op_1, add_op_3)

  def test_div_operation(self):
    self.assertEqual(Div(Const(10), Const(2)), Mul(Const(10), Exp(Const(2), Neg(Const(1)))))
    self.assertEqual(Div(Const(10), Const(2)).eval(), 5)

  def test_sub_operation(self):
    self.assertEqual(Sub(Const(10), Const(2)), Add(Const(10), Neg(Const(2))))
    self.assertEqual(Sub(Const(10), Const(2)).eval(), 8)

  def test_random_expressions_without_exponents(self):
    for _ in range(200):
      expr = generate_random_expression(random.randint(1, 12), exponents=False)
      self.assertEqual(eval(repr(expr).replace('^', '**')), expr.eval())

  def test_random_expressions_with_exponents(self):
    for _ in range(200):
      expr = generate_random_expression(random.randint(1, 3), exponents=True)
      self.assertEqual(eval(repr(expr).replace('^', '**')), expr.eval())

if __name__ == '__main__':
  unittest.main()