from .Bag import Bag
from pynars.Config import Config
from pynars.Narsese import Item, Task
from pynars.NAL.Functions.BudgetFunctions import *
from typing import Callable, Any

class Buffer(Bag):
    '''
    According to *the Conceptual Design of OpenNARS 3.1.0*:
        A buffer is a time-restricted bag containing new (input or derived) tasks.
        A buffer has the following major routines:
        **put**: As defined in bag.
        **take**: As defined in bag, except that if the selected task is already expired,
        the selection will repeat up to a predetermined times. Also, in buffer this
        operation is not directly invoked from the outside, but from insider, as
        part of observe.
        **observe**: If the buffer does not carry out temporal composition, this routine
        just call take to get a task, and return it. Otherwise it also uses the selected
        task and every other tasks to form tasks containing compounds events.
        The new tasks are put into the buffers. Given their high complexity,
        most of them will be removed. The remaining ones usually correspond to
        existing concepts in the memory or tasks in the buffer.
    '''

    def __init__(self, capacity: int, n_buckets: int=None, take_in_order: bool=False, max_duration: int=None) -> None:
        key: Callable[[Task], Any] = lambda task: (hash(task), hash(task.stamp.evidential_base))
        Bag.__init__(self, capacity, n_buckets=n_buckets, take_in_order=take_in_order, key=key)
        self.max_duration = max_duration if max_duration is not None else Config.max_duration

    # def put(self, task: Task):
    #     return Bag.put(self, task, (hash(task), hash(task.stamp.evidential_base)))
    
    # def put_back(self, task: Task):
    #     ''''''
    #     return Bag.put_back(self, task, (hash(task), hash(task.stamp.evidential_base)))

    

    def is_expired(self, put_time, current_time):
        return (current_time - put_time) > self.max_duration
