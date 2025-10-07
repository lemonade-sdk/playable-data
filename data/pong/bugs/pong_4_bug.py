# CREATE: pong
# ERROR: Traceback (most recent call last):
# ERROR:   File "C:\work\lsdk\playable-data\data\pong\bugs\pong_4_bug.py", line 235, in <module>
# ERROR:     game.run()
# ERROR:   File "C:\work\lsdk\playable-data\data\pong\bugs\pong_4_bug.py", line 224, in run
# ERROR:     active = self.input()
# ERROR:              ^^^^^^^^^^^^
# ERROR:   File "C:\work\lsdk\playable-data\data\pong\bugs\pong_4_bug.py", line 137, in input
# ERROR:     if keys[pygame.K_w]:
# ERROR:        ^^^^
# ERROR: NameError: name 'keys' is not defined

"""
Pong Game

Classic pong implementation with two-player gameplay. Each player controls
a paddle to hit the ball. Score points by getting ball past opponent.
Match ends when a player reaches winning score.
"""

import pygame
import sys

# Initialize pygame
pygame.init()

# Window settings
WIN_W = 720
WIN_H = 560
BG = (0, 0, 0)
FG = (255, 255, 255)
WINNER_COLOR = (0, 255, 65)

# Game config
PAD_W = 13
PAD_H = 75
BALL_R = 7
PAD_V = 8
BALL_V = 6
TARGET = 5


class Pad:
    """Player paddle"""

    def __init__(self, xpos):
        self.x = xpos
        self.y = WIN_H // 2 - PAD_H // 2
        self.w = PAD_W
        self.h = PAD_H
        self.v = PAD_V

    def up(self):
        """Move up"""
        if self.y > 0:
            self.y -= self.v

    def down(self):
        """Move down"""
        if self.y < WIN_H - self.h:
            self.y += self.v

    def draw(self, scr):
        """Render paddle"""
        pygame.draw.rect(scr, FG, (self.x, self.y, self.w, self.h))

    def contains(self, y):
        """Check if y coordinate is within paddle"""
        return self.y <= y <= self.y + self.h


class Ball:
    """Game ball"""

    def __init__(self):
        self.r = BALL_R
        self.init()

    def init(self, dx=1):
        """Initialize ball position"""
        self.x = WIN_W // 2
        self.y = WIN_H // 2
        self.dx = BALL_V * dx
        self.dy = BALL_V * 0.6

    def move(self):
        """Update position"""
        self.x += self.dx
        self.y += self.dy

    def flip_x(self):
        """Reverse horizontal direction"""
        self.dx = -self.dx

    def flip_y(self):
        """Reverse vertical direction"""
        self.dy = -self.dy

    def draw(self, scr):
        """Render ball"""
        pygame.draw.circle(scr, FG, (int(self.x), int(self.y)), self.r)

    def past_left(self):
        """Check if past left edge"""
        return self.x < 0

    def past_right(self):
        """Check if past right edge"""
        return self.x > WIN_W


class PongGame:
    """Main game class"""

    def __init__(self):
        self.scr = pygame.display.set_mode((WIN_W, WIN_H))
        pygame.display.set_caption("Pong Game")
        self.clk = pygame.time.Clock()
        self.big_font = pygame.font.Font(None, 54)
        self.med_font = pygame.font.Font(None, 42)
        self.setup()

    def setup(self):
        """Initialize game objects"""
        self.p1 = Pad(38)
        self.p2 = Pad(WIN_W - 38 - PAD_W)
        self.ball = Ball()
        self.s1 = 0
        self.s2 = 0
        self.done = False
        self.winner = ""

    def input(self):
        """Handle input"""
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            if ev.type == pygame.KEYDOWN:
                if self.done:
                    if ev.key == pygame.K_r:
                        self.setup()
                    elif ev.key == pygame.K_q:
                        return False

        if not self.done:
            k = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                self.p1.up()
            if keys[pygame.K_s]:
                self.p1.down()
            if keys[pygame.K_UP]:
                self.p2.up()
            if keys[pygame.K_DOWN]:
                self.p2.down()

        return True

    def update(self):
        """Update game state"""
        if self.done:
            return

        self.ball.move()

        # Top/bottom bounce
        if self.ball.y - self.ball.r <= 0 or self.ball.y + self.ball.r >= WIN_H:
            self.ball.flip_y()

        # Paddle collision
        if (
            self.ball.dx < 0
            and self.ball.x - self.ball.r <= self.p1.x + self.p1.w
            and self.p1.contains(self.ball.y)
        ):
            self.ball.flip_x()

        if (
            self.ball.dx > 0
            and self.ball.x + self.ball.r >= self.p2.x
            and self.p2.contains(self.ball.y)
        ):
            self.ball.flip_x()

        # Scoring
        if self.ball.past_left():
            self.s2 += 1
            self.ball.init(1)
        elif self.ball.past_right():
            self.s1 += 1
            self.ball.init(-1)

        # Check win
        if self.s1 >= TARGET:
            self.done = True
            self.winner = "Left Player Wins!"
        elif self.s2 >= TARGET:
            self.done = True
            self.winner = "Right Player Wins!"

    def render(self):
        """Render frame"""
        self.scr.fill(BG)

        # Dotted center
        for y in range(0, WIN_H, 22):
            pygame.draw.rect(self.scr, FG, (WIN_W // 2 - 2, y, 4, 11))

        # Draw objects
        self.p1.draw(self.scr)
        self.p2.draw(self.scr)
        self.ball.draw(self.scr)

        # Scores
        t1 = self.big_font.render(str(self.s1), True, FG)
        t2 = self.big_font.render(str(self.s2), True, FG)
        self.scr.blit(t1, (WIN_W // 4 - 18, 42))
        self.scr.blit(t2, (3 * WIN_W // 4 - 18, 42))

        # Game over
        if self.done:
            wt = self.med_font.render(self.winner, True, WINNER_COLOR)
            it = self.med_font.render("Press R to restart or Q to quit", True, FG)
            wr = wt.get_rect(center=(WIN_W // 2, WIN_H // 2 - 26))
            ir = it.get_rect(center=(WIN_W // 2, WIN_H // 2 + 26))
            self.scr.blit(wt, wr)
            self.scr.blit(it, ir)

        pygame.display.flip()

    def run(self):
        """Game loop"""
        active = True
        while active:
            active = self.input()
            self.update()
            self.render()
            self.clk.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = PongGame()
    game.run()
