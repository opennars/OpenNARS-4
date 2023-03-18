#!/usr/bin/python3
# *-* encoding:utf8 *_*

import sys
from game_sprites import *
from NARS import *

CREATE_ENEMY_EVENT = pygame.USEREVENT
UPDATE_NARS_EVENT = pygame.USEREVENT + 1
OPENNARS_BABBLE_EVENT = pygame.USEREVENT + 2


class PlaneGame:
    def __init__(self, nars_type):
        print("Game initialization...")
        pygame.init()
        self.game_speed = 1.0  # don't set too large, self.game_speed = 1.0 is the default speed.
        self.fps = 60 * self.game_speed
        self.nars_type = nars_type
        self.screen = pygame.display.set_mode(SCREEN_RECT.size)  # create a display surface, SCREEN_RECT.size=(480,700)
        self.clock = pygame.time.Clock()  # create a game clock
        self.font = pygame.font.SysFont('consolas', 18, True)  # display text like scores, times, etc.
        self.__create_sprites()  # sprites initialization
        self.__create_NARS(self.nars_type)
        self.__set_timer()
        self.score = 0  # hit enemy

    def __set_timer(self):
        CREATE_ENEMY_EVENT_TIMER = 1000
        UPDATE_NARS_EVENT_TIMER = 200
        OPENNARS_BABBLE_EVENT_TIMER = 250
        timer_enemy = int(CREATE_ENEMY_EVENT_TIMER / self.game_speed)
        timer_update_NARS = int(UPDATE_NARS_EVENT_TIMER / self.game_speed)
        timer_babble = int(OPENNARS_BABBLE_EVENT_TIMER / self.game_speed)
        pygame.time.set_timer(CREATE_ENEMY_EVENT, timer_enemy)  # the frequency of creating an enemy
        pygame.time.set_timer(UPDATE_NARS_EVENT, timer_update_NARS)  # the activity of NARS
        pygame.time.set_timer(OPENNARS_BABBLE_EVENT, timer_babble)

    def __create_sprites(self):
        bg1 = Background()
        bg2 = Background(True)
        self.background_group = pygame.sprite.Group(bg1, bg2)
        self.enemy_group = pygame.sprite.Group()
        self.hero = Hero()
        self.hero_group = pygame.sprite.Group(self.hero)

    def __create_NARS(self, type):
        # if type == 'opennars':
        #     self.nars = opennars()
        #     self.remaining_babble_times = 200
        # elif type == 'ONA':
        #     self.nars = ONA()
        #     self.remaining_babble_times = 0
        if type == 'pynars':
            self.nars = PyNARS()
            self.remaining_babble_times = 200

    def start_game(self):
        print("Game start...")
        self.start_time = pygame.time.get_ticks()
        while True:
            self.__event_handler()
            self.__check_collide()
            self.__update_sprites()
            pygame.display.update()
            self.clock.tick(self.fps)

    def __event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.nars.process_kill()
                PlaneGame.__game_over()
            elif event.type == CREATE_ENEMY_EVENT:
                enemy = Enemy()
                self.enemy_group.add(enemy)
            elif event.type == UPDATE_NARS_EVENT:
                self.nars.update(self.hero, self.enemy_group)  # use objects' positions to update NARS's sensors
            elif event.type == OPENNARS_BABBLE_EVENT:
                if self.remaining_babble_times == 0:
                    pygame.event.set_blocked(OPENNARS_BABBLE_EVENT)
                else:
                    self.nars.babble()
                    self.remaining_babble_times -= 1
                    print('The remaining babble times: ' + str(self.remaining_babble_times))
        if self.nars.operation_left:
            self.hero.speed = -4
        elif self.nars.operation_right:
            self.hero.speed = 4
        else:
            self.hero.speed = 0
        if self.nars.operation_fire:
            self.hero.fire()
            self.nars.operation_fire = False

    def __check_collide(self):
        # Several collisions may happen at the same time
        collisions = pygame.sprite.groupcollide(self.hero.bullets, self.enemy_group, True,
                                                True)  # collided=pygame.sprite.collide_circle_ratio(0.8)
        if collisions:
            self.score += len(collisions)  # len(collisions) denotes how many collisions happened
            self.nars.praise()
            print("good")
            print('score: ' + str(self.score))

        collisions = pygame.sprite.spritecollide(self.hero, self.enemy_group, True,
                                                 collided=pygame.sprite.collide_circle_ratio(0.7))
        if collisions:
            # self.score -= len(collisions)
            # self.nars.punish()
            # print("bad")
            pass

    def __update_sprites(self):
        self.background_group.update()
        self.background_group.draw(self.screen)
        self.enemy_group.update()
        self.enemy_group.draw(self.screen)
        self.hero_group.update()
        self.hero_group.draw(self.screen)
        self.hero.bullets.update()
        self.hero.bullets.draw(self.screen)
        self.__display_text()

    def __display_text(self):
        current_time = pygame.time.get_ticks()
        delta_time_s = (current_time - self.start_time) / 1000
        speeding_delta_time_s = delta_time_s * self.game_speed

        if delta_time_s == 0:
            performance = 0
        else:
            performance = self.score / speeding_delta_time_s

        if self.nars.operation_left:
            operation_text = 'move left'
        elif self.nars.operation_right:
            operation_text = 'move right'
        else:
            operation_text = 'stay still'

        surface_time = self.font.render('Time(s): %d' % speeding_delta_time_s, True, [235, 235, 20])
        surface_performance = self.font.render('Performance: %.3f' % performance, True, [235, 235, 20])
        surface_score = self.font.render('Score: %d' % self.score, True, [235, 235, 20])
        surface_fps = self.font.render('FPS: %d' % self.clock.get_fps(), True, [235, 235, 20])
        surface_babbling = self.font.render('Babbling: %d' % self.remaining_babble_times, True, [235, 235, 20])
        surface_nars_type = self.font.render(self.nars_type, True, [235, 235, 20])
        surface_version = self.font.render('v1.0', True, [235, 235, 20])
        surface_operation = self.font.render('Operation: %s' % operation_text, True, [235, 235, 20])
        self.screen.blit(surface_operation, [20, 10])
        self.screen.blit(surface_babbling, [20, 30])
        self.screen.blit(surface_time, [20, 50])
        self.screen.blit(surface_performance, [20, 70])
        self.screen.blit(surface_score, [370, 10])
        self.screen.blit(surface_fps, [370, 30])
        self.screen.blit(surface_nars_type, [5, 680])
        self.screen.blit(surface_version, [435, 680])

    @staticmethod
    def __game_over():
        print("Game over...")
        exit()


if __name__ == '__main__':
    #game = PlaneGame('opennars')  # input 'ONA' or 'opennars'
    game = PlaneGame('pynars')
    # game = PlaneGame(sys.argv[1])
    game.start_game()
