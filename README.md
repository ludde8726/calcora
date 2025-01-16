# Calcora

Calcora is a basic math framework that i am writing in my free time. Right now it is very basic but i will keep working on improving it.

## Features

Right now Calcora supports a few basic features but i will keep adding to it overtime:

### Ops
- Const
- Var
- Complex
- Constant
- Add
- Neg
- Mul
- Pow
- Log
- Sin
- Cos
---
- Sub
- Div
- Ln

These are the operations that calcora currently supports, however Sub, Div and Ln are only wrappers around other ops for utility reasons. Sub is just an Add combined with a Neg such that `Sub(x, y) = Add(x, Neg(y))` and Div is a Mul and an Pow combined such that `Div(x, y) = Mul(x, Pow(y, Neg(Const(1))))`. Ln is simply a wrapper over Log such that `Ln(x) = Log(x, Const(e))` where e is Eulers number.

Note that i wrote `Neg(Const(1))` inside of the `Pow` insted of simply -1, this is because all ops except for `Const` only accept other Ops as parameters. You could write `Pow(y, -1)` however this would automatically get converted to `Pow(y, Neg(Const(1))))`. All ops allow you to create them with any of the following types: types: int, float, complex, string, Expr or Numeric. `Expr` is the parent class of all ops and `Numeric` is calcoras own number type which i will explain further later on. These will however always get converted to a valid representation of `Expr` classes

The `Op` parent class also implements the python operations that Calcora supports. This means that writing `Add(Const(1), Const(2))` is the same as `Const(1) + Const(2)`. Note however that at least one of the arguments must be a Calcora op.

Some of the ops in the list above behave differently from all other ops. Constant is a lazy wrapper around different constants such as pi, e, etc. The reason they have to be separate class and not just a `Const` of ex. `math.pi` is to allow evaluation of expressions with constants to a specific precision. What that means i will explain deeper later on.

### Variables
As shown in the list of ops that calcora supports variables are an option. These are a special kind of operation that takes in a string as an argument. The variable name is simply a way to identify different variables.

Creating a variable is as simple as
```
>>> from calcora.core.ops import Var
>>> x = Var('x')
>>> x.args
('x',)
```

Note: All op subclasses have a member variable `args` that returns all the arguments the op was created with.

### Evaluation
All ops have a built in eval method that evaluates the op. For Add, as an example, this means simply adding together the evaluated arguments. The eval method takes in an unspecified amout of keyword arguments, these are for any variables in the expression. Calling eval on an expression with the argument `x = Const(3)` will set the value of every variable with the name `x` in the expression to three and then evaluate. Not specifying a value for any variables in the expression will raise a ValueError. The keyword arguments can be any of the following types: int, float, complex, string, Expr or Numeric. Expr is the parent class of all ops and Numeric is calcoras own number type which i will explain further later on. 
```
>>> from calcora.ops import Var
>>> x = Var('x')
>>> expression = x / 2 + 4
>>> expression.eval(x = Const(4))
6.0
>>> expression.eval()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  ...
ValueError: Specified value for type var is required for evaluation, no value for var with name 'x'

```

### Differentiation
All ops have a built in differentiate method that returns the derivative of said class (all ops are implemented as subclasses of a main `Expr` class). Differentiating an expression is a simple as calling `expression.differentiate(var)` where var is the variable you are differentiating based of. However it is always recommended using `calcora.core.differentiate.diff` instead as it has the option to specify the degree of the derivative and has built in simplification.

```
>>> from calcora.core.ops import Var
>>> x = Var('x')
>>> expression = 2*x + 3
>>> expression.differentiate(x)
0.0*x + 2.0*1.0 + 0.0
```


Note how the derivate is proboably not what you expected, the result should have been `2` right? If you look closely this expression does indeed simplify to two. The reason the result becomes longer and more complicated than it has to be is because we need to cover all possibilies. When the derivative of this operation is calculated, what happens is the outermost operation is evaluated, in this example this is the `Add`. This derivative then returns the derivative of both the arguments separately, this is implmented as:
```
def differentiate(self, var: Var) -> Op:
    return Add(self.x.differentiate(var), self.y.differentiate(var))
```
This then calls the Mul derivative aswell as the Const derivative which are implemented as:
```
# Mul
def differentiate(self, var: Var) -> Op:
    return Add(Mul(self.x.differentiate(var), self.y), Mul(self.x, self.y.differentiate(var)))

# Const
def differentiate(self, var: Var) -> Op: 
    return Const(0)
```

This pattern continues and hopefully you get the point now. The reason for the complex multiplication derivative is to cover the possibilty that both arguments of the operation can have variables in them.

Trying something like `x**2` will result in an even more complicated expression that also simplifies to the correct result `2*x`

```
>>> from calcora.core.ops import Var
>>> x = Var('x')
>>> expression = x ** 2
>>> expression.differentiate(x)
x^2.0*(2.0*1.0/x + 0.0*ln(x))
```

Trying the diff function looks something like this

```
>>> from calcora.core.ops import Var
>>> x = Var('x')
>>> expression = 2**x
>>> diff(expression, x, 4)
2.0^x*ln(2.0)*ln(2.0)*ln(2.0)*ln(2.0)
```

### Pattern matcher
Inside match.py and pattern.py there are two classes, `Pattern` and `PatternMatcher`. These contain the core engine in how calcora handles simplification of expressions. The `Pattern` class does most of the heavy lifting while `PatternMatcher` works like a wrapper around it to allow for more patterns at once. The `Pattern` class takes in a pattern of type `Expr` and a replacement callable that returns an `Expr`. The pattern then has a match function which by checking the pattern against an expression finds and replaces parts of the original expression. I won't go into depth how this works exacly but basically it recusively checks all the pattern arguments and the expression arguments until it finds a match. The `PatternMatcher` class takes in an iterable of patterns and saves them in a list. When called using the match method on an expression it continuously loops through the patterns until the expression is no longer simplified by any of the patterns. Inside match.py there is also a `SymbolicPatternMatcher`, which is an instance of the `PatternMatcher` class that has some basic simplification rules. For example there are rules basic for multiplication and addition of zero where `x + 0` becomes `x` and where`x * 0` becomes `0`. In this example `x` stands for any type of operation. There are also more complex patterns in the `SymbolicPatternMatcher`, for example.
`yx + zx = (y+z)x` and `x^y * x^z = x^(y+z)`, the way these are implmented is quite complicated but i can show you the first two rules:
```
Pattern(Add(AnyOp(), Const(0)), lambda x: x), # x + 0 = x
Pattern(Mul(AnyOp(), Const(0)), lambda x: Const(0)), # x * 0 = 0
```
If you want to see how the other rules are implemented you can look inside of match.py. Running the `SymbolicPatternMatcher` on the first two derivatives I showed would look like:
```
>>> from calcora.ops import Var
>>> from calcora.match import SymbolicPatternMatcher
>>> x = Var('x')
>>> expression = 2*x + 3
>>> dx = expression.differentiate(x)
>>> dx
0.0*x + 2.0*1.0 + 0.0
>>> SymbolicPatternMatcher.match(dx)
2
>>> 
```

```
>>> from calcora.ops import Var
>>> from calcora.match import SymbolicPatternMatcher
>>> x = Var('x')
>>> expression = x ** 2
>>> dx = expression.differentiate(x)
>>> dx
x^2.0*(2.0*1.0/x + 0.0*ln(x))
>>> SymbolicPatternMatcher.match(dx)
x^2.0*2.0/x
```

Notice how the result from the last expression still is not completely simplified as much as possible. As of right now however this is the closest we will get.

### Numeric
The `Numeric` class is basically calcoras own wrapper around an mpmath `mpc`. When you call `.evalf` on an expression the result may look like any other float or complex but in reality it's just an instance of the `Numeric` class. The Numeric class is a bit unlike the `Const` and complex in the sence that it works like any other number in python, all operations are evaluated instantly. The difference however is that a `Numeric` supports operations with arbitrary precision. You can set the precision and calculate expressions to any precision you want.

```
>>> from calcora.core.numeric import Numeric
>>> from calcora.globals import ec
>>> ec.precision = 50
>>> a = Numeric(1)
>>> b = Numeric('3+3i')
>>> print(a / b)
0.16666666666666666666666666666666666666666666666667 - 0.16666666666666666666666666666666666666666666666667i
```
Numerics can be created from the same types that the op classes themselves accept (except for Expr). Warning: The precision is not stable at all, sometimes it works great sometimes not. It is a work in progress :)

### Printing
Inside of calcora.printing.printing there is a class `Printer`. This class is responsible for dispatching the `__repr__` function of the `Expr` class to the correct printing method. Calcora supports class based printing, latex printing and regular printing which we have used up until now. The printer can also print rewritten and simplified versions of the expression what this means we will dive deaper into soon. Selecting the print type can be done in the following way.

```
>>> from calcora.core.ops import Var
>>> from calcora.globals import pc, PrintOptions
>>> expression = (x + x**x)/'2+4i'
>>> pc.print_type = PrintOptions.Regular
>>> expression
(x + x^x)/(2.0 + 4.0i)
>>> pc.print_type = PrintOptions.Class
>>> expression
Div(Add(Var(x), Pow(Var(x), Var(x))), Complex(Const(2.0), Const(4.0)))
>>> pc.print_type = PrintOptions.Latex
>>> expression
\frac{x + {x}^{x}}{2.0 + 4.0i}
```

You can see the how the different options change the output of expressions `__repr__` function. 

Remember how i told you how that some of the ops are wrappers around other ops? The reason we still see division as x/y and not x*y^(-1) is because of the rewrite option i told you about earlier. The printer has its own special PatternMatcher that finds all instances of x*y^(-1), x + (-y), log_e(x), etc and replaces them by so called `PrintableOps`. These ops have no functionallity other than printing and disappear as soon as the printing is done. Let's try setting rewrite to false and printing an expression.

```
>>> from calcora.core.ops import Var
>>> from calcora.globals import pc, PrintOptions
>>> pc.print_type = PrintOptions.Regular
>>> expression = (x-2)/3
>>> expression
(x - 2.0)/3.0
>>> pc.rewrite = False
>>> expression
(x + (-2.0))*3.0^(-1.0)
```

See the difference? The rewriter makes the output a whole lot easier to read right? There is one last "setting" for printing, simplify. You might be able to guess what it does... 

```
>>> from calcora.core.ops import Var
>>> from calcora.globals import pc
>>> expression = (x + 0)**1 - (-3) + x**1 * x**29
>>> expression
(x + 0.0)^1.0 - (-3.0) + x^1.0*x^29.0
>>> pc.simplify = True
x + 3.0 + x^30.0
```

The simplfy "setting" causes the printer to run the symbolic pattern matcher on the expression before printing it. Note however that this does not change the expression it only prints a simplified copy of it.

This might not be the best or most powerful math library (not even close), but it works, ish...