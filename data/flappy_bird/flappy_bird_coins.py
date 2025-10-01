# SOURCE: flappy_bird.py
# REMIX: add collectible coins

"""
Flappy Bird Coins Remix - A remix of the original Flappy Bird game with collectible coins for bonus score.
The bird falls due to gravity and flaps upward when spacebar is pressed. Game ends on collision with pipes or ground.
This remix adds golden coins that spawn between pipes and award bonus points when collected.
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
COIN_SIZE = 20
COIN_VALUE = 5
BLACK = (0, 0, 0)
GREEN = (0, 255, 65)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)


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


class Coin:
    def __init__(self, x, gap_y):
        self.x = x + PIPE_WIDTH // 2  # Center coin in pipe gap
        self.y = gap_y + PIPE_GAP // 2  # Center coin vertically in gap
        self.collected = False

    def update(self):
        self.x -= PIPE_SPEED

    def draw(self, screen):
        if not self.collected:
            pygame.draw.circle(screen, GOLD, (int(self.x), int(self.y)), COIN_SIZE // 2)
            # Add inner circle for coin detail
            pygame.draw.circle(
                screen, WHITE, (int(self.x), int(self.y)), COIN_SIZE // 4
            )

    def get_rect(self):
        return pygame.Rect(
            self.x - COIN_SIZE // 2, self.y - COIN_SIZE // 2, COIN_SIZE, COIN_SIZE
        )

    def is_off_screen(self):
        return self.x + COIN_SIZE < 0


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy Bird - Coins Remix")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.reset_game()

    def reset_game(self):
        self.bird = Bird()
        self.pipes = []
        self.coins = []
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

            # Spawn pipes and coins
            self.pipe_timer += 1
            if self.pipe_timer > 90:  # Spawn every 1.5 seconds at 60 FPS
                new_pipe = Pipe(SCREEN_WIDTH)
                self.pipes.append(new_pipe)
                # Spawn coin with 70% chance
                if random.random() < 0.7:
                    self.coins.append(Coin(SCREEN_WIDTH, new_pipe.gap_y))
                self.pipe_timer = 0

            # Update pipes
            for pipe in self.pipes[:]:
                pipe.update()
                if pipe.is_off_screen():
                    self.pipes.remove(pipe)
                elif not pipe.passed and pipe.x + PIPE_WIDTH < self.bird.x:
                    pipe.passed = True
                    self.score += 1

            # Update coins
            for coin in self.coins[:]:
                coin.update()
                if coin.is_off_screen():
                    self.coins.remove(coin)

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

            # Coin collection
            for coin in self.coins:
                if not coin.collected and bird_rect.colliderect(coin.get_rect()):
                    coin.collected = True
                    self.score += COIN_VALUE

    def draw(self):
        self.screen.fill(BLACK)

        # Draw game objects
        self.bird.draw(self.screen)
        for pipe in self.pipes:
            pipe.draw(self.screen)
        for coin in self.coins:
            coin.draw(self.screen)

        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # Draw game over screen
        if self.game_over:
            game_over_text = self.font.render("Game Over!", True, WHITE)
            final_score_text = self.font.render(
                f"Final Score: {self.score}", True, WHITE
            )
            restart_text = self.font.render(
                "Press R to restart or Q to quit", True, WHITE
            )

            game_over_rect = game_over_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
            )
            final_score_rect = final_score_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 10)
            )
            restart_rect = restart_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30)
            )

            self.screen.blit(game_over_text, game_over_rect)
            self.screen.blit(final_score_text, final_score_rect)
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
