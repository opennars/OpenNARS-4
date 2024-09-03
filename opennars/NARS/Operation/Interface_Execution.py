from typing import Iterable, List
import opennars.NAL.MentalOperation._execute as _execute
from opennars.NARS.DataStructures._py.Concept import Concept
from opennars.NARS.DataStructures._py.Memory import Memory
from opennars.Narsese import Task, Term
from ..DataStructures import Bag   
from copy import copy, deepcopy

def execute__believe(arguments: Iterable[Term], task: Task=None, memory: Memory=None):
    ''''''
    statement, truth_term = arguments[1], arguments[2]
    return _execute.believe(statement, truth_term)


def execute__doubt(arguments: Iterable[Term], task: Task=None, memory: Memory=None):
    ''''''
    term = arguments[1]
    concept = Concept._conceptualize(memory.concepts, term, task.budget)
    return _execute.doubt(list(concept.belief_table))


def execute__evaluate(arguments: Iterable[Term], task: Task=None, memory: Memory=None):
    ''''''
    statement = arguments[1]
    return _execute.evaluate(statement)


def execute__wonder(arguments: Iterable[Term], task: Task=None, memory: Memory=None):
    ''''''
    statement = arguments[1]
    return _execute.wonder(statement)


def execute__hesitate(arguments: Iterable[Term], task: Task=None, memory: Memory=None):
    ''''''
    term = arguments[1]
    concept = Concept._conceptualize(memory.concepts, term, task.budget)
    return _execute.hesitate(list(concept.desire_table))
    

def execute__want(arguments: Iterable[Term], task: Task=None, memory: Memory=None):
    ''''''
    statement = arguments[1]
    return _execute.want(statement)
    

def execute__register(arguments: Iterable[Term], task: Task=None, memory: Memory=None):
    '''let a term be used as an operator'''
    term = arguments[1]
    return _execute.register(term)
