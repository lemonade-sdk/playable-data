# CREATE: flappy bird with realistic bird graphics

"""
Flappy Bird Realistic Game

A side-scrolling game where the player controls a bird with enhanced visual design featuring
realistic bird-like appearance. The bird falls due to gravity and flaps upward when spacebar
is pressed. Bird rendering includes geometric shapes for body, wings, beak, and eye details
with simple wing flapping animation. Implementation uses pygame with enhanced graphics rendering,
collision detection, and physics simulation.
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
BIRD_SIZE = 30
PIPE_WIDTH = 80
PIPE_GAP = 200
PIPE_SPEED = 3
GRAVITY = 0.5
FLAP_STRENGTH = -8
BLACK = (0, 0, 0)
GREEN = (0, 255, 65)
WHITE = (255, 255, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)


class Bird:
    def __init__(self):
        self.x = 100
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.wing_angle = 0
        self.flap_timer = 0

    def flap(self):
        self.velocity = FLAP_STRENGTH
        self.flap_timer = 10  # Wing animation duration

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity

        # Update wing animation
        if self.flap_timer > 0:
            self.flap_timer -= 1
            self.wing_angle = math.sin(self.flap_timer * 0.8) * 30
        else:
            self.wing_angle = math.sin(pygame.time.get_ticks() * 0.01) * 15

    def draw(self, screen):
        # Bird body (main oval)
        body_rect = pygame.Rect(self.x - 15, self.y - 10, 30, 20)
        pygame.draw.ellipse(screen, GREEN, body_rect)

        # Bird head (smaller circle)
        head_center = (int(self.x + 8), int(self.y - 5))
        pygame.draw.circle(screen, GREEN, head_center, 12)

        # Beak (triangle)
        beak_points = [
            (self.x + 18, self.y - 5),
            (self.x + 28, self.y - 2),
            (self.x + 18, self.y + 1),
        ]
        pygame.draw.polygon(screen, ORANGE, beak_points)

        # Eye (white circle with black pupil)
        eye_center = (int(self.x + 12), int(self.y - 8))
        pygame.draw.circle(screen, WHITE, eye_center, 4)
        pygame.draw.circle(screen, BLACK, eye_center, 2)

        # Wing (animated ellipse)
        wing_offset_y = math.sin(math.radians(self.wing_angle)) * 5
        wing_rect = pygame.Rect(self.x - 8, self.y - 2 + wing_offset_y, 16, 8)
        pygame.draw.ellipse(screen, YELLOW, wing_rect)

        # Tail feathers (small triangles)
        tail_points = [
            (self.x - 15, self.y),
            (self.x - 25, self.y - 5),
            (self.x - 20, self.y + 3),
        ]
        pygame.draw.polygon(screen, YELLOW, tail_points)

    def get_rect(self):
        return pygame.Rect(
            self.x - BIRD_SIZE // 2, self.y - BIRD_SIZE // 2, BIRD_SIZE, BIRD_SIZE
        )


class Pipe:
    def __init__(self, x):
        self.x = x
        self.gap_y = random.randint(150, SCREEN_HEIGHT - 150 - PIPE_GAP)
        self.passed = False

    def update(self):
        self.x -= PIPE_SPEED

    def draw(self, screen):
        # Top pipe
        pygame.draw.rect(screen, GREEN, (self.x, 0, PIPE_WIDTH, self.gap_y))
        # Bottom pipe
        pygame.draw.rect(
            screen,
            GREEN,
            (
                self.x,
                self.gap_y + PIPE_GAP,
                PIPE_WIDTH,
                SCREEN_HEIGHT - self.gap_y - PIPE_GAP,
            ),
        )

    def get_rects(self):
        top_rect = pygame.Rect(self.x, 0, PIPE_WIDTH, self.gap_y)
        bottom_rect = pygame.Rect(
            self.x,
            self.gap_y + PIPE_GAP,
            PIPE_WIDTH,
            SCREEN_HEIGHT - self.gap_y - PIPE_GAP,
        )
        return [top_rect, bottom_rect]

    def is_off_screen(self):
        return self.x + PIPE_WIDTH < 0


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy Bird - Realistic Remix")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.reset_game()

    def reset_game(self):
        self.bird = Bird()
        self.pipes = []
        self.score = 0
        self.game_over = False
        self.pipe_timer = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_q:
                        return False
                else:
                    if event.key == pygame.K_SPACE:
                        self.bird.flap()
        return True

    def update(self):
        if not self.game_over:
            self.bird.update()

            # Spawn pipes
            self.pipe_timer += 1
            if self.pipe_timer > 90:  # Spawn every 1.5 seconds at 60 FPS
                self.pipes.append(Pipe(SCREEN_WIDTH))
                self.pipe_timer = 0

            # Update pipes
            for pipe in self.pipes[:]:
                pipe.update()
                if pipe.is_off_screen():
                    self.pipes.remove(pipe)
                elif not pipe.passed and pipe.x + PIPE_WIDTH < self.bird.x:
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

    def draw(self):
        self.screen.fill(BLACK)

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
