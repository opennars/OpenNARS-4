import unittest

from pynars.NAL.MetaLevelInference.VariableSubstitution import *
from pynars.NARS.InferenceEngine import GeneralEngine
from pynars.NARS.RuleMap import RuleMap

import Tests.utils_for_test as utils_for_test
from Tests.utils_for_test import *

# utils_for_test.rule_map = RuleMap_v2()

class TEST_NAL7(unittest.TestCase):
    def setUp(self):
        nars.reset()

    ''''''

    def test_deduction(self):
        '''
        'Temporal deduction
        
        'Someone enter the room_101 after he open the door_101
        <<(*, $x, room_101) --> enter> =\> <(*, $x, door_101) --> open>>. %0.90;0.90%

        'Someone open the door_101 after he hold the key_101
        <<(*, $y, door_101) --> open> =\> <(*, $y, key_101) --> hold>>. %0.80;0.90%

        100

        'If someone enter room_101, he should hold key_101 before
        ''outputMustContain('<<(*,$1,room_101) --> enter> =\> <(*,$1,key_101) --> hold>>. %0.72;0.58%')
        '''
        tasks_derived = process_two_premises(
            '<<(*, $x, room_101) --> enter> =\> <(*, $x, door_101) --> open>>. %0.90;0.90%',
            '<<(*, $y, door_101) --> open> =\> <(*, $y, key_101) --> hold>>. %0.80;0.90%',
            100
        )

        self.assertTrue(
            output_contains(tasks_derived, '<<(*,$0,room_101) --> enter> =\> <(*,$0,key_101) --> hold>>. %0.72;0.58%')
        )
        pass
        
    def test_expemplification(self):
        '''
        'Temporal explification
        
        'Someone enter the room_101 after he open the door_101
        <<(*, $x, room_101) --> enter> =\> <(*, $x, door_101) --> open>>. %0.90;0.90%

        'Someone open the door_101 after he hold the key_101
        <<(*, $y, door_101) --> open> =\> <(*, $y, key_101) --> hold>>. %0.80;0.90%

        100

        'If someone enter room_101, he should hold key_101 before
        ''outputMustContain('<<(*,$1,key_101) --> hold> =/> <(*,$1,room_101) --> enter>>. %1.00;0.37%')
        '''
        tasks_derived = process_two_premises(
            '<<(*, $x, room_101) --> enter> =\> <(*, $x, door_101) --> open>>. %0.90;0.90%',
            '<<(*, $y, door_101) --> open> =\> <(*, $y, key_101) --> hold>>. %0.80;0.90%',
            100
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<(*,$0,key_101) --> hold> =/> <(*,$0,room_101) --> enter>>. %1.00;0.37%')
        )
        pass

    def test_induction_0(self):
        '''
        'Temporal induction
        
        'Someone open door_101 before he enter room_101
        <<(*, $x, door_101) --> open> =/> <(*, $x, room_101) --> enter>>. %0.90;0.90%

        'Someone open door_101 after he hold key_101
        <<(*, $y, door_101) --> open> =\> <(*, $y, key_101) --> hold>>. %0.80;0.90%

        100

        'If someone hold key_101, he will enter room_101
        ''outputMustContain('<<(*,$1,key_101) --> hold> =/> <(*,$1,room_101) --> enter>>. %0.90;0.39%')
        'If someone enter room_101, he should hold key_101 before
        ''outputMustContain('<<(*,$1,room_101) --> enter> =\> <(*,$1,key_101) --> hold>>. %0.80;0.42%')
        '''
        tasks_derived = process_two_premises(
            '<<(*, $x, door_101) --> open> =/> <(*, $x, room_101) --> enter>>. %0.90;0.90%',
            '<<(*, $y, door_101) --> open> =\> <(*, $y, key_101) --> hold>>. %0.80;0.90%',
            100
        )

        self.assertTrue(
            output_contains(tasks_derived, '<<(*,$0,key_101) --> hold> =/> <(*,$0,room_101) --> enter>>. %0.90;0.39%')
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<(*,$0,room_101) --> enter> =\> <(*,$0,key_101) --> hold>>. %0.80;0.42%')
        )
        pass

    def test_induction_1(self):
        '''
        'Temporal induction
        
        'Someone open door_101 after he hold key_101
        <<(*, $y, door_101) --> open> =\> <(*, $y, key_101) --> hold>>. %0.80;0.90%

        'Someone open door_101 before he enter room_101
        <<(*, $x, door_101) --> open> =/> <(*, $x, room_101) --> enter>>. %0.90;0.90%

        100

        'If someone hold key_101, he will enter room_101
        ''outputMustContain('<<(*,$1,key_101) --> hold> =/> <(*,$1,room_101) --> enter>>. %0.90;0.39%')
        'If someone enter room_101, he should hold key_101 before
        ''outputMustContain('<<(*,$1,room_101) --> enter> =\> <(*,$1,key_101) --> hold>>. %0.80;0.42%')
        '''
        tasks_derived = process_two_premises(
            '<<(*, $y, door_101) --> open> =\> <(*, $y, key_101) --> hold>>. %0.80;0.90%',
            '<<(*, $x, door_101) --> open> =/> <(*, $x, room_101) --> enter>>. %0.90;0.90%',
            100
        )

        self.assertTrue(
            output_contains(tasks_derived, '<<(*,$0,key_101) --> hold> =/> <(*,$0,room_101) --> enter>>. %0.90;0.39%')
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<(*,$0,room_101) --> enter> =\> <(*,$0,key_101) --> hold>>. %0.80;0.42%')
        )
        pass

    
    def test_comparison_0(self):
        '''
        'Temporal comparison
        
        'Someone open door_101 before he enter room_101
        <<(*, $x, door_101) --> open> =/> <(*, $x, room_101) --> enter>>. %0.90;0.90%

        'Someone open door_101 after he hold key_101
        <<(*, $y, door_101) --> open> =\> <(*, $y, key_101) --> hold>>. %0.80;0.90%

        100

        'If someone hold key_101, it means he will enter room_101
        ''outputMustContain('<<(*,$1,key_101) --> hold> </> <(*,$1,room_101) --> enter>>. %0.73;0.44%')
        '''
        tasks_derived = process_two_premises(
            '<<(*, $x, door_101) --> open> =/> <(*, $x, room_101) --> enter>>. %0.90;0.90%',
            '<<(*, $y, door_101) --> open> =\> <(*, $y, key_101) --> hold>>. %0.80;0.90%',
            100
        )

        self.assertTrue(
            output_contains(tasks_derived, '<<(*,$0,key_101) --> hold> </> <(*,$0,room_101) --> enter>>. %0.73;0.44%')
        )
        pass

    def test_comparison_1(self):
        '''
        'Temporal comparison
        
        'Someone open door_101 after he hold key_101
        <<(*, $y, door_101) --> open> =\> <(*, $y, key_101) --> hold>>. %0.80;0.90%

        'Someone open door_101 before he enter room_101
        <<(*, $x, door_101) --> open> =/> <(*, $x, room_101) --> enter>>. %0.90;0.90%

        100

        'If someone hold key_101, it means he will enter room_101
        ''outputMustContain('<<(*,$1,key_101) --> hold> </> <(*,$1,room_101) --> enter>>. %0.73;0.44%')
        '''
        tasks_derived = process_two_premises(
            '<<(*, $y, door_101) --> open> =\> <(*, $y, key_101) --> hold>>. %0.80;0.90%',
            '<<(*, $x, door_101) --> open> =/> <(*, $x, room_101) --> enter>>. %0.90;0.90%',
            100
        )

        self.assertTrue(
            output_contains(tasks_derived, '<<(*,$0,key_101) --> hold> </> <(*,$0,room_101) --> enter>>. %0.73;0.44%')
        )
        pass

    def test_comparison_2(self):
        '''
        'Temporal comparison
        
        'Someone open door_101 before he enter room_101
        <<(*, $x, room_101) --> enter> =/> <(*, $x, door_101) --> open>>. %0.90;0.90%

        'Someone open door_101 after he hold key_101
        <<(*, $y, key_101) --> hold> =\> <(*, $y, door_101) --> open>>. %0.80;0.90%

        100

        'If someone hold key_101, it means he will enter room_101
        ''outputMustContain('<<(*,$1,room_101) --> enter> </> <(*,$1,key_101) --> hold>>. %0.73;0.44%')
        '''
        tasks_derived = process_two_premises(
            '<<(*, $x, room_101) --> enter> =/> <(*, $x, door_101) --> open>>. %0.90;0.90%',
            '<<(*, $y, key_101) --> hold> =\> <(*, $y, door_101) --> open>>. %0.80;0.90%',
            100
        )

        self.assertTrue(
            output_contains(tasks_derived, '<<(*,$0,room_101) --> enter> </> <(*,$0,key_101) --> hold>>. %0.73;0.44%')
        )
        pass

    def test_comparison_3(self):
        '''
        'Temporal comparison
        
        'Someone open door_101 after he hold key_101
        <<(*, $y, key_101) --> hold> =\> <(*, $y, door_101) --> open>>. %0.80;0.90%

        'Someone open door_101 before he enter room_101
        <<(*, $x, room_101) --> enter> =/> <(*, $x, door_101) --> open>>. %0.90;0.90%

        100

        'If someone hold key_101, it means he will enter room_101
        ''outputMustContain('<<(*,$1,room_101) --> enter> </> <(*,$1,key_101) --> hold>>. %0.73;0.44%')
        '''
        tasks_derived = process_two_premises(
            '<<(*, $y, key_101) --> hold> =\> <(*, $y, door_101) --> open>>. %0.80;0.90%',
            '<<(*, $x, room_101) --> enter> =/> <(*, $x, door_101) --> open>>. %0.90;0.90%',
            100
        )

        self.assertTrue(
            output_contains(tasks_derived, '<<(*,$0,room_101) --> enter> </> <(*,$0,key_101) --> hold>>. %0.73;0.44%')
        )
        pass


    def test_abduction(self):
        '''
        'Temporal abudction
        
        <A =/> B>. %0.80;0.90%
        <C =\> B>. %0.90;0.90%

        100

        ''outputMustContain('<A =/> C>. %0.80;0.42%')
        ''outputMustContain('<C =\> A>. %0.90;0.39%')
        '''
        tasks_derived = process_two_premises(
            '<A =/> B>. %0.80;0.90%',
            '<C =\> B>. %0.90;0.90%',
            100
        )

        self.assertTrue(
            output_contains(tasks_derived, '<A =/> C>. %0.80;0.42%')
        )
        self.assertTrue(
            output_contains(tasks_derived, '<C =\> A>. %0.90;0.39%')
        )
        pass


    def test_inference_on_tense_0(self):
        '''
        'Inference on tense 

        'John hold key_101 before he enter room_101
        <<(*,John,key_101) --> hold> =/> <(*,John,room_101) --> enter>>. %1.00;0.90%

        'John is holding key_101 now
        <(*,John,key_101) --> hold>. :|: %1.00;0.90%

        20

        'John will enter the room_101
        ''outputMustContain('<(*,John,room_101) --> enter>. :!5: %1.00;0.81%')
        '''
        tasks_derived = process_two_premises(
            '<(*,John,key_101) --> hold>. :|: %1.00;0.90%',
            '<<(*,John,key_101) --> hold> =/> <(*,John,room_101) --> enter>>. %1.00;0.90%',
            20
        )

        self.assertTrue(
            output_contains(tasks_derived, '<(*,John,room_101) --> enter>. :!5: %1.00;0.81%')
        )
        pass


    def test_inference_on_tense_1(self):
        '''
        ' inference on tense 

        'John hold key_101 before he enter room_101
        <<(*,John,key_101) --> hold> =/> <(*,John,room_101) --> enter>>. %1.00;0.90%
        
        'John entered room_101
        <(*,John,room_101) --> enter>. :\: %1.00;0.90%  

        3

        ''outputMustContain('<(*,John,key_101) --> hold>. :!-10: %1.00;0.45%')
        '''
        tasks_derived = process_two_premises(
            '<(*,John,room_101) --> enter>. :\: %1.00;0.90%',
            '<<(*,John,key_101) --> hold> =/> <(*,John,room_101) --> enter>>. %1.00;0.90%',
            10
        )

        self.assertTrue(
            output_contains(tasks_derived, '<(*,John,key_101) --> hold>. :!-10: %1.00;0.45%')
        )
        pass


    def test_inference_on_tense_2(self):
        '''
        ' inference on tense 

        'John hold key_101 before he enter room_101
        <<(*,John,key_101) --> hold> =/> <(*,John,room_101) --> enter>>. %1.00;0.90%
        
        'John entered room_101
        <(*,John,room_101) --> enter>. :\: %1.00;0.90%  

        3

        ''outputMustContain('<(*,John,key_101) --> hold>. %1.00;0.30%')
        '''
        tasks_derived = process_two_premises(
            '<<(*,John,key_101) --> hold> =/> <(*,John,room_101) --> enter>>. %1.00;0.90%',
            '<(*,John,room_101) --> enter>. :\: %1.00;0.90%',
            30
        )

        self.assertTrue(
            output_contains(tasks_derived, '<(*,John,key_101) --> hold>. %1.00;0.30%')
        )
        pass

    def test_induction_on_tense_0_0(self):
        '''
        nal7.6.nal

        'induction on events 

        'John is opening door_101
        <John --> (/,open,_,door_101)>. :|: 

        6

        'John is entering room_101
        <John --> (/,enter,_,room_101)>. :|: 

        20

        'If John enter room_101, he should open door_101 before
        ''outputMustContain('<<John --> (/,enter,_,room_101)> =\> (&/,<John --> (/,open,_,door_101)>,+6)>. :!6: %1.00;0.45%')

        'new: variable introduction also in time:

        'If someone enter room_101, he should open door_101 before
        ''outputMustContain('<<$1 --> (/,enter,_,room_101)> =\> (&/,<$1 --> (/,open,_,door_101)>,+6)>. :!6: %1.00;0.45%')

        'adjusted +2 to +3 in both conditions

        10
        '''
        tasks_derived = process_two_premises(
            '<John --> (/,open,_,door_101)>. :|:',
            None,
            6
        )
        tasks_derived.extend(process_two_premises(
            '<John --> (/,enter,_,room_101)>. :|:',
            None,
            20
        ))

        self.assertTrue(
            output_contains(tasks_derived, '<<John --> (/,enter,_,room_101)> =\> (&/,<John --> (/,open,_,door_101)>,+6)>. :!6: %1.00;0.45%')
        )
        pass

    
    def test_induction_on_tense_0_1(self):
        '''
        nal7.6.nal

        'induction on events 

        'John is opening door_101
        <John --> (/,open,_,door_101)>. :|: 

        6

        'John is entering room_101
        <John --> (/,enter,_,room_101)>. :|: 

        20

        'If John enter room_101, he should open door_101 before
        ''outputMustContain('<<John --> (/,enter,_,room_101)> =\> (&/,<John --> (/,open,_,door_101)>,+6)>. :!6: %1.00;0.45%')

        'new: variable introduction also in time:

        'If someone enter room_101, he should open door_101 before
        ''outputMustContain('<<$1 --> (/,enter,_,room_101)> =\> (&/,<$1 --> (/,open,_,door_101)>,+6)>. :!6: %1.00;0.45%')

        'adjusted +2 to +3 in both conditions

        10
        '''
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '<John --> (/,open,_,door_101)>. :|: ',
            '<John --> (/,enter,_,room_101)>. :|: ',
            'John.'
        )
        tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 
        self.assertTrue(
            output_contains(tasks_derived, '<<$1 --> (/,enter,_,room_101)> =\> (&/,<$1 --> (/,open,_,door_101)>,+6)>. :!6: %1.00;0.45%')
        )
        pass



    def test_induction_on_tense_1(self):
        '''
        nal7.7.nal

        'John is holding key_101 now
        <(*,John,key_101) --> hold>. :|:  %1.00;0.90% 

        6

        'If John open door_101, he will enter room_101
        <<(*,John,door_101) --> open> =/> <(*,John,room_101) --> enter>>. :|:  %1.00;0.90% 

        20

        'If John hold key_101 and open door_101 (after 6 steps), he will enter room_101
        ''outputMustContain('<(&/,<(*,John,key_101) --> hold>,+6,<(*,John,door_101) --> open>) =/> <(*,John,room_101) --> enter>>. :!6: %1.00;0.45%')
        'changed fomr +2 to +4 due to changes in interval calculations
        'this one is working, just throwing exception
        '''
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '<(*,John,key_101) --> hold>. :|:  %1.00;0.90% ',
            '<<(*,John,door_101) --> open> =/> <(*,John,room_101) --> enter>>. :|:  %1.00;0.90%',
            'John.'
        )
        tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 
        self.assertTrue(
            output_contains(tasks_derived, '<(&/,<(*,John,key_101) --> hold>,+6,<(*,John,door_101) --> open>) =/> <(*,John,room_101) --> enter>>. :!6: %1.00;0.45%')
        )
        pass

    def test_analogy(self):
        '''
        nal7.15.nal
        
        'If someone open door_101, he will enter room_101
        <<(*, $x, door_101) --> open> =/> <(*, $x, room_101) --> enter>>. %0.95;0.90%

        ' If someone enter room_101, it means he leave corridor_100
        <<(*, $x, room_101) --> enter> <|> <(*, $x, corridor_100) --> leave>>. %1.00;0.90%

        40

        'If someone open door_101, he will leave corridor_100
        ''outputMustContain('<<(*,$1,door_101) --> open> =/> <(*,$1,corridor_100) --> leave>>. %0.95;0.81%')
        '''
        tasks_derived = process_two_premises(
            '<<(*, $x, door_101) --> open> =/> <(*, $x, room_101) --> enter>>. %0.95;0.90%',
            '<<(*, $x, room_101) --> enter> <|> <(*, $x, corridor_100) --> leave>>. %1.00;0.90%',
            40
        )

        self.assertTrue(
            output_contains(tasks_derived, '<<(*,$0,door_101) --> open> =/> <(*,$0,corridor_100) --> leave>>. %0.95;0.81%')
        )
        pass


    def test_deduction_sequence_eliminate_0(self):
        '''
        nal7.18.nal
        
        'If someone hold key_101, he will enter room_101 (in 100 steps)
        <(&/,<(*, John, key_101) --> hold>,+100) =/> <(*, John, room_101) --> enter>>. %1.00;0.90%

        'John held the key_101
        <(*, John, key_101) --> hold>. :\: %1.00;0.90%

        210

        'John will enter room_101
        ''outputMustContain('<(*,John,room_101) --> enter>. :!100: %1.00;0.81%')

        'this one is working, but throws an exception
        '''
        tasks_derived = process_two_premises(
            '<(*, John, key_101) --> hold>. :\: %1.00;0.90%',
            '<(&/,<(*, John, key_101) --> hold>,+100) =/> <(*, John, room_101) --> enter>>. %1.00;0.90%',
            200
        )
        tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 
        self.assertTrue(
            output_contains(tasks_derived, '<(*,John,room_101) --> enter>. :!100: %1.00;0.81%')
        )
        pass

    def test_deduction_sequence_eliminate_0_1(self):
        '''
        '''
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '(&/,A,+100,B). :\: %1.00;0.90%',
            '<(&/,A,+100,B,+100) =/> D>. %1.00;0.90%',
            'B.'
        )
        tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 
        self.assertTrue(
            output_contains(tasks_derived, '<D. :!95: %1.00;0.81%')
        )
        pass


    def test_deduction_sequence_eliminate_1(self):
        '''
        nal7.18.nal
        
        'If someone hold key_101, he will enter room_101 (in 100 steps)
        <(&/,<(*, $x, key_101) --> hold>,+100) =/> <(*, $x, room_101) --> enter>>. %1.00;0.90%

        'John held the key_101
        <(*, John, key_101) --> hold>. :\: %1.00;0.90%

        210

        'John will enter room_101
        ''outputMustContain('<(*,John,room_101) --> enter>. :!95: %1.00;0.81%')

        'this one is working, but throws an exception
        '''
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '<(&/,<(*, $x, key_101) --> hold>,+100) =/> <(*, $x, room_101) --> enter>>. %1.00;0.90%',
            '<(*, John, key_101) --> hold>. :\: %1.00;0.90%',
            'hold.'
        )
        tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 
        self.assertTrue(
            output_contains(tasks_derived, '<(*,John,room_101) --> enter>. :!95: %1.00;0.81%')
        )
        pass

    
    def test_abduction_sequence_eliminate_0(self):
        '''
        nal7.19.nal
        
        'If someone hold key_101, he will enter room_101 (in 100 steps)
        <(&/,<(*, John, key_101) --> hold>,+100) =/> <(*, John, room_101) --> enter>>. %1.00;0.90%

        'John is entering room_101 now
        <(*,John,room_101) --> enter>. :|: %1.00;0.90%

        15

        'John held the key_101 (105 steps before)
        ''outputMustContain('<(*,John,key_101) --> hold>. :!-105: %1.00;0.45%')
        '''
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '<(*,John,room_101) --> enter>. :|: %1.00;0.90%',
            '<(&/,<(*, John, key_101) --> hold>,+100) =/> <(*, John, room_101) --> enter>>. %1.00;0.90%',
            '<(*,John,room_101) --> enter>.'
        )
        tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 
        self.assertTrue(
            output_contains(tasks_derived, '<(*,John,key_101) --> hold>. :!-105: %1.00;0.45%')
        )
        pass


    def test_abduction_sequence_eliminate_1(self):
        '''
        nal7.19.nal
        
        'If someone hold key_101, he will enter room_101 (in 100 steps)
        <(&/,<(*, $x, key_101) --> hold>,+100) =/> <(*, $x, room_101) --> enter>>. %1.00;0.90%

        'John is entering room_101 now
        <(*,John,room_101) --> enter>. :|: %1.00;0.90%

        15

        'John held the key_101 (105 steps before)
        ''outputMustContain('<(*,John,key_101) --> hold>. :!-105: %1.00;0.45%')
        '''
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '<(*, $x, room_101) --> enter>. :|: %1.00;0.90%',
            '<(&/,<(*, $x, key_101) --> hold>,+100) =/> <(*, $x, room_101) --> enter>>. %1.00;0.90%',
            '<(*, $x, room_101) --> enter>.'
        )
        tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 
        self.assertTrue(
            output_contains(tasks_derived, '<(*,John,key_101) --> hold>. :!-105: %1.00;0.45%')
        )
        pass


    def test_deduction_sequence(self):
        '''
        nal7.36.nal
        
        'deduction with interval summation

        ' a + 1 = b
        <(&/, a, +1) =/> b>. %1.00;0.90%

        ' b + 1 = c
        <(&/, b, +1) =/> c>. %1.00;0.90%
        
        10

        ' a + 2 = c
        ''outputMustContain('<(&/,a,+2) =/> c>. %1.00;0.81%')
        '''
        tasks_derived = process_two_premises(
            '<(&/, a, +1) =/> b>. %1.00;0.90%',
            '<(&/, b, +1) =/> c>. %1.00;0.90%',
            10
        )

        self.assertTrue(
            output_contains(tasks_derived, '<(&/,a,+2) =/> c>. %1.00;0.81%')
        )
        pass

class TEST_NAL7_ANALOGY(unittest.TestCase):
    def setUp(self):
        nars.reset()

    def test_analogy_0_0__0(self):
        '''
        
        '''
        tasks_derived = process_two_premises(
            '<A=/>B>. %1.00;0.90%',
            '<A</>C>. %1.00;0.90%',
            10
        )
        self.assertFalse(
            output_contains(tasks_derived, '<C=/>B>. %1.00;0.81%')
        )
    
    def test_analogy_0_0__1(self):
        '''
        
        '''
        tasks_derived = process_two_premises(
            '<A=/>B>. %1.00;0.90%',
            '<A<|>C>. %1.00;0.90%',
            10
        )

        self.assertTrue(
            output_contains(tasks_derived, '<C=/>B>. %1.00;0.81%')
        )
    
    def test_analogy_0_0__2(self):
        '''
        
        '''
        tasks_derived = process_two_premises(
            '<A=\>B>. %1.00;0.90%',
            '<A</>C>. %1.00;0.90%',
            10
        )

        self.assertTrue(
            output_contains(tasks_derived, '<B=/>C>. %1.00;0.81%')
        )

    def test_analogy_0_0__3(self):
        '''
        
        '''
        tasks_derived = process_two_premises(
            '<A=\>B>. %1.00;0.90%',
            '<A<|>C>. %1.00;0.90%',
            10
        )

        self.assertTrue(
            output_contains(tasks_derived, '<B=/>C>. %1.00;0.81%')
        )

    def test_analogy_0_0__4(self):
        '''
        
        '''
        tasks_derived = process_two_premises(
            '<A=|>B>. %1.00;0.90%',
            '<A</>C>. %1.00;0.90%',
            10
        )

        self.assertTrue(
            output_contains(tasks_derived, '<C=\>B>. %1.00;0.81%')
        )

    def test_analogy_0_0__5(self):
        '''
        
        '''
        tasks_derived = process_two_premises(
            '<A=|>B>. %1.00;0.90%',
            '<A<|>C>. %1.00;0.90%',
            10
        )

        self.assertTrue(
            output_contains(tasks_derived, '<C=|>B>. %1.00;0.81%')
        )

    def test_analogy_0_1__0(self):
        '''
        
        '''
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '<A=/>B>. %1.00;0.90%',
            '<C</>A>. %1.00;0.90%',
            'A.'
        )
        tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 
        self.assertTrue(
            output_contains(tasks_derived, '<C=/>B>. %1.00;0.81%')
        )

    def test_analogy_0_1__1(self):
        '''
        
        '''
        tasks_derived = process_two_premises(
            '<A=/>B>. %1.00;0.90%',
            '<C<|>A>. %1.00;0.90%',
            10
        )

        self.assertTrue(
            output_contains(tasks_derived, '<C=/>B>. %1.00;0.81%')
        )

    def test_analogy_0_1__2(self):
        '''
        
        '''
        tasks_derived = process_two_premises(
            '<A=\>B>. %1.00;0.90%',
            '<C</>A>. %1.00;0.90%',
            10
        )
        self.assertFalse(
            output_contains(tasks_derived, '<C=/>B>. %1.00;0.81%')
        )
        
    def test_analogy_0_1__3(self):
        '''
        
        '''
        tasks_derived = process_two_premises(
            '<A=\>B>. %1.00;0.90%',
            '<C<|>A>. %1.00;0.90%',
            10
        )
        self.assertTrue(
            output_contains(tasks_derived, '<B=/>C>. %1.00;0.81%')
        )

    def test_analogy_0_1__4(self):
        '''
        
        '''
        tasks_derived = process_two_premises(
            '<A=|>B>. %1.00;0.90%',
            '<C</>A>. %1.00;0.90%',
            10
        )
        self.assertTrue(
            output_contains(tasks_derived, '<C=/>B>. %1.00;0.81%')
        )

    def test_analogy_0_1__5(self):
        '''
        
        '''
        tasks_derived = process_two_premises(
            '<A=|>B>. %1.00;0.90%',
            '<C<|>A>. %1.00;0.90%',
            10
        )
        self.assertTrue(
            output_contains(tasks_derived, '<C=|>B>. %1.00;0.81%')
        )

    def test_analogy_1_0__0(self):
        '''
        
        '''
        tasks_derived = process_two_premises(
            '<A=/>B>. %1.00;0.90%',
            '<B</>C>. %1.00;0.90%',
            10
        )
        self.assertTrue(
            output_contains(tasks_derived, '<A=/>C>. %1.00;0.81%')
        )

    def test_analogy_1_0__1(self):
        '''
        
        '''
        tasks_derived = process_two_premises(
            '<A=/>B>. %1.00;0.90%',
            '<B<|>C>. %1.00;0.90%',
            10
        )
        self.assertTrue(
            output_contains(tasks_derived, '<A=/>C>. %1.00;0.81%')
        )

    def test_analogy_1_0__2(self):
        '''
        
        '''
        tasks_derived = process_two_premises(
            '<A=\>B>. %1.00;0.90%',
            '<B</>C>. %1.00;0.90%',
            10
        )
        self.assertFalse(
            output_contains(tasks_derived, '<A=/>C>. %1.00;0.81%')
        )
    
    def test_analogy_1_0__3(self):
        '''
        
        '''
        tasks_derived = process_two_premises(
            '<A=\>B>. %1.00;0.90%',
            '<B<|>C>. %1.00;0.90%',
            10
        )
        self.assertTrue(
            output_contains(tasks_derived, '<C=/>A>. %1.00;0.81%')
        )

    def test_analogy_1_0__4(self):
        '''
        
        '''
        tasks_derived = process_two_premises(
            '<A=|>B>. %1.00;0.90%',
            '<B</>C>. %1.00;0.90%',
            10
        )
        self.assertTrue(
            output_contains(tasks_derived, '<A=/>C>. %1.00;0.81%')
        )

    def test_analogy_1_0__5(self):
        '''
        
        '''
        tasks_derived = process_two_premises(
            '<A=|>B>. %1.00;0.90%',
            '<B<|>C>. %1.00;0.90%',
            10
        )
        self.assertTrue(
            output_contains(tasks_derived, '<A=|>C>. %1.00;0.81%')
        )

    def test_analogy_1_1__0(self):
        '''
        
        '''
        tasks_derived = process_two_premises(
            '<A=/>B>. %1.00;0.90%',
            '<C</>B>. %1.00;0.90%',
            10
        )
        self.assertTrue(
            output_contains(tasks_derived, '<A=/>C>. %1.00;0.81%')
        )

    def test_analogy_1_1__1(self):
        '''
        
        '''
        tasks_derived = process_two_premises(
            '<A=/>B>. %1.00;0.90%',
            '<C<|>B>. %1.00;0.90%',
            10
        )
        self.assertTrue(
            output_contains(tasks_derived, '<A=/>C>. %1.00;0.81%')
        )

    def test_analogy_1_1__2(self):
        '''
        
        '''
        tasks_derived = process_two_premises(
            '<A=\>B>. %1.00;0.90%',
            '<C</>B>. %1.00;0.90%',
            10
        )
        self.assertTrue(
            output_contains(tasks_derived, '<C=/>A>. %1.00;0.81%')
        )

    def test_analogy_1_1__3(self):
        '''
        
        '''
        tasks_derived = process_two_premises(
            '<A=\>B>. %1.00;0.90%',
            '<C<|>B>. %1.00;0.90%',
            10
        )
        self.assertTrue(
            output_contains(tasks_derived, '<C=/>A>. %1.00;0.81%')
        )

    def test_analogy_1_1__4(self):
        '''
        
        '''
        tasks_derived = process_two_premises(
            '<A=|>B>. %1.00;0.90%',
            '<C</>B>. %1.00;0.90%',
            10
        )
        self.assertTrue(
            output_contains(tasks_derived, '<A=\>C>. %1.00;0.81%')
        )

    def test_analogy_1_1__5(self):
        '''
        
        '''
        tasks_derived = process_two_premises(
            '<A=|>B>. %1.00;0.90%',
            '<C<|>B>. %1.00;0.90%',
            10
        )
        self.assertTrue(
            output_contains(tasks_derived, '<A=|>C>. %1.00;0.81%')
        )

if __name__ == '__main__':

    test_classes_to_run = [
        TEST_NAL7
    ]

    loader = unittest.TestLoader()

    suites = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites.append(suite)
        
    suites = unittest.TestSuite(suites)

    runner = unittest.TextTestRunner()
    results = runner.run(suites)