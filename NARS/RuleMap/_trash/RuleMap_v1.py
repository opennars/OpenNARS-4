from typing import Callable, Tuple, Type, Protocol, List
from pynars.NARS.DataStructures import Link, TaskLink, TermLink
from pynars.Narsese.Parser.narsese_lark import Rule
from pynars.Narsese import Belief, Term, Truth, Compound, Budget
from pynars.Narsese._py.Copula import Copula
from pynars.Narsese._py.Statement import Statement
from pynars.Narsese._py.Term import TermType
from ..DataStructures import LinkType, Task
import numpy as np
from pynars.NAL.Inference import *

from . import Interface_SyllogisticRules

def _at(compound: Compound, component: Term):
    '''
    To judge whether the `component` is in the `compound`.

    e.g. A@(&&,A,B), then return (True, 0); 
        B@(&&,A,B), then return (True, 1); 
        C@(&&,A,B), then return (False, None)
    '''

def _common(premise1: Statement, premise2: Statement):
    '''
    To judge whether the `premise1` and the `premise2` have common term.

    e.g. <S-->M>, <M-->P>, then return (True, 1, 0);
        <M-->P>, <S-->M>, then return (True, 0, 1);
        <M-->P>, <M-->S>, then return (True, 0, 0);
        <P-->M>, <S-->M>, then return (True, 1, 1);
        <A==>B>, A, then return (True, 0, 0)
        <A==>B>, B, then return (True, 1, 0)

    Return:
        has_common_id (bool), common_id_task (int), common_id_belief (int), match_reverse (bool)
    '''
    if premise1.is_statement and premise2.is_statement:
        if premise1.subject == premise2.predicate and premise1.predicate == premise2.subject:
            return True, None, None, True
        if premise1.subject == premise2.subject:
            return True, 0, 0, False
        elif premise1.subject == premise2.predicate:
            return True, 0, 1, False
        elif premise1.predicate == premise2.subject:
            return True, 1, 0, False
        elif premise1.predicate == premise2.predicate:
            return True, 1, 1, False
        else:
            return False, None, None, False
    elif premise1.is_statement and premise2.is_atom:
        if premise1.subject == premise2:
            return True, 0, 0, False
        elif premise1.predicate == premise2:
            return True, 1, 0, False
        else:
            return False, None, None, False
    elif premise2.is_statement and premise1.is_atom:
        if premise2.subject == premise1:
            return True, 0, 0, False
        elif premise2.predicate == premise1:
            return True, 0, 1, False
        else:
            return False, None, None, False
    else:
        return False, None, None, False


class RuleCallable(Protocol):
    def __call__(self, 
        task: Task, 
        belief: Belief, 
        budget_tasklink: Budget=None, 
        budget_termlink: Budget=None
    ) -> Tuple[Task, Tuple[Budget, float, float]]: ...

class RuleMapCallable(Protocol):
    def __call__(self, 
        task: Task, 
        term_belief: Statement | Term,
        truth_belief: Truth | None, 
        task_link: TaskLink, 
        term_link: TermLink
    ) -> List[RuleCallable]: ...



class RuleMap:
    # type_map: np.ndarray
    def __init__(self) -> None:
        '''
        given to premises, including the type of links and the relation (`_at` or `_common`), matched rules are obtained.
        '''
        n_types = max([t.value for t in LinkType.__members__.values()]) + 1
        self.type_map = np.empty((n_types, n_types), dtype=object) # There are 10 types of task-link and 8 types of term-link.
        # self.type_map[:, :] = None
        # self.type_map[LinkType.SELF.value, LinkType.COMPONENT.value] = self._self__component
        # self.type_map[LinkType.SELF.value, LinkType.COMPOUND.value] = self._self__compound
        # self.type_map[LinkType.SELF.value, LinkType.COMPONENT_STATEMENT.value] = self._self__component_statement
        # self.type_map[LinkType.SELF.value, LinkType.COMPOUND_STATEMENT.value] = self._self__compound_statement
        # self.type_map[LinkType.SELF.value, LinkType.COMPONENT_CONDITION.value] = self._self__component_condition
        # self.type_map[LinkType.SELF.value, LinkType.COMPOUND_CONDITION.value] = self._self__compound_condition
        # self.type_map[LinkType.COMPOUND.value, LinkType.COMPOUND.value] = self._compound__compound
        # self.type_map[LinkType.COMPOUND.value, LinkType.COMPOUND_STATEMENT.value] = self._compound__compound_statement
        # self.type_map[LinkType.COMPOUND.value, LinkType.COMPOUND_CONDITION.value] = self._compound__compound_condition
        # self.type_map[LinkType.COMPOUND_STATEMENT.value, LinkType.COMPONENT.value] = self._compound_statement__component
        # self.type_map[LinkType.COMPOUND_STATEMENT.value, LinkType.COMPOUND.value] = self._compound_statement__compound
        self.type_map[LinkType.COMPOUND_STATEMENT.value, LinkType.COMPOUND_STATEMENT.value] = self._compound_statement__compound_statement
        # self.type_map[LinkType.COMPOUND_STATEMENT.value, LinkType.COMPOUND_CONDITION.value] = self._compound_statement__compound_condition
        # self.type_map[LinkType.COMPOUND_CONDITION.value, LinkType.COMPOUND.value] = self._compound_condition__compound
        # self.type_map[LinkType.COMPOUND_CONDITION.value, LinkType.COMPOUND_STATEMENT.value] = self._compound_condition__compound_statement

        pass

    
    

    # def __call__(self, task: Task, belief: Belief) -> Type['RuleMap']:
    #     pass

    def _self__compound(self, task: Task, belief: Belief, task_link: TaskLink, term_link: TermLink):
        '''
        task: C
        belief: (&&, A, C)
        '''
        return []

    def _self__component(self, task: Task, belief: Belief, task_link: TaskLink, term_link: TermLink):
        ''''''
        return []


    def _self__component_statement(self, task: Task, belief: Belief, task_link: TaskLink, term_link: TermLink):
        ''''''
        return []


    def _self__compound_statement(self, 
        task: Task, 
        term_belief: Statement | Term,
        truth_belief: Truth | None, 
        task_link: TaskLink, 
        term_link: TermLink
    ):
        ''''''
        rules = []

        term_task: Statement = task.term
        truth_task = task.sentence.truth
        copula_task = term_task.copula
        copula_belief = term_belief.copula
        connector_task_subject = term_task.subject.copula if term_task.type == TermType.STATEMENT and term_task.subject.type == TermType.COMPOUND else None
        connector_task_predicate = term_task.predicate.copula if term_task.type == TermType.STATEMENT and term_task.predicate.type == TermType.COMPOUND else None
        connector_beleif_subject = term_belief.subject.copula if term_belief.type == TermType.STATEMENT and term_belief.subject.type == TermType.COMPOUND else None
        connector_beleif_predicate = term_belief.predicate.copula if term_belief.type == TermType.STATEMENT and term_belief.predicate.type == TermType.COMPOUND else None

        has_common_id, common_id_task, common_id_belief, match_reverse = _common(term_task, term_belief)
        if not has_common_id: return rules
        match (copula_task, copula_belief):
            case (Copula.Implication, None):
                # {<A==>B>. A.} |- B.
                match (common_id_task, common_id_belief):
                    case (0, 1):
                        pass
                    case (1, 0):
                        pass
                    case (0, 0):
                        pass
                    case (1, 1):
                        pass
                    case _:
                        raise "Error: No matched case!"
        return rules


    def _self__component_condition(self, task: Task, belief: Belief, task_link: TaskLink, term_link: TermLink):
        ''''''
        return []

    
    def _self__compound_condition(self, task: Task, belief: Belief, task_link: TaskLink, term_link: TermLink):
        ''''''
        return []

    
    def _compound__compound(self, task: Task, belief: Belief, task_link: TaskLink, term_link: TermLink):
        ''''''
        return []

    
    def _compound__compound_statement(self, task: Task, belief: Belief, task_link: TaskLink, term_link: TermLink):
        ''''''
        return []

    
    def _compound__compound_condition(self, task: Task, belief: Belief, task_link: TaskLink, term_link: TermLink):
        ''''''
        return []

    def _compound_statement__component(self, task: Task, belief: Belief, task_link: TaskLink, term_link: TermLink):
        ''''''
        return []

    def _compound_statement__compound(self, task: Task, belief: Belief, task_link: TaskLink, term_link: TermLink):
        ''''''
        return []

    def _compound_statement__compound_statement(self, 
        task: Task, 
        term_belief: Statement | Term,
        truth_belief: Truth | None, 
        task_link: TaskLink, 
        term_link: TermLink
    ):
        rules = []

        term_task: Statement = task.term
        truth_task = task.sentence.truth
        copula_task = term_task.copula
        copula_belief = term_belief.copula

        if term_task == term_belief: return rules
        has_common_id, common_id_task, common_id_belief, match_reverse = _common(term_task, term_belief)
        if not has_common_id: return rules
        
        match (copula_task, copula_belief):
            case (Copula.Inheritance, Copula.Inheritance): # OK
                if match_reverse:
                    rules.append(Interface_SyllogisticRules._syllogistic__reversion)
                else:
                    match (common_id_task, common_id_belief): 
                        case (0, 1):
                            rules.append(Interface_SyllogisticRules._syllogistic__deduction__0_1)
                            rules.append(Interface_SyllogisticRules._syllogistic__exemplification__0_1)
                        case (1, 0):
                            rules.append(Interface_SyllogisticRules._syllogistic__deduction__1_0)
                            rules.append(Interface_SyllogisticRules._syllogistic__exemplification__1_0)
                        case (0, 0):
                            rules.append(Interface_SyllogisticRules._syllogistic__induction__0_0)
                            rules.append(Interface_SyllogisticRules._syllogistic__induction__0_0_prime)
                            rules.append(Interface_SyllogisticRules._syllogistic__comparison__0_0)
                        case (1, 1):
                            rules.append(Interface_SyllogisticRules._syllogistic__abduction__1_1)
                            rules.append(Interface_SyllogisticRules._syllogistic__abduction__1_1_prime)
                            rules.append(Interface_SyllogisticRules._syllogistic__comparison__1_1)
                        case _:
                            raise "Error: No matched case!"
            case (Copula.Inheritance, Copula.Similarity):
                if not match_reverse:
                    match (common_id_task, common_id_belief):
                        case (0, 1):
                            rules.append(Interface_SyllogisticRules._syllogistic__analogy__0_1)
                        case (1, 0):
                            rules.append(Interface_SyllogisticRules._syllogistic__analogy__1_0)
                        case (0, 0):
                            rules.append(Interface_SyllogisticRules._syllogistic__analogy__0_0)
                        case (1, 1):
                            rules.append(Interface_SyllogisticRules._syllogistic__analogy__1_1)
                        case _:
                            raise "Error: No matched case!"
            case (Copula.Similarity, Copula.Inheritance):
                if not match_reverse:
                    match (common_id_task, common_id_belief):
                        case (0, 1):
                            rules.append(Interface_SyllogisticRules._syllogistic__analogy__0_1)
                        case (1, 0):
                            rules.append(Interface_SyllogisticRules._syllogistic__analogy__1_0)
                        case (0, 0):
                            rules.append(Interface_SyllogisticRules._syllogistic__analogy__0_0)
                        case (1, 1):
                            rules.append(Interface_SyllogisticRules._syllogistic__analogy__1_1)
                        case _:
                            raise "Error: No matched case!"
            case (Copula.Similarity, Copula.Similarity):
                if not match_reverse:
                    match (common_id_task, common_id_belief):
                        case (0, 1):
                            rules.append(Interface_SyllogisticRules._syllogistic__resemblance__0_1)
                        case (1, 0):
                            rules.append(Interface_SyllogisticRules._syllogistic__resemblance__1_0)
                        case (0, 0):
                            rules.append(Interface_SyllogisticRules._syllogistic__resemblance__0_0)
                        case (1, 1):
                            rules.append(Interface_SyllogisticRules._syllogistic__resemblance__1_1)
                        case _:
                            raise "Error: No matched case!"
            case (Copula.Implication, Copula.Similarity):
                if not match_reverse:
                    match (common_id_task, common_id_belief):
                        case (0, 1):
                            pass
                        case (1, 0):
                            pass
                        case (0, 0):
                            pass
                        case (1, 1):
                            pass
                        case _:
                            raise "Error: No matched case!"
            case (Copula.Similarity, Copula.Implication):
                if not match_reverse:
                    match (common_id_task, common_id_belief):
                        case (0, 1):
                            pass
                        case (1, 0):
                            pass
                        case (0, 0):
                            pass
                        case (1, 1):
                            pass
                        case _:
                            raise "Error: No matched case!"
            case (Copula.Equivalence, Copula.Similarity):
                if not match_reverse:
                    match (common_id_task, common_id_belief):
                        case (0, 1):
                            pass
                        case (1, 0):
                            pass
                        case (0, 0):
                            pass
                        case (1, 1):
                            pass
                        case _:
                            raise "Error: No matched case!"
            case (Copula.Similarity, Copula.Equivalence):
                if not match_reverse:
                    match (common_id_task, common_id_belief):
                        case (0, 1):
                            pass
                        case (1, 0):
                            pass
                        case (0, 0):
                            pass
                        case (1, 1):
                            pass
                        case _:
                            raise "Error: No matched case!"
            case (Copula.Implication, Copula.Implication): # OK
                if match_reverse:
                    rules.append(Interface_SyllogisticRules._syllogistic__reversion)
                else:
                    match (common_id_task, common_id_belief):
                        case (0, 1):
                            rules.append(Interface_SyllogisticRules._syllogistic__deduction__0_1)
                            rules.append(Interface_SyllogisticRules._syllogistic__exemplification__0_1)
                        case (1, 0):
                            rules.append(Interface_SyllogisticRules._syllogistic__deduction__1_0)
                            rules.append(Interface_SyllogisticRules._syllogistic__exemplification__1_0)
                        case (0, 0):
                            rules.append(Interface_SyllogisticRules._syllogistic__induction__0_0)
                            rules.append(Interface_SyllogisticRules._syllogistic__induction__0_0_prime)
                            rules.append(Interface_SyllogisticRules._syllogistic__comparison__0_0)
                        case (1, 1):
                            rules.append(Interface_SyllogisticRules._syllogistic__abduction__1_1)
                            rules.append(Interface_SyllogisticRules._syllogistic__abduction__1_1_prime)
                            rules.append(Interface_SyllogisticRules._syllogistic__comparison__1_1)
                        case _:
                            raise "Error: No matched case!"
            case (Copula.Implication, Copula.Equivalence):
                if not match_reverse:
                    match (common_id_task, common_id_belief):
                        case (0, 1):
                            pass
                        case (1, 0):
                            pass
                        case (0, 0):
                            pass
                        case (1, 1):
                            pass
                        case _:
                            raise "Error: No matched case!"
            case (Copula.Equivalence, Copula.Implication):
                if not match_reverse:
                    match (common_id_task, common_id_belief):
                        case (0, 1):
                            pass
                        case (1, 0):
                            pass
                        case (0, 0):
                            pass
                        case (1, 1):
                            pass
                        case _:
                            raise "Error: No matched case!"
            case (Copula.Equivalence, Copula.Equivalence):
                if not match_reverse:
                    match (common_id_task, common_id_belief):
                        case (0, 1):
                            pass
                        case (1, 0):
                            pass
                        case (0, 0):
                            pass
                        case (1, 1):
                            pass
                        case _:
                            raise "Error: No matched case!"
            case _:
                raise "Error: No matched case!"


        return rules

    def _compound_statement__compound_condition(self, task: Task, belief: Belief, task_link: TaskLink, term_link: TermLink):
        ''''''
        return []

    def _compound_condition__compound(self, task: Task, belief: Belief, task_link: TaskLink, term_link: TermLink):
        ''''''
        return []

    def _compound_condition__compound_statement(self, task: Task, belief: Belief, task_link: TaskLink, term_link: TermLink):
        ''''''
        return []

    def verify(self, task_link: TaskLink, term_link: TermLink, *args):
        return self.type_map[task_link.type.value, term_link.type.value] is not None

    def match(self, task: Task, belief: Belief, task_link: TaskLink, term_link: TermLink):
        '''
        Given a task and a belief, find the matched rules for one step inference.
        ''' 
        rule_map: RuleMapCallable = self.type_map[task_link.type.value, term_link.type.value]
        rules = rule_map(task, belief.term, belief.truth, task_link, term_link)
        return rules
    

    def __repr__(self) -> str:
        '''print self.type_map'''
        pass
    
    