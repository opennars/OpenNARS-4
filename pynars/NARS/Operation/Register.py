from typing import Callable, Dict
from pynars.Narsese._py.Operation import *

registered_operations: Dict[Operation, Callable] = {}

def registeredOperationNames():
    ''''''
    global registered_operations
    return [registered_operation.word for registered_operation in registered_operations.keys()]


def register(operation: Operation, callable: Callable):
    ''''''
    global registered_operations
    registered_operations[operation] = callable


def isRegisteredByName(word):
    ''''''
    global registered_operations
    for registered_operation in registered_operations.keys():
        if registered_operation.word == word:
            return True
    return False


def getRegisteredOperationByName(word):
    ''''''
    global registered_operations
    for registered_operation in registered_operations.keys():
        if registered_operation.word == word:
            return registered_operation
    return None