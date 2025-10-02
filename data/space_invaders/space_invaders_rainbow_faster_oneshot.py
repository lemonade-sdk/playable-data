# CREATE: space invaders with rainbow colored invaders that move fast

"""
Space Invaders Rainbow Fast Game

A space shooter where the player controls a ship to destroy invading aliens that
display rainbow colors and move at high speed across and down the screen. Each
invader is rendered in different rainbow colors while moving quickly in formation,
creating colorful high-speed gameplay. Implementation uses pygame with dynamic
color assignment, accelerated movement patterns, collision detection, and visual
color systems.
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
BLACK = (0, 0, 0)
GREEN = (0, 255, 65)
WHITE = (255, 255, 255)

# Game settings
PLAYER_SPEED = 5
BULLET_SPEED = 7
INVADER_SPEED = 2  # 2x faster than original
INVADER_DROP_SPEED = 40  # 2x faster drop speed


def hsv_to_rgb(h, s, v):
    """Convert HSV color to RGB"""
    h = h % 360
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c

    if 0 <= h < 60:
        r, g, b = c, x, 0
    elif 60 <= h < 120:
        r, g, b = x, c, 0
    elif 120 <= h < 180:
        r, g, b = 0, c, x
    elif 180 <= h < 240:
        r, g, b = 0, x, c
    elif 240 <= h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x

    return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))


class Player:
    def __init__(self):
        self.width = 40
        self.height = 20
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - 50
        self.speed = PLAYER_SPEED

    def move_left(self):
        if self.x > 0:
            self.x -= self.speed

    def move_right(self):
        if self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, (self.x, self.y, self.width, self.height))


class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 3
        self.height = 10
        self.speed = BULLET_SPEED

    def update(self):
        self.y -= self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, (self.x, self.y, self.width, self.height))

    def is_off_screen(self):
        return self.y < 0


class Invader:
    def __init__(self, x, y, row, col):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 20
        self.speed = INVADER_SPEED
        self.direction = 1
        # Generate rainbow color based on position
        hue = (row * 10 + col * 36) % 360  # Spread colors across rainbow
        self.color = hsv_to_rgb(hue, 1.0, 1.0)

    def update(self):
        self.x += self.speed * self.direction

    def drop_down(self):
        self.y += INVADER_DROP_SPEED
        self.direction *= -1

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, BLACK, (self.x + 5, self.y + 5, 5, 5))
        pygame.draw.rect(screen, BLACK, (self.x + 20, self.y + 5, 5, 5))


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Invaders - Rainbow + Faster")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.reset_game()

    def reset_game(self):
        self.player = Player()
        self.bullets = []
        self.invaders = []
        self.score = 0
        self.game_over = False
        self.victory = False

        # Create invader grid with rainbow colors
        for row in range(5):
            for col in range(10):
                x = 80 + col * 60
                y = 50 + row * 50
                self.invaders.append(Invader(x, y, row, col))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over:
                    # Shoot bullet
                    bullet_x = self.player.x + self.player.width // 2
                    bullet_y = self.player.y
                    self.bullets.append(Bullet(bullet_x, bullet_y))
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()
                elif event.key == pygame.K_q and self.game_over:
                    return False
        return True

    def update(self):
        if self.game_over:
            return

        # Handle player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.move_left()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.move_right()

        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.bullets.remove(bullet)

        # Update invaders
        edge_hit = False
        for invader in self.invaders:
            invader.update()
            if invader.x <= 0 or invader.x >= SCREEN_WIDTH - invader.width:
                edge_hit = True

        # Drop invaders down if edge hit
        if edge_hit:
            for invader in self.invaders:
                invader.drop_down()

        # Check bullet-invader collisions
        for bullet in self.bullets[:]:
            for invader in self.invaders[:]:
                if (
                    bullet.x < invader.x + invader.width
                    and bullet.x + bullet.width > invader.x
                    and bullet.y < invader.y + invader.height
                    and bullet.y + bullet.height > invader.y
                ):
                    self.bullets.remove(bullet)
                    self.invaders.remove(invader)
                    self.score += 10
                    break

        # Check if player wins
        if not self.invaders:
            self.victory = True
            self.game_over = True

        # Check if invaders reach bottom
        for invader in self.invaders:
            if invader.y + invader.height >= self.player.y:
                self.game_over = True
                break

    def draw(self):
        self.screen.fill(BLACK)

        if not self.game_over:
            # Draw game objects
            self.player.draw(self.screen)

            for bullet in self.bullets:
                bullet.draw(self.screen)

            for invader in self.invaders:
                invader.draw(self.screen)

        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, GREEN)
        self.screen.blit(score_text, (10, 10))

        # Draw game over screen
        if self.game_over:
            if self.victory:
                game_over_text = self.font.render("VICTORY!", True, GREEN)
            else:
                game_over_text = self.font.render("GAME OVER", True, GREEN)

            restart_text = self.font.render(
                "Press R to restart or Q to quit", True, GREEN
            )

            # Center the text
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


# Main execution
if __name__ == "__main__":
    game = Game()
    game.run()
