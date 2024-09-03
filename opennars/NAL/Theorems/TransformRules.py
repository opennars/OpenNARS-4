'''Although there are some theorems about transform between product and image, they are highly specialized, which can only handle some special forms or cases, e.g. `equivalence_theorem13()` in `StructuralRules.py`.
In this file, some more generalized functions of transform are implemented, though with a little differences in terms of parameters.
'''
from typing import List
from opennars.Narsese import Copula, Statement, Compound, Connector, Term, Judgement, Truth, Task, Belief, Budget, Stamp, Goal, Quest, Question
from opennars.Narsese import place_holder
from opennars.Narsese._py.Sentence import Sentence

from ..Functions.TruthValueFunctions import *
from ..Functions.DesireValueFunctions import *
from ..Functions.StampFunctions import *
from ..Functions.BudgetFunctions import *


def product_to_image(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False, index: tuple=None):
    '''
    it should be ensured that `len(index) >= 2`
    e.g. <(&&,<(*,a,b) --> R>,...) ==> C>. |- <(&&,<a --> (/,R,_,b)>,...) ==> C>
    '''
    term_task = task.term
    stat_product: Statement = term_task[index[:-2]] # <(*,a,b) --> R>
    compound_product: Compound = stat_product[index[-2]] # (*,a,b)
    idx_relation = 1-index[-2]
    idx_product = index[-1]
    term_relation = stat_product[idx_relation] # R
    if idx_relation == 0: # intensional image
        predicate = compound_product[idx_product]
        subject = Compound.IntensionalImage(term_relation, compound_product=compound_product, idx=idx_product)
    elif idx_relation == 1: # extensional image
        subject = compound_product[idx_product]
        predicate = Compound.ExtensionalImage(term_relation, compound_product=compound_product, idx=idx_product)
    else: raise "Invalid case."
    stat_image = Statement(subject, stat_product.copula, predicate) # BUG: the statment input should be replaced with `stat_image`, not using the stat_image as the statement output.
    budget = task.budget
    stamp = task.stamp
    # term_task

    if task.is_judgement:
        truth = task.truth
        sentence_derived = Judgement(stat_image, stamp, truth)
    elif task.is_goal:
        truth = task.truth
        sentence_derived = Goal(stat_image, stamp, truth)
    elif task.is_question:
        sentence_derived = Question(stat_image, stamp)
    elif task.is_quest:
        sentence_derived = Quest(stat_image, stamp)
    else: raise "Invalid case."
    
    return Task(sentence_derived, budget)


def image_to_product(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False, index=None):
    ''''''
    term_task = task.term
    stat_image: Statement = term_task[index[:-2]] # <a --> (/,R,_,b)>
    compound_image: Compound = stat_image[index[-2]] # (/,R,_,b)
    idx_term = 1-index[-2]
    idx_image = index[-1]
    term_relation = compound_image[0] # R
    term = stat_image[1-index[-2]]

    compound_product = Compound.Product(term, compound_image=compound_image)

    if idx_term == 0: 
        subject = compound_product
        predicate = term_relation
    elif idx_term == 1: 
        subject = term_relation
        predicate = compound_product
        
    else: raise "Invalid case."

    stat_image = Statement(subject, stat_image.copula, predicate)
    budget = task.budget
    stamp = task.stamp

    if task.is_judgement:
        truth = task.truth
        sentence_derived = Judgement(stat_image, stamp, truth)
    elif task.is_goal:
        truth = task.truth
        sentence_derived = Goal(stat_image, stamp, truth)
    elif task.is_question:
        sentence_derived = Question(stat_image, stamp)
    elif task.is_quest:
        sentence_derived = Quest(stat_image, stamp)
    else: raise "Invalid case."
    
    return Task(sentence_derived, budget)


def image_to_image(task: Task, term_concept: Term, budget_tasklink: Budget=None, budget_termlink: Budget=None, inverse_premise: bool=False, inverse_copula: bool=False, index=None):
    ''''''
    term_task = task.term
    stat_image: Statement = term_task[index[:-2]] # <a --> (/,R,_,b)>
    compound_image: Compound = stat_image[index[-2]] # (/,R,_,b)
    idx_term = 1-index[-2]
    idx_image = index[-1]
    term = stat_image[1-index[-2]]
    term_replaced = compound_image[idx_image]
    compound_image = Compound.Image(term, compound_image, idx_image)
    if idx_term == 0: 
        subject = term_replaced
        predicate = compound_image
    elif idx_term == 1: 
        subject = compound_image
        predicate = term_replaced

    stat_image = Statement(subject, stat_image.copula, predicate)
    budget = task.budget
    stamp = task.stamp

    if task.is_judgement:
        truth = task.truth
        sentence_derived = Judgement(stat_image, stamp, truth)
    elif task.is_goal:
        truth = task.truth
        sentence_derived = Goal(stat_image, stamp, truth)
    elif task.is_question:
        sentence_derived = Question(stat_image, stamp)
    elif task.is_quest:
        sentence_derived = Quest(stat_image, stamp)
    else: raise "Invalid case."
    
    return Task(sentence_derived, budget)