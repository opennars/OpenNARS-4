from copy import copy
from NAL.Functions.Tools import project_truth, revisible
from Narsese._py.Budget import Budget
from Narsese._py.Term import Term
from ..DataStructures import Task, Belief, Concept, TaskLink, TermLink
from typing import Callable, List, Tuple
from ..RuleMap import RuleCallable, RuleMap_v2
from NAL.Inference import local__revision
import Global
from .Engine import Engine


class GeneralEngine(Engine):
    
    rule_map = RuleMap_v2()

    def __init__(self):
        ''''''
        super().__init__()


    @classmethod
    def match(cls, task: Task, belief: Belief, belief_term: Term, task_link, term_link):
        '''To verify whether the task and the belief can interact with each other'''

        is_valid = False
        is_revision = False
        rules = []
        if belief is not None:
            if task == belief:
                if task.sentence.punct == belief.sentence.punct:
                    is_revision = revisible(task, belief)
            elif task.term.equal(belief.term): 
                # TODO: here
                pass
            elif not belief.evidential_base.is_overlaped(task.evidential_base):
                # Engine.rule_map.verify(task_link, term_link)
                rules = GeneralEngine.rule_map.match(task, belief, belief_term, task_link, term_link)
                if rules is not None and len(rules) > 0:
                    is_valid = True
        elif belief_term is not None: # belief is None
            if task.term == belief_term:pass
            elif task.term.equal(belief_term): pass
            else:
                rules = GeneralEngine.rule_map.match(task, belief, belief_term, task_link, term_link)
                if rules is not None and len(rules) > 0:
                    is_valid = True
        else: # belief is None and belief_term is None
            rules = GeneralEngine.rule_map.match(task, belief, belief_term, task_link, term_link)
            if rules is not None and len(rules) > 0:
                is_valid = True

        return is_valid, is_revision, rules


    def step(self, concept: Concept):
        '''One step inference.'''
        tasks_derived = []
        
        # Based on the selected concept, take out a task and a belief for further inference.
        task_link_valid: TaskLink = concept.task_links.take(remove=True)
        if task_link_valid is None: return tasks_derived
        concept.task_links.put_back(task_link_valid)

        task: Task = task_link_valid.target

        # inference for single-premise rules
        is_valid, _, rules_immediate = GeneralEngine.match(task, None, None, task_link_valid, None)
        if is_valid:
            tasks = self.inference(task, None, None, task_link_valid, None, rules_immediate)
            tasks_derived.extend(tasks)
    
        # inference for two-premises rules
        term_links = []
        term_link_valid = None
        is_valid = False
        for _ in range(len(concept.term_links)):
            #To find a belief, which is valid to interact with the task, by iterating over the term-links.
            term_link: TaskLink = concept.term_links.take(remove=True)
            term_links.append(term_link)
            
            concept_target: Concept = term_link.target
            belief = concept_target.get_belief() # TODO: consider all beliefs.
            term_belief = concept_target.term
            # if belief is None: continue
            # Verify the validity of the interaction, and find a pair which is valid for inference.
            is_valid, is_revision, rules = GeneralEngine.match(task, belief, term_belief, task_link_valid, term_link)
            if is_revision: tasks_derived.append(local__revision(task, belief, task_link_valid.budget, term_link.budget))
            if is_valid: 
                term_link_valid = term_link
                break
                
        
        if is_valid:
            tasks = self.inference(task, belief, term_belief, task_link_valid, term_link_valid, rules)
            if term_link_valid is not None: # TODO: Check here whether the budget updating is the same as OpenNARS 3.0.4.
                for task in tasks: TermLink.update_budget(term_link_valid.budget, task.budget.quality, belief.budget.priority if belief is not None else concept_target.budget.priority)
            
            tasks_derived.extend(tasks)
        
        for term_link in term_links: concept.term_links.put_back(term_link)
        
        return tasks_derived

    @staticmethod
    def inference(task: Task, belief: Belief, term_belief: Term, task_link: TaskLink, term_link: TermLink, rules: List[RuleCallable]) -> List[Task]: # Tuple[List[Task], List[Tuple[Budget, float, float]]]:
        '''
        It should be ensured that 
            1. the task and the belief can interact with each other;
            2. the task is the target node of the task-link, and the concept correspoding to the belief is the target node of the term-link.
            3. there is a function, indexed by the task_link and the term_link, in the RuleMap.
        '''
        # Temporal Projection and Eternalization
        if belief is not None:
            # TODO: Hanlde the backward inference.
            if not belief.is_eternal and (belief.is_judgement or belief.is_goal):
                truth_belief = project_truth(task.sentence, belief.sentence)
                belief = belief.eternalize(truth_belief)
                # beleif_eternalized = belief # TODO: should it be added into the `tasks_derived`?

        belief = belief if belief is not None else term_belief
        tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules]

        return tasks_derived

