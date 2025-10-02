# CREATE: pong where the paddles shrink when they hit the ball

"""
Pong Shrinking Paddles Game

A two-player paddle game where paddles decrease in size each time they make contact
with the ball, creating progressively more difficult gameplay during rallies.
Smaller paddles make ball interception more challenging as the game continues.
Implementation uses pygame with collision detection, paddle size modification,
and dynamic difficulty scaling.
"""

import pygame
import sys

# Initialize pygame
pygame.init()

# Game constants
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
PADDLE_WIDTH = 15
INITIAL_PADDLE_HEIGHT = 80
MIN_PADDLE_HEIGHT = 20  # Minimum size to prevent disappearing
BALL_SIZE = 15
PADDLE_SPEED = 8
BALL_SPEED = 5
PADDLE_SHRINK = 6  # How much paddles shrink per hit
WINNING_SCORE = 5

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 65)
RED = (255, 100, 100)  # Color for small paddles


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pong Game - Shrinking Paddles Remix")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)
        self.reset_game()

    def reset_game(self):
        # Paddle positions and sizes
        self.left_paddle_y = WINDOW_HEIGHT // 2 - INITIAL_PADDLE_HEIGHT // 2
        self.right_paddle_y = WINDOW_HEIGHT // 2 - INITIAL_PADDLE_HEIGHT // 2
        self.left_paddle_height = INITIAL_PADDLE_HEIGHT
        self.right_paddle_height = INITIAL_PADDLE_HEIGHT

        # Ball position and velocity
        self.ball_x = WINDOW_WIDTH // 2
        self.ball_y = WINDOW_HEIGHT // 2
        self.ball_vel_x = BALL_SPEED if pygame.time.get_ticks() % 2 else -BALL_SPEED
        self.ball_vel_y = BALL_SPEED * 0.5

        # Scores
        self.left_score = 0
        self.right_score = 0
        self.game_over = False
        self.winner = None

    def shrink_paddle(self, paddle_side):
        # Shrink the paddle that hit the ball
        if paddle_side == "left" and self.left_paddle_height > MIN_PADDLE_HEIGHT:
            old_height = self.left_paddle_height
            self.left_paddle_height -= PADDLE_SHRINK
            # Adjust Y position to keep paddle centered
            self.left_paddle_y += (old_height - self.left_paddle_height) // 2
        elif paddle_side == "right" and self.right_paddle_height > MIN_PADDLE_HEIGHT:
            old_height = self.right_paddle_height
            self.right_paddle_height -= PADDLE_SHRINK
            # Adjust Y position to keep paddle centered
            self.right_paddle_y += (old_height - self.right_paddle_height) // 2

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_q:
                        return False

        # Paddle controls
        if not self.game_over:
            keys = pygame.key.get_pressed()

            # Left paddle (W/S)
            if keys[pygame.K_w] and self.left_paddle_y > 0:
                self.left_paddle_y -= PADDLE_SPEED
            if (
                keys[pygame.K_s]
                and self.left_paddle_y < WINDOW_HEIGHT - self.left_paddle_height
            ):
                self.left_paddle_y += PADDLE_SPEED

            # Right paddle (Up/Down)
            if keys[pygame.K_UP] and self.right_paddle_y > 0:
                self.right_paddle_y -= PADDLE_SPEED
            if (
                keys[pygame.K_DOWN]
                and self.right_paddle_y < WINDOW_HEIGHT - self.right_paddle_height
            ):
                self.right_paddle_y += PADDLE_SPEED

        return True

    def update(self):
        if not self.game_over:
            # Move ball
            self.ball_x += self.ball_vel_x
            self.ball_y += self.ball_vel_y

            # Ball collision with top/bottom walls
            if self.ball_y <= 0 or self.ball_y >= WINDOW_HEIGHT - BALL_SIZE:
                self.ball_vel_y = -self.ball_vel_y

            # Ball collision with left paddle
            if (
                self.ball_x <= 30 + PADDLE_WIDTH
                and self.ball_vel_x < 0
                and self.left_paddle_y
                <= self.ball_y
                <= self.left_paddle_y + self.left_paddle_height
            ):
                self.ball_vel_x = -self.ball_vel_x
                self.shrink_paddle("left")  # Shrink left paddle

            # Ball collision with right paddle
            if (
                self.ball_x >= WINDOW_WIDTH - 30 - PADDLE_WIDTH - BALL_SIZE
                and self.ball_vel_x > 0
                and self.right_paddle_y
                <= self.ball_y
                <= self.right_paddle_y + self.right_paddle_height
            ):
                self.ball_vel_x = -self.ball_vel_x
                self.shrink_paddle("right")  # Shrink right paddle

            # Scoring
            if self.ball_x < 0:
                self.right_score += 1
                self.ball_x = WINDOW_WIDTH // 2
                self.ball_y = WINDOW_HEIGHT // 2
                self.ball_vel_x = BALL_SPEED
                # Reset paddle sizes after scoring
                self.left_paddle_height = INITIAL_PADDLE_HEIGHT
                self.right_paddle_height = INITIAL_PADDLE_HEIGHT
                self.left_paddle_y = WINDOW_HEIGHT // 2 - INITIAL_PADDLE_HEIGHT // 2
                self.right_paddle_y = WINDOW_HEIGHT // 2 - INITIAL_PADDLE_HEIGHT // 2
            elif self.ball_x > WINDOW_WIDTH:
                self.left_score += 1
                self.ball_x = WINDOW_WIDTH // 2
                self.ball_y = WINDOW_HEIGHT // 2
                self.ball_vel_x = -BALL_SPEED
                # Reset paddle sizes after scoring
                self.left_paddle_height = INITIAL_PADDLE_HEIGHT
                self.right_paddle_height = INITIAL_PADDLE_HEIGHT
                self.left_paddle_y = WINDOW_HEIGHT // 2 - INITIAL_PADDLE_HEIGHT // 2
                self.right_paddle_y = WINDOW_HEIGHT // 2 - INITIAL_PADDLE_HEIGHT // 2

            # Check win condition
            if self.left_score >= WINNING_SCORE:
                self.game_over = True
                self.winner = "Left Player Wins!"
            elif self.right_score >= WINNING_SCORE:
                self.game_over = True
                self.winner = "Right Player Wins!"

    def draw(self):
        self.screen.fill(BLACK)

        # Draw center line
        for y in range(0, WINDOW_HEIGHT, 20):
            pygame.draw.rect(self.screen, WHITE, (WINDOW_WIDTH // 2 - 2, y, 4, 10))

        # Draw paddles with dynamic colors based on size
        left_color = RED if self.left_paddle_height <= MIN_PADDLE_HEIGHT + 10 else WHITE
        right_color = (
            RED if self.right_paddle_height <= MIN_PADDLE_HEIGHT + 10 else WHITE
        )

        pygame.draw.rect(
            self.screen,
            left_color,
            (30, self.left_paddle_y, PADDLE_WIDTH, self.left_paddle_height),
        )
        pygame.draw.rect(
            self.screen,
            right_color,
            (
                WINDOW_WIDTH - 30 - PADDLE_WIDTH,
                self.right_paddle_y,
                PADDLE_WIDTH,
                self.right_paddle_height,
            ),
        )

        # Draw ball
        pygame.draw.rect(
            self.screen, WHITE, (self.ball_x, self.ball_y, BALL_SIZE, BALL_SIZE)
        )

        # Draw scores
        left_text = self.font.render(str(self.left_score), True, WHITE)
        right_text = self.font.render(str(self.right_score), True, WHITE)
        self.screen.blit(left_text, (WINDOW_WIDTH // 4, 50))
        self.screen.blit(right_text, (3 * WINDOW_WIDTH // 4, 50))

        # Draw game over screen
        if self.game_over:
            winner_text = self.font.render(self.winner, True, GREEN)
            restart_text = self.font.render(
                "Press R to restart or Q to quit", True, WHITE
            )

            winner_rect = winner_text.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30)
            )
            restart_rect = restart_text.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30)
            )

            self.screen.blit(winner_text, winner_rect)
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


# Main execution
if __name__ == "__main__":
    game = Game()
    game.run()
