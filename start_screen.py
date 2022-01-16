import pygame
import sys
import os


pygame.init()
with open("preferences.txt") as prefs:
    size = width, height = [int(num) for num in prefs.readline().split(", ")]
rsz = width / 1080
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
FPS = 60


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def terminate():
    pygame.quit()
    sys.exit()


class Button:
    font = pygame.font.SysFont("Trebuchet MS", 30, True)
    padding = (rsz * 750, rsz * 100, rsz * 0, rsz * 80, rsz * 10, rsz * 100)  # x, y, shiftx, shifty, focus_expand, last

    def __init__(self, text, pos, last=False):
        self.text = text
        self.pos = pos
        self.rect = pygame.rect.Rect([0, 0, 0, 0])
        self.is_focused = False
        self.is_last = last

    def update(self, pos, clicked):
        self.is_focused = self.rect.x <= pos[0] <= self.rect.x + self.rect.w and \
                          self.rect.y <= pos[1] <= self.rect.y + self.rect.h
        if self.is_focused and clicked:
            raise ScreenChange(self.text)

    def render(self):
        string_rendered = Button.font.render(self.text, True, "#cccccc")
        self.rect = string_rendered.get_rect()
        self.rect.x = Button.padding[0] + Button.padding[2] * self.pos
        self.rect.y = Button.padding[1] + Button.padding[3] * self.pos + self.is_last * Button.padding[5]

        if self.is_focused:
            border_rect = [self.rect.x - Button.padding[4], self.rect.y - Button.padding[4],
                           self.rect.w + Button.padding[4] * 2, self.rect.h + Button.padding[4] * 2]
            pygame.draw.rect(screen, "#dddddd", border_rect, 5)

        screen.blit(string_rendered, self.rect)


class ScreenChange(Exception):
    def __init__(self, screen):
        self.screen = screen


def start_screen():
    btn_texts = ["PLAY",
                 "LEADERBOARD",
                 "SETTINGS",
                 "HELP",
                 "EXIT GAME"]
    demo_rect = (rsz * 10, rsz * 10, width // 1.5 - rsz * 10 * 2, height - rsz * 10 * 2)
    buttons = [Button(btn_texts[i], i, i == len(btn_texts) - 1) for i in range(len(btn_texts))]
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
                try:
                    for btn in buttons:
                        btn.update(event.pos, event.type == pygame.MOUSEBUTTONDOWN)
                except ScreenChange as e:
                    return e.screen

        screen.fill("#111122")
        pygame.draw.rect(screen, "#cccccc", demo_rect, 5)

        for btn in buttons:
            btn.render()

        pygame.display.flip()
        clock.tick(FPS)
