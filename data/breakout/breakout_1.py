"""
Breakout - Classic paddle and ball game where you break bricks.
Control a paddle to bounce a ball and destroy all the bricks at the top of the screen.
The game ends when you clear all bricks (win) or the ball falls past your paddle (lose).
Features simple collision physics and score tracking.
"""

import pygame
import random
import sys

pygame.init()

# Screen settings
WIDTH = 600
HEIGHT = 400
BLACK = (0, 0, 0)
GREEN = (0, 255, 65)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)


class Paddle:
    def __init__(self):
        self.w = 90
        self.h = 12
        self.x = WIDTH // 2 - self.w // 2
        self.y = HEIGHT - 40
        self.speed = 7

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.w:
            self.x += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, (self.x, self.y, self.w, self.h))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)


class Ball:
    def __init__(self):
        self.size = 12
        self.speed = 4
        self.reset()

    def reset(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.vx = random.choice([-self.speed, self.speed])
        self.vy = self.speed

    def move(self):
        self.x += self.vx
        self.y += self.vy

        # Bounce off walls
        if self.x <= 0 or self.x >= WIDTH - self.size:
            self.vx = -self.vx
        if self.y <= 0:
            self.vy = -self.vy

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.size // 2)

    def get_rect(self):
        return pygame.Rect(
            self.x - self.size // 2, self.y - self.size // 2, self.size, self.size
        )

    def fell_off(self):
        return self.y > HEIGHT


class Brick:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.w = 60
        self.h = 25
        self.color = color
        self.active = True

    def draw(self, screen):
        if self.active:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.w, self.h))
            pygame.draw.rect(screen, BLACK, (self.x, self.y, self.w, self.h), 1)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Breakout")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 30)
        self.reset()

    def reset(self):
        self.paddle = Paddle()
        self.ball = Ball()
        self.bricks = []
        self.points = 0
        self.is_over = False
        self.victory = False
        self.make_bricks()

    def make_bricks(self):
        rows = 5
        cols = 9
        padding = 3
        brick_colors = [RED, RED, YELLOW, BLUE, BLUE]

        total_width = cols * 60 + (cols - 1) * padding
        start_x = (WIDTH - total_width) // 2
        start_y = 40

        for r in range(rows):
            for c in range(cols):
                x = start_x + c * (60 + padding)
                y = start_y + r * (25 + padding)
                color = brick_colors[r]
                self.bricks.append(Brick(x, y, color))

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if self.is_over:
                    if event.key == pygame.K_r:
                        self.reset()
                    elif event.key == pygame.K_q:
                        return False
        return True

    def update(self):
        if not self.is_over:
            keys = pygame.key.get_pressed()
            self.paddle.move(keys)
            self.ball.move()

            # Paddle collision
            if (
                self.ball.get_rect().colliderect(self.paddle.get_rect())
                and self.ball.vy > 0
            ):
                self.ball.vy = -self.ball.vy
                # Adjust horizontal velocity based on hit position
                relative_hit = (self.ball.x - self.paddle.x) / self.paddle.w
                self.ball.vx = self.ball.speed * (relative_hit - 0.5) * 2

            # Brick collisions
            for brick in self.bricks:
                if brick.active and self.ball.get_rect().colliderect(brick.get_rect()):
                    brick.active = False
                    self.ball.vy = -self.ball.vy
                    self.points += 15
                    break

            # Check win
            if all(not brick.active for brick in self.bricks):
                self.is_over = True
                self.victory = True

            # Check loss
            if self.ball.fell_off():
                self.is_over = True

    def render(self):
        self.screen.fill(BLACK)

        self.paddle.draw(self.screen)
        self.ball.draw(self.screen)
        for brick in self.bricks:
            brick.draw(self.screen)

        # Score
        score_surf = self.font.render(f"Score: {self.points}", True, WHITE)
        self.screen.blit(score_surf, (10, 10))

        # Game over messages
        if self.is_over:
            if self.victory:
                msg = self.font.render("You Win!", True, GREEN)
            else:
                msg = self.font.render("Game Over!", True, RED)

            info = self.font.render("Press R to restart or Q to quit", True, WHITE)

            msg_rect = msg.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
            info_rect = info.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))

            self.screen.blit(msg, msg_rect)
            self.screen.blit(info, info_rect)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.render()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
