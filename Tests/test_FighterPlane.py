from opennars import NARS, Narsese
import unittest

from opennars.NARS.DataStructures import Bag, Task, Concept, Table
from opennars.NARS.DataStructures._py.Link import TaskLink, TermLink
from opennars.Narsese import Judgement, Term, Statement, Copula, Truth   

from pathlib import Path
from opennars.Narsese import Compound, Connector
from opennars.NAL.MetaLevelInference.VariableSubstitution import *
from opennars.Narsese import VarPrefix, Variable
from opennars.NARS.RuleMap import RuleMap
from opennars.NARS import Reasoner as Reasoner

import Tests.utils_for_test as utils_for_test
from Tests.utils_for_test import *
from opennars.NARS.RuleMap import Interface_TransformRules

# utils_for_test.rule_map = RuleMap_v2()



class TEST_FighterPlane(unittest.TestCase):
    ''''''

    def test_0(self):
        '''
        task: $0.800;0.500;0.950$ <{enemy}-->[left]>. :\: %1.000;0.900%
        belief: $0.800;0.500;0.950$ <{enemy}-->[ahead]>. :\: %1.000;0.900%
        concept: {enemy}
        '''
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '$0.800;0.500;0.950$ <{enemy}-->[left]>. :\: %1.000;0.900%', 
            '$0.800;0.500;0.950$ <{enemy}-->[ahead]>. :\: %1.000;0.900%', 
            '{enemy}.')
        tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules]
        # self.assertTrue(
        #     output_contains(tasks_derived, '<swan --> (&,bird,swimmer)>. %0.72;0.81%')
        # )
        pass



if __name__ == '__main__':

    test_classes_to_run = [
        TEST_FighterPlane
    ]

    loader = unittest.TestLoader()

    suites = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites.append(suite)
        
    suites = unittest.TestSuite(suites)

    runner = unittest.TextTestRunner()
    results = runner.run(suites)