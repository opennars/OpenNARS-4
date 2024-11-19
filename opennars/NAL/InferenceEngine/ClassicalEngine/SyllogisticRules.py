"""
Reference:
SyllogisticRules.java in OpenNARS 1.5.6
It is transated into python.
@author: Bowen Xu
@date: Nov 11, 2024
"""
from opennars.Narsese import Term, Statement, Sentence, Budget, Truth
from opennars.NAL.Functions.BudgetFunctions import *
from opennars.NAL.Functions.TruthValueFunctions import *
from opennars.NAL.Functions.StampFunctions import *
import util

''' --------------- rules used in both first-tense inference and higher-tense inference --------------- '''

def ded_exe(term1: Term, term2: Term, task: Task, belief: Sentence, budget_tasklink: Budget, budget_termlink: Budget=None) -> list[Task]|None:
    '''
    {<S ==> M>, <M ==> P>} |- {<S ==> P>, <P ==> S>}
    Args:
        term1: Subject of the first new task
        term2: Predicate of the first new task
        task: The first premise
        belief: The second premise
        budget_tasklink: The budget for the task-link
        budget_termlink: The budget for the term-link
    '''
    if util.invalid_statement(term1, term2):
        return
    
    order1 = task.term.temporal_order
    order2 = belief.term.temporal_order
    order: int = dedExeOrder(order1, order2);
    if (order == ORDER_INVALID) {
        return;
    }
    
    value1 = task.truth
    value2 = belief.truth
    truth1 = None
    truth2 = None

    if task.is_question:
        budget1 = Budget_backward_weak(value2, budget_tasklink, budget_termlink)
        budget2 = Budget_backward_weak(value2, budget_tasklink, budget_termlink)
    else:
        truth1 = Truth_deduction(value1, value2)
        truth2 = Truth_exemplification(value1, value2)
        budget1 = Budget_forward(truth1, budget_tasklink, budget_termlink)
        budget2 = Budget_forward(truth2, budget_tasklink, budget_termlink)
    
    content: Statement = task.term # Assuming content is a Statement
    content1 = util.make_statement(content, term1, term2)
    content2 = util.make_statement(content, term2, term1)
    
    task_derived1 = util.double_premise_task(task, belief, content1, truth1, budget1)
    task_derived2 = util.double_premise_task(task, belief, content2, truth2, budget2)

    return [task_derived1, task_derived2]

def abd_ind_com(task: Task, belief: Sentence, term1: Term, term2: Term, figure: int, budget_tasklink: Budget, budget_termlink: Budget=None) -> list[Task]|None:
    '''
    {<M ==> S>, <M ==> P>} |- {<S ==> P>, <P ==> S>, <S <=> P>}

    Args:
        term1: Subject of the first new task
        term2: Predicate of the first new task
        taskSentence: The first premise
        belief: The second premise
        figure: Locations of the shared term in premises
        [to be added]
    '''
    tasks_derived = []

    if util.invalid_statement(term1, term2) or util.invalid_pair(str(term1), str(term2)):
        return
    
    taskContent: Statement = task.term
    truth1: Truth = None
    truth2: Truth = None
    truth3: Truth = None
    budget1: Budget; budget2: Budget; budget3: Budget
    value1: Truth = task.truth
    value2: Truth = belief.truth
    if task.is_question:
        budget1 = Budget_backward(value2, budget_tasklink, budget_termlink)
        budget2 = Budget_backward_weak(value2, budget_tasklink, budget_termlink)
        budget3 = Budget_backward(value2, budget_tasklink, budget_termlink)
    else:
        truth1 = Truth_abduction(value1, value2);
        truth2 = Truth_abduction(value2, value1);
        truth3 = Truth_comparison(value1, value2);
        budget1 = Budget_forward(truth1, budget_tasklink, budget_termlink)
        budget2 = Budget_forward(truth2, budget_tasklink, budget_termlink)
        budget3 = Budget_forward(truth3, budget_tasklink, budget_termlink)
    
    statement1 = util.make_statement(taskContent, term1, term2)
    statement2 = util.make_statement(taskContent, term2, term1)
    statement3 = util.make_symmetric_statement(taskContent, term1, term2)
    tasks_derived.append(util.double_premise_task(task, belief, statement1, truth1, budget1))
    tasks_derived.append(util.double_premise_task(task, belief, statement2, truth2, budget2))
    tasks_derived.append(util.double_premise_task(task, belief, statement3, truth3, budget3))