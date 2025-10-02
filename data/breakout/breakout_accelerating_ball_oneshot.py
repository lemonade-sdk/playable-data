# CREATE: breakout where the ball speeds up on each paddle hit

"""
Breakout Accelerating Ball Game

A brick-breaking game where the player controls a paddle to bounce a ball and destroy
bricks, with ball speed increasing each time it collides with the paddle. Creates
progressively more challenging gameplay as rallies continue and ball speed accumulates.
Implementation uses pygame with speed modification mechanics, collision detection, and
physics simulation.
"""

import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 15
PADDLE_SPEED = 8
BALL_SIZE = 15
BALL_SPEED = 5
BALL_ACCELERATION = 0.5  # Speed increase per paddle hit
BRICK_WIDTH = 75
BRICK_HEIGHT = 30
BRICK_ROWS = 6
BRICK_COLS = 10
BRICK_PADDING = 5
BLACK = (0, 0, 0)
GREEN = (0, 255, 65)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)


class Paddle:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2 - PADDLE_WIDTH // 2
        self.y = SCREEN_HEIGHT - 50
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= PADDLE_SPEED
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width:
            self.x += PADDLE_SPEED

    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, (self.x, self.y, self.width, self.height))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Ball:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.vel_x = random.choice([-BALL_SPEED, BALL_SPEED])
        self.vel_y = BALL_SPEED

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y

        # Wall bouncing
        if self.x <= 0 or self.x >= SCREEN_WIDTH - BALL_SIZE:
            self.vel_x = -self.vel_x
        if self.y <= 0:
            self.vel_y = -self.vel_y

    def accelerate(self):
        """Increase ball speed"""
        # Increase speed while maintaining direction
        if self.vel_x > 0:
            self.vel_x += BALL_ACCELERATION
        else:
            self.vel_x -= BALL_ACCELERATION

        if self.vel_y > 0:
            self.vel_y += BALL_ACCELERATION
        else:
            self.vel_y -= BALL_ACCELERATION

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), BALL_SIZE // 2)

    def get_rect(self):
        return pygame.Rect(
            self.x - BALL_SIZE // 2, self.y - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE
        )

    def is_below_screen(self):
        return self.y > SCREEN_HEIGHT


class Brick:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.width = BRICK_WIDTH
        self.height = BRICK_HEIGHT
        self.color = color
        self.destroyed = False

    def draw(self, screen):
        if not self.destroyed:
            pygame.draw.rect(
                screen, self.color, (self.x, self.y, self.width, self.height)
            )
            pygame.draw.rect(
                screen, BLACK, (self.x, self.y, self.width, self.height), 2
            )

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Breakout")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.reset_game()

    def reset_game(self):
        self.paddle = Paddle()
        self.ball = Ball()
        self.bricks = []
        self.score = 0
        self.game_over = False
        self.won = False
        self.create_bricks()

    def create_bricks(self):
        colors = [RED, RED, YELLOW, YELLOW, BLUE, BLUE]
        start_x = (
            SCREEN_WIDTH - (BRICK_COLS * (BRICK_WIDTH + BRICK_PADDING) - BRICK_PADDING)
        ) // 2
        start_y = 50

        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLS):
                x = start_x + col * (BRICK_WIDTH + BRICK_PADDING)
                y = start_y + row * (BRICK_HEIGHT + BRICK_PADDING)
                color = colors[row % len(colors)]
                self.bricks.append(Brick(x, y, color))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_q:
                        return False
        return True

    def update(self):
        if not self.game_over:
            keys = pygame.key.get_pressed()
            self.paddle.update(keys)
            self.ball.update()

            # Ball-paddle collision
            if (
                self.ball.get_rect().colliderect(self.paddle.get_rect())
                and self.ball.vel_y > 0
            ):
                self.ball.vel_y = -self.ball.vel_y
                # Add some angle based on where ball hits paddle
                hit_pos = (self.ball.x - self.paddle.x) / self.paddle.width
                self.ball.vel_x = BALL_SPEED * (hit_pos - 0.5) * 2
                # Accelerate the ball
                self.ball.accelerate()

            # Ball-brick collisions
            for brick in self.bricks:
                if not brick.destroyed and self.ball.get_rect().colliderect(
                    brick.get_rect()
                ):
                    brick.destroyed = True
                    self.ball.vel_y = -self.ball.vel_y
                    self.score += 10
                    break

            # Check win condition
            if all(brick.destroyed for brick in self.bricks):
                self.game_over = True
                self.won = True

            # Check lose condition
            if self.ball.is_below_screen():
                self.game_over = True

    def draw(self):
        self.screen.fill(BLACK)

        # Draw game objects
        self.paddle.draw(self.screen)
        self.ball.draw(self.screen)
        for brick in self.bricks:
            brick.draw(self.screen)

        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # Draw game over screen
        if self.game_over:
            if self.won:
                end_text = self.font.render("You Win!", True, GREEN)
            else:
                end_text = self.font.render("Game Over!", True, RED)

            restart_text = self.font.render(
                "Press R to restart or Q to quit", True, WHITE
            )

            end_rect = end_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30)
            )
            restart_rect = restart_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30)
            )

            self.screen.blit(end_text, end_rect)
            self.screen.blit(restart_text, restart_rect)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
