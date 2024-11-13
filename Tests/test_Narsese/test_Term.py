import unittest
from opennars.Narsese import Term

class TEST_Term(unittest.TestCase):
    def setUp(self):
        pass

    def test_create(self):
        term1 = Term("robin")
        self.assertEqual(str(term1), "robin")
    
    def test_equality(self):
        term1 = Term("robin")
        term2 = Term("robin")
        term3 = Term("bird")
        self.assertEqual(str(term1), "robin")
        self.assertTrue(term1 == term2)
        self.assertFalse(term1 == term3)
        self.assertTrue(term1 != term3)
        terms = {}
        terms[term1] = "robin"
        terms[term2] = "robin"
        terms[term3] = "bird"
        self.assertEqual(len(terms), 2)

    def test_clone(self):
        term1 = Term("robin")
        term2 = term1.clone()
        self.assertTrue(term1 == term2)
        self.assertFalse(term1 is term2)
    
    def test_deep_clone(self):
        term1 = Term("robin")
        term2 = term1.deep_clone()
        self.assertTrue(term1 == term2)
        self.assertFalse(term1 is term2)
