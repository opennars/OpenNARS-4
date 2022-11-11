import numpy as np


class WumpusWorld:

    def __init__(self, size, num_gold, num_wumpus, num_pit):
        self.size = size
        self.num_gold = num_gold
        self.num_wumpus = num_wumpus
        self.num_pit = num_pit
        # world initialization
        self.world_brick = np.arange(size ** 2)
        np.random.shuffle(self.world_brick)
        self.world_brick = self.world_brick.reshape((size, size))
        self.world_gold = None
        self.world_wumpus = None
        self.world_pit = None
        self.position = None
        self.gold_picked = 0
        self.pos_gold = None
        # world generation
        self.generate_world()
        self.visualization()

    def generate_world(self):
        # generate a brand-new world
        self.world_wumpus = np.zeros((self.size, self.size))
        self.world_pit = np.zeros((self.size, self.size))
        self.world_gold = np.zeros((self.size, self.size))
        pos_gold = []
        pos_wumpus = []
        pos_pit = []
        while True:
            pos = tuple(np.random.randint(0, self.size - 1, (1, 2)).squeeze())
            if not (pos_gold + pos_wumpus + pos_pit).__contains__(pos):
                pos_gold.append(tuple(pos))
                if len(pos_gold) == self.num_gold:
                    break
        while True:
            pos = tuple(np.random.randint(0, self.size - 1, (1, 2)).squeeze())
            if not (pos_gold + pos_wumpus + pos_pit).__contains__(pos):
                pos_wumpus.append(tuple(pos))
                if len(pos_wumpus) == self.num_wumpus:
                    break
        while True:
            pos = tuple(np.random.randint(0, self.size - 1, (1, 2)).squeeze())
            if not (pos_gold + pos_wumpus + pos_pit).__contains__(pos):
                pos_pit.append(tuple(pos))
                if len(pos_pit) == self.num_pit:
                    break
        while True:
            pos = tuple(np.random.randint(0, self.size - 1, (1, 2)).squeeze())
            if not (pos_gold + pos_wumpus + pos_pit).__contains__(pos):
                self.position = list(pos)
                break
        self.pos_gold = pos_gold
        for each in pos_gold:
            self.world_gold[each] = 2
            if each[0] != 0:
                self.world_gold[each[0] - 1, each[1]] = 1
            if each[0] != self.size - 1:
                self.world_gold[each[0] + 1, each[1]] = 1
            if each[1] != 0:
                self.world_gold[each[0], each[1] - 1] = 1
            if each[1] != self.size - 1:
                self.world_gold[each[0], each[1] + 1] = 1
        for each in pos_wumpus:
            self.world_wumpus[each] = 2
            if each[0] != 0:
                self.world_wumpus[each[0] - 1, each[1]] = 1
            if each[0] != self.size - 1:
                self.world_wumpus[each[0] + 1, each[1]] = 1
            if each[1] != 0:
                self.world_wumpus[each[0], each[1] - 1] = 1
            if each[1] != self.size - 1:
                self.world_wumpus[each[0], each[1] + 1] = 1
        for each in pos_pit:
            self.world_pit[each] = 2
            if each[0] != 0:
                self.world_pit[each[0] - 1, each[1]] = 1
            if each[0] != self.size - 1:
                self.world_pit[each[0] + 1, each[1]] = 1
            if each[1] != 0:
                self.world_pit[each[0], each[1] - 1] = 1
            if each[1] != self.size - 1:
                self.world_pit[each[0], each[1] + 1] = 1

    def up(self):
        if self.position[0] != 0:
            self.position[0] -= 1

    def down(self):
        if self.position[0] != self.size - 1:
            self.position[0] += 1

    def right(self):
        if self.position[1] != self.size - 1:
            self.position[1] += 1

    def left(self):
        if self.position[1] != 0:
            self.position[1] -= 1

    def pick(self):
        if self.world_gold[self.position] == 2:
            self.gold_picked += 1
            self.world_gold[self.position] = 0
            if self.position[0] != 0:
                self.world_gold[self.position[0] - 1, self.position[1]] = 0
            if self.position[0] != self.size - 1:
                self.world_gold[self.position[0] + 1, self.position[1]] = 0
            if self.position[1] != 0:
                self.world_gold[self.position[0], self.position[1] - 1] = 0
            if self.position[1] != self.size - 1:
                self.world_gold[self.position[0], self.position[1] + 1] = 0

    def visualization(self):
        print("Position")
        print(self.position)
        print("Brick")
        print(self.world_brick)
        print("Gold")
        print(self.world_gold)
        print("Wumpus")
        print(self.world_wumpus)
        print("Pit")
        print(self.world_pit)
        print("=" * 10)

    def shortest_path(self):
        if self.position[0] < self.pos_gold[0][0]:
            return "down"
        if self.position[1] < self.pos_gold[0][1]:
            return "right"
        if self.position[0] > self.pos_gold[0][0]:
            return "up"
        if self.position[1] > self.pos_gold[0][1]:
            return "left"
