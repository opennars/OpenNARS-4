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
from pynars.Narsese._py.Statement import Statement
from pynars.Narsese._py.Truth import Truth
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
        

        diff_x = x_p - x_b
        diff_y = y_p - y_b
        diff_x_last = x_p_last - x_b_last
        diff_y_last = y_p_last - y_b_last
        if abs(diff_x) < self.thresh_x_0: dist_x = 'zero'
        elif abs(diff_x) < self.thresh_x_1: dist_x = 'little'
        elif abs(diff_x) < self.thresh_x_2: dist_x = 'middle'
        else: dist_x = 'large'
        
        if abs(diff_y) < self.thresh_y_0: dist_y = 'zero'
        elif abs(diff_y) < self.thresh_y_1: dist_y = 'little'
        elif abs(diff_y) < self.thresh_y_2: dist_y = 'middle'
        else: dist_y = 'large'

        if abs(diff_x) < abs(diff_x_last): change_x = 'decrease'
        else: change_x = 'increase'
        if abs(diff_y) < abs(diff_y_last): change_y = 'decrease'
        else: change_y = 'increase'

        word_dist_x = f'dist_x_{dist_x}'
        word_dist_y = f'dist_y_{dist_y}'
        word_change_x = f'dist_x_{change_x}'
        word_change_y = f'dist_y_{change_y}'
            
        dist_x = Task(Judgement(Term(word_dist_x), Stamp(Global.time, Global.time, None, Base((Global.get_input_id(),)))))
        dist_y = Task(Judgement(Term(word_dist_y), Stamp(Global.time, Global.time, None, Base((Global.get_input_id(),)))))
        change_x = Task(Judgement(Term(word_change_x), Stamp(Global.time, Global.time, None, Base((Global.get_input_id(),)))))
        change_y = Task(Judgement(Term(word_change_y), Stamp(Global.time, Global.time, None, Base((Global.get_input_id(),)))))
        return dist_x, dist_y, change_x, change_y


    def step(self, player_x, player_y, ball_x, ball_y):
        ''''''
        result = None, None, None, None
        if self.i_step != 0:
            result = self.percetption(player_x, player_y, ball_x, ball_y, self.player_x_last, self.player_y_last, self.ball_x_last, self.ball_y_last)
        self.player_x_last, self.player_y_last, self.ball_x_last, self.ball_y_last = player_x, player_y, ball_x, ball_y
        self.i_step += 1
        return result


def policy_nars(env: gym.Env):
    ''''''
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
        handle_lines(nars, '100')

    # register operations 
    action: Literal[0, 2, 3] = 0 # 2: left, 0: stop, 3: right
    action_last = action
    term_left = Term('left')
    term_right = Term('right')
    def player_move(arguments: Iterable[Term], task: Task=None, memory: Memory=None):
        ''''''
        direction = arguments[1]
        if direction == term_left:
            action = 2
        elif direction == term_right:
            action = 3

    def player_stop(arguments: Iterable[Term], task: Task=None, memory: Memory=None):
        action = 0

    nars.register_operator('move', player_move)
    nars.register_operator('stop', player_stop)
        
    # begin playing
    i_step = 0
    while not done:
        if action == 0 and random() < 0.08: # random action
            action = sample((0, 2, 3), 1)[0]
        observation, reward, done, info = env.step(action)
        labels = info['labels']
        player_x, player_y = int(labels['player_x']), int(labels['player_y'])
        ball_x, ball_y = int(labels['ball_x']), int(labels['ball_y'])
        if ball_y != 0: # the player and machine are not died
            dist_x, dist_y, change_x, change_y = perceptron.step(player_x, player_y, ball_x, ball_y)
            # info_str = f'obs: {observation.shape}; reward: {reward}; ball: ({ball_x}, {ball_y});'
            # # info_str += f'{dist_x.term if dist_x is not None else None, dist_y.term if dist_y is not None else None, change_x.term if change_x is not None else None, change_y.term if change_y is not None else None}'
            # print(info_str)
            if dist_x is not None:
                nars.perception_channel.put(dist_x)
                nars.perception_channel.put(dist_y)
                nars.perception_channel.put(change_x)
                nars.perception_channel.put(change_y)
            handle_lines(nars, '10')
            # nars.cycles(10)
        else:
            game_reset = Task(Judgement(Statement.Inheritance(Compound.Instance(Term('game')), Compound.Property(Term('reset'))), Stamp(Global.time, Global.time, None, Base((Global.get_input_id(), )))))
            nars.perception_channel.put(game_reset)
        if i_step % 4 == 0:
            goal = Task(Judgement(Term('ball_holded'), Stamp(Global.time, Global.time, None, Base((Global.get_input_id(), ))), truth=Truth(1.00, 0.99, 1))) # remind the system the goal every 4 steps.
            nars.perception_channel.put(goal)

        action_last = action
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