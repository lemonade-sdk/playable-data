"""
Snake Game - Ultimate Challenge Remix

The ultimate Snake challenge combining both moving food and enemy chase mechanics.
The food moves to random adjacent positions while an enemy relentlessly pursues
the snake. This creates the most challenging Snake experience possible.

Remixed from the original Snake game, incorporating mechanics from both
the Moving Food and Enemy Chase remixes.
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
RED = (255, 0, 0)  # Enemy color

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


class MovingFood:
    def __init__(self):
        self.position = (
            random.randint(0, GRID_WIDTH - 1),
            random.randint(0, GRID_HEIGHT - 1),
        )
        self.move_timer = 0
        self.move_interval = 3  # Move every 3 game updates

    def move(self, snake_body, enemy_position):
        self.move_timer += 1

        # Only move every move_interval updates
        if self.move_timer >= self.move_interval:
            self.move_timer = 0

            # Get all valid adjacent positions
            x, y = self.position
            adjacent_positions = [
                (x + dx, y + dy)
                for dx, dy in [
                    UP,
                    DOWN,
                    LEFT,
                    RIGHT,
                    (0, 0),
                ]  # Include staying in place
            ]

            # Filter valid positions (within bounds, not on snake, not on enemy)
            valid_positions = [
                pos
                for pos in adjacent_positions
                if (
                    0 <= pos[0] < GRID_WIDTH
                    and 0 <= pos[1] < GRID_HEIGHT
                    and pos not in snake_body
                    and pos != enemy_position
                )
            ]

            # Move to random valid position, or stay if no valid moves
            if valid_positions:
                self.position = random.choice(valid_positions)

    def respawn(self, snake_body, enemy_position):
        while True:
            self.position = (
                random.randint(0, GRID_WIDTH - 1),
                random.randint(0, GRID_HEIGHT - 1),
            )
            if self.position not in snake_body and self.position != enemy_position:
                break


class Enemy:
    def __init__(self):
        # Start enemy in a corner, away from snake
        self.position = (0, 0)
        self.move_timer = 0
        self.move_interval = 2  # Move every 2 game updates (faster than moving food)

    def move(self, snake_head, snake_body):
        self.move_timer += 1

        # Only move every move_interval updates
        if self.move_timer >= self.move_interval:
            self.move_timer = 0

            # Simple AI: move towards snake head
            enemy_x, enemy_y = self.position
            snake_x, snake_y = snake_head

            # Calculate direction to move towards snake
            possible_moves = []

            # Prefer moving towards snake on both axes
            if snake_x > enemy_x and enemy_x + 1 < GRID_WIDTH:
                possible_moves.append((enemy_x + 1, enemy_y))  # Move right
            elif snake_x < enemy_x and enemy_x - 1 >= 0:
                possible_moves.append((enemy_x - 1, enemy_y))  # Move left

            if snake_y > enemy_y and enemy_y + 1 < GRID_HEIGHT:
                possible_moves.append((enemy_x, enemy_y + 1))  # Move down
            elif snake_y < enemy_y and enemy_y - 1 >= 0:
                possible_moves.append((enemy_x, enemy_y - 1))  # Move up

            # Only filter out positions that are out of bounds (enemy can move through snake body)
            valid_moves = [
                pos
                for pos in possible_moves
                if 0 <= pos[0] < GRID_WIDTH and 0 <= pos[1] < GRID_HEIGHT
            ]

            # If no direct moves available, try any adjacent valid position
            if not valid_moves:
                adjacent_positions = [
                    (enemy_x + dx, enemy_y + dy) for dx, dy in [UP, DOWN, LEFT, RIGHT]
                ]
                valid_moves = [
                    pos
                    for pos in adjacent_positions
                    if (0 <= pos[0] < GRID_WIDTH and 0 <= pos[1] < GRID_HEIGHT)
                ]

            # Move to best available position
            if valid_moves:
                # Choose the move that gets closest to snake head
                best_move = min(
                    valid_moves,
                    key=lambda pos: abs(pos[0] - snake_x) + abs(pos[1] - snake_y),
                )
                self.position = best_move


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Game - Ultimate Challenge Remix")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.reset_game()

    def reset_game(self):
        self.snake = Snake()
        self.food = MovingFood()
        self.enemy = Enemy()
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

            # Move enemy towards snake
            self.enemy.move(self.snake.body[0], self.snake.body)

            # Check food collision BEFORE moving food
            if self.snake.body[0] == self.food.position:
                self.snake.grow = True
                self.food.respawn(self.snake.body, self.enemy.position)
                self.score += 1
            else:
                # Only move food if not eaten
                self.food.move(self.snake.body, self.enemy.position)

            # Check enemy collision with snake
            if self.enemy.position == self.snake.body[0]:
                self.game_over = True

            # Check game over conditions (walls and self-collision)
            if self.snake.check_collision():
                self.game_over = True

    def draw(self):
        self.screen.fill(BLACK)

        # Draw snake
        for segment in self.snake.body:
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

        # Draw enemy
        pygame.draw.rect(
            self.screen,
            RED,
            pygame.Rect(
                self.enemy.position[0] * GRID_SIZE,
                self.enemy.position[1] * GRID_SIZE,
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
