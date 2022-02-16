import NARS
import unittest

from pynars.NARS.DataStructures import Bag, Task, Memory, Concept
from pynars.NARS.DataStructures._py.Concept import Concept
from pynars.Narsese import Judgement, Term, Statement, Copula, Truth   

from pathlib import Path
import Narsese
from pynars.Narsese import Compound, Connector


def test_conceptualize(self):
    pass

class TEST_Memory(unittest.TestCase):

    def test_conceptualize(self):
        ''''''
        nars = NARS.Reasoner_3_0_4(100, 100)

        line = '<bird-->animal>.'
        task = Narsese.parser.parse(line)
        Concept._conceptualize(nars.memory.concepts, task.term, task.budget)

        line = '<bird-->animal>.'
        Narsese.parser.parse(line)
        Concept._conceptualize(nars.memory.concepts, task.term, task.budget)

    def test_accept_1(self):
        ''''''
        nars = NARS.Reasoner_3_0_4(100, 100)

        line = '((&&, <robin-->bird>, <bird-->animal>) ==> <robin-->animal>).'
        task = Narsese.parser.parse(line)
        term1 = Term('robin')
        term2 = Term('bird')
        term3 = Term('animal')
        term4 = Statement(term1, Copula.Inheritance, term2)
        term5 = Statement(term2, Copula.Inheritance, term3)
        term6 = Statement(term1, Copula.Inheritance, term3)
        term7 = Compound(Connector.Conjunction, term4, term5)
        term8 = Statement(term7, Copula.Implication, term6)
        set1 = set((term1, term2, term3, term4, term5, term6, term7))
        set2 = set1 | set((term8,))
        term = task.term
        self.assertEquals(len(term._components), 7)
        self.assertEquals(len(term.sub_terms), 8)
        self.assertEquals(term._components, set1)
        self.assertEquals(term.sub_terms, set2)
        
        nars.memory.accept(task)

    def test_accept_2(self):
        ''''''
        nars = NARS.Reasoner_3_0_4(100, 100)

        line = '<bird-->animal>.'
        task = Narsese.parser.parse(line)
        nars.memory.accept(task)

        line = '<bird-->animal>.'
        task = Narsese.parser.parse(line)
        nars.memory.accept(task)
        
    def test_accept_3(self):
        ''''''
        memory = Memory(100, 100)

        line = '<robin-->bird>. %0.5;0.5%'
        task = Narsese.parser.parse(line)
        memory.accept(task)
        
        line = '<bird-->animal>. %0.7;0.7%'
        task = Narsese.parser.parse(line)
        memory.accept(task)
        
        self.assertEqual(len(memory), 5)

        pass


if __name__ == '__main__':

    test_classes_to_run = [
        TEST_Memory
    ]

    loader = unittest.TestLoader()

    suites = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites.append(suite)
        
    suites = unittest.TestSuite(suites)

    runner = unittest.TextTestRunner()
    results = runner.run(suites)
