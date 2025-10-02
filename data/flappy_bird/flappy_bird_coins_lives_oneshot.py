# CREATE: flappy bird with collectible coins and 3 lives

"""
Flappy Bird Coins Lives Game

A side-scrolling game where the player controls a bird that must navigate through pipe gaps
while collecting coins for bonus points and having three lives for multiple attempts. The bird
falls due to gravity and flaps upward when spacebar is pressed. Coins spawn between pipes for
additional score, and the player respawns after collisions until all three lives are lost.
Implementation uses pygame with coin collection mechanics, life tracking, respawn systems,
and collision detection.
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
STARTING_LIVES = 3
RESPAWN_DELAY = 60  # Frames to wait before respawning (1 second at 60 FPS)
BLACK = (0, 0, 0)
GREEN = (0, 255, 65)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
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
        self.gap_y = random.randint(150, SCREEN_HEIGHT - 150)
        self.passed = False

    def update(self):
        self.x -= PIPE_SPEED

    def draw(self, screen):
        # Draw top pipe
        pygame.draw.rect(
            screen,
            GREEN,
            (self.x, 0, PIPE_WIDTH, self.gap_y - PIPE_GAP // 2),
        )
        # Draw bottom pipe
        pygame.draw.rect(
            screen,
            GREEN,
            (
                self.x,
                self.gap_y + PIPE_GAP // 2,
                PIPE_WIDTH,
                SCREEN_HEIGHT - (self.gap_y + PIPE_GAP // 2),
            ),
        )

    def get_rects(self):
        top_rect = pygame.Rect(self.x, 0, PIPE_WIDTH, self.gap_y - PIPE_GAP // 2)
        bottom_rect = pygame.Rect(
            self.x,
            self.gap_y + PIPE_GAP // 2,
            PIPE_WIDTH,
            SCREEN_HEIGHT - (self.gap_y + PIPE_GAP // 2),
        )
        return [top_rect, bottom_rect]

    def is_off_screen(self):
        return self.x + PIPE_WIDTH < 0


class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.collected = False

    def update(self):
        self.x -= PIPE_SPEED

    def draw(self, screen):
        if not self.collected:
            pygame.draw.circle(screen, GOLD, (int(self.x), int(self.y)), COIN_SIZE // 2)
            # Add a simple shine effect
            pygame.draw.circle(screen, WHITE, (int(self.x - 3), int(self.y - 3)), 3)

    def get_rect(self):
        return pygame.Rect(
            self.x - COIN_SIZE // 2, self.y - COIN_SIZE // 2, COIN_SIZE, COIN_SIZE
        )

    def is_off_screen(self):
        return self.x + COIN_SIZE < 0


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
        self.coins = []
        self.score = 0
        self.lives = STARTING_LIVES
        self.game_over = False
        self.respawn_timer = 0
        self.pipe_timer = 0

    def spawn_pipe(self):
        pipe = Pipe(SCREEN_WIDTH)
        self.pipes.append(pipe)

        # Spawn coin in the gap with 70% chance
        if random.random() < 0.7:
            coin_x = pipe.x + PIPE_WIDTH // 2
            coin_y = pipe.gap_y + random.randint(-30, 30)
            self.coins.append(Coin(coin_x, coin_y))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not self.game_over and self.respawn_timer == 0:
                        self.bird.flap()
                elif self.game_over:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_q:
                        return False
        return True

    def update(self):
        if not self.game_over and self.respawn_timer == 0:
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

            # Update coins
            for coin in self.coins[:]:
                coin.update()
                if coin.is_off_screen():
                    self.coins.remove(coin)

            # Check for scoring (passing pipes)
            for pipe in self.pipes:
                if not pipe.passed and pipe.x + PIPE_WIDTH < self.bird.x:
                    pipe.passed = True
                    self.score += 1

            # Check coin collection
            for coin in self.coins:
                if not coin.collected and self.bird.get_rect().colliderect(
                    coin.get_rect()
                ):
                    coin.collected = True
                    self.score += COIN_VALUE

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

        # Handle respawn timer
        if self.respawn_timer > 0:
            self.respawn_timer -= 1
            if self.respawn_timer == 0:
                self.bird.reset_position()
                self.bird.velocity = 0

    def lose_life(self):
        self.lives -= 1
        if self.lives <= 0:
            self.game_over = True
        else:
            self.respawn_timer = RESPAWN_DELAY

    def draw(self):
        self.screen.fill(BLACK)

        if not self.game_over:
            # Draw game objects
            self.bird.draw(self.screen, self.lives)
            for pipe in self.pipes:
                pipe.draw(self.screen)
            for coin in self.coins:
                coin.draw(self.screen)

        # Draw score and lives
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (10, 50))

        # Draw respawn message
        if self.respawn_timer > 0:
            respawn_text = self.font.render("Respawning...", True, YELLOW)
            text_rect = respawn_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            )
            self.screen.blit(respawn_text, text_rect)

        # Draw game over screen
        if self.game_over:
            game_over_text = self.font.render("Game Over!", True, RED)
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
