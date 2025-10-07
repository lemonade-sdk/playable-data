# CREATE: snake
# ERROR: Traceback (most recent call last):
# ERROR:   File "C:\work\lsdk\playable-data\data\snake\bugs\snake_bug.py", line 208, in <module>
# ERROR:     game.run()
# ERROR:   File "C:\work\lsdk\playable-data\data\snake\bugs\snake_bug.py", line 198, in run
# ERROR:     self.draw()
# ERROR:   File "C:\work\lsdk\playable-data\data\snake\bugs\snake_bug.py", line 146, in draw
# ERROR:     for segment in self.snake.segments:
# ERROR:                    ^^^^^^^^^^^^^^^^^^^
# ERROR: AttributeError: 'Snake' object has no attribute 'segments'

"""
Snake Game

A classic Snake implementation using pygame with grid-based movement.
The snake grows when eating food, game ends on wall/self collision.
Uses event-driven input handling and object-oriented design with
separate Snake, Food, and Game classes for clean separation of concerns.
"""

import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Game constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 65)
WHITE = (255, 255, 255)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


class Snake:
    def __init__(self):
        self.body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.grow = False

    def move(self):
        head_x, head_y = self.body[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])
        self.body.insert(0, new_head)

        if not self.grow:
            self.body.pop()
        else:
            self.grow = False

    def change_direction(self, new_direction):
        # Prevent moving backwards into itself
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
            self.direction = new_direction

    def check_collision(self):
        head_x, head_y = self.body[0]

        # Wall collision
        if head_x < 0 or head_x >= GRID_WIDTH or head_y < 0 or head_y >= GRID_HEIGHT:
            return True

        # Self collision
        if self.body[0] in self.body[1:]:
            return True

        return False


class Food:
    def __init__(self):
        self.position = (
            random.randint(0, GRID_WIDTH - 1),
            random.randint(0, GRID_HEIGHT - 1),
        )

    def respawn(self, snake_body):
        while True:
            self.position = (
                random.randint(0, GRID_WIDTH - 1),
                random.randint(0, GRID_HEIGHT - 1),
            )
            if self.position not in snake_body:
                break


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.reset_game()

    def reset_game(self):
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.game_over = False

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
                else:
                    # Movement controls
                    if event.key == pygame.K_UP:
                        self.snake.change_direction(UP)
                    elif event.key == pygame.K_DOWN:
                        self.snake.change_direction(DOWN)
                    elif event.key == pygame.K_LEFT:
                        self.snake.change_direction(LEFT)
                    elif event.key == pygame.K_RIGHT:
                        self.snake.change_direction(RIGHT)

        return True

    def update(self):
        if not self.game_over:
            self.snake.move()

            # Check food collision
            if self.snake.body[0] == self.food.position:
                self.snake.grow = True
                self.food.respawn(self.snake.body)
                self.score += 1

            # Check game over conditions
            if self.snake.check_collision():
                self.game_over = True

    def draw(self):
        self.screen.fill(BLACK)

        # Draw snake
        for segment in self.snake.segments:
            pygame.draw.rect(
                self.screen,
                GREEN,
                pygame.Rect(
                    segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE
                ),
            )

        # Draw food
        pygame.draw.rect(
            self.screen,
            WHITE,
            pygame.Rect(
                self.food.position[0] * GRID_SIZE,
                self.food.position[1] * GRID_SIZE,
                GRID_SIZE,
                GRID_SIZE,
            ),
        )

        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # Draw game over screen
        if self.game_over:
            game_over_text = self.font.render("Game Over!", True, WHITE)
            restart_text = self.font.render(
                "Press R to restart or Q to quit", True, WHITE
            )

            self.screen.blit(
                game_over_text,
                game_over_text.get_rect(
                    center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20)
                ),
            )
            self.screen.blit(
                restart_text,
                restart_text.get_rect(
                    center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20)
                ),
            )

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(10)  # Game speed

        pygame.quit()
        sys.exit()


# Main execution
if __name__ == "__main__":
    game = Game()
    game.run()
