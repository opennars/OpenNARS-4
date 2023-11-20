from typing import Callable, List
from pynars.Config import Config
from pynars.NARS.DataStructures._py.Concept import Concept
from pynars.NARS.DataStructures._py.Memory import Memory
from pynars.Narsese._py.Budget import Budget
from pynars.Narsese._py.Operation import *
from pynars.Narsese._py.Sentence import Goal, Judgement, Quest, Question, Sentence, Stamp
from pynars.Narsese._py.Statement import Statement
from pynars.Narsese._py.Task import Belief, Desire, Task
from pynars.Narsese._py.Truth import Truth
from .Register import registered_operators
from pynars.Narsese import Term
from pynars.NAL.Functions.Tools import truth_from_term, truth_to_quality
from pynars.Narsese import Base
from pynars import Global

def executed_task(task: Task):
    '''
    '''
    input_id = Global.get_input_id()
    truth = Truth(1.0, Config.c_judgement, Config.k)
    # truth = Truth(1.0, 0.5, Config.k)
    stamp = Stamp(Global.time, Global.time, None, Base((input_id,)))
    budget = Budget(Config.p_feedback, Config.d_feedback, truth_to_quality(task.truth))
    
    return Task(Judgement(task.term, stamp, truth), budget, input_id)



def execute(task: Task, concept: Concept, memory: Memory):
    '''
    it should be ensured that the task is executable, i.e., `task.is_executable == True`.
    '''
    if task.term != concept.term:
        concept = memory.take_by_key(task.term, remove=False)
    stat: Statement = task.term
    operator: Operator = stat.predicate
    args = stat.subject.terms
    function_op: Callable = registered_operators.get(operator, None)

    if function_op is not None: 
        belief = executed_task(task)
        if concept is not None: 
            concept.add_belief(belief)
        return function_op(args, task, memory), belief
    else: 
        return None, None