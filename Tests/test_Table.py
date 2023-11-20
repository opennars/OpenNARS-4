import NARS
import unittest

from pynars.NARS.DataStructures import Bag, Task, Concept, Table
from pynars.Narsese import Judgement, Term, Statement, Copula, Truth   

from pathlib import Path
import Narsese
from pynars.Narsese import Compound, Connector


class TEST_Table(unittest.TestCase):

    def test_index(self):
        ''''''
        table = Table(100)

        line = '<robin-->bird>. %0.5;0.5%'
        task = Narsese.parser.parse(line)
        table.add(task, task.sentence.truth.e)
        task1 = task
        
        line = '<robin-->bird>. %0.7;0.7%'
        task = Narsese.parser.parse(line)
        table.add(task, task.sentence.truth.e)

        line = '<robin-->bird>. %0.9;0.9%'
        task = Narsese.parser.parse(line)
        table.add(task, task.sentence.truth.e)
        task2 = task

        line = '<robin-->bird>. %0.9;0.9%'
        task = Narsese.parser.parse(line)
        table.add(task, task.sentence.truth.e)

        self.assertEqual(table.first(), task2)
        self.assertEqual(table.last(), task1)
        pass

        

if __name__ == '__main__':

    test_classes_to_run = [
        TEST_Table
    ]

    loader = unittest.TestLoader()

    suites = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites.append(suite)
        
    suites = unittest.TestSuite(suites)

    runner = unittest.TextTestRunner()
    results = runner.run(suites)
