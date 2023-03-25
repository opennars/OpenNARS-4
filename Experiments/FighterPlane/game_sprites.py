'''
Reference:
https://github.com/Noctis-Xu/NARS-FighterPlane
'''
import pygame
import random
from pathlib import Path

image_root = (Path(__file__).parent/'images').absolute()

SCREEN_RECT = pygame.Rect(0, 0, 480, 700)  # the size of game window, Rect(left, top, width, height). left = x, top = y

class GameSprite(pygame.sprite.Sprite):
    def __init__(self, image_name, speed=1):
        super().__init__()
        self.image = pygame.image.load(image_name)
        self.rect = self.image.get_rect()
        self.speed = speed

    def update(self):  # sprite moves downward by default
        self.rect.y += self.speed  # if self.speed > 0, the sprite moves downward


class Background(GameSprite):
    def __init__(self, is_alternative=False):
        super().__init__(image_root/"background.png")
        if is_alternative:
            self.rect.y = -self.rect.height

    def update(self):  # two images are jointed to display in roll
        super().update()  # Background moves downward
        if self.rect.y >= SCREEN_RECT.height:
            self.rect.y = -self.rect.height


class Enemy(GameSprite):
    def __init__(self):
        super().__init__(image_root/"enemy1.png")
        self.speed = random.randint(2, 3)
        self.rect.bottom = 0
        max_x = SCREEN_RECT.width - self.rect.width
        self.rect.x = random.randint(0, max_x)  # the initial x position

    def update(self):
        super().update()
        if self.rect.y >= SCREEN_RECT.height:  # check the bottom boundary
            self.kill()

    def __del__(self):
        # print("enemy died... %s" % self.rect)
        pass


class Hero(GameSprite):
    def __init__(self):
        super().__init__(image_root/"me1.png", 0)
        self.rect.centerx = SCREEN_RECT.centerx
        self.rect.bottom = SCREEN_RECT.bottom
        self.bullets = pygame.sprite.Group()

    def update(self):
        self.rect.x += self.speed  # move horizontally. If self.speed > 0, move right
        if self.rect.x < 0:  # check the left boundary
            self.rect.x = 0
        elif self.rect.right > SCREEN_RECT.right:  # check the right boundary
            self.rect.right = SCREEN_RECT.right

    def fire(self):
        # print("fire")
        for i in [0]:
            bullet = Bullet(-50)
            bullet.rect.bottom = self.rect.top - i * 20  # bullet's initial position
            bullet.rect.centerx = self.rect.centerx
            self.bullets.add(bullet)


class Bullet(GameSprite):
    def __init__(self, speed=-2):
        super().__init__(image_root/"bullet1.png", speed)

    def update(self):
        super().update()
        if self.rect.bottom < 0:  # check boundary
            self.kill()

    def __del__(self):
        # print("Bullet is destroyed...")
        pass
