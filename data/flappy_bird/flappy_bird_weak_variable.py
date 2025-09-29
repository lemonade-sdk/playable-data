"""
Flappy Bird Weak Variable - A remix combining weak flap mechanics and variable gap sizes.
The bird falls due to gravity and flaps upward when spacebar is pressed. Game ends on collision with pipes or ground.
This remix reduces flap strength requiring more frequent tapping, while also randomizing pipe gap sizes
to create unpredictable difficulty that demands precise timing and rhythm.

This remix combines features from flappy_bird_weak_flap.py and flappy_bird_variable_gaps.py,
creating a challenging experience with both control and navigation difficulties.

Implementation uses pygame with minimal graphics and simple physics simulation.
"""

import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BIRD_SIZE = 30
PIPE_WIDTH = 80
BASE_PIPE_GAP = 180  # Base gap size
GAP_VARIATION = 60  # How much the gap can vary (+/-)
MIN_PIPE_GAP = 120  # Minimum playable gap
MAX_PIPE_GAP = 280  # Maximum gap
PIPE_SPEED = 3
GRAVITY = 0.5
FLAP_STRENGTH = -4  # Reduced from -8 to -4 for weaker flaps
BLACK = (0, 0, 0)
GREEN = (0, 255, 65)
WHITE = (255, 255, 255)


class Bird:
    def __init__(self):
        self.x = 100
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0

    def flap(self):
        self.velocity = FLAP_STRENGTH

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity

    def draw(self, screen):
        pygame.draw.circle(screen, GREEN, (int(self.x), int(self.y)), BIRD_SIZE // 2)

    def get_rect(self):
        return pygame.Rect(
            self.x - BIRD_SIZE // 2, self.y - BIRD_SIZE // 2, BIRD_SIZE, BIRD_SIZE
        )


class Pipe:
    def __init__(self, x):
        self.x = x
        # Generate variable gap size
        self.gap_size = random.randint(MIN_PIPE_GAP, MAX_PIPE_GAP)
        self.gap_y = random.randint(
            self.gap_size // 2 + 50, SCREEN_HEIGHT - self.gap_size // 2 - 50
        )
        self.passed = False

    def update(self):
        self.x -= PIPE_SPEED

    def draw(self, screen):
        # Draw top pipe
        pygame.draw.rect(
            screen,
            GREEN,
            (self.x, 0, PIPE_WIDTH, self.gap_y - self.gap_size // 2),
        )
        # Draw bottom pipe
        pygame.draw.rect(
            screen,
            GREEN,
            (
                self.x,
                self.gap_y + self.gap_size // 2,
                PIPE_WIDTH,
                SCREEN_HEIGHT - (self.gap_y + self.gap_size // 2),
            ),
        )

    def get_rects(self):
        top_rect = pygame.Rect(self.x, 0, PIPE_WIDTH, self.gap_y - self.gap_size // 2)
        bottom_rect = pygame.Rect(
            self.x,
            self.gap_y + self.gap_size // 2,
            PIPE_WIDTH,
            SCREEN_HEIGHT - (self.gap_y + self.gap_size // 2),
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
            self.bird.update()

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
