from pynars.Narsese import Term, parser
from pynars.NARS.DataStructures.MC.ChannelMC import ChannelMC


class SampleChannel3(ChannelMC):

    def __init__(self, num_slot, num_event, num_anticipation, num_prediction, memory, env, root_UI, UI_name):
        super(SampleChannel3, self).__init__(num_slot, num_event, num_anticipation, num_prediction, memory, root_UI,
                                             UI_name)
        self.operations = []
        self.env = env

    def execute(self, term: Term):
        pass

    # def information_gathering(self):
    #     ret = []
    #     shapes_detected = self.env.check_shape()
    #     for each in shapes_detected:
    #         task = parser.parse("<whole --> " + each + ">. :|:")
    #         # print(task)
    #     # print("==>")
    #     return ret

    def information_gathering(self):
        return self.env.check_shape()
