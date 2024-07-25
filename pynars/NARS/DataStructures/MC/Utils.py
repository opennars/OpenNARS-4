import random

from pynars.NAL.Functions import Or
from pynars.NARS.DataStructures import Memory
from pynars.Narsese import Task, Truth
from typing import Any, Callable, Generic, List, Optional, Tuple, TypeVar

T = TypeVar('T')

class PriorityQueue(Generic[T]):
    """
    It is not a heap, it is a sorted array by insertion sort. Since we need to 1) access the largest item, 2) access the
    smallest item, 3) access an item in the middle.
    """

    pq: List[Tuple[float, T]]
    size: int

    def __init__(self, size: int) -> None:
        self.pq = []
        self.size = size

    def __len__(self) -> int:
        return len(self.pq)

    def push(self, item, value) -> None:
        """
        Add a new one, regardless whether there are duplicates.
        """
        added = False
        for i in range(len(self.pq)):
            if value <= self.pq[i][0]:
                self.pq = self.pq[:i] + [(value, item)] + self.pq[i:]
                added = True
                break
        if not added:
            self.pq = self.pq + [(value, item)]
        if len(self.pq) > self.size:
            self.pq = self.pq[1:]

    def edit(self, item: T, value: float, identifier: Callable[[T], Any]) -> None:
        """
        Replacement.
        """
        found = False
        for i in range(len(self.pq)):
            if identifier(self.pq[i][1]) == identifier(item):
                self.pq.pop(i)
                # self.pq = self.pq[:i - 1] + self.pq[i:]
                found = True
                break
        if not found:
            return
        self.push(item, value)

    def pop(self) -> Tuple[T, float]:
        """
        Pop the highest.
        """
        value, item = self.pq[-1]
        self.pq = self.pq[:-1]
        return item, value

    def random_pop(self) -> Optional[T]:
        """
        Based on the priority (not budget.priority), randomly pop one buffer task.
        The higher the priority, the higher the probability to be popped.

        Design this function is mainly for the prediction generation in the conceptual design.

        It only gives the item, not the value.
        """
        for i in range(len(self.pq) - 1, -1, -1):
            if random.random() < self.pq[i][0]:
                ret = self.pq[i]
                self.pq = self.pq[:i] + self.pq[i + 1:]
                return ret[1]
        return None

    def show(self, identifier: Callable[[T], str]) -> None:
        """
        Show each item in the priority queue. Since it may contain items other than BufferTasks, you can design you own
        identifier to show what you want to show.
        """
        for each in sorted(self.pq, key=lambda x: x[0]):
            print(round(each[0], 3), "|", each[1].interval, "|", identifier(each[1])) # ? Why assume that the element in the queue has an attribute "interval"?
        print("---")


class BufferTask:
    """
    When a task is input to a buffer, its budget might be different from the original.
    But this is effected by many factors, and each factor might be further revised.
    Therefore, we restore each factor independently; only when everything is decided, the final budget is given.
    """

    task: Task
    channel_parameter: int
    preprocess_effect: float
    is_component: int
    expiration_effect: int

    def __init__(self, task: Task) -> None:
        self.task = task  # the original task
        # the influence of a channel, currently, all channels have parameter 1 and can't be changed
        self.channel_parameter = 1
        self.preprocess_effect = 1
        self.is_component = 0
        self.expiration_effect = 1

    @property
    def priority(self) -> float:
        """
        The priority of a BufferTask, which is not the budget of the corresponding Task.
        """
        return (self.task.budget.priority * self.channel_parameter * self.preprocess_effect * self.expiration_effect *
                ((2 - self.is_component) / 2))


def preprocessing(task: Task, memory: Memory) -> float:
    """
    Check whether a task is already a concept in the memory. If not, its budget is greatly decreased (based on its
    complexity). Else, its budget is the OR of the existed budget.
    """
    concept_in_memory = memory.take_by_key(task.term, False) # ? Why does `take_by_key` use `task` index instead of `task.term` using at this
    if concept_in_memory is None:
        return 1 / (1 + task.term.complexity)
    else:
        return Or(task.budget.priority, concept_in_memory.budget.priority)


def satisfaction_level(truth_1: Truth, truth_2: Truth) -> float:
    """
    Mainly used for check whether an anticipation is satisfied.
    """
    return abs(truth_1.f - truth_2.f)
