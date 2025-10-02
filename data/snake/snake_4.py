# CREATE: snake

"""
Snake Game

Implementation of the classic Snake game using pygame. Control a snake to
eat food and grow longer while avoiding walls and self-collision. Built
with clean OOP architecture suitable for game development learning.
"""

import pygame
import random
import sys

# Initialize pygame systems
pygame.init()

# Window dimensions
DISPLAY_WIDTH = 640
DISPLAY_HEIGHT = 480
BLOCK_SIZE = 16
NUM_COLS = DISPLAY_WIDTH // BLOCK_SIZE
NUM_ROWS = DISPLAY_HEIGHT // BLOCK_SIZE

# Game colors
COLOR_BACKGROUND = (0, 0, 0)
COLOR_SNAKE = (0, 255, 65)
COLOR_FOOD = (255, 255, 255)

# Direction constants
MOVE_UP = (0, -1)
MOVE_DOWN = (0, 1)
MOVE_LEFT = (-1, 0)
MOVE_RIGHT = (1, 0)


class SnakeBody:
    """
    Manages the snake's body segments and movement logic.
    """

    def __init__(self):
        initial_x = NUM_COLS // 2
        initial_y = NUM_ROWS // 2
        self.segments = [(initial_x, initial_y)]
        self.direction = MOVE_RIGHT
        self.needs_to_grow = False

    def change_direction(self, new_dir):
        """
        Update movement direction, preventing backward movement.
        """
        reverse_dir = (-self.direction[0], -self.direction[1])
        if new_dir != reverse_dir:
            self.direction = new_dir

    def process_movement(self):
        """
        Move snake forward by one block in current direction.
        """
        current_head = self.segments[0]
        new_x = current_head[0] + self.direction[0]
        new_y = current_head[1] + self.direction[1]
        new_head = (new_x, new_y)

        self.segments.insert(0, new_head)

        if not self.needs_to_grow:
            self.segments.pop()
        else:
            self.needs_to_grow = False

    def trigger_growth(self):
        """
        Mark snake to grow by one segment.
        """
        self.needs_to_grow = True

    def has_wall_collision(self):
        """
        Check if snake head is outside boundaries.
        """
        head_x, head_y = self.segments[0]
        return head_x < 0 or head_x >= NUM_COLS or head_y < 0 or head_y >= NUM_ROWS

    def has_self_collision(self):
        """
        Check if snake head overlaps with body.
        """
        return self.segments[0] in self.segments[1:]


class FoodPellet:
    """
    Manages food position and spawning.
    """

    def __init__(self):
        self.position = (0, 0)
        self.generate_position()

    def generate_position(self):
        """
        Create random position for food.
        """
        x = random.randint(0, NUM_COLS - 1)
        y = random.randint(0, NUM_ROWS - 1)
        self.position = (x, y)

    def respawn(self, occupied_cells):
        """
        Generate new position avoiding occupied cells.
        """
        while True:
            self.generate_position()
            if self.position not in occupied_cells:
                break


class SnakeGameEngine:
    """
    Core game engine managing state, rendering, and game loop.
    """

    def __init__(self):
        # Setup display
        self.screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        pygame.display.set_caption("Snake Game")

        # Game systems
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)

        # Initialize game state
        self.restart_game()

    def restart_game(self):
        """
        Reset all game objects to initial state.
        """
        self.snake = SnakeBody()
        self.food = FoodPellet()
        self.score = 0
        self.is_over = False

    def handle_events(self):
        """
        Process user input and window events.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if self.is_over:
                    # Game over controls
                    if event.key == pygame.K_r:
                        self.restart_game()
                    elif event.key == pygame.K_q:
                        return False
                else:
                    # Movement controls
                    if event.key == pygame.K_UP:
                        self.snake.change_direction(MOVE_UP)
                    elif event.key == pygame.K_DOWN:
                        self.snake.change_direction(MOVE_DOWN)
                    elif event.key == pygame.K_LEFT:
                        self.snake.change_direction(MOVE_LEFT)
                    elif event.key == pygame.K_RIGHT:
                        self.snake.change_direction(MOVE_RIGHT)

        return True

    def process(self):
        """
        Update game logic for current frame.
        """
        if not self.is_over:
            # Move snake
            self.snake.process_movement()

            # Check food collision
            if self.snake.segments[0] == self.food.position:
                self.snake.trigger_growth()
                self.food.respawn(self.snake.segments)
                self.score += 1

            # Check game over conditions
            if self.snake.has_wall_collision() or self.snake.has_self_collision():
                self.is_over = True

    def display(self):
        """
        Render all visual elements to screen.
        """
        # Clear screen
        self.screen.fill(COLOR_BACKGROUND)

        # Render snake
        for segment_x, segment_y in self.snake.segments:
            x_pixel = segment_x * BLOCK_SIZE
            y_pixel = segment_y * BLOCK_SIZE
            segment_rect = pygame.Rect(x_pixel, y_pixel, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(self.screen, COLOR_SNAKE, segment_rect)

        # Render food
        food_x, food_y = self.food.position
        food_pixel_x = food_x * BLOCK_SIZE
        food_pixel_y = food_y * BLOCK_SIZE
        food_rect = pygame.Rect(food_pixel_x, food_pixel_y, BLOCK_SIZE, BLOCK_SIZE)
        pygame.draw.rect(self.screen, COLOR_FOOD, food_rect)

        # Render score
        score_text = self.font.render(f"Score: {self.score}", True, COLOR_FOOD)
        self.screen.blit(score_text, (10, 10))

        # Render game over overlay
        if self.is_over:
            game_over_text = self.font.render("Game Over!", True, COLOR_FOOD)
            instruction_text = self.font.render(
                "Press R to restart or Q to quit", True, COLOR_FOOD
            )

            game_over_rect = game_over_text.get_rect(
                center=(DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2 - 20)
            )
            instruction_rect = instruction_text.get_rect(
                center=(DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2 + 20)
            )

            self.screen.blit(game_over_text, game_over_rect)
            self.screen.blit(instruction_text, instruction_rect)

        # Update display
        pygame.display.flip()

    def execute(self):
        """
        Run the main game loop.
        """
        is_running = True

        while is_running:
            is_running = self.handle_events()
            self.process()
            self.display()
            self.clock.tick(9)

        pygame.quit()
        sys.exit()


# Game entry point
if __name__ == "__main__":
    game_engine = SnakeGameEngine()
    game_engine.execute()
