from Pong.PongChannel import PongChannel, execute_MLeft, execute_MRight, execute_Hold
from pynars.NARS import Reasoner
from pynars.NARS.DataStructures.MC.EventBuffer import EventBuffer
from pynars.NARS.DataStructures.MC.NarseseChannel import NarseseChannel
from pynars.NARS.DataStructures.MC.OutputBuffer import OutputBuffer
from pynars.Narsese import Task

NarseseChannel_size = 100
Buffer_D = 0.9


class Console:

    def __init__(self, num_slot, num_events, num_anticipations, num_operations, num_predictive_implications, N=1):
        self.narsese_channel = NarseseChannel(NarseseChannel_size, N, Buffer_D)
        # internal/global buffers are event buffers
        self.internal_buffer = EventBuffer(num_slot, num_events, num_anticipations, num_operations,
                                           num_predictive_implications, N)
        self.global_buffer = EventBuffer(num_slot, num_events, num_anticipations, num_operations,
                                         num_predictive_implications, N)
        self.output_buffer = OutputBuffer(self.narsese_channel)
        self.for_globalBuffer = []

        self.sensorimotor_channels = {}

    def register_sensorimotor_channels(self, name, channel):
        self.sensorimotor_channels[name] = channel

    def unregister_sensorimotor_channels(self, name):
        self.sensorimotor_channels.pop(name)

    def cycle(self, text, reasoner):
        # get the task(s) from the Narsese input channel
        tmp = self.narsese_channel.channel_cycle(text, reasoner.memory)
        self.for_globalBuffer += tmp
        # collect the other tasks from the other channels
        for each in self.sensorimotor_channels:
            tmp = self.sensorimotor_channels[each].channel_cycle(reasoner.memory)

            # print("from sensorimotor channel", [each_tmp.sentence for each_tmp in tmp])
            # print("---")
            # for each_pq in self.sensorimotor_channels[each].input_buffer.slots[
            #     self.sensorimotor_channels[each].input_buffer.curr].events.pq:
            #     print("compounds", each_pq[0], each_pq[1].task.sentence)
            # print("---")
            # for each_prediction in self.sensorimotor_channels[each].input_buffer.predictive_implications.pq:
            #     print("predictions", each_prediction[0], each_prediction[1].task.sentence)
            # print("---")
            # for each_prediction in self.sensorimotor_channels[each].input_buffer.slots[
            #     self.sensorimotor_channels[each].input_buffer.curr].anticipations:
            #     print("anticipations", each_prediction)
            # print("---")

            self.for_globalBuffer += tmp

        # add all above tasks to the global buffer,
        # get the selected (and potentially composed) tasks and send them to the memory

        # cheating
        # since something is wrong the reasoner, such that it cannot generate sub-goals correctly, I have to cheat.
        # ==============================================================================================================
        _, for_memory = self.global_buffer.buffer_cycle(self.for_globalBuffer, reasoner.memory)
        # ==============================================================================================================
        # original
        # for_memory = self.global_buffer.buffer_cycle(self.for_globalBuffer, reasoner.memory)
        # ==============================================================================================================

        try:
            reasoner.memory.accept(*for_memory)  # unexpected errors in the reasoner ¯\_(ツ)_/¯
        except:
            pass

        self.for_globalBuffer = []

        # put all selected tasks to the memory and select one concept for reasoning
        try:
            tmp = reasoner.cycle()  # unexpected errors in the reasoner ¯\_(ツ)_/¯
        except:
            return

        if tmp is not None:
            tasks_derived, judgement_revised, goal_revised, answers_question, answers_quest, _ = tmp
        else:
            tasks_derived, judgement_revised, goal_revised, answers_question, answers_quest = [], [], [], [], []

        tasks_all = []
        if tasks_derived is not None:
            if isinstance(tasks_derived, Task):
                tasks_all.append(tasks_derived)
            elif len(tasks_derived) != 0:
                tasks_all.extend(tasks_derived)
        if judgement_revised is not None:
            if isinstance(judgement_revised, Task):
                tasks_all.append(judgement_revised)
            elif len(judgement_revised) != 0:
                tasks_all.extend(judgement_revised)
        if goal_revised is not None:
            if isinstance(goal_revised, Task):
                tasks_all.append(goal_revised)
            elif len(goal_revised) != 0:
                tasks_all.extend(goal_revised)
        if answers_question is not None:
            if isinstance(answers_question, Task):
                tasks_all.append(answers_question)
            elif len(answers_question) != 0:
                tasks_all.extend(answers_question)
        if answers_quest is not None:
            if isinstance(answers_quest, Task):
                tasks_all.append(answers_quest)
            elif len(answers_quest) != 0:
                tasks_all.extend(answers_quest)
        tmp = []
        for each in tasks_all:
            if not each.term.has_var and each.budget.priority > 0.5:  # ¯\_(ツ)_/¯, the system prefers to generate (--, )
                tmp.append(each)
        tasks_all = tmp

        self.output_buffer.buffer_cycle(tasks_all, self.sensorimotor_channels)

        # put all generated new tasks (or revised tasks) to the internal buffer,
        # for those answered questions, to-do operations, they are not sent to the corresponding output buffer,
        # e.g., the output buffer in the Narsese Channel, or those in the sensorimotor channels.
        for_internalBuffer = tasks_all

        # send selected results to the internal buffer, and the selected tasks will be forward to self.for_globalBuffer,
        # for the next cycle

        # cheating
        # since something is wrong the reasoner, such that it cannot generate sub-goals correctly, I have to cheat.
        # ==============================================================================================================
        _, tmp = self.internal_buffer.buffer_cycle(for_internalBuffer, reasoner.memory)
        # ==============================================================================================================
        # original
        # tmp = self.internal_buffer.buffer_cycle(for_internalBuffer, reasoner.memory)
        # ==============================================================================================================

        if tmp is not None:
            self.for_globalBuffer = tmp


if __name__ == "__main__":
    r = Reasoner(100, 100)
    pc = PongChannel("Pong", 1, 50, 50, 5, 50, 50, 2)
    pc.register_operation("^left", execute_MLeft, ["^left", "left"])
    pc.register_operation("^right", execute_MRight, ["^right", "right"])
    pc.register_operation("^hold", execute_Hold, ["^hold", "mid"])

    c = Console(2, 50, 50, 5, 50, 2)
    c.register_sensorimotor_channels(pc.ID, pc)

    for i in range(10000):
        if i % 25 == 0:
            c.cycle("<{SELF} --> [good]>!", r)
            # pc.input_buffer.predictive_implications.show(lambda x: x.task.sentence)
            for each in pc.reactions.pq:
                print("reactions", each)
        else:
            c.cycle("1", r)
