import NARS
import unittest

from pynars.NARS.DataStructures import Bag, Task, Concept, Table
from pynars.Narsese import Judgement, Term, Statement, Copula, Truth   

from pathlib import Path
import Narsese
from pynars.Narsese import Compound, Connector
from pynars.NAL.MetaLevelInference.VariableSubstitution import *

class TEST_Substitution(unittest.TestCase):

    def test_compound(self):
        ''''''
        compound = Compound(Connector.Conjunction, Term("A"), Term("B"), Term("C"))
        term_new = Compound(Connector.Conjunction, Term("D"), Term("B"), Term("C"))
        term_substitution = substitution(compound, Term("A"), Term("D"))
        self.assertEqual(term_substitution, term_new)
        pass
        
    def test_statement(self):
        ''''''
        statement = Statement(Term("A"), Copula.Inheritance, Term("B"))
        term_new = Statement(Term("C"), Copula.Inheritance, Term("B"))
        term_substitution = substitution(statement, Term("A"), Term("C"))
        self.assertEqual(term_substitution, term_new)
        pass
        
    def test_term(self):
        ''''''
        term = Term("A")
        term_new = Term("B")
        term_substitution = substitution(term, Term("A"), Term("B"))
        self.assertEqual(term_substitution, term_new)

        term = Term("A")
        term_new = Term("A")
        term_substitution = substitution(term, Term("B"), Term("B"))
        self.assertEqual(term_substitution, term_new)
        pass
        
    def test_complex(self):
        ''''''
        statement1 = Statement(Term("A"), Copula.Inheritance, Term("B"))
        statement2 = Statement(Term("A"), Copula.Inheritance, Term("C"))
        compound = Compound(Connector.Conjunction, statement1, statement2)
        statement1 = Statement(Term("D"), Copula.Inheritance, Term("B"))
        statement2 = Statement(Term("D"), Copula.Inheritance, Term("C"))
        term_new = Compound(Connector.Conjunction, statement1, statement2)
        term_substitution = substitution(compound, Term("A"), Term("D"))
        self.assertEqual(term_substitution, term_new)
        pass


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
