from pynars.Narsese import Budget
import unittest

from pynars.NARS.DataStructures import Bag, Task
from pynars.Narsese import Judgement, Term, Statement, Copula, Truth   
from pynars import Narsese
from pynars.NARS.DataStructures import Concept
from pynars.Narsese import Copula
from pynars.NARS.RuleMap import RuleMap
from pynars.NARS.RuleMap.RuleMap import CommonId
from pynars.NARS.DataStructures import LinkType

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
