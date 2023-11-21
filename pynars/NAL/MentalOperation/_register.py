
from typing import Callable, Dict
from pynars.Narsese._py.Operation import *

registered_operators: Dict[Operator, Callable] = {}

def register(operator: Operator, callable: Callable):
    ''''''
    global registered_operators
    registered_operators[operator] = callable