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

class TemporalEngine(Engine):
    ''''''

    rule_map = RuleMap(name='LUT_Tense', root_rules=Path(__file__).parent/'Rules')
    
    def __init__(self, build=True, add_rules={1,2,3,4,5,6,7,8,9}):
        ''''''
        super().__init__()
        n_is_temporal_copula1 = 2
        n_is_temporal_copula2 = 2
        n_is_temporal_connector1 = 2
        n_is_temporal_connector2 = 2
        n_copula = len(Copula)
        n_connector = len(Connector)

        self.rule_map.init_type(
            ("is_temporal_copula1", bool, n_is_temporal_copula1),
            ("is_temporal_copula2", bool, n_is_temporal_copula2),
            ("is_temporal_connector1", bool, n_is_temporal_connector1),
            ("is_temporal_connector2", bool, n_is_temporal_connector2),
            ('copula1', Copula, n_copula),
            ('copula2', Copula, n_copula),
            ('connector1', Connector, n_connector),
            ('connector2', Connector, n_connector),

        )
        
        map = self.rule_map.map
        structure = self.rule_map.structure
        add_rules__NAL7(map, structure) if 7 in add_rules else None

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
            int(feature.is_temporal_copula1),
            int(feature.is_temporal_copula2),
            int(feature.is_temporal_connector1),
            int(feature.is_temporal_connector2),
            int(term1.copula) if term1.is_statement else None,
            int(term2.copula) if term2.is_statement else None,
            int(term1.connector) if term1.is_compound else None,
            int(term2.connector) if term2.is_compound else None
        )
        rules: RuleCallable = cls.rule_map[indices]
        return rules
        
    @staticmethod
    def inference(task_event1: Task, task_event2: Task, rules: List[Callable[[Task, Task], List[Task]]]) -> List[Task]: 
        ''''''
        tasks_derived = []
        for rule in rules:
            try:
                tasks_derived.append(rule(task_event1, task_event2))
            except:
                pass
        # tasks_derived = [rule(task_event1, task_event2) for rule in rules]

        return tasks_derived

    def step(self, task: Task, concept: Union[Concept, None], sequence_buffer: Buffer, operations_buffer: Buffer):
        ''''''
        tasks_derived_all = []

        if not (task.is_judgement and task.is_external_event):
            return tasks_derived_all

        tasks_derived = self.step_with_sequence(task, sequence_buffer)
        self.add_event(task, concept, sequence_buffer)
        tasks_derived_all.extend(tasks_derived)
        
        tasks_derived = self.step_with_operations(task, operations_buffer)
        tasks_derived_all.extend(tasks_derived)
        self.add_operation_feedback(task, operations_buffer)

        return tasks_derived_all


    def step_with_sequence(self, task_event: Task, sequence_buffer: Buffer):
        '''
        inference with `self.sequence_buffer`
            Ref: OpenNARS 3.0.4 TemporalInferenceControl.java line 85~104
        '''
        tasks_derived = []
        tasks_attempted = []
        for _ in range(Config.n_sequence_attempts):
            task: Task = sequence_buffer.take(True)
            if task is None: break
            tasks_attempted.append(task)
            if task.evidential_base.is_overlaped(task_event.evidential_base):
                continue
            

            # temporal induction
            is_valid, rules = TemporalEngine.match(task_event, task)
            if is_valid:
                tasks_derived = self.inference(task_event, task, rules)
                # for task in tasks_derived:
                #     print(task)

        for task in tasks_attempted:
            sequence_buffer.put_back(task)



        return tasks_derived
        

    def step_with_operations(self, task_event: Task, operations_buffer: Buffer):
        '''
        inference with `self.operations_buffer`
            Ref: OpenNARS 3.0.4 TemporalInferenceControl.java line 107~162
        '''
        tasks_derived = []

        return tasks_derived
        
    
    def add_event(self, task_event: Task, concept: Concept, sequence_buffer: Buffer):
        '''
        add the event task to `self.sequence_buffer` and `self.operations_buffer`
            Ref: OpenNARS 3.0.4 TemporalInferenceControl.java line 167~213
        '''
        q = truth_to_quality(task_event.truth)
        p = max(q, concept.budget.priority) if concept is not None else q
        d = 1.0/task_event.term.complexity
        budget = Budget(p, d, q)
        task = Task(task_event.sentence, budget)
        sequence_buffer.put(task)

    def add_operation_feedback(self, task_event: Task, operations_buffer: Buffer):
        ''''''
        # Ref: OpenNARS 3.0.4 ProcessJudgement.java line 116~126, TemporalInferenceControl.java line 215~245
        if task_event.is_operation and not task_event.is_mental_operation:
            operations_buffer.put(task_event)