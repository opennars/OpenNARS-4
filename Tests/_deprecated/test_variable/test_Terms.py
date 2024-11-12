from opennars import NARS, Narsese
import unittest

from opennars.NARS.DataStructures import Bag, Task, Concept, Table
from opennars.Narsese import Judgement, Term, Statement, Copula, Truth   

from pathlib import Path
from opennars.Narsese import Compound, Connector
from opennars.NAL.MetaLevelInference.VariableSubstitution import *
from opennars.Narsese import Terms

class TEST_Terms(unittest.TestCase):

    def test_terms_0(self):
        
        term1 = Narsese.parse("<#x-->A>.").term
        term2 = Narsese.parse("<#x-->B>.").term
        term3 = Narsese.parse("<#y-->A>.").term
        term4 = Narsese.parse("<#y-->C>.").term
        term3._vars_dependent.indices[0](1)
        term4._vars_dependent.indices[0](1)
        terms1 = Terms((term1, term2), True)
        terms2 = Terms((term3, term4), True)
        terms3 = Terms((term1, term2, term3, term4), True)
        terms4 = Terms((term4, ), True)
        terms4[0]._vars_dependent.indices[0](0)

        terms4[0] == term4
        
        terms_union_1_2 = Terms.union(terms1, terms2)
        terms_inter_1_3 = Terms.intersection(terms1, terms3)
        terms_difference_3_2 = Terms.difference(terms3, terms2)
        
        terms3.issuperset(terms4)
        term1 = Narsese.parse("<$x-->A>.").term
        term2 = Narsese.parse("<$x-->A>.").term
        term2._vars_independent.indices[0](1)
        term2[0]._hash_value = None
        term2[1]._hash_value = None
        term2._hash_value = None
        print(hash(term1))
        print(hash(term2))
        pass

    def test_terms_1(self):
        
        term1 = Narsese.parse("<#x-->A>.").term
        term2 = Narsese.parse("<#x-->B>.").term
        term3 = Narsese.parse("<#y-->A>.").term
        term4 = Narsese.parse("<#y-->C>.").term
        terms1 = Terms((term1, term2), True, True)
        terms2 = Terms((term3, term4), False, True)
        terms3 = Terms((term1, term2, term3, term4), True, True)

        terms_union_1_2 = Terms.union(terms1, terms2)
        terms_inter_1_3 = Terms.intersection(terms1, terms3)
        terms_difference_3_2 = Terms.difference(terms3, terms2)
        
        terms_union_2_1 = Terms.union(terms2, terms1)
        pass

    def test_compound_0(self):
        ''''''
        term1 = Narsese.parse("(&&, <$x-->A>, <$y-->A>).").term
        repr(term1)
        term2 = Narsese.parse("(&/, <$x-->A>, <$y-->A>).").term
        pass

    def test_compound_1(self):
        '''
        {{<$x-->A>}, {<$y-->A>}}.
        |-
        {<$x-->A>, <$y-->A>}
        '''
        term1 = Narsese.parse("{{<$x-->A>}, {<$y-->A>}}.").term
        repr(term1)
        pass

    def test_compound_2(self):
        '''
        (&, {A, B}, {B,C}).
        '''
        term1 = Narsese.parse("(&, {A, B}, {B,C}).").term
        repr(term1)
        pass

    def test_compound_3(self):
        '''
        (&, [<A-->B>], [<C-->D>]).
        '''
        term1 = Narsese.parse("(&, [<A-->B>], [<C-->D>]).").term
        repr(term1)
        pass

    def test_compound_4(self):
        '''
        (&, {A,B,C}, {B,C,D}, [E, F], [F, G]).
        |-
        (&, {B,C}, [E, F, G]).
        '''
        term1 = Narsese.parse("(&, {A,B,C}, {B,C,D}, [E, F], [F, G]).").term
        repr(term1)
        self.assertEqual(str(term1).replace(' ', ''), '(&, {B,C}, [E, F, G])'.replace(' ', ''))
        pass


    def test_compound_5(self):
        '''
        (&, {<$x-->A>, <$x-->B>, <$y-->A>}, {<$y-->B>, <$y-->A>}, [<$x-->A>, <$x-->B>, <$y-->A>], [<$y-->B>, <$y-->A>]).
        |-
        (&, {<$y-->A>}, [<$x-->A>, <$x-->B>, <$y-->A>, <$y-->B>]).
        '''
        term1 = Narsese.parse("(&, {<$x-->A>, <$x-->B>, <$y-->A>}, {<$y-->B>, <$y-->A>}, [<$x-->A>, <$x-->B>, <$y-->A>], [<$y-->B>, <$y-->A>]).").term
        repr(term1)
        pass



if __name__ == '__main__':

    test_classes_to_run = [
        TEST_Terms
    ]

    loader = unittest.TestLoader()

    suites = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites.append(suite)
        
    suites = unittest.TestSuite(suites)

    runner = unittest.TextTestRunner()
    results = runner.run(suites)
