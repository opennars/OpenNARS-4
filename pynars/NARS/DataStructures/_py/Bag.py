from collections import OrderedDict
import random
import math
from depq import DEPQ
from pynars.Config import Config
from pynars.Narsese import Item, Task
from pynars.NAL.Functions.BudgetFunctions import *
from typing import Union, Callable, Any
from .Distributor import Distributor


class Bag:
    # TODO: Re-implement this DataStructure, in order to optimize the complexity.
    class LUT:
        def __init__(self, key=None, *args, **kwargs):
            self.lut = OrderedDict(*args, **kwargs)
            self.key = key

        def get(self, key, default = None):
            if self.key is not None: key = self.key(key)
            return self.lut.get(hash(key), default)

        def pop(self, key, default = None):
            if self.key is not None: key = self.key(key)
            return self.lut.pop(hash(key), default)

        def __getitem__(self, k):
            if self.key is not None: k = self.key(k)
            return self.lut.__getitem__(hash(k))

        def __setitem__(self, k, v):
            if self.key is not None: k = self.key(k)
            return self.lut.__setitem__(hash(k), v)

        def __contains__(self, o: object) -> bool:
            return self.lut.__contains__(hash(o))

        def __len__(self):
            return len(self.lut)
        
        def clear(self):
            self.lut.clear()


    def __init__(self, capacity: int, n_buckets: int = None, take_in_order: bool = True, key: Callable[[Item], Any]=None) -> None:
        '''
        Args:
            capacity (int): the maximum number of items.
            n_buckets (int): the number of buckets.
            take_in_order (bool): if True, an item is taken out in order within a bucket, otherwise a random item is taken out.
        '''
        self.capacity = capacity
        self.take_in_order = take_in_order
        self.item_lut = self.LUT(key=key)  # look up table
        self.n_levels = n_buckets if n_buckets is not None else Config.num_buckets
        self.pointer = self.n_levels - 1  # Pointing to the Bag's current bucket number

        self.distributor = Distributor.new(self.n_levels)
        
        self.levels = tuple(list() for i in range(self.n_levels))  # initialize buckets between 0 and capacity

        self.current_counter = 0
        self.level_index = capacity % self.n_levels

        # self.buckets = self.Depq(maxlen=self.n_buckets)
        n_digits = int(math.log10(self.n_levels)) + 3

        def map_priority(priority: float):
            idx = int(round(priority * self.n_levels, n_digits))
            return idx if idx < self.n_levels else self.n_levels - 1

        self.map_priority = map_priority
        self.busyness = 0.5

    def take(self, remove = True) -> Item:
        if len(self) == 0: return None
        if self._is_current_level_empty() or self.current_counter == 0:
            self.pointer = self.distributor.pick(self.level_index)
            self.level_index = self.distributor.next(self.level_index)
            while self._is_current_level_empty():
                self.pointer = self.distributor.pick(self.level_index)
                self.level_index = self.distributor.next(self.level_index)

        if self.take_in_order:
            # take the first item from the current bucket
            idx = 0
        else:
            # take an item randomly from the current bucket
            rnd = random.random()
            cnt = len(self.levels[self.pointer])
            idx = int(rnd * cnt)

        if remove:
            bucket: list = self.levels[self.pointer]
            item = bucket.pop(idx)
            self.item_lut.pop(item)
        else:
            item = self.levels[self.pointer][idx]

        self.current_counter = idx

        return item

    def take_by_key(self, key, remove = True) -> Union[Item, None]:
        if remove:
            item: Item = self.item_lut.pop(key)
            if item is not None:
                bucket = self.levels[self.map_priority(item.budget.priority)]
                if item in bucket:
                    bucket.remove(item)
        else:
            item = self.item_lut.get(key, None)
        return item

    def take_min(self, remove = True) -> Item:
        '''Take the item with lowest prioity'''
        if len(self) == 0:
            return None
        pointer = self._get_min_nonempty_level()
        if not remove:
            item = self.levels[pointer][0]
        else:
            item = self.levels[pointer].pop(0)
            self.item_lut.pop(item)
        return item

    def take_max(self, remove = True) -> Item:
        '''Take the item with highest prioity'''
        if len(self) == 0:
            return None
        pointer = self._get_max_nonempty_level()
        item = self.levels[pointer][-1]
        if not remove:
            item = self.levels[pointer][-1]
        else:
            item = self.levels[pointer].pop()
            self.item_lut.pop(item)
        return item

    def put(self, item: Item, key=None):
        if key is None: 
            key = item

        item_popped = None
        old_item: Item = self.take_by_key(key, remove=False)
        if old_item is not None:
            # merge duplicate items
            Budget_merge(old_item.budget, item.budget)
            return item_popped
        pointer_new = self.map_priority(item.budget.priority)

        if len(self.item_lut) >= self.capacity:
            # if the capacity is exceeded, remove the lowest-priority item
            pointer = self._get_min_nonempty_level()
            if pointer_new >= pointer:
                bucket = self.levels[self.pointer]
                if len(bucket) > 0:
                    item_lowest = bucket.pop(0)
                    self.item_lut.pop(item_lowest)
                    item_popped = item_lowest
            else:
                item_popped = item
                return item_popped

        self.item_lut[key] = item
        level: list = self.levels[pointer_new]
        level.append(item)

        return item_popped

    def put_back(self, item: Item, key=None):
        ''''''
        # return putIn(oldItem);
        Bag.decay(item)
        self.put(item, key)

    @classmethod
    def decay(cls, item: Item):
        ''''''
        # item.budget.decay()
        Budget_decay(item.budget)

    @classmethod
    def merge(cls, item_base: Item, item_merged: Item):
        Budget_merge(item_base.budget, item_merged.budget)

    def count(self):
        return sum((len(level) for level in self.levels))

    def __contains__(self, item):
        return item in self.item_lut

    def __iter__(self):
        return iter(self.item_lut.lut.values())

    def __len__(self):
        return len(self.item_lut)

    def _is_current_level_empty(self):
        return len(self.levels[self.pointer]) == 0

    def _move_to_next_nonempty_level(self):
        if len(self) == 0: return
        self._move_upward_to_next_level()
        while len(self.levels[self.pointer]) == 0:
            self._move_upward_to_next_level()

    def _move_to_max_nonempty_level(self):
        if len(self) == 0: return
        self.pointer = self.n_levels - 1
        while len(self.levels[self.pointer]) == 0:
            self._move_down_to_next_level()

    def _get_min_nonempty_level(self):
        pointer_cache = self.pointer
        self._move_to_min_nonempty_level()
        pointer = self.pointer
        self.pointer = pointer_cache
        return pointer

    def _get_max_nonempty_level(self):
        pointer_cache = self.pointer
        self._move_to_max_nonempty_level()
        pointer = self.pointer
        self.pointer = pointer_cache
        return pointer

    def _move_to_min_nonempty_level(self):
        self.pointer = 0
        self._move_to_next_nonempty_level()

    def _move_down_to_next_level(self):
        self.pointer = (self.pointer - 1) % self.n_levels

    def _move_upward_to_next_level(self):
        self.pointer = (self.pointer + 1) % self.n_levels

    def reset(self):
        self.item_lut.clear()
        for level in self.levels:
            level.clear()
        self.pointer = 0


    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: #items={len(self)}, #levels={len(self.levels)}, capacity={self.capacity}>"
