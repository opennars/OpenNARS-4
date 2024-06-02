import random
import socket

from pynars.NARS import Reasoner
from pynars.NARS.DataStructures.MC.SensorimotorChannel import SensorimotorChannel
from pynars.Narsese import parser

"""
The sensorimotor channel for the Pong game.
It is placed here because I believe that every channel needs to be designed by the user.
"""

nars_address = ("127.0.0.1", 54321)
game_address = ("127.0.0.1", 12345)


class PongChannel(SensorimotorChannel):

    def __init__(self, ID, num_slot, num_events, num_anticipations, num_operations, num_predictive_implications,
                 num_reactions, N=1):
        super().__init__(ID, num_slot, num_events, num_anticipations, num_operations, num_predictive_implications,
                         num_reactions, N)
        """
        Babbling is designed to be very simple. If the current channel cannot generate an operation based on the 
        reaction, then there is a certain probability that an operation will be generated through babbling. It is worth 
        noting that currently a channel can only execute one operation in a cycle. Of course, in the future, this 
        restriction can be lifted after the mutually exclusive relationship between operations is specified.
        
        Babbling can be performed a limited number of times and cannot be replenished.
        """
        self.num_babbling = 200
        self.babbling_chance = 0.5

    def information_gathering(self):
        """
        Receive a string from the game and parse it into a task.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(nars_address)
        data, _ = sock.recvfrom(1024)
        status = data.decode()
        if status != "GAME FAILED":
            try:
                return [parser.parse(each) for each in status.split("|")]
            except:  # for unexpected game input error
                print(status)
                exit()
        else:
            return []

    def babbling(self):
        """
        Based on the probability and remaining counts.
        """
        if random.random() < self.babbling_chance and self.num_babbling > 0:
            self.num_babbling -= 1
            return random.choice(list(self.operations.keys()))


def execute_MLeft():
    """
    All channels need to register for its own operations. It is recommended to list them in the channel created.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto("^left".encode(), game_address)


def execute_MRight():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto("^right".encode(), game_address)


def execute_Hold():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto("^hold".encode(), game_address)


if __name__ == "__main__":
    """
    Open the game first and run this script to see all predictions generated.
    "+1, +2" will not be in the Narsese.
    """
    r = Reasoner(100, 100)
    pc = PongChannel("Pong", 2, 5, 50, 5, 50, 50, 1)
    pc.register_operation("^left", execute_MLeft, ["^left", "left"])
    pc.register_operation("^right", execute_MRight, ["^right", "right"])
    pc.register_operation("^hold", execute_Hold, ["^hold", "mid"])
    for _ in range(1000):
        pc.channel_cycle(r.memory)
        pc.input_buffer.predictive_implications.show(lambda x: x.task.sentence)
