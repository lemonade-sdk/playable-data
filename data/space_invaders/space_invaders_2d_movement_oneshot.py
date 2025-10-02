# CREATE: space invaders where I can move in 2 dimensions

"""
Space Invaders 2D Movement Game

A space shooter where the player controls a ship that can move in both horizontal
and vertical directions instead of just left and right. The player can move freely
within the lower portion of the screen to dodge enemy bullets and position for
attacks. Implementation uses pygame with 2D movement controls, collision detection,
and enhanced positioning mechanics.
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
WHITE = (255, 255, 255)

# Game settings
PLAYER_SPEED = 5
BULLET_SPEED = 7
INVADER_SPEED = 1
INVADER_DROP_SPEED = 20
PLAYER_MOVEMENT_AREA = 150  # Bottom area where player can move vertically


class Player:
    def __init__(self):
        self.width = 40
        self.height = 20
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - 50
        self.speed = PLAYER_SPEED
        self.min_y = SCREEN_HEIGHT - PLAYER_MOVEMENT_AREA

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

    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, BLACK, (self.x + 5, self.y + 5, 5, 5))
        pygame.draw.rect(screen, BLACK, (self.x + 20, self.y + 5, 5, 5))


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Invaders - 2D Movement")
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
                    self.bullets.append(Bullet(bullet_x, bullet_y))
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()
                elif event.key == pygame.K_q and self.game_over:
                    return False
        return True

    def update(self):
        if self.game_over:
            return

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
