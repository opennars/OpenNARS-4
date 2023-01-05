from pynars.NARS.DataStructures.MC.ChannelMC import ChannelMC
from pynars.Narsese import Term, parser


# task generation utility function
def task_generation_util(visual_signal):
    task = parser.parse(
        "$0.5;0.5;0.5$ <(*, {SELF}, " + visual_signal + ") --> see>. :|: %0.9;0.5%")
    return task


class WumpusWorldGoldChannel(ChannelMC):

    def __init__(self, num_slot, num_event, num_anticipation, num_prediction, memory, env, root_UI, UI_name):
        super(WumpusWorldGoldChannel, self).__init__(num_slot, num_event, num_anticipation, num_prediction, memory,
                                                     root_UI, UI_name)
        self.operations = []
        self.env = env

    def execute(self, term: Term):
        pass

    def information_gathering(self):
        if self.env.world_gold[self.env.position[0], self.env.position[1]] == 2:
            return [task_generation_util("Gold")]
        elif self.env.world_gold[self.env.position[0], self.env.position[1]] == 1:
            return [task_generation_util("Glow")]

