from typing import Callable, Dict
from pynars.Narsese._py.Operation import *

registered_operations: Dict[Operation, Callable] = {}

def register(operation: Operation, callable: Callable):
    ''''''
    global registered_operations
    registered_operations[operation] = callable

def isRegisteredByName(word) -> bool:
    ''''''
    global registered_operations
    for registered_operation in registered_operations:
        if registered_operation.word == word:
            return True
    return False