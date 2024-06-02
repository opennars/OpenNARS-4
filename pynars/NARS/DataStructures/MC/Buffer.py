from pynars.NARS.DataStructures.MC import Utils
from pynars.NARS.DataStructures.MC.Utils import BufferTask, PriorityQueue


class Buffer:

    def __init__(self, size, N=1, D=0.9):
        """
        Buffer, which is not event buffer, currently only used in the Narsese channel.

        pq: a queue of buffer_tasks (in Utils.py)
        size: the length of the buffer
        N: pop top-N tasks in the pq
        D: decay rate for the remaining tasks in the buffer
        """
        self.pq = PriorityQueue(size)
        self.N = N
        self.D = D

    def select(self):
        """
        Select the top-N BufferTasks from the buffer, decay the remaining.
        """
        ret = []
        push_back = []
        for i in range(len(self.pq)):
            if i <= self.N:
                buffer_task, _ = self.pq.pop()
                ret.append(buffer_task)
            else:
                buffer_task, _ = self.pq.pop()
                buffer_task.expiration_effect *= self.D
                push_back.append(buffer_task)
        for each in push_back:
            self.pq.push(each, each.priority)
        return [each.task for each in ret]

    def add(self, tasks, memory):
        """
        Convert input tasks (Task) into BufferTasks.
        """
        for each in tasks:
            buffer_task = BufferTask(each)
            buffer_task.preprocess_effect = Utils.preprocessing(each, memory)
            self.pq.push(buffer_task, buffer_task.priority)
