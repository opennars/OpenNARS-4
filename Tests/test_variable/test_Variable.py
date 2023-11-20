from pynars import Narsese, NARS
import unittest

from pynars.NARS.DataStructures import Bag, Task, Concept, Table
from pynars.Narsese import Judgement, Term, Statement, Copula, Truth   

from pathlib import Path
from pynars.Narsese import Compound, Connector
from pynars.NAL.MetaLevelInference.VariableSubstitution import *
from pynars.Narsese._py.Variable import VarPrefix, Variable
from pynars.utils.IndexVar import IndexVar

class TEST_Variable(unittest.TestCase):

    def test_craete_var(self):
        ''''''
        var1 = Variable(VarPrefix.Independent, "x", 0)
        var2 = Variable.Dependent("x", 0)
        print(var1)
        print(var2)

    def test_index_var_0(self):
        ''''''
        index1 = IndexVar()
        index1.indices = [0, 1]
        index2 = IndexVar()
        index2.indices = [1, 0]
        self.assertEqual(index1, index2)
        pass

    def test_index_var_1(self):
        ''''''
        index1 = IndexVar()
        index1.indices = [0, 1, 0]
        index2 = IndexVar()
        index2.indices = [0, 1, 1]
        self.assertNotEqual(index1, index2)
        pass

    def test_index_var_2(self):
        ''''''
        term1 = Narsese.parse("<#x-->bird>.").term
        self.assertEqual(term1._vars_dependent.positions, [[0]])
        term2 = Narsese.parse("<bird-->#x>.").term
        self.assertEqual(term2._vars_dependent.positions, [[1]])
        term = Narsese.parse("<<$x-->bird> ==> <$x-->animal>>.").term
        self.assertEqual(term._vars_independent.positions, [[0,0], [1,0]])
        term = Narsese.parse("<<animal-->$x> ==> <bird-->$x>>.").term
        self.assertEqual(term._vars_independent.positions, [[0,1], [1,1]])
        pass


    def test_index_var_3(self):
        ''''''
        term = Narsese.parse("<<animal-->$x> ==> <bird-->$x>>.").term
        self.assertEqual(term._vars_independent.indices, [0, 0])

        term = Narsese.parse("(&&, <$x-->A>, <#y-->B>, <<$z-->C>==><$x-->A>>).").term
        self.assertEqual(term._vars_independent.indices, [0, 2, 0])
        self.assertEqual(term._vars_dependent.indices, [1])

        term = Narsese.parse("(&&, <$x-->A>, <#y-->B>, <$z==><$x-->A>>).").term
        # self.assertEqual(term.index_var.indices, [0, 2, 0])
        pass


    def test_index_var_4(self):
        ''''''
        term1 = Narsese.parse("(&&,<#y --> key>,<$x --> (/,open,#y,_)>).").term
        self.assertEqual(term1._vars_dependent.positions, [[0,0],[1,1,1]])
        self.assertEqual(term1._vars_independent.positions, [[1,0]])
        pass


    def test_unification_0(self):
        ''''''
        stat1: Statement = Narsese.parse("<<$x-->A>==><<$y-->B>==><$x-->C>>>.").term
        stat2: Statement = Narsese.parse("<<<$x-->B>==><$y-->C>>==><$x-->D>>.").term
        
        self.assertEqual(stat1.predicate, stat2.subject)
        stat1[1,0]
        subst = get_substitution__var_var(stat1, stat2, [1], [0])
        stat3 = subst.apply()
        stat4 = Statement.Implication(stat3[0], stat2[1])
        stat5 = Narsese.parse("<<$1-->A>==><$0-->D>>.").term
        self.assertTrue(stat4.identical(stat5))
        # R = unification(stat1, stat2, stat1.predicate, stat2.subject)

        pass

    
    def test_unification_1(self):
        '''
        (&&, <#x-->A>, <B-->C>) and (&&, <B-->C>, <{A1}-->A>) are equal, thought not identical.
        '''
        term1 = Narsese.parse('(&&, <#x-->A>, <B-->C>).').term
        term2 = Narsese.parse('(&&, <B-->C>, <{A1}-->A>).').term
        self.assertFalse(term1.identical(term2))
        self.assertTrue(term1.equal(term2))
        pass

    def test_unification_2(self):
        term1: Statement = Narsese.parse("<<$x-->A> ==> <$x-->B>>.").term
        term2 = Narsese.parse("<(&&, <#x-->C>, <#x-->D>)-->A>.").term
        self.assertTrue(term1.subject.equal(term2))
        self.assertTrue(term2.equal(term1.subject))
        # 1. to find the substitution
        term1.subject.equal(term2)
        term1[0,0]
        term1[0]

        term3 = Narsese.parse("<<(&&, <#x-->C>, <#x-->D>)-->A> ==> <(&&, <#x-->C>, <#x-->D>)-->B>>.").term
        pass

    def test_unification_3(self):
        '''
        'Multiple variable elimination

        'Every lock can be opened by some key.
        <<$x --> lock> ==> (&&,<#y --> key>,<$x --> (/,open,#y,_)>)>. %1.00;0.90%

        'Lock-1 is a lock.
        <{lock1} --> lock>. %1.00;0.90%

        9

        'Some key can open Lock-1.
        ''outputMustContain('(&&,<#1 --> key>,<{lock1} --> (/,open,#1,_)>). %1.00;0.81%')
        '''
        premise1 = Narsese.parse('<<$x --> lock> ==> (&&,<#y --> key>,<$x --> (/,open,#y,_)>)>. %1.00;0.90%').term
        premise2 = Narsese.parse('<{lock1} --> lock>. %1.00;0.90%').term
        

        pass


    def test_index_repr_0(self):
        ''''''
        term = Narsese.parse("<$x-->bird>.").term
        self.assertEqual(repr(term), "<Statement: <$0-->bird>>")

        pass

    def test_index_repr_1(self):
        ''''''
        term = Narsese.parse("<<animal-->$x>==><bird-->$y>>.").term
        self.assertEqual(repr(term), "<Statement: <<animal-->$0>==><bird-->$1>>>")

        pass

    def test_eq_0(self):
        '''
        (&&, <$1-->A>, <$2-->B>)
        (&&, <$1-->A>, <$1-->B>)
        the two should be unequal.
        '''
        compound1 = Compound(Connector.Conjunction, Statement(Variable(VarPrefix.Independent, "x", 0), Copula.Inheritance, Term("A")), Statement(Variable(VarPrefix.Independent, "y", 1), Copula.Inheritance, Term("B")))
        compound2 = Compound(Connector.Conjunction, Statement(Variable(VarPrefix.Independent, "x", 0), Copula.Inheritance, Term("A")), Statement(Variable(VarPrefix.Independent, "x", 0), Copula.Inheritance, Term("B")))
        self.assertNotEqual(compound1, compound2)
        self.assertTrue(compound1[1].identical(compound2[1]))
        pass


    

    # def test_eq_1(self):
    #     '''
    #     stat1 = (&&, <$1-->A>, <<$2-->B>==><$1-->C>>)
    #     stat2 = <<<$1-->B>==><$2-->C>> ==> <$2-->D>>
    #     |-
    #     stat3 = (&&, <$1-->A>, <$1-->D>>)

    #     stat1[1] == stat2[1]
    #     stat1 and stat2 should derive stat3
    #     '''
    #     pass

    
    # def test_eq_2(self):
    #     '''
    #     stat1 = <(&&, <$1-->A>, <$2-->B>) ==> <$3-->C>>
    #     stat2 = <<$1-->B>==><$2-->D>>
    #     |-
    #     stat3 = <(&&, <$1-->A>, <$2-->D>) ==> <$3-->C>>

    #     stat1[0][1] == stat2[0]
    #     stat1 and stat2 should derive stat3
    #     '''
    #     pass
        
    # def test_eq_3(self):
    #     '''
    #     stat1: (&&, <$1-->A>, <$2-->B>)
    #     stat2: (&&, <$1-->A>, <#2-->B>)
    #     stat1 != stat2
    #     '''
    
    # def test_eq_4(self):
    #     '''
    #     stat1 = (&&, <$1-->A>, <<$2-->B>==><#1-->C>>)
    #     stat2 = <<<$1-->B>==><#2-->C>> ==> <$2-->D>>
    #     |=
    #     stat3 = (&&, <$1-->A>, <$1-->D>>)

    #     stat1[1] == stat2[0]
    #     stat1 and stat2 should derive stat3
    #     '''
        
    #     pass

    # def test_eq_5(self):
    #     '''
    #     stat1 = (&&, <$1-->A>, <<$2-->B>==>(&&, <#1-->C>, <$1-->D>)>)
    #     stat2 = <<<$1-->B>==>(&&, <#2-->C>, <$2-->D>)> ==> <$2-->E>>
    #     |=
    #     stat3 = (&&, <$1-->A>, <$1-->E>>)

    #     stat1[1] == stat2[1]
    #     stat1 and stat2 should derive stat3
    #     '''
    #     pass

    # def test_eq_6(self):
    #     '''
    #     stat1 = (&&, <$1-->A>, <<$2-->B>==>(&&, <#1-->C>, <$1-->D>)>)
    #     stat2 = <<<$1-->B>==>(&&, <#1-->C>, <$2-->D>)> ==> <$2-->E>>

    #     stat1[1] != stat2[1]
    #     '''
    #     pass


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
