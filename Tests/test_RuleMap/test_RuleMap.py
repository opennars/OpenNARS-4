from pynars.Narsese import Budget
import unittest

from pynars.NARS.DataStructures import Bag, Task, Concept
from pynars.Narsese import Judgement, Term, Statement, Copula, Truth   

from pynars.NARS.RuleMap import RuleMap_v1

class TEST_RuleMap(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName=methodName)
        self.rule_map = RuleMap_v1()

    def test_1(self):
        rule_map = self.rule_map



if __name__ == '__main__':
    unittest.main()


