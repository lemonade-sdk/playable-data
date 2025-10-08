# CREATE: flappy bird

"""
Flappy Bird - Navigate a bird through obstacles by controlling its flight.
Press spacebar to make the bird flap its wings and rise. Gravity pulls it down constantly.
Pass through gaps in pipes to score points. Game ends if you hit a pipe or boundary.

Fix: In the draw_game method, use the correct method name self.bird.draw() instead of self.bird.render().
"""

import pygame
import random
import sys

# Initialize
pygame.init()

# Constants
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700
BIRD_RADIUS = 18
PIPE_WIDTH = 90
PIPE_GAP = 220
PIPE_SPEED = 4
GRAVITY = 0.6
FLAP_POWER = -9
BLACK = (0, 0, 0)
GREEN = (0, 255, 65)
WHITE = (255, 255, 255)


class Bird:
    def __init__(self):
        self.x = 120
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0

    def flap(self):
        self.velocity = FLAP_POWER

    def advance(self):
        self.velocity += GRAVITY
        self.y += self.velocity

    def draw(self, screen):
        pygame.draw.circle(screen, GREEN, (int(self.x), int(self.y)), BIRD_RADIUS)

    def bounds(self):
        return pygame.Rect(
            self.x - BIRD_RADIUS, self.y - BIRD_RADIUS, BIRD_RADIUS * 2, BIRD_RADIUS * 2
        )


class Pipe:
    def __init__(self, x_position):
        self.x = x_position
        self.gap_start = random.randint(150, SCREEN_HEIGHT - 150 - PIPE_GAP)
        self.has_passed = False

    def advance(self):
        self.x -= PIPE_SPEED

    def draw(self, screen):
        # Top pipe
        pygame.draw.rect(screen, GREEN, (self.x, 0, PIPE_WIDTH, self.gap_start))
        # Bottom pipe
        gap_end = self.gap_start + PIPE_GAP
        pygame.draw.rect(
            screen, GREEN, (self.x, gap_end, PIPE_WIDTH, SCREEN_HEIGHT - gap_end)
        )

    def collision_bounds(self):
        top_rect = pygame.Rect(self.x, 0, PIPE_WIDTH, self.gap_start)
        gap_end = self.gap_start + PIPE_GAP
        bottom_rect = pygame.Rect(self.x, gap_end, PIPE_WIDTH, SCREEN_HEIGHT - gap_end)
        return [top_rect, bottom_rect]

    def is_past_screen(self):
        return self.x + PIPE_WIDTH < 0


class FlappyGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy Bird")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 40)
        self.initialize()

    def initialize(self):
        self.bird = Bird()
        self.pipe_list = []
        self.score = 0
        self.game_over = False
        self.spawn_timer = 0

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_r:
                        self.initialize()
                    elif event.key == pygame.K_q:
                        return False
                else:
                    if event.key == pygame.K_SPACE:
                        self.bird.flap()
        return True

    def update_game(self):
        if not self.game_over:
            self.bird.advance()

            # Spawn new pipes
            self.spawn_timer += 1
            if self.spawn_timer > 80:  # Faster spawning
                self.pipe_list.append(Pipe(SCREEN_WIDTH))
                self.spawn_timer = 0

            # Update all pipes
            for pipe in self.pipe_list[:]:
                pipe.advance()
                if pipe.is_past_screen():
                    self.pipe_list.remove(pipe)
                elif not pipe.has_passed and pipe.x + PIPE_WIDTH < self.bird.x:
                    pipe.has_passed = True
                    self.score += 1

            # Collision detection
            bird_bounds = self.bird.bounds()

            # Screen boundary check
            if self.bird.y <= 0 or self.bird.y >= SCREEN_HEIGHT:
                self.game_over = True

            # Pipe collision check
            for pipe in self.pipe_list:
                for rect in pipe.collision_bounds():
                    if bird_bounds.colliderect(rect):
                        self.game_over = True

    def draw_game(self):
        self.screen.fill(BLACK)

        # Draw entities
        self.bird.draw(self.screen)  # Fixed: Use draw() instead of render()
        for pipe in self.pipe_list:
            pipe.draw(self.screen)

        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (15, 15))

        # Draw game over overlay
        if self.game_over:
            over_text = self.font.render("Game Over!", True, WHITE)
            instruction_text = self.font.render(
                "Press R to restart or Q to quit", True, WHITE
            )

            over_rect = over_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 35)
            )
            instruction_rect = instruction_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 35)
            )

            self.screen.blit(over_text, over_rect)
            self.screen.blit(instruction_text, instruction_rect)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.process_events()
            self.update_game()
            self.draw_game()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = FlappyGame()
    game.run()
