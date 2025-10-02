"""
Breakout - Brick breaking arcade game.
Use the paddle to keep the ball in play and destroy all bricks.
Hit all bricks to win, or lose if the ball falls off the bottom.
Classic arcade gameplay with score tracking and simple physics.
"""

import pygame
import random
import sys

# Initialize
pygame.init()

# Constants
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700
PADDLE_WIDTH = 120
PADDLE_HEIGHT = 18
PADDLE_SPEED = 9
BALL_RADIUS = 8
BALL_SPEED_X = 6
BALL_SPEED_Y = 6
BRICK_WIDTH = 85
BRICK_HEIGHT = 35
BRICK_ROWS = 7
BRICK_COLS = 10
BRICK_GAP = 4
BLACK = (0, 0, 0)
GREEN = (0, 255, 65)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (160, 32, 240)


class Paddle:
    def __init__(self):
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - 60

    def advance(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= PADDLE_SPEED
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width:
            self.x += PADDLE_SPEED

    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, (self.x, self.y, self.width, self.height))

    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Ball:
    def __init__(self):
        self.radius = BALL_RADIUS
        self.initialize()

    def initialize(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.velocity_x = random.choice([-BALL_SPEED_X, BALL_SPEED_X])
        self.velocity_y = BALL_SPEED_Y

    def advance(self):
        self.x += self.velocity_x
        self.y += self.velocity_y

        # Wall bouncing
        if self.x - self.radius <= 0 or self.x + self.radius >= SCREEN_WIDTH:
            self.velocity_x = -self.velocity_x
        if self.y - self.radius <= 0:
            self.velocity_y = -self.velocity_y

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)

    def rect(self):
        return pygame.Rect(
            self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2
        )

    def is_lost(self):
        return self.y > SCREEN_HEIGHT


class Brick:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.width = BRICK_WIDTH
        self.height = BRICK_HEIGHT
        self.color = color
        self.broken = False

    def draw(self, screen):
        if not self.broken:
            pygame.draw.rect(
                screen, self.color, (self.x, self.y, self.width, self.height)
            )
            pygame.draw.rect(
                screen, BLACK, (self.x, self.y, self.width, self.height), 2
            )

    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Breakout")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 40)
        self.initialize_game()

    def initialize_game(self):
        self.paddle = Paddle()
        self.ball = Ball()
        self.bricks = []
        self.score = 0
        self.game_over = False
        self.won = False
        self.setup_bricks()

    def setup_bricks(self):
        colors = [RED, ORANGE, YELLOW, YELLOW, BLUE, PURPLE, PURPLE]

        total_brick_width = BRICK_COLS * BRICK_WIDTH + (BRICK_COLS - 1) * BRICK_GAP
        start_x = (SCREEN_WIDTH - total_brick_width) // 2
        start_y = 60

        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLS):
                x = start_x + col * (BRICK_WIDTH + BRICK_GAP)
                y = start_y + row * (BRICK_HEIGHT + BRICK_GAP)
                color = colors[row % len(colors)]
                self.bricks.append(Brick(x, y, color))

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_r:
                        self.initialize_game()
                    elif event.key == pygame.K_q:
                        return False
        return True

    def check_collision_with_brick(self, brick):
        if not brick.broken and self.ball.rect().colliderect(brick.rect()):
            return True
        return False

    def check_collision_with_paddle(self):
        if (
            self.ball.rect().colliderect(self.paddle.rect())
            and self.ball.velocity_y > 0
        ):
            return True
        return False

    def update_game(self):
        if not self.game_over:
            keys = pygame.key.get_pressed()
            self.paddle.advance(keys)
            self.ball.advance()

            # Paddle collision
            if self.check_collision_with_paddle():
                self.ball.velocity_y = -self.ball.velocity_y
                # Adjust angle based on where ball hits
                hit_position = (self.ball.x - self.paddle.x) / self.paddle.width
                self.ball.velocity_x = BALL_SPEED_X * (hit_position - 0.5) * 2

            # Brick collisions
            for brick in self.bricks:
                if self.check_collision_with_brick(brick):
                    brick.broken = True
                    self.ball.velocity_y = -self.ball.velocity_y
                    self.score += 20
                    break

            # Check victory
            if all(brick.broken for brick in self.bricks):
                self.game_over = True
                self.won = True

            # Check defeat
            if self.ball.is_lost():
                self.game_over = True

    def draw_game(self):
        self.screen.fill(BLACK)

        # Draw objects
        self.paddle.draw(self.screen)
        self.ball.draw(self.screen)
        for brick in self.bricks:
            brick.draw(self.screen)

        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (15, 15))

        # Draw game over screen
        if self.game_over:
            if self.won:
                message = self.font.render("You Win!", True, GREEN)
            else:
                message = self.font.render("Game Over!", True, RED)

            instructions = self.font.render(
                "Press R to restart or Q to quit", True, WHITE
            )

            message_rect = message.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40)
            )
            instructions_rect = instructions.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)
            )

            self.screen.blit(message, message_rect)
            self.screen.blit(instructions, instructions_rect)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.process_events()
            self.update_game()
            self.draw_game()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
