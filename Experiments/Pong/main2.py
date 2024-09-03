'''
Pong-v0

Maximize your score in the Atari 2600 game Pong. In this environment, the observation is an RGB image of the screen, which is an array of shape (210, 160, 3) Each action is repeatedly performed for a duration of kk frames, where kk is uniformly sampled from {2,3,4}.

See:

    [1] https://gym.openai.com/envs/Pong-v0/

Note:
    In this experiment, we do not use NARS to play the game, but rather we use a special controller track the ball.

'''

from operator import truth
from random import random
from random import sample
from typing import Iterable
from typing_extensions import Literal
import gym
from Experiments.utils.AtariARI import AtariARIWrapper
from time import sleep
from opennars.NARS.DataStructures._py.Memory import Memory

from opennars.Narsese import Task, Judgement, Term, Stamp, Base
from opennars import Global
from opennars.NARS import Reasoner
from opennars.Console import handle_lines
from opennars.Narsese._py.Compound import Compound
from opennars.Narsese._py.Sentence import Goal
from opennars.Narsese._py.Statement import Statement
from opennars.Narsese._py.Truth import Truth
from opennars.utils.Print import PrintType, print_out
from opennars.utils.tools import rand_seed
from pynput import keyboard


rander_mode: Literal['human'] = 'human'
remind_cycle = 4  # remind the system the goal every x cycles


class Perceptron:
    """
    To convert game states into NARS tasks
    """
    player_x_last: int = None
    player_y_last: int = None
    ball_x_last: int = None
    ball_y_last: int = None
    ball_x_last2: int = None
    fist_iter: bool = True

    def __init__(self) -> None:
        x_min, x_max, y_min, y_max = 68, 205, 46, 205
        thresh_x_0 = 5
        thresh_y_0 = 5
        thresh_x_1 = (x_max-x_min)*0.6*0.4
        thresh_x_2 = (x_max-x_min)*0.6
        thresh_y_1 = (y_max-y_min)*0.6*0.4
        thresh_y_2 = (y_max-y_min)*0.6
        self.thresh_x_0, self.thresh_y_0, self.thresh_x_1, self.thresh_x_2, self.thresh_y_1, self.thresh_y_2 = thresh_x_0, thresh_y_0, thresh_x_1, thresh_x_2, thresh_y_1, thresh_y_2

    def percetption(self, x_p, y_p, x_b, y_b, x_p_last, y_p_last, x_b_last, y_b_last):
        """
        range of x: 68~205
        range of y: 46~205
        """
        width = 7
        if y_p-width > y_b:
            task = Task(Judgement(Term('ball_right'), Stamp(
                Global.time, Global.time, None, Base((Global.get_input_id(),)))))
        elif y_p+width < y_b:
            task = Task(Judgement(Term('ball_left'), Stamp(
                Global.time, Global.time, None, Base((Global.get_input_id(),)))))
        else:
            task = Task(Judgement(Term('ball_middle'), Stamp(
                Global.time, Global.time, None, Base((Global.get_input_id(),)))))
        return task

    def step(self, player_x, player_y, ball_x, ball_y):
        result = None
        hit = False
        if not self.fist_iter:
            result = self.percetption(player_x, player_y, ball_x, ball_y, self.player_x_last,
                                      self.player_y_last, self.ball_x_last, self.ball_y_last)
        else:
            self.fist_iter = False
        if self.ball_x_last2 is not None:
            if self.ball_x_last2 < self.ball_x_last and ball_x < self.ball_x_last:
                hit = True
        self.ball_x_last2 = self.ball_x_last
        self.player_x_last, self.player_y_last, self.ball_x_last, self.ball_y_last = player_x, player_y, ball_x, ball_y
        return result, hit

    def reset(self):
        self.fist_iter = True
        self.ball_x_last2 = None
        self.player_x_last, self.player_y_last, self.ball_x_last, self.ball_y_last = None, None, None, None


class Action:
    value: Literal[0, 2, 3] = 0  # 3: left, 0: stop, 2: right
    time = -100


term_left = Term('left')
term_right = Term('right')
term_stop = Term('stop')


class Controller:
    def __init__(self):
        self.ball_left = Term("ball_left")
        self.ball_right = Term("ball_right")
        self.ball_middle = Term("ball_middle")

    def put(self, event: Task):
        if event.term == self.ball_left:
            player_move((term_left, ))
        elif event.term == self.ball_right:
            player_move((term_right, ))
        elif event.term == self.ball_middle:
            player_move((term_stop, ))


def player_move(arguments: Iterable[Term], task: Task = None, memory: Memory = None):
    """
    It is called back when NARS executes the operation 'move'.
    """
    # assert not task.is_eternal, 'The task should not be eternal.'

    direction = arguments[0]
    # t_occ = task.stamp.t_occurrence
    # if t_occ > Action.time:
    #     Action.time = t_occ
    # else:
    #     return
    if direction == term_left:
        Action.value = 3
    elif direction == term_right:
        Action.value = 2
    elif direction == term_stop:
        Action.value = 0


def policy_nars(env: gym.Env):
    ''''''
    # global action
    seed = 137
    rand_seed(seed)
    epsilon = 0.08

    env.reset()
    # env.render()
    perceptron = Perceptron()

    nars = Controller()

    # register operations
    action_last = Action.value

    motor_bablling = 0

    # begin playing
    i_step = 0
    while True:
        if i_step < motor_bablling:
            Action.value = sample((0, 2, 3), 1)[0]
        else:
            pass
        observation, reward, terminated, truncated, info = env.step(
            Action.value)
        labels = info['labels']
        player_x, player_y = int(labels['player_x']), int(labels['player_y'])
        ball_x, ball_y = int(labels['ball_x']), int(labels['ball_y'])
        # print(ball_x, ball_y, reward)
        hit_event = None
        sensory_event = None
        motor_event = None
        if ball_y != 0:  # the player and machine are not died
            sensory_event, hit = perceptron.step(
                player_x, player_y, ball_x, ball_y)
            if Action.value == 0:
                motor_event = Task(Judgement(Term('stop'), Stamp(
                    Global.time, Global.time, None, Base((Global.get_input_id(),)))))
            elif Action.value == 2:
                motor_event = Task(Judgement(Term('right'), Stamp(
                    Global.time, Global.time, None, Base((Global.get_input_id(),)))))
            elif Action.value == 3:
                motor_event = Task(Judgement(Term('left'), Stamp(
                    Global.time, Global.time, None, Base((Global.get_input_id(),)))))

            if hit:
                print("hit!!!!!!!!!!!!!!!!")
                hit_event = Task(Judgement(Term('hit_ball'), Stamp(
                    Global.time, Global.time, None, Base((Global.get_input_id(),)))))

            if sensory_event is not None:
                nars.put(sensory_event)
            if hit_event is not None:
                nars.put(hit_event)
            if motor_event is not None:
                nars.put(motor_event)

        else:
            perceptron.reset()

        if i_step % remind_cycle == 0:
            goal = Task(
                Goal(Term('hit'), Stamp(Global.time, Global.time,
                     None, Base((Global.get_input_id(),))))
            )  # remind the system the goal of hitting the ball.
            nars.put(goal)

        action_last = Action.value
        i_step += 1
        if terminated:
            env.reset()
        pass


def run():
    '''
    Installation:
        ```
        pip install gym
        pip install 'gym[atari]'
        pip install 'gym[accept-rom-license]'
        pip install pyglet
        ```
    '''
    # env = gym.make("Pong-v0", render_mode='human')
    env = gym.make("Pong-ram-v0", render_mode='human')
    env = AtariARIWrapper(env)

    # observation space
    print(env.observation_space.shape)  # (210, 160, 3)
    # action space
    print(env.action_space)  # Discrete(6)

    act_meanings = env.unwrapped.get_action_meanings()
    print(f'actions (0~{len(act_meanings)-1}): {act_meanings}')

    policy_nars(env)


if __name__ == '__main__':
    run()
