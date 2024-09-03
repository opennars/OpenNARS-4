from typing import Dict, List
import NARS
import unittest

from opennars.NARS.DataStructures import Bag, Task, Concept, Link
from opennars.NARS.DataStructures._py.Link import LinkType, TaskLink, TermLink
from opennars.NARS.DataStructures._py.Memory import Memory
from opennars.Narsese import Judgement, Term, Statement, Copula, Truth, Connector

from pathlib import Path
import Narsese
from opennars.Narsese import Compound, Budget

from opennars.utils.Print import print_out, PrintType, print_filename

class TEST_Get_Index(unittest.TestCase):
    '''Examples files in `application`.'''

    def test_get_index_0(self):
        '''If source = A, target = <<B-->A>--><A-->C>>, then the type = COMPOUND_STATEMENT, the index = [[0,1], [1,0]]; if source = <<B-->A>--><A-->C>>, target = A, then the type = COMPONENT_STATEMENT, the index = [[0,1], [1,0]];'''
        source = Concept(Term("A"), Budget(0.5, 0.5, 0.5)) 
        target = Narsese.parser.parse("<<B-->A>--><A-->C>>.")
        
        term_link = TermLink(source, target, None, True, index=Link.get_index(target.term, source.term)[0])
        self.assertEqual(term_link.type, LinkType.COMPOUND_STATEMENT)
        self.assertEqual(term_link.component_index, (0,1))

        term_link = TermLink(target, source, None, False, index= Link.get_index(target.term, source.term)[1])
        self.assertEqual(term_link.type, LinkType.COMPONENT_STATEMENT)
        self.assertEqual(term_link.component_index, (1,0))
        pass


class TEST_LinkType(unittest.TestCase):
    '''Examples files in `application`.'''

    def test_transform(self):
        memory = Memory(100, 100)
        # task = Narsese.parse("<(*,acid, base) --> reaction>. %1.00;0.90%")
        task = Narsese.parse("<(&&,<(*,x,worms) --> food>,<(*,x,tree) --> live>) ==> <x --> bird>>. %1.00;0.90%")
        memory.accept(task)
        x: Concept = memory.concepts.take_by_key(Term("x"))
        links: Dict[int, TaskLink] = x.task_links.item_lut.lut
        for link in links.values():
            if len(link.component_index) > 2:
                self.assertIs(link.type, LinkType.TRANSFORM)
            else:
                self.assertIs(link.type, LinkType.COMPOUND_CONDITION)

                
        pass

if __name__ == '__main__':

    test_classes_to_run = [
        TEST_Get_Index,
        TEST_LinkType
    ]

    loader = unittest.TestLoader()

    suites = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites.append(suite)
        
    suites = unittest.TestSuite(suites)

    runner = unittest.TextTestRunner()
    results = runner.run(suites)
