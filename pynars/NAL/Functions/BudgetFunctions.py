# from pynars.NARS.DataStructures._py.Link import TermLink
from math import log2
from pynars.Narsese import Budget, Truth, Term, Task, Goal, Judgement
from pynars.Config import Config
from .ExtendedBooleanFunctions import *
from copy import deepcopy
from .UncertaintyMappingFunctions import w_to_c
from .Tools import truth_to_quality
from .Tools import calculate_solution_quality
from .ExtendedBooleanFunctions import Or

def Budget_revision(budget_task: Budget, truth_task: Truth, truth_belief: Truth, truth_derived: Truth, budget_tasklink: Budget=None, budget_termlink: Budget=None, replace=True, replace_tasklink=True, replace_termlink=True):
    '''
    budget_task (Budget):
        budget, of a task, to be revised.
    truth_task (Truth):
        truth of the task.
    truth_belief (Truth):
        truth of the belief.
    truth_derived (Truth):
        truth of a task derived from the task and the belief.
    replace (bool): 
        whether to revise the `budget_task` without a copy.
        default: True
    budget_tasklink (Budget): default: None
        budget, of the tasklink whose post-link task is the one with the `budget`, to be revised.
    replace_tasklink (bool):  
        whether to revise the `budget_tasklink` without a copy.
        default:True
    budget_termlink (Budget): default: None
        budget, of the termlink whose post-link task is the one with the `budget`, to be revised.
    replace_termlink (bool):  
        whether to revise the `replace_termlink` without a copy.
        default:True

    Ref: OpenNARS 3.1.0 BudgetFunctions.java line 72~118
        Evaluate the quality of a revision, then de-prioritize the premises
    '''
    if not replace: budget_task = deepcopy(budget_task)
    diff_task = abs(truth_task.e - truth_derived.e)
    budget_task.priority = And(budget_task.priority, 1-diff_task)
    budget_task.durability = And(budget_task.durability, 1-diff_task)

    if budget_tasklink is not None:
        if not replace_tasklink: budget_tasklink = deepcopy(budget_tasklink)
        budget_tasklink.priority = And(budget_task.priority, diff_task)
        budget_tasklink.durability = And(budget_task.durability, diff_task)
    if budget_termlink is not None:
        if not replace_termlink: budget_termlink = deepcopy(budget_termlink)
        diff_belief = abs(truth_belief.e - truth_derived.e)
        budget_termlink.priority = And(budget_termlink.priority, 1-diff_belief)
        budget_termlink.durability = And(budget_termlink.durability, 1-diff_belief)
    diff = truth_derived.c - max(truth_task.c, truth_belief.c)
    priority = Or(diff, budget_task.priority)
    durability = Average(diff, budget_task.durability)
    quality = truth_to_quality(truth_derived)
    return Budget(priority, durability, quality), budget_task, budget_tasklink, budget_termlink

def Budget_inference(quality: float, budget_tasklink: Budget, budget_termlink: Budget=None, simplicity: float=1.0):
    '''
    Ref. OpenNARS 3.1.0 BudgetFunctions.java line 292~317.
    '''
    p = budget_tasklink.priority
    d = budget_tasklink.durability * simplicity
    q = quality * simplicity
    if budget_termlink is not None:
        p = Or(p, budget_termlink.priority)
        d = And(d, budget_termlink.durability)
        # budget_termlink.priority = min(1.0, Or(budget_termlink.priority, Or(q, budget_belief.priority)))
        # budget_termlink.durability = min(1.0-Config.budget_epsilon, Or(budget_termlink.durability, q))
    # d = Scalar(d)
    # q = Scalar(q)
    return Budget(p, d, q) # , budget_termlink


def Budget_forward(truth_new_task: Truth, budget_tasklink: Budget, budget_termlink: Budget=None):
    return Budget_inference(truth_to_quality(truth_new_task), budget_tasklink, budget_termlink, 1.0)

def Budget_backward(truth_new_task: Truth, budget_tasklink: Budget, budget_termlink: Budget=None):
    return Budget_inference(truth_to_quality(truth_new_task), budget_tasklink, budget_termlink, 1.0)

def Budget_backward_weak(truth_new_task: Truth, budget_tasklink: Budget, budget_termlink: Budget=None):
    return Budget_inference(w_to_c(1, Config.k)*truth_to_quality(truth_new_task), budget_tasklink, budget_termlink, 1.0)

def Budget_forward_compound(content: Term, truth_new_task: Truth, budget_tasklink: Budget, budget_termlink: Budget=None):
    '''Ref. OpenNARS 3.1.0 BudgetFunctions.java line 254~257.'''
    return Budget_inference(truth_to_quality(truth_new_task), budget_tasklink, budget_termlink, content.simplicity)

def Budget_backward_compound(content: Term, budget_tasklink: Budget, budget_termlink: Budget=None):
    return Budget_inference(1.0, budget_tasklink, budget_termlink, content.simplicity)

def Budget_backward_weak_compound(content: Term, budget_tasklink: Budget, budget_termlink: Budget=None):
    return Budget_inference(w_to_c(1, Config.k), budget_tasklink, budget_termlink, content.simplicity)


'''Bag'''
def Budget_decay(budget: Budget, replace=True):
    '''
    Ref: The Conceptual Design of OpenNARS 3.1.0
    Ref: OpenNARS 3.1.0 BudgetFunctions.java line 176~196
        Decrease Priority after an item is used, called in Bag. After a constant time, p should become d*p. Since in this period, the item is accessed c*p times, each time p-q should multiple d^(1/(c*p)). The intuitive meaning of the parameter "forgetRate" is: after this number of times of access, priority 1 will become d, it is a system parameter
        adjustable in run time.
    '''
    if not replace: budget = deepcopy(budget)
    Q = Config.quality_min
    C = Config.cycles_forget
    p = budget.priority
    q = budget.quality * Q
    d = budget.durability
    if abs(p-q) == 0.0:
        return budget
    budget.priority = q + (p-q)*pow(d, 1.0/(abs(p-q)*C))
    # budget.priority = q + (p-q)*pow(d, 1.0/(abs(p-q)*C)) if p > q else q # the implementation in OpenNARS 3.0.4
    return budget

def Budget_merge(budget_base: Budget, budget_merged: Budget, replace=True):
    '''
    Ref: The Conceptual Design of OpenNARS 3.1.0
        When an item is added into a bag where there is another one with the same key, the two will be merged, with their budget accumulated. In this process, the two quality values should be the same, and if not, the max operator is used. The two priority values are combined using or, so that the result will be no smaller than either of the two, while still remains in the [0, 1] range. For the same reason, or is used to combine the two durability values. Consequently, repeatedly appeared items will get more resources, both at the moment and in the near future.
    Ref: OpenNARS 3.1.0 BudgetFunctions.java line 161~176, 206~209
        There are two options.
        1) use the `max` function to all three values;
        2) use the `or` function to `priority`, use `arithmetic average` funciton to `durability`, and keep the original value of `quality` of the concept unchanged.
    Here the implementation is accordant to the description in the Conceptual Design.
    '''
    if not replace: budget_base = deepcopy(budget_base)
    budget_base.priority = Or(budget_base.priority, budget_merged.priority)
    budget_base.durability = Or(budget_base.durability, budget_merged.durability)
    budget_base.quality = max(budget_base.quality, budget_merged.quality)
    return budget_base


'''Task'''
'''Concept'''
'''Task-Link'''
'''Term-Link'''
'''Belief and Desire'''
'''Processing Units'''
'''Goal Evaluations'''
def Budget_evaluate_goal_solution(problem: Goal, solution: Judgement, budget_problem: Budget, budget_tasklink: Budget=None) -> Budget:
    '''
    Evaluate the quality of a belief as a solution to a problem, then reward the belief and de-prioritize the problem
    '''
    quality = calculate_solution_quality(problem, solution, False) # TODO: final boolean rateByConfidence = problem.getTerm().hasVarQuery();

    budget = Budget(
        Or(budget_problem.priority, quality), 
        budget_problem.durability, 
        truth_to_quality(solution.truth)
    )

    budget_problem.priority = min(1-quality, budget_problem.quality)


    if budget_tasklink is not None:
        raise NotImplementedError("TODO: feedback to links")

    return budget