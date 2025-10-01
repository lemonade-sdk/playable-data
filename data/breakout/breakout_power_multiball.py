# SOURCE: breakout_power_bricks.py
# REMIX: add multiball power-up

"""
Breakout Power Multiball Remix - A remix of the Power Bricks Breakout with an additional multiball power-up.
The player controls a paddle to bounce balls and destroy bricks. Some bricks contain power-ups
that enhance gameplay: bigger paddle, faster ball, extra points, or spawn additional balls.
Power bricks are visually distinct and add strategic elements as players decide which bricks to target first.
Implementation uses pygame with minimal graphics and clean object-oriented design.
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
BRICK_WIDTH = 75
BRICK_HEIGHT = 30
BRICK_ROWS = 6
BRICK_COLS = 10
BRICK_PADDING = 5
POWER_DURATION = 300  # Frames power-ups last (5 seconds at 60 FPS)
BLACK = (0, 0, 0)
GREEN = (0, 255, 65)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)


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
                old_width = self.width
                self.width = self.base_width
                self.x += (old_width - self.width) // 2  # Keep centered

    def activate_big_paddle(self):
        if self.big_paddle_timer == 0:  # Only activate if not already active
            old_width = self.width
            self.width = self.base_width * 1.5
            self.x -= (self.width - old_width) // 2  # Keep centered
        self.big_paddle_timer = POWER_DURATION

    def draw(self, screen):
        color = ORANGE if self.big_paddle_timer > 0 else GREEN
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Ball:
    def __init__(self, x=None, y=None):
        if x is None or y is None:
            self.reset()
        else:
            self.x = x
            self.y = y
            self.vel_x = random.choice([-BALL_SPEED, BALL_SPEED])
            self.vel_y = BALL_SPEED
        self.base_speed = BALL_SPEED
        self.fast_ball_timer = 0

    def reset(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.vel_x = random.choice([-BALL_SPEED, BALL_SPEED])
        self.vel_y = BALL_SPEED

    def update(self):
        # Update power-up timers
        if self.fast_ball_timer > 0:
            self.fast_ball_timer -= 1

        # Apply speed multiplier
        speed_mult = 1.5 if self.fast_ball_timer > 0 else 1.0

        self.x += self.vel_x * speed_mult
        self.y += self.vel_y * speed_mult

        # Wall bouncing
        if self.x <= 0 or self.x >= SCREEN_WIDTH - BALL_SIZE:
            self.vel_x = -self.vel_x
        if self.y <= 0:
            self.vel_y = -self.vel_y

    def activate_fast_ball(self):
        self.fast_ball_timer = POWER_DURATION

    def draw(self, screen):
        color = YELLOW if self.fast_ball_timer > 0 else WHITE
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), BALL_SIZE // 2)

    def get_rect(self):
        return pygame.Rect(
            self.x - BALL_SIZE // 2, self.y - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE
        )

    def is_below_screen(self):
        return self.y > SCREEN_HEIGHT


class Brick:
    def __init__(self, x, y, color, power_type=None):
        self.x = x
        self.y = y
        self.width = BRICK_WIDTH
        self.height = BRICK_HEIGHT
        self.color = color
        self.power_type = (
            power_type  # None, 'big_paddle', 'fast_ball', 'bonus_points', 'multiball'
        )
        self.destroyed = False

    def draw(self, screen):
        if not self.destroyed:
            # Draw main brick
            pygame.draw.rect(
                screen, self.color, (self.x, self.y, self.width, self.height)
            )
            pygame.draw.rect(
                screen, BLACK, (self.x, self.y, self.width, self.height), 2
            )

            # Draw power-up indicator
            if self.power_type:
                center_x = self.x + self.width // 2
                center_y = self.y + self.height // 2
                if self.power_type == "big_paddle":
                    pygame.draw.circle(screen, WHITE, (center_x, center_y), 8)
                    pygame.draw.circle(screen, ORANGE, (center_x, center_y), 6)
                elif self.power_type == "fast_ball":
                    pygame.draw.circle(screen, WHITE, (center_x, center_y), 8)
                    pygame.draw.circle(screen, YELLOW, (center_x, center_y), 6)
                elif self.power_type == "bonus_points":
                    pygame.draw.circle(screen, WHITE, (center_x, center_y), 8)
                    pygame.draw.circle(screen, PURPLE, (center_x, center_y), 6)
                elif self.power_type == "multiball":
                    pygame.draw.circle(screen, WHITE, (center_x, center_y), 8)
                    pygame.draw.circle(screen, CYAN, (center_x, center_y), 6)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Breakout - Power Multiball Remix")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.reset_game()

    def reset_game(self):
        self.paddle = Paddle()
        self.balls = [Ball()]  # Start with one ball
        self.bricks = []
        self.score = 0
        self.game_over = False
        self.won = False
        self.create_bricks()

    def create_bricks(self):
        colors = [RED, RED, YELLOW, YELLOW, BLUE, BLUE]
        power_types = ["big_paddle", "fast_ball", "bonus_points", "multiball"]
        start_x = (
            SCREEN_WIDTH - (BRICK_COLS * (BRICK_WIDTH + BRICK_PADDING) - BRICK_PADDING)
        ) // 2
        start_y = 50

        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLS):
                x = start_x + col * (BRICK_WIDTH + BRICK_PADDING)
                y = start_y + row * (BRICK_HEIGHT + BRICK_PADDING)
                color = colors[row % len(colors)]

                # 20% chance for power-up brick
                power_type = (
                    random.choice(power_types) if random.random() < 0.2 else None
                )

                self.bricks.append(Brick(x, y, color, power_type))

    def spawn_new_ball(self, x, y):
        """Spawn a new ball at the given position"""
        new_ball = Ball(x, y)
        # Give it a random direction
        new_ball.vel_x = random.choice([-BALL_SPEED, BALL_SPEED])
        new_ball.vel_y = random.choice([-BALL_SPEED, BALL_SPEED])
        self.balls.append(new_ball)

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

            # Update all balls
            for ball in self.balls[:]:
                ball.update()

                # Ball-paddle collision
                if (
                    ball.get_rect().colliderect(self.paddle.get_rect())
                    and ball.vel_y > 0
                ):
                    ball.vel_y = -ball.vel_y
                    # Add some angle based on where ball hits paddle
                    hit_pos = (ball.x - self.paddle.x) / self.paddle.width
                    ball.vel_x = BALL_SPEED * (hit_pos - 0.5) * 2

                # Ball-brick collisions
                for brick in self.bricks:
                    if not brick.destroyed and ball.get_rect().colliderect(
                        brick.get_rect()
                    ):
                        brick.destroyed = True
                        ball.vel_y = -ball.vel_y

                        # Handle power-ups
                        if brick.power_type == "big_paddle":
                            self.paddle.activate_big_paddle()
                            self.score += 20
                        elif brick.power_type == "fast_ball":
                            # Apply fast ball to all balls
                            for b in self.balls:
                                b.activate_fast_ball()
                            self.score += 20
                        elif brick.power_type == "bonus_points":
                            self.score += 50
                        elif brick.power_type == "multiball":
                            # Spawn a new ball at the brick location
                            self.spawn_new_ball(
                                brick.x + brick.width // 2, brick.y + brick.height // 2
                            )
                            self.score += 30
                        else:
                            self.score += 10
                        break

                # Remove balls that fall below screen
                if ball.is_below_screen():
                    self.balls.remove(ball)

            # Check win condition
            if all(brick.destroyed for brick in self.bricks):
                self.game_over = True
                self.won = True

            # Check lose condition (no balls left)
            if not self.balls:
                self.game_over = True

    def draw(self):
        self.screen.fill(BLACK)

        # Draw game objects
        self.paddle.draw(self.screen)
        for ball in self.balls:
            ball.draw(self.screen)
        for brick in self.bricks:
            brick.draw(self.screen)

        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # Draw power-up status
        y_offset = 50
        if self.paddle.big_paddle_timer > 0:
            paddle_text = self.font.render("Big Paddle Active!", True, ORANGE)
            self.screen.blit(paddle_text, (10, y_offset))
            y_offset += 30

        # Check if any ball has fast ball active
        fast_ball_active = any(ball.fast_ball_timer > 0 for ball in self.balls)
        if fast_ball_active:
            ball_text = self.font.render("Fast Ball Active!", True, YELLOW)
            self.screen.blit(ball_text, (10, y_offset))

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
