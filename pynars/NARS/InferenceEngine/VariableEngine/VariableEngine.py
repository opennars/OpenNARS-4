from copy import copy
from typing import Union

from pynars.NAL.Functions.Tools import project_truth, revisible, truth_to_quality
from pynars.NARS.DataStructures._py.Buffer import Buffer
from pynars.NARS.DataStructures._py.Link import LinkType
from .Rules import *
from pynars.NARS.RuleMap.add_rule import CommonId
from pynars.Narsese._py.Budget import Budget
from pynars.Narsese._py.Connector import Connector
from pynars.Narsese._py.Copula import Copula
from pynars.Narsese._py.Evidence import Base
from pynars.Narsese._py.Statement import Statement
from pynars.Narsese._py.Term import Term
from ...DataStructures import Task, Belief, Concept, TaskLink, TermLink
from typing import Callable, List, Tuple
from ...RuleMap import RuleCallable, RuleMap
from pynars.NAL.Inference import local__revision
from pynars.Config import Config
from pynars import Global
from pynars.NAL.Inference import *
from ..Engine import Engine
from .extract_feature import extract_feature
from pathlib import Path

class TemporalEngine(Engine):
    ''''''

    rule_map = RuleMap(name='LUT_Tense', root_rules=Path(__file__).parent/'Rules')
    
    def __init__(self, build=True, add_rules={1,2,3,4,5,6,7,8,9}):
        ''''''
        super().__init__()

        self.rule_map.init_type(
            # init types

        )
        
        map = self.rule_map.map
        structure = self.rule_map.structure
        add_rules__NAL6(map, structure) if 6 in add_rules else None

        if build: self.build()

    @classmethod
    def match(cls, task_event1: Task, task_event2: Task):
        '''To verify whether the task and the belief can interact with each other'''

        is_valid = False
        rules = cls.match_rule(task_event1, task_event2)
        if rules is not None and len(rules) > 0:
            is_valid = True

        return is_valid, rules
        
    @classmethod
    def match_rule(cls, task_event1: Task, task_event2: Task):
        '''
        Given two events, find the matched rules for one step inference.
        '''
        term1 = task_event1.term
        term2 = task_event2.term
        feature = extract_feature(term1, term2)
        indices = (
            # TODO
        )
        rules: RuleCallable = cls.rule_map[indices]
        return rules
        
    @staticmethod
    def inference(task: Task, belief: Belief, term_belief: Term, task_link: TaskLink, term_link: TermLink, rules: List[RuleCallable]) -> List[Task]:
        ''''''
        tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules]
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