import unittest

from pynars.NAL.MetaLevelInference.VariableSubstitution import *
from pynars.NARS.RuleMap import RuleMap

import Tests.utils_for_test as utils_for_test
from Tests.utils_for_test import *

utils_for_test.engine = RuleMap()


class TEST_NAL8(unittest.TestCase):
    ''''''
    def test_0_0(self):
        '''
        nal8.1.0.nal

        '********** [01 + 03 -> 10]: 

        'The goal is to make t001 opened.
        <{t001} --> [opened]>! %1.00;0.90%

        'If the robot hold t002, then go to t001 and open t001, then t001 will be opened. 
        <(&/,<(*,SELF,{t002}) --> hold>,<(*,SELF,{t001}) --> at>,<(*,{t001}) --> ^open>) =/> <{t001} --> [opened]>>. %1.00;0.90%

        20

        ''outputMustContain('(&/,<(*,SELF,{t002}) --> hold>,<(*,SELF,{t001}) --> at>,(^open,{t001}))! %1.00;0.81%')
        ' working in GUI but not in testcase, maybe the following string needs some escapes? but where?
        '''
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '<{t001} --> [opened]>! %1.00;0.90%',
            '<(&/,<(*,SELF,{t002}) --> hold>,<(*,SELF,{t001}) --> at>,<(*,{t001}) --> ^open>) =/> <{t001} --> [opened]>>. %1.00;0.90%',
            '<{t001} --> [opened]>.'
        )

        tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 

        self.assertTrue(
            output_contains(tasks_derived, '(&/,<(*,SELF,{t002}) --> hold>,<(*,SELF,{t001}) --> at>,(^open,{t001}))! %1.00;0.81%')
        )


    def test_0_1(self):
        '''
        nal8.1.3.nal

        'The goal for the robot is to make t002 reachable. 
        <(*,SELF,{t002}) --> reachable>! %1.00;0.90%

        'If item 1 is on item 2 and the robot is also at item 2 at the same time, the robot will be able to reach item 1. 
        <(&|,<(*,{t002},#2) --> on>,<(*,SELF,#2) --> at>)=|><(*,SELF,{t002}) --> reachable>>. %1.00;0.90%

        10

        'The goal is to make the robot at #1 and t002 is on #1 at the same time
        ''outputMustContain('(&|,<(*,SELF,#1) --> at>,<(*,{t002},#1) --> on>)!  %1.00;0.81%')
        '''
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '<(*,SELF,{t002}) --> reachable>! %1.00;0.90%',
            '<(&|,<(*,{t002},#2) --> on>,<(*,SELF,#2) --> at>)=|><(*,SELF,{t002}) --> reachable>>. %1.00;0.90%',
            '<(*,SELF,{t002}) --> reachable>.'
        )

        tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 

        self.assertTrue(
            output_contains(tasks_derived, '(&|,<(*,SELF,#1) --> at>,<(*,{t002},#1) --> on>)! %1.00;0.81%')
        )


    def test_0_1_var(self):
        '''
        nal8.1.3.nal

        'The goal for the robot is to make t002 reachable. 
        <(*,SELF,{t002}) --> reachable>! %1.00;0.90%

        'If item 1 is on item 2 and the robot is also at item 2 at the same time, the robot will be able to reach item 1. 
        <(&|,<(*,$1,#2) --> on>,<(*,SELF,#2) --> at>)=|><(*,SELF,$1) --> reachable>>. %1.00;0.90%

        10

        'The goal is to make the robot at #1 and t002 is on #1 at the same time
        ''outputMustContain('(&|,<(*,SELF,#1) --> at>,<(*,{t002},#1) --> on>)! :!0: %1.00;0.73%')
        '''
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '<(*,SELF,{t002}) --> reachable>! %1.00;0.90%',
            '<(&|,<(*,$1,#2) --> on>,<(*,SELF,#2) --> at>)=|><(*,SELF,$1) --> reachable>>. %1.00;0.90%',
            '<(*,SELF,{t002}) --> reachable>.'
        )

        tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 

        self.assertTrue(
            output_contains(tasks_derived, '(&|,<(*,SELF,#1) --> at>,<(*,{t002},#1) --> on>)! :!0: %1.00;0.73%')
        )

    def test_0_2_var(self):
        '''
        nal8.1.4.nal

        '********** [07 + 14 -> 15]:

        't002 is on t003 now. 
        <(*,{t002},{t003}) --> on>. :|: 

        'The goal is to make t002 on #1 and #1 is at the robot at same time
        (&|,<(*,{t002},{t003}) --> on>,<(*,{t003},SELF) --> at>)! 

        350

        'The goal maybe to make t003 at the robot
        ''outputMustContain('<(*,{t003},SELF) --> at>! %1.00;0.43%')
        '''
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '<(*,{t002},{t003}) --> on>. :|:',
            '(&|,<(*,{t002},{t003}) --> on>,<(*,{t003},SELF) --> at>)!',
            '<(*,{t002},{t003}) --> on>.'
        )

        tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 

        self.assertTrue(
            output_contains(tasks_derived, '<(*,{t003},SELF) --> at>! %1.00;0.43%')
        )

    def test_1(self):
        '''
        '********** [10 -> 11]:

        'The goal is to hold t002, then arrive t001 and open t001
        (&/,<(*,SELF,{t002}) --> hold>,<(*,SELF,{t001}) --> at>,(^open,{t001}))!

        10

        'The goal is to hold t002
        ''outputMustContain('<(*,SELF,{t002}) --> hold>! %1.00;0.81%')
        '''

if __name__ == '__main__':

    test_classes_to_run = [
        TEST_NAL8
    ]

    loader = unittest.TestLoader()

    suites = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites.append(suite)
        
    suites = unittest.TestSuite(suites)

    runner = unittest.TextTestRunner()
    results = runner.run(suites)