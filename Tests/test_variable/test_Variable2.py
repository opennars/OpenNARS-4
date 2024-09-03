from opennars import Narsese, NARS
import unittest

from opennars.NARS.DataStructures import Bag, Task, Concept, Table
from opennars.Narsese import Judgement, Term, Statement, Copula, Truth   

from pathlib import Path
from opennars.Narsese import Compound, Connector
from opennars.NAL.MetaLevelInference.VariableSubstitution import *
from opennars.Narsese._py.Variable import VarPrefix, Variable
from opennars.utils.IndexVar import IndexVar

class TEST_Variable(unittest.TestCase):

    def test_equal_0(self):
        c1 = Narsese.parse("(&&, <#x-->A>, <#x -->B>, <#y-->A>, <#y -->C>).").term
        c2 = Narsese.parse("(&&, <#x-->A>, <#y -->B>, <#y-->A>, <#x -->C>).").term


    def test_equal_1(self):
        ''''''
        term1 = Narsese.parse("<robin-->bird>.").term
        term2 = Narsese.parse("<#1-->bird>.").term
        term3 = Narsese.parse("<$1-->bird>.").term
        term4 = Narsese.parse("<robin-->$1>.").term
        self.assertTrue(term1.equal(term2))
        self.assertTrue(term1.equal(term3))
        self.assertTrue(term1.equal(term4))
        self.assertTrue(term2.equal(term4))
        self.assertTrue(term3.equal(term4))
        self.assertFalse(term2.equal(term3))
        pass



if __name__ == '__main__':

    test_classes_to_run = [
        TEST_Variable
    ]

    loader = unittest.TestLoader()

    suites = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites.append(suite)
        
    suites = unittest.TestSuite(suites)

    runner = unittest.TextTestRunner()
    results = runner.run(suites)
