from opennars import NARS
import unittest

from opennars.NARS.DataStructures import Bag, Task, Concept, Table
from opennars.Narsese import Judgement, Term, Statement, Copula, Truth   

from pathlib import Path
from opennars import Narsese
from opennars.Narsese import Compound, Connector
from opennars.NAL.MetaLevelInference.VariableSubstitution import *
from opennars.Narsese._py.Variable import VarPrefix, Variable
from opennars.utils.IndexVar import IndexVar

class TEST_Compound(unittest.TestCase):
    def test_0(self):
        c1 = Compound.ExtensionalSet(Term("A"), Term("B"))
        c2 = Compound.ExtensionalSet(Term("B"), Term("C"))
        c3 = c1-c2
        c4 = Compound.ExtensionalSet(Term("A"))
        self.assertEqual(c3, c4)
        pass

    def test_1(self):
        c1 = Compound.ExtensionalSet(Term("A"), Term("B"))
        c2 = Compound.ExtensionalSet(Term("B"), Term("C"))
        c3 = c1-c2
        c4 = Compound.ExtensionalSet(Term("A"))
        c5 = c2-c1
        c6 = c1 - Term("A")
        c7 = Term("A") - c1
        self.assertEqual(c3, c4)
        pass

    def test_mix_several_term_0(self):
        c1 = Compound.ExtensionalSet(Term("A"), Term("B"))
        c2 = Compound.ExtensionalSet(Term("B"), Term("C"))
        c3 = Compound.ExtensionalSet(c1, c2)
        c4 = Compound.ExtensionalSet(Term("A"), Term("B"), Term("C"))
        self.assertEqual(c3, c4)

        c5 = Compound.ExtensionalSet(c1, c2, Term("A"))
        c6 = Compound.ExtensionalSet(c3, Term("A"))
        self.assertEqual(c5, c6)
        self.assertEqual(str(c5), '{A, B, C}')

        c7 = Compound.IntensionalSet(Term("A"))
        c8 = Compound.ExtensionalSet(c1, c2, c7, Term("A"))
        c9 = Compound.ExtensionalSet(c3, c7, Term("A"))
        self.assertEqual(c8, c9)
        self.assertEqual(str(c8), '{A, B, C, [A]}')
        pass

    def test_mix_several_terms_1(self):
        c1 = Compound.ExtensionalSet(Term("A"), Term("B"))
        c2 = Compound.ExtensionalSet(Term("B"), Term("C"))
        c3 = Compound.ExtensionalIntersection(c1, c2)
        c4 = Compound.ExtensionalSet(Term("B"))
        self.assertEqual(c3, c4)

        pass

    def test_mix_several_terms_2(self):
        c1 = Compound.IntensionalSet(Term("A"), Term("B"))
        c2 = Compound.IntensionalSet(Term("B"), Term("C"))
        c3 = Compound.IntensionalIntersection(c1, c2)
        c4 = Compound.IntensionalSet(Term("B"))
        self.assertEqual(c3, c4)

        pass

    def test_mix_several_terms_3(self):
        c1 = Compound.IntensionalSet(Term("A"), Term("B"))
        c2 = Compound.IntensionalSet(Term("B"), Term("C"))
        c3 = Compound.IntensionalSet(c1, c2)
        c4 = Compound.IntensionalSet(Term("A"), Term("B"), Term("C"))
        self.assertEqual(c3, c4)

        pass

    def test_compound_variable_0(self):
        '''
        <(&&, <$x-->A>, <$y-->A>) ==> (&&, <$x-->B>, <$y-->C>)>.
        '''
        term = Narsese.parse("<(&&, <$x-->A>, <$y-->A>) ==> (&&, <$x-->B>, <$y-->C>)>.").term
        repr(term[0])
        self.assertEqual(len(term[0].terms), 2)

    
    def test_compound_variable_1(self):
        line = '(&&, <(&&, <#x-->bird>, <#x-->swimer>)-->#y>, <swan-->#y>).'
        term = Narsese.parse(line).term
        pass
        

if __name__ == '__main__':

    test_classes_to_run = [
        TEST_Compound
    ]

    loader = unittest.TestLoader()

    suites = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites.append(suite)
        
    suites = unittest.TestSuite(suites)

    runner = unittest.TextTestRunner()
    results = runner.run(suites)
