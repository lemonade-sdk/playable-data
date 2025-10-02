"""
Space Invaders

Classic arcade shooter. Player defends against waves of aliens moving across
the screen. Shoot all aliens to win. Game over if aliens reach player level.
Simple OOP design with pygame rendering.
"""

import pygame
import sys

pygame.init()

WIDTH = 850
HEIGHT = 600
BLACK = (0, 0, 0)
GREEN = (0, 255, 65)
WHITE = (255, 255, 255)


class Ship:
    def __init__(self):
        self.w = 45
        self.h = 20
        self.x = WIDTH // 2 - self.w // 2
        self.y = HEIGHT - 55
        self.spd = 5

    def left(self):
        if self.x > 0:
            self.x -= self.spd

    def right(self):
        if self.x < WIDTH - self.w:
            self.x += self.spd

    def draw(self, scr):
        pygame.draw.rect(scr, GREEN, (self.x, self.y, self.w, self.h))


class Shot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 4
        self.h = 10
        self.spd = 9

    def move(self):
        self.y -= self.spd

    def draw(self, scr):
        pygame.draw.rect(scr, GREEN, (self.x, self.y, self.w, self.h))

    def gone(self):
        return self.y < 0


class Alien:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 32
        self.h = 24
        self.spd = 0.8
        self.dir = 1

    def move(self):
        self.x += self.spd * self.dir

    def drop(self):
        self.y += 30
        self.dir *= -1

    def draw(self, scr):
        pygame.draw.rect(scr, GREEN, (self.x, self.y, self.w, self.h))
        pygame.draw.rect(scr, BLACK, (self.x + 6, self.y + 6, 4, 4))
        pygame.draw.rect(scr, BLACK, (self.x + 22, self.y + 6, 4, 4))

    def hit_edge(self):
        return self.x <= 0 or self.x >= WIDTH - self.w


class Game:
    def __init__(self):
        self.scr = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Space Invaders")
        self.clk = pygame.time.Clock()
        self.fnt = pygame.font.Font(None, 30)
        self.reset()

    def reset(self):
        self.ship = Ship()
        self.shots = []
        self.aliens = []
        self.pts = 0
        self.done = False
        self.win = False
        self.spawn_aliens()

    def spawn_aliens(self):
        for r in range(5):
            for c in range(11):
                ax = 60 + c * 65
                ay = 50 + r * 50
                self.aliens.append(Alien(ax, ay))

    def events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE and not self.done:
                    sx = self.ship.x + self.ship.w // 2
                    sy = self.ship.y
                    self.shots.append(Shot(sx, sy))
                elif e.key == pygame.K_r and self.done:
                    self.reset()
                elif e.key == pygame.K_q and self.done:
                    return False
        return True

    def tick(self):
        if self.done:
            return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.ship.left()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.ship.right()

        for s in self.shots[:]:
            s.move()
            if s.gone():
                self.shots.remove(s)

        edge = False
        for a in self.aliens:
            a.move()
            if a.hit_edge():
                edge = True

        if edge:
            for a in self.aliens:
                a.drop()

        for s in self.shots[:]:
            for a in self.aliens[:]:
                if (
                    s.x < a.x + a.w
                    and s.x + s.w > a.x
                    and s.y < a.y + a.h
                    and s.y + s.h > a.y
                ):
                    if s in self.shots:
                        self.shots.remove(s)
                    if a in self.aliens:
                        self.aliens.remove(a)
                    self.pts += 10
                    break

        if not self.aliens:
            self.win = True
            self.done = True

        for a in self.aliens:
            if a.y + a.h >= self.ship.y:
                self.done = True
                break

    def draw(self):
        self.scr.fill(BLACK)

        if not self.done:
            self.ship.draw(self.scr)
            for s in self.shots:
                s.draw(self.scr)
            for a in self.aliens:
                a.draw(self.scr)

        txt = self.fnt.render(f"Score: {self.pts}", True, GREEN)
        self.scr.blit(txt, (10, 10))

        if self.done:
            if self.win:
                msg = self.fnt.render("VICTORY!", True, GREEN)
            else:
                msg = self.fnt.render("GAME OVER", True, GREEN)
            ins = self.fnt.render("Press R to restart or Q to quit", True, GREEN)
            mr = msg.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
            ir = ins.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
            self.scr.blit(msg, mr)
            self.scr.blit(ins, ir)

        pygame.display.flip()

    def run(self):
        go = True
        while go:
            go = self.events()
            self.tick()
            self.draw()
            self.clk.tick(60)
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    g = Game()
    g.run()
