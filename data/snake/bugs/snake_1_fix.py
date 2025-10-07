# CREATE: snake

"""
Snake Game

Classic snake game where the player controls a snake that grows by eating food.
The game ends if the snake collides with walls or itself.
Features event-driven controls and organized class structure.

BUG FIX: In the collision detection method, when checking for self-collision, the
code tries to check if the head is in a single segment instead of a list of segments.
Look for where it checks collision with the snake's body.
"""

import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Display settings
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
CELL_SIZE = 25
COLUMNS = SCREEN_WIDTH // CELL_SIZE
ROWS = SCREEN_HEIGHT // CELL_SIZE

# Color definitions
COLOR_BLACK = (0, 0, 0)
COLOR_GREEN = (0, 255, 65)
COLOR_WHITE = (255, 255, 255)

# Movement directions
DIRECTION_UP = (0, -1)
DIRECTION_DOWN = (0, 1)
DIRECTION_LEFT = (-1, 0)
DIRECTION_RIGHT = (1, 0)


class SnakePlayer:
    """Represents the snake controlled by the player"""

    def __init__(self):
        start_col = COLUMNS // 2
        start_row = ROWS // 2
        self.segments = [(start_col, start_row)]
        self.current_direction = DIRECTION_RIGHT
        self.next_direction = DIRECTION_RIGHT
        self.should_grow_next_move = False

    def update_position(self):
        """Move the snake in its current direction"""
        self.current_direction = self.next_direction
        head_col, head_row = self.segments[0]
        new_head_col = head_col + self.current_direction[0]
        new_head_row = head_row + self.current_direction[1]
        new_head = (new_head_col, new_head_row)

        self.segments.insert(0, new_head)

        if not self.should_grow_next_move:
            self.segments.pop()
        else:
            self.should_grow_next_move = False

    def set_direction(self, new_direction):
        """Change snake direction, preventing 180-degree turns"""
        opposite_direction = (-self.current_direction[0], -self.current_direction[1])
        if new_direction != opposite_direction:
            self.next_direction = new_direction

    def mark_for_growth(self):
        """Mark snake to grow on next move"""
        self.should_grow_next_move = True

    def check_if_collision_occurred(self):
        """Check if snake hit a wall or itself"""
        head_col, head_row = self.segments[0]

        # Check wall collision
        if head_col < 0 or head_col >= COLUMNS:
            return True
        if head_row < 0 or head_row >= ROWS:
            return True

        # Check self collision
        # Fixed: use slicing self.segments[1:] to get list of body segments, not single element
        if self.segments[0] in self.segments[1:]:
            return True

        return False


class FoodItem:
    """Represents food that the snake can eat"""

    def __init__(self):
        self.grid_position = (0, 0)
        self.place_randomly()

    def place_randomly(self):
        """Place food at a random grid location"""
        col = random.randint(0, COLUMNS - 1)
        row = random.randint(0, ROWS - 1)
        self.grid_position = (col, row)

    def relocate_avoiding_snake(self, snake_segments):
        """Place food at location not occupied by snake"""
        while True:
            self.place_randomly()
            if self.grid_position not in snake_segments:
                break


class SnakeGame:
    """Main game controller"""

    def __init__(self):
        self.display_surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.game_clock = pygame.time.Clock()
        self.text_font = pygame.font.Font(None, 40)
        self.initialize_new_game()

    def initialize_new_game(self):
        """Reset game state for a new game"""
        self.snake_player = SnakePlayer()
        self.food_item = FoodItem()
        self.current_score = 0
        self.is_game_over = False

    def process_user_input(self):
        """Handle keyboard and window events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if self.is_game_over:
                    if event.key == pygame.K_r:
                        self.initialize_new_game()
                    elif event.key == pygame.K_q:
                        return False
                else:
                    if event.key == pygame.K_UP:
                        self.snake_player.set_direction(DIRECTION_UP)
                    elif event.key == pygame.K_DOWN:
                        self.snake_player.set_direction(DIRECTION_DOWN)
                    elif event.key == pygame.K_LEFT:
                        self.snake_player.set_direction(DIRECTION_LEFT)
                    elif event.key == pygame.K_RIGHT:
                        self.snake_player.set_direction(DIRECTION_RIGHT)

        return True

    def update_game_state(self):
        """Update all game objects"""
        if not self.is_game_over:
            self.snake_player.update_position()

            # Check if snake ate food
            if self.snake_player.segments[0] == self.food_item.grid_position:
                self.snake_player.mark_for_growth()
                self.food_item.relocate_avoiding_snake(self.snake_player.segments)
                self.current_score += 1

            # Check for game over
            if self.snake_player.check_if_collision_occurred():
                self.is_game_over = True

    def render_graphics(self):
        """Draw all game elements"""
        self.display_surface.fill(COLOR_BLACK)

        # Draw snake segments
        for segment_col, segment_row in self.snake_player.segments:
            pixel_x = segment_col * CELL_SIZE
            pixel_y = segment_row * CELL_SIZE
            pygame.draw.rect(
                self.display_surface,
                COLOR_GREEN,
                pygame.Rect(pixel_x, pixel_y, CELL_SIZE, CELL_SIZE),
            )

        # Draw food
        food_col, food_row = self.food_item.grid_position
        food_x = food_col * CELL_SIZE
        food_y = food_row * CELL_SIZE
        pygame.draw.rect(
            self.display_surface,
            COLOR_WHITE,
            pygame.Rect(food_x, food_y, CELL_SIZE, CELL_SIZE),
        )

        # Draw score
        score_surface = self.text_font.render(
            f"Score: {self.current_score}", True, COLOR_WHITE
        )
        self.display_surface.blit(score_surface, (10, 10))

        # Draw game over message
        if self.is_game_over:
            game_over_surface = self.text_font.render("Game Over!", True, COLOR_WHITE)
            restart_surface = self.text_font.render(
                "Press R to restart or Q to quit", True, COLOR_WHITE
            )

            game_over_rect = game_over_surface.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30)
            )
            restart_rect = restart_surface.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30)
            )

            self.display_surface.blit(game_over_surface, game_over_rect)
            self.display_surface.blit(restart_surface, restart_rect)

        pygame.display.flip()

    def run_game_loop(self):
        """Main game loop"""
        game_is_running = True
        while game_is_running:
            game_is_running = self.process_user_input()
            self.update_game_state()
            self.render_graphics()
            self.game_clock.tick(8)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = SnakeGame()
    game.run_game_loop()
