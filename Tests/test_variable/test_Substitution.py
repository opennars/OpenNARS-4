from pynars import Narsese, NARS
import unittest

from pynars.NARS.DataStructures import Bag, Task, Concept, Table
from pynars.Narsese import Judgement, Term, Statement, Copula, Truth   

from pathlib import Path
from pynars.Narsese import Compound, Connector
from pynars.NAL.MetaLevelInference.VariableSubstitution import *
from pynars.Narsese import Terms, VarPrefix

class TEST_Substitution(unittest.TestCase):

    def test_substition_var_to_var_0(self):
        '''
        <(&&, <#x-->A>, <#x-->B>, <<$y-->C>==><$y-->D>>, <$z-->E>) ==> <$z-->F>>.
        <<$x-->F>==><$x-->H>>.
        |-
        <(&&, <#x-->A>, <#x-->B>, <<$y-->C>==><$y-->D>>, <$z-->E>) ==> <$x-->H>>.
        '''
        term1 = Narsese.parse("<(&&, <#x-->A>, <#x-->B>, <<$y-->C>==><$y-->D>>, <$z-->E>) ==> <$z-->F>>.").term
        term2 = Narsese.parse("<<$x-->F>==><$x-->H>>.").term
        subst_var = get_substitution__var_var(term1, term2, [1], [0]) # to find possible replacement.
        term3 = subst_var.apply()
        term4 = Statement.Implication(term3[0], term2[1])
        term5 = Narsese.parse("<(&&, <#x-->A>, <#x-->B>, <<$y-->C>==><$y-->D>>, <$z-->E>) ==> <$z-->H>>.").term
        self.assertTrue(term4.identical(term5))
        pass
    
    def test_substition_var_to_var_1(self):
        '''
        <(&&, <#x-->A>, <#x-->B>, <<$y-->C>==><$y-->D>>, <$z-->E>) ==> (&&, <$z-->F>, <#p-->G>, <#p-->H>)>.
        <<(&&, <$x-->F>, <#p-->G>, <#p-->H>)==><$x-->H>>.
        |-
        <(&&, <#x-->A>, <#x-->B>, <<$y-->C>==><$y-->D>>, <$z-->E>) ==> <$x-->H>>.
        '''
        term1 = Narsese.parse("<(&&, <#x-->A>, <#x-->B>, <<$y-->C>==><$y-->D>>, <$z-->E>) ==> (&&, <$z-->F>, <#p-->G>, <#p-->H>)>.").term
        term2 = Narsese.parse("<(&&, <$x-->F>, <#p-->G>, <#p-->H>)==><$x-->H>>.").term
        subst_var = get_substitution__var_var(term1, term2, [1], [0]) # to find possible replacement.
        term3 = subst_var.apply()
        term4 = Statement.Implication(term3[0], term2[1])
        term5 = Narsese.parse("<(&&, <#x-->A>, <#x-->B>, <<$y-->C>==><$y-->D>>, <$z-->E>) ==> <$z-->H>>.").term
        self.assertTrue(term4.identical(term5))
        pass



    def test_introduction_const_to_var_0(self):
        '''
        <swan-->bird>.
        <swan-->animal>.
        |-
        <<$x-->bird>==><$x-->animal>>.
        '''
        term1 = Narsese.parse("<swan-->bird>.").term
        term2 = Narsese.parse("<swan-->animal>.").term
        term_common = Term('swan')
        intro_var: Introduction = get_introduction__const_var(term1, term2, term_common)
        term1, term2 = intro_var.apply(type_var=VarPrefix.Independent)
        term3 = Statement.Implication(term1, term2)
        print(term1)
        print(term2)
        print(term3)

    def test_introduction_const_to_var_0_1(self):
        '''
        '''
        term1 = Narsese.parse("(&&, <<A-->B>==>B>, B, C).").term
        term2 = Narsese.parse("(&&, A, B, C).").term
        term_common = Term('A')
        intro_var: Introduction = get_introduction__const_var(term1, term2, term_common)
        term1, term2 = intro_var.apply(type_var=VarPrefix.Independent)
        term3 = Statement.Implication(term1, term2)
        print(term1.repr())
        print(term2.repr())
        print(term3.repr())


    def test_introduction_const_to_var_1(self):
        '''
        Valid Syntax, Invalid Semantic
        <swan-->(&&, <#x-->bird>, <#x-->swimer>)>.
        <swan-->animal>.
        '''
        term1 = Narsese.parse("<swan-->(&&, <#x-->bird>, <#x-->swimer>)>.").term
        term2 = Narsese.parse("<swan-->animal>.").term
        term_common = Term('swan')
        intro_var: Introduction = get_introduction__const_var(term1, term2, term_common)
        term1, term2 = intro_var.apply(type_var=VarPrefix.Dependent)
        term3 = Compound.Conjunction(term1, term2)
        print(term1.repr())
        print(term2.repr())
        print(term3.repr())

    
    def test_introduction_const_to_var_2(self):
        '''
        Valid Syntax, Invalid Semantic
        <(&&, <#x-->bird>, <#x-->swimer>)-->animal>.
        <swan-->animal>.
        '''
        term1 = Narsese.parse("<(&&, <#x-->bird>, <#x-->swimer>)-->animal>.").term
        term2 = Narsese.parse("<swan-->animal>.").term
        term_common = Term('animal')
        intro_var: Introduction = get_introduction__const_var(term1, term2, term_common)
        term1, term2 = intro_var.apply(type_var=VarPrefix.Dependent)
        term3 = Compound.Conjunction(term1, term2)
        print(term1.repr())
        print(term2.repr())
        print(term3.repr())
        term4 = Narsese.parse("(&&, <(&&, <#x-->bird>, <#x-->swimer>)-->#y>, <swan-->#y>).").term
        self.assertTrue(term3 == term4)

    def test_introduction_const_to_var_3(self):
        '''
        Valid Syntax, Invalid Semantic
        <swan-->(&&, <#1-->bird>, <#1-->swimer>)>.
        <swan-->animal>.
        '''
        # BUG
        term1 = Narsese.parse("<swan-->(&&, <#1-->bird>, <#1-->swimer>)>.").term
        term2 = Narsese.parse("<swan-->animal>.").term
        term_common = Term('swan')
        intro_var: Introduction = get_introduction__const_var(term1, term2, term_common)
        term1, term2 = intro_var.apply(type_var=VarPrefix.Dependent)
        term3 = Compound.Conjunction(term1, term2)
        print(term1.repr())
        print(term2.repr())
        print(term3.repr())
        term4 = Narsese.parse("(&&, <#0-->(&&, <#1-->bird>, <#1-->swimer>)>, <#0-->animal>).").term
        self.assertTrue(term3 == term4)


    def test_elimination_var_to_const_0_0(self):
        '''
        <<$x-->A>==><$x-->B>>.
        <<C-->B>==><C-->D>>.
        |-
        <<C-->A>==><C-->D>>
        '''
        term1 = Narsese.parse("<<$x-->A>==><$x-->B>>.").term
        term2 = Narsese.parse("<<C-->B>==><C-->D>>.").term
        self.assertTrue(term1[1].equal(term2[0]))
        subst_var = get_elimination__var_const(term1, term2, [1], [0]) # to find possible replacement.
        term3 = subst_var.apply()
        term4 = Statement.Implication(term3[0], term2[1])
        # term_substitution = substitution(compound, Term("A"), Term("D"))
        # self.assertEqual(term_substitution, term_new)
        pass

    def test_elimination_var_to_const_0_1(self):
        '''
        <<$x-->A>==><$x-->B>>.
        <<C-->B>==><D-->A>>.
        |-
        <<C-->A>==><D-->A>>
        <<C-->B>==><D-->B>>
        '''
        term1 = Narsese.parse("<<$x-->A>==><$x-->B>>.").term
        term2 = Narsese.parse("<<C-->B>==><D-->A>>.").term
        self.assertTrue(term1[1].equal(term2[0]))
        subst_var = get_elimination__var_const(term1, term2, [1], [0]) # to find possible replacement.
        term3 = subst_var.apply()
        term4 = Statement.Implication(term3[0], term2[1])
        # term_substitution = substitution(compound, Term("A"), Term("D"))
        # self.assertEqual(term_substitution, term_new)
        pass

    def test_elimination_var_to_const_1(self):
        '''
        <(&&, <$x-->A>, <$y-->A>) ==> (&&, <$x-->B>, <$y-->C>)>.
        <<D-->E> ==> (&&, <F-->A>, <G-->A>)>.
        |-
        <<D-->E> ==> (&&, <F-->B>, <G-->C>)>.
        <<D-->E> ==> (&&, <G-->B>, <F-->C>)>.
        '''
        term1 = Narsese.parse("<(&&, <$x-->A>, <$y-->A>) ==> (&&, <$x-->B>, <$y-->C>)>.").term
        term2 = Narsese.parse("<<D-->E> ==> (&&, <F-->A>, <G-->A>)>.").term
        self.assertTrue(term1[0].equal(term2[1]))
        subst_var = get_elimination__var_const(term1, term2, [0], [1]) # to find possible replacement.
        term3 = subst_var.apply()
        term4 = Statement.Implication(term2[0], term3[1])
        # term_substitution = substitution(compound, Term("A"), Term("D"))
        # self.assertEqual(term_substitution, term_new)
        pass

    def test_check_conflict(self):
        '''
        '''
        
        is_conflict, mapping = Elimination.check_conflict([0,0], [Term("C"), Term("D")])
        self.assertTrue(is_conflict)
        pass

    def test_statement_equal_0(self):
        '''
        <<$x-->A><=><$x-->B>>.
        <<C-->A><=><C-->B>>.
        '''
        term1 = Narsese.parse("<<$x-->A><=><$x-->B>>.").term
        term2 = Narsese.parse("<<C-->B><=><C-->A>>.").term
        self.assertTrue(term1.equal(term2))
        pass

    def test_compound_equal_0(self):
        '''
        (&/, <$x-->A>, <$x-->B>).
        (&/, <C-->A>, <C-->B>).
        '''
        term1 = Narsese.parse("(&/, <$x-->A>, <$x-->B>).").term
        term2 = Narsese.parse("(&/, <C-->A>, <C-->B>).").term
        self.assertTrue(term1.equal(term2))
        pass

    def test_compound_equal_1(self):
        '''
        (&&, <$x-->A>, <$x-->B>, <C-->D>).
        (&&, <C-->D>, <E-->B>, <E-->A>).
        '''
        term1 = Narsese.parse("(&&, <$x-->A>, <$x-->B>, <C-->D>).").term
        term2 = Narsese.parse("(&&, <C-->D>, <E-->B>, <E-->A>).").term
        self.assertTrue(term1.equal(term2))
        pass

    def test_compound_equal_2(self):
        '''
        (&&, <$x-->A>, <$x-->B>, <C-->D>).
        (&&, <C-->D>, <E-->B>, <F-->B>).
        '''
        term1 = Narsese.parse("(&&, <$x-->A>, <$x-->B>, <C-->D>).").term
        term2 = Narsese.parse("(&&, <C-->D>, <E-->B>, <F-->B>).").term
        self.assertFalse(term1.equal(term2))
        pass

    def test_substitution_0(self):
        term1 = Narsese.parse("(&&, <$x-->A>, <$x-->B>, <C-->D>).").term
        term2 = Narsese.parse("(&&, <C-->D>, <E-->B>, <F-->B>).").term




if __name__ == '__main__':

    test_classes_to_run = [
        TEST_Substitution
    ]

    loader = unittest.TestLoader()

    suites = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites.append(suite)
        
    suites = unittest.TestSuite(suites)

    runner = unittest.TextTestRunner()
    results = runner.run(suites)
