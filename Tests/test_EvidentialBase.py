from pynars.Narsese import Budget
import unittest

from pynars.NARS.DataStructures import Bag, Task, Concept
from pynars.Narsese import Judgement, Term, Statement, Copula, Truth   

from pynars.Narsese import Base, Task

class TEST_Base(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName=methodName)

    def test_add_evidence_1(self):
        ''''''
        task1 = Task(Judgement(Statement(Term('robin'), Copula.Inheritance, Term('bird'))))
        task2 = Task(Judgement(Statement(Term('bird'), Copula.Inheritance, Term('animal'))))
        task3 = Task(Judgement(Statement(Term('robin'), Copula.Inheritance, Term('animal'))))
        base = Base()
        base.add(task1)
        base.add(task2)
        self.assertEqual(len(base), 2)
        base = Base((task1, task2, task3))
        self.assertEqual(len(base), 3)


    def test_overlap_1(self):
        ''''''
        task1 = Task(Judgement(Statement(Term('robin'), Copula.Inheritance, Term('bird'))))
        task2 = Task(Judgement(Statement(Term('bird'), Copula.Inheritance, Term('animal'))))
        task3 = Task(Judgement(Statement(Term('robin'), Copula.Inheritance, Term('animal'))))
        base1 = Base((task1, task2))
        base2 = Base((task2, task3))
        self.assertTrue(base1.is_overlaped(base2))
    
    def test_overlap_1(self):
        ''''''
        task1 = Task(Judgement(Statement(Term('robin'), Copula.Inheritance, Term('bird'))))
        task2 = Task(Judgement(Statement(Term('bird'), Copula.Inheritance, Term('animal'))))
        task3 = Task(Judgement(Statement(Term('robin'), Copula.Inheritance, Term('animal'))))
        base1 = Base((task1, task2))
        base2 = Base((task2, task3))
        self.assertFalse(base1==base2)
        
    def test_add_base_1(self):
        ''''''
        task1 = Task(Judgement(Statement(Term('robin'), Copula.Inheritance, Term('bird'))))
        task2 = Task(Judgement(Statement(Term('bird'), Copula.Inheritance, Term('animal'))))
        task3 = Task(Judgement(Statement(Term('robin'), Copula.Inheritance, Term('animal'))))
        base1 = Base((task1, task2))
        base2 = Base((task2, task3))
        base3 = base1 | base2
        self.assertEqual(len(base3), 3)
        self.assertEqual(len(base1), 2)
        self.assertEqual(len(base2), 2)
        base2 |= base1
        self.assertEqual(len(base1), 2)
        self.assertEqual(len(base2), 3)
        pass
        
    def test_hash_1(self):
        task1 = Task(Judgement(Statement(Term('robin'), Copula.Inheritance, Term('bird'))))
        task2 = Task(Judgement(Statement(Term('bird'), Copula.Inheritance, Term('animal'))))
        task3 = Task(Judgement(Statement(Term('robin'), Copula.Inheritance, Term('animal'))))
        base = Base((task1, task2))
        self.assertIsNone(base._hash)
        h1 = hash(base)
        self.assertIsNotNone(base._hash)
        base.add(task3)
        self.assertIsNone(base._hash)
        h2 = hash(base)
        self.assertIsNotNone(base._hash)
        self.assertNotEqual(h1, h2)
        pass

if __name__ == '__main__':
    unittest.main()
