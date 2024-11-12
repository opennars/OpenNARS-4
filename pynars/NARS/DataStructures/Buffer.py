from pynars.NAL.Functions import Truth_intersection, Stamp_merge
from pynars.NAL.Inference.TemporalRules import induction_composition, induction_implication
from .Bag import Bag
from pynars.Config import Config
from pynars.Narsese import Item, Task, TermType, Compound, Interval, Statement
from pynars.NAL.Functions.BudgetFunctions import *
from typing import Callable, Any, List


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
        self.busyness = 0.5

    # def put(self, task: Task):
    #     return Bag.put(self, task, (hash(task), hash(task.stamp.evidential_base)))
    
    # def put_back(self, task: Task):
    #     ''''''
    #     return Bag.put_back(self, task, (hash(task), hash(task.stamp.evidential_base)))

    

    def is_expired(self, put_time, current_time):
        return (current_time - put_time) > self.max_duration


class EventBuffer:
    '''
        This buffer holds first-order events, sorted by time.
        The purpose of this buffer is to generate temporal implication statements, e.g., (A &/ B =/> C)
        and compound events, e.g., (A &/ B).

        The operation for generating temporal statements is exhaustive. That means, for generating 3-component
        implication statements like (A &/ B =/> C), the algorithm scales O(n^3) for n elements

        The oldest events are at the lowest index, the newest events are at the highest index.
        The larger the event's timestamp, the newer it is.
    '''
    def __init__(self, capacity: int):
        self.buffer: List[Task] = []
        self.capacity: int = capacity

    def __len__(self):
        return len(self.buffer)

    def get_oldest_event(self):
        return self.buffer[0]

    def get_newest_event(self):
        return self.buffer[-1]

    def generate_temporal_sentences(self):
        results: List[Task] = []
        # first event A occurred, then event B occurred, then event C
        for i in range(len(self.buffer)):
            event_A_task = self.buffer[i]
            for j in range(i+1,len(self.buffer)):
                # create (A &/ B)
                event_B_task = self.buffer[j]
                compound_event_task = induction_composition(event_A_task, event_B_task)
                results.append(compound_event_task) # append
                for k in range(j + 1, len(self.buffer)):
                    # create (A &/ B) =/> C
                    event_C = self.buffer[k]
                    temporal_implication_task = induction_implication(compound_event_task, event_C)
                    results.append(temporal_implication_task)  # append

        return results

    def put(self, event_task_to_insert: Task):
        if not self.can_task_enter(event_task_to_insert):
            raise Exception("ERROR! Only events with first-order statements can enter the EventBuffer.")

        if len(self.buffer) == 0: # if nothing in the buffer, just insert it
            self.buffer.append(event_task_to_insert)
            return

        newest_event = self.get_newest_event()

        if event_task_to_insert.stamp.t_occurrence >= newest_event.stamp.t_occurrence:
            # if its newer than even the newest event, just insert it at the end
            self.buffer.append(event_task_to_insert)
        else:
            # otherwise, we have to go through the list to insert it properly
            for i in range(len(self.buffer)):
                buffer_event = self.buffer[i]
                if event_task_to_insert.stamp.t_occurrence <= buffer_event.stamp.t_occurrence:
                    # the inserted event occurs first, so insert it here
                    self.buffer.insert(i, event_task_to_insert)
                    break


        if len(self.buffer) > self.capacity:
            # if too many events, take out the oldest event
            self.buffer.pop(0)

    def can_task_enter(self, task: Task):
       return task.is_event \
            and task.term.type == TermType.STATEMENT
            # and not task.term.is_higher_order