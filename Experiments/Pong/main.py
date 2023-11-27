'''
Pong-v0

Maximize your score in the Atari 2600 game Pong. In this environment, the observation is an RGB image of the screen, which is an array of shape (210, 160, 3) Each action is repeatedly performed for a duration of kk frames, where kk is uniformly sampled from {2,3,4}.

See:

    [1] https://gym.openai.com/envs/Pong-v0/

'''

from operator import truth
from random import random
from random import sample
from typing import Iterable
from typing_extensions import Literal
import gym
from atariari.benchmark.wrapper import AtariARIWrapper
from time import sleep
from pynars.NARS.DataStructures._py.Memory import Memory

from pynars.Narsese import Task, Judgement, Term, Stamp, Base
from pynars import Global
from pynars.NARS import Reasoner
from pynars.Console import handle_lines, run_file
from pynars.Narsese._py.Compound import Compound
from pynars.Narsese._py.Sentence import Goal
from pynars.Narsese._py.Statement import Statement
from pynars.Narsese._py.Truth import Truth
from pynars.utils.Print import PrintType, print_out
from pynars.utils.tools import rand_seed

rander_mode: Literal['human'] = 'human'


class Perceptron:
    ''''''
    player_x_last: int = None
    player_y_last: int = None
    ball_x_last: int = None
    ball_y_last: int = None
    i_step: int = 0

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
        '''
        range of x: 68~205
        range of y: 46~205
        '''
        
        if y_p+5 > y_b: # <{ball} --> [right]>
            task = Task(Judgement(Statement.Inheritance(Compound.Instance(Term('ball')), Compound.Property(Term('right'))), Stamp(Global.time, Global.time, None, Base((Global.get_input_id(),)))))
        elif y_p-5 < y_b:
            task = Task(Judgement(Statement.Inheritance(Compound.Instance(Term('ball')), Compound.Property(Term('left'))), Stamp(Global.time, Global.time, None, Base((Global.get_input_id(),)))))
        else:
            task = Task(Judgement(Statement.Inheritance(Compound.Instance(Term('ball')), Compound.Property(Term('middle'))), Stamp(Global.time, Global.time, None, Base((Global.get_input_id(),)))))
        return task


    def step(self, player_x, player_y, ball_x, ball_y):
        ''''''
        result = None
        if self.i_step != 0:
            result = self.percetption(player_x, player_y, ball_x, ball_y, self.player_x_last, self.player_y_last, self.ball_x_last, self.ball_y_last)
        self.player_x_last, self.player_y_last, self.ball_x_last, self.ball_y_last = player_x, player_y, ball_x, ball_y
        self.i_step += 1
        return result

class Action:
    value: Literal[0, 2, 3] = 0 # 3: left, 0: stop, 2: right
    time = -100

def policy_nars(env: gym.Env):
    ''''''
    # global action
    seed = 137
    rand_seed(seed)
    epsilon = 0.08

    env.reset()
    # env.render()
    done = False
    perceptron = Perceptron()
    
    nars = Reasoner(1000, 1000)
    # initialize nars
    run_file(nars, './pynars/RL/Pong/pong.nal')
    for _ in range(1):
        handle_lines(nars, '9')
    handle_lines(nars, '1')

    # register operations 
    action_last = Action.value
    term_left = Term('left')
    term_right = Term('right')
    def player_move(arguments: Iterable[Term], task: Task=None, memory: Memory=None):
        ''''''
        if task.is_eternal: return
        direction = arguments[0]
        t_occ = task.stamp.t_occurrence
        if t_occ > Action.time:
            Action.time = t_occ
        else: 
            return
        if direction == term_left:
            Action.value = 3
        elif direction == term_right:
            Action.value = 2

    def player_stop(arguments: Iterable[Term], task: Task=None, memory: Memory=None):
        Action.value = 0

    nars.register_operator('move', player_move)
    nars.register_operator('stop', player_stop)
        
    # begin playing
    i_step = 0
    while not done:
        if Action.value == 0 and random() < 0.08: # random action
            Action.value = sample((0, 2, 3), 1)[0]
        observation, reward, done, info = env.step(Action.value)
        labels = info['labels']
        player_x, player_y = int(labels['player_x']), int(labels['player_y'])
        ball_x, ball_y = int(labels['ball_x']), int(labels['ball_y'])
        if ball_y != 0: # the player and machine are not died
            task = perceptron.step(player_x, player_y, ball_x, ball_y)
            # info_str = f'obs: {observation.shape}; reward: {reward}; ball: ({ball_x}, {ball_y});'
            # # info_str += f'{dist_x.term if dist_x is not None else None, dist_y.term if dist_y is not None else None, change_x.term if change_x is not None else None, change_y.term if change_y is not None else None}'
            # print(info_str)
            if task is not None:
                nars.perception_channel.put(task)
                print_out(PrintType.IN, task.sentence, *task.budget)
            handle_lines(nars, '10')
            # nars.cycles(10)
        else:
            game_reset = Task(Judgement(Statement.Inheritance(Compound.Instance(Term('game')), Compound.Property(Term('reset'))), Stamp(Global.time, Global.time, None, Base((Global.get_input_id(), )))))
            nars.perception_channel.put(game_reset)
        if i_step % 4 == 0:
            goal = Task(Goal(Statement.Inheritance(Compound.Instance(Term('SELF')), Compound.Property(Term('good'))), Stamp(Global.time, Global.time, None, Base((Global.get_input_id(),))))) # remind the system the goal every 4 steps.
            nars.perception_channel.put(goal)

        action_last = Action.value
        i_step += 1
        pass
        

def run():
    '''
    Installation:
        1. gym
        ```
        pip install gym
        pip install gym[atari]
        pip install gym[accept-rom-license]
        pip install pyglet
        ```
        2. interface
        ```
        pip install git+git://github.com/mila-iqia/atari-representation-learning.git
        ```
    '''
    # env = gym.make("Pong-v0", render_mode='human')  
    env = gym.make("Pong-ram-v0", render_mode='human') 
    env = AtariARIWrapper(env)

    # observation space
    print(env.observation_space.shape) # (210, 160, 3)
    # action space
    print(env.action_space) # Discrete(6)

    act_meanings = env.unwrapped.get_action_meanings()
    print(f'actions (0~{len(act_meanings)-1}): {act_meanings}')

    policy_nars(env)


if __name__ == '__main__':
    run()