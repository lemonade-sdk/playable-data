"""
Flappy Bird Growing Scaling - A remix combining growing bird and scaling pipes mechanics.
The bird falls due to gravity and flaps upward when spacebar is pressed. Game ends on collision with pipes or ground.
This remix makes the bird progressively larger with each point scored while pipes dynamically scale and stretch
as they move across the screen, creating a double challenge of increasing bird size and morphing obstacles.

This remix combines features from flappy_bird_growing.py and flappy_bird_scaling_pipes.py,
creating escalating difficulty through both player size and dynamic obstacles.

Implementation uses pygame with minimal graphics and simple physics simulation.
"""

import pygame
import random
import sys
import math

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BASE_BIRD_SIZE = 20
BIRD_GROWTH_RATE = 2  # Pixels to grow per point
MAX_BIRD_SIZE = 60  # Maximum bird size
PIPE_WIDTH = 80
PIPE_GAP = 250
PIPE_SPEED = 2.5
GRAVITY = 0.4
FLAP_STRENGTH = -9
BLACK = (0, 0, 0)
GREEN = (0, 255, 65)
WHITE = (255, 255, 255)


class Bird:
    def __init__(self):
        self.x = 100
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.size = BASE_BIRD_SIZE

    def flap(self):
        self.velocity = FLAP_STRENGTH

    def update(self, score):
        self.velocity += GRAVITY
        self.y += self.velocity

        # Update bird size based on score
        self.size = min(BASE_BIRD_SIZE + (score * BIRD_GROWTH_RATE), MAX_BIRD_SIZE)

    def draw(self, screen):
        pygame.draw.circle(screen, GREEN, (int(self.x), int(self.y)), self.size // 2)

    def get_rect(self):
        return pygame.Rect(
            self.x - self.size // 2, self.y - self.size // 2, self.size, self.size
        )


class Pipe:
    def __init__(self, x):
        self.x = x
        self.base_gap_y = random.randint(150, SCREEN_HEIGHT - 150)
        self.base_gap_size = PIPE_GAP
        self.passed = False
        self.time_offset = random.uniform(0, 2 * math.pi)  # Random phase for scaling

    def update(self):
        self.x -= PIPE_SPEED

    def get_current_gap_info(self):
        # Calculate current gap size and position based on scaling animation
        scale_factor = 0.8 + 0.4 * math.sin(
            self.x * 0.02 + self.time_offset
        )  # Scale between 0.8 and 1.2
        current_gap_size = self.base_gap_size * scale_factor

        # Slight vertical oscillation
        vertical_offset = 20 * math.sin(self.x * 0.03 + self.time_offset)
        current_gap_y = self.base_gap_y + vertical_offset

        return current_gap_y, current_gap_size

    def draw(self, screen):
        gap_y, gap_size = self.get_current_gap_info()

        # Draw top pipe
        pygame.draw.rect(
            screen,
            GREEN,
            (self.x, 0, PIPE_WIDTH, gap_y - gap_size // 2),
        )
        # Draw bottom pipe
        pygame.draw.rect(
            screen,
            GREEN,
            (
                self.x,
                gap_y + gap_size // 2,
                PIPE_WIDTH,
                SCREEN_HEIGHT - (gap_y + gap_size // 2),
            ),
        )

    def get_rects(self):
        gap_y, gap_size = self.get_current_gap_info()

        top_rect = pygame.Rect(self.x, 0, PIPE_WIDTH, gap_y - gap_size // 2)
        bottom_rect = pygame.Rect(
            self.x,
            gap_y + gap_size // 2,
            PIPE_WIDTH,
            SCREEN_HEIGHT - (gap_y + gap_size // 2),
        )
        return [top_rect, bottom_rect]

    def is_off_screen(self):
        return self.x + PIPE_WIDTH < 0


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy Bird")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.reset_game()

    def reset_game(self):
        self.bird = Bird()
        self.pipes = []
        self.score = 0
        self.game_over = False
        self.pipe_timer = 0

    def spawn_pipe(self):
        pipe = Pipe(SCREEN_WIDTH)
        self.pipes.append(pipe)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over:
                    self.bird.flap()
                elif self.game_over:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_q:
                        return False
        return True

    def update(self):
        if not self.game_over:
            self.bird.update(self.score)

            # Spawn pipes
            self.pipe_timer += 1
            if self.pipe_timer >= 120:  # Spawn every 2 seconds
                self.spawn_pipe()
                self.pipe_timer = 0

            # Update pipes
            for pipe in self.pipes[:]:
                pipe.update()
                if pipe.is_off_screen():
                    self.pipes.remove(pipe)

            # Check for scoring (passing pipes)
            for pipe in self.pipes:
                if not pipe.passed and pipe.x + PIPE_WIDTH < self.bird.x:
                    pipe.passed = True
                    self.score += 1

            # Check collisions
            bird_rect = self.bird.get_rect()

            # Ground and ceiling collision
            if self.bird.y <= 0 or self.bird.y >= SCREEN_HEIGHT:
                self.game_over = True

            # Pipe collision
            for pipe in self.pipes:
                for pipe_rect in pipe.get_rects():
                    if bird_rect.colliderect(pipe_rect):
                        self.game_over = True
                        break

    def draw(self):
        self.screen.fill(BLACK)

        if not self.game_over:
            # Draw game objects
            self.bird.draw(self.screen)
            for pipe in self.pipes:
                pipe.draw(self.screen)

        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # Draw game over screen
        if self.game_over:
            game_over_text = self.font.render("Game Over!", True, WHITE)
            restart_text = self.font.render(
                "Press R to restart or Q to quit", True, WHITE
            )

            game_over_rect = game_over_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30)
            )
            restart_rect = restart_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30)
            )

            self.screen.blit(game_over_text, game_over_rect)
            self.screen.blit(restart_text, restart_rect)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
