from typing import List, Tuple
from pynars.NAL import Inference
from pynars.NARS.DataStructures._py.Concept import Concept
from pynars.NARS.DataStructures._py.Link import Link, TaskLink, TermLink
from pynars.NARS.InferenceEngine.GeneralEngine.GeneralEngine import GeneralEngine
from pynars.Narsese import Task
from pynars import Narsese
from pynars.NARS.RuleMap import RuleMap, RuleCallable
from pynars.NARS import Reasoner as Reasoner
from pynars.Narsese._py.Statement import Statement
from pynars.Narsese._py.Task import Belief
from pynars.Narsese._py.Term import Term
from pynars.NAL.MentalOperation import execute
from pynars.Narsese import Sentence, Judgement, Quest, Question, Goal
from pynars.Config import Config, Enable

nars = Reasoner(100, 100)
engine: GeneralEngine = nars.inference

NUM_CYCLES_MULTIPLIER = 4
def process_two_premises(premise1: str, premise2: str, n_cycle: int) -> List[Task]:
    ''''''
    tasks_all_cycles = []

    success, task, task_overflow = nars.input_narsese(premise1)
    tasks_all_cycles.append(task)
    
    if premise2 is not None:
        success, task, task_overflow = nars.input_narsese(premise2)
        tasks_all_cycles.append(task)

    for tasks_all in nars.cycles(n_cycle*NUM_CYCLES_MULTIPLIER):
        # print('>>>', tasks_all)
        tasks_derived, judgement_revised, goal_revised, answers_question, \
            answers_quest, (task_operation_return, task_executed) = tasks_all
        tasks_all_cycles.extend(tasks_derived)
        if judgement_revised is not None:
            tasks_all_cycles.append(judgement_revised)
        if answers_question is not None:
            tasks_all_cycles.extend(answers_question)
        if answers_quest is not None:
            tasks_all_cycles.extend(answers_quest)

    return [t for t in tasks_all_cycles if t is not None]

def rule_map_two_premises(premise1: str, premise2: str, term_common: str, inverse: bool=False, is_belief_term: bool=False, index_task=None, index_belief=None) -> Tuple[List[RuleCallable], Task, Belief, Concept, TaskLink, TermLink, Tuple[Task, Task, Task, Task]]:
    ''''''
    premise1: Task = Narsese.parse(premise1)
    result1 = nars.memory.accept(premise1)
    premise2: Task = Narsese.parse(premise2)
    result2 = nars.memory.accept(premise2)

    task, belief = (premise1, premise2) if not inverse else( premise2, premise1)
    
    term_common: Term = Narsese.parse(term_common).term
    concept = nars.memory.take_by_key(term_common)


    if index_task is None:
        if task.term == concept.term: index_task = ()
        else: 
            if task.term.complexity > concept.term.complexity: indices_task = Link.get_index(task.term, concept.term)
            else: indices_task = Link.get_index(concept.term, task.term)
            if indices_task is not None: index_task = indices_task[0]


    if index_belief is None:
        if belief.term == concept.term: index_belief = ()
        else:
            if belief.term.complexity > concept.term.complexity: indices_belief = Link.get_index(belief.term, concept.term)
            else: indices_belief = Link.get_index(concept.term, belief.term)
            if indices_belief is not None: index_belief = indices_belief[0]

    tl = TaskLink(concept, task, None, index=index_task)
    task_link = [link for link in concept.task_links.item_lut.lut.values() if link.source == tl.source and link.target==tl.target and link.component_index==tl.component_index]
    task_link = task_link[0] if len(task_link) > 0 else None
    tl = TermLink(concept, belief, None, index=index_belief)
    term_link = [link for link in concept.term_links.item_lut.lut.values() if link.source == tl.source and link.target==tl.target and link.component_index==tl.component_index]
    term_link = term_link[0] if len(term_link) > 0 else None
    
    subst, elimn, intro = GeneralEngine.unify(task.term, belief.term, term_common, task_link, term_link)
    task_subst, task_elimn, task_intro = GeneralEngine.substitute(subst, elimn, intro, task)
    task = task_subst or task_elimn or task_intro or task

    belief: Belief
    _, _, rules = engine.match(task, (belief if not is_belief_term else None), belief.term, task_link, term_link)
    return rules, task, belief, concept, task_link, term_link, result1, result2

def rule_map_task_only(premise1: str, conecept_term: str, index_concept_task: tuple):
    ''''''
    task = Narsese.parse(premise1)
    result1 = nars.memory.accept(task)
    concept_term = Narsese.parse(conecept_term+".").term
    
    concept = nars.memory.take_by_key(concept_term)
    task_link = concept.task_links.take_by_key(TaskLink(concept, task, None, index=index_concept_task))

    _, _, rules = engine.match(task, None, None, task_link, None)
    return rules, task, concept, task_link, result1


def memory_accept_revision(judgement1: str, judgement2: str):
    task1 = Narsese.parse(judgement1)
    nars.memory.accept(task1)
    task2 = Narsese.parse(judgement2)
    task_derived, *_ = nars.memory.accept(task2)
    return [task_derived]


def execute_one_premise(premise: Task):
    ''''''
    stat: Statement = premise.term
    if stat.is_executable:
        op = stat.predicate
        args = stat.subject.terms
        return execute(op, *args)
    else:
        raise "Invalide case."

def output_contains(outputs: List[Task], target: str):
    target: Task = Narsese.parse(target)
    for output in outputs:
        flag_contain = output.term.identical(target.term)
        if output.truth is None:
            flag_contain &= target.truth is None
        else:
            if target.truth is not None:
                flag_contain &= round(output.truth.f, 2) == round(target.truth.f, 2)
                flag_contain &= round(output.truth.c, 2) == round(target.truth.c, 2)
            flag_contain &= target.sentence.is_eternal == output.sentence.is_eternal
            # compare the time stamp
            if not target.sentence.is_eternal:
                flag_contain &= target.stamp.t_occurrence == output.stamp.t_occurrence
        if flag_contain:
            return True
    return False