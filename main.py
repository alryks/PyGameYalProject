import pygame
from pygame.locals import *

import sys
import os
import shutil

from PIL import Image

import random

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
    img_new = img.resize((int(img_width * size), int(img_height * size)))
    to_save = os.path.join(os.path.join("img", "temp"), name)
    create_temp()
    img_new.save(to_save)


# FPS counter


def update_fps():
    fps = str(int(clock.get_fps()))
    font = pygame.font.SysFont("Verdana", 18)
    fps_text = font.render(fps, 1, pygame.Color("green"))
    return fps_text


class Spaceship(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)
        scale_image("spaceship.png", size=width / 12 / 1000)
        sprite_img = load_image(os.path.join("temp", "spaceship.png"))
        self.image = sprite_img
        self.rect = self.image.get_rect()
        self.rect.x = width // 2 - self.rect.width // 2
        self.rect.y = height // 2 - self.rect.height // 2

    def update(self, *args):
        self.rect.x = args[0]
        self.rect.y = args[1]


if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption('not enough SPACE')
    size = pygame.display.get_desktop_sizes()[0]
    # size = width, height = size[0] // 2, size[1] // 2
    size = width, height = 1920, 1080
    flags = DOUBLEBUF
    screen = pygame.display.set_mode(size, flags)
    screen.set_alpha(None)

    ''

    all_sprites = pygame.sprite.Group()
    spaceship = Spaceship(all_sprites)
    v = 0
    a = 0
    x = spaceship.rect.x
    y = spaceship.rect.y

    ''

    running = True
    clock = pygame.time.Clock()
    fps = 144
    while running:

        screen.fill('#111122')
        screen.blit(update_fps(), (width - 40, 10))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    a = height // (fps / 4)
                elif event.key == pygame.K_RIGHT:
                    a = -height // (fps / 4)
            if event.type == pygame.KEYUP:
                a = 0

        ''

        all_sprites.draw(screen)

        v += a * clock.tick() / 1000
        y += v

        all_sprites.update(int(x), int(y))

        ''

        pygame.display.flip()

        ''

        ''

        clock.tick(fps)
    pygame.quit()

delete_temp()
