from pynars.Narsese import Budget
import unittest

from pynars.NARS.DataStructures import Bag, Task
from pynars.Narsese import Judgement, Term, Statement, Copula, Truth   
from pynars import Narsese
from pynars.NARS.DataStructures import Concept

class TEST_Concept(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName=methodName)

    def test_accept_task(self):
        ''''''
        # engine = Engine()

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

        line = '<robin-->bird>. %0.9;0.9%'
        task = Narsese.parser.parse(line)
        concept.accept(task)
        task1 = task
        
        self.assertEqual(len(concept.belief_table), 4)

        belief = concept.get_belief()
        self.assertEqual(task1, belief)
        pass


if __name__ == '__main__':
    unittest.main()
