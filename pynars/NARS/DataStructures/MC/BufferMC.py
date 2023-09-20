from pynars.NAL.Functions import Budget_decay
from pynars.NARS.DataStructures import Memory
from pynars.Narsese import Task


def priority_value(task: Task, memory: Memory):
    """
    calculating the priority value, combined with "memory-based evaluation".
    """
    truth = task.truth
    budget = task.budget
    complexity = task.term.complexity
    pv = truth.e * budget.priority * budget.quality * 0.9 ** complexity  # the original value

    task_in_memory = memory.take_by_key(task, remove=False)
    if task_in_memory is not None:
        # if one task is already in the memory, then its pv is multiplied.
        pv *= 1 + task_in_memory.budget.priority
    else:
        sub_concepts = filter(lambda x: x is not None,
                              [memory.concepts.take_by_key(each, remove=False) for each in task.term.sub_terms])
        for sub_concept in sub_concepts:
            # for each sub-concept in the memory, its pv is increased.
            pv *= 1 + sub_concept.budget.priority

    return pv


class Buffer:
    """
    Buffer is a basic class of all advanced buffers (including, event buffer, global buffer, internal buffer).

    Buffer cycle:
    1. Get a lot of inputs (Tasks), put them to the priority queue based on the inputting truth and budget.
    2. Check these inputs with the memory, this will change the priority value (the original truth and budget will
        not be changed).

    In implementation, checking the memory when each individual input is in.

    3. Pop the most prioritized input.
    """

    def __init__(self, size, memory: Memory):
        self.size = size
        self.memory = memory
        self.priority_queue = []

    def buffer_cycle(self, tasks: [Task]):
        """
        It takes some inputs, and return the one with the maximum priority.
        If there are no inputs, say tasks = [], then it will keep popping till the buffer is empty.
        """
        for task in tasks:
            pv = priority_value(task, self.memory)
            if len(self.priority_queue) == 0:
                self.priority_queue = [(pv, task)]
                continue
            mark = False
            for i in range(len(self.priority_queue)):
                if pv > self.priority_queue[i][0]:
                    self.priority_queue = self.priority_queue[:i] + [(pv, task)] + self.priority_queue[i:]
                    mark = True
                    break
            if not mark:
                self.priority_queue = self.priority_queue + [(pv, task)]
        if len(self.priority_queue) > self.size:
            self.priority_queue = self.priority_queue[:self.size]
        if len(self.priority_queue) > 0:
            return self.priority_queue.pop(0)
        else:
            return None
