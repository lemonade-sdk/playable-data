# CREATE: space invaders

"""
Space Invaders

BUG FIX: In PlayerCraft's draw method, an incorrect attribute name is used for
the width dimension. Check what the width is called in __init__ versus the draw method.

Classic space shooter game implemented with pygame. Player pilots a ship that
must shoot down formations of alien invaders before they reach the bottom.
Features collision detection, scoring, and win/lose conditions.
"""

import pygame
import sys

# Initialize pygame
pygame.init()

# Screen constants
SCREEN_W = 640
SCREEN_H = 520
BG_COLOR = (0, 0, 0)
SPRITE_COLOR = (0, 255, 65)
TEXT_COLOR = (255, 255, 255)

# Game parameters
P_SPEED = 4
B_SPEED = 8
E_SPEED = 1.5
E_DROP = 18


class PlayerCraft:
    """Player's spacecraft at bottom of screen"""

    def __init__(self):
        self.w = 42
        self.h = 18
        self.x = SCREEN_W // 2 - self.w // 2
        self.y = SCREEN_H - 45
        self.speed = P_SPEED

    def move_left(self):
        """Shift craft left"""
        if self.x > 0:
            self.x -= self.speed

    def move_right(self):
        """Shift craft right"""
        if self.x < SCREEN_W - self.w:
            self.x += self.speed

    def draw(self, screen):
        """Render the craft"""
        # Fixed: use correct attribute name self.w instead of self.width
        pygame.draw.rect(screen, SPRITE_COLOR, (self.x, self.y, self.w, self.h))

    def cannon_pos(self):
        """Calculate firing position"""
        return self.x + self.w // 2, self.y


class Bullet:
    """Player's bullet projectile"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 4
        self.h = 12
        self.speed = B_SPEED

    def update(self):
        """Move bullet upward"""
        self.y -= self.speed

    def draw(self, screen):
        """Render the bullet"""
        pygame.draw.rect(screen, SPRITE_COLOR, (self.x, self.y, self.w, self.h))

    def off_screen(self):
        """Check if out of bounds"""
        return self.y < 0

    def collides_with(self, enemy):
        """Check collision with enemy"""
        return (
            self.x < enemy.x + enemy.w
            and self.x + self.w > enemy.x
            and self.y < enemy.y + enemy.h
            and self.y + self.h > enemy.y
        )


class Enemy:
    """Alien enemy invader"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 26
        self.h = 20
        self.speed = E_SPEED
        self.direction = 1

    def update(self):
        """Move enemy horizontally"""
        self.x += self.speed * self.direction

    def reverse_and_drop(self):
        """Reverse direction and move down"""
        self.y += E_DROP
        self.direction *= -1

    def draw(self, screen):
        """Render the enemy"""
        pygame.draw.rect(screen, SPRITE_COLOR, (self.x, self.y, self.w, self.h))
        # Simple eyes
        pygame.draw.rect(screen, BG_COLOR, (self.x + 4, self.y + 5, 4, 4))
        pygame.draw.rect(screen, BG_COLOR, (self.x + 18, self.y + 5, 4, 4))

    def at_edge(self):
        """Check if at screen edge"""
        return self.x <= 0 or self.x >= SCREEN_W - self.w

    def reached_bottom(self, threshold):
        """Check if reached bottom threshold"""
        return self.y + self.h >= threshold


class GameManager:
    """Manages overall game state and logic"""

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Space Invaders")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 28)
        self.init_game()

    def init_game(self):
        """Setup initial game state"""
        self.player = PlayerCraft()
        self.bullets = []
        self.enemies = []
        self.score = 0
        self.game_over = False
        self.won = False
        self.build_enemy_formation()

    def build_enemy_formation(self):
        """Create enemy grid formation"""
        num_rows = 5
        num_cols = 8
        spacing_x = 70
        spacing_y = 45
        offset_x = 60
        offset_y = 50

        for row in range(num_rows):
            for col in range(num_cols):
                ex = offset_x + col * spacing_x
                ey = offset_y + row * spacing_y
                self.enemies.append(Enemy(ex, ey))

    def handle_input(self):
        """Process user input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over:
                    self.shoot()
                elif event.key == pygame.K_r and self.game_over:
                    self.init_game()
                elif event.key == pygame.K_q and self.game_over:
                    return False

        return True

    def shoot(self):
        """Fire a bullet from player position"""
        bx, by = self.player.cannon_pos()
        self.bullets.append(Bullet(bx, by))

    def update(self):
        """Update game state each frame"""
        if self.game_over:
            return

        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.move_left()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.move_right()

        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.off_screen():
                self.bullets.remove(bullet)

        # Update enemies
        edge_reached = False
        for enemy in self.enemies:
            enemy.update()
            if enemy.at_edge():
                edge_reached = True

        if edge_reached:
            for enemy in self.enemies:
                enemy.reverse_and_drop()

        # Collision detection
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.collides_with(enemy):
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    if enemy in self.enemies:
                        self.enemies.remove(enemy)
                        self.score += 10
                    break

        # Win condition
        if not self.enemies:
            self.won = True
            self.game_over = True

        # Lose condition
        for enemy in self.enemies:
            if enemy.reached_bottom(self.player.y):
                self.game_over = True
                break

    def draw(self):
        """Render all game elements"""
        self.screen.fill(BG_COLOR)

        if not self.game_over:
            self.player.draw(self.screen)

            for bullet in self.bullets:
                bullet.draw(self.screen)

            for enemy in self.enemies:
                enemy.draw(self.screen)

        # Score
        score_text = self.font.render(f"Score: {self.score}", True, SPRITE_COLOR)
        self.screen.blit(score_text, (10, 10))

        # Game over screen
        if self.game_over:
            if self.won:
                status = "VICTORY!"
            else:
                status = "GAME OVER"

            status_text = self.font.render(status, True, SPRITE_COLOR)
            info_text = self.font.render(
                "Press R to restart or Q to quit", True, SPRITE_COLOR
            )

            status_rect = status_text.get_rect(
                center=(SCREEN_W // 2, SCREEN_H // 2 - 22)
            )
            info_rect = info_text.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 22))

            self.screen.blit(status_text, status_rect)
            self.screen.blit(info_text, info_rect)

        pygame.display.flip()

    def run(self):
        """Main game loop"""
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = GameManager()
    game.run()
