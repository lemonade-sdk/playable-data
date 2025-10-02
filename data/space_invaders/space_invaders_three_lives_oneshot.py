# CREATE: space invaders with 3 lives

"""
Space Invaders Three Lives Game

A space shooter where the player controls a ship to destroy invading aliens with
a three-lives system. The player can be hit multiple times before game over, with
lives displayed on screen and respawn mechanics after each hit. Game ends when
all three lives are lost. Implementation uses pygame with life tracking, respawn
mechanics, and collision detection.
"""

import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLACK = (0, 0, 0)
GREEN = (0, 255, 65)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

# Game settings
PLAYER_SPEED = 5
BULLET_SPEED = 7
INVADER_SPEED = 1
INVADER_DROP_SPEED = 20
ENEMY_BULLET_SPEED = 4
ENEMY_SHOOT_CHANCE = 0.002  # Probability per frame per invader
STARTING_LIVES = 3
RESPAWN_INVULNERABILITY = 120  # Frames of invulnerability after respawn


class Player:
    def __init__(self):
        self.width = 40
        self.height = 20
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - 50
        self.speed = PLAYER_SPEED
        self.invulnerable_timer = 0

    def move_left(self):
        if self.x > 0:
            self.x -= self.speed

    def move_right(self):
        if self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed

    def update(self):
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1

    def is_invulnerable(self):
        return self.invulnerable_timer > 0

    def make_invulnerable(self):
        self.invulnerable_timer = RESPAWN_INVULNERABILITY

    def draw(self, screen):
        # Flash when invulnerable
        if self.is_invulnerable() and (self.invulnerable_timer // 5) % 2:
            color = RED
        else:
            color = GREEN
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))


class Bullet:
    def __init__(self, x, y, direction=1):
        self.x = x
        self.y = y
        self.width = 3
        self.height = 10
        self.speed = BULLET_SPEED if direction == 1 else ENEMY_BULLET_SPEED
        self.direction = direction  # 1 for up (player), -1 for down (enemy)

    def update(self):
        self.y -= self.speed * self.direction

    def draw(self, screen):
        color = GREEN if self.direction == 1 else RED
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))

    def is_off_screen(self):
        return self.y < 0 or self.y > SCREEN_HEIGHT


class Invader:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 20
        self.speed = INVADER_SPEED
        self.direction = 1

    def update(self):
        self.x += self.speed * self.direction

    def drop_down(self):
        self.y += INVADER_DROP_SPEED
        self.direction *= -1

    def can_shoot(self, invaders):
        # Only shoot if no invader is directly below
        for other in invaders:
            if (
                other != self
                and abs(other.x - self.x) < self.width
                and other.y > self.y
            ):
                return False
        return True

    def shoot(self):
        bullet_x = self.x + self.width // 2
        bullet_y = self.y + self.height
        return Bullet(bullet_x, bullet_y, direction=-1)

    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, BLACK, (self.x + 5, self.y + 5, 5, 5))
        pygame.draw.rect(screen, BLACK, (self.x + 20, self.y + 5, 5, 5))


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Invaders - Three Lives")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.reset_game()

    def reset_game(self):
        self.player = Player()
        self.player_bullets = []
        self.enemy_bullets = []
        self.invaders = []
        self.score = 0
        self.lives = STARTING_LIVES
        self.game_over = False
        self.victory = False

        # Create invader grid
        for row in range(5):
            for col in range(10):
                x = 80 + col * 60
                y = 50 + row * 50
                self.invaders.append(Invader(x, y))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over:
                    # Shoot bullet
                    bullet_x = self.player.x + self.player.width // 2
                    bullet_y = self.player.y
                    self.player_bullets.append(Bullet(bullet_x, bullet_y))
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()
                elif event.key == pygame.K_q and self.game_over:
                    return False
        return True

    def update(self):
        if self.game_over:
            return

        # Update player
        self.player.update()

        # Handle player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.move_left()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.move_right()

        # Update player bullets
        for bullet in self.player_bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.player_bullets.remove(bullet)

        # Update enemy bullets
        for bullet in self.enemy_bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.enemy_bullets.remove(bullet)

        # Invaders shoot randomly
        for invader in self.invaders:
            if random.random() < ENEMY_SHOOT_CHANCE and invader.can_shoot(
                self.invaders
            ):
                self.enemy_bullets.append(invader.shoot())

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

        # Check player bullet-invader collisions
        for bullet in self.player_bullets[:]:
            for invader in self.invaders[:]:
                if (
                    bullet.x < invader.x + invader.width
                    and bullet.x + bullet.width > invader.x
                    and bullet.y < invader.y + invader.height
                    and bullet.y + bullet.height > invader.y
                ):
                    self.player_bullets.remove(bullet)
                    self.invaders.remove(invader)
                    self.score += 10
                    break

        # Check enemy bullet-player collisions
        if not self.player.is_invulnerable():
            for bullet in self.enemy_bullets[:]:
                if (
                    bullet.x < self.player.x + self.player.width
                    and bullet.x + bullet.width > self.player.x
                    and bullet.y < self.player.y + self.player.height
                    and bullet.y + bullet.height > self.player.y
                ):
                    self.enemy_bullets.remove(bullet)
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
                    else:
                        # Respawn with invulnerability
                        self.player.make_invulnerable()
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

            for bullet in self.player_bullets:
                bullet.draw(self.screen)

            for bullet in self.enemy_bullets:
                bullet.draw(self.screen)

            for invader in self.invaders:
                invader.draw(self.screen)

        # Draw score and lives
        score_text = self.font.render(f"Score: {self.score}", True, GREEN)
        lives_text = self.font.render(f"Lives: {self.lives}", True, GREEN)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (10, 50))

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
