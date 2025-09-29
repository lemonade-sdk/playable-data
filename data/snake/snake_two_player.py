"""
Snake Game - Two Player Remix

A competitive two-player Snake game where both players share the same board.
Player 1 uses arrow keys, Player 2 uses WASD. Both snakes compete for food
and must avoid colliding with walls, themselves, or each other.

Remixed from the original Snake game implementation.
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
GREEN = (0, 255, 65)  # Player 1 snake
BLUE = (0, 100, 255)  # Player 2 snake
WHITE = (255, 255, 255)
RED = (255, 100, 100)  # Game over text

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


class Snake:
    def __init__(self, start_position, start_direction, color):
        self.body = [start_position]
        self.direction = start_direction
        self.grow = False
        self.color = color
        self.alive = True

    def move(self):
        if not self.alive:
            return

        head_x, head_y = self.body[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])
        self.body.insert(0, new_head)

        if not self.grow:
            self.body.pop()
        else:
            self.grow = False

    def change_direction(self, new_direction):
        if not self.alive:
            return
        # Prevent moving backwards into itself
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
            self.direction = new_direction

    def check_wall_collision(self):
        if not self.alive:
            return False
        head_x, head_y = self.body[0]
        return head_x < 0 or head_x >= GRID_WIDTH or head_y < 0 or head_y >= GRID_HEIGHT

    def check_self_collision(self):
        if not self.alive:
            return False
        return self.body[0] in self.body[1:]

    def check_other_snake_collision(self, other_snake):
        if not self.alive or not other_snake.alive:
            return False
        return self.body[0] in other_snake.body

    def eat_food(self):
        if self.alive:
            self.grow = True


class Food:
    def __init__(self):
        self.position = (
            random.randint(0, GRID_WIDTH - 1),
            random.randint(0, GRID_HEIGHT - 1),
        )

    def respawn(self, snake1_body, snake2_body):
        while True:
            self.position = (
                random.randint(0, GRID_WIDTH - 1),
                random.randint(0, GRID_HEIGHT - 1),
            )
            if self.position not in snake1_body and self.position not in snake2_body:
                break


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Game - Two Player Remix")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.reset_game()

    def reset_game(self):
        # Player 1 starts on the left side
        self.player1 = Snake((GRID_WIDTH // 4, GRID_HEIGHT // 2), RIGHT, GREEN)
        # Player 2 starts on the right side
        self.player2 = Snake((3 * GRID_WIDTH // 4, GRID_HEIGHT // 2), LEFT, BLUE)

        self.food = Food()
        self.player1_score = 0
        self.player2_score = 0
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
                else:
                    # Player 1 controls (Arrow keys)
                    if event.key == pygame.K_UP:
                        self.player1.change_direction(UP)
                    elif event.key == pygame.K_DOWN:
                        self.player1.change_direction(DOWN)
                    elif event.key == pygame.K_LEFT:
                        self.player1.change_direction(LEFT)
                    elif event.key == pygame.K_RIGHT:
                        self.player1.change_direction(RIGHT)

                    # Player 2 controls (WASD)
                    elif event.key == pygame.K_w:
                        self.player2.change_direction(UP)
                    elif event.key == pygame.K_s:
                        self.player2.change_direction(DOWN)
                    elif event.key == pygame.K_a:
                        self.player2.change_direction(LEFT)
                    elif event.key == pygame.K_d:
                        self.player2.change_direction(RIGHT)

        return True

    def update(self):
        if not self.game_over:
            # Move both snakes
            self.player1.move()
            self.player2.move()

            # Check food collision for both players
            if self.player1.alive and self.player1.body[0] == self.food.position:
                self.player1.eat_food()
                self.player1_score += 1
                self.food.respawn(self.player1.body, self.player2.body)
            elif self.player2.alive and self.player2.body[0] == self.food.position:
                self.player2.eat_food()
                self.player2_score += 1
                self.food.respawn(self.player1.body, self.player2.body)

            # Check collisions for Player 1
            if self.player1.alive:
                if (
                    self.player1.check_wall_collision()
                    or self.player1.check_self_collision()
                    or self.player1.check_other_snake_collision(self.player2)
                ):
                    self.player1.alive = False

            # Check collisions for Player 2
            if self.player2.alive:
                if (
                    self.player2.check_wall_collision()
                    or self.player2.check_self_collision()
                    or self.player2.check_other_snake_collision(self.player1)
                ):
                    self.player2.alive = False

            # Check game over conditions
            if not self.player1.alive and not self.player2.alive:
                self.game_over = True
                if self.player1_score > self.player2_score:
                    self.winner = "Player 1 Wins!"
                elif self.player2_score > self.player1_score:
                    self.winner = "Player 2 Wins!"
                else:
                    self.winner = "It's a Tie!"
            elif not self.player1.alive:
                self.game_over = True
                self.winner = "Player 2 Wins!"
            elif not self.player2.alive:
                self.game_over = True
                self.winner = "Player 1 Wins!"

    def draw(self):
        self.screen.fill(BLACK)

        # Draw Player 1 snake
        if self.player1.alive:
            for segment in self.player1.body:
                pygame.draw.rect(
                    self.screen,
                    self.player1.color,
                    pygame.Rect(
                        segment[0] * GRID_SIZE,
                        segment[1] * GRID_SIZE,
                        GRID_SIZE,
                        GRID_SIZE,
                    ),
                )

        # Draw Player 2 snake
        if self.player2.alive:
            for segment in self.player2.body:
                pygame.draw.rect(
                    self.screen,
                    self.player2.color,
                    pygame.Rect(
                        segment[0] * GRID_SIZE,
                        segment[1] * GRID_SIZE,
                        GRID_SIZE,
                        GRID_SIZE,
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

        # Draw scores
        player1_text = self.small_font.render(
            f"Player 1: {self.player1_score}", True, GREEN
        )
        player2_text = self.small_font.render(
            f"Player 2: {self.player2_score}", True, BLUE
        )
        self.screen.blit(player1_text, (10, 10))
        self.screen.blit(player2_text, (10, 35))

        # Draw controls
        controls1_text = self.small_font.render("P1: Arrow Keys", True, WHITE)
        controls2_text = self.small_font.render("P2: WASD", True, WHITE)
        self.screen.blit(controls1_text, (WINDOW_WIDTH - 150, 10))
        self.screen.blit(controls2_text, (WINDOW_WIDTH - 150, 35))

        # Draw game over screen
        if self.game_over:
            winner_text = self.font.render(self.winner, True, RED)
            restart_text = self.font.render(
                "Press R to restart or Q to quit", True, WHITE
            )

            self.screen.blit(
                winner_text,
                winner_text.get_rect(
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
