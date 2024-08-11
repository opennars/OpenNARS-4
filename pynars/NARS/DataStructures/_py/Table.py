from typing import Union
from depq import DEPQ
from pynars.Narsese import Task, Belief

class Table:
    '''
    Used for belief table, desire table, etc., in the `Concept`.
    '''
    def __init__(self, capacity):
        self._table = DEPQ(maxlen=capacity)

    def add(self, task: Task, p: float):
        if task in self:
            self._table.remove(task)
        self._table.insert(task, p)


    # def remove(self, task: Task):
    #     self._table.elim(task)

    @property
    def empty(self):
        return self._table.is_empty()
    
    def first(self):
        return self._table.first() if len(self._table) > 0 else None
    
    def last(self):
        return self._table.last() if len(self._table) > 0 else None

    def __iter__(self):
        return (value for value, _ in self._table)
    
    def __contains__(self, item):
        return item in self._table
    
    def values(self):
        return tuple(iter(self))
    
    def items(self):
        return tuple(iter(self._table))

    def keys(self):
        return tuple(key for _, key in self._table)

    def __getitem__(self, idx: int) -> Union[Task, Belief]:
        return self._table[idx][0]

    def __len__(self):
        return len(self._table)

    def __str__(self):
        return f'<Table: #items={len(self._table)}, capacity={self._table.maxlen}>'

    def __repr__(self):
        return str(self)