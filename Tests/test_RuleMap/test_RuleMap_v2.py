from Narsese import Budget
import unittest

from NARS.DataStructures import Bag, Task
from Narsese import Judgement, Term, Statement, Copula, Truth   
import Narsese
from NARS.DataStructures import Concept
from Narsese import Copula
from NARS.RuleMap import RuleMap_v2
from NARS.RuleMap.RuleMap_v2 import CommonId
from NARS.DataStructures import LinkType

class TEST_RuleMap_v2(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName=methodName)
    
    def test_0(self):
        rulemap = RuleMap_v2(False)
        rulemap.build(False)
        rulemap.draw(show_labels=False)
        pass



if __name__ == '__main__':
    unittest.main()
