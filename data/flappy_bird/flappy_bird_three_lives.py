"""
Flappy Bird Three Lives Remix - A remix of the original Flappy Bird with a 3-lives system.
The bird falls due to gravity and flaps upward when spacebar is pressed. Game ends when all lives are lost.
This remix gives players 3 lives, allowing them to continue playing after collisions by respawning
the bird at the starting position, making the game more forgiving for learning players.
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
PIPE_GAP = 200
PIPE_SPEED = 3
GRAVITY = 0.5
FLAP_STRENGTH = -8
STARTING_LIVES = 3
RESPAWN_DELAY = 60  # Frames to wait before respawning (1 second at 60 FPS)
BLACK = (0, 0, 0)
GREEN = (0, 255, 65)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)


class Bird:
    def __init__(self):
        self.reset_position()
        self.velocity = 0

    def reset_position(self):
        self.x = 100
        self.y = SCREEN_HEIGHT // 2

    def flap(self):
        self.velocity = FLAP_STRENGTH

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity

    def draw(self, screen, lives):
        # Change bird color based on remaining lives
        if lives == 3:
            color = GREEN
        elif lives == 2:
            color = YELLOW
        else:  # lives == 1
            color = RED
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), BIRD_SIZE // 2)

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
        pygame.display.set_caption("Flappy Bird - Three Lives Remix")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.reset_game()

    def reset_game(self):
        self.bird = Bird()
        self.pipes = []
        self.score = 0
        self.lives = STARTING_LIVES
        self.game_over = False
        self.pipe_timer = 0
        self.respawn_timer = 0
        self.respawning = False

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
                    if event.key == pygame.K_SPACE and not self.respawning:
                        self.bird.flap()
        return True

    def lose_life(self):
        self.lives -= 1
        if self.lives <= 0:
            self.game_over = True
        else:
            # Start respawn process
            self.respawning = True
            self.respawn_timer = RESPAWN_DELAY
            self.bird.reset_position()
            self.bird.velocity = 0

    def update(self):
        if not self.game_over:
            # Handle respawn timer
            if self.respawning:
                self.respawn_timer -= 1
                if self.respawn_timer <= 0:
                    self.respawning = False
                return  # Don't update game during respawn

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
                self.lose_life()

            # Pipe collision
            for pipe in self.pipes:
                for pipe_rect in pipe.get_rects():
                    if bird_rect.colliderect(pipe_rect):
                        self.lose_life()
                        break

    def draw(self):
        self.screen.fill(BLACK)

        # Draw game objects
        if not self.respawning:  # Only draw bird when not respawning
            self.bird.draw(self.screen, self.lives)
        for pipe in self.pipes:
            pipe.draw(self.screen)

        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # Draw respawn message
        if self.respawning:
            respawn_text = self.font.render("Respawning...", True, WHITE)
            respawn_rect = respawn_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            )
            self.screen.blit(respawn_text, respawn_rect)

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
