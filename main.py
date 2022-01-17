import pygame
from pygame.locals import *

import sys
import os
import shutil

from PIL import Image

import random
import math

import start_screen


'''
CONSTANTS
'''

pi = math.pi

'''
Functions for images
'''


# Loading images


def load_image(name):
    fullname = os.path.join("img", name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


# Creating temporary folder for edited images


def create_temp():
    newpath = os.path.join("img", "temp")
    if not os.path.exists(newpath):
        os.makedirs(newpath)


# Deleting temporary folder for edited images


def delete_temp():
    path = os.path.join("img", "temp")
    if os.path.exists(path):
        shutil.rmtree(path)


# Scaling images


def scale_image(name, size=1.0):
    fullname = os.path.join("img", name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    img = Image.open(fullname)
    img_width, img_height = img.size
    img_scale = img.resize((int(img_width * size), int(img_height * size)))
    to_save = os.path.join(os.path.join("img", "temp"), name)
    create_temp()
    img_scale.save(to_save)
    img.close()


# FPS counter


def update_fps():
    # fps = str(int(clock.get_fps()))
    fps = str(1000 // tick)
    font = pygame.font.SysFont("Verdana", 18)
    fps_text = font.render(fps, 1, pygame.Color("green"))
    return fps_text


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.add(obstacles)
        self.image = load_image(os.path.join("temp", "spaceship.png"))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(int(width / 16 * 3.5), width - int(width / 16 * 3.5))
        self.rect.y = y
        self.x = x
        self.y = y
        self.speed = height / 10

    def update(self, *args):
        self.y += self.speed / fps
        self.rect.y = int(self.y)

        if pygame.sprite.collide_mask(self, spaceship):
            spaceship.v = [0, 0]
            spaceship.a = 0
            spaceship.d = 0

            spaceship.aw = 0
            spaceship.w = 0

            spaceship.go = False

            self.speed = 0


class Border(pygame.sprite.Sprite):
    def __init__(self, x1, y1, x2, y2):
        super().__init__(all_sprites)
        self.add(borders)
        self.image = pygame.Surface([abs(x2 - x1), abs(y2 - y1)])
        self.image.fill('#333333')
        self.rect = pygame.Rect(x1, y1, x2 - x1, y2 - y1)

    def update(self, *args):
        if pygame.sprite.collide_mask(self, spaceship):
            spaceship.v = [0, 0]
            spaceship.a = 0
            spaceship.d = 0

            spaceship.aw = 0
            spaceship.w = 0

            for sprite in obstacles:
                sprite.speed = 0

            spaceship.go = False


class Spaceship(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)
        scale_image("spaceship.png", size=width / 10 / 1000)
        self.sprite_img = load_image(os.path.join("temp", "spaceship.png"))
        self.image = self.sprite_img
        self.rect = self.image.get_rect()
        self.rect.x = width // 2 - self.rect.width // 2
        self.rect.y = height // 6 * 5

        self.width = self.rect.width
        self.go = True

        self.v = [0, 0]
        self.a = 0
        self.x = self.rect.x
        self.y = self.rect.y
        self.d = 0

        self.aw = 0
        self.w = 0
        self.angle = 0

    def update(self, *args):
        self.w += self.aw / 50
        self.angle += self.w / 50
        angle_rad = self.angle / 360 * 2 * pi

        self.v = [self.v[0] - self.a * tick / 1000 * math.sin(angle_rad),
                  self.v[1] - self.a * tick / 1000 * math.cos(angle_rad)]
        self.x += self.v[0]
        self.y += self.v[1]

        self.image = pygame.transform.rotate(self.sprite_img, self.angle)
        self.rect = self.image.get_rect()
        self.d = (self.rect.width - self.width) // 2
        self.rect.x = int(self.x) - self.d
        self.rect.y = int(self.y) - self.d

    def changes(self, type):
        if type == pygame.KEYDOWN and self.go:
            if event.key in [pygame.K_LEFT, pygame.K_a]:
                self.aw = 1 * tick / 1000 * 100 / (2 * pi) * 360
            elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                self.aw = -1 * tick / 1000 * 100 / (2 * pi) * 360
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.a = -height * tick / 1000 / 3
            elif event.key in [pygame.K_UP, pygame.K_w]:
                self.a = height * tick / 1000 / 3
        if type == pygame.KEYUP and self.go:
            if event.key in [pygame.K_LEFT, pygame.K_RIGHT,
                             pygame.K_a, pygame.K_d]:
                self.aw = 0
            elif event.key in [pygame.K_DOWN, pygame.K_UP,
                               pygame.K_s, pygame.K_w]:
                self.a = 0


if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption('not enough SPACE')
    size = pygame.display.get_desktop_sizes()[0]
    # size = width, height = size[0] // 2, size[1] // 2
    with open("preferences.txt") as prefs:
        size = width, height = [int(num) for num in prefs.readline().split(", ")]
    flags = DOUBLEBUF
    screen = pygame.display.set_mode(size, flags)
    screen.set_alpha(None)

    ''

    all_sprites = pygame.sprite.Group()

    borders = pygame.sprite.Group()
    Border(0, 0, int(width / 16 * 3.5), height)
    Border(width - int(width / 16 * 3.5), 0, width, height)
    Border(0, -height, width, 0)
    Border(0, height, width, 2 * height)

    spaceship = Spaceship()

    obstacles = pygame.sprite.Group()
    Obstacle(0, 0)

    ''

    running = True
    clock = pygame.time.Clock()
    fps = 60

    start_screen.width = width
    start_screen.height = height
    start_screen.rsz = height / 1080
    where_to_go = start_screen.start_screen()

    while running:
        tick = clock.tick(fps)
        screen.fill('#111122')

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            spaceship.changes(event.type)

        all_sprites.draw(screen)
        all_sprites.update()
        screen.blit(update_fps(), (width - 40, 10))

        pygame.display.flip()

    pygame.quit()

delete_temp()
