from pynars import NARS
import unittest

from pynars.NARS.DataStructures import Bag, Task, Concept, Table
from pynars.Narsese import Judgement, Term, Statement, Copula, Truth   

from pathlib import Path
from pynars import Narsese
from pynars.Narsese import Compound, Connector

from pynars.NARS.RuleMap.RuleMap import extract_feature

class TEST_ExtractFeature(unittest.TestCase):

    def test_statement_statement_0(self):
        ''''''
        # <S-->P>, <P-->S>
        premise1 = Narsese.parse("<S-->P>.").term
        premise2 = Narsese.parse("<P-->S>.").term
        feature = extract_feature(premise1, premise2)
        self.assertTrue(feature.match_reverse)
        pass
        

    def test_statement_statement_1(self):
        ''''''
        # <M-->S>, <M-->P>
        premise1 = Narsese.parse("<M-->S>.").term
        premise2 = Narsese.parse("<M-->P>.").term
        feature = extract_feature(premise1, premise2)
        self.assertFalse(feature.match_reverse)
        self.assertTrue(feature.has_common_id)
        self.assertEqual(feature.common_id_task, 0)
        self.assertEqual(feature.common_id_belief, 0)

        # <M-->P>, <S-->M>
        premise1 = Narsese.parse("<M-->P>.").term
        premise2 = Narsese.parse("<S-->M>.").term
        feature = extract_feature(premise1, premise2)
        self.assertFalse(feature.match_reverse)
        self.assertTrue(feature.has_common_id)
        self.assertEqual(feature.common_id_task, 0)
        self.assertEqual(feature.common_id_belief, 1)

        # <S-->M>, <M-->P>
        premise1 = Narsese.parse("<S-->M>.").term
        premise2 = Narsese.parse("<M-->P>.").term
        feature = extract_feature(premise1, premise2)
        self.assertFalse(feature.match_reverse)
        self.assertTrue(feature.has_common_id)
        self.assertEqual(feature.common_id_task, 1)
        self.assertEqual(feature.common_id_belief, 0)

        # <S-->M>, <P-->M>
        premise1 = Narsese.parse("<S-->M>.").term
        premise2 = Narsese.parse("<P-->M>.").term
        feature = extract_feature(premise1, premise2)
        self.assertFalse(feature.match_reverse)
        self.assertTrue(feature.has_common_id)
        self.assertEqual(feature.common_id_task, 1)
        self.assertEqual(feature.common_id_belief, 1)

        pass


    def test_statement_statement_2(self):
        ''''''
        # <S-->P>, <P-->S>
        premise1 = Narsese.parse("<S-->P>.").term
        premise2 = Narsese.parse("<P-->S>.").term
        feature = extract_feature(premise1, premise2)
        self.assertTrue(feature.match_reverse)
        self.assertIsNone(feature.has_common_id)
        pass


        

if __name__ == '__main__':

    test_classes_to_run = [
        TEST_ExtractFeature
    ]

    loader = unittest.TestLoader()

    suites = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites.append(suite)
        
    suites = unittest.TestSuite(suites)

    runner = unittest.TextTestRunner()
    results = runner.run(suites)
