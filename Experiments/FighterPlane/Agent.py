'''
Reference:
https://github.com/Noctis-Xu/NARS-FighterPlane
'''
import threading
import queue
import subprocess
import random
import signal
from pynars.NARS.Control.Reasoner import Reasoner
from time import time

class Agent:
    def __init__(self):  # nars_type: 'opennars' or 'ONA'
        self.inference_cycle_frequency = 1  # set too large will get delayed and slow down the game
        self.operation_left = False
        self.operation_right = False
        self.operation_fire = False

        self.core = Reasoner(100, 100)
        # if operation == '^left':
        #     self.move_left()
        # elif operation == '^right':
        #     self.move_right()
        # elif operation == '^deactivate':
        #     self.dont_move()
        # elif operation == '^fire':
        #     self.fire()
        self.core.register_operator('left', self.move_left)
        self.core.register_operator('right', self.move_right)
        self.core.register_operator('deactivate', self.dont_move)
        self.core.register_operator('fire', self.fire)
        self.inference_cycle_frequency = 5


    def add_inference_cycles(self, num):
        t1 = time()
        for _ in range(num):
            tasks_derived, judgement_revised, goal_revised, answers_question, answers_quest, (
            task_operation_return, task_executed) = self.core.cycle()
            if len(tasks_derived) > 0:
                for task in tasks_derived:
                    print(task)
            if task_operation_return is not None and len(task_operation_return) > 0:
                print("task_operation_return")
            if task_executed is not None:
                print(task_executed)
        t2 = time()
        # print(f"time: {t2-t1}")

    def update(self, hero, enemy_group):  # update sensors (object positions), remind goals, and make inference
        self.update_sensors(hero, enemy_group)
        self.remind_goal()
        self.remind_knowledge()
        self.add_inference_cycles(self.inference_cycle_frequency)

    def update_sensors(self, hero, enemy_group):
        enemy_left = False
        enemy_right = False
        enemy_ahead = False
        for enemy in enemy_group.sprites():
            if enemy.rect.right < hero.rect.centerx:
                enemy_left = True
            elif hero.rect.centerx < enemy.rect.left:
                enemy_right = True
            else:  # enemy.rect.left <= hero.rect.centerx and hero.rect.centerx <= enemy.rect.right
                enemy_ahead = True
        if enemy_left:
            # self.add_to_cmd('<{enemy} --> [left]>. :|:')
            self.core.input_narsese('<{enemy} --> [left]>. :|:')
        if enemy_right:
            # self.add_to_cmd('<{enemy} --> [right]>. :|:')
            self.core.input_narsese('<{enemy} --> [right]>. :|:')
        if enemy_ahead:
            # self.add_to_cmd('<{enemy} --> [ahead]>. :|:')
            self.core.input_narsese('<{enemy} --> [ahead]>. :|:')

    def move_left(self, *args):  # NARS gives <(*,{SELF}) --> ^left>. :|:
        self.operation_left = True
        self.operation_right = False
        print('move left')

    def move_right(self, *args):  # NARS gives <(*,{SELF}) --> ^right>. :|:
        self.operation_left = False
        self.operation_right = True
        print('move right')

    def dont_move(self, *args):  # NARS gives <(*,{SELF}) --> ^deactivate>. :|:
        self.operation_left = False
        self.operation_right = False
        print('stay still')

    def fire(self, *args):  # NARS gives <(*,{SELF}) --> ^strike>. :|:
        self.operation_fire = True
        print('fire')

    def remind_knowledge(self):
        ''''''
        # self.core.input_narsese('< (&/, <{enemy} --> [left]>, (&/, <(*,{SELF}) --> ^left>, <(*,{SELF}) --> ^fire>)) =/> <{SELF} --> [good]>>.')
        # self.core.input_narsese('< (&/, <{enemy} --> [right]>, (&/, <(*,{SELF}) --> ^right>), <(*,{SELF}) --> ^fire>) =/> <{SELF} --> [good]>>.')
        self.core.input_narsese('< (&/, <{enemy} --> [left]>, <(*,{SELF}) --> ^left>) =/> <{SELF} --> [good]>>. :|:')
        self.core.input_narsese('< (&/, <{enemy} --> [right]>, <(*,{SELF}) --> ^right>) =/> <{SELF} --> [good]>>. :|:')
        self.core.input_narsese('< (&/, <{enemy} --> [ahead]>, <(*,{SELF}) --> ^fire>) =/> <{SELF} --> [good]>>. :|:')
        # self.core.input_narsese('<(*,{SELF}) --> ^fire>! :|:')

    def remind_goal(self):
        # self.add_to_cmd('<{SELF} --> [good]>! :|:')
        self.core.input_narsese('<{SELF} --> [good]>! :|:')

    def praise(self):
        # self.add_to_cmd('<{SELF} --> [good]>. :|:')
        self.core.input_narsese('<{SELF} --> [good]>. :|:')

    def punish(self):
        # self.add_to_cmd('(--,<{SELF} --> [good]>). :|:')
        self.core.input_narsese('(--,<{SELF} --> [good]>). :|:')


    def babble(self):
        rand_int = random.randint(1, 7)
        if rand_int == 1:
            self.move_left()
            # self.add_to_cmd('<(*,{SELF}) --> ^left>. :|:')
            self.core.input_narsese('<(*,{SELF}) --> ^left>. :|:')
        if rand_int == 2:
            self.move_right()
            # self.add_to_cmd('<(*,{SELF}) --> ^right>. :|:')
            self.core.input_narsese('<(*,{SELF}) --> ^right>. :|:')
        if rand_int == 3:
            self.dont_move()
            # self.add_to_cmd('<(*,{SELF}) --> ^deactivate>. :|:')
            self.core.input_narsese('<(*,{SELF}) --> ^deactivate>. :|:')
        else:
            self.fire()
            # self.add_to_cmd('<(*,{SELF}) --> ^strike>. :|:')
            self.core.input_narsese('<(*,{SELF}) --> ^strike>. :|:')

    def read_line(self, out):  # read line without blocking
        for line in iter(out.readline, b'\n'):  # get operations
            if line[0:3] == 'EXE':
                subline = line.split(' ', 2)[2]
                operation = subline.split('(', 1)[0]
                if operation == '^left':
                    self.move_left()
                elif operation == '^right':
                    self.move_right()
                elif operation == '^deactivate':
                    self.dont_move()
                elif operation == '^strike':
                    self.fire()
        out.close()

        

    