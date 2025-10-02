# CREATE: flappy bird

"""
Flappy Bird - Classic bird navigation game through pipe obstacles.
Control a bird that falls due to gravity by pressing spacebar to flap upward.
Avoid collision with pipes and screen boundaries while scoring points for each pipe passed.
Features simple physics and collision detection.
"""

import pygame
import random
import sys

pygame.init()

# Screen
SCREEN_W = 700
SCREEN_H = 550

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 65)
WHITE = (255, 255, 255)


class Bird:
    SIZE = 28
    GRAVITY_VAL = 0.45
    FLAP_VAL = -7.5

    def __init__(self):
        self.x = 90
        self.y = SCREEN_H // 2
        self.vel_y = 0

    def do_flap(self):
        self.vel_y = self.FLAP_VAL

    def tick(self):
        self.vel_y += self.GRAVITY_VAL
        self.y += self.vel_y

    def render(self, surface):
        # Draw as circle
        pygame.draw.circle(surface, GREEN, (int(self.x), int(self.y)), self.SIZE // 2)

    def get_bounds(self):
        half = self.SIZE // 2
        return pygame.Rect(self.x - half, self.y - half, self.SIZE, self.SIZE)


class Pipe:
    WIDTH = 75
    GAP = 190
    SPEED = 3.2

    def __init__(self, x_coord):
        self.x = x_coord
        self.top_height = random.randint(130, SCREEN_H - 130 - self.GAP)
        self.counted = False

    def tick(self):
        self.x -= self.SPEED

    def render(self, surface):
        # Top section
        pygame.draw.rect(surface, GREEN, (self.x, 0, self.WIDTH, self.top_height))
        # Bottom section
        bottom_start = self.top_height + self.GAP
        pygame.draw.rect(
            surface, GREEN, (self.x, bottom_start, self.WIDTH, SCREEN_H - bottom_start)
        )

    def get_bounds(self):
        top = pygame.Rect(self.x, 0, self.WIDTH, self.top_height)
        bottom_start = self.top_height + self.GAP
        bottom = pygame.Rect(self.x, bottom_start, self.WIDTH, SCREEN_H - bottom_start)
        return [top, bottom]

    def check_offscreen(self):
        return self.x + self.WIDTH < 0


class FlappyBirdGame:
    SPAWN_INTERVAL = 95

    def __init__(self):
        self.display = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Flappy Bird")
        self.game_clock = pygame.time.Clock()
        self.text_font = pygame.font.Font(None, 35)
        self.new_game()

    def new_game(self):
        self.player_bird = Bird()
        self.obstacles = []
        self.current_score = 0
        self.finished = False
        self.tick_counter = 0

    def handle_events(self):
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                return False
            elif evt.type == pygame.KEYDOWN:
                if self.finished:
                    if evt.key == pygame.K_r:
                        self.new_game()
                    elif evt.key == pygame.K_q:
                        return False
                else:
                    if evt.key == pygame.K_SPACE:
                        self.player_bird.do_flap()
        return True

    def check_collision(self, rect1, rect2):
        return rect1.colliderect(rect2)

    def update_state(self):
        if not self.finished:
            self.player_bird.tick()

            # Create obstacles
            self.tick_counter += 1
            if self.tick_counter > self.SPAWN_INTERVAL:
                self.obstacles.append(Pipe(SCREEN_W))
                self.tick_counter = 0

            # Update obstacles
            for obstacle in self.obstacles[:]:
                obstacle.tick()
                if obstacle.check_offscreen():
                    self.obstacles.remove(obstacle)
                elif (
                    not obstacle.counted
                    and obstacle.x + Pipe.WIDTH < self.player_bird.x
                ):
                    obstacle.counted = True
                    self.current_score += 1

            # Check for collisions
            bird_rect = self.player_bird.get_bounds()

            # Boundary collision
            if self.player_bird.y <= 0 or self.player_bird.y >= SCREEN_H:
                self.finished = True

            # Obstacle collision
            for obstacle in self.obstacles:
                for rect in obstacle.get_bounds():
                    if self.check_collision(bird_rect, rect):
                        self.finished = True

    def draw_screen(self):
        self.display.fill(BLACK)

        # Render game objects
        self.player_bird.render(self.display)
        for obstacle in self.obstacles:
            obstacle.render(self.display)

        # Render score
        score_surf = self.text_font.render(f"Score: {self.current_score}", True, WHITE)
        self.display.blit(score_surf, (12, 12))

        # Render game over
        if self.finished:
            game_over_surf = self.text_font.render("Game Over!", True, WHITE)
            restart_surf = self.text_font.render(
                "Press R to restart or Q to quit", True, WHITE
            )

            game_over_pos = game_over_surf.get_rect(
                center=(SCREEN_W // 2, SCREEN_H // 2 - 25)
            )
            restart_pos = restart_surf.get_rect(
                center=(SCREEN_W // 2, SCREEN_H // 2 + 25)
            )

            self.display.blit(game_over_surf, game_over_pos)
            self.display.blit(restart_surf, restart_pos)

        pygame.display.flip()

    def run(self):
        active = True
        while active:
            active = self.handle_events()
            self.update_state()
            self.draw_screen()
            self.game_clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = FlappyBirdGame()
    game.run()
