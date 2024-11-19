import unittest
from opennars.Narsese import TemporalOrder

class TEST_Tense(unittest.TestCase):
    def setUp(self):
        pass

    def test__reverse(self):
        order1 = TemporalOrder.NONE
        order2 = TemporalOrder.FORWARD
        order3 = TemporalOrder.BACKWARD
        order4 = TemporalOrder.INVALID
        order5 = TemporalOrder.CONCURRENT
        self.assertTrue(order1 is -order4)
        self.assertTrue(order2 is -order3)
        self.assertTrue(order5 is -order5)
    
    