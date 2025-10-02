"""
Pong Game

Classic two-player pong game implemented with pygame. Players control paddles
on opposite sides of the screen, bouncing a ball back and forth. Score points
when opponent misses. First player to reach the target score wins.
"""

import pygame
import sys

# Initialize pygame
pygame.init()

# Display settings
SCREEN_WIDTH = 700
SCREEN_HEIGHT = 500
BACKGROUND_COLOR = (0, 0, 0)
FOREGROUND_COLOR = (255, 255, 255)
HIGHLIGHT_COLOR = (0, 255, 65)

# Gameplay constants
PADDLE_WIDTH = 12
PADDLE_HEIGHT = 90
BALL_RADIUS = 8
PADDLE_VELOCITY = 7
BALL_INITIAL_SPEED = 4.5
POINTS_TO_WIN = 7


class PaddleController:
    """Represents a player's paddle"""

    def __init__(self, position_x):
        self.x = position_x
        self.y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.velocity = PADDLE_VELOCITY

    def move_upward(self):
        """Move paddle up within bounds"""
        if self.y > 0:
            self.y -= self.velocity

    def move_downward(self):
        """Move paddle down within bounds"""
        if self.y < SCREEN_HEIGHT - self.height:
            self.y += self.velocity

    def render_to_screen(self, display):
        """Draw the paddle"""
        pygame.draw.rect(
            display, FOREGROUND_COLOR, (self.x, self.y, self.width, self.height)
        )

    def get_center_y(self):
        """Return vertical center of paddle"""
        return self.y + self.height // 2


class BallObject:
    """Represents the pong ball"""

    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.radius = BALL_RADIUS
        self.velocity_x = BALL_INITIAL_SPEED
        self.velocity_y = BALL_INITIAL_SPEED * 0.6

    def update_position(self):
        """Move ball based on velocity"""
        self.x += self.velocity_x
        self.y += self.velocity_y

    def bounce_vertically(self):
        """Reverse vertical direction"""
        self.velocity_y = -self.velocity_y

    def bounce_horizontally(self):
        """Reverse horizontal direction"""
        self.velocity_x = -self.velocity_x

    def reset_to_center(self, direction):
        """Reset ball position after scoring"""
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.velocity_x = BALL_INITIAL_SPEED * direction
        self.velocity_y = BALL_INITIAL_SPEED * 0.6

    def render_to_screen(self, display):
        """Draw the ball"""
        pygame.draw.circle(
            display, FOREGROUND_COLOR, (int(self.x), int(self.y)), self.radius
        )


class PongGame:
    """Main game controller"""

    def __init__(self):
        self.display = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pong Game")
        self.clock = pygame.time.Clock()
        self.score_font = pygame.font.Font(None, 56)
        self.message_font = pygame.font.Font(None, 40)
        self.initialize_game()

    def initialize_game(self):
        """Setup game objects and state"""
        self.left_paddle = PaddleController(40)
        self.right_paddle = PaddleController(SCREEN_WIDTH - 40 - PADDLE_WIDTH)
        self.ball = BallObject()
        self.left_player_score = 0
        self.right_player_score = 0
        self.game_finished = False
        self.winning_message = ""

    def process_input(self):
        """Handle user input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if self.game_finished:
                    if event.key == pygame.K_r:
                        self.initialize_game()
                    elif event.key == pygame.K_q:
                        return False

        if not self.game_finished:
            keys_pressed = pygame.key.get_pressed()

            # Left paddle controls (W/S)
            if keys_pressed[pygame.K_w]:
                self.left_paddle.move_upward()
            if keys_pressed[pygame.K_s]:
                self.left_paddle.move_downward()

            # Right paddle controls (Up/Down arrows)
            if keys_pressed[pygame.K_UP]:
                self.right_paddle.move_upward()
            if keys_pressed[pygame.K_DOWN]:
                self.right_paddle.move_downward()

        return True

    def update_game_state(self):
        """Update game logic"""
        if self.game_finished:
            return

        self.ball.update_position()
        self.check_wall_collisions()
        self.check_paddle_collisions()
        self.check_scoring()
        self.check_win_condition()

    def check_wall_collisions(self):
        """Check if ball hits top or bottom wall"""
        if self.ball.y - self.ball.radius <= 0:
            self.ball.y = self.ball.radius
            self.ball.bounce_vertically()
        elif self.ball.y + self.ball.radius >= SCREEN_HEIGHT:
            self.ball.y = SCREEN_HEIGHT - self.ball.radius
            self.ball.bounce_vertically()

    def check_paddle_collisions(self):
        """Check if ball collides with paddles"""
        # Left paddle collision
        if (
            self.ball.velocity_x < 0
            and self.ball.x - self.ball.radius
            <= self.left_paddle.x + self.left_paddle.width
            and self.left_paddle.y
            <= self.ball.y
            <= self.left_paddle.y + self.left_paddle.height
        ):
            self.ball.x = self.left_paddle.x + self.left_paddle.width + self.ball.radius
            self.ball.bounce_horizontally()

        # Right paddle collision
        if (
            self.ball.velocity_x > 0
            and self.ball.x + self.ball.radius >= self.right_paddle.x
            and self.right_paddle.y
            <= self.ball.y
            <= self.right_paddle.y + self.right_paddle.height
        ):
            self.ball.x = self.right_paddle.x - self.ball.radius
            self.ball.bounce_horizontally()

    def check_scoring(self):
        """Check if ball went past paddles"""
        if self.ball.x < 0:
            # Right player scores
            self.right_player_score += 1
            self.ball.reset_to_center(1)
        elif self.ball.x > SCREEN_WIDTH:
            # Left player scores
            self.left_player_score += 1
            self.ball.reset_to_center(-1)

    def check_win_condition(self):
        """Check if game has been won"""
        if self.left_player_score >= POINTS_TO_WIN:
            self.game_finished = True
            self.winning_message = "Left Player Wins!"
        elif self.right_player_score >= POINTS_TO_WIN:
            self.game_finished = True
            self.winning_message = "Right Player Wins!"

    def render_graphics(self):
        """Draw all visual elements"""
        self.display.fill(BACKGROUND_COLOR)
        self.draw_center_line()
        self.left_paddle.render_to_screen(self.display)
        self.right_paddle.render_to_screen(self.display)
        self.ball.render_to_screen(self.display)
        self.draw_scores()

        if self.game_finished:
            self.draw_game_over_screen()

        pygame.display.flip()

    def draw_center_line(self):
        """Draw dashed line in center"""
        for y in range(0, SCREEN_HEIGHT, 25):
            pygame.draw.rect(
                self.display, FOREGROUND_COLOR, (SCREEN_WIDTH // 2 - 2, y, 4, 12)
            )

    def draw_scores(self):
        """Draw player scores"""
        left_score_text = self.score_font.render(
            str(self.left_player_score), True, FOREGROUND_COLOR
        )
        right_score_text = self.score_font.render(
            str(self.right_player_score), True, FOREGROUND_COLOR
        )
        self.display.blit(left_score_text, (SCREEN_WIDTH // 4 - 20, 40))
        self.display.blit(right_score_text, (3 * SCREEN_WIDTH // 4 - 20, 40))

    def draw_game_over_screen(self):
        """Draw end game message"""
        winner_surface = self.message_font.render(
            self.winning_message, True, HIGHLIGHT_COLOR
        )
        instruction_surface = self.message_font.render(
            "Press R to restart or Q to quit", True, FOREGROUND_COLOR
        )

        winner_rect = winner_surface.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30)
        )
        instruction_rect = instruction_surface.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30)
        )

        self.display.blit(winner_surface, winner_rect)
        self.display.blit(instruction_surface, instruction_rect)

    def run_game_loop(self):
        """Main game loop"""
        running = True
        while running:
            running = self.process_input()
            self.update_game_state()
            self.render_graphics()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = PongGame()
    game.run_game_loop()
