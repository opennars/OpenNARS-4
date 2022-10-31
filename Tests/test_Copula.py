from pynars.Narsese import Budget
import unittest

from pynars.NARS.DataStructures import Bag, Task
from pynars.Narsese import Judgement, Term, Statement, Copula, Truth   
import Narsese
from pynars.NARS.DataStructures import Concept
from pynars.Narsese import Copula

class TEST_Concept(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName=methodName)

    def test_copla_id(self):
        ''''''
        self.assertEqual(int(Copula.Inheritance), 0)
        self.assertEqual(int(Copula.Similarity), 1)
        pass


if __name__ == '__main__':
    unittest.main()
