import NARS
import unittest

from pynars.NARS.DataStructures import Bag, Task, Concept
from pynars.Narsese import Judgement, Term, Statement, Copula, Truth   

from pathlib import Path
import Narsese

from pynars.utils.Print import print_out, PrintType, print_filename

examples_path = Path(__file__).parent/'examples'
single_step_path = examples_path/'single_step'
multi_step_path = examples_path/'multi_step'
application_step_path = examples_path/'application'
stability_step_path = examples_path/'stability'

'''methods'''


def parse_file(file: str):
    with open(file, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        i += 1
        line = line.strip(' \n')
        if line.startswith("//"):
            continue
        elif line.startswith("'''expect.outEmpty"):
            pass # TODO: check the outputs
            continue
        elif line.startswith("''"):
            if line.startswith("''outputMustContain('"):
                line = line[len("''outputMustContain('"):].rstrip("')\n")
                if len(line) == 0: continue
                try:
                    content_check = Narsese.parser.parse(line) # TODO: check the outputs
                except:
                    print_out(PrintType.ERROR, f'{file}, line {i}, {line}')
                    raise
            continue
        elif line.startswith("'"):
            continue
        elif line.isdigit():
            n_cycle = int(line)
            print_out(PrintType.INFO, f'Run {n_cycle} cycles.')

        else:
            line = line.rstrip(' \n')
            if len(line) == 0:
                continue
            # content = Narsese.parser.parse(line)
            try:
                content = Narsese.parser.parse(line) # TODO: check the outputs
                print_out(PrintType.IN, str(content.sentence), *content.budget)
            except:
                print_out(PrintType.ERROR, f'{file}, line {i}, {line}')
                raise



class TEST_Examples_Parse_Single(unittest.TestCase):
    '''Examples files in `single_step`.'''

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName=methodName)

    '''test'''
    def test_single_step_nal1(self):
        print('\n')
        files = list(single_step_path.glob("nal1*.nal"))
        for file in files:
            # file = Path(r'D:\Codes\py-nars\Tests\examples\single_step\nal1.2.nal')
            print_filename(file.name)
            parse_file(file)
            
            # break

    def test_single_step_nal2(self):
        print('\n')
        files = list(single_step_path.glob("nal2*.nal"))
        for file in files:
            # file = Path(r'D:\Codes\py-nars\Tests\examples\single_step\nal2.8.nal')
            print_filename(file.name)
            parse_file(file)
            # break
    def test_single_step_nal3(self):
        print('\n')
        files = list(single_step_path.glob("nal3*.nal"))
        for file in files:
            # file = Path(r'D:\Codes\py-nars\Tests\examples\single_step\nal2.8.nal')
            print_filename(file.name)
            parse_file(file)

    def test_single_step_nal4(self):
        print('\n')
        files = list(single_step_path.glob("nal4*.nal"))
        for file in files:
            # file = Path(r'D:\Codes\py-nars\Tests\examples\single_step\nal2.8.nal')
            print_filename(file.name)
            parse_file(file)

    def test_single_step_nal5(self):
        print('\n')
        files = list(single_step_path.glob("nal5*.nal"))
        for file in files:
            # file = Path(r'D:\Codes\py-nars\Tests\examples\single_step\nal5.19.nal')
            print_filename(file.name)
            parse_file(file)
            # break

    def test_single_step_nal6(self):
        print('\n')
        files = list(single_step_path.glob("nal6*.nal"))
        for file in files:
            # file = Path(r'D:\Codes\py-nars\Tests\examples\single_step\nal6.24.nal')
            print_filename(file.name)
            parse_file(file)

    def test_single_step_nal7(self):
        print('\n')
        files = list(single_step_path.glob("nal7*.nal"))
        for file in files:
            # file = Path(r'D:\Codes\py-nars\Tests\examples\single_step\nal2.8.nal')
            print_filename(file.name)
            parse_file(file)

    def test_single_step_nal8(self):
        print('\n')
        files = list(single_step_path.glob("nal8*.nal"))
        for file in files:
            # file = Path(r'D:\Codes\py-nars\Tests\examples\single_step\nal2.8.nal')
            print_filename(file.name)
            parse_file(file)

    def test_single_step_nal9(self):
        print('\n')
        files = list(single_step_path.glob("nal9*.nal"))
        for file in files:
            # file = Path(r'D:\Codes\py-nars\Tests\examples\single_step\nal2.8.nal')
            print_filename(file.name)
            parse_file(file)

    def test_single_step_nal9_4(self):
        print('\n')
        files = list(single_step_path.glob("nal9.4.nal"))
        for file in files:
            # file = Path(r'D:\Codes\py-nars\Tests\examples\single_step\nal2.8.nal')
            print_filename(file.name)
            parse_file(file)

    def test_others(self):
        print('\n')
        files = [set(single_step_path.glob(f"nal{i}*.nal")) for i in range(1,10)]
        files = set.union(*files)
        files = set(single_step_path.glob(f"*.nal")) - files
        for file in files:
            # file = Path(r'D:\Codes\py-nars\Tests\examples\single_step\nal2.8.nal')
            print_filename(file.name)
            parse_file(file)

class TEST_Examples_Parse_Multi(unittest.TestCase):
    '''Examples files in `multi_step`.'''

    def test_multi_step_nal(self):
        print('\n')
        files = list(multi_step_path.glob("*.nal"))
        for file in files:
            # file = Path(r'D:\Codes\py-nars\Tests\examples\single_step\nal2.8.nal')
            print_filename(file.name)
            parse_file(file)

class TEST_Examples_Parse_Application(unittest.TestCase):
    '''Examples files in `application`.'''

    def test_multi_step_nal(self):
        print('\n')
        files = list(application_step_path.glob("*.nal"))
        for file in files:
            # file = Path(r'D:\Codes\py-nars\Tests\examples\single_step\nal2.8.nal')
            print_filename(file.name)
            parse_file(file)

class TEST_Examples_Parse_Stability(unittest.TestCase):
    '''Examples files in `application`.'''

    def test_multi_step_nal(self):
        print('\n')
        files = list(stability_step_path.glob("*.nal"))
        for file in files:
            # file = Path(r'D:\Codes\py-nars\Tests\examples\single_step\nal2.8.nal')
            print_filename(file.name)
            parse_file(file)

if __name__ == '__main__':

    test_classes_to_run = [
        TEST_Examples_Parse_Stability,
        TEST_Examples_Parse_Single,
        TEST_Examples_Parse_Multi,
        TEST_Examples_Parse_Application,
    ]

    loader = unittest.TestLoader()

    suites = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites.append(suite)
        
    suites = unittest.TestSuite(suites)

    runner = unittest.TextTestRunner()
    results = runner.run(suites)


