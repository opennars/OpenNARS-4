from pynars.utils.RuleLUT import RuleLUT, Any

from pynars.NARS.DataStructures._py.Link import LinkType
from pynars.NARS.RuleMap import Interface_SyllogisticRules, RuleMap_v2
from pynars.Narsese import Budget
import unittest

from pynars.NARS.DataStructures import Bag, Task, Concept
from pynars.Narsese import Judgement, Term, Statement, Copula, Truth   

from pynars.utils.SparseLUT import SparseLUT

from pynars.NARS.RuleMap.RuleMap_v2 import CommonId

class TEST_RuleLUT(unittest.TestCase):
    
    def test_0(self):
        '''
        (3,3,3)
        [
            ([0, 1, 2], "r1"),
            ([0, 1, 1], "r2"),
            ([Any, 0, 1], "r3"),
            ([2, [0,1], [1,2]], "r4"),
            ([2, [1,2], [2,3]], "r5"),
        ]
        [
            [0, 1, 2],
            [0, 1, 1],
            [[0,1,2], 0, 1],
            [2, [0,1], [1,2]],
            [2, [1,2], [2,3]],
        ]
        r1
            [0, 1, 2],
        r2
            [0, 1, 1],
        r3
            [0, 0, 1],
            [1, 0, 1],
            [2, 0, 1],
        r4
            [2, 0, 1],
            [2, 0, 2],
            [2, 1, 1],
            [2, 1, 2],
        r5
            [2, 1, 2],
            [2, 1, 3],
            [2, 2, 2],
            [2, 2, 3],


        [0, 1, 2], r1
        [0, 1, 1], r2
        [0, 0, 1], r3
        [1, 0, 1], r3
        [2, 0, 1], r3, r4
        [2, 0, 2], r4
        [2, 1, 1], r4
        [2, 1, 2], r4, r5
        [2, 1, 3], r5
        [2, 2, 2], r5
        [2, 2, 3], r5
        ]
        '''
        lut = RuleLUT((3, 3, 4))
        lut.add("r1", [0, 1, 2])
        lut.add("r2", [0, 1, 1])
        lut.add("r3", [Any, 0, 1])
        lut.add("r4", [2, [0,1], [1,2]])
        lut.add("r5", [2, [0,2], [2,3]])
        lut.build()
        
        # self.assertEqual(lut[0, 1, 2], ["r1", "r4", "r5"])
        # self.assertEqual(lut[0, 1, 1], ["r1", "r4", "r5"])
        # self.assertEqual(lut[0, 0, 1], ["r1", "r4", "r5"])
        # self.assertEqual(lut[2, 0, 1], ["r1", "r4", "r5"])
        # self.assertEqual(lut[2, 0, 2], ["r1", "r4", "r5"])
        # self.assertEqual(lut[2, 1, 1], ["r1", "r4", "r5"])
        # self.assertEqual(lut[2, 1, 2], ["r1", "r4", "r5"])
        # self.assertEqual(lut[2, 1, 3], ["r1", "r4", "r5"])
        # self.assertEqual(lut[2, 2, 2], ["r1", "r4", "r5"])
        # self.assertEqual(lut[2, 2, 3], ["r1", "r4", "r5"])
        pass

    

if __name__ == '__main__':

    test_classes_to_run = [
        TEST_RuleLUT
    ]

    loader = unittest.TestLoader()

    suites = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites.append(suite)
        
    suites = unittest.TestSuite(suites)

    runner = unittest.TextTestRunner()
    results = runner.run(suites)
