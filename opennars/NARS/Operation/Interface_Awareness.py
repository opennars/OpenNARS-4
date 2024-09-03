from typing import List
import opennars.NAL.MentalOperation._aware as aware
from opennars.NARS.DataStructures._py.Concept import Concept
from opennars.NARS.DataStructures._py.Memory import Memory
from opennars.Narsese import Task, Term
from ..DataStructures import Bag   
from copy import copy, deepcopy

def aware__believe(task: Task, memory: Memory=None):
    ''''''
    return aware.believe(task.sentence, task.truth, task.budget)

def aware__wonder(task: Task, memory: Memory=None):
    ''''''
    return aware.wonder(task.sentence, task.budget)

# def _aware__doubt(arguments: List[Term], task: Task=None, memory: Memory=None):
#     ''''''
#     term = arguments[1]
#     concept = Concept._conceptualize(memory.concepts, term, task.budget)
#     return execute.doubt(list(concept.belief_table))


def aware__evaluate(task: Task, memory: Memory=None):
    ''''''
    return aware.evaluate(task.sentence, task.budget)


# def _aware__hesitate(arguments: List[Term], task: Task=None, memory: Memory=None):
#     ''''''
#     term = arguments[1]
#     concept = Concept._conceptualize(memory.concepts, term, task.budget)
#     return execute.hesitate(list(concept.desire_table))
    

# def _aware__want(arguments: List[Term], task: Task=None, memory: Memory=None):
#     ''''''
#     statement = arguments[1]
#     return execute.want(statement)
    