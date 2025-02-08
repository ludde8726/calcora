from __future__ import annotations

from typing import Type
from typing import TYPE_CHECKING

import math
import random
import string
import unittest

from calcora.codegen.lambdify import lambdify, find_expression_vars, string_lambda

from calcora.core.ops import Add, Complex, Const, Cos, Log, Mul, Neg, Pow, Sin, Var
from calcora.core.constants import E, PI, One, Two
from calcora.core.registry import Dispatcher as d
from calcora.core.numeric import Numeric
from calcora.globals import ec

if TYPE_CHECKING:
  from calcora.core.expression import Expr

def generate_random_expression(depth: int, num_vars: int = 0) -> Expr:
  vars = string.ascii_lowercase[:num_vars]
  if depth == 1: return Const(Numeric(random.uniform(1, 7)))
  else:
    operation : Type[Expr] = random.choice([Add, Mul, Neg]) if not num_vars else random.choice([Add, Mul, Neg, Var])
    left_expr = generate_random_expression(depth - 1, num_vars)
    if operation is Add or operation is Mul:
      right_expr = generate_random_expression(depth - 1, num_vars)
      return operation(left_expr, right_expr)
    elif operation is Var:
      return Var(vars[random.randint(0,num_vars-1)])
    else: return Neg(left_expr)

class TestLambdify(unittest.TestCase):
  def test_lambdify_python_add(self) -> None:
    self.assertEqual(string_lambda(Add(One, Two), backend='python'), 'lambda: (float(1.0)+float(2.0))')
    self.assertEqual(string_lambda(Add(Var('x'), Var('y')), backend='python'), 'lambda x,y: (x+y)')
    self.assertEqual(lambdify(Add(Var('x'), Var('y')), backend='python')(1, 2), 3)

  def test_lambdify_mpmath_add(self) -> None:
    self.assertEqual(string_lambda(Add(One, Two), backend='mpmath'), 'lambda: (mpmath.mpf(1.0)+mpmath.mpf(2.0))')
    self.assertEqual(string_lambda(Add(Var('x'), Var('y')), backend='mpmath'), 'lambda x,y: (x+y)')
    self.assertEqual(lambdify(Add(Var('x'), Var('y')), backend='mpmath')(1, 2), 3)

  def test_lambdify_numpy_add(self) -> None:
    self.assertEqual(string_lambda(Add(One, Two), backend='numpy'), 'lambda: (numpy.float64(1.0)+numpy.float64(2.0))')
    self.assertEqual(string_lambda(Add(Var('x'), Var('y')), backend='numpy'), 'lambda x,y: (x+y)')
    self.assertEqual(lambdify(Add(Var('x'), Var('y')), backend='numpy')(1, 2), 3)

  def test_lambdify_python_mul(self) -> None:
    self.assertEqual(string_lambda(Mul(One, Two), backend='python'), 'lambda: (float(1.0)*float(2.0))')
    self.assertEqual(string_lambda(Mul(Var('x'), Var('y')), backend='python'), 'lambda x,y: (x*y)')
    self.assertEqual(lambdify(Mul(Var('x'), Var('y')), backend='python')(1, 2), 2)

  def test_lambdify_mpmath_mul(self) -> None:
    self.assertEqual(string_lambda(Mul(One, Two), backend='mpmath'), 'lambda: (mpmath.mpf(1.0)*mpmath.mpf(2.0))')
    self.assertEqual(string_lambda(Mul(Var('x'), Var('y')), backend='mpmath'), 'lambda x,y: (x*y)')
    self.assertEqual(lambdify(Mul(Var('x'), Var('y')), backend='mpmath')(1, 2), 2)

  def test_lambdify_numpy_mul(self) -> None:
    self.assertEqual(string_lambda(Mul(One, Two), backend='numpy'), 'lambda: (numpy.float64(1.0)*numpy.float64(2.0))')
    self.assertEqual(string_lambda(Mul(Var('x'), Var('y')), backend='numpy'), 'lambda x,y: (x*y)')
    self.assertEqual(lambdify(Mul(Var('x'), Var('y')), backend='numpy')(1, 2), 2)

  def test_lambdify_python_neg(self) -> None:
    self.assertEqual(string_lambda(Neg(Two), backend='python'), 'lambda: (-float(2.0))')
    self.assertEqual(string_lambda(Neg(Var('x')), backend='python'), 'lambda x: (-x)')
    self.assertEqual(lambdify(Neg(Var('x')), backend='python')(2), -2)

  def test_lambdify_mpmath_neg(self) -> None:
    self.assertEqual(string_lambda(Neg(Two), backend='mpmath'), 'lambda: (-mpmath.mpf(2.0))')
    self.assertEqual(string_lambda(Neg(Var('x')), backend='mpmath'), 'lambda x: (-x)')
    self.assertEqual(lambdify(Neg(Var('x')), backend='mpmath')(2), -2)

  def test_lambdify_numpy_neg(self) -> None:
    self.assertEqual(string_lambda(Neg(Two), backend='numpy'), 'lambda: (-numpy.float64(2.0))')
    self.assertEqual(string_lambda(Neg(Var('x')), backend='numpy'), 'lambda x: (-x)')
    self.assertEqual(lambdify(Neg(Var('x')), backend='numpy')(2), -2)

  def test_lambdify_python_pow(self) -> None:
    self.assertEqual(string_lambda(Pow(One, Two), backend='python'), 'lambda: (float(1.0)**float(2.0))')
    self.assertEqual(string_lambda(Pow(Var('x'), Var('y')), backend='python'), 'lambda x,y: (x**y)')
    self.assertEqual(lambdify(Pow(Var('x'), Var('y')), backend='python')(1, 2), 1)

  def test_lambdify_mpmath_pow(self) -> None:
    self.assertEqual(string_lambda(Pow(One, Two), backend='mpmath'), 'lambda: (mpmath.mpf(1.0)**mpmath.mpf(2.0))')
    self.assertEqual(string_lambda(Pow(Var('x'), Var('y')), backend='mpmath'), 'lambda x,y: (x**y)')
    self.assertEqual(lambdify(Pow(Var('x'), Var('y')), backend='mpmath')(1, 2), 1)

  def test_lambdify_numpy_pow(self) -> None:
    self.assertEqual(string_lambda(Pow(One, Two), backend='numpy'), 'lambda: (numpy.float64(1.0)**numpy.float64(2.0))')
    self.assertEqual(string_lambda(Pow(Var('x'), Var('y')), backend='numpy'), 'lambda x,y: (x**y)')
    self.assertEqual(lambdify(Pow(Var('x'), Var('y')), backend='numpy')(1, 2), 1)

  def test_lambdify_python_log(self) -> None:
    self.assertEqual(string_lambda(Log(E**4, E), backend='python'), 'lambda: math.log((math.e**float(4.0)), math.e)')
    self.assertEqual(string_lambda(Log(Var('x'), Var('y')), backend='python'), 'lambda x,y: math.log(x, y)')
    self.assertEqual(lambdify(Log(Var('x'), Var('y')), backend='python')(math.e**4, math.e), 4)

  def test_lambdify_mpmath_log(self) -> None:
    self.assertEqual(string_lambda(Log(E**4, E), backend='mpmath'), 'lambda: mpmath.log((mpmath.e**mpmath.mpf(4.0)), mpmath.e)')
    self.assertEqual(string_lambda(Log(Var('x'), Var('y')), backend='mpmath'), 'lambda x,y: mpmath.log(x, y)')
    self.assertEqual(lambdify(Log(Var('x'), Var('y')), backend='mpmath')(math.e**4, math.e), 4)

  def test_lambdify_numpy_log(self) -> None:
    self.assertEqual(string_lambda(Log(E**4, E), backend='numpy'), 'lambda: numpy.emath.logn(numpy.e, (numpy.e**numpy.float64(4.0)))')
    self.assertEqual(string_lambda(Log(Var('x'), Var('y')), backend='numpy'), 'lambda x,y: numpy.emath.logn(y, x)')
    self.assertEqual(lambdify(Log(Var('x'), Var('y')), backend='numpy')(math.e**4, math.e), 4)

  def test_lambdify_python_complex(self) -> None:
    self.assertEqual(string_lambda(Complex(One, Two), backend='python'), 'lambda: complex(float(1.0), float(2.0))')
    self.assertEqual(string_lambda(Complex(Var('x'), Var('y')), backend='python'), 'lambda x,y: complex(x, y)')
    self.assertEqual(lambdify(Complex(Var('x'), Var('y')), backend='python')(1, 2), complex(1, 2))

  def test_lambdify_mpmath_complex(self) -> None:
    self.assertEqual(string_lambda(Complex(One, Two), backend='mpmath'), 'lambda: mpmath.mpc(mpmath.mpf(1.0), mpmath.mpf(2.0))')
    self.assertEqual(string_lambda(Complex(Var('x'), Var('y')), backend='mpmath'), 'lambda x,y: mpmath.mpc(x, y)')
    self.assertEqual(lambdify(Complex(Var('x'), Var('y')), backend='mpmath')(1, 2), complex(1, 2)) 

  def test_lambdify_numpy_complex(self) -> None:
    self.assertEqual(string_lambda(Complex(One, Two), backend='numpy'), 'lambda: numpy.complex128(numpy.float64(1.0), numpy.float64(2.0))')
    self.assertEqual(string_lambda(Complex(Var('x'), Var('y')), backend='numpy'), 'lambda x,y: numpy.complex128(x, y)')
    self.assertEqual(lambdify(Complex(Var('x'), Var('y')), backend='numpy')(1, 2), complex(1, 2)) 
  
  def test_lambdify_python_sin(self) -> None:
    self.assertEqual(string_lambda(Sin(PI), backend='python'), 'lambda: math.sin(math.pi)')
    self.assertEqual(string_lambda(Sin(Var('x')), backend='python'), 'lambda x: math.sin(x)')
    self.assertAlmostEqual(lambdify(Sin(Var('x')), backend='python')(math.pi), 0, delta=1e-15) # Apparently sin(pi) is not 0 but 1e-16...

  def test_lambdify_mpmath_sin(self) -> None:
    self.assertEqual(string_lambda(Sin(PI), backend='mpmath'), 'lambda: mpmath.sin(mpmath.pi)')
    self.assertEqual(string_lambda(Sin(Var('x')), backend='mpmath'), 'lambda x: mpmath.sin(x)')
    self.assertAlmostEqual(lambdify(Sin(Var('x')), backend='mpmath')(math.pi), 0, delta=1e-15) # Apparently sin(pi) is not 0 but 1e-16...

  def test_lambdify_numpy_sin(self) -> None:
    self.assertEqual(string_lambda(Sin(PI), backend='numpy'), 'lambda: numpy.sin(numpy.pi)')
    self.assertEqual(string_lambda(Sin(Var('x')), backend='numpy'), 'lambda x: numpy.sin(x)')
    self.assertAlmostEqual(lambdify(Sin(Var('x')), backend='numpy')(math.pi), 0, delta=1e-15) # Apparently sin(pi) is not 0 but 1e-16...

  def test_lambdify_python(self) -> None:
    self.assertEqual(string_lambda(Cos(PI), backend='python'), 'lambda: math.cos(math.pi)')
    self.assertEqual(string_lambda(Cos(Var('x')), backend='python'), 'lambda x: math.cos(x)')
    self.assertAlmostEqual(lambdify(Cos(Var('x')), backend='python')(math.pi), -1) # But cos(pi) is of course exactly -1

  def test_lambdify_mpmath(self) -> None:
    self.assertEqual(string_lambda(Cos(PI), backend='mpmath'), 'lambda: mpmath.cos(mpmath.pi)')
    self.assertEqual(string_lambda(Cos(Var('x')), backend='mpmath'), 'lambda x: mpmath.cos(x)')
    self.assertAlmostEqual(lambdify(Cos(Var('x')), backend='mpmath')(math.pi), -1) # But cos(pi) is of course exactly -1

  def test_lambdify_numpy(self) -> None:
    self.assertEqual(string_lambda(Cos(PI), backend='numpy'), 'lambda: numpy.cos(numpy.pi)')
    self.assertEqual(string_lambda(Cos(Var('x')), backend='numpy'), 'lambda x: numpy.cos(x)')
    self.assertAlmostEqual(float(lambdify(Cos(Var('x')), backend='numpy')(math.pi)), -1) # But cos(pi) is of course exactly -1

  def test_lambdify_python_random(self) -> None:
    for _ in range(1000):
      num_vars = random.randint(1, 3)
      expr = generate_random_expression(random.randint(1, 5), num_vars)
      lambda_expr = lambdify(expr, "python")
      args = {name:random.uniform(0, 100) for name in find_expression_vars(expr)}
      self.assertAlmostEqual(float(expr.evalf(**{k:d.typecast(v) for k,v in args.items()})), lambda_expr(**args), delta=1e-3)
  
  def test_lambdify_mpmath_random(self) -> None:
    ec.precision = 100
    for _ in range(1000):
      num_vars = random.randint(1, 3)
      expr = generate_random_expression(random.randint(1, 5), num_vars)
      lambda_expr = lambdify(expr, "mpmath")
      args = {name:random.uniform(0, 100) for name in find_expression_vars(expr)}
      self.assertAlmostEqual(expr._eval(**{k:d.typecast(v) for k,v in args.items()}), lambda_expr(**args), delta=1e-7)
    ec.precision = 16

  def test_lambdify_numpy_random(self) -> None:
    import numpy as np
    for _ in range(1000):
      num_vars = random.randint(1, 3)
      expr = generate_random_expression(random.randint(1, 5), num_vars)
      lambda_expr = lambdify(expr, "numpy")
      args = {name:np.float64(random.uniform(0, 100)) for name in find_expression_vars(expr)}
      self.assertAlmostEqual(np.float64(float(expr.evalf(**{k:d.typecast(v) for k,v in args.items()}))), 
                       lambda_expr(**args), delta=1e-7)

if __name__ == '__main__':
  unittest.main()