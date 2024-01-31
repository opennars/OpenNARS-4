from copy import copy
from pynars.NAL.Functions.Tools import project_truth, revisible
from pynars.NARS.DataStructures._py.Link import LinkType
from .Rules import *
from ...RuleMap.add_rule import _compound_has_common, _compound_at, _at, _common
from pynars.NARS.RuleMap.add_rule import CommonId
from pynars.Narsese._py.Budget import Budget
from pynars.Narsese._py.Connector import Connector
from pynars.Narsese._py.Copula import Copula
from pynars.Narsese._py.Term import Term
from ...DataStructures import Task, Belief, Concept, TaskLink, TermLink
from typing import Callable, List, Tuple
from ...RuleMap import RuleCallable, RuleMap
from pynars.NAL.Inference import local__revision
from pynars import Global
from ..Engine import Engine
from .extract_feature import extract_feature
from pathlib import Path
from ....NAL.MetaLevelInference.VariableSubstitution.Unification import unify__substitution, unify__introduction, unify__elimination, Substitution, Introduction, Elimination
from ...DataStructures._py.Link import Link
from pynars.Narsese import VarPrefix

from ..VariableEngine.VariableEngine import VariableEngine
from ordered_set import OrderedSet

class GeneralEngine(Engine):
    
    rule_map = RuleMap(name='LUT', root_rules=Path(__file__).parent/'Rules')

    def __init__(self, build=True, add_rules={1,2,3,4,5,6,7,8,9}):
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

            ("Copula1", Copula, n_copula),
            ("Copula2", Copula, max(n_copula, n_connector)),

            ("Connector1", Connector, n_connector),
            ("Connector2", Connector, n_connector),

            ("has_compound_at", bool, n_has_compound_at),
            ("at_compound_pos", int, n_at_compound_pos),
            ("the_other_compound_has_common", bool, n_the_other_compound_has_common),
            ("the_other_compound_p1_at_p2", bool, n_the_other_compound_p1_at_p2),
            ("the_other_compound_p2_at_p1", bool, n_the_other_compound_p2_at_p1),

            
            ("compound_common_id", CommonId, n_compound_common_id),
            
            ("has_common_id", bool, n_has_common_id),
            ("has_compound_common_id", bool, n_has_compound_common_id),
            ("has_at", bool, n_has_at),
            ("p1_at_p2", bool, n_p1_at_p2),
            ("p2_at_p1", bool, n_p2_at_p1),
            ("common_id", CommonId, n_common_id),

        )
        
        map = self.rule_map.map
        structure = self.rule_map.structure
        add_rules__NAL1(map, structure) if 1 in add_rules else None
        add_rules__NAL2(map, structure) if 2 in add_rules else None
        add_rules__NAL3(map, structure) if 3 in add_rules else None
        add_rules__NAL4(map, structure) if 4 in add_rules else None
        add_rules__NAL5(map, structure) if 5 in add_rules else None
        add_rules__NAL6(map, structure) if 6 in add_rules else None
        add_rules__NAL7(map, structure) if 7 in add_rules else None
        add_rules__NAL8(map, structure) if 8 in add_rules else None
        add_rules__NAL9(map, structure) if 9 in add_rules else None

        if build: self.build()
        
        pass


    @classmethod
    def match(cls, task: Task, belief: Belief, term_belief: Term, task_link, term_link):
        '''To verify whether the task and the belief can interact with each other'''
        is_valid = False
        is_revision = False
        rules = []
        if belief is not None:
            if task == belief:
                if task.sentence.punct == belief.sentence.punct:
                    is_revision = revisible(task, belief)
            elif task.term.identical(belief.term): 
            # elif task.term.equal(belief.term): 
                # TODO: here
                pass
            elif not belief.evidential_base.is_overlaped(task.evidential_base):
                # Engine.rule_map.verify(task_link, term_link)
                rules = GeneralEngine.match_rule(task, belief, term_belief, task_link, term_link)

                rules_var = VariableEngine.match_rule(task, belief, term_belief, task_link, term_link)
                if rules_var is not None:
                    rules = rules | rules_var if rules is not None else rules_var

                if rules is not None and len(rules) > 0:
                    is_valid = True
        elif term_belief is not None: # belief is None
            if task.term == term_belief:pass
            elif task.term.equal(term_belief): pass
            else:
                rules = GeneralEngine.match_rule(task, belief, term_belief, task_link, term_link)
                if rules is not None and len(rules) > 0:
                    is_valid = True
        else: # belief is None and belief_term is None
            rules = GeneralEngine.match_rule(task, belief, term_belief, task_link, term_link)
            if rules is not None and len(rules) > 0:
                is_valid = True

        return is_valid, is_revision, rules

    @classmethod
    def match_rule(cls, task: Task, belief: Union[Belief, None], belief_term: Union[Term, Compound, Statement, None], task_link: TaskLink, term_link: TermLink) -> OrderedSet:
        '''
        Given a task and a belief, find the matched rules for one step inference.
        ''' 
        link1 = task_link.type
        link2 = term_link.type if term_link is not None else None # `term_link` may be `None` in case of single premise inference.
        
        the_other_compound_has_common = the_other_compound_p1_at_p2 = the_other_compound_p2_at_p1 = False
        connector1 = connector2 = None
        at_compound_pos = None

        common_id = None
        compound_common_id = None

        feature = extract_feature(task.term, (belief.term if belief is not None else belief_term))
        p2_at_p1 = feature.p2_at_p1
        p1_at_p2 = feature.p1_at_p2

        # if belief_term is None:
        if link1 is LinkType.TRANSFORM:
            compound_transform: Compound = task.term[task_link.component_index[:-1]]
            if compound_transform.is_compound:
                connector1 = compound_transform.connector
                if connector1 in (Connector.ExtensionalImage, Connector.IntensionalImage) and task_link.component_index[-1] == 0:
                    connector1 = None

        elif belief_term is not None:
            if feature.match_reverse is True:
                pass
            elif feature.has_common_id:
                if feature.has_at:
                    if feature.common_id_task is not None:
                        common_id = feature.common_id_task 
                    elif feature.common_id_belief is not None:
                        common_id = feature.common_id_belief
                    else: raise "Invalid case."
                elif feature.has_compound_at:
                    if feature.compound_common_id_task is not None:
                        common_id = feature.compound_common_id_task 
                        compound: Compound = task.term[common_id]
                        connector1 = compound.connector
                    elif feature.compound_common_id_belief is not None:
                        common_id = feature.compound_common_id_belief
                        compound: Compound = belief_term[common_id]
                        connector2 = compound.connector
                    else: raise "Invalid case."

                    if compound.is_double_only:
                        if compound[0] == belief_term: 
                            at_compound_pos = 0 
                        elif compound[1] == belief_term:
                            at_compound_pos = 1
                        else: raise "Invalid case."
                elif feature.has_compound_common_id:
                    
                    if feature.compound_common_id_belief is not None and feature.compound_common_id_task is not None: 
                        # Now, both `task` and `belief` are not None.
                        compound_task_term: Compound = task.term[feature.compound_common_id_task]
                        compound_belief_term: Compound = belief_term[feature.compound_common_id_belief]
                        compound_p1_at_p2 = _compound_at(compound_task_term, compound_belief_term, False)
                        compound_p2_at_p1 = _compound_at(compound_belief_term, compound_task_term, False)
                        if compound_p1_at_p2 and compound_belief_term.is_compound:
                            connector2 = compound_belief_term.connector
                        if compound_p2_at_p1 and compound_task_term.is_compound:
                            connector1 = compound_task_term.connector
                        
                        compound_common_id = feature.compound_common_id_task*2 + feature.compound_common_id_belief
                    elif feature.compound_common_id_belief is None and belief_term.is_compound: 
                        # Now, `belief` is None
                        compound_common_id = feature.compound_common_id_task
                        connector2 = belief_term.connector
                        if compound_common_id is not None:
                            common_term = task.term[compound_common_id]
                            if belief_term.is_double_only:
                                if common_term == belief_term[0]: 
                                    at_compound_pos = 0 
                                elif common_term == belief_term[1]:
                                    at_compound_pos = 1
                                else: raise "Invalid case."
                            elif belief_term.is_multiple_only:
                                if common_term == belief_term[0]: 
                                    at_compound_pos = 0 
                                else:
                                    at_compound_pos = 1
                                pass

                    elif feature.compound_common_id_task is None: 
                        # Now, `task` is None
                        compound_common_id = feature.compound_common_id_belief
                        task_term: Compound = task.term
                        if task_term.is_compound: 
                            connector1 = task_term.connector
                        #     compound_belief = belief_term[compound_common_id]
                        #     if compound_belief.is_compound:
                        #         connector2 = compound_belief.connector
                        # elif belief_term.is_compound:
                        #     connector2 = belief_term.connector
                        #     compound_task = task_term[compound_common_id]
                        #     if compound_task.is_compound:
                        #         connector1 = compound_task.connector
                        

                elif feature.common_id_task is not None and feature.common_id_belief is not None:
                    common_id = feature.common_id_task*2 + feature.common_id_belief
                else:
                    if feature.p1_at_p2 and belief_term.is_compound:
                        connector2 = belief_term.connector
                    if feature.p2_at_p1 and task.term.is_compound:
                        connector1 = task.term.connector
            else:
                if task.term.is_compound:
                    connector1 = task.term.connector
                if belief_term.is_compound:
                    connector2 = belief_term.connector
            
            term1, term2 = feature.the_other1, feature.the_other2
            if term1 is not None and term2 is not None:
                the_other_compound_has_common = _compound_has_common(term1, term2)
                # _the_other_compound_has_common1 = _the_other_compound_has_common2 = False
                

                if the_other_compound_has_common:
                    the_other_compound_p1_at_p2 = _compound_at(term1, term2, the_other_compound_has_common)
                    the_other_compound_p2_at_p1 = _compound_at(term2, term1, the_other_compound_has_common)

                    if the_other_compound_p1_at_p2 and the_other_compound_p2_at_p1: 
                        term1: Compound
                        term2: Compound
                        connector1 = term1.connector
                        connector2 = term2.connector
                    elif the_other_compound_p1_at_p2: 
                        term2: Compound
                        connector1 = None
                        connector2 = term2.connector
                        # if term2.is_double_only:
                        #     if term1 == term2[0]: at_compound_pos = 0 
                        #     elif term1 == term2[1]: at_compound_pos = 1
                        #     else: raise "Invalid case."
                    elif the_other_compound_p2_at_p1: 
                        term1: Compound
                        connector1 = term1.connector
                        connector2 = None
                        # if term1.is_double_only:
                        #     if term2 == term1[0]: at_compound_pos = 0 
                        #     elif term2 == term1[1]: at_compound_pos = 1
                        #     else: raise "Invalid case."
        if connector1 is not None and connector1 is Connector.SequentialEvents:
            # if connector1 is &/, then judge whether p1 is the first component of p1
            if p2_at_p1 and belief_term is not None:
                # (&/, A, B, C)! A.
                if not belief_term.equal(task.term.terms[0]):
                    p2_at_p1 = False
        elif connector2 is not None and connector2 is Connector.SequentialEvents:
            # if connector1 is &/, then judge whether p1 is the first component of p1
            if p1_at_p2 and belief_term is not None:
                # C! (&/, A, B, C).
                if not task.term.equal(belief_term.terms[-1]):
                    p1_at_p2 = False



        indices = (
            int(False) if belief is None else int(True),
            task_type_id(task),
            int(feature.match_reverse),
            
            link1.value,
            link2.value if link2 is not None else None,

            int(task.term.copula) if task.term.is_statement else None, 
            int(belief.term.copula) if (belief is not None and belief_term.is_statement) else None, # (int(belief_term.connector) if (belief_term is not None and belief_term.is_compound) else None),

            int(connector1) if connector1 is not None else None, 
            int(connector2) if connector2 is not None else None,

            int(feature.has_compound_at), 
            at_compound_pos,
            int(the_other_compound_has_common),
            int(the_other_compound_p1_at_p2),
            int(the_other_compound_p2_at_p1),

            compound_common_id,

            int(feature.has_common_id), 
            int(feature.has_compound_common_id), 
            int(feature.has_at), 
            int(p1_at_p2) if p1_at_p2 is not None else None,
            int(p2_at_p1) if p2_at_p1 is not None else None,
            common_id, 
            
            
        )
        rules: RuleCallable = cls.rule_map[indices]
        return rules

    def step(self, concept: Concept):
        '''One step inference.'''
        tasks_derived = []

        Global.States.record_concept(concept)
        
        # Based on the selected concept, take out a task and a belief for further inference.
        task_link_valid: TaskLink = concept.task_links.take(remove=True)
        if task_link_valid is None: return tasks_derived
        concept.task_links.put_back(task_link_valid)

        task: Task = task_link_valid.target

        # inference for single-premise rules
        is_valid, _, rules_immediate = GeneralEngine.match(task, None, None, task_link_valid, None)
        if is_valid:
            Global.States.record_premises(task)
            Global.States.record_rules(rules_immediate)
            tasks = self.inference(task, None, None, task_link_valid, None, rules_immediate)
            tasks_derived.extend(tasks)
    
        # inference for two-premises rules
        term_links = []
        term_link_valid = None
        is_valid = False
        for _ in range(len(concept.term_links)):
            # To find a belief, which is valid to interact with the task, by iterating over the term-links.
            term_link: TermLink = concept.term_links.take(remove=True)
            term_links.append(term_link)

            if not task_link_valid.novel(term_link, Global.time):
                continue
            
            concept_target: Concept = term_link.target
            belief = concept_target.get_belief() # TODO: consider all beliefs.
            if belief is None: continue
            term_belief = concept_target.term
            # if belief is None: continue

            # before matching and applying the rules, do variable-related processes (i.e. unification, and substitution/introduction/elimination)
            subst, elimn, intro = GeneralEngine.unify(task.term, belief.term if belief is not None else None, concept.term, task_link_valid, term_link)
            task_subst, task_elimn, task_intro = GeneralEngine.substitute(subst, elimn, intro, task)
            task = task_subst or task_elimn or task_intro or task

            # Verify the interaction, and find a pair which is valid for inference.
            is_valid, is_revision, rules = GeneralEngine.match(task, belief, term_belief, task_link_valid, term_link)
            if is_revision: tasks_derived.append(local__revision(task, belief, task_link_valid.budget, term_link.budget))
            if is_valid: 
                term_link_valid = term_link
                break
                
        
        if is_valid:
            Global.States.record_premises(task, belief)
            Global.States.record_rules(rules)
            new_tasks = self.inference(task, belief, term_belief, task_link_valid, term_link_valid, rules)
            if term_link_valid is not None:
                # reward the termlink
                for new_task in new_tasks:
                    reward: float = max(new_task.budget.priority, task.achieving_level())
                    term_link_valid.reward_budget(reward)

            tasks_derived.extend(new_tasks)
        
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
        tasks_derived = []
        for rule in rules:
            try:
                tasks_derived.append(rule(task, belief, task_link, term_link))
            except:
                pass
        # tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules]

        # normalize the variable indices
        for task in tasks_derived:
            task.term._normalize_variables()

        return tasks_derived

    @staticmethod
    def unify(term1: Term, term2: Term, term_common: Term, task_link: Link, term_link: Link) -> Tuple[Substitution, Elimination, Introduction]:
        ''''''
        subst: Substitution
        elimn: Elimination
        intro: Introduction
        subst, elimn, intro = None, None, None
        
        # find a possible (var-to-var) substitution
        if term2 is not None and term_link is not None:
            # +: term_common is a component of task.term/belief.term
            # -: task.term/belief.term is a component of term_common
            # four possible cases: 1. ++ 2. +- 3. -+ 4. -- 
            if task_link.source_is_component and term_link.source_is_component: # ++
                pos1 = list(task_link.component_index)
                pos2 = list(term_link.component_index)
                if term_common.is_atom:
                    pos1, pos2 = pos1[:-1], pos2[:-1]
                subst = unify__substitution(term1, term2, pos1, pos2)
                # elimn = unify__elimination(term1, term2, pos1, pos2)
            elif task_link.source_is_component and not term_link.source_is_component: # +-
                pos1 = list(task_link.component_index) + list(term_link.component_index)
                pos2 = []
                subst = unify__substitution(term1, term2, pos1, pos2)
            elif not task_link.source_is_component and term_link.source_is_component: # -+
                pos1 = [] 
                pos2 = list(term_link.component_index) + list(task_link.component_index)
                subst = unify__substitution(term1, term2, pos1, pos2)
            elif not task_link.source_is_component and not term_link.source_is_component: # --
                pass # TODO
        
        # find a possible elimination
        if term2 is not None and term_link is not None:
            if task_link.source_is_component and term_link.source_is_component: # ++
                pos1 = list(task_link.component_index)
                pos2 = list(term_link.component_index)
                pos1, pos2 = pos1[:-1], pos2[:-1]
                elimn = unify__elimination(term1, term2, pos1, pos2)
            
        return subst, elimn, intro

    @staticmethod
    def substitute(subst: Substitution, elimn: Elimination, intro: Introduction, task: Task):
        ''''''
        task_subst, task_elimn, task_intro = None, None, None
        if subst is not None and subst.is_valid:
            term_task = subst.apply()
            if task.is_judgement: sentence = Judgement(term_task, task.stamp, task.truth)
            elif task.is_goal: sentence = Goal(term_task, task.stamp, task.truth)
            elif task.is_question: sentence = Question(term_task, task.stamp)
            elif task.is_quest: sentence = Quest(term_task, task.stamp)
            task = Task(sentence, task.budget)
        if elimn is not None and elimn.is_ivar_valid:
            term_task = elimn.apply(type_var={VarPrefix.Independent})
            if task.is_judgement: sentence = Judgement(term_task, task.stamp, task.truth)
            elif task.is_goal: sentence = Goal(term_task, task.stamp, task.truth)
            elif task.is_question: sentence = Question(term_task, task.stamp)
            elif task.is_quest: sentence = Quest(term_task, task.stamp)
            task_elimn = Task(sentence, task.budget)
        return task_subst, task_elimn, task_intro