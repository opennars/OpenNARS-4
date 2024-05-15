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

# utils_for_test.rule_map = RuleMap_v2()


class TEST_NAL3(unittest.TestCase):
    def setUp(self):
        nars.reset()

    ''''''
    
    def test_compound_intersection_extension(self):
        '''
        'Compound composition, two premises

        'Swan is a type of swimmer.
        <swan --> swimmer>. %0.90;0.90%

        'Swan is a type of bird.
        <swan --> bird>. %0.80;0.90%

        16

        'Swan is a type of bird or a type of swimmer. 
        ''outputMustContain('<swan --> (|,bird,swimmer)>. %0.98;0.81%')


        'Swan is a type of swimming bird. 
        ''outputMustContain('<swan --> (&,bird,swimmer)>. %0.72;0.81%')
        '''
        tasks_derived = process_two_premises(
            '<swan --> swimmer>. %0.90;0.90%', 
            '<swan --> bird>. %0.80;0.90%', 
            16
        )
        self.assertTrue(
            output_contains(tasks_derived, '<swan --> (&,bird,swimmer)>. %0.72;0.81%')
        )
        pass

    
    def test_compound_union_extension(self):
        '''
        'Compound composition, two premises

        'Swan is a type of swimmer.
        <swan --> swimmer>. %0.90;0.90%

        'Swan is a type of bird.
        <swan --> bird>. %0.80;0.90%

        16

        'Swan is a type of bird or a type of swimmer. 
        ''outputMustContain('<swan --> (|,bird,swimmer)>. %0.98;0.81%')
        '''
        tasks_derived = process_two_premises(
            '<swan --> swimmer>. %0.90;0.90%', 
            '<swan --> bird>. %0.80;0.90%', 
            16
        )
        self.assertTrue(
            output_contains(tasks_derived, '<swan --> (|,bird,swimmer)>. %0.98;0.81%')
        )        
        pass


    def test_compound_intersection_intension(self):
        '''
        'Compound composition, two premises

        'Sport is a type of competition. 
        <sport --> competition>. %0.90;0.90%

        'Chess is a type of competition. 
        <chess --> competition>. %0.80;0.90%

        16

        'If something is either chess or sport, then it is a competition.
        ''outputMustContain('<(|,chess,sport) --> competition>. %0.72;0.81%')
        '''
        tasks_derived = process_two_premises(
            '<sport --> competition>. %0.90;0.90%', 
            '<chess --> competition>. %0.80;0.90%', 
            16
        )
        self.assertTrue(
            output_contains(tasks_derived, '<(|,chess,sport) --> competition>. %0.72;0.81%')
        )        
        pass


    def test_compound_union_intension(self):
        '''
        'Compound composition, two premises

        'Sport is a type of competition. 
        <sport --> competition>. %0.90;0.90%

        'Chess is a type of competition. 
        <chess --> competition>. %0.80;0.90%

        16

        'If something is both chess and sport, then it is a competition.
        ''outputMustContain('<(&,chess,sport) --> competition>. %0.98;0.81%')
        '''
        tasks_derived = process_two_premises(
            '<sport --> competition>. %0.90;0.90%', 
            '<chess --> competition>. %0.80;0.90%', 
            16
        )
        self.assertTrue(
            output_contains(tasks_derived, '<(&,chess,sport) --> competition>. %0.98;0.81%')
        )        
        pass


    def test_compound_decomposition_intensional_intersection(self):
        '''
        'Compound decomposition, two premises

        'Robin is a type of bird or a type of swimmer. 
        <robin --> (|,bird,swimmer)>. %1.00;0.90%

        'Robin is not a type of swimmer. 
        <robin --> swimmer>. %0.00;0.90%

        32

        'Robin is a type of bird. 

        ''outputMustContain('<robin --> bird>. %1.00;0.81%')
        '''
        tasks_derived = process_two_premises(
            '<robin --> (|,bird,swimmer)>. %1.00;0.90%', 
            '<robin --> swimmer>. %0.00;0.90%', 
            20
        )
        self.assertTrue(
            output_contains(tasks_derived, '<robin --> bird>. %1.00;0.81%')
        )        

        nars.reset()

        tasks_derived = process_two_premises(
            '<robin --> swimmer>. %0.00;0.90%', 
            '<robin --> (|,bird,swimmer)>. %1.00;0.90%', 
            20
        )
        self.assertTrue(
            output_contains(tasks_derived, '<robin --> bird>. %1.00;0.81%')
        )        
        pass

    
    def test_compound_decomposition_extensional_difference(self):
        '''
        'Compound decomposition, two premises

        'Robin is not a type of swimmer. 
        <robin --> swimmer>. %0.00;0.90%  

        'Robin is not a nonswimming mammal. 
        <robin --> (-,mammal,swimmer)>. %0.00;0.90%  

        32

        'Robin is not a type of mammal.
        ''outputMustContain('<robin --> mammal>. %0.00;0.81%')
        '''
        tasks_derived = process_two_premises(
            '<robin --> swimmer>. %0.00;0.90%', 
            '<robin --> (-,mammal,swimmer)>. %0.00;0.90%', 
            32
        )
        self.assertTrue(
            output_contains(tasks_derived, '<robin --> mammal>. %0.00;0.81%')
        )

        nars.reset()

        tasks_derived = process_two_premises(
            '<robin --> (-,mammal,swimmer)>. %0.00;0.90%', 
            '<robin --> swimmer>. %0.00;0.90%', 
            32
        )
        self.assertTrue(
            output_contains(tasks_derived, '<robin --> mammal>. %0.00;0.81%')
        )      

        pass


    def test_set_operations_0(self):
        '''
        'Compound decomposition, two premises

        'PlanetX is Mars, Pluto, or Venus.  
        <planetX --> {Mars,Pluto,Venus}>. %0.90;0.90% 

        'PlanetX is probably Pluto or Saturn.  
        <planetX --> {Pluto,Saturn}>. %0.70;0.90% 

        32

        'PlanetX is Mars, Pluto, Saturn, or Venus. 
        ''outputMustContain('<planetX --> {Mars,Pluto,Saturn,Venus}>. %0.97;0.81%')

        'PlanetX is probably Pluto. 
        ''outputMustContain('<planetX --> {Pluto}>. %0.63;0.81%')
        '''
        tasks_derived = process_two_premises(
            '<planetX --> {Mars,Pluto,Venus}>. %0.90;0.90%', 
            '<planetX --> {Pluto,Saturn}>. %0.70;0.90%', 
            32
        )
        self.assertTrue(
            output_contains(tasks_derived, '<planetX --> {Mars,Pluto,Saturn,Venus}>. %0.97;0.81%')
        )
        self.assertTrue(
            output_contains(tasks_derived, '<planetX --> {Pluto}>. %0.63;0.81%')
        )


        pass


    def test_set_operations_1(self):
        '''
        'Compound decomposition, two premises
        'PlanetX is Mars, Pluto, or Venus.  
        <planetX --> {Mars,Pluto,Venus}>. %0.90;0.90% 
        
        'PlanetX is probably neither Pluto nor Saturn.  
        <planetX --> {Pluto,Saturn}>. %0.10;0.90% 

        32

        'PlanetX is Mars, Pluto, Saturn, or Venus. 
        ''outputMustContain('<planetX --> {Mars,Pluto,Saturn,Venus}>. %0.91;0.81%')

        'PlanetX is either Mars or Venus.
        ''outputMustContain('<planetX --> {Mars,Venus}>. %0.81;0.81%')
        '''
        tasks_derived = process_two_premises(
            '<planetX --> {Mars,Pluto,Venus}>. %0.90;0.90%', 
            '<planetX --> {Pluto,Saturn}>. %0.10;0.90%', 
            32
        )
        self.assertTrue(
            output_contains(tasks_derived, '<planetX --> {Mars,Pluto,Saturn,Venus}>. %0.91;0.81%')
        )
        self.assertTrue(
            output_contains(tasks_derived, '<planetX --> {Mars,Venus}>. %0.81;0.81%')
        )

        pass


    def test_bi_composition_0(self):
        '''
        'Compound decomposition, two premises
        
        'Bird is a type of animal. 
        <bird --> animal>. %0.90;0.90% 

        'Is a swimming bird a type of swimming animal?
        <(&,bird,swimmer) --> (&,animal,swimmer)>?  

        32

        'A swimming bird is probably a type of swimming animal.
        ''outputMustContain('<(&,bird,swimmer) --> (&,animal,swimmer)>. %0.90;0.73%')
        '''
        tasks_derived = process_two_premises(
            '<bird --> animal>. %0.90;0.90%', 
            '<(&,bird,swimmer) --> (&,animal,swimmer)>?', 
            32
        )
        self.assertTrue(
            output_contains(tasks_derived, '<(&,bird,swimmer) --> (&,animal,swimmer)>. %0.90;0.73%')
        )
        pass


    def test_bi_composition_1(self):
        '''
        'Compound decomposition, two premises
        
        'Bird is a type of animal. 
        <bird --> animal>. %0.90;0.90%

        'Is a nonanimal swimmer a type of a nonbird swimmer?
        <(-,swimmer,animal) --> (-,swimmer,bird)>?   

        32

        'A nonanimal swimmer is probably a type of nonbird swimmer.
        ''outputMustContain('<(-,swimmer,animal) --> (-,swimmer,bird)>. %0.90;0.73%')
        '''
        tasks_derived = process_two_premises(
            '<bird --> animal>. %0.90;0.90%', 
            '<(-,swimmer,animal) --> (-,swimmer,bird)>?', 
            32
        )
        self.assertTrue(
            output_contains(tasks_derived, '<(-,swimmer,animal) --> (-,swimmer,bird)>. %0.90;0.73%')
        )
        pass

    
    def test_uni_composition_0(self):
        '''
        'Compound decomposition, two premises
        
        'Swan is a type of bird. 
        <swan --> bird>. %0.90;0.90%  

        'Is a swan a type of bird or swimmer?
        <swan --> (|,bird,swimmer)>?

        32

        'A swan is probably a type of bird or swimmer. 
        ''outputMustContain('<swan --> (|,bird,swimmer)>. %0.90;0.73%')
        '''
        tasks_derived = process_two_premises(
            '<swan --> bird>. %0.90;0.90%', 
            '<swan --> (|,bird,swimmer)>?', 
            32)
        self.assertTrue(
            output_contains(tasks_derived, '<swan --> (|,bird,swimmer)>. %0.90;0.73%')
        )

        pass


    def test_uni_composition_1(self):
        '''
        'Compound decomposition, two premises
        
        <swan --> bird>. %0.90;0.90%

        'Swan is a type of bird. 
        <(&,swan,swimmer) --> bird>?

        'Is swimming swan a type of bird?
        32

        'Swimming swan is a type of bird.
        ''outputMustContain('<(&,swan,swimmer) --> bird>. %0.90;0.73%')
        '''
        tasks_derived = process_two_premises(
            '<swan --> bird>. %0.90;0.90%', 
            '<(&,swan,swimmer) --> bird>?', 
            32
        )
        self.assertTrue(
            output_contains(tasks_derived, '<(&,swan,swimmer) --> bird>. %0.90;0.73%')
        )

        pass


    def test_uni_composition_2(self):
        '''
        'Compound decomposition, two premises
        
        'Swan is a type of bird. 
        <swan --> bird>. %0.90;0.90% 

        'Is swan a type of nonbird swimmer?
        <swan --> (-,swimmer,bird)>?

        32

        'A swan is not a type of nonbird swimmer.
        ''outputMustContain('<swan --> (-,swimmer,bird)>. %0.10;0.73%')
        '''
        tasks_derived = process_two_premises(
            '<swan --> bird>. %0.90;0.90%', 
            '<swan --> (-,swimmer,bird)>?', 
            32
        )
        self.assertTrue(
            output_contains(tasks_derived, '<swan --> (-,swimmer,bird)>. %0.10;0.73%')
        )

        pass


    def test_uni_decomposition_0(self):
        '''
        'Compound decomposition, two premises
        
        'Robin is a type of swimming bird.
        <robin --> (&,bird,swimmer)>. %0.90% 

        32

        'Robin is a type of bird. 
        ''outputMustContain('<robin --> bird>. %0.90;0.73%')
        '''
        tasks_derived = process_two_premises(
            '<robin --> (&,bird,swimmer)>. %0.90;0.90%', 
            None,
            32
        )
        self.assertTrue(
            output_contains(tasks_derived, '<robin --> bird>. %0.90;0.73%')
        )

        pass


    def test_uni_decomposition_1(self):
        '''
        'Compound decomposition, two premises
        
        'Robin is a type of nonswimming bird. 
        <robin --> (-,bird,swimmer)>. %0.90;0.90% 

        32

        'Robin is a type of bird. 
        ''outputMustContain('<robin --> bird>. %0.90;0.73%')
        '''
        tasks_derived = process_two_premises(
            '<robin --> (-,bird,swimmer)>. %0.90;0.90% ', 
            None,
            32
        )
        self.assertTrue(
            output_contains(tasks_derived, '<robin --> bird>. %0.90;0.73%')
        )
        pass

    def test_uni_decomposition_2(self):
        '''
        'Boys and girls are youth.
        <(|, boy, girl) --> youth>. %0.90;0.90% 

        32

        'Boys are youth.
        ''outputMustContain('<boy --> youth>. %0.90;0.73%')
        '''
        tasks_derived = process_two_premises(
            '<(|, boy, girl) --> youth>. %0.90;0.90% ', 
            None,
            32
        )
        self.assertTrue(
            output_contains(tasks_derived, '<boy --> youth>. %0.90;0.73%')
        )

        pass

    def test_uni_decomposition_3(self):
        '''
        'What differs boys from gials are being strong.
        <(~, boy, girl) --> [strong]>. %0.90;0.90% 

        32

        'Boys are strong.
        ''outputMustContain('<boy --> [strong]>. %0.90;0.73%')
        '''
        tasks_derived = process_two_premises(
            '<(~, boy, girl) --> [strong]>. %0.90;0.90%', 
            None,
            32
        )
        self.assertTrue(
            output_contains(tasks_derived, '<boy --> [strong]>. %0.90;0.73%')
        )

        pass

if __name__ == '__main__':

    test_classes_to_run = [
        TEST_NAL3
    ]

    loader = unittest.TestLoader()

    suites = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites.append(suite)
        
    suites = unittest.TestSuite(suites)

    runner = unittest.TextTestRunner()
    results = runner.run(suites)