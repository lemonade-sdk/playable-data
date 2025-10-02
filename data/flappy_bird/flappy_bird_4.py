"""
Flappy Bird - A bird flying game where you navigate through pipe gaps.
The bird is affected by gravity and you must tap spacebar to make it fly upward.
Score increases as you successfully pass between pipes. Collision ends the game.
"""

import pygame
import random
import sys

pygame.init()

BLACK = (0, 0, 0)
GREEN = (0, 255, 65)
WHITE = (255, 255, 255)


class Bird:
    def __init__(self, screen_width, screen_height):
        self.screen_h = screen_height
        self.size = 32
        self.pos_x = 100
        self.pos_y = screen_height // 2
        self.velocity = 0
        self.gravity = 0.55
        self.jump_force = -8.5

    def jump(self):
        self.velocity = self.jump_force

    def update(self):
        self.velocity += self.gravity
        self.pos_y += self.velocity

    def draw(self, screen):
        # Square bird
        half_size = self.size // 2
        pygame.draw.rect(
            screen,
            GREEN,
            (self.pos_x - half_size, self.pos_y - half_size, self.size, self.size),
        )

    def collision_box(self):
        half_size = self.size // 2
        return pygame.Rect(
            self.pos_x - half_size, self.pos_y - half_size, self.size, self.size
        )

    def is_out_of_bounds(self):
        return self.pos_y <= 0 or self.pos_y >= self.screen_h


class Pipe:
    def __init__(self, x, screen_height):
        self.screen_h = screen_height
        self.pos_x = x
        self.width = 85
        self.gap_size = 210
        self.move_speed = 3.5
        self.gap_position = random.randint(140, screen_height - 140 - self.gap_size)
        self.point_awarded = False

    def update(self):
        self.pos_x -= self.move_speed

    def draw(self, screen):
        # Upper pipe
        pygame.draw.rect(screen, GREEN, (self.pos_x, 0, self.width, self.gap_position))
        # Lower pipe
        lower_start = self.gap_position + self.gap_size
        pygame.draw.rect(
            screen,
            GREEN,
            (self.pos_x, lower_start, self.width, self.screen_h - lower_start),
        )

    def collision_boxes(self):
        upper = pygame.Rect(self.pos_x, 0, self.width, self.gap_position)
        lower_start = self.gap_position + self.gap_size
        lower = pygame.Rect(
            self.pos_x, lower_start, self.width, self.screen_h - lower_start
        )
        return [upper, lower]

    def passed_left_edge(self):
        return self.pos_x + self.width < 0


class Game:
    SCREEN_SIZE = 650
    PIPE_SPAWN_TIME = 85

    def __init__(self):
        self.screen = pygame.display.set_mode((self.SCREEN_SIZE, self.SCREEN_SIZE))
        pygame.display.set_caption("Flappy Bird")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.restart_game()

    def restart_game(self):
        self.bird = Bird(self.SCREEN_SIZE, self.SCREEN_SIZE)
        self.pipe_collection = []
        self.player_score = 0
        self.over = False
        self.frame_timer = 0

    def process_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if self.over:
                    if event.key == pygame.K_r:
                        self.restart_game()
                    elif event.key == pygame.K_q:
                        return False
                else:
                    if event.key == pygame.K_SPACE:
                        self.bird.jump()
        return True

    def update(self):
        if not self.over:
            self.bird.update()

            # Spawn pipes
            self.frame_timer += 1
            if self.frame_timer > self.PIPE_SPAWN_TIME:
                new_pipe = Pipe(self.SCREEN_SIZE, self.SCREEN_SIZE)
                self.pipe_collection.append(new_pipe)
                self.frame_timer = 0

            # Update pipes
            for pipe in self.pipe_collection[:]:
                pipe.update()
                if pipe.passed_left_edge():
                    self.pipe_collection.remove(pipe)
                elif (
                    not pipe.point_awarded and pipe.pos_x + pipe.width < self.bird.pos_x
                ):
                    pipe.point_awarded = True
                    self.player_score += 1

            # Check collisions
            bird_box = self.bird.collision_box()

            # Out of bounds
            if self.bird.is_out_of_bounds():
                self.over = True

            # Pipe collisions
            for pipe in self.pipe_collection:
                for box in pipe.collision_boxes():
                    if bird_box.colliderect(box):
                        self.over = True

    def render(self):
        self.screen.fill(BLACK)

        # Draw objects
        self.bird.draw(self.screen)
        for pipe in self.pipe_collection:
            pipe.draw(self.screen)

        # Draw score
        score_display = self.font.render(f"Score: {self.player_score}", True, WHITE)
        self.screen.blit(score_display, (15, 15))

        # Draw game over
        if self.over:
            over_display = self.font.render("Game Over!", True, WHITE)
            help_display = self.font.render(
                "Press R to restart or Q to quit", True, WHITE
            )

            over_position = over_display.get_rect(
                center=(self.SCREEN_SIZE // 2, self.SCREEN_SIZE // 2 - 30)
            )
            help_position = help_display.get_rect(
                center=(self.SCREEN_SIZE // 2, self.SCREEN_SIZE // 2 + 30)
            )

            self.screen.blit(over_display, over_position)
            self.screen.blit(help_display, help_position)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.process_input()
            self.update()
            self.render()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
