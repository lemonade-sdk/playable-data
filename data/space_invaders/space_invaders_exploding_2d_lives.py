"""
Space Invaders - Exploding Bullets + 2D Movement + Three Lives Triple Combo

Triple combination remix featuring exploding bullets powerup system, 2D player
movement, and three lives system. Player can collect powerups for explosive
ammunition, move in all directions within a defined area, and has multiple
lives with invulnerability periods after being hit.
Based on space_invaders_exploding_2d.py with three lives system added.
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
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
WHITE = (255, 255, 255)

# Game settings
PLAYER_SPEED = 5
BULLET_SPEED = 7
INVADER_SPEED = 1
INVADER_DROP_SPEED = 20
POWERUP_SPAWN_CHANCE = 0.002  # Probability per frame
EXPLOSION_RADIUS = 60
EXPLOSIVE_SHOTS = 10  # Number of explosive shots per powerup
PLAYER_MOVEMENT_AREA = 150  # Bottom area where player can move vertically
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
        self.explosive_shots = 0
        self.min_y = SCREEN_HEIGHT - PLAYER_MOVEMENT_AREA
        self.invulnerable_timer = 0

    def move_left(self):
        if self.x > 0:
            self.x -= self.speed

    def move_right(self):
        if self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed

    def move_up(self):
        if self.y > self.min_y:
            self.y -= self.speed

    def move_down(self):
        if self.y < SCREEN_HEIGHT - self.height:
            self.y += self.speed

    def has_explosive_shots(self):
        return self.explosive_shots > 0

    def use_explosive_shot(self):
        if self.explosive_shots > 0:
            self.explosive_shots -= 1

    def add_explosive_shots(self, amount):
        self.explosive_shots += amount

    def update(self):
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1

    def is_invulnerable(self):
        return self.invulnerable_timer > 0

    def make_invulnerable(self):
        self.invulnerable_timer = RESPAWN_INVULNERABILITY

    def draw(self, screen):
        # Flash when invulnerable, orange when has explosive shots, otherwise green
        if self.is_invulnerable() and (self.invulnerable_timer // 5) % 2:
            color = RED
        elif self.has_explosive_shots():
            color = ORANGE
        else:
            color = GREEN
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))


class Bullet:
    def __init__(self, x, y, explosive=False, direction=1):
        self.x = x
        self.y = y
        self.width = 3
        self.height = 10
        self.speed = BULLET_SPEED if direction == 1 else ENEMY_BULLET_SPEED
        self.explosive = explosive
        self.direction = direction  # 1 for up (player), -1 for down (enemy)

    def update(self):
        self.y -= self.speed * self.direction

    def draw(self, screen):
        if self.direction == 1:  # Player bullet
            color = ORANGE if self.explosive else GREEN
        else:  # Enemy bullet
            color = RED
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))

    def is_off_screen(self):
        return self.y < 0 or self.y > SCREEN_HEIGHT


class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 0
        self.max_radius = EXPLOSION_RADIUS
        self.duration = 20
        self.timer = self.duration

    def update(self):
        self.timer -= 1
        self.radius = (self.max_radius * (self.duration - self.timer)) / self.duration

    def is_finished(self):
        return self.timer <= 0

    def draw(self, screen):
        if self.timer > 0:
            alpha = int(255 * (self.timer / self.duration))
            color = (255, alpha, 0)  # Fade from yellow to red
            pygame.draw.circle(
                screen, color, (int(self.x), int(self.y)), int(self.radius), 2
            )


class Powerup:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.speed = 2
        self.pulse = 0

    def update(self):
        self.y += self.speed
        self.pulse += 0.2

    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT

    def draw(self, screen):
        # Pulsing effect
        size_offset = int(math.sin(self.pulse) * 3)
        width = self.width + size_offset
        height = self.height + size_offset
        x = self.x - size_offset // 2
        y = self.y - size_offset // 2

        pygame.draw.rect(screen, YELLOW, (x, y, width, height))
        pygame.draw.rect(screen, ORANGE, (x + 2, y + 2, width - 4, height - 4))


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

    def get_center(self):
        return (self.x + self.width // 2, self.y + self.height // 2)

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
        pygame.display.set_caption("Space Invaders - Exploding + 2D + Lives")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.reset_game()

    def reset_game(self):
        self.player = Player()
        self.player_bullets = []
        self.enemy_bullets = []
        self.invaders = []
        self.powerups = []
        self.explosions = []
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
                    explosive = self.player.has_explosive_shots()
                    if explosive:
                        self.player.use_explosive_shot()
                    self.player_bullets.append(Bullet(bullet_x, bullet_y, explosive))
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()
                elif event.key == pygame.K_q and self.game_over:
                    return False
        return True

    def spawn_powerup(self):
        if random.random() < POWERUP_SPAWN_CHANCE:
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = -20
            self.powerups.append(Powerup(x, y))

    def explode_at(self, x, y):
        self.explosions.append(Explosion(x, y))
        # Destroy invaders in explosion radius
        for invader in self.invaders[:]:
            inv_center = invader.get_center()
            distance = math.sqrt((inv_center[0] - x) ** 2 + (inv_center[1] - y) ** 2)
            if distance <= EXPLOSION_RADIUS:
                self.invaders.remove(invader)
                self.score += 10

    def update(self):
        if self.game_over:
            return

        # Update player
        self.player.update()

        # Handle player movement (2D)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.move_left()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.move_right()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.player.move_up()
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.player.move_down()

        # Spawn powerups
        self.spawn_powerup()

        # Update powerups
        for powerup in self.powerups[:]:
            powerup.update()
            if powerup.is_off_screen():
                self.powerups.remove(powerup)

        # Check powerup collection
        for powerup in self.powerups[:]:
            if (
                powerup.x < self.player.x + self.player.width
                and powerup.x + powerup.width > self.player.x
                and powerup.y < self.player.y + self.player.height
                and powerup.y + powerup.height > self.player.y
            ):
                self.powerups.remove(powerup)
                self.player.add_explosive_shots(EXPLOSIVE_SHOTS)

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

        # Update explosions
        for explosion in self.explosions[:]:
            explosion.update()
            if explosion.is_finished():
                self.explosions.remove(explosion)

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

                    if bullet.explosive:
                        # Create explosion
                        self.explode_at(bullet.x, bullet.y)
                    else:
                        # Normal hit
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

        # Check if invaders reach player area
        for invader in self.invaders:
            if invader.y + invader.height >= self.player.min_y:
                self.game_over = True
                break

    def draw(self):
        self.screen.fill(BLACK)

        # Draw player movement area boundary
        pygame.draw.line(
            self.screen,
            GREEN,
            (0, SCREEN_HEIGHT - PLAYER_MOVEMENT_AREA),
            (SCREEN_WIDTH, SCREEN_HEIGHT - PLAYER_MOVEMENT_AREA),
            1,
        )

        if not self.game_over:
            # Draw game objects
            self.player.draw(self.screen)

            for bullet in self.player_bullets:
                bullet.draw(self.screen)

            for bullet in self.enemy_bullets:
                bullet.draw(self.screen)

            for invader in self.invaders:
                invader.draw(self.screen)

            for powerup in self.powerups:
                powerup.draw(self.screen)

            for explosion in self.explosions:
                explosion.draw(self.screen)

        # Draw score, lives, and explosive shots
        score_text = self.font.render(f"Score: {self.score}", True, GREEN)
        lives_text = self.font.render(f"Lives: {self.lives}", True, GREEN)
        explosive_text = self.small_font.render(
            f"Explosive Shots: {self.player.explosive_shots}", True, ORANGE
        )
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (10, 50))
        self.screen.blit(explosive_text, (10, 80))

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
