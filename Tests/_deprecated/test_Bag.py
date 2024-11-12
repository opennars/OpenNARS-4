from pynars.Narsese import Budget
import unittest

from pynars.NARS.DataStructures import Bag, Task, Concept
from pynars.Narsese import Judgement, Term, Statement, Copula, Truth   

import matplotlib.pyplot as plt

class TEST_Bag(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName=methodName)

    def test_bag_put_task(self):
        ''''''
        bag = Bag(1000, 100)
        task = Task(Judgement(Statement(Term('robin'), Copula.Inheritance, Term('bird'))))
        self.assertEqual(len(bag), bag.count())
        self.assertEqual(len(bag), 0)
        bag.put(task)
        self.assertIn(task, bag)
        self.assertEqual(len(bag), bag.count())
        self.assertEqual(len(bag), 1)
        pass

    def test_bag_put_task_merge(self):
        bag = Bag(1000, 100)
        task = Task(Judgement(Statement(Term('robin'), Copula.Inheritance, Term('bird'))), Budget(0.5, 0.5, 0.5))
        self.assertEqual(len(bag), bag.count())
        self.assertEqual(len(bag), 0)
        bag.put(task)
        self.assertIn(task, bag)
        self.assertEqual(len(bag), bag.count())
        self.assertEqual(len(bag), 1)
        task = Task(Judgement(Statement(Term('robin'), Copula.Inheritance, Term('bird'))), Budget(1.0, 1.0, 1.0))
        bag.put(task)
        self.assertIn(task, bag)
        self.assertEqual(len(bag), bag.count())
        self.assertEqual(len(bag), 1)
        task = bag.take_by_key(task, False)
        self.assertEqual(task.budget.priority, 1.0)
        self.assertEqual(task.budget.durability, 1.0)
        self.assertEqual(task.budget.quality, 1.0)
        task = Task(Judgement(Statement(Term('robin'), Copula.Inheritance, Term('bird'))), Budget(0.9, 0.9, 0.9))        
        # bag.put(task, merge=False)
        # self.assertIn(task, bag)
        # self.assertEqual(len(bag), bag.count())
        # self.assertEqual(len(bag), 1)
        # task = bag.take_by_key(task, False)
        # self.assertEqual(task.budget.priority, 0.9)
        # self.assertEqual(task.budget.durability, 0.9)
        # self.assertEqual(task.budget.quality, 0.9)
        pass
    def test_bag_take_task_by_key(self):
        ''''''
        bag = Bag(1000, 100)
        task1 = Task(Judgement(Statement(Term('robin'), Copula.Inheritance, Term('bird'))))
        task2 = Task(Judgement(Statement(Term('bird'), Copula.Inheritance, Term('animal'))))
        self.assertEqual(len(bag), bag.count())
        bag.put(task1)
        self.assertEqual(len(bag), bag.count())
        task = bag.take_by_key(task2, remove=False)
        self.assertIsNone(task)
        task = bag.take_by_key(task2, remove=True)
        self.assertIsNone(task)
        self.assertEqual(len(bag), 1)
        task = bag.take_by_key(task1, remove=False)
        self.assertEqual(len(bag), 1)
        self.assertIsNotNone(task)
        task = bag.take_by_key(task1, remove=True)
        self.assertEqual(len(bag), bag.count())
        self.assertEqual(len(bag), 0)
        self.assertIsNotNone(task)
        pass

    def test_bag_take_task(self):
        '''take a task using the priority'''
        bag = Bag(1000, 100)
        task1 = Task(Judgement(Statement(Term('robin'), Copula.Inheritance, Term('bird'))), Budget(0.9, 0.5, 0.5))
        task2 = Task(Judgement(Statement(Term('bird'), Copula.Inheritance, Term('animal'))), Budget(0.5, 0.6, 0.6))
        bag.put(task1)
        bag.put(task2)
        self.assertEqual(len(bag), bag.count())
        self.assertEqual(len(bag), 2)

        cnt1 = 0
        cnt2 = 0
        for _ in range(10000):
            task = bag.take(remove=False)
            if task == task1: 
                cnt1 += 1
            elif task == task2: 
                cnt2 += 1
        self.assertGreater(cnt1, cnt2)

        bag.take_by_key(task1)
        bag.take_by_key(task2)
        self.assertEqual(len(bag), 0)
        for i in range(0, 100):
            p = i/100
            task = Task(Judgement(Statement(Term(f'robin_{i}'), Copula.Inheritance, Term('bird'))), Budget(p, 0.5, 0.5))
            bag.put(task)
        
        self.assertEqual(len(bag), 100)
        import numpy as np
        cnt = np.array([0 for _ in range(100)])
        from tqdm import tqdm
        n = 10000
        for _ in tqdm(range(n)):
            task = bag.take(remove=False)
            idx = bag.map_priority(task.budget.priority)
            cnt[idx] += 1
        # self.assertTrue(cnt[-1]/cnt[-3] > 2)
        plt.figure(1)
        plt.bar(list(range(len(cnt))), cnt)
        plt.title(f'n={n}')
        plt.savefig(f'./Tests/test_Bag_take_{n}')
        n = 1000000
        for _ in tqdm(range(n)):
            task = bag.take(remove=False)
            idx = bag.map_priority(task.budget.priority)
            cnt[idx] += 1
        plt.figure(2)
        plt.bar(list(range(len(cnt))), cnt)
        plt.title(f'n={n}')
        plt.savefig(f'./Tests/test_Bag_take_{n}')
        plt.show()



if __name__ == '__main__':
    unittest.main()


