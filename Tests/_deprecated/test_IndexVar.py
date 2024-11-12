from opennars import NARS, Narsese
import unittest

from opennars.NARS.DataStructures import Bag, Task, Concept, Link
from opennars.Narsese import Judgement, Term, Statement, Copula, Truth, Connector

from pathlib import Path
from opennars.Narsese._py.Compound import Compound

from opennars.utils.Print import print_out, PrintType, print_filename

class TEST_IndexVar(unittest.TestCase):
    '''Examples files in `application`.'''

    def test_int_var(self):
        ''''''
        from opennars.utils.IndexVar import IndexVar, IntVar

        a = IntVar(2)
        b = IntVar(1)
        c = IntVar(0)
        a.connect(b)
        b.connect(c)
        print(a, b, c)
        a.propagate_down()
        print(a, b, c)
        c(0)
        c.propagate_up()
        print(a, b, c)
    
    def test_index_var_0(self):
        ''''''
        from opennars.utils.IndexVar import IndexVar, IntVar
        idxvar_0 = IndexVar()

        idxvar_1_0= IndexVar()
        idxvar_1_1= IndexVar()

        idxvar_2_0 = IndexVar()
        idxvar_2_1 = IndexVar()
        idxvar_2_2 = IndexVar()

        idxvar_2_0.add(0, [0])
        idxvar_2_1.add(0, [0])
        idxvar_2_2.add(0, [0])

        idxvar_1_0.add(0, [0])
        idxvar_1_0.add(0, [1])
        idxvar_1_0.add(1, [2])
        idxvar_1_1.add(0, [0])

        idxvar_0.add(0, [0])
        idxvar_0.add(0, [0])
        idxvar_0.add(1, [0])
        idxvar_0.add(1, [1])

        idxvar_0.connect(idxvar_1_0)
        idxvar_0.connect(idxvar_1_1)

        idxvar_1_0.connect(idxvar_2_0)
        idxvar_1_0.connect(idxvar_2_1)
        idxvar_1_0.connect(idxvar_2_2)

        pass


    def test_index_var_1(self):
        ''''''
        from opennars.utils.IndexVar import IndexVar, IntVar
        idxvar_0 = IndexVar()

        idxvar_1_0= IndexVar()
        idxvar_1_1= IndexVar()

        idxvar_2_0 = IndexVar()
        idxvar_2_1 = IndexVar()
        idxvar_2_2 = IndexVar()

        idxvar_2_0.add(0, [0])
        idxvar_2_1.add(0, [0])
        idxvar_2_2.add(0, [0])
        idxvar_1_1.add(0, [0])

        idxvar_1_0.connect(idxvar_2_0, True)
        idxvar_1_0.connect(idxvar_2_1, True)
        idxvar_1_0.connect(idxvar_2_2, True)

        idxvar_0.connect(idxvar_1_0, True)
        idxvar_0.connect(idxvar_1_1, True)
        for idx, num in zip(idxvar_0.indices, [0,0,1,1]):
            idx(num)
            

        pass


    def test_index_var_2(self):
        ''''''
        from opennars.utils.IndexVar import IndexVar, IntVar
        idxvar_0 = IndexVar()

        idxvar_1_0= IndexVar()
        idxvar_1_1= IndexVar()

        idxvar_2_0 = IndexVar()
        idxvar_2_1 = IndexVar()
        idxvar_2_2 = IndexVar()

        idxvar_2_0.add(0, [0])
        idxvar_2_1.add(0, [0])
        idxvar_2_2.add(0, [0])
        idxvar_1_1.add(0, [0])

        idxvar_1_0.connect(idxvar_2_0, True)
        idxvar_1_0.connect(idxvar_2_1, True)
        idxvar_1_0.connect(idxvar_2_2, True)

        idxvar_cloned = idxvar_1_0.clone()

        pass

    def test_index_var__add_0(self):
        ''''''
        from opennars.utils.IndexVar import IndexVar, IntVar
        idxvar_0 = IndexVar()

        idxvar_1_0= IndexVar()
        idxvar_1_1= IndexVar()

        idxvar_2_0 = IndexVar()
        idxvar_2_1 = IndexVar()
        idxvar_2_2 = IndexVar()

        idxvar_0.connect(idxvar_1_0, True)
        idxvar_0.connect(idxvar_1_1, True)

        idxvar_1_0.connect(idxvar_2_0, True)
        idxvar_1_0.connect(idxvar_2_1, True)
        idxvar_1_0.connect(idxvar_2_2, True)

        idxvar_2_0.add(0, [0])
        idxvar_2_1.add(0, [0])
        idxvar_2_2.add(0, [0])
        idxvar_1_1.add(0, [0])

        idxvar_0.rebuild()

        for idx, num in zip(idxvar_0.indices, [0,0,1,1]):
            idx(num)
            
        

    def test_index_var__add_1(self):
        ''''''
        from opennars.utils.IndexVar import IndexVar, IntVar
        '''<(&&, <E-->A>, <E-->B>, <$y-->C>)==><$y-->D>>'''
        idxvar_0 = IndexVar()

        idxvar_1_0= IndexVar()
        idxvar_1_1= IndexVar()
        idxvar_0.connect(idxvar_1_0)
        idxvar_0.connect(idxvar_1_1)

        idxvar_2_0 = IndexVar()
        idxvar_2_1 = IndexVar()
        idxvar_2_2 = IndexVar()
        idxvar_1_0.connect(idxvar_2_0)
        idxvar_1_0.connect(idxvar_2_1)
        idxvar_1_0.connect(idxvar_2_2)
        idxvar_2_3 = IndexVar()
        idxvar_2_4 = IndexVar()
        idxvar_1_1.connect(idxvar_2_3)
        idxvar_1_1.connect(idxvar_2_4)
        idxvar_2_3.add(0, [])

        idxvar_3_0 = IndexVar()
        idxvar_3_1 = IndexVar()
        idxvar_3_2 = IndexVar()
        idxvar_3_3 = IndexVar()
        idxvar_3_4 = IndexVar()
        idxvar_3_5 = IndexVar()
        idxvar_2_0.connect(idxvar_3_0)
        idxvar_2_0.connect(idxvar_3_1)
        idxvar_2_1.connect(idxvar_3_2)
        idxvar_2_1.connect(idxvar_3_3)
        idxvar_2_2.connect(idxvar_3_4)
        idxvar_2_2.connect(idxvar_3_5)

        idxvar_3_4.add(0, [])

        idxvar_0.rebuild()

        '''<(&&, <#x-->A>, <#x-->B>, <$y-->C>)==><$y-->D>>'''
        idxvar_0.add(1, [0,0,0])
        idxvar_3_2.add(1, [])
        idxvar_0.rebuild()
        pass


    def test_index_var__remove(self):
        ''''''
        from opennars.utils.IndexVar import IndexVar, IntVar
        '''<(&&, <#x-->A>, <#x-->B>, <$y-->C>)==><$y-->D>>'''
        idxvar_0 = IndexVar()

        idxvar_1_0= IndexVar()
        idxvar_1_1= IndexVar()
        idxvar_0.connect(idxvar_1_0)
        idxvar_0.connect(idxvar_1_1)

        idxvar_2_0 = IndexVar()
        idxvar_2_1 = IndexVar()
        idxvar_2_2 = IndexVar()
        idxvar_1_0.connect(idxvar_2_0)
        idxvar_1_0.connect(idxvar_2_1)
        idxvar_1_0.connect(idxvar_2_2)
        idxvar_2_3 = IndexVar()
        idxvar_2_4 = IndexVar()
        idxvar_1_1.connect(idxvar_2_3)
        idxvar_1_1.connect(idxvar_2_4)
        idxvar_2_3.add(0, [])

        idxvar_3_0 = IndexVar()
        idxvar_3_1 = IndexVar()
        idxvar_3_2 = IndexVar()
        idxvar_3_3 = IndexVar()
        idxvar_3_4 = IndexVar()
        idxvar_3_5 = IndexVar()
        idxvar_2_0.connect(idxvar_3_0)
        idxvar_2_0.connect(idxvar_3_1)
        idxvar_2_1.connect(idxvar_3_2)
        idxvar_2_1.connect(idxvar_3_3)
        idxvar_2_2.connect(idxvar_3_4)
        idxvar_2_2.connect(idxvar_3_5)

        idxvar_3_4.add(0, [])
        idxvar_3_0.add(1, [])
        idxvar_3_2.add(1, [])

        idxvar_0.rebuild()
        '''<(&&, <E-->A>, <E-->B>, <$y-->C>)==><$y-->D>>'''
        idxvar_0.remove([0,0,0])
        idxvar_3_2.remove([])
        idxvar_0.rebuild()
        # idxvar_0.rebuild()
        pass



if __name__ == '__main__':

    test_classes_to_run = [
        TEST_IndexVar
    ]

    loader = unittest.TestLoader()

    suites = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites.append(suite)
        
    suites = unittest.TestSuite(suites)

    runner = unittest.TextTestRunner()
    results = runner.run(suites)
