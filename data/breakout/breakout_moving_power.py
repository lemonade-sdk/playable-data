# SOURCE: breakout_moving_bricks.py
# REMIX: add power-up bricks

"""
Breakout Moving Power - A remix combining moving bricks and power bricks mechanics.
Bricks slowly move side to side while some contain power-ups that enhance gameplay.
This creates dynamic targets with strategic power-up collection opportunities.

This remix combines features from breakout_moving_bricks.py and breakout_power_bricks.py,
creating engaging gameplay with mobile targets and strategic power-up decisions.

Implementation uses pygame with minimal graphics and clean object-oriented design.
"""

import pygame
import random
import sys
import math

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
BRICK_WIDTH = 75
BRICK_HEIGHT = 30
BRICK_ROWS = 6
BRICK_COLS = 10
BRICK_PADDING = 5
BRICK_MOVE_SPEED = 1
BRICK_MOVE_RANGE = 30  # How far bricks move from center
POWER_DURATION = 300  # Frames power-ups last (5 seconds at 60 FPS)
BLACK = (0, 0, 0)
GREEN = (0, 255, 65)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)


class Paddle:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2 - PADDLE_WIDTH // 2
        self.y = SCREEN_HEIGHT - 50
        self.base_width = PADDLE_WIDTH
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.big_paddle_timer = 0

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= PADDLE_SPEED
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width:
            self.x += PADDLE_SPEED

        # Update power-up timers
        if self.big_paddle_timer > 0:
            self.big_paddle_timer -= 1
            if self.big_paddle_timer == 0:
                self.width = self.base_width

    def activate_big_paddle(self):
        """Activate big paddle power-up"""
        self.width = self.base_width * 1.5
        self.big_paddle_timer = POWER_DURATION

    def draw(self, screen):
        color = GREEN
        if self.big_paddle_timer > 0:
            color = PURPLE  # Different color when powered up
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Ball:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.base_speed = BALL_SPEED
        self.vel_x = random.choice([-self.base_speed, self.base_speed])
        self.vel_y = self.base_speed
        self.fast_ball_timer = 0

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y

        # Wall bouncing
        if self.x <= 0 or self.x >= SCREEN_WIDTH - BALL_SIZE:
            self.vel_x = -self.vel_x
        if self.y <= 0:
            self.vel_y = -self.vel_y

        # Update power-up timers
        if self.fast_ball_timer > 0:
            self.fast_ball_timer -= 1
            if self.fast_ball_timer == 0:
                # Reset to normal speed
                speed_ratio = self.base_speed / (self.base_speed * 1.5)
                self.vel_x *= speed_ratio
                self.vel_y *= speed_ratio

    def activate_fast_ball(self):
        """Activate fast ball power-up"""
        speed_ratio = 1.5
        self.vel_x *= speed_ratio
        self.vel_y *= speed_ratio
        self.fast_ball_timer = POWER_DURATION

    def draw(self, screen):
        color = WHITE
        if self.fast_ball_timer > 0:
            color = ORANGE  # Different color when powered up
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), BALL_SIZE // 2)

    def get_rect(self):
        return pygame.Rect(
            self.x - BALL_SIZE // 2, self.y - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE
        )

    def is_below_screen(self):
        return self.y > SCREEN_HEIGHT


class Brick:
    def __init__(self, x, y, color, power_type=None):
        self.center_x = x
        self.x = x
        self.y = y
        self.width = BRICK_WIDTH
        self.height = BRICK_HEIGHT
        self.color = color
        self.power_type = power_type
        self.destroyed = False
        self.move_offset = random.uniform(0, 2 * math.pi)  # Random phase for movement

    def update(self, frame_count):
        """Update brick position with oscillating movement"""
        if not self.destroyed:
            # Oscillate around center position
            self.x = (
                self.center_x
                + math.sin(frame_count * 0.02 + self.move_offset) * BRICK_MOVE_RANGE
            )

    def draw(self, screen):
        if not self.destroyed:
            color = self.color
            if self.power_type:
                # Power bricks have a special border
                pygame.draw.rect(
                    screen, color, (int(self.x), self.y, self.width, self.height)
                )
                pygame.draw.rect(
                    screen, WHITE, (int(self.x), self.y, self.width, self.height), 4
                )
            else:
                pygame.draw.rect(
                    screen, color, (int(self.x), self.y, self.width, self.height)
                )
                pygame.draw.rect(
                    screen, BLACK, (int(self.x), self.y, self.width, self.height), 2
                )

    def get_rect(self):
        return pygame.Rect(int(self.x), self.y, self.width, self.height)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Breakout")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.frame_count = 0
        self.reset_game()

    def reset_game(self):
        self.paddle = Paddle()
        self.ball = Ball()
        self.bricks = []
        self.score = 0
        self.game_over = False
        self.won = False
        self.frame_count = 0
        self.create_bricks()

    def create_bricks(self):
        colors = [RED, RED, YELLOW, YELLOW, BLUE, BLUE]
        power_types = ["big_paddle", "fast_ball", "bonus_points"]
        start_x = (
            SCREEN_WIDTH - (BRICK_COLS * (BRICK_WIDTH + BRICK_PADDING) - BRICK_PADDING)
        ) // 2
        start_y = 50

        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLS):
                x = start_x + col * (BRICK_WIDTH + BRICK_PADDING)
                y = start_y + row * (BRICK_HEIGHT + BRICK_PADDING)
                color = colors[row % len(colors)]

                # 20% chance for power brick
                power_type = None
                if random.random() < 0.2:
                    power_type = random.choice(power_types)
                    if power_type == "big_paddle":
                        color = PURPLE
                    elif power_type == "fast_ball":
                        color = ORANGE
                    elif power_type == "bonus_points":
                        color = WHITE

                self.bricks.append(Brick(x, y, color, power_type))

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
            self.frame_count += 1
            keys = pygame.key.get_pressed()
            self.paddle.update(keys)
            self.ball.update()

            # Update moving bricks
            for brick in self.bricks:
                brick.update(self.frame_count)

            # Ball-paddle collision
            if (
                self.ball.get_rect().colliderect(self.paddle.get_rect())
                and self.ball.vel_y > 0
            ):
                self.ball.vel_y = -self.ball.vel_y
                # Add some angle based on where ball hits paddle
                hit_pos = (self.ball.x - self.paddle.x) / self.paddle.width
                self.ball.vel_x = BALL_SPEED * (hit_pos - 0.5) * 2

            # Ball-brick collisions
            for brick in self.bricks:
                if not brick.destroyed and self.ball.get_rect().colliderect(
                    brick.get_rect()
                ):
                    brick.destroyed = True
                    self.ball.vel_y = -self.ball.vel_y

                    # Handle power-ups
                    if brick.power_type == "big_paddle":
                        self.paddle.activate_big_paddle()
                        self.score += 20
                    elif brick.power_type == "fast_ball":
                        self.ball.activate_fast_ball()
                        self.score += 20
                    elif brick.power_type == "bonus_points":
                        self.score += 50
                    else:
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
