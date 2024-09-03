from opennars.Narsese import Budget
import unittest

from opennars.NARS.DataStructures import Bag, Task
from opennars.Narsese import Judgement, Term, Statement, Copula, Truth   
from opennars import Narsese
from opennars.NARS.DataStructures import Concept
from opennars.Narsese import Copula
from opennars.NARS.RuleMap import RuleMap
from opennars.NARS.RuleMap.RuleMap import CommonId
from opennars.NARS.DataStructures import LinkType

class TEST_RuleMap_v2(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName=methodName)
    
    def test_0(self):
        rulemap = RuleMap(False)
        rulemap.build(False)
        rulemap.draw(show_labels=False)
        pass



if __name__ == '__main__':
    unittest.main()
