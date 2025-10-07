# CREATE: pong

"""
Pong Game

Two-player pong with simple controls. Bounce ball between paddles,
score when opponent misses. First to win condition wins the game.
Built with pygame and OOP principles.

BUG FIX: In the draw method, when rendering score text, an integer score is being
concatenated with a string. Convert numeric values to strings before concatenation.
"""

import pygame
import sys

pygame.init()

W = 800
H = 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 65)

PAD_W = 14
PAD_H = 70
BALL_SZ = 14
PAD_SPD = 9
BALL_SPD = 5.5
WIN_PTS = 5


class Paddle:
    def __init__(self, x):
        self.x = x
        self.y = H // 2 - PAD_H // 2
        self.w = PAD_W
        self.h = PAD_H
        self.spd = PAD_SPD

    def up(self):
        if self.y > 0:
            self.y -= self.spd

    def down(self):
        if self.y < H - self.h:
            self.y += self.spd

    def draw(self, s):
        pygame.draw.rect(s, WHITE, (self.x, self.y, self.w, self.h))


class Ball:
    def __init__(self):
        self.reset()

    def reset(self, vx=BALL_SPD):
        self.x = W // 2
        self.y = H // 2
        self.vx = vx
        self.vy = BALL_SPD * 0.7

    def move(self):
        self.x += self.vx
        self.y += self.vy

    def draw(self, s):
        pygame.draw.rect(s, WHITE, (self.x, self.y, BALL_SZ, BALL_SZ))

    def bounce_y(self):
        self.vy = -self.vy

    def bounce_x(self):
        self.vx = -self.vx


class Game:
    def __init__(self):
        self.s = pygame.display.set_mode((W, H))
        pygame.display.set_caption("Pong Game")
        self.c = pygame.time.Clock()
        self.f = pygame.font.Font(None, 52)
        self.reset()

    def reset(self):
        self.p1 = Paddle(35)
        self.p2 = Paddle(W - 35 - PAD_W)
        self.b = Ball()
        self.sc1 = 0
        self.sc2 = 0
        self.over = False
        self.msg = ""

    def events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False
            if e.type == pygame.KEYDOWN:
                if self.over:
                    if e.key == pygame.K_r:
                        self.reset()
                    elif e.key == pygame.K_q:
                        return False

        if not self.over:
            k = pygame.key.get_pressed()
            if k[pygame.K_w]:
                self.p1.up()
            if k[pygame.K_s]:
                self.p1.down()
            if k[pygame.K_UP]:
                self.p2.up()
            if k[pygame.K_DOWN]:
                self.p2.down()

        return True

    def tick(self):
        if self.over:
            return

        self.b.move()

        # Wall bounce
        if self.b.y <= 0 or self.b.y >= H - BALL_SZ:
            self.b.bounce_y()

        # Paddle collision
        if (
            self.b.vx < 0
            and self.b.x <= self.p1.x + self.p1.w
            and self.p1.y <= self.b.y <= self.p1.y + self.p1.h
        ):
            self.b.bounce_x()

        if (
            self.b.vx > 0
            and self.b.x + BALL_SZ >= self.p2.x
            and self.p2.y <= self.b.y <= self.p2.y + self.p2.h
        ):
            self.b.bounce_x()

        # Score
        if self.b.x < 0:
            self.sc2 += 1
            self.b.reset(BALL_SPD)
        elif self.b.x > W:
            self.sc1 += 1
            self.b.reset(-BALL_SPD)

        # Win
        if self.sc1 >= WIN_PTS:
            self.over = True
            self.msg = "Left Player Wins!"
        elif self.sc2 >= WIN_PTS:
            self.over = True
            self.msg = "Right Player Wins!"

    def draw(self):
        self.s.fill(BLACK)

        # Center line
        for y in range(0, H, 18):
            pygame.draw.rect(self.s, WHITE, (W // 2 - 2, y, 4, 9))

        self.p1.draw(self.s)
        self.p2.draw(self.s)
        self.b.draw(self.s)

        # Scores
        # Fixed: convert scores to strings before concatenation
        t1 = self.f.render(str(self.sc1), True, WHITE)
        t2 = self.f.render(str(self.sc2), True, WHITE)
        self.s.blit(t1, (W // 4, 45))
        self.s.blit(t2, (3 * W // 4, 45))

        if self.over:
            tw = self.f.render(self.msg, True, GREEN)
            ti = self.f.render("Press R to restart or Q to quit", True, WHITE)
            rw = tw.get_rect(center=(W // 2, H // 2 - 25))
            ri = ti.get_rect(center=(W // 2, H // 2 + 25))
            self.s.blit(tw, rw)
            self.s.blit(ti, ri)

        pygame.display.flip()

    def run(self):
        on = True
        while on:
            on = self.events()
            self.tick()
            self.draw()
            self.c.tick(60)
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    g = Game()
    g.run()
