import unittest

from pynars.NARS.DataStructures import Task
from pynars.NAL.MetaLevelInference.VariableSubstitution import *
# from pynars.NARS.RuleMap import RuleMap

# import Tests.utils_for_test as utils_for_test
from Tests.utils_for_test import *
from pynars.utils.Print import PrintType, out_print


# utils_for_test.rule_map = RuleMap_v2()

# class SubstituteVar:
#     ''''''
#     def __init__(self, mapping_ivar: bidict, mapping_dvar: bidict, mapping_qvar: bidict) -> None:
#         self.mapping_ivar = mapping_ivar
#         self.mapping_dvar = mapping_dvar
#         self.mapping_qvar = mapping_qvar
    
#     @property
#     def is_valid(self):
#         return len(self.mapping_dvar) > 0 or len(self.mapping_ivar) > 0 or len(self.mapping_qvar) > 0

#     @property
#     def is_qvar_valid(self):
#         return len(self.mapping_qvar) > 0
    
#     @property
#     def is_dvar_valid(self):
#         return len(self.mapping_dvar) > 0

#     @property
#     def is_ivar_valid(self):
#         return len(self.mapping_ivar) > 0
    
#     def apply(self, term1: Term, term2: Term, inverse=False):
#         mapping_ivar = self.mapping_ivar
#         mapping_dvar = self.mapping_dvar
#         mapping_qvar = self.mapping_qvar
#         if inverse:
#             term1, term2 = term2, term1            
#             mapping_ivar = mapping_ivar.inverse
#             mapping_dvar = mapping_dvar.inverse
#             mapping_qvar = mapping_qvar.inverse
#         ivar = [int(var) for var in term2._index_var.var_independent]
#         dvar = [int(var) for var in term2._index_var.var_dependent]
#         qvar = [int(var) for var in term2._index_var.var_query]

#         term2._index_var.var_independent = [var(mapping_ivar[var_int]) for var, var_int in zip(term2._index_var.var_independent, ivar)]
#         term2._index_var.var_dependent = [var(mapping_dvar[var_int]) for var, var_int in zip(term2._index_var.var_dependent, dvar)]
#         term2._index_var.var_query = [var(mapping_qvar[var_int]) for var, var_int in zip(term2._index_var.var_query, qvar)]
#         # TODO: to recursively apply the variable-mapping to the terms.



# find_var_with_pos: Callable = lambda pos_search, variables, positions: [var for var, pos in zip(variables, positions) if pos[:len(pos_search)] == pos_search]

# def _build_mapping(variables1, variables2, var_common1, var_common2):
#     if len(variables1) == 0 and len(variables2) == 0:
#         mapping = bidict()
#     elif len(variables1) > 0 and len(variables2) > 0:
#         var_diff1 = sorted(list(set(variables1)-set(var_common1)))
#         var_diff2 = sorted(list(set(variables2)-set(var_common2)))
#         var_bias1 = max(variables1) + 1
#         var_bias2 = max(variables2) + 1
#         var_diff_new1 = [ivar+var_bias2 for ivar in var_diff1]
#         var_diff_new2 = [ivar+var_bias1 for ivar in var_diff2]
#         # mapping the second to the first
#         mapping = bidict({int(key): int(value) for key, value in (*zip(var_common2, var_common1), *zip(var_diff2, var_diff_new2), *zip(var_diff_new1, var_diff1))})
#     else: # (len(variables1) > 0) ^ (len(variables2) > 0)
        
#         mapping = bidict()
#         pass
#     return mapping

# def unification__var_var(term1: Term, term2: Term, pos_common1: List[int], pos_common2: List[int]):
#     ''''''
#     # 1. find the variables in the first common position
#     ivar1 = find_var_with_pos(pos_common1, term1._index_var.var_independent, term1._index_var.positions_ivar)
#     dvar1 = find_var_with_pos(pos_common1, term1._index_var.var_dependent, term1._index_var.positions_dvar)
#     qvar1 = find_var_with_pos(pos_common1, term1._index_var.var_query, term1._index_var.positions_qvar)

#     # 2. find the variables in the second common position
#     ivar2 = find_var_with_pos(pos_common2, term2._index_var.var_independent, term2._index_var.positions_ivar)
#     dvar2 = find_var_with_pos(pos_common2, term2._index_var.var_dependent, term2._index_var.positions_dvar)
#     qvar2 = find_var_with_pos(pos_common2, term2._index_var.var_query, term2._index_var.positions_qvar)

#     # 3. build the mapping
#     mapping_ivar = _build_mapping(term1._index_var.var_independent, term2._index_var.var_independent, ivar1, ivar2)
#     mapping_dvar = _build_mapping(term1._index_var.var_dependent, term2._index_var.var_dependent, dvar1, dvar2)
#     mapping_qvar = _build_mapping(term1._index_var.var_query, term2._index_var.var_query, qvar1, qvar2)

#     return SubstituteVar(mapping_ivar, mapping_dvar, mapping_qvar)



class TEST_NAL6(unittest.TestCase):
    ''''''

    # def test_substition_var_to_var(self):
    #     '''
    #     <(&&, <#x-->A>, <#x-->B>, <<$y-->C>==><$y-->D>>, <$z-->E>) ==> <$z-->F>>.
    #     <<$x-->F>==><$x-->H>>.
    #     |-
    #     <(&&, <#x-->A>, <#x-->B>, <<$y-->C>==><$y-->D>>, <$z-->E>) ==> <$x-->H>>.
    #     '''
    #     term1 = Narsese.parse("<<$x-->F>==><$x-->H>>.").term
    #     term2 = Narsese.parse("<(&&, <#x-->A>, <#x-->B>, <<$y-->C>==><$y-->D>>, <$z-->E>) ==> <$z-->F>>.").term
    #     subst_var = unification__var_var(term1, term2, [0], [1]) # to find possible replacement.
    #     subst_var.apply(term1, term2)
    #     # subst_var.apply()
    #     term3 = Statement.Implication(term1[0], term2[1])
    #     # term_substitution = substitution(compound, Term("A"), Term("D"))
    #     # self.assertEqual(term_substitution, term_new)
    #     pass

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
        tasks_derived = memory_accept_revision(
            '<<$x --> bird> ==> <$x --> flyer>>. %1.00;0.90%',
            '<<$y --> bird> ==> <$y --> flyer>>. %0.00;0.70%'
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
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '<<$x --> bird> ==> <$x --> animal>>. %1.00;0.90%',
            '<<$y --> robin> ==> <$y --> bird>>. %1.00;0.90%',
            '<$x --> bird>.', index_task=(0,), index_belief=(1,)
        )
        self.assertNotEqual(rules, None)

        subst_var = get_substitution__var_var(task.term, belief.term, [0], [1]) # to find possible replacement.
        subst_var.apply(task.term, belief.term)
        tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 

        repr(tasks_derived[0].term)
        self.assertTrue(
            output_contains(tasks_derived, '<<$1 --> robin> ==> <$1 --> animal>>. %1.00;0.81%')
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<$1 --> animal> ==> <$1 --> robin>>. %1.00;0.45%')
        )

        self.assertTrue(
            not output_contains(tasks_derived, '<<$1 --> animal> ==> <$2 --> robin>>. %1.00;0.45%')
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

        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '<<$x --> swan> ==> <$x --> bird>>. %1.00;0.80% ',
            '<<$y --> swan> ==> <$y --> swimmer>>. %0.80;0.90%',
            '<$x --> swan>.'
        )
        self.assertNotEqual(rules, None)

        subst_var = get_substitution__var_var(task.term, belief.term, [0], [0]) # to find possible replacement.
        subst_var.apply(task.term, belief.term)
        tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 


        self.assertTrue(
            output_contains(tasks_derived, '<<$1 --> swan> ==> (||,<$1 --> bird>,<$1 --> swimmer>)>. %1.00;0.72%')
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<$1 --> swan> ==> (&&,<$1 --> bird>,<$1 --> swimmer>)>. %0.80;0.72%')
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<$1 --> swimmer> ==> <$1 --> bird>>. %1.00;0.37%')
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<$1 --> bird> ==> <$1 --> swimmer>>. %0.80;0.42%')
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<$1 --> bird> <=> <$1 --> swimmer>>. %0.80;0.42%')
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
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '<<bird --> $x> ==> <robin --> $x>>. %1.00;0.90%',
            '<<swimmer --> $y> ==> <robin --> $y>>. %0.70;0.90%',
            '<robin --> $x>.'
        )
        self.assertNotEqual(rules, None)

        subst_var = get_substitution__var_var(task.term, belief.term, [1], [1]) # to find possible replacement.
        subst_var.apply(task.term, belief.term)
        tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 

        self.assertTrue(
            output_contains(tasks_derived, '<(&&,<bird --> $1>,<swimmer --> $1>) ==> <robin --> $1>>. %1.00;0.81%')
        )
        self.assertTrue(
            output_contains(tasks_derived, '<(||,<bird --> $1>,<swimmer --> $1>) ==> <robin --> $1>>. %0.70;0.81%')
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<bird --> $1> ==> <swimmer --> $1>>. %1.00;0.36%')
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<swimmer --> $1> ==> <bird --> $1>>. %0.70;0.45%')
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<bird --> $1> <=> <swimmer --> $1>>. %0.70;0.45%')
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
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '<(&&,<$x --> flyer>,<$x --> [chirping]>) ==> <$x --> bird>>. %1.00;0.90%',
            '<<$y --> [with_wings]> ==> <$y --> flyer>>. %1.00;0.90%',
            '<$y --> flyer>.'
        )
        self.assertNotEqual(rules, None)

        subst_var = get_substitution__var_var(task.term, belief.term, [0,0], [1]) # to find possible replacement.
        subst_var.apply(task.term, belief.term)
        tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 

        self.assertTrue(
            output_contains(tasks_derived, '<(&&,<$1 --> [chirping]>,<$1 --> [with_wings]>) ==> <$1 --> bird>>. %1.00;0.81%')
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
        <(&&,<$x --> flyer>,<(*,$x,worms) --> food>) ==> <$x --> bird>>.

        'If something can fly, then it has wings.
        <<$y --> flyer> ==> <$y --> [with_wings]>>.

        // 4 originally
        13 

        'If something has wings and eats worms, then I guess it is a bird.
        ''outputMustContain('<(&&,<$1 --> [with_wings]>,<(*,$1,worms) --> food>) ==> <$1 --> bird>>. %1.00;0.45%')
        '''
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
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '<<$x --> bird> ==> <$x --> animal>>. %1.00;0.90%',
            '<robin --> bird>. %1.00;0.90%',
            'bird.'
        )
        self.assertNotEqual(rules, None)

        subst_var = get_substitution__var_var(task.term, belief.term, [0], [0]) # to find possible replacement.
        subst_var.apply(task.term, belief.term)
        tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 


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
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '<<$x --> lock> ==> (&&,<#y --> key>,<$x --> (/,open,#y,_)>)>. %1.00;0.90%',
            '<{lock1} --> lock>. %1.00;0.90%',
            'lock.'
        )
        self.assertNotEqual(rules, None)
        
        tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 

        self.assertTrue(
            output_contains(tasks_derived, '(&&,<#1 --> key>,<{lock1} --> (/,open,#1,_)>). %1.00;0.81%')
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
        pass


    def test_introduction_0(self):
        '''
        'Introduction

        'A swan is a bird.
        <swan --> bird>.  

        'A swan is usually a swimmer.
        <swan --> swimmer>. %0.80%

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
        pass


    def test_introduction_1(self):
        '''
        'Introduction

        'A gull is a swimmer.
        <gull --> swimmer>. 

        'Usually, a swan is a swimmer.
        <swan --> swimmer>. %0.80% 

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
        pass


    def test_introduction_2(self):
        '''
        'Introduction

        'Key-1 opens Lock-1.
        <{key1} --> (/,open,_,{lock1})>. 

        'Key-1 is a key.
        <{key1} --> key>.

        45

        'I guess every key can open Lock-1.
        ''outputMustContain('<<$1 --> key> ==> <$1 --> (/,open,_,{lock1})>>. %1.00;0.45%')

        'Some key can open Lock-1.
        ''//outputMustContain('(&&,<#1 --> (/,open,_,{lock1})>,<#1 --> key>). %1.00;0.81%') //reversed
        ''  outputMustContain('(&&,<#1 --> (/,open,_,{lock1})>,<#1 --> key>). %1.00;0.25%')
        '''
        pass


    def test_multiple_variables_introduction_0(self):
        '''
        'Multiple variables introduction

        'Lock-1 can be opened by every key.
        <<$x --> key> ==> <{lock1} --> (/,open,$x,_)>>. 

        'Lock-1 is a lock.
        <{lock1} --> lock>. 

        166

        'There is a lock that can be opened by every key.
        ''outputMustContain('(&&,<#1 --> lock>,<<$2 --> key> ==> <#1 --> (/,open,$2,_)>>). %1.00;0.81%')

        'I guess every lock can be opened by every key.
        ''outputMustContain('<(&&,<$1 --> key>,<$2 --> lock>) ==> <$2 --> (/,open,$1,_)>>. %1.00;0.45%')
        '''
        pass


    def test_multiple_variables_introduction_1(self):
        '''
        'Multiple variables introduction

        'Lock-1 can be opened by some key.
        (&&,<#x --> key>,<{lock1} --> (/,open,#x,_)>).  

        'Lock-1 is a lock.
        <{lock1} --> lock>. 

        17

        'There is a key that can open some lock.
        ''outputMustContain('(&&,<#1 --> key>,<#2 --> (/,open,#1,_)>,<#2 --> lock>). %1.00;0.81%')

        'I guess every lock can be opened by some key.
        ''outputMustContain('<<$1 --> lock> ==> (&&,<#2 --> key>,<$1 --> (/,open,#2,_)>)>. %1.00;0.45%')
        '''
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
        pass


    def test_second_variable_introduction_induction(self):
        '''
        'Second variable introduction (induction)

        'if something opens lock1, it is a key
        <<lock1 --> (/,open,$1,_)> ==> <$1 --> key>>.

        'lock1 is a key
        <lock1 --> lock>.

        7

        'there is a lock with the property that when opened by something, this something is a key (induction)
        ''outputMustContain('<(&&,<#1 --> (/,open,$2,_)>,<#1 --> lock>) ==> <$2 --> key>>. %1.00;0.45%')    
        '''
        pass


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
        pass


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
        rules, task, belief, concept, task_link, term_link, result1, result2 = rule_map_two_premises(
            '<<#x-->A> ==> (&&, <#y-->B>, <#x-->C>)>. %1.00;0.90%',
            '<(&&, <#x-->B>, <#y-->C>) ==> <#x --> D>>. %1.00;0.90% ',
            '(&&, <#y-->B>, <#x-->C>).'
        )
        self.assertNotEqual(rules, None)

        subst_var = get_substitution__var_var(task.term, belief.term, [1], [0]) # to find possible replacement.
        subst_var.apply(task.term, belief.term)
        tasks_derived = [rule(task, belief, task_link, term_link) for rule in rules] 

        self.assertTrue(
            output_contains(tasks_derived, '<<#1 --> A> ==> <#2 --> D>>. %1.00;0.81%')
        )
        self.assertTrue(
            output_contains(tasks_derived, '<<#1 --> D> ==> <#2 --> A>>. %1.00;0.45%')
        )

        self.assertTrue(
            not output_contains(tasks_derived, '<<$1 --> D> ==> <$1 --> A>>. %1.00;0.45%')
        )
        print("")
        out_print(PrintType.IN, task.sentence.repr, *task.budget)
        out_print(PrintType.IN, belief.sentence.repr, *belief.budget)
        for task in tasks_derived:
            task: Task
            out_print(PrintType.OUT, task.sentence.repr, *task.budget)
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