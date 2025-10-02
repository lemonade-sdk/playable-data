"""
Pong Game

Traditional pong game featuring two paddles and a bouncing ball. Players
compete by hitting the ball back and forth. Points are awarded when the
opponent fails to return the ball. Game continues until one player reaches
the winning score threshold.
"""

import pygame
import sys

# Initialize pygame module
pygame.init()

# Display configuration
DISPLAY_WIDTH = 650
DISPLAY_HEIGHT = 550
COLOR_BACKGROUND = (0, 0, 0)
COLOR_OBJECT = (255, 255, 255)
COLOR_WINNER = (0, 255, 65)

# Game object dimensions and speeds
PADDLE_WIDTH = 16
PADDLE_HEIGHT = 70
BALL_SIZE = 12
PADDLE_SPEED = 6
BALL_SPEED = 6.5
SCORE_LIMIT = 6


class PaddleEntity:
    """Represents a player's paddle in the game"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = PADDLE_WIDTH
        self.h = PADDLE_HEIGHT
        self.speed = PADDLE_SPEED

    def move_up(self):
        if self.y > 0:
            self.y -= self.speed

    def move_down(self):
        if self.y < DISPLAY_HEIGHT - self.h:
            self.y += self.speed

    def render(self, surface):
        pygame.draw.rect(surface, COLOR_OBJECT, (self.x, self.y, self.w, self.h))

    def contains_y(self, y_pos):
        """Check if y coordinate is within paddle bounds"""
        return self.y <= y_pos <= self.y + self.h


class BallEntity:
    """Represents the bouncing ball"""

    def __init__(self):
        self.x = DISPLAY_WIDTH // 2
        self.y = DISPLAY_HEIGHT // 2
        self.vx = BALL_SPEED
        self.vy = BALL_SPEED * 0.5
        self.radius = BALL_SIZE // 2

    def reset(self, direction):
        """Reset ball to center with given direction"""
        self.x = DISPLAY_WIDTH // 2
        self.y = DISPLAY_HEIGHT // 2
        self.vx = BALL_SPEED * direction
        self.vy = BALL_SPEED * 0.5

    def update(self):
        """Move ball according to velocity"""
        self.x += self.vx
        self.y += self.vy

    def bounce_x(self):
        self.vx = -self.vx

    def bounce_y(self):
        self.vy = -self.vy

    def render(self, surface):
        pygame.draw.circle(
            surface, COLOR_OBJECT, (int(self.x), int(self.y)), self.radius
        )


class GameController:
    """Main controller for pong game logic"""

    def __init__(self):
        self.screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        pygame.display.set_caption("Pong Game")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 50)
        self.font_medium = pygame.font.Font(None, 38)
        self.reset()

    def reset(self):
        """Setup game entities and state"""
        paddle_x_offset = 45
        start_y = DISPLAY_HEIGHT // 2 - PADDLE_HEIGHT // 2

        self.left_paddle = PaddleEntity(paddle_x_offset, start_y)
        self.right_paddle = PaddleEntity(
            DISPLAY_WIDTH - paddle_x_offset - PADDLE_WIDTH, start_y
        )
        self.ball = BallEntity()
        self.score_left = 0
        self.score_right = 0
        self.game_ended = False
        self.winner = ""

    def handle_input(self):
        """Process keyboard and window events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and self.game_ended:
                if event.key == pygame.K_r:
                    self.reset()
                elif event.key == pygame.K_q:
                    return False

        if not self.game_ended:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                self.left_paddle.move_up()
            if keys[pygame.K_s]:
                self.left_paddle.move_down()
            if keys[pygame.K_UP]:
                self.right_paddle.move_up()
            if keys[pygame.K_DOWN]:
                self.right_paddle.move_down()

        return True

    def update(self):
        """Update all game logic"""
        if self.game_ended:
            return

        self.ball.update()

        # Wall bounces
        if self.ball.y <= 0 or self.ball.y >= DISPLAY_HEIGHT:
            self.ball.bounce_y()

        # Paddle collisions
        if self.ball.vx < 0 and self.ball.x <= self.left_paddle.x + self.left_paddle.w:
            if self.left_paddle.contains_y(self.ball.y):
                self.ball.bounce_x()

        if self.ball.vx > 0 and self.ball.x >= self.right_paddle.x:
            if self.right_paddle.contains_y(self.ball.y):
                self.ball.bounce_x()

        # Scoring
        if self.ball.x < 0:
            self.score_right += 1
            self.ball.reset(1)
        elif self.ball.x > DISPLAY_WIDTH:
            self.score_left += 1
            self.ball.reset(-1)

        # Win condition
        if self.score_left >= SCORE_LIMIT:
            self.game_ended = True
            self.winner = "Left Player Wins!"
        elif self.score_right >= SCORE_LIMIT:
            self.game_ended = True
            self.winner = "Right Player Wins!"

    def render(self):
        """Draw all visual elements"""
        self.screen.fill(COLOR_BACKGROUND)

        # Center divider
        for y in range(0, DISPLAY_HEIGHT, 20):
            pygame.draw.rect(
                self.screen, COLOR_OBJECT, (DISPLAY_WIDTH // 2 - 2, y, 4, 15)
            )

        # Game objects
        self.left_paddle.render(self.screen)
        self.right_paddle.render(self.screen)
        self.ball.render(self.screen)

        # Scores
        left_text = self.font_large.render(str(self.score_left), True, COLOR_OBJECT)
        right_text = self.font_large.render(str(self.score_right), True, COLOR_OBJECT)
        self.screen.blit(left_text, (DISPLAY_WIDTH // 4 - 15, 35))
        self.screen.blit(right_text, (3 * DISPLAY_WIDTH // 4 - 15, 35))

        # Game over screen
        if self.game_ended:
            winner_text = self.font_medium.render(self.winner, True, COLOR_WINNER)
            info_text = self.font_medium.render(
                "Press R to restart or Q to quit", True, COLOR_OBJECT
            )

            winner_rect = winner_text.get_rect(
                center=(DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2 - 28)
            )
            info_rect = info_text.get_rect(
                center=(DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2 + 28)
            )

            self.screen.blit(winner_text, winner_rect)
            self.screen.blit(info_text, info_rect)

        pygame.display.flip()

    def run(self):
        """Execute main game loop"""
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.render()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = GameController()
    game.run()
