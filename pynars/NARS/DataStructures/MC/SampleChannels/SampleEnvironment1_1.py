import numpy as np


class SampleEnvironment1_1:

    def __init__(self):
        self.content = None
        self.grid_size = None
        self.content_generation(8)
        self.mask_size = 2
        self.step_length = 1
        self.mask_position = [0, 0]  # left_top corner

    def content_generation(self, n):
        self.grid_size = n
        self.content = np.zeros([n, n])
        anchor = [np.random.randint(n), np.random.randint(n)]
        # first block, block [1]
        self.content[anchor[0], (anchor[1] + 2) % n] = 1
        self.content[(anchor[0] + 1) % n, (anchor[1] + 2) % n] = 1
        self.content[anchor[0], (anchor[1] + 3) % n] = 1
        self.content[(anchor[0] + 1) % n, (anchor[1] + 2) % n] = 1
        # first block, block [2]
        self.content[(anchor[0] + 2) % n, anchor[1]] = 2
        self.content[(anchor[0] + 3) % n, anchor[1]] = 2
        self.content[(anchor[0] + 2) % n, (anchor[1] + 1) % n] = 2
        self.content[(anchor[0] + 3) % n, (anchor[1] + 1) % n] = 2
        # first block, block [3]
        self.content[(anchor[0] + 2) % n, (anchor[1] + 4) % n] = 3
        self.content[(anchor[0] + 2) % n, (anchor[1] + 5) % n] = 3
        self.content[(anchor[0] + 3) % n, (anchor[1] + 4) % n] = 3
        self.content[(anchor[0] + 3) % n, (anchor[1] + 5) % n] = 3
        # first block, block [4]
        self.content[(anchor[0] + 4) % n, (anchor[1] + 2) % n] = 4
        self.content[(anchor[0] + 4) % n, (anchor[1] + 3) % n] = 4
        self.content[(anchor[0] + 5) % n, (anchor[1] + 2) % n] = 4
        self.content[(anchor[0] + 5) % n, (anchor[1] + 3) % n] = 4

    def visualization(self):
        pass

    def visual_signal(self):
        if self.mask_position[0] + self.mask_size > self.grid_size and self.mask_position[1] + self.mask_size > \
                self.grid_size:
            A = self.content[self.mask_position[0]:self.grid_size, self.mask_position[1]:self.grid_size]
            B = self.content[0:self.grid_size - self.mask_position[0], 0:self.grid_size - self.mask_position[1]]
            C = self.content[self.mask_position[0]:self.grid_size, 0:self.grid_size - self.mask_position[1]]
            D = self.content[0:self.grid_size - self.mask_position[0], self.mask_position[1]:self.grid_size]
            return np.squeeze(np.array([[A, C], [D, B]]))
        elif self.mask_position[0] + self.mask_size > self.grid_size:
            A = self.content[self.mask_position[0]:self.grid_size,
                self.mask_position[1]:self.mask_position[1] + self.mask_size]
            B = self.content[0:self.grid_size - self.mask_position[0],
                self.mask_position[1]:self.mask_position[1] + self.mask_size]
            return np.squeeze(np.array([[A], [B]]))
        elif self.mask_position[1] + self.mask_size > self.grid_size:
            A = self.content[self.mask_position[0]:self.mask_position[0] + self.mask_size,
                self.mask_position[1]:self.grid_size]
            B = self.content[self.mask_position[0]:self.mask_position[0] + self.mask_size,
                0:self.grid_size - self.mask_position[1]]
            return np.squeeze(np.array([A, B]))
        else:
            return np.squeeze(self.content[self.mask_position[0]:self.mask_position[0] + self.mask_size,
                              self.mask_position[1]:self.mask_position[1] + self.mask_size])

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

    def check_shape(self):
        tmp = self.visual_signal()
        if tmp.all() == 1:
            return "block_1"
        elif tmp.all() == 2:
            return "block_2"
        elif tmp.all() == 3:
            return "block_3"
        elif tmp.all() == 4:
            return "block_4"
