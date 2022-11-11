from pynars.NARS.DataStructures.MC.ChannelMC import ChannelMC
from pynars.Narsese import Term, parser


# task generation utility function
def task_generation_util(brick_ID):
    task = parser.parse(
        "$0.5;0.5;0.5$ <(*, {SELF}, " + str(brick_ID) + ") --> at>. :|: %0.9;0.5%")
    return task


class WumpusWorldBodySenseChannel(ChannelMC):

    def __init__(self, num_slot, num_event, num_anticipation, num_prediction, memory, env, root_UI, UI_name):
        super(WumpusWorldBodySenseChannel, self).__init__(num_slot, num_event, num_anticipation, num_prediction, memory,
                                                          root_UI, UI_name)
        self.operations = [Term("^up"), Term("^down"), Term("^right"), Term("^left")]
        self.env = env

    def execute(self, term: Term):
        if term.equal(self.operations[0]):
            self.env.up()
        elif term.equal(self.operations[1]):
            self.env.down()
        elif term.equal(self.operations[2]):
            self.env.right()
        elif term.equal(self.operations[3]):
            self.env.left()

    def information_gathering(self):
        return [task_generation_util(self.env.world_brick[self.env.position[0], self.env.position[1]])]
