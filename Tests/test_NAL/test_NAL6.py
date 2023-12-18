import unittest

from pynars.NARS.DataStructures import Task
from pynars.NAL.MetaLevelInference.VariableSubstitution import *
# from pynars.NARS.RuleMap import RuleMap

# import Tests.utils_for_test as utils_for_test
from Tests.utils_for_test import *
from pynars.utils.Print import PrintType, print_out
from pynars.NARS.InferenceEngine.VariableEngine.VariableEngine import VariableEngine

class TEST_NAL6(unittest.TestCase):
    def setUp(self):
        nars.reset()

    ''''''

    def test_unification_0(self):
        '''
        'Variable unification

        'If something is a bird, then it is a flyer.
        <<$x --> bird> ==> <$x --> flyer>>. %1.00;0.90% 
        <bird-->filyer>
        'If something is a bird, then it is not a flyer. 
        <<$y --> bird> ==> <$y --> flyer>>. %0.00;0.70% 

        1

        'If something is a bird, then usually, it is a flyer. 
        ''outputMustContain('<<$1 --> bird> ==> <$1 --> flyer>>. %0.79;0.92%')
        '''
        tasks_derived = process_two_premises(
            '<<$x --> bird> ==> <$x --> flyer>>. %1.00;0.90%',
            '<<$y --> bird> ==> <$y --> flyer>>. %0.00;0.70%',
            20
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<$1 --> bird> ==> <$1 --> flyer>>. %0.79;0.92%')
        )
        pass


    def test_unification_1(self):
        '''
        'Variable unification

        'If something is a bird, then it is a animal. 
        <<$x --> bird> ==> <$x --> animal>>. %1.00;0.90% 

        'If something is a robin, then it is a bird. 
        <<$y --> robin> ==> <$y --> bird>>. %1.00;0.90% 

        3

        'If something is a robin, then it is a animal. 
        ''outputMustContain('<<$1 --> robin> ==> <$1 --> animal>>. %1.00;0.81%')

        'I guess that if something is a animal, then it is a robin. 
        ''outputMustContain('<<$1 --> animal> ==> <$1 --> robin>>. %1.00;0.45%')
        '''
        tasks_derived = process_two_premises(
            '<<$x --> bird> ==> <$x --> animal>>. %1.00;0.90%',
            '<<$y --> robin> ==> <$y --> bird>>. %1.00;0.90%',
            20
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<$0 --> robin> ==> <$0 --> animal>>. %1.00;0.81%')
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<$0 --> animal> ==> <$0 --> robin>>. %1.00;0.45%')
        )

        self.assertTrue(
            not output_contains(tasks_derived, '<<$0 --> animal> ==> <$1 --> robin>>. %1.00;0.45%')
        )
        pass


    def test_unification_2(self):
        '''
        'Variable unification

        'If something is a swan, then it is a bird.
        <<$x --> swan> ==> <$x --> bird>>. %1.00;0.80%  

        'If something is a swan, then it is a swimmer.
        <<$y --> swan> ==> <$y --> swimmer>>. %0.80;0.90% 

        3

        'I believe that if something is a swan, then it is a bird or a swimmer.
        ''outputMustContain('<<$1 --> swan> ==> (||,<$1 --> bird>,<$1 --> swimmer>)>. %1.00;0.72%')

        'I believe that if something is a swan, then usually, it is both a bird and a swimmer.
        ''outputMustContain('<<$1 --> swan> ==> (&&,<$1 --> bird>,<$1 --> swimmer>)>. %0.80;0.72%')

        'I guess if something is a swimmer, then it is a bird. 
        ''outputMustContain('<<$1 --> swimmer> ==> <$1 --> bird>>. %1.00;0.37%')

        'I guess if something is a bird, then it is a swimmer. 
        ''outputMustContain('<<$1 --> bird> ==> <$1 --> swimmer>>. %0.80;0.42%')

        'I guess something is a bird, if and only if it is a swimmer. 
        ''outputMustContain('<<$1 --> bird> <=> <$1 --> swimmer>>. %0.80;0.42%')
        '''

        tasks_derived = process_two_premises(
            '<<$x --> swan> ==> <$x --> bird>>. %1.00;0.80% ',
            '<<$y --> swan> ==> <$y --> swimmer>>. %0.80;0.90%',
            20
        )

        self.assertTrue(
            output_contains(tasks_derived, '<<$0 --> swan> ==> (||,<$0 --> bird>,<$0 --> swimmer>)>. %1.00;0.72%')
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<$0 --> swan> ==> (&&,<$0 --> bird>,<$0 --> swimmer>)>. %0.80;0.72%')
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<$0 --> swimmer> ==> <$0 --> bird>>. %1.00;0.37%')
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<$0 --> bird> ==> <$0 --> swimmer>>. %0.80;0.42%')
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<$0 --> bird> <=> <$0 --> swimmer>>. %0.80;0.42%')
        )
        pass


    def test_unification_3(self):
        '''
        'Variable unification

        'What can be said about bird can also be said about robin.
        <<bird --> $x> ==> <robin --> $x>>. %1.00;0.90%

        'What can be said about swimmer usually can also be said about robin.
        <<swimmer --> $y> ==> <robin --> $y>>. %0.70;0.90%  

        3

        'What can be said about bird and swimmer can also be said about robin.
        ''outputMustContain('<(&&,<bird --> $1>,<swimmer --> $1>) ==> <robin --> $1>>. %1.00;0.81%')

        'What can be said about bird or swimmer can also be said about robin.
        ''outputMustContain('<(||,<bird --> $1>,<swimmer --> $1>) ==> <robin --> $1>>. %0.70;0.81%')

        'I guess what can be said about bird can also be said about swimmer.
        ''outputMustContain('<<bird --> $1> ==> <swimmer --> $1>>. %1.00;0.36%')

        'I guess what can be said about swimmer can also be said about bird.
        ''outputMustContain('<<swimmer --> $1> ==> <bird --> $1>>. %0.70;0.45%')

        'I guess bird and swimmer share most properties.
        ''outputMustContain('<<bird --> $1> <=> <swimmer --> $1>>. %0.70;0.45%')
        '''
        tasks_derived = process_two_premises(
            '<<bird --> $x> ==> <robin --> $x>>. %1.00;0.90%',
            '<<swimmer --> $y> ==> <robin --> $y>>. %0.70;0.90%',
            20
        )
        
        self.assertTrue(
            output_contains(tasks_derived, '<(&&,<bird --> $0>,<swimmer --> $0>) ==> <robin --> $0>>. %1.00;0.81%')
        )
        self.assertTrue(
            output_contains(tasks_derived, '<(||,<bird --> $0>,<swimmer --> $0>) ==> <robin --> $0>>. %0.70;0.81%')
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<bird --> $0> ==> <swimmer --> $0>>. %1.00;0.36%')
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<swimmer --> $0> ==> <bird --> $0>>. %0.70;0.45%')
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<bird --> $0> <=> <swimmer --> $0>>. %0.70;0.45%')
        )


    def test_unification_4(self):
        '''
        'Variable unification

        'If something can fly and chirp, then it is a bird.
        <(&&,<$x --> flyer>,<$x --> [chirping]>) ==> <$x --> bird>>. %1.00;0.90%

        'If something has wings, then it can fly.
        <<$y --> [with_wings]> ==> <$y --> flyer>>. %1.00;0.90%

        8

        'If something can chirp and has wings, then it is a bird.
        ''outputMustContain('<(&&,<$1 --> [chirping]>,<$1 --> [with_wings]>) ==> <$1 --> bird>>. %1.00;0.81%')
        '''
        tasks_derived = process_two_premises(
            '<(&&,<$x --> flyer>,<$x --> [chirping]>) ==> <$x --> bird>>. %1.00;0.90%',
            '<<$y --> [with_wings]> ==> <$y --> flyer>>. %1.00;0.90%',
            20
        )
        
        self.assertTrue(
            output_contains(tasks_derived, '<(&&,<$0 --> [chirping]>,<$0 --> [with_wings]>) ==> <$0 --> bird>>. %1.00;0.81%')
        )
        pass


    def test_unification_5(self):
        '''
        'Variable unification

        'If something can fly, chirp, and eats worms, then it is a bird.
        <(&&,<$x --> flyer>,<$x --> [chirping]>, <(*, $x, worms) --> food>) ==> <$x --> bird>>. 

        'If something can chirp and has wings, then it is a bird.
        <(&&,<$x --> [chirping]>,<$x --> [with_wings]>) ==> <$x --> bird>>.

        ''//6
        12

        'If something can fly and eats worms, then I guess it has wings.
        ''outputMustContain('<(&&,<$1 --> flyer>,<(*,$1,worms) --> food>) ==> <$1 --> [with_wings]>>. %1.00;0.45%')

        'I guess if something has wings, then it can fly and eats worms.
        ''outputMustContain('<<$1 --> [with_wings]> ==> (&&,<$1 --> flyer>,<(*,$1,worms) --> food>)>. %1.00;0.45%')
        '''
        tasks_derived = process_two_premises(
            '<(&&,<$x --> flyer>,<$x --> [chirping]>, <(*, $x, worms) --> food>) ==> <$x --> bird>>.  %1.00;0.90%',
            '<(&&,<$x --> [chirping]>,<$x --> [with_wings]>) ==> <$x --> bird>>. %1.00;0.90%',
            20
        )
        
        self.assertTrue(
            output_contains(tasks_derived, '<(&&,<$0 --> flyer>,<(*,$0,worms) --> food>) ==> <$0 --> [with_wings]>>. %1.00;0.45%')
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<$0 --> [with_wings]> ==> (&&,<$0 --> flyer>,<(*,$0,worms) --> food>)>. %1.00;0.45%')
        )
        pass

    def test_unification_5_1(self):
        '''
        'Variable unification 
        <(&&,<$x --> A>,<$x --> B>, <$y --> C>) ==> <$y --> D>>. 
        <(&&,<$x --> C>, <$x --> E>) ==> <$x --> D>>.

        ''outputMustContain('<(&&,<$x --> A>,<$x --> B>) ==> <$y --> D>>.  %1.00;0.45%')
        '''
        pass



    def test_unification_6(self):
        '''
        'Variable unification

        'If something can fly and eats worms, then it is a bird.
        <(&&,<$x --> flyer>,<(*,$x,worms) --> food>) ==> <$x --> bird>>. %1.00;0.90%

        'If something can fly, then it has wings.
        <<$y --> flyer> ==> <$y --> [with_wings]>>. %1.00;0.90%

        // 4 originally
        13 

        'If something has wings and eats worms, then I guess it is a bird.
        ''outputMustContain('<(&&,<$1 --> [with_wings]>,<(*,$1,worms) --> food>) ==> <$1 --> bird>>. %1.00;0.45%')
        '''
        tasks_derived = process_two_premises(
            '<(&&,<$x --> flyer>,<(*,$x,worms) --> food>) ==> <$x --> bird>>. %1.00;0.90%',
            '<<$y --> flyer> ==> <$y --> [with_wings]>>. %1.00;0.90%',
            20
        )
       
        self.assertTrue(
            output_contains(tasks_derived, '<(&&,<$0 --> [with_wings]>,<(*,$0,worms) --> food>) ==> <$0 --> bird>>. %1.00;0.45%')
        )
        pass


    def test_elimination_0(self):
        '''
        'Variable elimination

        'If something is a bird, then it is an animal.
        <<$x --> bird> ==> <$x --> animal>>. %1.00;0.90%

        'A robin is a bird.
        <robin --> bird>. %1.00;0.90%

        3

        'A robin is an animal.
        ''outputMustContain('<robin --> animal>. %1.00;0.81%')
        '''
        tasks_derived = process_two_premises(
            '<<$x --> bird> ==> <$x --> animal>>. %1.00;0.90%',
            '<robin --> bird>. %1.00;0.90%',
            3
        )
        
        self.assertTrue(
            output_contains(tasks_derived, '<robin --> animal>. %1.00;0.81%')
        )
        pass


    def test_elimination_1(self):
        '''
        'Variable elimination

        'If something is a bird, then it is an animal.
        <<$x --> bird> ==> <$x --> animal>>. 

        'A tiger is an animal.
        <tiger --> animal>. 

        10

        'I guess that a tiger is a bird.
        ''outputMustContain('<tiger --> bird>. %1.00;0.45%')
        '''
        tasks_derived = process_two_premises(
            '<<$x --> bird> ==> <$x --> animal>>. %1.00;0.90%',
            '<tiger --> animal>. %1.00;0.90%',
            10
        )

        self.assertTrue(
            output_contains(tasks_derived, '<tiger --> bird>. %1.00;0.45%')
        )
        pass


    def test_elimination_2(self):
        '''
        'Variable elimination

        'Something is a animal if and only if it is a bird.
        <<$x --> animal> <=> <$x --> bird>>. 

        'A robin is a bird.
        <robin --> bird>.

        3

        'A robin is a animal.
        ''outputMustContain('<robin --> animal>. %1.00;0.81%')
        '''
        tasks_derived = process_two_premises(
            '<<$x --> animal> <=> <$x --> bird>>. %1.00;0.90%',
            '<robin --> bird>. %1.00;0.90%',
            3
        )

        self.assertTrue(
            output_contains(tasks_derived, '<robin --> animal>. %1.00;0.81%')
        )
        pass


    def test_elimination_3(self):
        '''
        'Variable elimination

        'Some bird can swim.
        (&&,<#x --> bird>,<#x --> swimmer>). 

        'Swan is a type of bird.
        <swan --> bird>. %0.90%

        3

        'I guess swan can swim.
        ''outputMustContain('<swan --> swimmer>. %0.90;0.43%')
        '''
        tasks_derived = process_two_premises(
            '(&&,<#x --> bird>,<#x --> swimmer>).  %1.00;0.90%',
            '<swan --> bird>. %0.90;0.90%',
            10
        )

        self.assertTrue(
            output_contains(tasks_derived, '<swan --> swimmer>. %0.90;0.43%')
        )
        pass


    def test_elimination_3_1(self):
        '''
        (&&,<C --> A>,<D --> B>). %1.00;0.90%
        <M --> A>. %0.90;0.90%

        '''
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '(&&,<C --> A>,<D --> B>). %1.00;0.90%',
            '<M --> A>. %0.90;0.90%',
            'A.'
        )
        rules = [] if rules is None else rules
        rules_var = {rule for _, rule in VariableEngine.rule_map.map.data}
        self.assertTrue(len(set(rules) & rules_var) == 0)

        pass

    def test_elimination_4(self):
        '''
        'Variable elimination

        'Tweety has wings.
        <{Tweety} --> [with_wings]>.

        'If something can chirp and has wings, then it is a bird.
        <(&&,<$x --> [chirping]>,<$x --> [with_wings]>) ==> <$x --> bird>>.

        23

        'If Tweety can chirp, then it is a bird.
        ''outputMustContain('<<{Tweety} --> [chirping]> ==> <{Tweety} --> bird>>. %1.00;0.81%')
        '''
        tasks_derived = process_two_premises(
            '<(&&,<$x --> [chirping]>,<$x --> [with_wings]>) ==> <$x --> bird>>. %1.00;0.90%',
            '<{Tweety} --> [with_wings]>.  %1.00;0.90%',
            30
        )

        self.assertTrue(
            output_contains(tasks_derived, '<<{Tweety} --> [chirping]> ==> <{Tweety} --> bird>>. %1.00;0.81%')
        )
        pass


    def test_elimination_5(self):
        '''
        'Variable elimination

        'If something can fly, chirp, and eats worms, then it is a bird.
        <(&&,<$x --> flyer>,<$x --> [chirping]>, <(*, $x, worms) --> food>) ==> <$x --> bird>>. 

        'Tweety can fly.
        <{Tweety} --> flyer>.

        7

        'If Tweety can chirp and eats worms, then it is a bird.
        ''outputMustContain('<(&&,<(*,{Tweety},worms) --> food>,<{Tweety} --> [chirping]>) ==> <{Tweety} --> bird>>. %1.00;0.81%')
        '''
        tasks_derived = process_two_premises(
            '<(&&,<$x --> flyer>,<$x --> [chirping]>, <(*, $x, worms) --> food>) ==> <$x --> bird>>.%1.00;0.90%',
            '<{Tweety} --> flyer>.  %1.00;0.90%',
            10
        )

        self.assertTrue(
            output_contains(tasks_derived, '<(&&,<(*,{Tweety},worms) --> food>,<{Tweety} --> [chirping]>) ==> <{Tweety} --> bird>>. %1.00;0.81%')
        )
        pass


    def test_elimination_6(self):
        '''
        'Variable elimination

        'Every lock can be opened by every key.
        <(&&,<$x --> key>,<$y --> lock>) ==> <$y --> (/,open,$x,_)>>.  

        'Lock-1 is a lock.
        <{lock1} --> lock>. 

        20

        'Lock-1 can be opened by every key.
        ''outputMustContain('<<$1 --> key> ==> <{lock1} --> (/,open,$1,_)>>. %1.00;0.81%')
        '''
        tasks_derived = process_two_premises(
            '<(&&,<$x --> key>,<$y --> lock>) ==> <$y --> (/,open,$x,_)>>. %1.00;0.90%',
            '<{lock1} --> lock>. %1.00;0.90%',
            20
        )

        self.assertTrue(
            output_contains(tasks_derived, '<<$0 --> key> ==> <{lock1} --> (/,open,$0,_)>>. %1.00;0.81%')
        )
        pass


    def test_multiple_variable_elimination_0(self):
        '''
        'Multiple variable elimination

        'Every lock can be opened by some key.
        <<$x --> lock> ==> (&&,<#y --> key>,<$x --> (/,open,#y,_)>)>. %1.00;0.90%

        'Lock-1 is a lock.
        <{lock1} --> lock>. %1.00;0.90%

        9

        'Some key can open Lock-1.
        ''outputMustContain('(&&,<#1 --> key>,<{lock1} --> (/,open,#1,_)>). %1.00;0.81%')
        '''
        tasks_derived = process_two_premises(
            '<<$x --> lock> ==> (&&,<#y --> key>,<$x --> (/,open,#y,_)>)>. %1.00;0.90%',
            '<{lock1} --> lock>. %1.00;0.90%',
            100
        )

        self.assertTrue(
            output_contains(tasks_derived, '(&&,<#0 --> key>,<{lock1} --> (/,open,#0,_)>). %1.00;0.81%')
        )

        pass


    def test_multiple_variable_elimination_1(self):
        '''
        'Multiple variable elimination

        'There is a lock that can be opened by every key.
        (&&,<#x --> lock>,<<$y --> key> ==> <#x --> (/,open,$y,_)>>).  

        'Lock-1 is a lock.
        <{lock1} --> lock>.

        9

        'I guess Lock-1 can be opened by every key.
        ''outputMustContain('<<$1 --> key> ==> <{lock1} --> (/,open,$1,_)>>. %1.00;0.43%')
        '''
        tasks_derived = process_two_premises(
            '(&&,<#x --> lock>,<<$y --> key> ==> <#x --> (/,open,$y,_)>>). %1.00;0.90%',
            '<{lock1} --> lock>. %1.00;0.90%',
            100
        )

        self.assertTrue(
            output_contains(tasks_derived, '<<$0 --> key> ==> <{lock1} --> (/,open,$0,_)>>. %1.00;0.43%')
        )

        pass


    def test_multiple_variable_elimination_2(self):
        '''
        'Multiple variable elimination

        'There is a key that can open some lock.
        (&&,<#x --> (/,open,#y,_)>,<#x --> lock>,<#y --> key>).  

        'Lock-1 is a lock.
        <{lock1} --> lock>.

        18

        'I guess there is a key that can open Lock-1.
        ''outputMustContain('(&&,<#1 --> key>,<{lock1} --> (/,open,#1,_)>). %1.00;0.43%')
        '''
        tasks_derived = process_two_premises(
            '(&&,<#x --> (/,open,#y,_)>,<#x --> lock>,<#y --> key>).',
            '<{lock1} --> lock>.',
            100
        )

        self.assertTrue(
            output_contains(tasks_derived, '(&&,<#0 --> key>,<{lock1} --> (/,open,#0,_)>). %1.00;0.43%')
        )
        pass


    def test_introduction_0(self):
        '''
        'Introduction

        'A swan is a bird.
        <swan --> bird>. %1.00;0.90%

        'A swan is usually a swimmer.
        <swan --> swimmer>. %0.80;0.90%

        3

        'I guess a bird is usually a swimmer.
        ''outputMustContain('<<$1 --> bird> ==> <$1 --> swimmer>>. %0.80;0.45%')

        'I guess a swimmer is a bird.
        ''outputMustContain('<<$1 --> swimmer> ==> <$1 --> bird>>. %1.00;0.39%')

        'I guess a bird is usually a swimmer, and the other way around.
        ''outputMustContain('<<$1 --> bird> <=> <$1 --> swimmer>>. %0.80;0.45%')

        'Some bird can swim.
        ''outputMustContain('(&&,<#1 --> bird>,<#1 --> swimmer>). %0.80;0.81%')
        '''

        tasks_derived = process_two_premises(
            '<swan --> bird>. %1.00;0.90%',
            '<swan --> swimmer>. %0.80;0.90%',
            100
        )

        self.assertTrue(
            output_contains(tasks_derived, '<<$0 --> bird> ==> <$0 --> swimmer>>. %0.80;0.45%')
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<$0 --> swimmer> ==> <$0 --> bird>>. %1.00;0.39%')
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<$0 --> bird> <=> <$0 --> swimmer>>. %0.80;0.45%')
        )
        self.assertTrue(
            output_contains(tasks_derived, '(&&,<#0 --> bird>,<#0 --> swimmer>). %0.80;0.81%')
        )
        pass


    def test_introduction_1(self):
        '''
        'Introduction

        'A gull is a swimmer.
        <gull --> swimmer>. %1.00;0.90%

        'Usually, a swan is a swimmer.
        <swan --> swimmer>. %0.80;0.90%

        3

        'I guess what can be said about gull usually can also be said about swan.
        ''outputMustContain('<<gull --> $1> ==> <swan --> $1>>. %0.80;0.45%')

        'I guess what can be said about swan can also be said about gull.
        ''outputMustContain('<<swan --> $1> ==> <gull --> $1>>. %1.00;0.39%')

        'I guess gull and swan share most properties.
        ''outputMustContain('<<gull --> $1> <=> <swan --> $1>>. %0.80;0.45%')

        'Gull and swan have some common property.
        ''outputMustContain('(&&,<gull --> #1>,<swan --> #1>). %0.80;0.81%')
        '''
        tasks_derived = process_two_premises(
            '<gull --> swimmer>. %1.00;0.90%',
            '<swan --> swimmer>. %0.80;0.90%',
            100
        )

        self.assertTrue(
            output_contains(tasks_derived, '<<gull --> $0> ==> <swan --> $0>>. %0.80;0.45%')
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<swan --> $0> ==> <gull --> $0>>. %1.00;0.39%')
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<gull --> $0> <=> <swan --> $0>>. %0.80;0.45%')
        )
        self.assertTrue(
            output_contains(tasks_derived, '(&&,<gull --> #0>,<swan --> #0>). %0.80;0.81%')
        )
        pass


    def test_introduction_2(self):
        '''
        'Introduction

        'Key-1 opens Lock-1.
        <{key1} --> (/,open,_,{lock1})>. %1.00;0.90%

        'Key-1 is a key.
        <{key1} --> key>. %1.00;0.90%

        45

        'I guess every key can open Lock-1.
        ''outputMustContain('<<$1 --> key> ==> <$1 --> (/,open,_,{lock1})>>. %1.00;0.45%')

        'Some key can open Lock-1.
        ''//outputMustContain('(&&,<#1 --> (/,open,_,{lock1})>,<#1 --> key>). %1.00;0.81%') //reversed
        ''  outputMustContain('(&&,<#1 --> (/,open,_,{lock1})>,<#1 --> key>). %1.00;0.25%')
        '''

        tasks_derived = process_two_premises(
            '<{key1} --> (/,open,_,{lock1})>. %1.00;0.90%',
            '<{key1} --> key>. %1.00;0.90%',
            100
        )

        self.assertTrue(
            output_contains(tasks_derived, '<<$0 --> key> ==> <$0 --> (/,open,_,{lock1})>>. %1.00;0.45%')
        )
        self.assertTrue(
            output_contains(tasks_derived, '(&&,<#0 --> (/,open,_,{lock1})>,<#0 --> key>). %1.00;0.81%')
        )

        pass


    def test_multiple_variables_introduction_0(self):
        '''
        'Multiple variables introduction

        'Lock-1 can be opened by every key.
        <<$x --> key> ==> <{lock1} --> (/,open,$x,_)>>. %1.00;0.90%

        'Lock-1 is a lock.
        <{lock1} --> lock>. %1.00;0.90%

        166

        'There is a lock that can be opened by every key.
        ''outputMustContain('(&&,<#1 --> lock>,<<$2 --> key> ==> <#1 --> (/,open,$2,_)>>). %1.00;0.81%')

        'I guess every lock can be opened by every key.
        ''outputMustContain('<(&&,<$1 --> key>,<$2 --> lock>) ==> <$2 --> (/,open,$1,_)>>. %1.00;0.45%')
        '''
        tasks_derived = process_two_premises(
            '<<$x --> key> ==> <{lock1} --> (/,open,$x,_)>>. %1.00;0.90%',
            '<{lock1} --> lock>. %1.00;0.90%',
            10
        )

        self.assertTrue(
            output_contains(tasks_derived, '(&&,<#0 --> lock>,<<$1 --> key> ==> <#0 --> (/,open,$1,_)>>). %1.00;0.81%')
        )
        self.assertTrue(
            output_contains(tasks_derived, '<(&&,<$0 --> key>,<$1 --> lock>) ==> <$1 --> (/,open,$0,_)>>. %1.00;0.45%')
        )

        pass


    def test_multiple_variables_introduction_1(self):
        '''
        'Multiple variables introduction

        'Lock-1 can be opened by some key.
        (&&,<#x --> key>,<{lock1} --> (/,open,#x,_)>). %1.00;0.90%

        'Lock-1 is a lock.
        <{lock1} --> lock>. %1.00;0.90%

        17

        'There is a key that can open some lock.
        ''outputMustContain('(&&,<#1 --> key>,<#2 --> (/,open,#1,_)>,<#2 --> lock>). %1.00;0.81%')

        'I guess every lock can be opened by some key.
        ''outputMustContain('<<$1 --> lock> ==> (&&,<#2 --> key>,<$1 --> (/,open,#2,_)>)>. %1.00;0.45%')
        '''
        tasks_derived = process_two_premises(
            '(&&,<#x --> key>,<{lock1} --> (/,open,#x,_)>). %1.00;0.90%',
            '<{lock1} --> lock>. %1.00;0.90%',
            20
        )

        self.assertTrue(
            output_contains(tasks_derived, '(&&,<#0 --> key>,<#1 --> (/,open,#0,_)>,<#1 --> lock>). %1.00;0.81%')
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<$0 --> lock> ==> (&&,<#1 --> key>,<$0 --> (/,open,#1,_)>)>. %1.00;0.45%')
        )

        pass


    def test_second_variable_introduction_induction(self):
        '''
        'Second variable introduction (induction)

        'if something opens lock1, it is a key
        <<lock1 --> (/,open,$1,_)> ==> <$1 --> key>>. %1.00;0.90%

        'lock1 is a key
        <lock1 --> lock>. %1.00;0.90%

        7

        'there is a lock with the property that when opened by something, this something is a key (induction)
        ''outputMustContain('<(&&,<#1 --> (/,open,$2,_)>,<#1 --> lock>) ==> <$2 --> key>>. %1.00;0.45%')    
        '''
        tasks_derived = process_two_premises(
            '<<lock1 --> (/,open,$1,_)> ==> <$1 --> key>>. %1.00;0.90%',
            '<lock1 --> lock>. %1.00;0.90%',
            20
        )

        self.assertTrue(
            output_contains(tasks_derived, '<(&&,<#0 --> (/,open,$1,_)>,<#0 --> lock>) ==> <$1 --> key>>. %1.00;0.81%')
        )

        pass


    def test_recursion(self):
        '''
        'Recursion

        '0 is a number
        <0 --> num>. %1.00;0.90%
        'If n is a number, n+1 is also a number
        <<$1 --> num> ==> <(*,$1) --> num>>. %1.00;0.90%
        '3 is a number?
        <(*,(*,(*,0))) --> num>?
        70000
        'I guess 3 is a number
        ''outputMustContain('<(*,(*,(*,0))) --> num>. %1.00;0.66%')            
        '''
        pass


    def test_second_level_variable_unification_0(self):
        '''
        'Second level variable unification

        'there is a lock which is opened by all keys
        (&&,<#1 --> lock>,<<$2 --> key> ==> <#1 --> (/,open,$2,_)>>). %1.00;0.90% 

        'key1 is a key
        <{key1} --> key>. %1.00;0.90%

        5

        'there is a lock which is opened by key1
        ''outputMustContain('(&&,<#1 --> (/,open,{key1},_)>,<#1 --> lock>). %1.00;0.81%')          
        '''
        pass


    def test_second_level_variable_unification_1(self):
        '''
        'Second level variable unification

        'all locks are opened by some key
        <<$1 --> lock> ==> (&&,<#2 --> key>,<$1 --> (/,open,#2,_)>)>. %1.00;0.90% 

        'key1 is a key
        <{key1} --> key>. %1.00;0.90% 

        5

        'maybe all locks are opened by key1
        ''outputMustContain('')
        //''outputMustContain('<<$1 --> lock> ==> <$1 --> (/,open,{key1},_)>>. %1.00;0.43%')       
        '''
        tasks_derived = process_two_premises(
            '<<$1 --> lock> ==> (&&,<#2 --> key>,<$1 --> (/,open,#2,_)>)>. %1.00;0.90%',
            '<{key1} --> key>. %1.00;0.90% ',
            100
        )

        self.assertTrue(
            output_contains(tasks_derived, '<<$0 --> lock> ==> <$0 --> (/,open,{key1},_)>>. %1.00;0.43%')
        )
        pass

    def test_second_level_variable_unification_1_0(self):
        '''
        <A ==> (&&,<#2 --> B>,C)>. %1.00;0.90% 

        <M --> B>. %1.00;0.90% 

        ''outputMustContain('<A ==> C>. %1.00;0.43%')       
        '''
        tasks_derived = process_two_premises(
            '<A ==> (&&,<#2 --> B>,C)>. %1.00;0.90%',
            '<M --> B>. %1.00;0.90%',
            20
        )

        self.assertTrue(
            output_contains(tasks_derived, '<A ==> C>. %1.00;0.43%')
        )
        pass
    
    def test_second_level_variable_unification_1_1(self):
        '''
        <A ==> (&&,<D --> B>,C)>. %1.00;0.90% 

        <M --> B>. %1.00;0.90% 

        '''
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '<A ==> (&&,<D --> B>,C)>. %1.00;0.90%',
            '<M --> B>. %1.00;0.90%',
            'B.'
        )
        rules = [] if rules is None else rules
        rules_var = {rule for _, rule in VariableEngine.rule_map.map.data}
        self.assertTrue(len(set(rules) & rules_var) == 0)



    def test_variable_elimination_deduction(self):
        '''
        'Second variable introduction (induction)

        'lock1 is a lock
        <lock1 --> lock>. %1.00;0.90%

        'there is a lock with the property that when opened by something, this something is a key
        <(&&,<#1 --> lock>,<#1 --> (/,open,$2,_)>) ==> <$2 --> key>>. %1.00;0.90% 

        4

        'whatever opens lock1 is a key
        ''outputMustContain('<<lock1 --> (/,open,$1,_)> ==> <$1 --> key>>. %1.00;0.81%')
        '''
        tasks_derived = process_two_premises(
            '<(&&,<#1 --> lock>,<#1 --> (/,open,$2,_)>) ==> <$2 --> key>>. %1.00;0.90%',
            '<lock1 --> lock>. %1.00;0.90%',
            100
        )

        self.assertTrue(
            output_contains(tasks_derived, '<<lock1 --> (/,open,$0,_)> ==> <$0 --> key>>. %1.00;0.81%')
        )
        pass


    def test_variable_elimination_deduction_0(self):
        '''
        <M --> A>. %1.00;0.90%
        <(&&,<#1 --> A>,<#1 --> B) ==> C>. %1.00;0.90% 

        ''outputMustContain('<<M --> B> ==> C>. %1.00;0.81%')
        '''
        tasks_derived = process_two_premises(
            '<(&&,<#1 --> A>, <#1 --> B>) ==> C>. %1.00;0.90%',
            '<M --> A>. %1.00;0.90%',
            100
        )

        self.assertTrue(
            output_contains(tasks_derived, '<<M --> B> ==> C>. %1.00;0.81%')
        )
        pass

    def test_variable_elimination_deduction_1(self):
        '''
        <M --> A>. %1.00;0.90%
        <(&&,<C --> A>,<D --> B>) ==> C>. %1.00;0.90% 
        '''
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '<(&&,<C --> A>,<D --> B>) ==> C>. %1.00;0.90%',
            '<M --> A>. %1.00;0.90%',
            'A.'
        )
        rules = [] if rules is None else rules
        rules_var = {rule for _, rule in VariableEngine.rule_map.map.data}
        self.assertTrue(len(set(rules) & rules_var) == 0)

        pass


    def test_abduction_with_variable_elimination_abduction(self):
        '''
        'Abduction with variable elimination (abduction)

        'whatever opens lock1 is a key
        <<lock1 --> (/,open,$1,_)> ==> <$1 --> key>>. %1.00;0.90%

        'there is a lock with the property that when opened by something, this something is a key
        <(&&,<#1 --> lock>,<#1 --> (/,open,$2,_)>) ==> <$2 --> key>>. %1.00;0.90%

        10

        'lock1 is a lock
        ''outputMustContain('<lock1 --> lock>. %1.00;0.45%')
        '''
        tasks_derived = process_two_premises(
            '<(&&,<#1 --> lock>,<#1 --> (/,open,$2,_)>) ==> <$2 --> key>>. %1.00;0.90%',
            '<<lock1 --> (/,open,$1,_)> ==> <$1 --> key>>. %1.00;0.90%',
            200
        )

        self.assertTrue(
            output_contains(tasks_derived, '<lock1 --> lock>. %1.00;0.45%')
        )

    def test_abduction_with_variable_elimination_abduction_0(self):
        '''
        <<M --> A> ==> C>. %1.00;0.90%
        <(&&,<#1 --> A>,<#1 --> B>) ==> C>. %1.00;0.90%

        ''outputMustContain('<M --> B>. %1.00;0.45%')
        '''
        tasks_derived = process_two_premises(
            '<(&&,<#1 --> A>,<#1 --> B>) ==> C>. %1.00;0.90%',
            '<<M --> A> ==> C>. %1.00;0.90%',
            200
        )

        self.assertTrue(
            output_contains(tasks_derived, '<M --> B>. %1.00;0.45%')
        )

    def test_abduction_with_variable_elimination_abduction_1(self):
        '''
        <<M --> A> ==> C>. %1.00;0.90%
        <(&&,<D --> A>,<E --> B>) ==> C>. %1.00;0.90%

        ''outputMustContain('<M --> B>. %1.00;0.45%')
        '''
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '<(&&,<D --> A>,<E --> B>) ==> C>. %1.00;0.90%',
            '<<M --> A> ==> C>. %1.00;0.90%',
            'A.'
        )
        rules = [] if rules is None else rules
        rules_var = {rule for _, rule in VariableEngine.rule_map.map.data}
        self.assertTrue(len(set(rules) & rules_var) == 0)


    def test_birdClaimedByBob(self):
        '''
        'from https://code.google.com/archive/p/open-nars/issues/7

        <(&,<{Tweety} --> bird>,<bird --> fly>) --> claimedByBob>.
        <<(&,<#1 --> $2>,<$3 --> #1>) --> claimedByBob> ==> <<$3 --> $2> --> claimedByBob>>.

        <?x --> claimedByBob>?
        100
        ''outputMustContain('<<{Tweety} --> fly> --> claimedByBob>. %1.00;0.81%')
        '''
        pass


    def test_can_of_worms(self):
        '''
        <0 --> num>. %1.00;0.90%
        <0 --> (/,num,_)>. %1.00;0.90%

        20

        ''outputMustContain('<<$1 --> num> ==> <$1 --> (/,num,_)>>. %1.00;0.45%')
        '''
        pass


    def test_nlp1(self):
        '''
        <(\,REPRESENT,_,CAT) --> cat>. %1.00;0.90%
        <(\,(\,REPRESENT,_,<(*,CAT,FISH) --> FOOD>),_,eat,fish) --> cat>.
        5
        ''outputMustContain('<<(\,REPRESENT,_,$1) --> $2> ==> <(\,(\,REPRESENT,_,<(*,$1,FISH) --> FOOD>),_,eat,fish) --> $2>>. %1.00;0.40%')
        '''
        pass


    def test_nlp2(self):
        '''
        <cat --> (/,(/,REPRESENT,_,<(*,CAT,FISH) --> FOOD>),_,eat,fish)>.
        <cat --> CAT>. %1.00;0.90%
        300
        ''outputMustContain('<<$1 --> $2> ==> <$1 --> (/,(/,REPRESENT,_,<(*,$2,FISH) --> FOOD>),_,eat,fish)>>. %1.00;0.40%')
        '''
        pass


    def test_redundant(self):
        '''
        <<lock1 --> (/,open,$1,_)> ==> <$1 --> key>>. 
        100
        ''outputMustNotContain('<(&&,<lock1 --> (/,open,$1,_)>,<(*,$1,lock1) --> open>) ==> <$1 --> key>>. %1.00;0.81%')
        ''outputMustNotContain('<<(*,$1,lock1) --> open> ==> <lock1 --> (/,open,$1,_)>>. %1.00;0.45%')
        '''
        pass


    def test_symmetry(self):
        '''
        <(*,a,b) --> like>. %1.00;0.90%
        <(*,b,a) --> like>. %1.00;0.90%
        <<(*,$1,$2) --> like> <=> <(*,$2,$1) --> like>>?
        20
        ''outputMustContain('<<(*,$1,$2) --> like> <=> <(*,$2,$1) --> like>>. %1.00;0.40%')
        '''
        pass


    def test_uncle(self):
        '''
        <tim --> (/,uncle,_,tom)>. %1.00;0.90%
        <tim --> (/,uncle,tom,_)>. %0.00;0.90%
        10
        ''outputMustContain('<<$1 --> (/,uncle,_,$2)> ==> <$1 --> (/,uncle,$2,_)>>. %0.00;0.40%')
        'would be a strange variable introduction when it would be allowed to use ImageExt and not just looking at <SUB --> PRED>
        'this is a strange example I added..
        '''
        pass


    def test_unification_a1(self):
        '''
        'Variable unification

        'If something is a bird, then it is a animal. 
        <<#x-->A> ==> (&&, <#y-->B>, <#x-->C>)>. %1.00;0.90%

        'If something is a robin, then it is a bird. 
        <(&&, <#x-->B>, <#y-->C>) ==> <#x --> D>>. %1.00;0.90%

        3

        'If something is a robin, then it is a animal. 
        ''outputMustContain('<<#1 --> A> ==> <#2 --> D>>. %1.00;0.81%')

        'I guess that if something is a animal, then it is a robin. 
        ''outputMustContain('<<#1 --> D> ==> <#2 --> A>>. %1.00;0.45%')
        '''
        tasks_derived = process_two_premises(
            '<<#x-->A> ==> (&&, <#y-->B>, <#x-->C>)>. %1.00;0.90%',
            '<(&&, <#x-->B>, <#y-->C>) ==> <#x --> D>>. %1.00;0.90%',
            10
        )

        self.assertTrue(
            output_contains(tasks_derived, '<<#0 --> A> ==> <#1 --> D>>. %1.00;0.81%')
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<#0 --> D> ==> <#1 --> A>>. %1.00;0.45%')
        )

        self.assertTrue(
            not output_contains(tasks_derived, '<<$0 --> D> ==> <$0 --> A>>. %1.00;0.45%')
        )

    def test_0(self):
        '''
        <(&&, <#x-->A>, <#x-->B>, <<$y-->C>==><$y-->D>>, <$z-->E>) ==> (&&, <$z-->F>, <#p-->G>, <#p-->H>)>.
        <<(&&, <$x-->F>, <#p-->G>, <#p-->H>)==><$x-->H>>.
        |-
        <(&&, <#x-->A>, <#x-->B>, <<$y-->C>==><$y-->D>>, <$z-->E>) ==> <$x-->H>>.
        '''

        tasks_derived = rule_map_two_premises(
            "<(&&, <#x-->A>, <#x-->B>, <<$y-->C>==><$y-->D>>, <$z-->E>) ==> (&&, <$z-->F>, <#p-->G>, <#p-->H>)>. %1.00;0.90%", 
            "<(&&, <$x-->F>, <#p-->G>, <#p-->H>)==><$x-->H>>. %1.00;0.90%", 
            10)
        self.assertTrue(
            output_contains(tasks_derived, "<(&&, <#x-->A>, <#x-->B>, <<$y-->C>==><$y-->D>>, <$z-->E>) ==> <$z-->H>>. %1.00;0.81%")
        )
        pass


    def test_1(self):
        '''
        (&&, <#x-->A>, <#x-->B>, <<$y-->C>==><$y-->D>>).
        <$x-->D>.
        |-
        <(&&, <#x-->A>, <#x-->B>, <<$y-->C>==><$y-->D>>, <$z-->E>) ==> <$x-->H>>.
        '''
        from pynars.Narsese import Budget
        task = Narsese.parse("(&&, <#x-->A>, <#x-->B>, <<$y-->C>==><$y-->D>>).")
        belief = Narsese.parse("<$x-->D>.")
        term_common = Narsese.parse("<<$y-->C>==><$y-->D>>.").term
        nars.memory.accept(task)
        nars.memory.accept(belief)
        concept = nars.memory.take_by_key(term_common)
        task_link = concept.task_links.take_by_key(TaskLink(concept, task, None, index=(2, )))
        term_link = concept.term_links.take_by_key(TermLink(concept, belief, None, index=(1, )))
        belief.term[0]._vars_independent.indices[0](1)
        
        subst, _, _ = GeneralEngine.unify(task.term, belief.term, term_common, task_link, term_link)
        self.assertIsNotNone(subst)
        term = subst.apply()
        self.assertEqual(term._vars_independent.indices[0], 1)
        self.assertEqual(term._vars_independent.indices[1], 1)
        pass


if __name__ == '__main__':

    test_classes_to_run = [
        TEST_NAL6
    ]

    loader = unittest.TestLoader()

    suites = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites.append(suite)
        
    suites = unittest.TestSuite(suites)

    runner = unittest.TextTestRunner()
    results = runner.run(suites)