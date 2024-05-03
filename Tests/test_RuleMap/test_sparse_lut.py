from pynars.NARS.DataStructures._py.Link import LinkType
from pynars.NARS.RuleMap import Interface_SyllogisticRules, RuleMap
from pynars.Narsese import Budget
import unittest

from pynars.NARS.DataStructures import Bag, Task, Concept
from pynars.Narsese import Judgement, Term, Statement, Copula, Truth   

from sparse_lut import SparseLUT, Any
# from pynars.utils.tools import get_size
# from pynars.NARS.RuleMap.RuleMap import CommonId
from pynars.utils.SparseLUT.branch_list import Node

class TEST_SparseLUT(unittest.TestCase):
    
    def test_new_0(self):
        lut = SparseLUT((3, 3, 3))
        lut.add([0, Any, Any], "A")
        lut.add([Any, 0, 1], "B")
        lut.build(False)
        lut.blist.draw()
        pass
    
    def test_0_0(self):
        lut = SparseLUT((10, 20))
        lut[1, 1] = "foo"
        lut.build()
        self.assertEqual(lut[1, 1], ["foo"])
        self.assertEqual(lut[2, 2], None)
        pass

    def test_0_1(self):
        lut = SparseLUT((3, 3, 3))
        lut.add([0, Any, Any], "A")
        lut.add([Any, 0, 1], "B")
        lut.build(False)
        lut.draw()
        self.assertEqual(lut[0, 2, 2], ["A"])
        self.assertEqual(lut[2, 0 ,1], ["B"])
        self.assertEqual(lut[0, 0 ,1], ["A", "B"])
        pass

    def test_2(self):
        # TODO: the SparseLUT seems still improvable. This case shows why.
        #       [0, 0, ...] and [0, 1, ...] can share the rest part with [[1,2,None], 0, ...] and [[1,2,None], 1, ...] correspondingly.
        lut = SparseLUT((3, 3, 3, 3, 3))
        lut.add([Any, 0, Any, Any, Any], "A")
        lut.add([Any, 1, Any, Any, Any], "B")
        lut.add([0, 2, Any, Any, Any], "C")
        lut.build(False)
        lut.draw()
        pass

    def test_3(self):
        lut = SparseLUT((3, 3, 3, 4, 3, 3, 3))
        lut.add([[0,1,2],0,[0,1,2],[0,1,2],[0,1,2],[1],[0,1,2]], "A")
        lut.add([[0,1,2],0,[0,1,2],[0,1,2],[0,1,2],[0,1,2],[0,1,2]], "B")
        lut.add([[0,1,2],1,[0,1,2],[0,1,2],[0,1,2],[0,1,2],[0,1,2]], "C")
        # lut.add([0,2,[0,1,2],[0,1,2],[0,1,2],[0,1,2],[0,1,2]], "D")
        # lut.add([[1,2],0,[0,1,2],[1,3],[0,1,2],2,[0,1,2]], "E")
        lut.build(False)
        lut.draw()
        pass

    def test_4(self):
        lut = SparseLUT((3, 3, 3))
        lut.add([[0,1,2],[0,1],[0,1,2]], "A")
        lut.add([[0,1,2],[1,2],[0,1,2]], "B")
        lut.add([[0],[2],[0,1,2]], "C")
        lut.build(False)
        lut.draw()
        pass

    def test_6(self):
        lut = SparseLUT((3, 3))
        lut.add([[0,1,2],[0,1]], "A")
        lut.add([[0],[1,2]], "B")
        lut.build(False)
        lut.draw()
        pass

    def test_7(self):
        lut = SparseLUT((3,3,3))
        lut.add([[0,1,2],0,[0,1]], "A")
        lut.add([[0,1,2],1,[1,2]], "B")
        lut.add([[0,1,2],[0,1,2],[0,1,2]], "C")
        lut.build(False)
        lut.draw()
        pass


    def test_8(self):
        '''
        [[0,1,2],0,1,[0,1,2]]
        [[0,1,2],0,[0,1,2],[0,1,2]]
        [[0,1,2],1,[0,1,2],[0,1,2]]
        [0,2,[0,1,2],[0,1,2]]

        [[1,2],0,[0,2],[0,1,2]]
        '''
        lut = SparseLUT((3, 3, 3, 3))
        lut.add([[0,1,2],0,1,[0,1,2]], "A")
        lut.add([[0,1,2],0,[0,1,2],[0,1,2]], "B")
        lut.add([[0,1,2],1,[0,1,2],[0,1,2]], "C")
        lut.add([0,2,[0,1,2],[0,1,2]], "D")
        lut.add([[1,2],0,[0,2],[0,1,2]], "E")
        lut.build(False)
        lut.draw()
        pass


    def test_9(self):
        lut = SparseLUT((3, 3, 3))
        lut.add([[0,1,2], [0,1], [0,1,2]], "A")
        lut.add([0,[1], [0,1,2]], "B")
        # lut.add([[1,2],0,[0,2],[0,1,2]], "E")
        lut.build(False)
        lut.draw()
        pass

    def test_9_1(self):
        lut = SparseLUT((3, 3, 3, 3))
        lut.add([[0,1,2], [0,1], [0,1,2], [0,1,2]], "A")
        lut.add([0, 1, 0, [0,1,2]], "B")
        # lut.add([[1,2],0,[0,2],[0,1,2]], "E")
        lut.build(False)
        lut.draw()
        pass

    def test_9_2(self):
        lut = SparseLUT((3, 3, 3, 3))
        lut.add([[0,1,2], [0,1], [0,1,2], [0,1,2]], "A")
        lut.add([0, 1, 0, 0], "B")
        # lut.add([[1,2],0,[0,2],[0,1,2]], "E")
        lut.build(False)
        lut.draw()
        pass


    def test_10(self):
        lut = SparseLUT((3, 3, 3, 3, 3))
        lut.add([[0,1,2], 0, 0, 0, [0,1,2]], "A")
        lut.add([0, 0, 0, 0, 0], "B")
        lut.build(False)
        lut.draw()
        pass

    def test_11(self):
        lut = SparseLUT((3,))
        lut.add([[0,1]], "A")
        lut.add([[0,2]], "B")
        lut.build(False)
        lut.draw()
        pass

    def test_12(self):
        lut = SparseLUT((3, 3, 3, 3, 3))
        lut.add([[0,1,2], 0, 0, 0, [0,1,2]], "A")
        lut.add([0, 0, 0, 0, 0], "B")
        # lut.add([[1,2],0,[0,2],[0,1,2]], "E")
        lut.build(False)
        lut.draw()
        pass

    def test_13(self):
        lut = SparseLUT((3, 3, 3, 3, 3))
        lut.add([[0,1,2], [0,1], [0,1,2], [0,1,2], [0,1,2]], "A")
        lut.add([0, 1, [0,1,2], [0,1,2], [0,1,2]], "B")
        # lut.add([[1,2],0,[0,2],[0,1,2]], "E")
        lut.build(False)
        lut.draw()
        pass

    def test_14_0(self):
        lut = SparseLUT((3, 3, 3))
        lut.add([[0,1,2], [0,1,2], [0,1,2]], "A")
        lut.add([[0,1,2], [1,2], [0,1,2]], "B")
        lut.build(False)
        lut.draw()
        pass

    def test_14_1(self):
        lut = SparseLUT((3, 3, 3, 3))
        lut.add([[0,1,2], [0,1,2], [0,1,2], [0,1,2]], "A")
        lut.add([[0,1,2], [1,2], [1], [0,1,2]], "B")
        lut.build(False)
        lut.draw()
        pass
    
    def test_14_1_2(self):
        lut = SparseLUT((3, 3, 3))
        lut.add([[0,1,2], [0,1,2], [0,1,2]], "A")
        lut.add([[0,1,2], [1,2], [1]], "B")
        lut.build(False)
        lut.draw()
        pass

    def test_14_2(self):
        lut = SparseLUT((3, 3, 3, 3, 3, 3))
        lut.add([[0,1,2], [0,1,2], [0,1,2], [0,1,2], [0,1,2], [0,1,2]], "A")
        lut.add([[0,1,2], [1,2], [1], [1,2], [0,1,2], [0,1,2]], "B")
        lut.build(False)
        lut.draw()
        pass

    def test_15(self):
        lut = SparseLUT((3, 3, 3, 3, 3, 3))
        lut.add([[0,1,2], [0,1,2], [0,1,2], [0,1,2], [0,1,2], [0,1,2]], "A")
        lut.add([[0,1,2], [1,2], [0], [0,1,2], [0,1,2], [0,1,2]], "B")
        lut.build(False)
        lut.draw()
        pass

    def test_15_1(self):
        lut = SparseLUT((3, 3, 3, 3, 3, 3))
        lut.add([[0,1,2], [0,1,2], [0,1,2], [0,1,2], [0,1,2], [0,1,2]], "A")
        lut.add([[0,1,2], [1,2], [0], [0,1,2], [0,1,2], [0,1,2]], "B")
        lut.add([[0,1,2], [1,2], [1,2], [0,1,2], [0,1,2], [0,1,2]], "C")
        lut.build(False)
        lut.draw()
        pass

    def test_15_2(self):
        lut = SparseLUT((3, 3, 3, 3, 3, 3))
        lut.add([[0,1,2], [0,1,2], [0,1,2], [0,1,2], [0,1,2], [0,1,2]], "A")
        lut.add([[0,1,2], [1,2], [0], [0,1,2], [0,1,2], [0,1,2]], "B")
        lut.add([[0,1,2], [1,2], [1,2], [1,2], [0,1,2], [0,1,2]], "C")
        lut.build(False)
        lut.draw()
        pass

    def test_15_3(self):
        lut = SparseLUT((3, 3, 3, 3, 3))
        lut.add([[0,1,2], [0,1,2], [0,1,2], [0,1,2], [0,1,2]], "A")
        lut.add([[1,2], [0], [0,1,2], [0,1,2], [0,1,2]], "B")
        lut.add([[1,2], [1], [0,1,2], [0,1,2], [0,1,2]], "C")
        lut.build(False)
        lut.draw()
        pass


    # def test_complex_0(self):
    #     ''''''
    #     lut = SparseLUT([8, 8, 2, 2, 2, 2, 2, 2, 2, 12, 12, 2, 4, 15, 15, 4])
    #     lut.add((4, 4, [1, 0], None, None, None, None, None, None, 0, 0, 0, [2, 1], None, None, None), "foo")
    #     lut.build()

    # def test_complex_1(self):
    #     ''''''
    #     lut = SparseLUT([8, 8, 2, 2, 2, 2, 2, 2, 2, 12, 12, 2, 4, 15, 15, 4])
    #     lut.add((4, 4, 1, None, None, None, None, None, None, 0, 0, 0, 1, None, None, None), "foo1")
    #     lut.add((4, 4, 1, None, None, None, None, None, None, 0, 0, 0, 2, None, None, None), "foo2")
    #     lut.add((4, 4, 1, None, None, None, None, None, None, 0, 0, 0, 1, None, None, None), "foo3")
    #     lut.add((4, 4, 1, None, None, None, None, None, None, 0, 0, 0, 2, None, None, None), "foo4")
    #     lut.add((4, 4, 1, None, None, None, None, None, None, 0, 0, 0, 0, None, None, None), "foo5")
    #     lut.add((4, 4, 1, None, None, None, None, None, None, 0, 0, 0, 0, None, None, None), "foo6")
    #     lut.add((4, 4, 1, None, None, None, None, None, None, 0, 0, 0, 3, None, None, None), "foo7")
    #     lut.add((4, 4, 1, None, None, None, None, None, None, 0, 0, 0, 3, None, None, None), "foo8")
    #     lut.add((4, 4, 1, None, None, None, None, None, None, 0, 0, 1, None, None, None, None), "foo9")
    #     lut.add((4, 4, 1, None, None, None, None, None, None, 0, 0, 0, 0, None, None, [0]), "foo10")
    #     lut.add((4, 4, 1, None, None, None, None, None, None, 0, 0, 0, 0, None, None, [0]), "foo11")
    #     lut.add((4, 4, 1, None, None, None, None, None, None, 0, 0, 0, 3, None, None, [0]), "foo12")
    #     lut.add((4, 4, 1, None, None, None, None, None, None, 0, 0, 0, 3, None, None, [0]), "foo13")
    #     lut.add((4, 4, 1, None, None, None, 1,    0,    1,    0, 0, 0, 0, 5,    5,    [0]), "foo14")
    #     lut.add((4, 4, 1, None, None, None, 1, 1, 0, 0, 0, 0, 0, 5, 5, [0]), "foo15")
    #     lut.build(False)
    #     # lut.print(False)
    #     lut[(4, 4, 1, None, None, None, 1, 0, 1, 0, 0, 0, 0, 5, 5, 0)]
    #     lut[(4, 4, 1, None, None, None, 1, 1, 0, 0, 0, 0, 0, 5, 5, 0)]
    #     pass

    # def test_rulemap_0(self):
    #     rulemap = RuleMap_v2(False)

    #     indices1 = rulemap._add_rule(Interface_SyllogisticRules._syllogistic__deduction__0_1, 
    #         LinkType1 = LinkType.COMPOUND_STATEMENT, 
    #         LinkType2 = LinkType.COMPOUND_STATEMENT, 
    #         has_common_id = True,
    #         Copula1 = Copula.Inheritance,
    #         Copula2 = Copula.Inheritance,
    #         match_reverse = False,
    #         common_id = CommonId(0, 1)
    #     )

    #     indices2 = rulemap._add_rule(Interface_SyllogisticRules._syllogistic__deduction__1_0, 
    #         LinkType1 = LinkType.COMPOUND_STATEMENT, 
    #         LinkType2 = LinkType.COMPOUND_STATEMENT, 
    #         has_common_id = [True, False],
    #         Copula1 = Copula.Inheritance,
    #         Copula2 = Copula.Inheritance,
    #         match_reverse = False,
    #         common_id = [CommonId(1, 0), CommonId(0, 1)]
    #     )
    #     rulemap.build(False)
    #     rulemap.map.draw()
    #     pass


class TEST_SparseLUT_v3(unittest.TestCase):
    
    def test_node_0(self):
        node1 = Node({1,2,3})
        node2 = Node({4,5,6})
        node3 = Node({1,2,3})
        node1.append(node2)
        node3.append(node2)
        self.assertEqual(len(node2.last_nodes_list), 2)
        node2.remove_last(node1)
        self.assertEqual(len(node2.last_nodes_list), 0)
        pass

    def test_duplicate_shallow(self):
        node1 = Node({0,1,2})
        node1.append(Node({3}))

        Node({0,2}).append(node1)
        Node({1}).append(node1)
        node2 = node1.duplicate_shallow({1,2})
        node1.reset_index({0})

        self.assertEqual(node1.last_nodes_list, node2.last_nodes_list)
        self.assertEqual(node1.next_nodes_list, node2.next_nodes_list)
        pass


    def test_pop_identical(self):
        node1 = Node({1,2,3})
        node2 = Node({4,5,6})
        node3 = Node({1,2,3})
        node1.append(node2)
        node3.append(node2)
        node2.remove_last(node1, True)
        self.assertEqual(len(node2.last_nodes_list), 1)
        self.assertEqual(node2.last_nodes_list[0], node3)
        self.assertEqual(id(node2.last_nodes_list[0]), id(node3))
        node2.remove_last(node3, True)
        self.assertEqual(len(node2.last_nodes_list), 0)

        pass

if __name__ == '__main__':

    test_classes_to_run = [
        TEST_SparseLUT,
        # TEST_SparseLUT_v3,
    ]

    loader = unittest.TestLoader()

    suites = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites.append(suite)
        
    suites = unittest.TestSuite(suites)

    runner = unittest.TextTestRunner()
    results = runner.run(suites)
