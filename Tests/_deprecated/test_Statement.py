import unittest


class TEST_Statement(unittest.TestCase):
    def test_0(self):
        from pynars.Narsese import Statement, Term, Copula
        stat = Statement(Term("robin"), Copula.Inheritance, Term("bird"))
        pass
    
    def test_1(self):
        from pynars.Narsese import Statement, Term, Copula
        from pynars import Narsese
        stat = Narsese.parse("<robin-->bird>.").term
        pass

    def test_2(self):
        from pynars.Narsese import Statement, Term, Copula
        from pynars import Narsese
        stat = Narsese.parse("<$x-->$y>.").term
        repr(stat)
        pass

    def test_3(self):
        from pynars.Narsese import Statement, Term, Copula
        from pynars import Narsese
        stat = Narsese.parse("<<$x-->A> ==> <$x-->B>>.").term
        repr(stat)
        pass

if __name__ == '__main__':

    test_classes_to_run = [
        TEST_Statement
    ]

    loader = unittest.TestLoader()

    suites = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites.append(suite)
        
    suites = unittest.TestSuite(suites)

    runner = unittest.TextTestRunner()
    results = runner.run(suites)
