import calcora.core.ops
import calcora.core.constants

from calcora.core.registry import FunctionRegistry, ConstantRegistry

Var = FunctionRegistry.get('Var')
Const = FunctionRegistry.get('Const')
Complex = FunctionRegistry.get('Complex')
Add = FunctionRegistry.get('Add')
Neg = FunctionRegistry.get('Neg')
Mul = FunctionRegistry.get('Mul')
Log = FunctionRegistry.get('Log')
Pow = FunctionRegistry.get('Pow')

Div = FunctionRegistry.get('Div')
Sub = FunctionRegistry.get('Sub')
Ln = FunctionRegistry.get('Ln')

E = ConstantRegistry.get('e')
PI = ConstantRegistry.get('e')