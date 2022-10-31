import NARS
import unittest

from pynars.NARS.DataStructures import Bag, Task, Concept, Table
from pynars.Narsese import Judgement, Term, Statement, Copula, Truth   

from pathlib import Path
import Narsese
from pynars.Narsese import Compound, Connector
from pynars.NAL.MetaLevelInference.VariableSubstitution import *
from pynars.Narsese import Terms

class TEST_Substitution(unittest.TestCase):

    def test_substition_var_to_var(self):
        '''
        <(&&, <#x-->A>, <#x-->B>, <<$y-->C>==><$y-->D>>, <$z-->E>) ==> <$z-->F>>.
        <<$x-->F>==><$x-->H>>.
        |-
        <(&&, <#x-->A>, <#x-->B>, <<$y-->C>==><$y-->D>>, <$z-->E>) ==> <$x-->H>>.
        '''
        term1 = Narsese.parse("<(&&, <#x-->A>, <#x-->B>, <<$y-->C>==><$y-->D>>, <$z-->E>) ==> <$z-->F>>.").term
        term2 = Narsese.parse("<<$x-->F>==><$x-->H>>.").term
        subst_var = unification__var_var(term1, term2, [1], [0]) # to find possible replacement.
        term2 = subst_var.apply(inverse=True)
        term3 = Statement.Implication(term1[0], term2[1])
        # term_substitution = substitution(compound, Term("A"), Term("D"))
        # self.assertEqual(term_substitution, term_new)
        pass

    def test_substition_var_to_const_0(self):
        '''
        <<$x-->A>==><$x-->B>>.
        <<C-->B>==><C-->D>>.
        |-
        <<C-->A>==><C-->D>>
        '''
        term1 = Narsese.parse("<<$x-->A>==><$x-->B>>.").term
        term2 = Narsese.parse("<<C-->B>==><C-->D>>.").term
        self.assertTrue(term1[1].equal(term2[0]))
        subst_var = unification__var_const(term1, term2, [1], [0]) # to find possible replacement.
        term2 = subst_var.apply(inverse=True)
        term3 = Statement.Implication(term1[0], term2[1])
        # term_substitution = substitution(compound, Term("A"), Term("D"))
        # self.assertEqual(term_substitution, term_new)
        pass

    def test_substition_var_to_const_1(self):
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
        subst_var = unification__var_const(term1, term2, [0], [1]) # to find possible replacement.
        term2 = subst_var.apply()
        term3 = Statement.Implication(term1[0], term2[1])
        # term_substitution = substitution(compound, Term("A"), Term("D"))
        # self.assertEqual(term_substitution, term_new)
        pass

    def test_check_conflict(self):
        '''
        <<$x-->A>==><$x-->B>>.
        <<C-->B>==><C-->D>>.
        |-
        <<C-->A>==><C-->D>>
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
