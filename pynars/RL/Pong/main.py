'''
Pong-v0

Maximize your score in the Atari 2600 game Pong. In this environment, the observation is an RGB image of the screen, which is an array of shape (210, 160, 3) Each action is repeatedly performed for a duration of kk frames, where kk is uniformly sampled from {2,3,4}.

See:

    [1] https://gym.openai.com/envs/Pong-v0/

'''

from typing_extensions import Literal
import gym
from atariari.benchmark.wrapper import AtariARIWrapper
from time import sleep

rander_mode: Literal['human'] = 'human'

def policy_random(env: gym.Env):
    ''''''
    env.reset()
    # env.render()
    env.reset()
    done = False
    while not done:
        action = env.action_space.sample()
        action = 0
        observation, reward, done, info = env.step(action)
        print('obs: {}; reward: {}'.format(observation.shape, reward))
        # env.render()
        # sleep(0.02)
        

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

    policy_random(env)


if __name__ == '__main__':
    run()