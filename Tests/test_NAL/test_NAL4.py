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



class TEST_NAL4(unittest.TestCase):
    def setUp(self):
        nars.reset()

    ''''''

    def test_structural_transformation_0(self):
        '''
        'Structural transformation

        'An acid and a base can have a reaction.
        <(*,acid, base) --> reaction>. %1.00;0.90%

        2

        'Acid can react with base.
        ''outputMustContain('<acid --> (/,reaction,_,base)>. %1.00;0.90%')

        'A base is something that has a reaction with an acid. 
        ''outputMustContain('<base --> (/,reaction,acid,_)>. %1.00;0.90%')
        '''
        tasks_derived = process_two_premises(
            '<(*,acid, base) --> reaction>. %1.00;0.90%',
            None,
            10
        )

        self.assertTrue(
            output_contains(tasks_derived, '<acid --> (/,reaction,_,base)>. %1.00;0.90%')
        )

        self.assertTrue(
            output_contains(tasks_derived, '<base --> (/,reaction,acid,_)>. %1.00;0.90%')
        )
        pass


    def test_structural_transformation_1(self):
        '''
        'Structural transformation

        'Acid can react with base.
        <acid --> (/,reaction,_,base)>. %1.00;0.90%

        3

        'An acid and a base can have a reaction.
        ''outputMustContain('<(*,acid,base) --> reaction>. %1.00;0.90%')
        '''
        tasks_derived = process_two_premises(
            '<acid --> (/,reaction,_,base)>. %1.00;0.90%',
            None,
            10
        )
        
        self.assertTrue(
            output_contains(tasks_derived, '<(*,acid,base) --> reaction>. %1.00;0.90%')
        )
        pass
        

    def test_structural_transformation_2(self):
        '''
        'Structural transformation

        'Acid can react with base.
        <acid --> (/,reaction,_,base)>. %1.00;0.90%

        3

        'A base is something that has a reaction with an acid. 
        ''outputMustContain('<base --> (/,reaction,acid,_)>. %1.00;0.90%')
        '''
        tasks_derived = process_two_premises(
            '<acid --> (/,reaction,_,base)>. %1.00;0.90%',
            None,
            10
        )
        
        self.assertTrue(
            output_contains(tasks_derived, '<base --> (/,reaction,acid,_)>. %1.00;0.90%')
        )
        pass


    def test_structural_transformation_3(self):
        '''
        'Structural transformation

        'A base is something that has a reaction with an acid. 
        <base --> (/,reaction,acid,_)>. %1.00;0.90%

        3

        'Acid can react with base.
        ''outputMustContain('<acid --> (/,reaction,_,base)>. %1.00;0.90%')
        '''
        tasks_derived = process_two_premises(
            '<base --> (/,reaction,acid,_)>. %1.00;0.90%',
            None,
            10
        )
        
        self.assertTrue(
            output_contains(tasks_derived, '<acid --> (/,reaction,_,base)>. %1.00;0.90%')
        )
        pass


    def test_structural_transformation_4(self):
        '''
        'Structural transformation

        'Something that can neutralize a base is an acid.
        <(\,neutralization,_,base) --> acid>. %1.00;0.90%

        2

        'Neutralization is a relation between an acid and a base. 
        ''outputMustContain('<neutralization --> (*,acid,base)>. %1.00;0.90%')
        '''
        tasks_derived = process_two_premises(
            '<(\,neutralization,_,base) --> acid>. %1.00;0.90%',
            None,
            10
        )
        
        self.assertTrue(
            output_contains(tasks_derived, '<neutralization --> (*,acid,base)>. %1.00;0.90%')
        )
        pass


    def test_structural_transformation_5(self):
        '''
        'Structural transformation

        'Something that can neutralize a base is an acid.
        <(\,neutralization,_,base) --> acid>. %1.00;0.90%

        2

        'Something that can be neutralized by an acid is a base.
        ''outputMustContain('<(\,neutralization,acid,_) --> base>. %1.00;0.90%')
        '''
        tasks_derived = process_two_premises(
            '<(\,neutralization,_,base) --> acid>. %1.00;0.90%',
            None,
            10
        )
        
        self.assertTrue(
            output_contains(tasks_derived, '<(\,neutralization,acid,_) --> base>. %1.00;0.90%')
        )
        pass


    def test_structural_transformation_6(self):
        '''
        'Structural transformation

        'Something that can be neutralized by an acid is a base.
        <(\,neutralization,acid,_) --> base>. %1.00;0.90%

        2

        'Something that can neutralize a base is an acid.
        ''outputMustContain('<(\,neutralization,_,base) --> acid>. %1.00;0.90%')
        '''
        tasks_derived = process_two_premises(
            '<(\,neutralization,acid,_) --> base>. %1.00;0.90%',
            None,
            10
        )
        
        self.assertTrue(
            output_contains(tasks_derived, '<(\,neutralization,_,base) --> acid>. %1.00;0.90%')
        )
        pass


    def test_structural_transformation_7(self):
        '''
        'Structural transformation

        'Something that can be neutralized by an acid is a base.
        <(\,neutralization,acid,_) --> base>. %1.00;0.90%

        2

        'Neutralization is a relation between an acid and a base. 
        ''outputMustContain('<neutralization --> (*,acid,base)>. %1.00;0.90%')
        '''
        tasks_derived = process_two_premises(
            '<(\,neutralization,acid,_) --> base>. %1.00;0.90%',
            None,
            10
        )
        
        self.assertTrue(
            output_contains(tasks_derived, '<neutralization --> (*,acid,base)>. %1.00;0.90%')
        )
        pass


    def test_structural_transformation_8(self):
        '''
        'Structural transformation

        'Bird is a type of animal.
        <bird --> animal>. %1.00;0.90%

        'What is the relation between a bird and a plant?
        <(*,bird,plant) --> ?x>?  

        6

        'The relation between bird and plant is a type of relation between animal and plant.
        ''outputMustContain('<(*,bird,plant) --> (*,animal,plant)>. %1.00;0.81%')
        '''
        tasks_derived = process_two_premises(
            '<bird --> animal>. %1.00;0.90%', 
            '<(*,bird,plant) --> ?x>?', 
            6
        )
        self.assertTrue(
            output_contains(tasks_derived, '<(*,bird,plant) --> (*,animal,plant)>. %1.00;0.81%')
        )
        pass

    def test_structural_transformation_9(self):
        '''
        'Structural transformation

        'Neutralization is a type of reaction.
        <neutralization --> reaction>. %1.00;0.90%

        'What can be neutralized by acid?
        <(\,neutralization,acid,_) --> ?x>?

        6

        'What can be neutralized by acid can react with acid. 
        ''outputMustContain('<(\,neutralization,acid,_) --> (\,reaction,acid,_)>. %1.00;0.81%')
        '''
        tasks_derived = process_two_premises(
            '<neutralization --> reaction>. %1.00;0.90%', 
            '<(\,neutralization,acid,_) --> ?x>?', 
            6
        )
        self.assertTrue(
            output_contains(tasks_derived, '<(\,neutralization,acid,_) --> (\,reaction,acid,_)>. %1.00;0.81%')
        )
        pass


    def test_structural_transformation_10(self):
        '''
        'Structural transformation

        'Soda is a type of base.
        <soda --> base>. %1.00;0.90%

        'What is something that can neutralize a base?
        <(/,neutralization,_,base) --> ?x>?

        6

        'What can neutraliz base can react with base. 
        ''outputMustContain('<(/,neutralization,_,base) --> (/,neutralization,_,soda)>. %1.00;0.81%')
        '''
        tasks_derived = process_two_premises(
            '<soda --> base>. %1.00;0.90%', 
            '<(/,neutralization,_,base) --> ?x>?', 
            6
        )
        self.assertTrue(
            output_contains(tasks_derived, '<(/,neutralization,_,base) --> (/,neutralization,_,soda)>. %1.00;0.81%')
        )
        pass

if __name__ == '__main__':

    test_classes_to_run = [
        TEST_NAL4
    ]

    loader = unittest.TestLoader()

    suites = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites.append(suite)
        
    suites = unittest.TestSuite(suites)

    runner = unittest.TextTestRunner()
    results = runner.run(suites)