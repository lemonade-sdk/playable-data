# SOURCE: pong.py
# REMIX: paddles can move in 2 dimensions

"""
Pong Game - 2D Paddles Remix

A remix of classic Pong where paddles can move in both dimensions (up/down and left/right).
Each paddle is restricted to its own half of the court and cannot cross the center line.
This adds a new strategic element to positioning and ball interception.

Remixed from the original Pong game implementation.
"""

import pygame
import sys

# Initialize pygame
pygame.init()

# Game constants
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 80
BALL_SIZE = 15
PADDLE_SPEED = 8
BALL_SPEED = 5
WINNING_SCORE = 5

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 65)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pong Game - 2D Paddles Remix")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 24)
        self.reset_game()

    def reset_game(self):
        # Paddle positions (x, y)
        self.left_paddle_x = 30
        self.left_paddle_y = WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.right_paddle_x = WINDOW_WIDTH - 30 - PADDLE_WIDTH
        self.right_paddle_y = WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2

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

            # Left paddle (WASD)
            if keys[pygame.K_w] and self.left_paddle_y > 0:
                self.left_paddle_y -= PADDLE_SPEED
            if keys[pygame.K_s] and self.left_paddle_y < WINDOW_HEIGHT - PADDLE_HEIGHT:
                self.left_paddle_y += PADDLE_SPEED
            if keys[pygame.K_a] and self.left_paddle_x > 0:
                self.left_paddle_x -= PADDLE_SPEED
            if (
                keys[pygame.K_d]
                and self.left_paddle_x < WINDOW_WIDTH // 2 - PADDLE_WIDTH
            ):
                self.left_paddle_x += PADDLE_SPEED

            # Right paddle (Arrow keys)
            if keys[pygame.K_UP] and self.right_paddle_y > 0:
                self.right_paddle_y -= PADDLE_SPEED
            if (
                keys[pygame.K_DOWN]
                and self.right_paddle_y < WINDOW_HEIGHT - PADDLE_HEIGHT
            ):
                self.right_paddle_y += PADDLE_SPEED
            if keys[pygame.K_LEFT] and self.right_paddle_x > WINDOW_WIDTH // 2:
                self.right_paddle_x -= PADDLE_SPEED
            if (
                keys[pygame.K_RIGHT]
                and self.right_paddle_x < WINDOW_WIDTH - PADDLE_WIDTH
            ):
                self.right_paddle_x += PADDLE_SPEED

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
                self.ball_x <= self.left_paddle_x + PADDLE_WIDTH
                and self.ball_x >= self.left_paddle_x
                and self.ball_vel_x < 0
                and self.left_paddle_y
                <= self.ball_y
                <= self.left_paddle_y + PADDLE_HEIGHT
            ):
                self.ball_vel_x = -self.ball_vel_x

            # Ball collision with right paddle
            if (
                self.ball_x + BALL_SIZE >= self.right_paddle_x
                and self.ball_x <= self.right_paddle_x + PADDLE_WIDTH
                and self.ball_vel_x > 0
                and self.right_paddle_y
                <= self.ball_y
                <= self.right_paddle_y + PADDLE_HEIGHT
            ):
                self.ball_vel_x = -self.ball_vel_x

            # Scoring
            if self.ball_x < 0:
                self.right_score += 1
                self.ball_x = WINDOW_WIDTH // 2
                self.ball_y = WINDOW_HEIGHT // 2
                self.ball_vel_x = BALL_SPEED
            elif self.ball_x > WINDOW_WIDTH:
                self.left_score += 1
                self.ball_x = WINDOW_WIDTH // 2
                self.ball_y = WINDOW_HEIGHT // 2
                self.ball_vel_x = -BALL_SPEED

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

        # Draw paddles at their 2D positions
        pygame.draw.rect(
            self.screen,
            WHITE,
            (self.left_paddle_x, self.left_paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT),
        )
        pygame.draw.rect(
            self.screen,
            WHITE,
            (self.right_paddle_x, self.right_paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT),
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

        # Draw control instructions
        controls_text = self.small_font.render(
            "Left: WASD  |  Right: Arrow Keys", True, WHITE
        )
        controls_rect = controls_text.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30)
        )
        self.screen.blit(controls_text, controls_rect)

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
