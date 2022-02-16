from typing import List
import NARS
import unittest

from pynars.NARS.DataStructures import Bag, Task, Concept
from pynars.Narsese import Judgement, Term, Statement, Copula, Truth   

from pathlib import Path
import Narsese

from pynars.utils.Print import out_print, PrintType, print_filename

examples_path = Path(__file__).parent/'examples'

def run_file(file: str):
    nars = NARS.Reasoner_3_0_4(100, 100)

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
                    out_print(PrintType.ERROR, f'{file}, line {i}, {line}')
                    raise
            continue
        elif line.startswith("'"):
            continue
        elif line.isdigit():
            n_cycle = int(line)
            out_print(PrintType.INFO, f'Run {n_cycle} cycles.')
            for _ in range(n_cycle):
                tasks_derived = nars.cycle()
                tasks_derived_all.extend(tasks_derived)
                for task in tasks_derived: out_print(PrintType.OUT, str(task.sentence), *task.budget)

        else:
            line = line.rstrip(' \n')
            if len(line) == 0:
                continue
            # content = Narsese.parser.parse(line)
            try:
                success, task, _ = nars.input_narsese(line, go_cycle=False)
                if success: out_print(PrintType.IN, task.sentence, *task.budget)
                else: out_print(PrintType.ERROR, f'Invalid input! Failed to parse: {line}')

                tasks_derived = nars.cycle()
                tasks_derived_all.extend(tasks_derived)
                for task in tasks_derived: out_print(PrintType.OUT, str(task.sentence), *task.budget)
                if not success:
                    raise
            except:
                out_print(PrintType.ERROR, f'{file}, line {i}, {line}')
                raise
    if expect_out_empty and len(output_contains)==0:
        if len(tasks_derived_all) != 0: raise
    else:
        output_not_contains = set(output_contains) - set(tasks_derived_all)
        if len(output_not_contains) > 0:
            for output in output_not_contains:
                out_print(PrintType.ERROR, f'Fail to reason out: {output.sentence}')
            raise
    

class TEST_Examples_Single_NAL1(unittest.TestCase):
    '''Examples files in `application`.'''

    # def test_revision_0(self):
    #     print('\n')
    #     file = examples_path/'single_step/nal1.0.nal'
    #     print_filename(file.name)
    #     run_file(file)

    def test_deduction_0(self):
        print('\n')
        file = examples_path/'single_step/nal1/nal1.0.nal'
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
