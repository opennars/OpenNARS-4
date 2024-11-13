import unittest
from opennars.Narsese import Compound, Connector, Term, Variable

class TEST_Compound(unittest.TestCase):
    def setUp(self):
        pass

    def test__create(self):
        term1 = Compound(Connector.ExtensionalSet, Term("Ann"), Term("Bob"))
        self.assertTrue(str(term1) == "{Ann, Bob}" or str(term1) == "{Bob, Ann}")
        from ordered_set import OrderedSet
        self.assertTrue(isinstance(term1.components, OrderedSet))

        term2 = Compound(Connector.Product, Term("bird"), Term("tree"))
        self.assertTrue(str(term2) == "(*, bird, tree)")
        self.assertTrue(isinstance(term2.components, list))

        
    
    def test__equality(self):
        term1 = Compound(Connector.ExtensionalSet, Term("Ann"), Term("Bob"))
        term2 = Compound(Connector.ExtensionalSet, Term("Bob"), Term("Ann"))
        term3 = Compound(Connector.ExtensionalSet, Term("Ann"), Term("Carl"))
        self.assertTrue(term1 == term2)
        self.assertFalse(term1 == term3)
        self.assertTrue(term1 != term3)

    def test__get_component(self):
        term1 = Compound(Connector.ExtensionalSet, Term("Ann"), Term("Bob"))
        term2 = term1[0]
        self.assertTrue(term2 == Term("Ann") or term2 == Term("Bob"))
        term3 = Compound(Connector.Product, term1, Term("bird"))
        term4 = term3[0, 0]
        self.assertTrue(term4 == Term("Ann") or term4 == Term("Bob"))

    def test__clone(self):
        term1 = Compound(Connector.Product, Term("Ann"), Term("Bob"))
        term2 = term1.clone()
        self.assertTrue(term1 == term2)
        self.assertFalse(term1 is term2)
        self.assertTrue(term1[0])
    
    def test__deep_clone(self):
        term1 = Compound(Connector.Product, Term("Ann"), Term("Bob"))
        term2 = term1.deep_clone()
        self.assertTrue(term1 == term2)
        self.assertFalse(term1 is term2)
        self.assertTrue(term1[0] == term2[0])
        self.assertFalse(term1[0] is term2[0])
        pass

    def test__deep_clone_with_variables(self):
        term1 = Compound(Connector.Product, Term("Ann"), Term("Bob"), Variable.Independent("X"))
        self.assertTrue(term1.has_var)
        term2 = term1.deep_clone(False)
        term3 = term1.deep_clone(True)
        self.assertTrue(term1 == term2)
        self.assertFalse(term1 is term2)
        self.assertTrue(term1 == term3)
        self.assertFalse(term1 is term3)
        self.assertTrue(term1[0] == term2[0])
        self.assertFalse(term1[0] is term2[0])
        self.assertTrue(term1[0] == term3[0])
        self.assertFalse(term1[0] is term3[0])
        self.assertFalse(term1[2] is term2[2])
        self.assertFalse(term1[2] is term3[2])

    
    def test__counts_term_recursively(self):
        term1 = Compound(Connector.Product, Term("Ann"), Term("Bob"), Term("Bob"), Variable.Independent("X"))
        map = term1.count_term_recursively(False)
        self.assertTrue(len(map) == 3)
        self.assertTrue(map[Term("Ann")] == 1)
        self.assertTrue(map[Term("Bob")] == 2)

    def test__contains_all_components(self):
        term1 = Compound(Connector.Product, Term("Ann"), Term("Bob"), Term("Carl"), Variable.Independent("X"))
        term2 = Compound(Connector.Product, Term("Ann"), Term("Bob"))
        term3 = Compound(Connector.Product, Term("Ann"), Term("Doe"))
        term4 = Compound(Connector.Conjunction, term1, term2)
        self.assertTrue(term1.contains_all_components(term2))
        self.assertFalse(term1.contains_all_components(term3))
        self.assertTrue(term4.contains_all_components(term2))
        self.assertFalse(term4.contains_all_components(term3))
        