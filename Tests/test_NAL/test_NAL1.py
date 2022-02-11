import NARS
import unittest

from NARS.DataStructures import Bag, Task, Concept, Table
from NARS.DataStructures._py.Link import TaskLink, TermLink
from Narsese import Judgement, Term, Statement, Copula, Truth   

from pathlib import Path
import Narsese
from Narsese import Compound, Connector
from NAL.MetaLevelInference.VariableSubstitution import *
from Narsese import VarPrefix, Variable
from NARS.RuleMap import RuleMap_v2
from NARS import Reasoner_3_0_4 as Reasoner

import Tests.utils_for_test as utils_for_test
from Tests.utils_for_test import *

utils_for_test.rule_map = RuleMap_v2()

class TEST_NAL1(unittest.TestCase):

    def test_revision(self):
        '''
        'Revision ------

        'Bird is a type of swimmer.
        <bird --> swimmer>. %1.00;0.90%

        'Bird is probably not a type of swimmer.
        <bird --> swimmer>. %0.10;0.60%

        1

        'Bird is very likely to be a type of swimmer.
        ''outputMustContain('<bird --> swimmer>. %0.87;0.91%')
        '''
        tasks_derived = memory_accept_revision(
            '<bird --> swimmer>. %1.00;0.90%',
            '<bird --> swimmer>. %0.10;0.60%'
        )
        self.assertTrue(
            output_contains(tasks_derived, '<bird --> swimmer>. %0.87;0.91%')
        )
        
        pass


    def test_deduction(self):
        '''
        'Deduction

        'Bird is a type of animal.
        <bird --> animal>. %1.00;0.90%

        'Robin is a type of bird. 
        <robin --> bird>. %1.00;0.90%

        10

        'Robin is a type of animal.
        ''outputMustContain('<robin --> animal>. %1.00;0.81%')
        '''
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '<bird --> animal>. %1.00;0.90%', 
            '<robin --> bird>. %1.00;0.90%', 
            'bird.')
        tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 
        self.assertTrue(
            output_contains(tasks_derived, '<robin --> animal>. %1.00;0.81%')
        )
        
        pass


    def test_abduction(self):
        '''
        'Abduction

        'Sport is a type of competition.
        <sport --> competition>. %1.00;0.90%

        'Chess is a type of competition.
        <chess --> competition>. %0.90;0.90%

        3

        'I guess sport is a type of chess.
        ''outputMustContain('<sport --> chess>. %1.00;0.42%')

        'I guess chess is a type of sport.
        ''outputMustContain('<chess --> sport>. %0.90;0.45%')
        '''
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '<sport --> competition>. %1.00;0.90%', 
            '<chess --> competition>. %0.90;0.90%', 
            'competition.')
        tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 
        self.assertTrue(
            output_contains(tasks_derived, '<sport --> chess>. %1.00;0.42%')
        )
        self.assertTrue(
            output_contains(tasks_derived, '<chess --> sport>. %0.90;0.45%')
        )
        
        pass


    def test_induction(self):
        '''
        'Induction

        'Swan is a type of swimmer. 
        <swan --> swimmer>. %0.90;0.90%

        'Swan is a type of bird. 
        <swan --> bird>.  %1.00;0.90%

        3

        'I guess bird is a type of swimmer.
        ''outputMustContain('<bird --> swimmer>. %0.90;0.45%')

        'I guess swimmer is a type of bird.
        ''outputMustContain('<swimmer --> bird>. %1.00;0.42%')
        '''
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '<swan --> swimmer>. %0.90;0.90%', 
            '<swan --> bird>.  %1.00;0.90%', 
            'swan.')
        tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 
        self.assertTrue(
            output_contains(tasks_derived, '<bird --> swimmer>. %0.90;0.45%')
        )
        self.assertTrue(
            output_contains(tasks_derived, '<swimmer --> bird>. %1.00;0.42%')
        )
        
        pass


    def test_exemplification(self):
        '''
        'Exemplification

        'Robin is a type of bird.
        <robin --> bird>. %1.00;0.90%

        'A bird is a type of animal.
        <bird --> animal>. %1.00;0.90%

        3

        'I guess animal is a type of robin. 
        ''outputMustContain('<animal --> robin>. %1.00;0.45%')
        '''
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '<robin --> bird>. %1.00;0.90%', 
            '<bird --> animal>. %1.00;0.90%', 
            'bird.')
        tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 
        self.assertTrue(
            output_contains(tasks_derived, '<animal --> robin>. %1.00;0.45%')
        )
        
        pass


    def test_conversion(self):
        '''
        'Conversion

        'Bird is a type of swimmer. 
        <bird --> swimmer>. %1.00;0.90%

        'Is swimmer a type of bird?
        <swimmer --> bird>?

        6

        'I guess swimmer is a type of bird.
        ''outputMustContain('<swimmer --> bird>. %1.00;0.47%')
        '''
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '<bird --> swimmer>. %1.00;0.90%', 
            '<swimmer --> bird>?', 
            'bird.',
            True)
        tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 
        self.assertTrue(
            output_contains(tasks_derived, '<swimmer --> bird>. %1.00;0.47%')
        )
        
        pass    
        
    
    def test_yn_question(self):
        '''
        '"y/n" question

        ' Bird is a type of swimmer.
        <bird --> swimmer>. %1.00;0.90%

        ' Is bird a type of swimmer?
        <bird --> swimmer>? 

        1

        ' Bird is a type of swimmer.
        ''outputMustContain('<bird --> swimmer>. %1.00;0.90%')
        '''
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '<bird --> swimmer>. %1.00;0.90%', 
            '<bird --> swimmer>? ', 
            'bird.', 
            True)
        _, _, answers_question, _ = result2
        # self.assertIsNone(rules)
        # tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 
        self.assertTrue(
            output_contains(answers_question, '<bird --> swimmer>. %1.00;0.90%')
        )
        
        pass    
    
    def test_wh_question_0(self):
        '''
        ' "wh" question

        ' Bird is a type of swimmer.
        <bird --> swimmer>. %1.00;0.80%

        ' What is a type of swimmer?
        <?x --> swimmer>?  

        5

        ' Bird is a type of swimmer.
        ''outputMustContain('<bird --> swimmer>. %1.00;0.80%')
        '''
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '<bird --> swimmer>. %1.00;0.80%', 
            '<?x --> swimmer>?', 
            'swimmer.', 
            True)
        _, _, _, answers_quest = result2
        # tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 
        self.assertTrue(
            output_contains(answers_quest, '<bird --> swimmer>. %1.00;0.90%')
        )
        
        pass    


    def test_wh_question_1(self):
        '''
        ' "wh" question

        ' Bird is a type of swimmer.
        <bird --> swimmer>. %1.00;0.90%
        <bird --> flyer>. %1.00;0.90%

        ' What is a type of swimmer?
        (&&, <?x --> swimmer>, <?x --> flyer>)?  

        5

        ' Bird is a type of swimmer.
        ''outputMustContain('(&&, <bird --> swimmer>, <bird --> flyer>). %1.00;0.81%')
        '''
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '<bird --> swimmer>. %1.00;0.80%', 
            '<?x --> swimmer>?', 
            'swimmer.', 
            True)
        _, _, _, answers_quest = result2
        # tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 
        self.assertTrue(
            output_contains(answers_quest, '<bird --> swimmer>. %1.00;0.90%')
        )
        
        pass    


    def test_backward_inference(self):
        '''
        ' Backward inference

        ' Bird is a type of swimmer.
        <bird --> swimmer>. %1.00;0.80%

        ' What is a type of swimmer?
        <?1 --> swimmer>?  

        5

        ' What is a type of bird?
        ''outputMustContain('<?1 --> bird>?')

        ' What is the type of bird?
        ''outputMustContain('<bird --> ?1>?')
        '''
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '<bird --> swimmer>. %1.00;0.80%', 
            '<?x --> swimmer>?', 
            'swimmer.', 
            True)
        task.sentence.repr
        tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 
        self.assertTrue(
            output_contains(tasks_derived, '<?1 --> bird>?')
        )
        self.assertTrue(
            output_contains(tasks_derived, '<bird --> ?1>?')
        )
        
        pass    
    

if __name__ == '__main__':

    test_classes_to_run = [
        TEST_NAL1
    ]

    loader = unittest.TestLoader()

    suites = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites.append(suite)
        
    suites = unittest.TestSuite(suites)

    runner = unittest.TextTestRunner()
    results = runner.run(suites)