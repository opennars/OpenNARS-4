import NARS
import unittest

from opennars.NARS.DataStructures import Bag
from opennars.NARS.DataStructures._py.Concept import Concept
from opennars.NARS.DataStructures._py.Memory import Memory

from opennars.NARS.InferenceEngine import GeneralEngine
import Narsese


class TEST_InferenceEngine(unittest.TestCase):

    def test_validation(self):
        ''''''
        engine = GeneralEngine()
        line = '<robin-->bird>. %0.5;0.5%'
        task = Narsese.parser.parse(line)
        concept = Concept(task.term, task.budget)
        concept.accept(task)
        
        line = '<robin-->bird>. %0.7;0.7%'
        task = Narsese.parser.parse(line)
        concept.accept(task)
        
        line = '<robin-->bird>. %0.9;0.9%'
        task = Narsese.parser.parse(line)
        concept.accept(task)
        task1 = task

        line = '<bird-->animal>. %0.9;0.9%'
        task = Narsese.parser.parse(line)
        task2 = task

        belief = concept.get_belief()
        self.assertFalse(engine.match(task1, belief))
        self.assertTrue(engine.match(task2, belief))

        
        pass

        

if __name__ == '__main__':

    test_classes_to_run = [
        TEST_InferenceEngine
    ]

    loader = unittest.TestLoader()

    suites = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites.append(suite)
        
    suites = unittest.TestSuite(suites)

    runner = unittest.TextTestRunner()
    results = runner.run(suites)
