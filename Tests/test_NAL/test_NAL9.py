import unittest

from pynars.NAL.MetaLevelInference.VariableSubstitution import *
from pynars.NARS.RuleMap import RuleMap

import Tests.utils_for_test as utils_for_test
from Tests.utils_for_test import *
from pynars.NAL.MentalOperation import execute

nars = utils_for_test.nars

class TEST_NAL9(unittest.TestCase):
    def setUp(self):
        nars.reset()

    ''''''
    def test_anticipate_0(self):
        '''
        <<(&/,<a --> A>,+10) =/> <b --> B>>.
        'making it observable:
        <b --> B>.
        'ok start:
        <a --> A>. :|:
        10
        ''outputMustContain('(^anticipate,{SELF},<b --> B>). :!0: %1.00;0.90%')
        '''


    def test_believe_0(self):
        '''
        <a --> b>.
        'ok, being aware needs attention, so lets ask NARS about it:
        <a --> b>?
        'ok this concept should now be important enough for it so that NARS now knows 
        2
        ''outputMustContain('(^believe,{SELF},<a --> b>,TRUE). :!0: %1.00;0.90%')
        '''
        # rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
        #     '<(*,John,key_101) --> hold>. :|: %1.00;0.90%',
        #     '<<(*,John,key_101) --> hold> =/> <(*,John,room_101) --> enter>>. %1.00;0.90%',
        #     '<(*,John,key_101) --> hold>.'
        # )
        # tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 
        # self.assertTrue(
        #     output_contains(tasks_derived, '<(*,John,room_101) --> enter>. :|: %1.00;0.81%')
        # )
        # pass

    def test_believe_1(self):
        '''
        (^believe,{SELF},<cat --> animal>,FALSE)!
        10
        ''outputMustContain('<cat --> animal>. :!0: %0.00;0.90%')
        '''
        
        tasks_derived = process_two_premises(
            '(^believe,{SELF},<cat --> animal>,FALSE)!',
            None,
            10
        )
        self.assertTrue(
            output_contains(tasks_derived, '<cat --> animal>. :!0: %0.00;0.90%')
        )
        pass

    def test_doubt_0(self):
        '''
        <a --> b>. %1.00;0.90%
        20
        (^doubt,{SELF},<a --> b>)! %1.00;0.90%
        20
        <a --> b>?
        ''outputMustContain('<a --> b>. %1.00;0.45%')

        '''
        process_two_premises(
            '<a --> b>. %1.00;0.90%',
            '(^doubt,{SELF},<a --> b>)! %1.00;0.90%',
            100
        )

        nars.reset()
        
        tasks_derived = process_two_premises(
            '<a --> b>?',
            None,
            100
        )

        self.assertTrue(
            output_contains(tasks_derived, '<a --> b>. %1.00;0.45%')
        )


if __name__ == '__main__':

    test_classes_to_run = [
        TEST_NAL9
    ]

    loader = unittest.TestLoader()

    suites = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites.append(suite)
        
    suites = unittest.TestSuite(suites)

    runner = unittest.TextTestRunner()
    results = runner.run(suites)