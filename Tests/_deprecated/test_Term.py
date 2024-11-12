import unittest


class TEST_Term(unittest.TestCase):
    def test_0(self):
        from opennars.Narsese import Term, parse
        t1 = parse("A.").term
        t2 = Term("B")
        print(t1)
        print(t2)
        pass

        

if __name__ == '__main__':

    test_classes_to_run = [
        TEST_Term
    ]

    loader = unittest.TestLoader()

    suites = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites.append(suite)
        
    suites = unittest.TestSuite(suites)

    runner = unittest.TextTestRunner()
    results = runner.run(suites)
