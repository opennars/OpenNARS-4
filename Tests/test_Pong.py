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


class TEST_PONG(unittest.TestCase):

    def test_0(self):
        '''
        '''
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '(&|, dist_x_zero, dist_y_zero)! %1.00;0.90%',
            'dist_x_zero.',
            'dist_x_zero.', is_belief_term=True)

        tasks_derived = engine.inference(task, None, belief.term, task_link, term_link, rules)
        self.assertTrue(
            output_contains(tasks_derived, 'dist_x_zero! %1.00;0.81%')
        )

        pass

    def test_1(self):
        '''
        '''
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            'dist_y_decrease!',
            '<(&/, <(*, ball, {SELF})-->[left]>, (^move, right)) =/> dist_y_decrease>. %1.00;0.90%',
            'dist_y_decrease.')

        tasks_derived = engine.inference(task, belief, belief.term, task_link, term_link, rules)
        self.assertTrue(
            output_contains(tasks_derived, '(&/, <(*, ball, {SELF})-->[left]>, (^move, right))! %1.00;0.81%')
        )
        pass

    def test_2(self):
        '''
        '''
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '<{SELF}-->[good]>!',
            '<<(*, left)-->^move>=/><{SELF}-->[good]>>.',
            '<{SELF}-->[good]>.')

        tasks_derived = engine.inference(task, belief, belief.term, task_link, term_link, rules)
        self.assertTrue(
            output_contains(tasks_derived, '<(*, left)-->^move>! %1.00;0.81%')
        )

        pass


if __name__ == '__main__':

    test_classes_to_run = [
        TEST_PONG
    ]

    loader = unittest.TestLoader()

    suites = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites.append(suite)

    suites = unittest.TestSuite(suites)

    runner = unittest.TextTestRunner()
    results = runner.run(suites)
