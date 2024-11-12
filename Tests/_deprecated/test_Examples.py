from typing import List
import unittest

from pynars.NARS.DataStructures import Bag, Task, Concept
from pynars.Narsese import Judgement, Term, Statement, Copula, Truth   

from pathlib import Path
from pynars import Narsese, NARS

from pynars.utils.Print import print_out, PrintType, print_filename

examples_path = Path(__file__).parent/'examples'

def print_tasks(tasks_line):
    tasks_derived, judgement_revised, goal_revised, answers_question, answers_quest, (task_operation_return, task_executed) = tasks_line
    for task in tasks_derived: print_out(PrintType.OUT, task.sentence.repr(), *task.budget)
    
    if judgement_revised is not None: print_out(PrintType.OUT, judgement_revised.sentence.repr(), *judgement_revised.budget)
    if goal_revised is not None: print_out(PrintType.OUT, goal_revised.sentence.repr(), *goal_revised.budget)
    if answers_question is not None: 
        for answer in answers_question: print_out(PrintType.ANSWER, answer.sentence.repr(), *answer.budget)
    if answers_quest is not None: 
        for answer in answers_quest: print_out(PrintType.ANSWER, answers_quest.sentence.repr(), *answers_quest.budget)
    if task_executed is not None:
        print_out(PrintType.EXE, f'{task_executed.term.repr()} = {str(task_operation_return) if task_operation_return is not None else None}')

def run_file(file: str):
    nars = NARS.Reasoner(100, 100)

    with open(file, 'r') as f:
        lines = f.readlines()
    tasks_derived_all: List[Task] = []
    expect_out_empty = False
    output_contains: List[Task] = []
    for i, line in enumerate(lines):
        i += 1
        line = line.strip(' \n')
        if line.startswith("//"):
            continue
        elif line.startswith("'''expect.outEmpty"):
            expect_out_empty = True
            continue
        elif line.startswith("''"):
            if line.startswith("''outputMustContain('"):
                line = line[len("''outputMustContain('"):].rstrip("')\n")
                if len(line) == 0: continue
                try:
                    content_check = Narsese.parser.parse(line)
                    output_contains.append(content_check)
                except:
                    print_out(PrintType.ERROR, f'{file}, line {i}, {line}')
                    raise
            continue
        elif line.startswith("'"):
            continue
        elif line.isdigit():
            n_cycle = int(line)
            print_out(PrintType.INFO, f'Run {n_cycle} cycles.')
            for _ in range(n_cycle):
                tasks_derived = nars.cycle()
                # tasks_derived_all.extend(tasks_derived)
                # for task in tasks_derived: out_print(PrintType.OUT, str(task.sentence), *task.budget)
                print_tasks(tasks_derived)


        else:
            line = line.rstrip(' \n')
            if len(line) == 0:
                continue
            # content = Narsese.parser.parse(line)
            try:
                success, task, _ = nars.input_narsese(line, go_cycle=False)
                if success: print_out(PrintType.IN, task.sentence, *task.budget)
                else: print_out(PrintType.ERROR, f'Invalid input! Failed to parse: {line}')

                tasks_derived = nars.cycle()
                print_tasks(tasks_derived)
                # tasks_derived_all.extend(tasks_derived)
                # for task in tasks_derived: out_print(PrintType.OUT, str(task.sentence), *task.budget)
                
                if not success:
                    raise
            except:
                print_out(PrintType.ERROR, f'{file}, line {i}, {line}')
                raise
    # if expect_out_empty and len(output_contains)==0:
    #     if len(tasks_derived_all) != 0: raise
    # else:
    #     output_not_contains = set(output_contains) - set(tasks_derived_all)
    #     if len(output_not_contains) > 0:
    #         for output in output_not_contains:
    #             out_print(PrintType.ERROR, f'Fail to reason out: {output.sentence}')
    #         raise
    

class TEST_Examples_Single_NAL1(unittest.TestCase):
    '''Examples files in `application`.'''

    # def test_revision_0(self):
    #     print('\n')
    #     file = examples_path/'single_step/nal1.0.nal'
    #     print_filename(file.name)
    #     run_file(file)

    def test_deduction_0(self):
        print('\n')
        file = examples_path/'single_step/nal5/nal5.29.nal'
        print_filename(file.name)
        run_file(file)

if __name__ == '__main__':

    test_classes_to_run = [
        TEST_Examples_Single_NAL1
    ]

    loader = unittest.TestLoader()

    suites = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites.append(suite)
        
    suites = unittest.TestSuite(suites)

    runner = unittest.TextTestRunner()
    results = runner.run(suites)
