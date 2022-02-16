from copy import copy
from typing import Union
from pynars.NAL.Functions.Tools import project_truth, revisible, truth_to_quality
from pynars.NARS.DataStructures._py.Buffer import Buffer
from pynars.Narsese._py.Budget import Budget
from pynars.Narsese._py.Copula import Copula
from pynars.Narsese._py.Evidence import Base
from pynars.Narsese._py.Statement import Statement
from pynars.Narsese._py.Term import Term
from ..DataStructures import Task, Belief, Concept, TaskLink, TermLink
from typing import Callable, List, Tuple
from ..RuleMap import RuleCallable, RuleMap_v2
from pynars.NAL.Inference import local__revision
from pynars.Config import Config
from pynars import Global
from pynars.NAL.Inference import *
from .Engine import Engine

class TemporalEngine(Engine):
    ''''''

    # rule_map = RuleMap_v2()
    
    def __init__(self) -> None:
        ''''''
        super().__init__()


    def step(self, task: Task, concept: Union[Concept, None], sequence_buffer: Buffer, operations_buffer: Buffer):
        ''''''
        tasks_derived = []

        if not (task.is_judgement and task.is_event):
            return tasks_derived
        
        tasks_derived.extend(self.inference_with_sequence(task, sequence_buffer))
        self.add_event(task, concept, sequence_buffer)

        tasks_derived.extend(self.inference_with_operations(task, operations_buffer))
        self.add_operation_feedback(task, operations_buffer)

        return tasks_derived


    def inference_with_sequence(self, task_event: Task, sequence_buffer: Buffer):
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
            # TODO: use SparseLUT to find the rules.
            task1, task2 = (task_event, task) if task.stamp.t_occurrence > task_event.stamp.t_occurrence else (task, task_event)
            
            task = temporal__induction_implication(task1, task2, None, None)
            tasks_derived.append(task)
            if task2.term.is_statement and task2.term.copula in (Copula.ConcurrentImplication, Copula.PredictiveImplication, Copula.RetrospectiveImplication):
                task = temporal__induction_composition(task1, task2, None, None)
            else:
                task = temporal__induction_composition(task2, task1, None, None)
            tasks_derived.append(task)
            # TODO: The current impication above is problematic.

        for task in tasks_attempted:
            sequence_buffer.put_back(task)



        return tasks_derived
        

    def inference_with_operations(self, task_event: Task, operations_buffer: Buffer):
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