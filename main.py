import pygame
from pygame.locals import *

import sys
import os
import shutil

from PIL import Image

import random
import math

import sqlite3

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
    image = pygame.image.load(fullname).convert_alpha()
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


'''
DB
'''


def db_get():
    con = sqlite3.connect('db.db')
    cur = con.cursor()
    res = cur.execute('SELECT score FROM score').fetchall()[0][0]
    con.close()
    return res


def db_post(n):
    if os.path.exists('db.db'):
        if n > db_get():
            con = sqlite3.connect('db.db')
            cur = con.cursor()
            cur.execute(f'UPDATE score SET score = {n}')
            con.commit()
            con.close()
    else:
        f = open('db.db', 'w')
        f.close()
        con = sqlite3.connect('db.db')
        cur = con.cursor()
        cur.execute('CREATE TABLE score (score INTEGER);')
        cur.execute(f'INSERT INTO score (score) VALUES({n})')
        con.commit()
        con.close()


'''
FPS counter
'''


def update_fps():
    fpss = str(int(clock.get_fps()))
    font = pygame.font.SysFont("Verdana", 18)
    fps_text = font.render(fpss, True, pygame.Color("green"))
    return fps_text


'''
Preferences
'''


def load_prefs():
    global size
    global fps
    global width
    global height
    with open("preferences.txt") as prefs:
        size = width, height = tuple(int(num) for num in
                                prefs.readline().split("x"))
        fps = int(prefs.readline())


def change_prefs(text):
    global size
    global fps
    global width
    global height
    with open("preferences.txt", "w") as prefs:
        prefs.write(text + '\n' + str(fps))


'''
Terminate
'''


def terminate():
    pygame.quit()
    sys.exit()


'''
Classes for game
'''


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__(all_sprites)
        self.add(obstacles)

        images = ["meteor_small.png",
                  "meteor_big.png",
                  "blue_planet.png",
                  "black_planet.png",
                  "saturn_planet.png"]
        chosen_image = random.choice(images)
        scale_image(chosen_image, size=height / 1080)
        self.sprite_img = load_image(os.path.join("temp", chosen_image))
        self.image = self.sprite_img
        self.rect = self.image.get_rect()

        self.width = self.rect.width

        self.rect.x = random.randint(
            int(width / 16 * 3.5), width - int(width / 16 * 3.5) - self.width)
        self.rect.y = -height // 4

        self.x = self.rect.x
        self.y = self.rect.y
        self.speed = speed

        self.w = 2
        self.angle = 0

        self.d = 0

    def update(self, *args):
        self.speed = args[2]
        self.angle += self.w * spaceship.go

        self.y += self.speed / fps * spaceship.go
        self.rect.y = int(self.y)

        self.image = pygame.transform.rotate(self.sprite_img, self.angle)
        self.rect = self.image.get_rect()
        self.d = (self.rect.width - self.width) // 2
        self.rect.x = int(self.x) - self.d
        self.rect.y = int(self.y) - self.d

        if pygame.sprite.collide_mask(self, spaceship):
            spaceship.go = False
        if self.rect.y > height:
            self.kill()

        return 1


class Border(pygame.sprite.Sprite):
    def __init__(self, x1, y1, x2, y2):
        super().__init__(all_sprites)
        self.add(borders)

        self.image = pygame.Surface([abs(x2 - x1), abs(y2 - y1)])
        self.image.fill('#11111A')
        self.rect = pygame.Rect(x1, y1, x2 - x1, y2 - y1)

    def update(self, *args):
        if pygame.sprite.collide_mask(self, spaceship):
            spaceship.go = False


class Spaceship(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)

        scale_image("spaceship.png", size=height / 1080)
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
        self.w += self.aw / 50 * self.go
        self.angle += self.w / 50 * self.go
        angle_rad = self.angle / 360 * 2 * pi * self.go

        self.v = [self.v[0] - self.a / fps * math.sin(angle_rad),
                  self.v[1] - self.a / fps * math.cos(angle_rad)]
        self.x += self.v[0] * self.go
        self.y += self.v[1] * self.go

        self.image = pygame.transform.rotate(self.sprite_img, self.angle)
        self.rect = self.image.get_rect()
        self.d = (self.rect.width - self.width) // 2
        self.rect.x = int(self.x) - self.d
        self.rect.y = int(self.y) - self.d

    def changes(self, event):
        if event.type == pygame.KEYDOWN and self.go:
            if event.key in [pygame.K_LEFT, pygame.K_a]:
                self.aw = 1 / fps * 150 / (2 * pi) * 360
            elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                self.aw = -1 / fps * 150 / (2 * pi) * 360
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.a = -height / fps / 3
            elif event.key in [pygame.K_UP, pygame.K_w]:
                self.a = height / fps / 3
        if event.type == pygame.KEYUP and self.go:
            if event.key in [pygame.K_LEFT, pygame.K_RIGHT,
                             pygame.K_a, pygame.K_d]:
                self.aw = 0
            elif event.key in [pygame.K_DOWN, pygame.K_UP,
                               pygame.K_s, pygame.K_w]:
                self.a = 0


'''
Classes for menu
'''


class Button(pygame.sprite.Sprite):
    def __init__(self, text, pos):
        super().__init__(btns)
        self.font = pygame.font.SysFont("Trebuchet MS", int(60 * height / 1080), True)
        self.color = '#CCCCCC'
        self.text = text
        self.pos = self.x, self.y = pos
        self.string_rendered = self.font.render(self.text, True, self.color)
        self.rect = self.string_rendered.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        self.is_focused = False

    def update(self, *args):
        self.rect.y = self.y
        pos, clicked = args[0], args[1]
        self.is_focused = self.rect.x <= pos[0] <= self.rect.x + self.rect.w and self.rect.y <= pos[1] <= self.rect.y + self.rect.h
        if self.is_focused:
            self.color = '#AAAAAA'
            self.rect.y += 2
        else:
            self.color = '#CCCCCC'
        if self.is_focused and clicked:
            raise ScreenChange(self.text)
        self.string_rendered = self.font.render(self.text, True, self.color)
        screen.blit(self.string_rendered, self.rect)


class Choose(pygame.sprite.Sprite):
    def __init__(self, text, pos, i):
        super().__init__(choose)
        self.font = pygame.font.SysFont("Trebuchet MS", int(60 * height / 1080), True)
        self.color = '#CCCCCC'
        self.text = text
        self.pos = self.x, self.y = pos
        self.i = i
        self.string_rendered = self.font.render(self.text, True, self.color)
        self.rect = self.string_rendered.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        self.is_focused = False

    def update(self, *args):
        self.rect.y = self.y
        pos, clicked = args[0], args[1]
        self.is_focused = self.rect.x - int(60 * height / 1080) <= pos[0] <= self.rect.x + self.rect.w and self.rect.y <= pos[1] <= self.rect.y + self.rect.h
        if self.is_focused and clicked:
            pygame.draw.circle(screen, self.color, (self.rect.x - int(30 * height / 1080), self.rect.y + self.rect.h // 2), int(10 * height / 1080))
            if self.i < 3:
                chooses[0] = 0
                chooses[1] = 0
                chooses[2] = 0
            else:
                chooses[3] = 0
                chooses[4] = 0
            chooses[self.i] = 1
            if self.text == 'FULLSCREEN':
                flags = DOUBLEBUF | FULLSCREEN
                change_prefs('x'.join(list(map(str, list(pygame.display.get_desktop_sizes()[0])))))
            else:
                flags = DOUBLEBUF
                change_prefs(self.text)
            load_prefs()
            pygame.display.set_mode(size, flags)
        if chooses[self.i]:
            pygame.draw.circle(screen, self.color, (self.rect.x - int(30 * height / 1080), self.rect.y + self.rect.h // 2), int(10 * height / 1080))
        self.string_rendered = self.font.render(self.text, True, self.color)
        screen.blit(self.string_rendered, self.rect)
        pygame.draw.circle(screen, self.color, (self.rect.x - int(30 * height / 1080), self.rect.y + self.rect.h // 2), int(15 * height / 1080), int(3 * height / 1080))


class ScreenChange(Exception):
    def __init__(self, screen):
        self.screen = screen


'''
Parts of the game
'''


def start_screen():
    if chooses[0] == 1:
        flags = DOUBLEBUF | FULLSCREEN
        change_prefs('x'.join(
            list(map(str, list(pygame.display.get_desktop_sizes()[0])))))
        load_prefs()
        pygame.display.set_mode(size, flags)

    b_play = Button('PLAY', (int(height / 1080 * 1280), int(height / 1080 * 120)))
    b_settings = Button('SETTINGS', (int(height / 1080 * 1280), int(height / 1080 * 220)))
    b_help = Button('HELP', (int(height / 1080 * 1280), int(height / 1080 * 320)))
    b_quit = Button('QUIT GAME', (int(height / 1080 * 1280), height - int(height / 1080 * 180)))

    running = True

    pos = (0, 0)

    while running:
        clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEMOTION:
                pos = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN:
                clicked = True

        screen.fill("#11111A")
        try:
            all_sprites.update(pos, clicked)
            btns.update(pos, clicked)
        except ScreenChange as e:
            return e.screen
        pygame.draw.rect(screen, "#CCCCCC", (int(height / 1080 * 120), int(height / 1080 * 120), int(height / 1080 * 1080), height - 2 * int(height / 1080 * 120)), 5)

        pygame.display.flip()
        clock.tick(fps)


def help_screen():
    if chooses[0] == 1:
        flags = DOUBLEBUF | FULLSCREEN
        change_prefs('x'.join(
            list(map(str, list(pygame.display.get_desktop_sizes()[0])))))
        load_prefs()
        pygame.display.set_mode(size, flags)

    b_back = Button('BACK', (int(height / 1080 * 120), int(height / 1080 * 60)))

    running = True

    pos = (0, 0)

    text_y = 180
    font = pygame.font.SysFont("Trebuchet MS", int(30 * height / 1080), True, True)
    text1 = font.render('This game is about a spaceship lost in space.', True, '#CCCCCC')
    text2 = font.render('The only goal is to stay alive.', True, '#CCCCCC')
    text3 = font.render('To turn around yourself use A / Left and D / Right. To go forwards and backwards use W / Up and S / Down.', True, '#CCCCCC')
    text4 = font.render('To play press PLAY. If you lose, press BACK to go back to the main menu or RESTART to restart.', True, '#CCCCCC')
    text5 = font.render('To change settings press SETTINGS. To quit the game press QUIT GAME.', True, '#CCCCCC')

    created_by = font.render('Created by: SKLYAR NIKITA & SHELIPOVA VALERIA & TOKAREV FEDOR', True, '#CCCCCC')

    while running:
        clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEMOTION:
                pos = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN:
                clicked = True

        screen.fill("#111122")
        try:
            all_sprites.update(pos, clicked)
            btns.update(pos, clicked)
        except ScreenChange as e:
            return e.screen

        pygame.draw.rect(screen, '#CCCCCC', (height / 1080 * 120, height / 1080 * 140, height / 1080 * 240, height / 1080 * 6), 0)
        pygame.draw.rect(screen, '#CCCCCC', (height / 1080 * 120, height / 1080 * 940, height / 1080 * 240, height / 1080 * 6), 0)

        screen.blit(text1, (height / 1080 * 120, height / 1080 * text_y))
        screen.blit(text2, (height / 1080 * 120, height / 1080 * (text_y + 50)))
        screen.blit(text3, (height / 1080 * 120, height / 1080 * (text_y + 150)))
        screen.blit(text4, (height / 1080 * 120, height / 1080 * (text_y + 250)))
        screen.blit(text5, (height / 1080 * 120, height / 1080 * (text_y + 300)))
        screen.blit(created_by, (height / 1080 * 120, height / 1080 * 960))

        pygame.display.flip()
        clock.tick(fps)


def settings_screen():
    b_back = Button('BACK', (int(height / 1080 * 120), int(height / 1080 * 60)))

    choose_fullscreen = Choose('FULLSCREEN', (int(height / 1080 * 165), int(height / 1080 * 280)), 0)
    choose_fullhd = Choose('1920x1080', (int(height / 1080 * 665), int(height / 1080 * 280)), 1)
    choose_hd = Choose('1280x720', (int(height / 1080 * 1165), int(height / 1080 * 280)), 2)

    running = True

    pos = (0, 0)

    text_y = 200
    # text2 = font.render('Show FPS?', True, '#CCCCCC')

    while running:
        font = pygame.font.SysFont("Trebuchet MS", int(30 * height / 1080), True, True)
        text1 = font.render('Choose resolution', True, '#CCCCCC')
        clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                change_prefs('1280x720')
                terminate()
            elif event.type == pygame.MOUSEMOTION:
                pos = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN:
                clicked = True

        screen.fill("#111122")
        try:
            all_sprites.update(pos, clicked)
            btns.update(pos, clicked)
        except ScreenChange as e:
            return e.screen

        choose.update(pos, clicked)

        b_back.kill()
        choose_fullscreen.kill()
        choose_fullhd.kill()
        choose_hd.kill()

        b_back = Button('BACK',
                        (int(height / 1080 * 120), int(height / 1080 * 60)))

        choose_fullscreen = Choose('FULLSCREEN', (
        int(height / 1080 * 165), int(height / 1080 * 280)), 0)
        choose_fullhd = Choose('1920x1080', (
        int(height / 1080 * 665), int(height / 1080 * 280)), 1)
        choose_hd = Choose('1280x720', (
        int(height / 1080 * 1165), int(height / 1080 * 280)), 2)

        pygame.draw.rect(screen, '#CCCCCC', (height / 1080 * 120, height / 1080 * 140, height / 1080 * 240, height / 1080 * 6), 0)

        screen.blit(text1, (height / 1080 * 120, height / 1080 * text_y))
        # screen.blit(text2, (height / 1080 * 120, height / 1080 * (text_y + 250)))

        pygame.display.flip()
        clock.tick(fps)


def game_screen():
    if chooses[0] == 1:
        flags = DOUBLEBUF | FULLSCREEN
        change_prefs('x'.join(
            list(map(str, list(pygame.display.get_desktop_sizes()[0])))))
        load_prefs()
        pygame.display.set_mode(size, flags)

    db_post(0)
    btn_back = Button('BACK', (int(height / 1080 * 60), int(height / 1080 * 60)))
    btn_restart = Button('RESTART', (int(height / 1080 * 60), int(height / 1080 * 160)))
    btn_help = Button('HELP', (int(height / 1080 * 60), int(height / 1080 * 260)))

    Border(0, 0, int(width / 16 * 3.5), height)
    Border(width - int(width / 16 * 3.5), 0, width, height)
    Border(0, -height, width, 0)
    Border(0, height, width, 2 * height)

    a = height / fps / 3
    speed = height / 10

    time = 0
    difficulty = 1.5
    score = 0

    pos = (0, 0)

    bg_y = 0

    flag = False

    screen2 = pygame.Surface((width, height))
    screen2.set_alpha(120)
    screen2.fill((0, 0, 0))

    font = pygame.font.SysFont("Trebuchet MS", int(30 * height / 1080), True)
    score_text = font.render('SCORE', True, '#CCCCCC')

    running = True

    while running:
        clicked = False

        screen.fill('#111122')

        bg_y += height / 10 / fps

        if bg_y > height:
            bg_y = 0

        main_bg_rect.y = int(bg_y)
        screen.blit(main_bg, main_bg_rect)

        main_bg_rect.y = int(bg_y) - height
        screen.blit(main_bg, main_bg_rect)

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                db_post(score)
                delete_temp()
                terminate()
            elif event.type == pygame.MOUSEMOTION:
                pos = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN:
                clicked = True
            spaceship.changes(event)

        speed += a / fps
        time += 1 / fps

        if time > difficulty and spaceship.go:
            for i in range(int(time // difficulty)):
                Obstacle(speed)
            score += int(time // difficulty)
            time = 0

        all_sprites.update(pos, clicked, speed)
        all_sprites.draw(screen)

        screen.blit(update_fps(), (width - 40, 10))

        screen.blit(score_text, ((width - height) // 2 + height + height / 1080 * 180, height / 1080 * 60))

        font = pygame.font.SysFont("Trebuchet MS", int(120 * height / 1080), True)
        score_text_score = font.render(str(score) if len(str(score)) >= 2 else ' ' + str(score), True, '#CCCCCC')
        screen.blit(score_text_score, ((width - height) // 2 + height + height / 1080 * 150, height / 1080 * 120))

        font = pygame.font.SysFont("Trebuchet MS", int(30 * height / 1080), True)
        highest = font.render('HIGHEST SCORE', True, '#CCCCCC')
        screen.blit(highest, ((width - height) // 2 + height + height / 1080 * 120, height / 1080 * 360))

        font = pygame.font.SysFont("Trebuchet MS", int(120 * height / 1080), True)
        highest_score = font.render(str(db_get()) if len(str(db_get())) >= 2 else ' ' + str(db_get()), True, '#CCCCCC')
        screen.blit(highest_score, ((width - height) // 2 + height + height / 1080 * 150, height / 1080 * 400))

        if spaceship.go == False:
            if not flag:
                Button('BACK', (int(height / 1080 * 720), int(height / 1080 * 510)))
                Button('RESTART', (int(height / 1080 * 960), int(height / 1080 * 510)))
                flag = True
            btn_back.kill()
            btn_restart.kill()
            btn_help.kill()
            screen.blit(screen2, screen2.get_rect())

        try:
            btns.update(pos, clicked)
        except ScreenChange as e:
            db_post(score)
            delete_temp()
            return e.screen

        pygame.display.flip()
        clock.tick(fps)

    delete_temp()


if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption('not enough SPACE')
    load_prefs()
    flags = DOUBLEBUF
    screen = pygame.display.set_mode(size, flags)
    screen.set_alpha(None)

    ''

    where_to_go = 'START'
    chooses = [0, 0, 1, 1, 0]

    while where_to_go != 'QUIT GAME':
        load_prefs()
        screen = pygame.display.set_mode(size, flags)
        screen.set_alpha(None)

        clock = pygame.time.Clock()
        all_sprites = pygame.sprite.Group()
        btns = pygame.sprite.Group()
        choose = pygame.sprite.Group()

        if where_to_go == 'START' or where_to_go == 'BACK':
            where_to_go = start_screen()
        elif where_to_go == 'PLAY' or where_to_go == 'RESTART':
            borders = pygame.sprite.Group()
            obstacles = pygame.sprite.Group()
            spaceship = Spaceship()

            scale_image("main_bg.png", size=height / 1080)
            main_bg = load_image(os.path.join("temp", "main_bg.png"))
            main_bg_rect = main_bg.get_rect()
            main_bg_rect.x = (width - height) // 2
            main_bg_rect.y = 0

            where_to_go = game_screen()
        elif where_to_go == 'HELP':
            where_to_go = help_screen()
        elif where_to_go == 'SETTINGS':
            where_to_go = settings_screen()
