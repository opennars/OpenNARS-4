import numpy as np


class SampleEnvironment1:

    def __init__(self):
        self.content = np.array([[2, 2, 1, 1, 0, 0, 0, 2],
                                 [2, 0, 1, 1, 1, 0, 0, 2],
                                 [0, 0, 0, 1, 0, 0, 0, 0],
                                 [0, 0, 0, 0, 0, 0, 0, 0],
                                 [0, 0, 0, 0, 0, 0, 0, 0],
                                 [0, 0, 0, 0, 0, 0, 0, 0],
                                 [0, 0, 0, 0, 0, 0, 0, 0],
                                 [2, 2, 0, 0, 0, 0, 0, 0]])
        self.grid_size = 8
        self.mask_size = 2
        self.step_length = 1
        self.mask_position = [0, 0]  # left_top corner
        self.rotation = 0
        self.shapes = {"shape1": [[0, 2], [1, 3]]}

    def visualization(self):
        pass

    def visual_signal(self):
        if self.mask_position[0] + self.mask_size > self.grid_size and self.mask_position[1] + self.mask_size > \
                self.grid_size:
            A = self.content[self.mask_position[0]:self.grid_size, self.mask_position[1]:self.grid_size]
            B = self.content[0:self.grid_size - self.mask_position[0], 0:self.grid_size - self.mask_position[1]]
            C = self.content[self.mask_position[0]:self.grid_size, 0:self.grid_size - self.mask_position[1]]
            D = self.content[0:self.grid_size - self.mask_position[0], self.mask_position[1]:self.grid_size]
            return np.rot90(np.squeeze(np.array([[A, C], [D, B]])), self.rotation)
        elif self.mask_position[0] + self.mask_size > self.grid_size:
            A = self.content[self.mask_position[0]:self.grid_size,
                self.mask_position[1]:self.mask_position[1] + self.mask_size]
            B = self.content[0:self.grid_size - self.mask_position[0],
                self.mask_position[1]:self.mask_position[1] + self.mask_size]
            return np.rot90(np.squeeze(np.array([[A], [B]])), self.rotation)
        elif self.mask_position[1] + self.mask_size > self.grid_size:
            A = self.content[self.mask_position[0]:self.mask_position[0] + self.mask_size,
                self.mask_position[1]:self.grid_size]
            B = self.content[self.mask_position[0]:self.mask_position[0] + self.mask_size,
                0:self.grid_size - self.mask_position[1]]
            return np.rot90(np.squeeze(np.array([A, B])), self.rotation)
        else:
            return np.rot90(np.squeeze(self.content[self.mask_position[0]:self.mask_position[0] + self.mask_size,
                                       self.mask_position[1]:self.mask_position[1] + self.mask_size]), self.rotation)

    def zoom(self):
        if self.mask_size == 2:
            self.mask_size = 4
            return
        if self.mask_size == 4:
            self.mask_size = 8
            return
        if self.mask_size == 8:
            self.mask_size = 2
            return

    def up(self):
        if self.mask_position[0] == 0:
            self.mask_position[0] = self.grid_size - 1
        else:
            self.mask_position[0] -= 1

    def down(self):
        if self.mask_position[0] == self.grid_size - 1:
            self.mask_position[0] = 0
        else:
            self.mask_position[0] += 1

    def right(self):
        if self.mask_position[1] == self.grid_size - 1:
            self.mask_position[1] = 0
        else:
            self.mask_position[1] += 1

    def left(self):
        if self.mask_position[1] == 0:
            self.mask_position[1] = self.grid_size - 1
        else:
            self.mask_position[1] -= 1

    def rotate(self):
        if self.rotation == 0:
            self.rotation = 1
            return
        if self.rotation == 1:
            self.rotation = 2
            return
        if self.rotation == 2:
            self.rotation = 3
            return
        if self.rotation == 3:
            self.rotation = 0
            return

    def check_shape(self):
        for each_shape in self.shapes:
            if self.mask_position[0] <= self.shapes[each_shape][0][0] \
                    and self.mask_position[1] <= self.shapes[each_shape][0][1] \
                    and self.mask_position[0] + self.mask_size >= self.shapes[each_shape][1][0] \
                    and self.mask_position[1] + self.mask_size >= self.shapes[each_shape][1][1]:
                return each_shape


Env = SampleEnvironment1()
