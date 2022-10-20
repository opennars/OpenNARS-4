from pynars.NARS.DataStructures.MC.ChannelMC import ChannelMC
from pynars.Narsese import Term, parser


# task generation utility function
def task_generation_util(v, ID):
    if v > 0.5:
        round_v = round(v)
        task = parser.parse(
            "<" + ID + " --> shape_" + str(round_v) + ">. %" + str(1 - abs(round_v - v)) + ";0.5%")
        return task


class SampleChannel2(ChannelMC):

    def __init__(self, ID: str, num_slot, num_event, num_anticipation, num_prediction, memory, env):
        super(SampleChannel2, self).__init__(ID, num_slot, num_event, num_anticipation, num_prediction, memory)
        self.operations = [Term("^rotate"), Term("^zoom"), Term("^up"), Term("^down"), Term("^right"), Term("^left")]
        self.env = env

    def execute(self, term: Term):
        if term.equal(self.operations[0]):
            self.env.rotate()
        elif term.equal(self.operations[1]):
            self.env.zoom()
        elif term.equal(self.operations[2]):
            self.env.up()
        elif term.equal(self.operations[3]):
            self.env.down()
        elif term.equal(self.operations[4]):
            self.env.right()
        elif term.equal(self.operations[5]):
            self.env.left()

    def information_gathering(self):
        ret = []
        mat = self.env.visual_signal()
        task_A, task_B, task_C, task_D = None, None, None, None
        if mat.shape[0] == 2:
            A = (mat[0, 0] + mat[0, 1]) / 2
            B = (mat[0, 0] + mat[1, 0]) / 2
            C = (mat[1, 0] + mat[1, 1]) / 2
            D = (mat[0, 1] + mat[1, 1]) / 2
            task_A = task_generation_util(A, "A")
            task_B = task_generation_util(B, "B")
            task_C = task_generation_util(C, "C")
            task_D = task_generation_util(D, "D")
        elif mat.shape[0] == 4:
            A = (sum(mat[0, :]) + mat[1, 1] + mat[1, 2]) / 6
            B = (sum(mat[:, 0]) + mat[1, 1] + mat[2, 1]) / 6
            C = (sum(mat[3, :]) + mat[2, 1] + mat[2, 2]) / 6
            D = (sum(mat[:, 3]) + mat[1, 2] + mat[2, 2]) / 6
            task_A = task_generation_util(A, "A")
            task_B = task_generation_util(B, "B")
            task_C = task_generation_util(C, "C")
            task_D = task_generation_util(D, "D")
        elif mat.shape[0] == 8:
            A = (sum(mat[0, :]) + sum(mat[1, 1:6]) + sum(mat[2, 2:5]) + mat[3, 3]) / 19
            B = (sum(mat[:, 0]) + sum(mat[1:6, 1]) + sum(mat[2:5, 2]) + mat[3, 3]) / 19
            C = (sum(mat[7, :]) + sum(mat[6, 1:6]) + sum(mat[5, 2:5]) + mat[3, 3]) / 19
            D = (sum(mat[:, 7]) + sum(mat[1:6, ]) + sum(mat[2:5, 2]) + mat[3, 3]) / 19
            task_A = task_generation_util(A, "A")
            task_B = task_generation_util(B, "B")
            task_C = task_generation_util(C, "C")
            task_D = task_generation_util(D, "D")
        if task_A:
            ret.append(task_A)
        if task_B:
            ret.append(task_B)
        if task_C:
            ret.append(task_C)
        if task_D:
            ret.append(task_D)
        return ret
