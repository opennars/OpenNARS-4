from re import L
import unittest

from pynars.NAL.MetaLevelInference.VariableSubstitution import *
from pynars.NARS.RuleMap import RuleMap

import Tests.utils_for_test as utils_for_test
from Tests.utils_for_test import *

# utils_for_test.engine = RuleMap()


class TEST_NAL8(unittest.TestCase):
    def setUp(self):
        nars.reset()

    ''''''
    def test_1_0(self):
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
        tasks_derived = process_two_premises(
            '<{t001} --> [opened]>! %1.00;0.90%',
            '<(&/,<(*,SELF,{t002}) --> hold>,<(*,SELF,{t001}) --> at>,<(*,{t001}) --> ^open>) =/> <{t001} --> [opened]>>. %1.00;0.90%',
            10
        )

        self.assertTrue(
            output_contains(tasks_derived, '(&/,<(*,SELF,{t002}) --> hold>,<(*,SELF,{t001}) --> at>,(^open,{t001}))! %1.00;0.81%')
        )


    def test_1_1(self):
        '''
        nal8.1.1.nal

        '********** [10 -> 11]:

        'The goal is to hold t002, then arrive t001 and open t001
        (&/,<(*,SELF,{t002}) --> hold>,<(*,SELF,{t001}) --> at>,(^open,{t001}))! %1.00;0.90%

        10

        'The goal is to hold t002
        ''outputMustContain('<(*,SELF,{t002}) --> hold>! %1.00;0.81%')
        '''
        tasks_derived = process_two_premises(
            '(&/,<(*,SELF,{t002}) --> hold>,<(*,SELF,{t001}) --> at>,(^open,{t001}))! %0.90;0.90%',
            None,
            100
        )

        self.assertTrue(
            output_contains(tasks_derived, '<(*,SELF,{t002}) --> hold>! %0.90;0.81%')
        )
    
    def test_1_2(self):
        '''
        nal8.1.2.nal

        '********** [12 -> 13]:

        'The goal for the robot is to make t002 reachable and then pick it. 
        (&/,<(*,SELF,{t002}) --> reachable>,(^pick,{t002}))!

        5

        'The goal for the robot is to make t002 reachable. 
        ''outputMustContain('<(*,SELF,{t002}) --> reachable>! %1.00;0.81%')
        '''
        tasks_derived = process_two_premises(
            '(&/,<(*,SELF,{t002}) --> reachable>,(^pick,{t002}))! %0.90;0.90%',
            None,
            10
        )

        self.assertTrue(
            output_contains(tasks_derived, '<(*,SELF,{t002}) --> reachable>! %0.90;0.81%')
        )


    def test_1_3(self):
        '''
        nal8.1.3.nal

        '********** [13 + 06 -> 14]:

        'The goal for the robot is to make t002 reachable. 
        <(*,SELF,{t002}) --> reachable>! 

        'If item 1 is on item 2 and the robot is also at item 2 at the same time, the robot will be able to reach item 1. 
        <(&|,<(*,{t002},#1) --> on>,<(*,SELF,#1) --> at>)=|><(*,SELF,{t002}) --> reachable>>.

        20

        'The goal is to make the robot at #1 and t002 is on #1 at the same time
        ''outputMustContain('(&|,<(*,SELF,#1) --> at>,<(*,{t002},#1) --> on>)! %1.00;0.81%')
        '''
        tasks_derived = process_two_premises(
            '<(*,SELF,{t002}) --> reachable>! %1.00;0.90%',
            '<(&|,<(*,{t002},#1) --> on>,<(*,SELF,#1) --> at>)=|><(*,SELF,{t002}) --> reachable>>.',
            0
        )

        self.assertTrue(
            output_contains(tasks_derived, '(&|,<(*,SELF,#0) --> at>,<(*,{t002},#0) --> on>)! %1.00;0.81%')
        )

    def test_1_3_var(self):
        '''
        nal8.1.3.nal

        '********** [13 + 06 -> 14]:

        'The goal for the robot is to make t002 reachable. 
        <(*,SELF,{t002}) --> reachable>! 

        'If item 1 is on item 2 and the robot is also at item 2 at the same time, the robot will be able to reach item 1. 
       <(&|,<(*,$1,#2) --> on>,<(*,SELF,#2) --> at>)=|><(*,SELF,$1) --> reachable>>.

        20

        'The goal is to make the robot at #1 and t002 is on #1 at the same time
        ''outputMustContain('(&|,<(*,SELF,#1) --> at>,<(*,{t002},#1) --> on>)! %1.00;0.81%')
        '''
        tasks_derived = process_two_premises(
            '<(*,SELF,{t002}) --> reachable>! %1.00;0.90%',
            '<(&|,<(*,$1,#2) --> on>,<(*,SELF,#2) --> at>)=|><(*,SELF,{t002}) --> reachable>>.',
            0
        )

        self.assertTrue(
            output_contains(tasks_derived, '(&|,<(*,SELF,#0) --> at>,<(*,{t002},#0) --> on>)!  %1.00;0.81%')
        )

    def test_1_4(self):
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
        tasks_derived = process_two_premises(
            '(&|,<(*,{t002},{t003}) --> on>,<(*,{t003},SELF) --> at>)!',
            '<(*,{t002},{t003}) --> on>. :|:',
            0
        )

        self.assertTrue(
            output_contains(tasks_derived, '<(*,{t003},SELF) --> at>! %1.00;0.43%')
        )


    def test_1_4_var(self):
        '''
        nal8.1.4.nal

        '********** [07 + 14 -> 15]:

        't002 is on t003 now. 
        <(*,{t002},{t003}) --> on>. :|: 

        'The goal is to make t002 on #1 and #1 is at the robot at same time
        (&|,<(*,{t002},#1) --> on>,<(*,#1,SELF) --> at>)! 

        350

        'The goal maybe to make t003 at the robot
        ''outputMustContain('<(*,{t003},SELF) --> at>! %1.00;0.43%')
        '''
        tasks_derived = process_two_premises(
            '<(*,{t002},{t003}) --> on>. :|:',
            '(&|,<(*,{t002},#1) --> on>,<(*,#1,SELF) --> at>)!',
            0
        )

        self.assertTrue(
            output_contains(tasks_derived, '<(*,{t003},SELF) --> at>! %1.00;0.43%')
        )


    def test_1_5(self):
        '''
        nal8.1.5.nal

        '********** [15 + 09 -> 16]:

        'The goal for the robot is to arrive t003. 
        <(*,SELF,{t003}) --> at>!

        'If go to somewhere, the robot will be at there.
        <(^go_to,{t003})=/><(*,SELF,{t003}) --> at>>.

        100

        'The goal is to go to t003.
        ''outputMustContain('(^go_to,{t003})! %1.00;0.81%')

        '''
        tasks_derived = process_two_premises(
            '<(*,SELF,{t003}) --> at>!',
            '<(^go_to,{t003})=/><(*,SELF,{t003}) --> at>>.',
            10
        )

        self.assertTrue(
            output_contains(tasks_derived, '(^go_to,{t003})! %1.00;0.81%')
        )


    def test_1_7(self):
        '''
        nal8.1.7.nal

        '********** [17 + 09 -> 18]

        'Now the robot is going to t003. 
        <(*,{t003}) --> ^go_to>. :|: 

        'If go to somewhere, the robor will be at there.
        <<(*,{t003}) --> ^go_to> =/> <(*,SELF,{t003}) --> at>>. 

        20

        'The robot will be at t003. 
        ''outputMustContain('<(*,SELF,{t003}) --> at>. :!5: %1.00;0.81%')

        '''
        tasks_derived = process_two_premises(
            '<(*,{t003}) --> ^go_to>. :|:',
            '<<(*,{t003}) --> ^go_to> =/> <(*,SELF,{t003}) --> at>>.',
            0
        )

        self.assertTrue(
            output_contains(tasks_derived, '<(*,SELF,{t003}) --> at>. :!5: %1.00;0.81%')
        )

    def test_1_7_var(self):
        '''
        nal8.1.7.nal

        '********** [17 + 09 -> 18]

        'Now the robot is going to t003. 
        <(*,{t003}) --> ^go_to>. :|: 

        'If go to somewhere, the robor will be at there.
        <<(*,$1) --> ^go_to> =/> <(*,SELF,$1) --> at>>. 

        20

        'The robot will be at t003. 
        ''outputMustContain('<(*,SELF,{t003}) --> at>. :!5: %1.00;0.81%')

        '''
        tasks_derived = process_two_premises(
            '<(*,{t003}) --> ^go_to>. :|:',
            '<<(*,$1) --> ^go_to> =/> <(*,SELF,$1) --> at>>.',
            0
        )

        self.assertTrue(
            output_contains(tasks_derived, '<(*,SELF,{t003}) --> at>. :!5: %1.00;0.81%')
        )
    

    def test_1_8(self):
        '''
        nal8.1.8.nal

        '********** [18 -> 19]

        'The robot was at t003. 
        <SELF --> (/,at,_,{t003})>. :\:

        6

        'The robot was at t003. 
        ''outputMustContain('<{t003} --> (/,at,SELF,_)>. :!-5: %1.00;0.90%')


        '''
        tasks_derived = process_two_premises(
            '<SELF --> (/,at,_,{t003})>. :\:',
            None,
            0
        )

        self.assertTrue(
            output_contains(tasks_derived, '<{t003} --> (/,at,SELF,_)>. :!-5: %1.00;0.90%')
        )

    def test_1_9(self):
        '''
        nal8.1.9.nal

        '********** [07 -> 20]

        't002 is on t003 now.
        <(*,{t002},{t003}) --> on>. :|:

        6

        't002 is on t003 now.
        ''outputMustContain('<{t003} --> (/,on,{t002},_)>. :!0: %1.00;0.90%')

        '''
        tasks_derived = process_two_premises(
            '<(*,{t002},{t003}) --> on>. :|:',
            None,
            0
        )

        self.assertTrue(
            output_contains(tasks_derived, '<{t003} --> (/,on,{t002},_)>. :!0: %1.00;0.90%')
        )


    def test_1_10(self):
        '''
        nal8.1.10.nal

        '********** [19 + 20 -> 21]

        'The robot was at t003.
        <{t003} --> (/,at,SELF,_)>. :\:

        't002 was on the t003. 
        <{t003} --> (/,on,{t002},_)>. :\:

        33

        'If the robot was at someting, t002 was also on it. 
        ''outputMustContain('(&&,<#1 --> (/,at,SELF,_)>,<#1 --> (/,on,{t002},_)>). :!-5: %1.00;0.81%')

        '''
        # rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
        #     '<{t003} --> (/,at,SELF,_)>. :\:',
        #     '<{t003} --> (/,on,{t002},_)>. :\:',
        #     'at.'
        # )

        # tasks_derived = engine.inference(task, belief, belief.term, task_link, term_link, rules)

        # self.assertTrue(
        #     output_contains(tasks_derived, '(^go_to,{t003})! %1.00;0.81%')
        # )
        raise


    def test_1_11(self):
        '''
        nal8.1.11.nal

        '********** [21 -> 22]

        't002 was on someting and the robot was also at it at the same time.
        (&|,<#1 --> (/,on,{t002},_)>,<#1 --> (/,at,SELF,_)>). :\:

        8

        't002 was on someting and the robot was also at it at the same time.
        ''outputMustContain('(&|,<#1 --> (/,on,{t002},_)>,<(*,SELF,#1) --> at>). :!-5: %1.00;0.90%')

        '''
        raise


    def test_1_13(self):
        '''
        nal8.1.13.nal

        '********** [23 + 06 -> 24]

        't002 is on something, and the robot is also at it at the same time. 
        (&|,<(*,{t002},#1) --> on>,<(*,SELF,#1) --> at>). :|: 

        'If item 1 is on item 2 and the robot is also at item 2 at the same time, the robot will be able to reach item 1. 
        <(&|,<(*,{t002},$2) --> on>,<(*,SELF,$2) --> at>) =|> <(*,SELF,{t002}) --> reachable>>.

        260

        'The robot is able to reach t002. 
        ''outputMustContain('<(*,SELF,{t002}) --> reachable>. :!0: %1.00;0.81%')

        '''
        # rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
        #     '(&|,<(*,{t002},#1) --> on>,<(*,SELF,#1) --> at>). :|:',
        #     '<(&|,<(*,{t002},#1) --> on>,<(*,SELF,#1) --> at>) =|> <(*,SELF,{t002}) --> reachable>>.',
        #     '(&|,<(*,{t002},#1) --> on>,<(*,SELF,#1) --> at>).'
        # )

        tasks_derived = process_two_premises(
            '(&&,A, B, D). :|:',
            '<(&&,A, B) ==> C>.',
            0
        )

        self.assertTrue(
            output_contains(tasks_derived, '<(*,SELF,{t002}) --> reachable>. :!0: %1.00;0.81%')
        )

    def test_1_13_var(self):
        '''
        nal8.1.13.nal

        '********** [23 + 06 -> 24]

        't002 is on something, and the robot is also at it at the same time. 
        (&|,<(*,{t002},#1) --> on>,<(*,SELF,#1) --> at>). :|: 

        'If item 1 is on item 2 and the robot is also at item 2 at the same time, the robot will be able to reach item 1. 
        <(&|,<(*,$1,$2) --> on>,<(*,SELF,$2) --> at>) =|> <(*,SELF,$1) --> reachable>>.

        260

        'The robot is able to reach t002. 
        ''outputMustContain('<(*,SELF,{t002}) --> reachable>. :!0: %1.00;0.81%')

        '''
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '(&|,<(*,{t002},#1) --> on>,<(*,SELF,#1) --> at>). :|:',
            '<(&|,<(*,$1,$2) --> on>,<(*,SELF,$2) --> at>) =|> <(*,SELF,$1) --> reachable>>.',
            'on.'
        )

        tasks_derived = engine.inference(task, belief, belief.term, task_link, term_link, rules)

        self.assertTrue(
            output_contains(tasks_derived, '(^go_to,{t003})! %1.00;0.81%')
        )


    def test_1_14(self):
        '''
        nal8.1.14.nal

        '********** [24 + 12 -> 25]

        'The robot is able to reach t002. 
        <(*,SELF,{t002}) --> reachable>. :|: 

        'The goal for the robot is to make t002 reachable and then pick it. 
        (&/,<(*,SELF,{t002}) --> reachable>,(^pick,{t002}))! 

        45

        'The goal maybe to pick t002. 
        ''outputMustContain('(^pick,{t002})! %1.00;0.43%')


        '''
        tasks_derived = process_two_premises(
            '(&/,<(*,SELF,{t002}) --> reachable>,(^pick,{t002}))! ',
            '<(*,SELF,{t002}) --> reachable>. :|: ',
            0
        )

        self.assertTrue(
            output_contains(tasks_derived, '(^pick,{t002})! %1.00;0.43%')
        )

    
    def test_1_16(self):
        '''
        nal8.1.16.nal

        '********** [24 + 05 -> 27]

        'The robot is able to reach t002. 
        <(*,SELF,{t002}) --> reachable>. :|:

        'If the robot reach t002 and pick it, the robot will hold t002.
        <(&/,<(*,SELF,{t002}) --> reachable>,(^pick,{t002}))=/><(*,SELF,{t002}) --> hold>>.

        1

        'If the robot pick t002, it will hold t002. 
        ''outputMustContain('<(^pick,{t002}) =/> <(*,SELF,{t002}) --> hold>>. :!0: %1.00;0.81%')

        '''
        tasks_derived = process_two_premises(
            '<(*,SELF,{t002}) --> reachable>. :|:',
            '<(&/,<(*,SELF,{t002}) --> reachable>,(^pick,{t002}))=/><(*,SELF,{t002}) --> hold>>.',
            0
        )

        self.assertTrue(
            output_contains(tasks_derived, '<(^pick,{t002}) =/> <(*,SELF,{t002}) --> hold>>. :!0: %1.00;0.81%')
        )


    def test_sequence_0(self):
        '''
        (&/, A, B, C).
        A.
        |- 
        (&/, B, C).
        '''
        # rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
        #     'A.',
        #     '(&/, A, B, C).',
        #     'A.'
        # )

        # tasks_derived = engine.inference(task, belief, belief.term, task_link, term_link, rules)
        
        # self.assertTrue(
        #     output_contains(tasks_derived, '(&/, B, C). %1.00;0.43%')
        # )

        tasks_derived = process_two_premises(
            '(&/, A, B, C). %1.00;0.90%',
            'A. %1.00;0.90%',
            10
        )
        
        self.assertTrue(
            output_contains(tasks_derived, '(&/, B, C). %1.00;0.81%')
        )

    def test_sequence_1(self):
        '''
        C!
        (&/, A, B, C).
        |- 
        (&/, A, B)!
        '''
        tasks_derived = process_two_premises(
            'C!',
            '(&/, A, B, C).',
            0
        )
        
        self.assertTrue(
            output_contains(tasks_derived, '(&/, A, B)! %1.00;0.81%')
        )

    def test_sequence_2(self):
        '''

        (&/, A, B, C)!
        A.
        |- 
        (&/, B, C)!
        '''
        tasks_derived = process_two_premises(
            '(&/, A, B, C)!',
            'A.',
            0
        )

        self.assertTrue(
            output_contains(tasks_derived, '(&/, B, C)! %1.00;0.81%')
        )

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