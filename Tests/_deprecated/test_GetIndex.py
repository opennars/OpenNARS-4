import NARS
import unittest

from pynars.NARS.DataStructures import Bag, Task, Concept, Link
from pynars.Narsese import Judgement, Term, Statement, Copula, Truth, Connector

from pathlib import Path
import Narsese
from pynars.Narsese._py.Compound import Compound

from pynars.utils.Print import print_out, PrintType, print_filename

class TEST_Get_Index(unittest.TestCase):
    '''Examples files in `application`.'''

    def test_get_index_0(self):
        '''If term_component = A, term_compound = <<B-->A>--><A-->C>>, then the index = [[0,1], [1,0]].'''
        term_component = Term("A")
        term_compound = Statement(
            Statement(Term("B"), Copula.Inheritance, Term("A")),
            Copula.Inheritance,
            Statement(Term("A"), Copula.Inheritance, Term("C")),
        )
        indexes = Link.get_index(term_component, term_compound)
        self.assertEqual(len(indexes), 2)
        self.assertEqual(indexes[0], [0, 1])
        self.assertEqual(indexes[1], [1, 0])
        pass

    def test_get_index_1(self):
        '''If term_component = A, term_compound = <(&,B,A)-->(&,A,C)>, then the index = [[0,1], [1,0]].'''
        term_component = Term("A")
        term_compound = Statement(
            Compound(Connector.ExtensionalIntersection, Term("B"), Term("A")),
            Copula.Inheritance,
            Compound(Connector.ExtensionalIntersection, Term("A"), Term("C"))
        )
        indexes = Link.get_index(term_component, term_compound)
        self.assertEqual(len(indexes), 2)
        self.assertEqual(indexes[0], [0, 1])
        self.assertEqual(indexes[1], [1, 0])
        pass

    def test_get_index_2(self):
        '''If term_component = A, term_compound = <(&,<B-->A>,(|,A,B,C))-->(&,(|, <A-->C>, (&, C, <B--><B-->A>>)), C)>, then the index = [[0, 0, 1], [0, 1, 0], [1, 0, 0, 0], [1, 0, 1, 1, 1, 1]].'''
        term_component = Term("A")
        term_compound = Narsese.parser.parse("<(&,<B-->A>,(|,A,B,C))-->(&,(|, <A-->C>, (&, C, <B--><B-->A>>)), C)>.").term
        # term_compound = Statement(
        #     Compound(Connector.ExtensionalIntersection, Term("B"), Term("A")),
        #     Copula.Inheritence,
        #     Compound(Connector.ExtensionalIntersection, Term("A"), Term("C"))
        # )
        indexes = Link.get_index(term_component, term_compound)
        self.assertEqual(len(indexes), 4)
        self.assertEqual(indexes[0], [0, 0, 1])
        self.assertEqual(indexes[1], [0, 1, 0])
        self.assertEqual(indexes[2], [1, 0, 0, 0])
        self.assertEqual(indexes[3], [1, 0, 1, 1, 1, 1])
        pass

    def test_get_index_3(self):
        '''If term_component = <B-->A>, term_compound = <(&,<B-->A>,(|,A,B,C))-->(&,(|, <A-->C>, (&, C, <B--><B-->A>>)), C)>, then the index = [[0, 0], [1, 0, 1, 1, 1]].'''
        term_component = Narsese.parser.parse("<B-->A>.").term
        term_compound = Narsese.parser.parse("<(&,<B-->A>,(|,A,B,C))-->(&,(|, <A-->C>, (&, C, <B--><B-->A>>)), C)>.").term
        indexes = Link.get_index(term_component, term_compound)
        self.assertEqual(len(indexes), 2)
        self.assertEqual(indexes[0], [0, 0])
        self.assertEqual(indexes[1], [1, 0, 1, 1, 1])
        pass

    def test_get_index_5(self):
        '''If term_component = <A-->B>, term_compound = <A-->B>, then the index = [[]].'''
        term_component = Narsese.parser.parse("<A-->B>.").term
        term_compound = Narsese.parser.parse("<A-->B>.").term
        indexes = Link.get_index(term_component, term_compound)
        self.assertEqual(len(indexes), 1)
        self.assertEqual(indexes[0], [])
        pass
if __name__ == '__main__':

    test_classes_to_run = [
        TEST_Get_Index
    ]

    loader = unittest.TestLoader()

    suites = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites.append(suite)
        
    suites = unittest.TestSuite(suites)

    runner = unittest.TextTestRunner()
    results = runner.run(suites)
