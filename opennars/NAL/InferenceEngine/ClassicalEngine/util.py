"""
Reference:
Related code in OpenNARS 1.5.6
It is transated into python.
@author: Bowen Xu
@date: Nov 11, 2024
"""

from opennars.Narsese import Term, Statement, Budget, Truth, Compound, Copula, Connector, Task, Stamp
from opennars.Narsese import Sentence, Judgement, Goal, Question, Quest
from copy import copy, deepcopy
from opennars.NAL.Functions.StampFunctions import Stamp_merge
from . import VariableTools

''' --------------- helper functions for Statement --------------- '''
def invalid_statement(subject: Term|Compound|Statement, predicate: Term|Compound|Statement, check_same_term_in_predicate_and_subject: bool=True):
    '''
    Check the validity of a potential Statement. [To be refined]

    Minimum requirement: the two terms cannot be the same, or containing each other as component
    Args:
        subject: The first component
        predicate: The second component
    Returns:
        Whether The Statement is invalid
    '''
    if subject == predicate:
        return True

    if check_same_term_in_predicate_and_subject:
        if subject == predicate: # e.g., bird --> bird
            return True
        if invalid_reflexive(subject, predicate): # e.g., (|, flyer, swimmer) --> swimmer
            return True

        if invalid_reflexive(predicate, subject): # e.g., swimmer --> (&, flyer, swimmer)
            return True

    if subject.is_statement and predicate.is_statement:
        s1: Statement = subject
        s2: Statement = predicate
        t11 = s1.subject
        t12 = s1.predicate
        t21 = s2.subject
        t22 = s2.predicate
        
        if t11 == t22 and t12 == t21:
            return True

    return False


def invalid_reflexive(t1: Term, t2: Term) -> bool:
    '''
    Check if one term is identical to or included in another one, except in a reflexive relation

    Args:
        t1: The first term
        t2: The second term
    Returns:
        Whether they cannot be related in a statement
    '''
    if not t1.is_compound:
        return False

    com: Compound = t1
    if (com.connector is Connector.ExtensionalImage) or (com.connector is Connector.IntensionalImage):
        return False
    return com.contains_component(t2)

def invalid_pair(s1: str, s2: str) -> bool: 
    if VariableTools.contain_var_indep(s1) and not VariableTools.contain_var_indep(s2):
        return True
    elif not VariableTools.contain_var_indep(s1) and VariableTools.contain_var_indep(s2):
        return True
    return False

def make_statement(statement: Statement, subj: Term, pred: Term) -> Statement:
    '''
    Make a Statement from given components, called by the rules
    Args:
        subj The first component
        pred The second component
        statement A sample statement providing the class type
    Returns: 
        The Statement built
    '''
    if statement.copula is Copula.Inheritance:
        return make_inheritance_statement(subj, pred)
        
    if statement.copula is Copula.Similarity:
        return make_similarity_statement(subj, pred)
    
    if statement.copula is Copula.Implication:
        return make_implication_statement(subj, pred)
    if statement.copula is Copula.Equivalence:
        return make_equivalence_statement(subj, pred)
    return None

def make_symmetric_statement(statement: Statement, subj: Term, pred: Term) -> Statement:
    '''
    Make a symmetric Statement from given components and temporal
    information, called by the rules

    Args:
        statement: A sample asymmetric statement providing the class type
        subj: The first component
        pred: The second component
    Returns:
        The Statement built
    '''
    if (statement.copula is Copula.Inheritance):
        return make_similarity_statement(subj, pred)
    if (statement.copula is Copula.Implication):
        return make_equivalence_statement(subj, pred)
    return None

def make_inheritance_statement(subject: Term, predicate: Term):
    if invalid_statement(subject, predicate):
        return None
    # Note: 
    # In OpenNARS 1.5.7, If the statement has already been built in the memory, it can return the existing statement.
    # However, herein we create a new statement anyway. [to be reconsidered]

    return Statement.Inheritance(subject, predicate)

def make_similarity_statement(subject: Term, predicate: Term):

    '''
    Try to make a new compound from two components. Called by the inference rules.
    Args:
        subject: The first compoment
        predicate: The second compoment
    Returns:
        A compound generated or null
    '''
    if invalid_statement(subject, predicate):
        return None
    
    # Note: 
    #   In OpenNARS 1.5.7, If the statement has already been built in the memory, it can return the existing statement.
    #   However, herein we create a new statement anyway. [to be reconsidered]
    
    return Statement.Similarity(subject, predicate)

def make_implication_statement(subject: Term|None, predicate: Term|None):
    '''
    
    Try to make a new compound from two components. Called by the inference rules.
    Args:
        subject: The first component
        predicate: The second component
    Returns:
        A compound generated or a term it reduced to
    */
    '''
    if (subject is None) or (predicate is None):
        return None
    
    if (subject.copula is Copula.Implication) or (subject.copula is Copula.Equivalence) or (predicate.copula is Copula.Equivalence):
        return None
    
    if invalid_statement(subject, predicate):
        return None

    # Note: 
    #   In OpenNARS 1.5.7, If the statement has already been built in the memory, it can return the existing statement.
    #   However, herein we create a new statement anyway. [to be reconsidered]

    if predicate.is_statement and predicate.copula is Copula.Implication:
        predicate: Statement
        oldCondition: Term = predicate.subject
        if oldCondition.is_compound and (oldCondition.connector is Connector.Conjunction) and (subject in oldCondition.terms):
            return None
        
        newCondition = make_conjunction_compound(subject, oldCondition)
        return make_implication_statement(newCondition, predicate.predicate)
    else:
        return Statement.Implication(subject, predicate)

def make_conjunction_compound(term1: Term, term2: Term):
    '''
    Try to make a new compound from two components. Called by the inference rules.
    Args:
        term1 The first compoment
        term2 The second compoment
    Returns:
        A compound generated or a term it reduced to
    '''
    
    terms = set[Term]()
    if (term1.is_compound and term1.connector is Connector.Conjunction):
        terms = set(term1.terms)
        if (term2.is_compound and term2.connector is Connector.Conjunction):
            terms.update(term2.terms) # (&,(&,P,Q),(&,R,S)) = (&,P,Q,R,S)
        else:
            terms.add(term2) #(&,(&,P,Q),R) = (&,P,Q,R)
    elif term2.is_compound and term2.connector is Connector.Conjunction:
        terms = set(term2.terms)
        terms.update(term1) # (&,R,(&,P,Q)) = (&,P,Q,R)
    else:
        terms = {term1, term2}
    
    # The `Conjunction.make(TreeSet<Term>, Memory)` private method in the java code is unwrapped here
    if len(terms) == 0:
        return None # special case: single component
    if len(terms) == 1:
        return terms.pop() # special case: single component
    
    # Note: 
    #   In OpenNARS 1.5.7, If the statement has already been built in the memory, it can return the existing statement.
    #   However, herein we create a new statement anyway. [to be reconsidered]

    return Compound.Conjunction(*terms)

def make_equivalence_statement(subject: Term, predicate: Term): # to be extended to check if subject is Conjunction
    '''
    Try to make a new compound from two components. Called by the inference rules.
    Args:
        subject: The first component
        predicate: The second component
    Returns:
        A compound generated or null
    '''
    if subject.is_statement and (subject.copula is Copula.Implication) or (subject.copula is Copula.Equivalence):
        return None

    if (predicate.copula is Copula.Implication) or (predicate.copula is Copula.Equivalence):
        return None

    if invalid_statement(subject, predicate):
        return None

    # Note: 
    #   In OpenNARS 1.5.7, If the statement has already been built in the memory, it can return the existing statement.
    #   However, herein we create a new statement anyway. [to be reconsidered]
    
    return Statement.Equivalence(subject, predicate)

def set_component(compound: Compound, index: int, t: Term):
    '''
    Try to replace a component in a compound at a given index by another one
    
    Args:
        compound: The compound
        index: The location of replacement
        t: The new component
    Returns:
        The new compound
    '''
    list1 = list(compound.terms.clone())
    # list_.remove(index)
    if t is not None:
        if (compound.connector is not t.connector):
            list1[index] = t
        else:
            t: Compound = t
            list2 = list(t.terms.clone())
            list1 = [*list1[:index], *list2, *list1[index+1:]]
            
    return Compound(compound.connector, *list1)

def double_premise_task(currentTask: Task, currentBelief: Sentence, newContent: Term, newTruth: Truth, newBudget: Budget, revisible: bool=True):
    '''
    Shared final operations by all double-premise rules, called from the rules except StructuralRules

    Args:
        currentTask: The current task
        newContent: The content of the sentence in task
        newTruth: The truth value of the sentence in task
        newBudget: The budget value in task
        revisible: Whether the sentence is revisible
    '''
    newStamp = Stamp_merge(currentTask.stamp, currentBelief.stamp)
    if newContent is not None:
        punc = currentTask.sentence.punct
        if punc.is_judgement:
            newSentence = Judgement(newContent, newStamp, newTruth)
        elif punc.is_goal:
            newSentence = Goal(newContent, newStamp, newTruth)
        elif punc.is_question:
            newSentence = Question(newContent, newStamp, newTruth)
        elif punc.is_quest:
            newSentence = Quest(newContent, newStamp, newTruth)
        newSentence.revisible = revisible
        newTask = Task(newSentence, newBudget, parent_task=currentTask, parent_belief=currentBelief)
        return newTask
    return None