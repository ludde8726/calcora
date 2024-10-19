# Calcora

Calcora is a basic math framework that i am writing in my free time. Right now it is very basic but i will keep working on improving it.

## Features

Right now Calcora only supports a few basic features:

### Ops
- Const
- Var
- Add
- Neg
- Mul
- Exp
- Log
---
- Sub
- Div
- Ln

These are the operations that calcora currently supports, however Sub, Div and Ln are only wrappers around other ops for utility reasons. Sub is just an Add combined with a Neg such that `Sub(x, y) = Add(x, Neg(y))` and Div is a Mul and an Exp combined such that `Div(x, y) = Mul(x, Exp(y, Neg(Const(1))))`. Ln is simply a wrapper over Log such that `Ln(x) = Log(x, Const(e))` where e is Eulers number.

Note that i wrote `Neg(Const(1))` inside of the `Exp` insted of simply -1, this is because all ops except for `Const` only accept other Ops as parameters. The reason for this will be explained later.

The `Op` parent class also implements the python operations that Calcora supports. This means that writing `Add(Const(1), Const(2))` is the same as `Const(1) + Const(2)`. Note however that at least one of the arguments must be a Calcora op.

### Variables
As shown in the list of ops that calcora supports variables are an option. These are a special kind of operation that takes in a string as an argument. The variable name is simply a way to identify different variables.

Creating a variable is as simple as
```
>>> from calcora.ops import Var
>>> x = Var('x')
>>> x.args
('x',)
```

Note: All op subclasses have a member variable `args` that returns all the arguments the op was created with.

### Evaluation
All ops have a built in eval method that evaluates the op, for Add, as an example, this means simply adding together the evaluated arguments. The eval method takes in an unspecified amout of keyword arguments, these are for any variables in the expression. Calling eval on an expression with the argument `x = Const(3)` will set the value of every variable with the name `x` in the expression to three and then evaluate. Not specifying a value for any variables in the expression will raise an error.
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
All ops have a built in differentiate method that returns the derivative of said class (all ops are implemented as subclasses of a main `Op` class). Differentiating an expression is a simple as calling `expression.differentiate(var)` where var is the variable you are differentiating based of.

```
>>> from calcora.ops import Add, Const, Mul, Var
>>> x = Var('x')
>>> expression = Add(Mul(Const(2), x), Const(3))
>>> expression.differentiate(x)
(((0 * x) + (2 * 1)) + 0)
```

Note how the derivate is proboably not what you expected, the result should have been `2` right? If you look closely this expression does indeed simplify to two. The reason the result becomes longer and more complicated than it has to be is because we need to cover all possibilies. When the derivative of this operation is calculated, what happens is the outermost operation is evaluated, in this example this is the `Add`. This derivative then return the derivative of both the arguments separately, this is implmented as:
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

Trying something like `Exp(x, Const(2))` will result in an even more complicated expression that also simplifies to the correct result `Mul(Const(2), x)`

```
>>> from calcora.ops import Const, Exp, Var
>>> x = Var('x')
>>> expression = x ** 2
>>> expression.differentiate(x)
(((2 * (x)^((2 + -(1)))) * 1) + (((x)^(2) * ln(x)) * 0))
```

### Pattern matcher
Inside match.py there are two classes, `Pattern` and `PatternMatcher`. These are used to create patterns for simplifying expressions. The `Pattern` class does most of the heavy lifting while `PatternMatcher` works like a wrapper around it to allow for more patterns at once. The `Pattern` class takes in a pattern of type `Op` and a replacement callable that returns an `Op`. The pattern then has a match function which by checking the pattern against an expression finds and replaces parts of the original expression. I won't go into depth how this works exacly but basically it recusively checks all the pattern arguments and the expression arguments until it finds a match. The `PatternMatcher` class takes in an iterable of patterns and saves them in a list. When called using the match method on an expression it continuously loops through the patterns until the expression is no longer simplified by any of the patterns. Inside match.py there is also a `SymbolicPatternMatcher`, which is an instance of the `PatternMatcher` class that has some basic simplification rules. For example there are rules basic for multiplication and addition of zero where `x + 0` becomes `x` and where`x * 0` becomes `0`. In this example `x` stands for any type of operation. There are also more complex patterns in the `SymbolicPatternMatcher`, for example.
`yx + zx = (y+z)x` and `x^y * x^z = x^(y+z)`, the way these are implmented is quite complicated but i can show you the first two rules:
```
Pattern(Add(AnyOp(), Const(0)), lambda x: x), # x + 0 = x
Pattern(Mul(AnyOp(), Const(0)), lambda x: Const(0)), # x * 0 = 0
```
If you want to see how the other rules are implemented you can look inside of match.py. Running the `SymbolicPatternMatcher` on the first two derivatives I showed would look like:
```
>>> from calcora.ops import Add, Const, Mul, Var
>>> from calcora.match import SymbolicPatternMatcher
>>> x = Var('x')
>>> expression = Add(Mul(Const(2), x), Const(3))
>>> dx = expression.differentiate(x)
>>> dx
(((0 * x) + (2 * 1)) + 0)
>>> SymbolicPatternMatcher.match(dx)
2
>>> 
```

```
>>> from calcora.ops import Const, Exp, Var
>>> from calcora.match import SymbolicPatternMatcher
>>> x = Var('x')
>>> expression = x ** 2
>>> dx = expression.differentiate(x)
>>> dx
(((2 * (x)^((2 + -(1)))) * 1) + (((x)^(2) * ln(x)) * 0))
>>> SymbolicPatternMatcher.match(dx)
(2 * (x)^((2 + -(1))))
```

Notice how the result from the last expression still is not completely simplified as much as possible.

### Utilities
There are a few utility functions provided inside of utils.py. The ones you might be interested in are:
* is_const_like
* partial_eval

The `is_const_like` function takes in an expression and returns a boolean of whether the expression contains any variables. This is useful for evaluating expressions you are unsure whether they conain any variables or not, primarily however it is used in `Pattern` and in the `partial_eval` function.

```
>>> from calcora.ops import Const, Var
>>> from calcora.utils import is_const_like
>>> expression_1 = Const(2) * 4 + 1
>>> expression_2 = (Var('x') + 4) / 2
>>> is_const_like(expression_1)
True
>>> is_const_like(expression_2)
False
```

The `partial_eval` function tries to evaluate as much as possible of an expression that contains variables, it recursively checks the arguments of operations and evaluates those who don't contain any variables. Using it on the last example from the `PatternMatcher` we can see how it might be useful.

```
>>> from calcora.ops import Const, Exp, Var
>>> from calcora.match import SymbolicPatternMatcher
>>> from calcora.utils import partial_eval
>>> x = Var('x')
>>> expression = x ** 2
>>> dx = expression.differentiate(x)
>>> dx
(((2 * (x)^((2 + -(1)))) * 1) + (((x)^(2) * ln(x)) * 0))
>>> simplified_dx = SymbolicPatternMatcher.match(dx)
>>> simplified_dx
(2 * (x)^((2 + -(1))))
>>> simplified_dx = partial_eval(simplified_dx)
>>> simplified_dx
(2 * (x)^(1)) # We're getting there
>>> simplified_dx = SymbolicPatternMatcher.match(simplified_dx)
>>> simplified_dx
(2 * x)
```
While this might not be the most elegant library it works (kinda).