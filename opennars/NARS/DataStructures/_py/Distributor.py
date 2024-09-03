from functools import lru_cache

"""
A pseudo-random number generator, used in Bag
"""
class Distributor:
    @staticmethod
    @lru_cache(maxsize=None)
    def new(range_val):
        '''Factory method for creating new Distributors with caching to avoid repeated calculations'''
        return Distributor(range_val)

    """
    For any number N < range, there is N+1 copies of it in the array, distributed as evenly as possible
    """
    def __init__(self, range_val):
        self.capacity = (range_val * (range_val + 1)) // 2
        self.order = [-1] * self.capacity

        index = 0
        for rank in range(range_val, 0, -1):
            for time in range(rank):
                index = ((self.capacity // rank) + index) % self.capacity
                while self.order[index] >= 0:
                    index = (index + 1) % self.capacity
                self.order[index] = rank - 1

    def pick(self, index):
        return self.order[index]

    def next(self, index):
        return (index + 1) % self.capacity