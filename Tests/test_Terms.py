import unittest


class TEST_Terms(unittest.TestCase):
    def test_0(self):
        from pynars.Narsese import Term, Terms
        terms = Terms((Term("A"), Term("B"), Term("C")), False) 
        pass

    def test_1(self):
        from pynars.Narsese import Term, Terms, Statement, Variable
        stat1 = Statement.Inheritance(Variable.Independent("x", idx=0), Term("A"))
        repr(stat1)
        stat2 = Statement.Inheritance(Variable.Independent("x", idx=0), Term("B"))
        stat3 = Statement.Inheritance(Variable.Independent("y", idx=1), Term("C"))
        stat4 = Statement.Inheritance(Variable.Independent("y", idx=1), Term("D"))
        terms = Terms((Term("E"), stat1, stat2, stat3, stat4, Term("F")), False) 
        pass

    def test_2(self):
        from pynars.Narsese import Term, Terms, Statement, Variable
        stat1 = Statement.Inheritance(Variable.Independent("x", idx=0), Term("A"))
        repr(stat1)
        stat2 = Statement.Inheritance(Variable.Independent("x", idx=0), Term("B"))
        stat3 = Statement.Inheritance(Variable.Independent("y", idx=1), Term("C"))
        stat4 = Statement.Inheritance(Variable.Independent("y", idx=1), Term("D"))
        terms = Terms((Term("E"), stat1, stat2, stat3, stat4, Term("F")), True) 
        pass

    def test_3(self):
        from pynars.Narsese import Term, Terms, Statement, Variable
        stat1 = Statement.Inheritance(Variable.Independent("x", idx=0), Term("A"))
        repr(stat1)
        stat2 = Statement.Inheritance(Variable.Independent("x", idx=0), Term("B"))
        stat3 = Statement.Inheritance(Variable.Independent("y", idx=0), Term("A"))
        stat4 = Statement.Inheritance(Variable.Independent("y", idx=0), Term("C"))
        terms1 = Terms((Term("D"), stat1, stat2, Term("E")), True)
        terms2 = Terms((Term("D"), stat3, stat4, Term("F")), True) 
        terms3 = Terms.intersection(terms1, terms2)
        pass

    def test_4(self):
        from pynars.Narsese import Term, Terms, Statement, Variable
        stat1 = Statement.Inheritance(Variable.Independent("x", idx=0), Term("A"))
        repr(stat1)
        stat2 = Statement.Inheritance(Variable.Independent("x", idx=0), Term("B"))
        stat3 = Statement.Inheritance(Variable.Independent("y", idx=0), Term("A"))
        stat4 = Statement.Inheritance(Variable.Independent("y", idx=0), Term("C"))
        terms1 = Terms((Term("D"), stat1, stat2, Term("E")), True)
        terms2 = Terms((Term("D"), stat3, stat4, Term("F")), True) 
        terms3 = Terms.union(terms1, terms2)
        pass
        

if __name__ == '__main__':

    test_classes_to_run = [
        TEST_Terms
    ]

    loader = unittest.TestLoader()

    suites = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites.append(suite)
        
    suites = unittest.TestSuite(suites)

    runner = unittest.TextTestRunner()
    results = runner.run(suites)
