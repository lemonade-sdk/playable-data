"""
Snake Game

A traditional snake game implementation with pygame. The player navigates
a snake around the screen to collect food items. Each food eaten causes
the snake to grow longer. The game ends if the snake collides with the
walls or its own body.
"""

import pygame
import random
import sys

# Initialize pygame module
pygame.init()

# Screen configuration
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
TILE_SIZE = 25
GRID_COLS = WINDOW_WIDTH // TILE_SIZE
GRID_ROWS = WINDOW_HEIGHT // TILE_SIZE

# Color palette
BLACK = (0, 0, 0)
GREEN = (0, 255, 65)
WHITE = (255, 255, 255)

# Direction vectors
DIR_UP = (0, -1)
DIR_DOWN = (0, 1)
DIR_LEFT = (-1, 0)
DIR_RIGHT = (1, 0)


class SnakeEntity:
    """Snake entity with movement and collision detection"""

    def __init__(self, start_x, start_y):
        self.body_parts = [(start_x, start_y)]
        self.heading = DIR_RIGHT
        self.pending_growth = 0

    def add_growth(self, amount=1):
        """Queue growth segments to add"""
        self.pending_growth += amount

    def advance(self):
        """Move snake forward one step"""
        head = self.body_parts[0]
        new_x = head[0] + self.heading[0]
        new_y = head[1] + self.heading[1]
        new_head = (new_x, new_y)

        self.body_parts.insert(0, new_head)

        if self.pending_growth > 0:
            self.pending_growth -= 1
        else:
            self.body_parts.pop()

    def turn(self, new_heading):
        """Change direction if not opposite"""
        if not self._is_opposite(new_heading):
            self.heading = new_heading

    def _is_opposite(self, direction):
        """Helper to check if direction is opposite to current"""
        return direction[0] == -self.heading[0] and direction[1] == -self.heading[1]

    def get_head_position(self):
        """Return position of snake head"""
        return self.body_parts[0]

    def is_colliding_with_bounds(self):
        """Check if head is outside play area"""
        x, y = self.body_parts[0]
        if x < 0 or x >= GRID_COLS:
            return True
        if y < 0 or y >= GRID_ROWS:
            return True
        return False

    def is_colliding_with_self(self):
        """Check if head overlaps body"""
        return self.body_parts[0] in self.body_parts[1:]

    def get_all_positions(self):
        """Return all grid positions occupied by snake"""
        return list(self.body_parts)


class FoodEntity:
    """Food entity that snake can collect"""

    def __init__(self):
        self.location = (0, 0)
        self.randomize_position()

    def randomize_position(self):
        """Place food at random grid location"""
        x = random.randint(0, GRID_COLS - 1)
        y = random.randint(0, GRID_ROWS - 1)
        self.location = (x, y)

    def relocate(self, blocked_positions):
        """Move food to position not in blocked list"""
        attempts = 0
        max_attempts = 100
        while attempts < max_attempts:
            self.randomize_position()
            if self.location not in blocked_positions:
                return
            attempts += 1

    def get_position(self):
        """Return current food position"""
        return self.location


class GameController:
    """Main game controller managing all entities and game state"""

    def __init__(self):
        self.display = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self._initialize_game()

    def _initialize_game(self):
        """Set up new game state"""
        start_x = GRID_COLS // 2
        start_y = GRID_ROWS // 2
        self.snake = SnakeEntity(start_x, start_y)
        self.food = FoodEntity()
        self.food.relocate(self.snake.get_all_positions())
        self.points = 0
        self.game_ended = False

    def handle_input(self):
        """Process keyboard and window events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if self.game_ended:
                    if event.key == pygame.K_r:
                        self._initialize_game()
                    elif event.key == pygame.K_q:
                        return False
                else:
                    self._process_direction_key(event.key)

        return True

    def _process_direction_key(self, key):
        """Helper to handle directional input"""
        if key == pygame.K_UP:
            self.snake.turn(DIR_UP)
        elif key == pygame.K_DOWN:
            self.snake.turn(DIR_DOWN)
        elif key == pygame.K_LEFT:
            self.snake.turn(DIR_LEFT)
        elif key == pygame.K_RIGHT:
            self.snake.turn(DIR_RIGHT)

    def advance_game(self):
        """Update game state for one frame"""
        if not self.game_ended:
            self.snake.advance()
            self._check_food_collection()
            self._check_collisions()

    def _check_food_collection(self):
        """Check if snake collected food"""
        if self.snake.get_head_position() == self.food.get_position():
            self.snake.add_growth(1)
            self.food.relocate(self.snake.get_all_positions())
            self.points += 1

    def _check_collisions(self):
        """Check for game ending collisions"""
        if self.snake.is_colliding_with_bounds() or self.snake.is_colliding_with_self():
            self.game_ended = True

    def render(self):
        """Draw all game elements to screen"""
        self.display.fill(BLACK)
        self._render_snake()
        self._render_food()
        self._render_score()
        if self.game_ended:
            self._render_game_over()
        pygame.display.flip()

    def _render_snake(self):
        """Helper to draw snake"""
        for x, y in self.snake.get_all_positions():
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(self.display, GREEN, rect)

    def _render_food(self):
        """Helper to draw food"""
        x, y = self.food.get_position()
        rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(self.display, WHITE, rect)

    def _render_score(self):
        """Helper to draw score"""
        text = self.font.render(f"Score: {self.points}", True, WHITE)
        self.display.blit(text, (10, 10))

    def _render_game_over(self):
        """Helper to draw game over screen"""
        text1 = self.font.render("Game Over!", True, WHITE)
        text2 = self.font.render("Press R to restart or Q to quit", True, WHITE)

        rect1 = text1.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 25))
        rect2 = text2.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 25))

        self.display.blit(text1, rect1)
        self.display.blit(text2, rect2)

    def start(self):
        """Begin main game loop"""
        running = True
        while running:
            running = self.handle_input()
            self.advance_game()
            self.render()
            self.clock.tick(10)

        pygame.quit()
        sys.exit()


def main():
    """Entry point for snake game"""
    controller = GameController()
    controller.start()


if __name__ == "__main__":
    main()
