from typing import Callable, Dict
from pynars.Narsese._py.Operation import *

registered_operations: Dict[Operation, Callable] = {}

def registered_operation_names():
    ''''''
    global registered_operations
    return [registered_operation.word for registered_operation in registered_operations.keys()]


def register(operation: Operation, callable: Callable):
    ''''''
    global registered_operations
    registered_operations[operation] = callable


def is_registered_by_name(word):
    ''''''
    global registered_operations
    for registered_operation in registered_operations.keys():
        if registered_operation.word == word:
            return True
    return False


def get_registered_operation_by_name(word):
    ''''''
    global registered_operations
    for registered_operation in registered_operations.keys():
        if registered_operation.word == word:
            return registered_operation
    return None