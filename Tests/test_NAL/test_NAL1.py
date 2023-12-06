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

# utils_for_test.engine = RuleMap()

class TEST_NAL1(unittest.TestCase):
    def setUp(self):
        nars.reset()

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
        tasks_derived = process_two_premises(
            '<bird --> swimmer>. %1.00;0.90%',
            '<bird --> swimmer>. %0.10;0.60%',
            2
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
        tasks_derived = process_two_premises(
            '<bird --> animal>. %1.00;0.90%', 
            '<robin --> bird>. %1.00;0.90%', 
            10
        )
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
        tasks_derived = process_two_premises(
            '<sport --> competition>. %1.00;0.90%', 
            '<chess --> competition>. %0.90;0.90%', 
            5
        )
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
        tasks_derived = process_two_premises(
            '<swan --> swimmer>. %0.90;0.90%', 
            '<swan --> bird>.  %1.00;0.90%', 
            5
        )
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
        tasks_derived = process_two_premises(
            '<robin --> bird>. %1.00;0.90%', 
            '<bird --> animal>. %1.00;0.90%', 
            5
        )
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
        tasks_derived = process_two_premises(
            '<bird --> swimmer>. %1.00;0.90%', 
            '<swimmer --> bird>?', 
            10
        )
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
        tasks_derived = process_two_premises(
            '<bird --> swimmer>. %1.00;0.90%', 
            '<bird --> swimmer>? ', 
            2 
        )
        # self.assertIsNone(rules)
        # tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 
        self.assertTrue(
            output_contains(tasks_derived, '<bird --> swimmer>. %1.00;0.90%')
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
        tasks_derived = process_two_premises(
            '<bird --> swimmer>. %1.00;0.80%', 
            '<?x --> swimmer>?', 
            5
        )
        # tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 
        self.assertTrue(
            output_contains(tasks_derived, '<bird --> swimmer>. %1.00;0.80%')
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
        tasks_derived = process_two_premises(
            '<bird --> swimmer>. %1.00;0.80%', 
            '<?x --> swimmer>?', 
            5
        )
        # tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 
        self.assertTrue(
            output_contains(tasks_derived, '<bird --> swimmer>. %1.00;0.80%')
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
        tasks_derived = process_two_premises(
            '<bird --> swimmer>. %1.00;0.80%', 
            '<?x --> swimmer>?', 
            10
        )
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