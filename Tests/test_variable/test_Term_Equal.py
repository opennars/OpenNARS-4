from pynars import Narsese, NARS
import unittest

from pynars.NARS.DataStructures import Bag, Task, Concept, Table
from pynars.Narsese import Judgement, Term, Statement, Copula, Truth   

from pathlib import Path
from pynars.Narsese import Compound, Connector
from pynars.NAL.MetaLevelInference.VariableSubstitution import *
from pynars.Narsese._py.Variable import VarPrefix, Variable
from pynars.utils.IndexVar import IndexVar

class TEST_Term_Equal(unittest.TestCase):

    def test_identical(self):
        ''''''
        '''
        (&&, <#x-->A>, <B-->C>) and (&&, <B-->C>, <{A1}-->A>) are equal, thought not identical.
        '''
        term1 = Narsese.parse('(&&, <#x-->A>, <B-->C>).').term
        term2 = Narsese.parse('(&&, <B-->C>, <#y-->A>).').term
        self.assertTrue(term1.identical(term2))
        pass

    def test_term_equal_0(self):
        term1 = Term("bird")
        term2 = Term("bird")
        self.assertTrue(term1.equal(term2))
        pass

    def test_term_equal_1(self):
        term1 = Term("bird")
        term2 = Term("animal")
        self.assertFalse(term1.equal(term2))
        pass

    def test_term_equal_2(self):
        term1 = Term("bird")
        term2 = Variable.Independent("x")
        self.assertTrue(term1.equal(term2))
        pass

    def test_mix_equal_0(self):
        term1 = Term("bird")
        term2 = Statement.Inheritance(Term("brid"), Term("animal"))
        self.assertFalse(term1.equal(term2))
        self.assertFalse(term2.equal(term1))
        pass
    

    def test_mix_equal_1(self):
        term1 = Term("bird")
        term2 = Compound.ExtensionalIntersection(Term("brid"), Term("monkey"))
        self.assertFalse(term1.equal(term2))
        self.assertFalse(term2.equal(term1))
        pass


    def test_mix_equal_2(self):
        term1 = Statement.Inheritance(Term("brid"), Term("animal"))
        term2 = Compound.ExtensionalIntersection(Term("brid"), Term("animal"))
        self.assertFalse(term1.equal(term2))
        self.assertFalse(term2.equal(term1))
        pass


    def test_mix_equal_3(self):
        term1: Statement = Narsese.parse("<<$x-->A> ==> <$x-->B>>.").term
        term2 = Narsese.parse("<(&&, <#x-->C>, <#x-->D>)-->A>.").term
        self.assertTrue(term1.subject.equal(term2))
        self.assertTrue(term2.equal(term1.subject))
        pass
    

    def test_statement_equal_0(self):
        term1 = Statement.Inheritance(Term("bird"), Term("animal"))
        term2 = Statement.Inheritance(Term("bird"), Term("animal"))
        self.assertTrue(term1.identical(term2))
        self.assertTrue(term1.equal(term2))
        pass


    def test_statement_equal_1(self):
        term1 = Statement.Inheritance(Term("bird"), Term("animal"))
        term2 = Statement.Inheritance(Term("robin"), Term("animal"))
        self.assertFalse(term1.equal(term2))
        pass


    def test_statement_equal_2(self):
        term1 = Statement.Inheritance(Term("bird"), Term("animal"))
        term2 = Statement.Inheritance(Variable.Independent("x"), Term("animal"))
        self.assertTrue(term1.equal(term2))
        self.assertTrue(term2.equal(term1))
        pass


    def test_statement_equal_3(self):
        term1 = Statement.Inheritance(Variable.Independent("y"), Term("animal"))
        term2 = Statement.Inheritance(Variable.Independent("x"), Term("animal"))
        self.assertTrue(term1.equal(term2))
        self.assertTrue(term2.equal(term1))
        pass


    def test_statement_equal_4(self):
        term1 = Statement.Inheritance(Term("bird"), Variable.Independent("x"))
        term2 = Statement.Inheritance(Variable.Independent("x"), Term("animal"))
        self.assertTrue(term1.equal(term2))
        self.assertTrue(term2.equal(term1))
        pass


    def test_statement_equal_5(self):
        term1 = Statement.Inheritance(Variable.Independent("y"), Term("animal"))
        term2 = Statement.Inheritance(Variable.Dependent("x"), Term("animal"))
        self.assertFalse(term1.equal(term2))
        self.assertFalse(term2.equal(term1))
        pass


    def test_statement_equal_6(self):
        term1 = Statement.Inheritance(Variable.Dependent("x"), Variable.Independent("y"))
        term2 = Statement.Inheritance(Variable.Dependent("a"), Variable.Independent("b"))
        self.assertTrue(term1.equal(term2))
        self.assertTrue(term2.equal(term1))
        pass


    def test_statement_equal_7(self):
        term1 = Statement.Inheritance(Variable.Independent("x"), Term("animal"))
        term2 = Statement.Inheritance(Compound.ExtensionalIntersection(Term("brid"), Term("flyer")), Term("animal"))
        self.assertTrue(term1.equal(term2))
        self.assertTrue(term2.equal(term1))
        pass


    def test_compound_equal_0(self):
        term1 = Narsese.parse('(&&, <A-->B>, <B-->C>).').term
        term2 = Narsese.parse('(&&, <B-->C>, <A-->B>).').term
        self.assertTrue(term1.identical(term2))
        self.assertTrue(term1.equal(term2))
        self.assertTrue(term2.equal(term1))
        pass


    def test_compound_equal_1(self):
        '''
        (&&, <#x-->A>, <B-->C>) and (&&, <B-->C>, <{A1}-->A>) are equal, thought not identical.
        '''
        term1 = Narsese.parse('(&&, <#x-->A>, <B-->C>).').term
        term2 = Narsese.parse('(&&, <B-->C>, <{A1}-->A>).').term
        self.assertFalse(term1.identical(term2))
        self.assertTrue(term1.equal(term2))
        self.assertTrue(term2.equal(term1))
        pass
    

    def test_compound_equal_2(self):
        term1 = Compound.Conjunction(Variable.Independent("x"), Term("animal"))
        term2 = Compound.Conjunction(Compound.ExtensionalIntersection(Term("brid"), Term("flyer")), Term("animal"))
        self.assertTrue(term1.equal(term2))
        self.assertTrue(term2.equal(term1))
        pass



if __name__ == '__main__':

    test_classes_to_run = [
        TEST_Term_Equal
    ]

    loader = unittest.TestLoader()

    suites = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites.append(suite)
        
    suites = unittest.TestSuite(suites)

    runner = unittest.TextTestRunner()
    results = runner.run(suites)
