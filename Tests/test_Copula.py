from opennars.Narsese import Budget
import unittest

from opennars.NARS.DataStructures import Bag, Task
from opennars.Narsese import Judgement, Term, Statement, Copula, Truth   
import Narsese
from opennars.NARS.DataStructures import Concept
from opennars.Narsese import Copula

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
