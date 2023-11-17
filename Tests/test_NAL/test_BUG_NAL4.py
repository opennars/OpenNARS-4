from pynars import NARS, Narsese
import unittest

from pynars.NARS.DataStructures import Bag, Task, Concept, Table
from pynars.NARS.DataStructures._py.Link import TaskLink, TermLink
from pynars.Narsese import Judgement, Term, Statement, Copula, Truth   

from pathlib import Path
from pynars.Narsese import Compound, Connector
from pynars.NAL.MetaLevelInference.VariableSubstitution import *
from pynars.Narsese import VarPrefix, Variable
from pynars.NARS.RuleMap import RuleMap
from pynars.NARS import Reasoner as Reasoner

import Tests.utils_for_test as utils_for_test
from Tests.utils_for_test import *
from pynars.NARS.RuleMap import Interface_TransformRules

# utils_for_test.rule_map = RuleMap_v2()



class TEST_BUG_NAL4(unittest.TestCase):
    def setUp(self):
        nars.reset()
        
    ''''''
    def test_bug_0(self):
        '''
        <bird --> animal>. %1.00;0.90%
        (/, ?0, bird, _)
        
        |-
        <(/, ?0, animal, _) --> (/, ?0, bird, _)>.
        '''

        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '<bird --> animal>. %1.00;0.90%', 
            '(/, tree, bird, _).', 
            'bird.', is_belief_term=True)
        tasks_derived = [rule(task, belief.term, task_link, term_link) for rule in rules]
        self.assertTrue(
            output_contains(tasks_derived, '<(/, tree, animal, _) --> (/, tree, bird, _)>. %1.00;0.81%')
        )

        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '<bird --> animal>. %1.00;0.90%', 
            '(/, ?0, bird, _).', 
            'bird.', is_belief_term=True)
        if rules is not None:
            tasks_derived = [rule(task, belief.term, task_link, term_link) for rule in rules]
            self.assertFalse(
                output_contains(tasks_derived, '<(/, ?0, animal, _) --> (/, ?0, bird, _)>. %1.00;0.81%')
            )
        
        pass

    


if __name__ == '__main__':

    test_classes_to_run = [
        TEST_BUG_NAL4
    ]

    loader = unittest.TestLoader()

    suites = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites.append(suite)
        
    suites = unittest.TestSuite(suites)

    runner = unittest.TextTestRunner()
    results = runner.run(suites)