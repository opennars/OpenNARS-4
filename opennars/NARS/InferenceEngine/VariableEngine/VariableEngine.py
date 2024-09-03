from copy import copy
from typing import Union

from opennars.NAL.Functions.Tools import project_truth, revisible, truth_to_quality
from opennars.NARS.DataStructures._py.Buffer import Buffer
from opennars.NARS.DataStructures._py.Link import LinkType
from .Rules import *
from opennars.NARS.RuleMap.add_rule import CommonId
from opennars.Narsese._py.Budget import Budget
from opennars.Narsese._py.Connector import Connector
from opennars.Narsese._py.Copula import Copula
from opennars.Narsese._py.Evidence import Base
from opennars.Narsese._py.Statement import Statement
from opennars.Narsese._py.Term import Term
from ...DataStructures import Task, Belief, Concept, TaskLink, TermLink
from typing import Callable, List, Tuple
from ...RuleMap import RuleCallable, RuleMap
from opennars.NAL.Inference import local__revision
from opennars.Config import Config
from opennars import Global
from opennars.NAL.Inference import *
from ..Engine import Engine
from .extract_feature import extract_feature
from pathlib import Path


def get_common(stat1: Statement, stat2: Statement):
    ''''''
    common1 = None
    common2 = None
    term = None
    if stat1.is_statement and stat2.is_statement:
        if stat1.subject == stat2.subject:
            common1 = 0
            common2 = 0
            term = stat1.subject
        elif stat1.subject == stat2.predicate:
            common1 = 0
            common2 = 1
            term = stat1.subject
        elif stat1.predicate == stat2.subject:
            common1 = 1
            common2 = 0
            term = stat1.predicate
        elif stat1.predicate == stat2.predicate:
            common1 = 1
            common2 = 1
            term = stat1.predicate
    return common1, common2


def has_common(cpmd1: Compound, stat2: Statement):
    common = False
    common1 = None
    common2 = None
    if cpmd1.is_compound and stat2.is_statement:
        ''''''
        for term in cpmd1:
            common1, common2 = get_common(term, stat2)
            if not (common1 is None or common2 is None):
                common = True
                break
    return common, common1, common2

def is_dvar_eliminable(stat1: Statement, stat2: Statement):
    ''''''
    if not (stat1.is_statement and stat2.is_statement):
        return False
    
    if not stat1.equal(stat2): 
        return False
    
    if stat1.subject == stat2.subject and stat1.predicate.is_dvar:
        return True
    
    if stat1.predicate == stat2.predicate and stat1.subject.is_dvar:
        return True
    
    return False

class VariableEngine(Engine):
    ''''''

    rule_map = RuleMap(name='LUT_Variable',
                       root_rules=Path(__file__).parent/'Rules')

    def __init__(self, build=True, add_rules={1, 2, 3, 4, 5, 6, 7, 8, 9}):
        ''''''
        super().__init__()

        n_link_types = max([t.value for t in LinkType.__members__.values()])
        n_copula = len(Copula)
        n_has_common_id = 2
        n_match_reverse = 2
        n_common_id = 4
        n_compound_common_id = 4
        n_connector = len(Connector)
        n_sentence_type = 4

        n_has_compound_common_id = 2
        n_has_at = 2
        n_has_compound_at = 2
        n_the_other_compound_has_common = 2
        n_the_other_compound_p1_at_p2 = 2
        n_the_other_compound_p2_at_p1 = 2
        n_is_belief_valid = 2
        n_at_compound_pos = 2
        n_p1_at_p2 = 2
        n_p2_at_p1 = 2

        self.rule_map.init_type(
            ("is_belief_valid", bool, n_is_belief_valid),

            ("sentence_type", int, n_sentence_type),

            ("match_reverse", bool, n_match_reverse),

            ("LinkType1", LinkType, n_link_types),
            ("LinkType2", LinkType, n_link_types),

            ("L1_Copula1", Copula, n_copula),
            ("L1_Connector1", Connector, n_copula),
            ("L1_Copula2", Copula, n_copula),
            ("L1_Connector2", Connector, n_copula),
            ('L1_common1', int, 2),
            ('L1_common2', int, 2),
            ('L1_has_common', int, 2),
            ('L1_eliminable', bool, 2),

            ("L2_Copula1", Copula, n_copula),
            ("L2_Connector1", Connector, n_copula),
            ("L2_Copula2", Copula, n_copula),
            ("L2_Connector2", Connector, n_copula),
            ('L2_common1', int, 2),
            ('L2_common2', int, 2),
            ('L2_has_common', int, 2),
            ('L2_eliminable', bool, 2),

            ("L3_Copula", Copula, n_copula),
            ("L3_Connector", Connector, n_copula),
            ('L3_common1', int, 2),
            ('L3_common2', int, 2),
            ('L3_has_common', int, 2),
            ('L3_eliminable', bool, 2),
        )

        map = self.rule_map.map
        structure = self.rule_map.structure
        add_rules__NAL6(map, structure) if 6 in add_rules else None

        if build:
            self.build()

    @classmethod
    def match(cls, task_event1: Task, task_event2: Task):
        '''To verify whether the task and the belief can interact with each other'''

        is_valid = False
        rules = cls.match_rule(task_event1, task_event2)
        if rules is not None and len(rules) > 0:
            is_valid = True

        return is_valid, rules

    @classmethod
    def match_rule(cls, task: Task, belief: Union[Belief, None], belief_term: Union[Term, Compound, Statement, None], task_link: TaskLink, term_link: TermLink):
        '''
        Given two events, find the matched rules for one step inference.
        '''
        rules = []
        link1 = task_link.type
        # `term_link` may be `None` in case of single premise inference.
        link2 = term_link.type if term_link is not None else None

        term1 = task.term
        term2 = belief.term

        match_reverse = False
        
        L1_Copula1 = term1.copula if term1.is_statement else None
        L1_Connector1 = term1.connector if term1.is_compound else None
        L1_Copula2 = term2.copula if term2.is_statement else None
        L1_Connector2 = term2.connector if term2.is_compound else None

        L1_common1 = None
        L1_common2 = None
        L1_has_common = None
        L1_eliminable = False

        L2_Copula1 = None
        L2_Connector1 = None
        L2_Copula2 = None
        L2_Connector2 = None
        L2_common1 = None
        L2_common2 = None
        L2_has_common = None
        L2_eliminable = False

        L3_Copula = None
        L3_Connector = None
        L3_common1 = None
        L3_common2 = None
        L3_has_common = None
        L3_eliminable = False

        if term1.is_statement and term2.is_statement:
            stat1: Statement = term1
            stat2: Statement = term2
            match_reverse = stat1.subject == stat2.predicate and stat1.predicate == stat1.subject
        if term1.is_statement and not term1.is_higher_order:  # -->
            stat1: Statement = term1
            stat2: Statement = term2
            L1_common1, L1_common2 = get_common(stat1, stat2)
        elif term1.is_statement and term1.is_higher_order:  # ==>
            stat1: Statement = term1
            stat2: Statement = term2
            if stat1[0].is_statement:  # ==>, -->
                L2_Copula1 = stat1[0].copula
                if not stat1[0].is_higher_order:
                    L2_common1, L1_common2 = get_common(stat1[0], stat2)
                    if L2_common1 is not None:
                        L1_common1 = 0
            elif stat1[0].is_compound:  # ==>, &&
                if stat2.is_statement and stat2.copula is Copula.Inheritance:
                    L2_Connector1 = stat1[0].connector

                    L2_has_common, L3_common1, L1_common2 = has_common(
                        stat1[0], stat2)
                    
                    if L2_has_common:
                        for cpnt in stat1[0]:
                            if cpnt.is_statement and cpnt.copula is Copula.Inheritance:
                                L3_common1, L1_common2 = get_common(cpnt, stat2)
                                if L3_common1 is not None:
                                    L3_Copula = cpnt.copula
                                    L1_common1 = 0
                                    L3_eliminable = is_dvar_eliminable(cpnt, stat2)
                                    break
                elif stat2.is_statement and stat2.copula is Copula.Implication:
                    L2_Connector1 = stat1[0].connector
                    if stat2[0].is_statement and stat2[0].copula is Copula.Inheritance:
                        L2_Copula2 = stat2[0].copula
                        L2_has_common, _, _ = has_common(
                        stat1[0], stat2[0])
                        if L2_has_common:
                            for cpnt in stat1[0]:
                                if cpnt.is_statement and cpnt.copula is Copula.Inheritance:
                                    L3_common1, L2_common2 = get_common(cpnt, stat2[0])
                                    if L3_common1 is not None:
                                        L3_Copula = cpnt.copula
                                        L1_common1 = 0
                                        L1_common2 = 0
                                        L3_eliminable = is_dvar_eliminable(cpnt, stat2[0])
                                        break


            if stat1[1].is_statement and L1_common1 is None:  # ==>, -->

                if not stat1[1].is_higher_order:
                    L2_common1, L1_common2 = get_common(stat1[1], stat2)
                    if L2_common1 is not None:
                        L2_Copula1 = stat1[1].copula
                        L1_common1 = 1
            elif stat1[1].is_compound and L1_common1 is None:  # ==>, &&
                L2_Connector1 = stat1[1].connector

                L2_has_common, L3_common1, L1_common2 = has_common(
                    stat1[1], stat2)
                if L2_has_common:
                    for cpnt in stat1[1]:
                        if cpnt.is_statement and cpnt.copula is Copula.Inheritance:
                            L3_common1, L1_common2 = get_common(cpnt, stat2)
                            if L3_common1 is not None:
                                L3_Copula = cpnt.copula
                                L3_eliminable = is_dvar_eliminable(cpnt, stat2)
                                L1_common1 = 1
                                break

        elif term1.is_compound:  # &&
            cpnd1: Compound = term1
            stat2: Statement = term2
            L1_has_common, L2_common1, L1_common2 = has_common(
                cpnd1, stat2)
            if not L1_has_common: # &&, ==>
                for cpnt in cpnd1:
                    if cpnt.is_statement and cpnt.copula is Copula.Implication:
                        L3_common1, L3_common2 = get_common(cpnt, stat2)
                        if L3_common1 is not None:
                            L2_Copula1 = cpnt.copula
                            L3_eliminable = is_dvar_eliminable(cpnt, stat2)

                            L1_has_common = True
                            break
            else:
                for cpnt in cpnd1:
                    cpnt: Statement
                    if cpnt.is_statement and cpnt.copula is Copula.Inheritance:
                        L2_common1, L1_common2 = get_common(cpnt, stat2)
                        if L2_common1 is not None:
                            L2_Copula1 = cpnt.copula
                            L2_eliminable = is_dvar_eliminable(cpnt, stat2)
                            break

        indices = (
            int(False) if belief is None else int(True),
            task_type_id(task),
            match_reverse,

            link1.value,
            link2.value if link2 is not None else None,

            L1_Copula1,
            L1_Connector1,
            L1_Copula2,
            L1_Connector2,

            L1_common1,
            L1_common2,
            L1_has_common,
            L1_eliminable,

            L2_Copula1,
            L2_Connector1,
            L2_Copula2,
            L2_Connector2,
            L2_common1,
            L2_common2,
            L2_has_common,
            L2_eliminable,

            L3_Copula,
            L3_Connector,
            L3_common1,
            L3_common2,
            L3_has_common,
            L3_eliminable,
        )
        indices = tuple(int(idx) if idx is not None else None for idx in indices)
        rules: RuleCallable = cls.rule_map[indices]
        return rules

    @staticmethod
    def inference(task: Task, belief: Belief, term_belief: Term, task_link: TaskLink, term_link: TermLink, rules: List[RuleCallable]) -> List[Task]:
        ''''''
        tasks_derived = [rule(task, belief, task_link, term_link)
                         for rule in rules]
        return tasks_derived

    def step(self, task: Task, concept: Union[Concept, None], sequence_buffer: Buffer, operations_buffer: Buffer):
        ''''''
        tasks_derived_all = []

        return tasks_derived_all

    def add_operation_feedback(self, task_event: Task, operations_buffer: Buffer):
        ''''''
        # Ref: OpenNARS 3.0.4 ProcessJudgement.java line 116~126, TemporalInferenceControl.java line 215~245
        if task_event.is_operation and not task_event.is_mental_operation:
            operations_buffer.put(task_event)
