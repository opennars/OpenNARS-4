from pynars.Narsese import Term, parser
from pynars.NARS.DataStructures.MC.ChannelMC import ChannelMC


# task generation utility function
def task_generation_util(v, ID):
    if round(v) != 0:
        task = parser.parse(
            "<" + ID + " --> shape_" + str(round(v)) + ">. :|: %0.9;0.5%")
        return task


class SampleChannel2(ChannelMC):

    def __init__(self, num_slot, num_event, num_anticipation, num_operation, num_prediction,
                 memory, env, root_UI, UI_name):
        super(SampleChannel2, self).__init__(num_slot, num_event, num_anticipation, num_operation, num_prediction,
                                             memory, root_UI, UI_name)
        # self.operations = [Term("^rotate"), Term("^zoom"), Term("^up"), Term("^down"), Term("^right"), Term("^left")]
        # rotation, zoom temporally disabled
        self.operations = [Term("^up"), Term("^down"), Term("^right"), Term("^left")]
        self.env = env

    def execute(self, term: Term):
        if term.equal(self.operations[0]):
            # self.env.rotate()
            pass
        elif term.equal(self.operations[1]):
            # self.env.zoom()
            pass
        elif term.equal(self.operations[2]):
            self.env.up()
        elif term.equal(self.operations[3]):
            self.env.down()
        elif term.equal(self.operations[4]):
            self.env.right()
        elif term.equal(self.operations[5]):
            self.env.left()
        else:
            return

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
        # print(self.env.mask_position)
        # print(self.env.mask_size)
        # print(self.env.rotation)
        # print("==>")
        # ret.append(parser.parse("<X1 --> X2>."))
        # ret.append(parser.parse("<X3 --> X4>."))
        # ret.append(parser.parse("<X5 --> X6>."))
        # ret.append(parser.parse("<X7 --> X8>."))

        return ret
