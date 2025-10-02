# CREATE: snake

"""
Snake Game

Grid-based snake game with simple controls. Snake grows when eating food,
game over when hitting walls or self. Built with pygame and OOP design.
"""

import pygame
import random
import sys

pygame.init()

WIDTH = 900
HEIGHT = 700
GRID = 30
COLS = WIDTH // GRID
ROWS = HEIGHT // GRID

BLACK = (0, 0, 0)
GREEN = (0, 255, 65)
WHITE = (255, 255, 255)

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


class Snake:
    def __init__(self):
        self.pos = [(COLS // 2, ROWS // 2)]
        self.dir = LEFT
        self.grow_flag = False

    def eat(self):
        self.grow_flag = True

    def get_head(self):
        return self.pos[0]

    def hit_wall(self):
        x, y = self.pos[0]
        return x < 0 or x >= COLS or y < 0 or y >= ROWS

    def hit_self(self):
        return self.pos[0] in self.pos[1:]

    def set_dir(self, direction):
        if (direction[0] + self.dir[0], direction[1] + self.dir[1]) != (0, 0):
            self.dir = direction

    def tick(self):
        x, y = self.pos[0]
        nx, ny = x + self.dir[0], y + self.dir[1]
        self.pos.insert(0, (nx, ny))
        if not self.grow_flag:
            self.pos.pop()
        else:
            self.grow_flag = False


class Food:
    def __init__(self):
        self.pos = (0, 0)
        self.spawn()

    def spawn(self):
        self.pos = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))

    def spawn_away_from(self, blocks):
        while True:
            self.spawn()
            if self.pos not in blocks:
                return


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)
        self.reset()

    def draw(self):
        self.screen.fill(BLACK)

        for x, y in self.snake.pos:
            pygame.draw.rect(self.screen, GREEN, (x * GRID, y * GRID, GRID, GRID))

        fx, fy = self.food.pos
        pygame.draw.rect(self.screen, WHITE, (fx * GRID, fy * GRID, GRID, GRID))

        score_txt = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_txt, (10, 10))

        if self.over:
            txt1 = self.font.render("Game Over!", True, WHITE)
            txt2 = self.font.render("Press R to restart or Q to quit", True, WHITE)
            r1 = txt1.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
            r2 = txt2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
            self.screen.blit(txt1, r1)
            self.screen.blit(txt2, r2)

        pygame.display.flip()

    def events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False
            if e.type == pygame.KEYDOWN:
                if self.over:
                    if e.key == pygame.K_r:
                        self.reset()
                    elif e.key == pygame.K_q:
                        return False
                else:
                    if e.key == pygame.K_UP:
                        self.snake.set_dir(UP)
                    elif e.key == pygame.K_DOWN:
                        self.snake.set_dir(DOWN)
                    elif e.key == pygame.K_LEFT:
                        self.snake.set_dir(LEFT)
                    elif e.key == pygame.K_RIGHT:
                        self.snake.set_dir(RIGHT)
        return True

    def reset(self):
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.over = False

    def run(self):
        active = True
        while active:
            active = self.events()
            self.tick()
            self.draw()
            self.clock.tick(12)
        pygame.quit()
        sys.exit()

    def tick(self):
        if not self.over:
            self.snake.tick()

            if self.snake.get_head() == self.food.pos:
                self.snake.eat()
                self.food.spawn_away_from(self.snake.pos)
                self.score += 1

            if self.snake.hit_wall() or self.snake.hit_self():
                self.over = True


if __name__ == "__main__":
    game = Game()
    game.run()
