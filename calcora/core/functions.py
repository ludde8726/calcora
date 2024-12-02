from __future__ import annotations

from typing import TYPE_CHECKING

from calcora.core.number import Number
from calcora.core.constants import PI, I
from calcora.core.ops import Complex, Const, Neg, Sin, Cos
from calcora.types import RealNumberLike
from calcora.utils import colored

from mpmath import fabs, fac, gamma
from mpmath import arg as argument

if TYPE_CHECKING:
  from calcora.core.expression import Expr

def abs(expression: Expr) -> Expr: return Number(fabs(expression._eval()))
def round(expression: Expr) -> Expr: raise NotImplementedError()
def ceil(expression: Expr) -> Expr: raise NotImplementedError()
def floor(expression: Expr) -> Expr: raise NotImplementedError()

def arg(expression: Expr) -> Expr: return Number(argument(expression._eval()))
def conj(expression: Expr) -> Expr:
  n = expression.eval()
  if isinstance(n, Complex): return Complex(n.real, Neg(n.imag))
  else: return n
def polar(expression: Expr) -> Expr:
  print(colored('Warning! Polar form of complex numbers cannot be converted back to real numbers.', 'bright_yellow'))
  r = abs(expression)
  argv = arg(expression)
  return r * (Cos(argv) + I * Sin(argv))

def rad(degrees: RealNumberLike, eval: bool = True): 
  if eval: return ((Number(degrees) * PI) / 180).eval()
  else: return (Number(degrees) * PI) / 180
def deg(radians: RealNumberLike, eval: bool = True): 
  if eval: return ((Number(radians) * 180) / PI).eval()
  else: return (Number(radians) * 180) / PI

def factorial(x: RealNumberLike) -> Expr:
  value = Number(x)
  value = value._eval()
  if value % 1 != 0: raise ValueError('Cannot calculate factorial of a non integer!')
  return Number(fac(value))

def gamma(x: RealNumberLike):
  return Number(fac((Number(x) - 1)._eval()))