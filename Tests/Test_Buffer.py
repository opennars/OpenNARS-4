import unittest

from pynars import Narsese
from pynars.Config import Config
from pynars.NARS.DataStructures import EventBuffer
from pynars.Narsese import Judgement, Term, Task, Stamp, Base, Statement


class TEST_Buffer(unittest.TestCase):

    def test(self):
        pass # todo add regular Buffer tests if needed

class TEST_EventBuffer(unittest.TestCase):

    def test_3_firstorder_event_temporal_chaining(self):
        """
            Add 3 first order events to the buffer (A,B,C), each with different timestamps (A=1, B=2, C=3)

            Ensure that the compound events are all created:
                (A &/ B), (B &/ C), (A &/ C)

            Ensure that the implication statement is created:
                ((A &/ B) =/> C)
        """
        event_buffer: EventBuffer = EventBuffer(capacity=3)

        event_A_task: Task = Narsese.parser.parse("<A1-->A2>.")
        event_A_time = 0
        event_A_task.stamp.t_occurrence = event_A_time

        event_B_task: Task = Narsese.parser.parse("<B1-->B2>.")
        event_B_time = event_A_time + (Config.temporal_duration + 1)
        event_B_task.stamp.t_occurrence = event_B_time

        event_C_task: Task = Narsese.parser.parse("<C1-->C2>.")
        event_C_time = event_B_time + (Config.temporal_duration + 1)
        event_C_task.stamp.t_occurrence = event_C_time

        event_buffer.put(event_A_task)
        event_buffer.put(event_B_task)
        event_buffer.put(event_C_task)
        results = event_buffer.generate_temporal_sentences()


        A_and_B: Task = Narsese.parser.parse("(&/, <A1-->A2>,+" + str(event_B_time - event_A_time) + ",<B1-->B2>).")

        B_and_C: Task = Narsese.parser.parse("(&/, <B1-->B2>,+" + str(event_C_time - event_B_time) + ",<C1-->C2>).")

        A_and_C: Task = Narsese.parser.parse("(&/, <A1-->A2>,+" + str(event_C_time - event_A_time) + ",<C1-->C2>).")

        A_and_B_imply_C = Narsese.parser.parse("<(&/, <A1-->A2>,+" + str(event_B_time - event_A_time) + ",<B1-->B2>,+" + str(
            event_C_time - event_B_time) + ") =/> <C1-->C2>>.")

        expected_results = [A_and_B.term,
                            B_and_C.term,
                            A_and_C.term,
                           A_and_B_imply_C.term]

        for result in results:
            self.assertTrue(result.term in expected_results,msg=str(result.term) + " was not found in results.")
            expected_results.remove(result.term)


    def test_buffer_overflow_maintains_capacity(self):
        """
            Test to ensure the number of items in the buffer doesnt
            exceed its upper bound
        """
        capacity = 5
        event_buffer: EventBuffer = EventBuffer(capacity=capacity)

        # ensure the buffer adds events regularly
        for i in range(capacity):
            self.assertEqual(i, len(event_buffer))
            event_task = Narsese.parser.parse("<A1-->A2>.")
            event_task.stamp.t_occurrence = 1
            event_buffer.put(event_task)

        # ensure the buffer is at max capcity
        self.assertEqual(capacity, len(event_buffer))

        # ensure the buffer does not exceed its capacity when overflowing
        event_task = Narsese.parser.parse("<A1-->A2>.")
        event_task.stamp.t_occurrence = 1
        event_buffer.put(event_task)
        self.assertEqual(capacity, len(event_buffer))

    def test_buffer_overflow_discards_older_events(self):
        """
            Test to ensure that new events are added to the buffer,
            whereas old events are purged from the buffer.
        """
        capacity = 5
        event_buffer: EventBuffer = EventBuffer(capacity=capacity)

        for i in range(capacity):
            event_task = Narsese.parser.parse("<A" + str(i) + " -->B" + str(i) + ">.")
            event_task.stamp.t_occurrence = i + 1
            event_buffer.put(event_task)

        # ensure getting older/newer events functions properly
        self.assertTrue(event_buffer.get_newest_event().stamp.t_occurrence > event_buffer.get_oldest_event().stamp.t_occurrence)

        # add an event older than all the others, ensure it doesnt get into the buffer
        old_event_task = Narsese.parser.parse("<oldA-->oldB>.")
        old_event_task.stamp.t_occurrence = 0
        event_buffer.put(old_event_task)
        self.assertTrue(event_buffer.get_oldest_event().term != old_event_task.term)

        # add an event newer than all the others, ensure it goes to the front of the buffer
        new_event_task = Narsese.parser.parse("<newA-->newB>.")
        new_event_task.stamp.t_occurrence = capacity
        event_buffer.put(new_event_task)
        self.assertTrue(event_buffer.get_newest_event().term == new_event_task.term)

if __name__ == '__main__':

    test_classes_to_run = [
        TEST_EventBuffer
    ]

    loader = unittest.TestLoader()

    suites = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites.append(suite)

    suites = unittest.TestSuite(suites)

    runner = unittest.TextTestRunner()
    results = runner.run(suites)