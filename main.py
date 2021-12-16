import pygame


KEYS = {1073741903: [1, 0], 1073741904: [-1, 0], 1073741905: [0, 1], 1073741906: [0, -1]}


class Player:
    def __init__(self, screen):
        self.screen = screen
        self.pos = [screen.get_width() // 2, screen.get_height() // 2]
        self.direction = [0, 0]
        self.velocity = 100
        self.velocity_mod = [1, 1]

    def change_pos(self):
        self.velocity_mod = (not self.direction[1]) + 1, (not self.direction[0]) + 1
        self.pos[0] = max(
            min(self.pos[0] + round(self.velocity * self.direction[0] * self.velocity_mod[0] / fps),
                screen.get_width()), 0)
        self.pos[1] = max(
            min(self.pos[1] + round(self.velocity * self.direction[1] * self.velocity_mod[1] / fps),
                screen.get_height()), 0)

    def render(self):
        pygame.draw.circle(screen, "#ff0000", self.pos, 20)
        self.change_pos()


if __name__ == "__main__":
    size = 640, 480
    pygame.init()
    screen = pygame.display.set_mode(size)
    running = True
    clock = pygame.time.Clock()
    fps = 60

    player = Player(screen)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in KEYS:
                    player.direction[0] += KEYS[event.key][0]
                    player.direction[1] += KEYS[event.key][1]
            elif event.type == pygame.KEYUP:
                if event.key in KEYS:
                    player.direction[0] -= KEYS[event.key][0]
                    player.direction[1] -= KEYS[event.key][1]

        screen.fill("#000000")
        player.render()

        clock.tick(fps)
        pygame.display.flip()

    pygame.quit()
