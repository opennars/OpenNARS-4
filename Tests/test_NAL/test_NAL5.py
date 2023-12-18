'''
test NAL5 
'''
import unittest
from pathlib import Path

from pynars import NARS, Narsese
import Tests.utils_for_test as utils_for_test
from pynars.NAL.MetaLevelInference.VariableSubstitution import *
from pynars.NARS import Reasoner as Reasoner
from pynars.NARS.DataStructures import Bag, Concept, Table, Task
from pynars.NARS.DataStructures._py.Link import TaskLink, TermLink
from pynars.NARS.RuleMap import RuleMap
from pynars.Narsese import (Compound, Connector, Copula, Judgement, Statement, Term,
                     Truth, Variable, VarPrefix)
from Tests.utils_for_test import *

# utils_for_test.rule_map = RuleMap_v2()


class TEST_NAL5(unittest.TestCase):
    def setUp(self):
        nars.reset()

    ''''''
    
    def test_revision(self):
        '''
        'Revision

        'If robin can fly then robin is a type of bird. 
        <<robin --> [flying]> ==> <robin --> bird>>. %1.00;0.90%

        'If robin can fly then robin may not a type of bird. 
        <<robin --> [flying]> ==> <robin --> bird>>. %0.00;0.60% 

        1

        'If robin can fly then robin is a type of bird. 
        ''outputMustContain('<<robin --> [flying]> ==> <robin --> bird>>. %0.86;0.91%')
        '''
        tasks_derived = process_two_premises(
            '<<robin --> [flying]> ==> <robin --> bird>>. %1.00;0.90%',
            '<<robin --> [flying]> ==> <robin --> bird>>. %0.00;0.60% ',
            2
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<robin --> [flying]> ==> <robin --> bird>>. %0.86;0.91%')
        )
        
        pass


    def test_deduction(self):
        '''
        'Deduction

        'If robin is a type of bird then robin is a type of animal. 
        <<robin --> bird> ==> <robin --> animal>>. %1.00;0.9%

        'If robin can fly then robin is a type of bird. 
        <<robin --> [flying]> ==> <robin --> bird>>. %1.00;0.9%

        14

        'If robin can fly then robin is a type of animal. 
        ''outputMustContain('<<robin --> [flying]> ==> <robin --> animal>>. %1.00;0.81%')
        '''
        tasks_derived = process_two_premises(
            '<<robin --> bird> ==> <robin --> animal>>. %1.00;0.9%', 
            '<<robin --> [flying]> ==> <robin --> bird>>. %1.00;0.9%', 
            14
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<robin --> [flying]> ==> <robin --> animal>>. %1.00;0.81%')
        )
        pass
    
    def test_exemplification(self):
        '''
        'Exemplification

        'If robin can fly then robin is a type of bird. 
        <<robin --> [flying]> ==> <robin --> bird>>. %1.00;0.90%

        'If robin is a type of bird then robin is a type of animal. 
        <<robin --> bird> ==> <robin --> animal>>. %1.00;0.90%

        19

        'I guess if robin is a type of animal then robin can fly. 
        ''outputMustContain('<<robin --> animal> ==> <robin --> [flying]>>. %1.00;0.45%')
        '''
        tasks_derived = process_two_premises(
            '<<robin --> [flying]> ==> <robin --> bird>>. %1.00;0.90%', 
            '<<robin --> bird> ==> <robin --> animal>>. %1.00;0.90%', 
            19
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<robin --> animal> ==> <robin --> [flying]>>. %1.00;0.45%')
        )
        pass


    def test_induction(self):
        '''
        'Induction

        'If robin is a type of bird then robin is a type of animal. 
        <<robin --> bird> ==> <robin --> animal>>. %1.00;0.90%

        'If robin is a type of bird then robin can fly. 
        <<robin --> bird> ==> <robin --> [flying]>>. %0.80;0.90% 

        140

        'I guess if robin can fly then robin is a type of animal. 
        ''outputMustContain('<<robin --> [flying]> ==> <robin --> animal>>. %1.00;0.39%')

        'I guess if robin is a type of animal then robin can fly. 
        ''outputMustContain('<<robin --> animal> ==> <robin --> [flying]>>. %0.80;0.45%')
        '''
        tasks_derived = process_two_premises(
            '<<robin --> bird> ==> <robin --> animal>>. %1.00;0.90%', 
            '<<robin --> bird> ==> <robin --> [flying]>>. %0.80;0.90%', 
            14
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<robin --> animal> ==> <robin --> [flying]>>. %0.80;0.45%')
        )
        pass


    def test_abduction(self):
        '''
        'Abduction

        'If robin is a type of bird then robin is a type of animal. 
        <<robin --> bird> ==> <robin --> animal>>. %1.00;0.90%

        'If robin can fly then robin is probably a type of animal. 
        <<robin --> [flying]> ==> <robin --> animal>>. %0.80;0.90%

        19

        'I guess if robin is a type of bird then robin can fly. 
        ''outputMustContain('<<robin --> bird> ==> <robin --> [flying]>>. %1.00;0.39%')

        'I guess if robin can fly then robin is a type of bird.
        ''outputMustContain('<<robin --> [flying]> ==> <robin --> bird>>. %0.80;0.45%')
        '''
        tasks_derived = process_two_premises(
            '<<robin --> bird> ==> <robin --> animal>>. %1.00;0.90%', 
            '<<robin --> [flying]> ==> <robin --> animal>>. %0.80;0.90%', 
            19
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<robin --> [flying]> ==> <robin --> bird>>. %0.80;0.45%')
        )
        pass

    
    def test_conditional_deduction_0(self):
        '''
        'Detachment

        'If robin is a type of bird then robin can fly. 
        <<robin --> bird> ==> <robin --> animal>>. %1.00;0.90% 

        'Robin is a type of bird. 
        <robin --> bird>. %1.00;0.90%

        1

        'Robin is a type of animal. 
        ''outputMustContain('<robin --> animal>. %1.00;0.81%')
        '''
        tasks_derived = process_two_premises(
            '<<robin --> bird> ==> <robin --> animal>>. %1.00;0.90%', 
            '<robin --> bird>. %1.00;0.90%', 
            6)
        self.assertTrue(
            output_contains(tasks_derived, '<robin --> animal>. %1.00;0.81%')
        )

        nars.reset()

        tasks_derived = process_two_premises(
            '<robin --> bird>. %1.00;0.90%', 
            '<<robin --> bird> ==> <robin --> animal>>. %1.00;0.90%', 
            6
        )
        self.assertTrue(
            output_contains(tasks_derived, '<robin --> animal>. %1.00;0.81%')
        )
        pass


    def test_conditional_abduction(self):
        '''
        'Detachment

        'Usually if robin is a type of bird then robin is a type of animal. 
        <<robin --> bird> ==> <robin --> animal>>. %0.70;0.90% 

        'Robin is a type of animal. 
        <robin --> animal>. %1.00;0.90%

        1

        'I guess robin is a type of bird. 
        ''outputMustContain('<robin --> bird>. %1.00;0.36%')
        '''
        tasks_derived = process_two_premises(
            '<<robin --> bird> ==> <robin --> animal>>. %0.70;0.90%', 
            '<robin --> animal>. %1.00;0.90%', 
            6
        )
        self.assertTrue(
            output_contains(tasks_derived, '<robin --> bird>. %1.00;0.36%')
        )
        pass


    def test_conditional_abduction_0(self):
        '''
        'Detachment

        'Usually if robin is a type of bird then robin is a type of animal. 
        <<robin --> bird> ==> <robin --> animal>>. %0.70;0.90% 

        'Robin is a type of animal. 
        <robin --> animal>. %1.00;0.90%

        1

        'I guess robin is a type of bird. 
        ''outputMustContain('<robin --> bird>. %1.00;0.36%')
        '''
        tasks_derived = process_two_premises(
            '<<robin --> bird> ==> <robin --> animal>>. %0.70;0.90%', 
            '<robin --> animal>. %1.00;0.90%', 
            6
        )
        self.assertTrue(
            output_contains(tasks_derived, '<robin --> bird>. %1.00;0.36%')
        )
        pass



    def test_comparison_0(self):
        '''
        'Detachment

        'If robin is a type of bird then robin is a type of animal. 
        <<robin --> bird> ==> <robin --> animal>>. %1.00;0.90%

        'If robin is a type of bird then robin can fly.
        <<robin --> bird> ==> <robin --> [flying]>>. %0.80;0.90%  

        14

        'I guess robin is a type of animal if and only if robin can fly.
        ''outputMustContain('<<robin --> [flying]> <=> <robin --> animal>>. %0.80;0.45%')
        '''
        tasks_derived = process_two_premises(
            '<<robin --> bird> ==> <robin --> animal>>. %1.00;0.90%', 
            '<<robin --> bird> ==> <robin --> [flying]>>. %0.80;0.90%', 
            14
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<robin --> [flying]> <=> <robin --> animal>>. %0.80;0.45%')
        )
        pass


    def test_comparison_1(self):
        '''
        'Detachment

        'If robin is a type of bird then usually robin is a type of animal. 
        <<robin --> bird> ==> <robin --> animal>>. %0.70;0.90%

        'If robin can fly then robin is a type of animal. 
        <<robin --> [flying]> ==> <robin --> animal>>. %1.00;0.90%

        19

        'I guess robin is a type of bird if and only if robin can fly. 
        ''outputMustContain('<<robin --> [flying]> <=> <robin --> bird>>. %0.70;0.45%')
        '''
        tasks_derived = process_two_premises(
            '<<robin --> bird> ==> <robin --> animal>>. %0.70;0.90%', 
            '<<robin --> [flying]> ==> <robin --> animal>>. %1.00;0.90%', 
            19
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<robin --> [flying]> <=> <robin --> bird>>. %0.70;0.45%')
        )
        pass


    def test_analogy(self):
        '''
        'Detachment

        'If robin is a type of bird then robin is a type of animal. 
        <<robin --> bird> ==> <robin --> animal>>. %1.00;0.90%

        'Usually, robin is a type of bird if and only if robin can fly.
        <<robin --> bird> <=> <robin --> [flying]>>. %0.80;0.90% 

        14

        'If robin can fly then probably robin is a type of animal. 
        ''outputMustContain('<<robin --> [flying]> ==> <robin --> animal>>. %0.80;0.65%')
        '''
        tasks_derived = process_two_premises(
            '<<robin --> bird> ==> <robin --> animal>>. %1.00;0.90%', 
            '<<robin --> bird> <=> <robin --> [flying]>>. %0.80;0.90%', 
            14
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<robin --> [flying]> ==> <robin --> animal>>. %0.80;0.65%')
        )
        pass


    def test_conditional_analogy(self):
        '''
        'Detachment

        'Robin is a type of bird. 
        <robin --> bird>. %1.00;0.90%

        'Usually, robin is a type of bird if and only if robin can fly. 
        <<robin --> bird> <=> <robin --> [flying]>>. %0.80;0.90% 

        1

        'I guess usually robin can fly.
        ''outputMustContain('<robin --> [flying]>. %0.80;0.65%')
        '''
        tasks_derived = process_two_premises(
            '<robin --> bird>. %1.00;0.90%', 
            '<<robin --> bird> <=> <robin --> [flying]>>. %0.80;0.90%', 
            10
        )
        self.assertTrue(
            output_contains(tasks_derived, '<robin --> [flying]>. %0.80;0.65%')
        )

        nars.reset()

        tasks_derived = process_two_premises(
            '<<robin --> bird> <=> <robin --> [flying]>>. %0.80;0.90%', 
            '<robin --> bird>. %1.00;0.90%', 
            10
        )
        self.assertTrue(
            output_contains(tasks_derived, '<robin --> [flying]>. %0.80;0.65%')
        )

        nars.reset()

        tasks_derived = process_two_premises(
            '<robin --> bird>. %1.00;0.90%', 
            '<<robin --> [flying]> <=> <robin --> bird>>. %0.80;0.90%', 
            10
        )
        self.assertTrue(
            output_contains(tasks_derived, '<robin --> [flying]>. %0.80;0.65%')
        )

        nars.reset()

        tasks_derived = process_two_premises(
            '<<robin --> [flying]> <=> <robin --> bird>>. %0.80;0.90%', 
            '<robin --> bird>. %1.00;0.90%', 
            10
        )
        self.assertTrue(
            output_contains(tasks_derived, '<robin --> [flying]>. %0.80;0.65%')
        )
        pass


    def test_resemblance(self):
        '''
        'Detachment

        'Robin is a type of animal if and only if robin is a type of bird. 
        <<robin --> animal> <=> <robin --> bird>>. %1.00;0.90%

        'Robin is a type of bird if and only if robin can fly. 
        <<robin --> bird> <=> <robin --> [flying]>>. %0.90;0.90% 

        19

        'Robin is a type of animal if and only if robin can fly. 
        ''outputMustContain('<<robin --> [flying]> <=> <robin --> animal>>. %0.90;0.81%')
        '''
        tasks_derived = process_two_premises(
            '<<robin --> animal> <=> <robin --> bird>>. %1.00;0.90%', 
            '<<robin --> bird> <=> <robin --> [flying]>>. %0.90;0.90% ', 
            19
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<robin --> [flying]> <=> <robin --> animal>>. %0.90;0.81%')
        )
        pass


    def test_conversions_between_implication_and_equivalence(self):
        '''
        'conversions between Implication and Equivalence

        'If robin can fly then robin is a type of bird. 
        <<robin --> [flying]> ==> <robin --> bird>>. %0.90;0.90% 

        'If robin is a type of bird then robin can fly.
        <<robin --> bird> ==> <robin --> [flying]>>. %0.90;0.90% 

        7

        'Robin can fly if and only if robin is a type of bird. 
        ''outputMustContain('<<robin --> [flying]> <=> <robin --> bird>>. %0.81;0.81%')
        '''
        tasks_derived = process_two_premises(
            '<<robin --> [flying]> ==> <robin --> bird>>. %0.90;0.90%', 
            '<<robin --> bird> ==> <robin --> [flying]>>. %0.90;0.90%', 
            7
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<robin --> [flying]> <=> <robin --> bird>>. %0.81;0.81%')
        )
        pass


    def test_conjunction_0(self):
        '''
        'compound composition, two premises

        'If robin is a type of bird then robin is a type of animal. 
        <<robin --> bird> ==> <robin --> animal>>. %1.00;0.90%

        'If robin is a type of bird then robin can fly.
        <<robin --> bird> ==> <robin --> [flying]>>. %0.90;0.90%  

        14

        'If robin is a type of bird then usually robin is a type of animal and can fly. 
        ''outputMustContain('<<robin --> bird> ==> (&&,<robin --> [flying]>,<robin --> animal>)>. %0.90;0.81%')
        '''
        tasks_derived = process_two_premises(
            '<<robin --> bird> ==> <robin --> animal>>. %1.00;0.90%', 
            '<<robin --> bird> ==> <robin --> [flying]>>. %0.90;0.90%', 
            14
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<robin --> bird> ==> (&&,<robin --> [flying]>,<robin --> animal>)>. %0.90;0.81%')
        )
        pass


    def test_conjunction_1(self):
        '''
        'compound composition, two premises

        'If robin is a type of bird then robin is a type of animal. 
        <<robin --> bird> ==> <robin --> animal>>. %1.00;0.90%

        'If robin can fly then robin is a type of animal. 
        <<robin --> [flying]> ==> <robin --> animal>>. %0.90;0.90% 

        19

        'If robin can fly and is a type of bird then robin is a type of animal. 
        ''outputMustContain('<(&&,<robin --> [flying]>,<robin --> bird>) ==> <robin --> animal>>. %1.00;0.81%')
        '''
        tasks_derived = process_two_premises(
            '<<robin --> bird> ==> <robin --> animal>>. %1.00;0.90%', 
            '<<robin --> [flying]> ==> <robin --> animal>>. %0.90;0.90% ', 
            19
        )
        self.assertTrue(
            output_contains(tasks_derived, '<(&&,<robin --> [flying]>,<robin --> bird>) ==> <robin --> animal>>. %1.00;0.81%')
        )
        pass


    def test_disjunction_0(self):
        '''
        'compound composition, two premises

        'If robin is a type of bird then robin is a type of animal. 
        <<robin --> bird> ==> <robin --> animal>>. %1.00;0.90%

        'If robin is a type of bird then robin can fly.
        <<robin --> bird> ==> <robin --> [flying]>>. %0.90;0.90%  

        14

        'If robin is a type of bird then robin is a type of animal or can fly. 
        ''outputMustContain('<<robin --> bird> ==> (||,<robin --> [flying]>,<robin --> animal>)>. %1.00;0.81%')
        '''
        tasks_derived = process_two_premises(
            '<<robin --> bird> ==> <robin --> animal>>. %1.00;0.90%', 
            '<<robin --> bird> ==> <robin --> [flying]>>. %0.90;0.90%', 
            14
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<robin --> bird> ==> (||,<robin --> [flying]>,<robin --> animal>)>. %1.00;0.81%')
        )
        pass

    def test_disjunction_1(self):
        '''
        'compound composition, two premises

        'If robin is a type of bird then robin is a type of animal. 
        <<robin --> bird> ==> <robin --> animal>>. %1.00;0.90%

        'If robin can fly then robin is a type of animal. 
        <<robin --> [flying]> ==> <robin --> animal>>. %0.90;0.90% 

        19

        'If robin can fly or is a type of bird then robin is a type of animal. 
        ''outputMustContain('<(||,<robin --> [flying]>,<robin --> bird>) ==> <robin --> animal>>. %0.90;0.81%')
        '''
        tasks_derived = process_two_premises(
            '<<robin --> bird> ==> <robin --> animal>>. %1.00;0.90%', 
            '<<robin --> [flying]> ==> <robin --> animal>>. %0.90;0.90% ', 
            19
        )
        self.assertTrue(
            output_contains(tasks_derived, '<(||,<robin --> [flying]>,<robin --> bird>) ==> <robin --> animal>>. %0.90;0.81%')
        )
        pass


    def test_decomposition_0(self):
        '''
        'compound decomposition, two premises

        'If robin is a type of bird then robin is not a type of flying animal. 
        <<robin --> bird> ==> (&&,<robin --> animal>,<robin --> [flying]>)>. %0.00;0.90% 

        'If robin is a type of bird then robin can fly. 
        <<robin --> bird> ==> <robin --> [flying]>>. %1.00;0.90%

        8

        'It is unlikely that if a robin is a type of bird then robin is a type of animal. 
        ''outputMustContain('<<robin --> bird> ==> <robin --> animal>>. %0.00;0.81%')
        '''
        tasks_derived = process_two_premises(
            '<<robin --> bird> ==> (&&,<robin --> animal>,<robin --> [flying]>)>. %0.00;0.90%', 
            '<<robin --> bird> ==> <robin --> [flying]>>. %1.00;0.90%', 
            8
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<robin --> bird> ==> <robin --> animal>>. %0.00;0.81%')
        )
        pass


    def test_decomposition_1(self):
        '''
        'compound decomposition, two premises

        'Robin cannot be both a flyer and a swimmer. 
        (&&,<robin --> [flying]>,<robin --> swimmer>). %0.00;0.90% 

        'Robin can fly. 
        <robin --> [flying]>. %1.00;0.90%

        6

        'Robin cannot swim. 
        ''outputMustContain('<robin --> swimmer>. %0.00;0.81%')
        '''
        tasks_derived = process_two_premises(
            '(&&,<robin --> [flying]>,<robin --> swimmer>). %0.00;0.90% ', 
            '<robin --> [flying]>. %1.00;0.90%', 
            6
        )
        self.assertTrue(
            output_contains(tasks_derived, '<robin --> swimmer>. %0.00;0.81%')
        )

        nars.reset()

        tasks_derived = process_two_premises(
            '<robin --> [flying]>. %1.00;0.90%', 
            '(&&,<robin --> [flying]>,<robin --> swimmer>). %0.00;0.90% ', 
            6
        )
        self.assertTrue(
            output_contains(tasks_derived, '<robin --> swimmer>. %0.00;0.81%')
        )

        pass


    def test_decomposition_2(self):
        '''
        'compound decomposition, two premises

        'Robin can fly or swim. 
        (||,<robin --> [flying]>,<robin --> swimmer>). %1.00;0.90% 

        'Robin cannot swim.
        <robin --> swimmer>. %0.00;0.90% 

        2

        'Robin can fly. 
        ''outputMustContain('<robin --> [flying]>. %1.00;0.81%')
        '''
        tasks_derived = process_two_premises(
            '(||,<robin --> [flying]>,<robin --> swimmer>). %1.00;0.90% ', 
            '<robin --> swimmer>. %0.00;0.90%', 
            6
        )
        self.assertTrue(
            output_contains(tasks_derived, '<robin --> [flying]>. %1.00;0.81%')
        )

    
    def test_composition_0(self):
        '''
        'compound decomposition, two premises

        'Robin can fly. 
        <robin --> [flying]>. %1.00;0.90%

        'Can robin fly or swim?
        (||,<robin --> [flying]>,<robin --> swimmer>)?  

        7
        ''//+1 from original

        'Robin can fly or swim.
        ''outputMustContain('(||,<robin --> [flying]>,<robin --> swimmer>). %1.00;0.81%')
        '''
        tasks_derived = process_two_premises(
            '<robin --> [flying]>. %1.00;0.90%', 
            '(||,<robin --> [flying]>,<robin --> swimmer>)?', 
            7
        )
        self.assertTrue(
            output_contains(tasks_derived, '(||,<robin --> [flying]>,<robin --> swimmer>). %1.00;0.81%')
        )
        pass


    def test_composition_1(self):
        '''
        'compound decomposition, two premises

        'Robin can fly and swim.
        $0.90;0.90$ (&&,<robin --> swimmer>,<robin --> [flying]>). %0.90;0.90%


        1

        'Robin can swim. 
        ''outputMustContain('<robin --> swimmer>. %0.90;0.73%')

        5
        ''//+2 from original

        'Robin can fly. 
        ''outputMustContain('<robin --> [flying]>. %0.90;0.73%')
        '''
        tasks_derived = process_two_premises(
            '$0.90;0.90$ (&&,<robin --> swimmer>,<robin --> [flying]>). %0.90;0.90%', 
            6
        )
        self.assertTrue(
            output_contains(tasks_derived, '<robin --> swimmer>. %0.90;0.73%')
        )

        self.assertTrue(
            output_contains(tasks_derived, '<robin --> [flying]>. %0.90;0.73%')
        )

    
    def test_negation_0(self):
        '''
        'negation

        'It is unlikely that robin cannot fly. 
        (--,<robin --> [flying]>). %0.10;0.90% 

        3

        'Robin can fly. 
        ''outputMustContain('<robin --> [flying]>. %0.90;0.90%')
        '''

        tasks_derived = process_two_premises(
            '(--,<robin --> [flying]>). %0.10;0.90%', 
            '<robin --> [flying]>?',
            3
        )
        self.assertTrue(
            output_contains(tasks_derived, '<robin --> [flying]>. %0.10;0.90%')
        )

    
    def test_negation_1(self):
        '''
        'negation

        'Robin can fly. 
        <robin --> [flying]>. %0.90;0.90%

        'Can robin fly or not?
        (--,<robin --> [flying]>)?  

        ''//15
        30

        'It is unlikely that robin cannot fly. 
        ''outputMustContain('(--,<robin --> [flying]>). %0.10;0.90%')
        '''

        tasks_derived = process_two_premises(
            '<robin --> [flying]>. %0.90;0.90%', 
            '(--,<robin --> [flying]>)?', 
            30
        )
        self.assertTrue(
            output_contains(tasks_derived, '(--,<robin --> [flying]>). %0.10;0.90%')
        )


    def test_contraposition_0(self):
        '''
        'contraposition

        'It is unlikely that if robin is not a type of bird then robin can fly. 
        <(--,<robin --> bird>) ==> <robin --> [flying]>>. %0.10;0.90%

        'If robin cannot fly then is robin a type of bird?
        <(--,<robin --> [flying]>) ==> <robin --> bird>>?

        29

        'I guess it is unlikely that if robin cannot fly then robin is a type of bird.
        ''outputMustContain('<(--,<robin --> [flying]>) ==> <robin --> bird>>. %0.00;0.45%')

        561
        '''
        tasks_derived = process_two_premises(
            '<(--,<robin --> bird>) ==> <robin --> [flying]>>. %0.10;0.90%', 
            '<(--,<robin --> [flying]>) ==> <robin --> bird>>?', 
            30,
        )
        self.assertTrue(
            output_contains(tasks_derived, '<(--,<robin --> [flying]>) ==> <robin --> bird>>. %0.00;0.45%')
        )
        pass


    def test_conditional_deduction_compound_eliminate_0(self):
        '''
        'conditional deduction

        'If robin can fly and has wings then robin is a bird.
        <(&&,<robin --> [flying]>,<robin --> [with_wings]>) ==> <robin --> bird>>. %1.00;0.90%

        'robin can fly.
        <robin --> [flying]>. %1.00;0.90%

        1

        'If robin has wings then robin is a bird
        ''outputMustContain('<<robin --> [with_wings]> ==> <robin --> bird>>. %1.00;0.81%')
        '''
        tasks_derived = process_two_premises(
            '<(&&,<robin --> [flying]>,<robin --> [with_wings]>) ==> <robin --> bird>>. %1.00;0.90%', 
            '<robin --> [flying]>. %1.00;0.90%', 
            10
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<robin --> [with_wings]> ==> <robin --> bird>>. %1.00;0.81%')
        )

        nars.reset()

        tasks_derived = process_two_premises(
            '<robin --> [flying]>. %1.00;0.90%', 
            '<(&&,<robin --> [flying]>,<robin --> [with_wings]>) ==> <robin --> bird>>. %1.00;0.90%', 
            10
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<robin --> [with_wings]> ==> <robin --> bird>>. %1.00;0.81%')
        )


    def test_conditional_deduction_compound_eliminate_1(self):
        '''
        'conditional deduction

        'If robin can fly, has wings, and chirps, then robin is a bird
        <(&&,<robin --> [chirping]>,<robin --> [flying]>,<robin --> [with_wings]>) ==> <robin --> bird>>. %1.00;0.90%

        'robin can fly.
        <robin --> [flying]>. %1.00;0.90%

        5

        'If robin has wings and chirps then robin is a bird.
        ''outputMustContain('<(&&,<robin --> [chirping]>,<robin --> [with_wings]>) ==> <robin --> bird>>. %1.00;0.81%')
        '''
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '<(&&,<robin --> [chirping]>,<robin --> [flying]>,<robin --> [with_wings]>) ==> <robin --> bird>>. %1.00;0.90%', 
            '<robin --> [flying]>. %1.00;0.90%', 
            'robin.', index_task=(0,0,0), index_belief=(0,))
        tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 
        self.assertTrue(
            output_contains(tasks_derived, '<(&&,<robin --> [chirping]>,<robin --> [with_wings]>) ==> <robin --> bird>>. %1.00;0.81%')
        )
        pass


    def test_conditional_deduction_compound_replace_0(self):
        '''
        'conditional deduction

        'If robin is a bird and it's living, then robin is an animal
        <(&&,<robin --> bird>,<robin --> [living]>) ==> <robin --> animal>>. %1.00;0.90%

        'If robin can fly, then robin is a bird
        <<robin --> [flying]> ==> <robin --> bird>>. %1.00;0.90% 

        1

        'If robin is living and it can fly, then robin is an animal.
        ''outputMustContain('<(&&,<robin --> [flying]>,<robin --> [living]>) ==> <robin --> animal>>. %1.00;0.81%')
        '''
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '<(&&,<robin --> bird>,<robin --> [living]>) ==> <robin --> animal>>. %1.00;0.90%', 
            '<<robin --> [flying]> ==> <robin --> bird>>. %1.00;0.90% ', 
            'robin.', index_task=(0,0,0), index_belief=(0,0))
        tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 
        self.assertTrue(
            output_contains(tasks_derived, '<(&&,<robin --> [flying]>,<robin --> [living]>) ==> <robin --> animal>>. %1.00;0.81%')
        )

        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '<<robin --> [flying]> ==> <robin --> bird>>. %1.00;0.90% ', 
            '<(&&,<robin --> bird>,<robin --> [living]>) ==> <robin --> animal>>. %1.00;0.90%', 
            'robin.', index_task=(0,0), index_belief=(0,0,0))
        tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 
        self.assertTrue(
            output_contains(tasks_derived, '<(&&,<robin --> [flying]>,<robin --> [living]>) ==> <robin --> animal>>. %1.00;0.81%')
        )
        pass


    def test_conditional_abduction_compound_replace_1(self):
        '''
        'conditional abduction

        'If robin can fly then robin is a bird.
        <<robin --> [flying]> ==> <robin --> bird>>. %1.00;0.90%

        'If robin both swims and flys then robin is a bird.
        <(&&,<robin --> swimmer>,<robin --> [flying]>) ==> <robin --> bird>>. %1.00;0.90%

        7

        'I guess robin swims.
        ''outputMustContain('<robin --> swimmer>. %1.00;0.45%')
        '''
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '<(&&,<robin --> swimmer>,<robin --> [flying]>) ==> <robin --> bird>>. %1.00;0.90%', 
            '<<robin --> [flying]> ==> <robin --> bird>>. %1.00;0.90%', 
            'robin.', index_task=(0,0,0), index_belief=(0,0))
        tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 
        self.assertTrue(
            output_contains(tasks_derived, '<robin --> swimmer>. %1.00;0.45%')
        )
        pass


    def test_conditional_abduction_compound_replace_2(self):
        '''
        'conditional abduction

        'If robin can fly and it has wings, then robin is living.
        <(&&,<robin --> [flying]>,<robin --> [with_wings]>) ==> <robin --> [living]>>. %0.90;0.90%

        'If robin can fly and robin is a bird then robin is living.
        <(&&,<robin --> [flying]>,<robin --> bird>) ==> <robin --> [living]>>. %1.00;0.90%

        18

        'I guess if robin is a bird, then robin has wings.
        ''outputMustContain('<<robin --> bird> ==> <robin --> [with_wings]>>. %1.00;0.42%')

        'I guess if robin has wings, then robin is a bird.
        ''outputMustContain('<<robin --> [with_wings]> ==> <robin --> bird>>. %0.90;0.45%')
        '''
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '<(&&,<robin --> [flying]>,<robin --> [with_wings]>) ==> <robin --> [living]>>. %0.90;0.90%', 
            '<(&&,<robin --> [flying]>,<robin --> bird>) ==> <robin --> [living]>>. %1.00;0.90%', 
            'robin.', index_task=(0,0,0), index_belief=(0,0,0))
        tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 
        self.assertTrue(
            output_contains(tasks_derived, '<<robin --> bird> ==> <robin --> [with_wings]>>. %1.00;0.42%')
        )
        
        self.assertTrue(
            output_contains(tasks_derived, '<<robin --> [with_wings]> ==> <robin --> bird>>. %0.90;0.45%')
        )
        pass

    
    def test_conditional_induction_compose(self):
        '''
        'conditional induction

        'If robin can fly and robin chirps, then robin is a bird
        <(&&,<robin --> [chirping]>,<robin --> [flying]>) ==> <robin --> bird>>. %1.00;0.90%

        'If robin can fly then usually robin has a beak.
        <<robin --> [flying]> ==> <robin --> [with_beak]>>. %0.90;0.90%  

        18

        'I guess that if robin chirps and robin has a beak, then robin is a bird.
        ''outputMustContain('<(&&,<robin --> [chirping]>,<robin --> [with_beak]>) ==> <robin --> bird>>. %1.00;0.42%')
        '''
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '<(&&,<robin --> [chirping]>,<robin --> [flying]>) ==> <robin --> bird>>. %1.00;0.90%', 
            '<<robin --> [flying]> ==> <robin --> [with_beak]>>. %0.90;0.90%', 
            'robin.', index_task=(0,0,0), index_belief=(0,0))
        tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 
        self.assertTrue(
            output_contains(tasks_derived, '<(&&,<robin --> [chirping]>,<robin --> [with_beak]>) ==> <robin --> bird>>. %1.00;0.42%')
        )

        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '<<robin --> [flying]> ==> <robin --> [with_beak]>>. %0.90;0.90%', 
            '<(&&,<robin --> [chirping]>,<robin --> [flying]>) ==> <robin --> bird>>. %1.00;0.90%', 
            'robin.', index_task=(0,0), index_belief=(0,0,0))
        tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 
        self.assertTrue(
            output_contains(tasks_derived, '<(&&,<robin --> [chirping]>,<robin --> [with_beak]>) ==> <robin --> bird>>. %1.00;0.42%')
        )
        pass

    def test_question_0(self):
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '(&&, A, B)?', 
            'A.', 
            'A.', is_belief_term=True)
        tasks_derived = [rule(task, belief.term, task_link, term_link) for rule in rules] 
        self.assertTrue(
            output_contains(tasks_derived, 'A?')
        )

    def test_question_1(self):
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            'C?', 
            '<(&&, A, B)==>C>.', 
            'C.')
        tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 
        self.assertTrue(
            output_contains(tasks_derived, '(&&, A, B)?')
        )

    def test_0(self):
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            'A.', 
            '<(&&, A, B)==>C>.', 
            'A.')
        tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 
        self.assertTrue(
            output_contains(tasks_derived, '<B==>C>. %1.00;0.81%')
        )


if __name__ == '__main__':

    test_classes_to_run = [
        TEST_NAL5
    ]

    loader = unittest.TestLoader()

    suites = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites.append(suite)
        
    suites = unittest.TestSuite(suites)

    runner = unittest.TextTestRunner()
    results = runner.run(suites)
