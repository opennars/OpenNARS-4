from typing import Callable, Dict
from pynars.Narsese._py.Operation import *

registered_operators: Dict[Operator, Callable] = {}

def registered_operator_names():
    ''''''
    global registered_operators
    return [registered_operator.word for registered_operator in registered_operators.keys()]


def register(operator: Operator, callable: Callable):
    ''''''
    global registered_operators
    registered_operators[operator] = callable


def is_registered_by_name(word):
    ''''''
    global registered_operators
    for registered_operator in registered_operators.keys():
        if registered_operator.word == word:
            return True
    return False


def get_registered_operator_by_name(word):
    ''''''
    global registered_operators
    for registered_operator in registered_operators.keys():
        if registered_operator.word == word:
            return registered_operator
    return None