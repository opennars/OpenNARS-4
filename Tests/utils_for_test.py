from typing import List
from opennars.NARS.InferenceEngine.GeneralEngine.GeneralEngine import GeneralEngine
from opennars.Narsese import Task
from opennars import Narsese
from opennars.NARS import Reasoner as Reasoner
from opennars.Narsese._py.Statement import Statement
from opennars.NAL.MentalOperation import execute

nars = Reasoner(100, 100)
nars.add_channel(nars.narsese_channel)

engine: GeneralEngine = nars.inference

NUM_CYCLES_MULTIPLIER = 4
def process_two_premises(premise1: str, premise2: str, n_cycle: int) -> List[Task]:
    ''''''
    tasks_all_cycles = []

    success, task, task_overflow = nars.input_narsese(premise1, go_cycle=False)
    tasks_all_cycles.append(task)
    
    if premise2 is not None:
        success, task, task_overflow = nars.input_narsese(premise2, go_cycle=False)
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