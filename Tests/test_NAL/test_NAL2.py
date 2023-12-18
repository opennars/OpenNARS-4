import unittest

from pynars import Narsese
from pynars.NAL.MetaLevelInference.VariableSubstitution import *

from Tests.utils_for_test import *


class TEST_NAL2(unittest.TestCase):
    def setUp(self):
        nars.reset()

    ''''''
    
    def test_revision(self):
        '''
        'Revision

        'Robin is similar to swan.
        <robin <-> swan>. %1.00;0.90%

        'I think robin is not similar to swan.
        <robin <-> swan>. %0.10;0.60% 

        1

        'Robin is probably similar to swan. 
        ''outputMustContain('<robin <-> swan>. %0.87;0.91%')
        '''

        tasks_derived = process_two_premises(
            '<robin <-> swan>. %1.00;0.90%',
            '<robin <-> swan>. %0.10;0.60%',
            2
        )
        self.assertTrue(
            output_contains(tasks_derived, '<robin <-> swan>. %0.87;0.91%')
        )

    
    def test_comparison(self):
        '''
        'Comparison

        'Swan is a type of swimmer.
        <swan --> swimmer>. %0.90;0.90% 

        'Swan is a type of bird. 
        <swan --> bird>. %1.00;0.90%

        3

        'I guess that bird is similar to swimmer.
        ''outputMustContain('<bird <-> swimmer>. %0.90;0.45%')
        '''

        tasks_derived = process_two_premises(
            '<swan --> swimmer>. %0.90;0.90%', 
            '<swan --> bird>. %1.00;0.90%', 
            3
        )
        self.assertTrue(
            output_contains(tasks_derived, '<bird <-> swimmer>. %0.90;0.45%')
        )
        
        pass  

    def test_backward_inference(self):
        '''
        'Backward inference

        'Bird is a type of swimmer.
        <bird --> swimmer>. %1.00;0.90%
        
        'What is a swimmer?
        <{?1} --> swimmer>?

        5

        'What is a bird?
        ''outputMustContain('<{?1} --> bird>?')
        '''

        tasks_derived = process_two_premises(
            '<bird --> swimmer>. %1.00;0.90%', 
            '<{?1} --> swimmer>?', 
            20
        )
        self.assertTrue(
            output_contains(tasks_derived, '<{?1} --> bird>?')
        )
        
        pass  


    def test_comparison(self):
        '''
        'Comparison

        'Sport is a type of competition. 
        <sport --> competition>. %1.00;0.90%

        'Chess is a type of competition. 
        <chess --> competition>. %0.90;0.90% 

        3

        'I guess chess is similar to sport.
        ''outputMustContain('<chess <-> sport>. %0.90;0.45%')
        '''

        tasks_derived = process_two_premises(
            '<sport --> competition>. %1.00;0.90%', 
            '<chess --> competition>. %0.90;0.90% ', 
            5 
        )
        self.assertTrue(
            output_contains(tasks_derived, '<chess <-> sport>. %0.90;0.45%')
        )
        
        pass  

    def test_analogy_0(self):
        '''
        'Analogy

        'Swan is a type of swimmer. 
        <swan --> swimmer>. %1.00;0.90%

        'Gull is similar to swan. 
        <gull <-> swan>. %1.00;0.90%

        3

        'I think gull is a type of swimmer.
        ''outputMustContain('<gull --> swimmer>. %1.00;0.81%')
        '''

        tasks_derived = process_two_premises(
            '<swan --> swimmer>. %1.00;0.90%', 
            '<gull <-> swan>. %1.00;0.90%', 
            5
        )
        self.assertTrue(
            output_contains(tasks_derived, '<gull --> swimmer>. %1.00;0.81%')
        )
        pass

    def test_analogy_1(self):
        '''
        'Analogy

        'Gull is a type of swimmer. 
        <gull --> swimmer>. %1.00;0.90%

        'Gull is similar to a swan. 
        <gull <-> swan>. %1.00;0.90%

        3

        'I believe a swan is a type of swimmer. 
        ''outputMustContain('<swan --> swimmer>. %1.00;0.81%')
        '''

        tasks_derived = process_two_premises(
            '<gull --> swimmer>. %1.00;0.90%', 
            '<gull <-> swan>. %1.00;0.90%', 
            5
        )
        self.assertTrue(
            output_contains(tasks_derived, '<swan --> swimmer>. %1.00;0.81%')
        )
        pass
    
    def test_resemblance(self):
        '''
        'Resemblance

        'Robin is similar to swan. 
        <robin <-> swan>. %1.00;0.90%

        'Gull is similar to swan. 
        <gull <-> swan>. %1.00;0.90%

        3

        'Gull is similar to robin.
        ''outputMustContain('<gull <-> robin>. %1.00;0.81%')
        '''

        tasks_derived = process_two_premises(
            '<robin <-> swan>. %1.00;0.90%', 
            '<gull <-> swan>. %1.00;0.90%', 
            5
        )
        self.assertTrue(
            output_contains(tasks_derived, '<gull <-> robin>. %1.00;0.81%')
        )
        pass


    def test_conversions_between_inheritance_and_similarity(self):
        '''
        'Conversions between inheritance and similarity

        'Swan is a type of bird. 
        <swan --> bird>. %1.00;0.90%

        'Bird is not a type of swan. 
        <bird --> swan>. %0.10;0.90%

        1

        'Bird is different from swan. 
        ''outputMustContain('<bird <-> swan>. %0.10;0.81%')
        '''

        tasks_derived = process_two_premises(
            '<swan --> bird>. %1.00;0.90%', 
            '<bird --> swan>. %0.10;0.90%', 
            10
        )
        self.assertTrue(
            output_contains(tasks_derived, '<bird <-> swan>. %0.10;0.81%')
        )
        pass

    def test_structure_transformation_0(self):
        '''
        'Structure transformation

        'Bright is similar to smart. 
        <bright <-> smart>. %0.90;0.90% 

        'Is bright thing a type of smart thing?
        <[smart] --> [bright]>?

        6

        'Bright thing is a type of smart thing. 
        ''outputMustContain('<[bright] <-> [smart]>. %0.90;0.90%')
        ''outputMustContain('<[smart] --> [bright]>. %0.90;0.66%')
        '''

        tasks_derived = process_two_premises(
            '<bright <-> smart>. %0.90;0.90%', 
            '<[smart] --> [bright]>?', 
            10
        )
        self.assertTrue(
            output_contains(tasks_derived, '<[bright] <-> [smart]>. %0.90;0.90%')
        )
        self.assertTrue(
            output_contains(tasks_derived, '<[smart] --> [bright]>. %0.90;0.66%')
        )
        pass

    def test_structure_transformation_1(self):
        '''
        'Structure transformation

        'Birdie is similar to Tweety
        <Birdie <-> Tweety>. %0.90;0.90%

        'Is Birdie similar to Tweety?
        <{Birdie} <-> {Tweety}>?  

        6

        'Birdie is similar to Tweety. 
        ''outputMustContain('<{Birdie} <-> {Tweety}>. %0.90;0.73%')
        '''

        tasks_derived = process_two_premises(
            '<Birdie <-> Tweety>. %0.90;0.90%', 
            '<{Birdie} <-> {Tweety}>?', 
            10
        )
        self.assertTrue(
            output_contains(tasks_derived, '<{Birdie} <-> {Tweety}>. %0.90;0.73%')
        )
        pass

    def test_conversions_between_inheritance_and_similarity_0(self):
        '''
        'Conversions between inheritance and similarity

        'Swan is a type of bird. 
        <swan --> bird>. %1.00;0.90%

        'Bird is different from swan. 
        <bird <-> swan>. %0.10;0.90% 

        1

        'Bird is probably not a type of swan. 
        ''outputMustContain('<bird --> swan>. %0.10;0.73%')
        '''

        tasks_derived = process_two_premises(
            '<swan --> bird>. %1.00;0.90%', 
            '<bird <-> swan>. %0.10;0.90%', 
            10
        )
        self.assertTrue(
            output_contains(tasks_derived, '<bird --> swan>. %0.10;0.73%')
        )
        pass

    
    def test_conversions_between_inheritance_and_similarity_1(self):
        '''
        'Conversions between inheritance and similarity

        'Swan is a type of bird. 
        <swan --> bird>. %0.90;0.90%


        'Is bird similar to swan?
        <bird <-> swan>?

        6
        
        'I guess that bird is similar to swan. 
        ''outputMustContain('<bird <-> swan>. %0.90;0.47%')
        '''

        tasks_derived = process_two_premises(
            '<swan --> bird>. %0.90;0.90%', 
            '<bird <-> swan>?', 
            10
        )
        self.assertTrue(
            output_contains(tasks_derived, '<bird <-> swan>. %0.90;0.47%')
        )
        pass


    def test_conversions_between_inheritance_and_similarity_2(self):
        '''
        'Conversions between inheritance and similarity

        'a bird is similar to a swan. 
        <bird <-> swan>. %0.90;0.90%

        'Is swan a type of bird?
        <swan --> bird>?  

        6

        'A swan is a type of bird. 
        ''outputMustContain('<swan --> bird>. %0.90;0.81%')
        '''

        tasks_derived = process_two_premises(
            '<bird <-> swan>. %0.90;0.90%', 
            '<swan --> bird>?', 
            10
        )
        self.assertTrue(
            output_contains(tasks_derived, '<swan --> bird>. %0.90;0.81%')
        )
        pass


    def test_translating_instance_into_inheritance(self):
        '''
        'Translating instance into inheritance

        'Tweety is a bird.
        <Tweety {-- bird>. %1.00;0.90%

        1

        ''outputMustContain('<{Tweety} --> bird>. %1.00;0.90%')
        '//expect.outEmpty
        '''
        tasks_derived = process_two_premises(
            '<Tweety {-- bird>. %1.00;0.90%',
            None,
            1
        )
        self.assertTrue(
            output_contains(tasks_derived, '<{Tweety} --> bird>. %1.00;0.90%')
        )
        pass

    
    def test_translating_property_into_inheritance(self):
        '''
        'Translating property into inheritance

        'Ravens are black. 
        <raven --] black>. %1.00;0.90%

        1

        ''outputMustContain('<raven --> [black]>. %1.00;0.90%')
        '''
        tasks_derived = process_two_premises(
            '<raven --] black>. %1.00;0.90%',
            None,
            1
        )
        self.assertTrue(
            output_contains(tasks_derived, '<raven --> [black]>. %1.00;0.90%')
        )
        pass


    def test_translating_instance_property_into_inheritance(self):
        '''
        'Translating instance-property into inheritance

        'Tweety is yellow.
        <Tweety {-] yellow>. %1.00;0.90%

        1

        ''outputMustContain('<{Tweety} --> [yellow]>. %1.00;0.90%')
        '''
        tasks_derived = process_two_premises(
            '<Tweety {-] yellow>. %1.00;0.90%',
            None,
            1
        )
        self.assertTrue(
            output_contains(tasks_derived, '<{Tweety} --> [yellow]>. %1.00;0.90%')
        )
        pass

    def test_set_definition_0(self):
        '''
        'Set definition

        'Tweety is Birdie. 
        <{Tweety} --> {Birdie}>. %1.00;0.90%

        3

        'Birdie is similar to Tweety. 
        ''outputMustContain('<{Birdie} <-> {Tweety}>. %1.00;0.90%')
        '''
        tasks_derived = process_two_premises(
            '<{Tweety} --> {Birdie}>. %1.00;0.90%',
            None,
            3
        )
        self.assertTrue(
            output_contains(tasks_derived, '<{Birdie} <-> {Tweety}>. %1.00;0.90%')
        )
        pass


    def test_set_definition_1(self):
        '''
        'Set definition

        'Smart thing is a type of bright thing. 
        <[smart] --> [bright]>. %1.00;0.90%

        1

        'Bright thing is similar to smart thing. 
        ''outputMustContain('<[bright] <-> [smart]>. %1.00;0.90%')
        '''
        tasks_derived = process_two_premises(
            '<[smart] --> [bright]>. %1.00;0.90%',
            None,
            1
        )
        self.assertTrue(
            output_contains(tasks_derived, '<[bright] <-> [smart]>. %1.00;0.90%')
        )
        pass

    
    def test_set_definition_2(self):
        '''
        'Set definition

        'Birdie is similar to Tweety. 
        <{Birdie} <-> {Tweety}>. %1.00;0.90%

        1

        'Birdie is similar to Tweety. 
        ''outputMustContain('<Birdie <-> Tweety>. %1.00;0.90%')

        'Tweety is Birdie. 
        ''outputMustContain('<{Tweety} --> {Birdie}>. %1.00;0.90%')
        '''
        tasks_derived = process_two_premises(
            '<{Birdie} <-> {Tweety}>. %1.00;0.90%',
            None,
            1
        )
        self.assertTrue(
            output_contains(tasks_derived, '<Birdie <-> Tweety>. %1.00;0.90%')
        )
        
        self.assertTrue(
            output_contains(tasks_derived, '<{Tweety} --> {Birdie}>. %1.00;0.90%')
        )
        pass

    def test_set_definition_3(self):
        '''
        'Set definition

        'Bright thing is similar to smart thing. 
        <[bright] <-> [smart]>. %1.00;0.90%

        1

        'Bright is similar to smart. 
        ''outputMustContain('<bright <-> smart>. %1.00;0.90%')

        'Bright thing is a type of smart thing. 
        ''outputMustContain('<[bright] --> [smart]>. %1.00;0.90%')
        '''
        tasks_derived = process_two_premises(
            '<[bright] <-> [smart]>. %1.00;0.90%',
            None,
            1
        )
        self.assertTrue(
            output_contains(tasks_derived, '<bright <-> smart>. %1.00;0.90%')
        )
        
        self.assertTrue(
            output_contains(tasks_derived, '<[bright] --> [smart]>. %1.00;0.90%')
        )
        pass

if __name__ == '__main__':

    test_classes_to_run = [
        TEST_NAL2
    ]

    loader = unittest.TestLoader()

    suites = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites.append(suite)
        
    suites = unittest.TestSuite(suites)

    runner = unittest.TextTestRunner()
    results = runner.run(suites)