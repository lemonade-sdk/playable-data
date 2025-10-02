# CREATE: pong vs computer

"""
Pong vs Computer Game

A single-player Pong game where you play against a computer-controlled opponent.
The left paddle is controlled by AI that follows the ball, while the player
controls the right paddle. The AI has some limitations to keep it beatable,
creating challenging but fair gameplay. Perfect for solo practice or when
you need an opponent that's always available.

Implementation uses pygame with AI opponent mechanics and balanced difficulty.
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
AI_SPEED = 6  # AI paddle moves slightly slower than player
BALL_SPEED = 5
WINNING_SCORE = 5

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 65)
BLUE = (100, 150, 255)  # AI paddle color


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pong Game - VS Computer")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 24)
        self.reset_game()

    def reset_game(self):
        # Paddle positions
        self.left_paddle_y = WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.right_paddle_y = WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2

        # Ball position and velocity
        self.ball_x = WINDOW_WIDTH // 2
        self.ball_y = WINDOW_HEIGHT // 2
        self.ball_vel_x = BALL_SPEED if pygame.time.get_ticks() % 2 else -BALL_SPEED
        self.ball_vel_y = BALL_SPEED * 0.5

        # Scores
        self.ai_score = 0
        self.player_score = 0
        self.game_over = False
        self.winner = None

    def update_ai_paddle(self):
        # AI follows the ball with some limitations for balanced gameplay
        ball_center_y = self.ball_y + BALL_SIZE // 2
        paddle_center_y = self.left_paddle_y + PADDLE_HEIGHT // 2

        # Only move AI paddle when ball is coming toward it
        if self.ball_vel_x < 0:  # Ball moving toward AI paddle
            if ball_center_y < paddle_center_y - 10:  # Dead zone for imperfection
                if self.left_paddle_y > 0:
                    self.left_paddle_y -= AI_SPEED
            elif ball_center_y > paddle_center_y + 10:  # Dead zone for imperfection
                if self.left_paddle_y < WINDOW_HEIGHT - PADDLE_HEIGHT:
                    self.left_paddle_y += AI_SPEED

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

        # Player paddle controls (right paddle only)
        if not self.game_over:
            keys = pygame.key.get_pressed()

            # Right paddle (Up/Down arrows or W/S)
            if (keys[pygame.K_UP] or keys[pygame.K_w]) and self.right_paddle_y > 0:
                self.right_paddle_y -= PADDLE_SPEED
            if (
                keys[pygame.K_DOWN] or keys[pygame.K_s]
            ) and self.right_paddle_y < WINDOW_HEIGHT - PADDLE_HEIGHT:
                self.right_paddle_y += PADDLE_SPEED

        return True

    def update(self):
        if not self.game_over:
            # Update AI paddle
            self.update_ai_paddle()

            # Move ball
            self.ball_x += self.ball_vel_x
            self.ball_y += self.ball_vel_y

            # Ball collision with top/bottom walls
            if self.ball_y <= 0 or self.ball_y >= WINDOW_HEIGHT - BALL_SIZE:
                self.ball_vel_y = -self.ball_vel_y

            # Ball collision with left paddle (AI)
            if (
                self.ball_x <= 30 + PADDLE_WIDTH
                and self.ball_vel_x < 0
                and self.left_paddle_y
                <= self.ball_y
                <= self.left_paddle_y + PADDLE_HEIGHT
            ):
                self.ball_vel_x = -self.ball_vel_x

            # Ball collision with right paddle (Player)
            if (
                self.ball_x >= WINDOW_WIDTH - 30 - PADDLE_WIDTH - BALL_SIZE
                and self.ball_vel_x > 0
                and self.right_paddle_y
                <= self.ball_y
                <= self.right_paddle_y + PADDLE_HEIGHT
            ):
                self.ball_vel_x = -self.ball_vel_x

            # Scoring
            if self.ball_x < 0:
                self.player_score += 1
                self.ball_x = WINDOW_WIDTH // 2
                self.ball_y = WINDOW_HEIGHT // 2
                self.ball_vel_x = BALL_SPEED
            elif self.ball_x > WINDOW_WIDTH:
                self.ai_score += 1
                self.ball_x = WINDOW_WIDTH // 2
                self.ball_y = WINDOW_HEIGHT // 2
                self.ball_vel_x = -BALL_SPEED

            # Check win condition
            if self.ai_score >= WINNING_SCORE:
                self.game_over = True
                self.winner = "Computer Wins!"
            elif self.player_score >= WINNING_SCORE:
                self.game_over = True
                self.winner = "You Win!"

    def draw(self):
        self.screen.fill(BLACK)

        # Draw center line
        for y in range(0, WINDOW_HEIGHT, 20):
            pygame.draw.rect(self.screen, WHITE, (WINDOW_WIDTH // 2 - 2, y, 4, 10))

        # Draw AI paddle (left, blue)
        pygame.draw.rect(
            self.screen, BLUE, (30, self.left_paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT)
        )

        # Draw player paddle (right, white)
        pygame.draw.rect(
            self.screen,
            WHITE,
            (
                WINDOW_WIDTH - 30 - PADDLE_WIDTH,
                self.right_paddle_y,
                PADDLE_WIDTH,
                PADDLE_HEIGHT,
            ),
        )

        # Draw ball
        pygame.draw.rect(
            self.screen, WHITE, (self.ball_x, self.ball_y, BALL_SIZE, BALL_SIZE)
        )

        # Draw scores with labels
        ai_text = self.font.render(str(self.ai_score), True, BLUE)
        player_text = self.font.render(str(self.player_score), True, WHITE)
        self.screen.blit(ai_text, (WINDOW_WIDTH // 4, 50))
        self.screen.blit(player_text, (3 * WINDOW_WIDTH // 4, 50))

        # Draw labels
        ai_label = self.small_font.render("Computer", True, BLUE)
        player_label = self.small_font.render("You", True, WHITE)
        self.screen.blit(ai_label, (WINDOW_WIDTH // 4 - 30, 20))
        self.screen.blit(player_label, (3 * WINDOW_WIDTH // 4 - 15, 20))

        # Draw game over screen
        if self.game_over:
            winner_color = GREEN if "You Win" in self.winner else WHITE
            winner_text = self.font.render(self.winner, True, winner_color)
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
