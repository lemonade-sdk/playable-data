# CREATE: space invaders

"""
Space Invaders

A classic arcade-style shooter game. The player controls a spaceship at the
bottom of the screen and must shoot down waves of alien invaders before they
reach the bottom. Invaders move side-to-side and descend toward the player.
Game ends when invaders reach the player's level.
"""

import pygame
import sys

# Initialize pygame
pygame.init()

# Display configuration
DISPLAY_WIDTH = 700
DISPLAY_HEIGHT = 550
BACKGROUND_COLOR = (0, 0, 0)
PRIMARY_COLOR = (0, 255, 65)
SECONDARY_COLOR = (255, 255, 255)

# Movement speeds
SHIP_VELOCITY = 6
PROJECTILE_VELOCITY = 8
ALIEN_VELOCITY = 1
ALIEN_DESCENT_AMOUNT = 25


class PlayerShip:
    """Player-controlled spaceship"""

    def __init__(self):
        self.rect_width = 35
        self.rect_height = 18
        self.position_x = DISPLAY_WIDTH // 2 - self.rect_width // 2
        self.position_y = DISPLAY_HEIGHT - 60
        self.velocity = SHIP_VELOCITY

    def move_to_left(self):
        """Move ship left if within bounds"""
        if self.position_x > 0:
            self.position_x -= self.velocity

    def move_to_right(self):
        """Move ship right if within bounds"""
        if self.position_x < DISPLAY_WIDTH - self.rect_width:
            self.position_x += self.velocity

    def render(self, surface):
        """Draw the player ship"""
        pygame.draw.rect(
            surface,
            PRIMARY_COLOR,
            (self.position_x, self.position_y, self.rect_width, self.rect_height),
        )

    def get_center_x(self):
        """Return horizontal center of ship"""
        return self.position_x + self.rect_width // 2


class Projectile:
    """Bullet fired by player"""

    def __init__(self, start_x, start_y):
        self.position_x = start_x
        self.position_y = start_y
        self.rect_width = 3
        self.rect_height = 12
        self.velocity = PROJECTILE_VELOCITY

    def advance(self):
        """Move projectile upward"""
        self.position_y -= self.velocity

    def render(self, surface):
        """Draw the projectile"""
        pygame.draw.rect(
            surface,
            PRIMARY_COLOR,
            (self.position_x, self.position_y, self.rect_width, self.rect_height),
        )

    def is_beyond_screen(self):
        """Check if projectile is off screen"""
        return self.position_y < 0


class AlienInvader:
    """Enemy alien invader"""

    def __init__(self, start_x, start_y):
        self.position_x = start_x
        self.position_y = start_y
        self.rect_width = 28
        self.rect_height = 22
        self.velocity = ALIEN_VELOCITY
        self.movement_direction = 1

    def advance(self):
        """Move alien horizontally"""
        self.position_x += self.velocity * self.movement_direction

    def descend(self):
        """Move alien down and reverse direction"""
        self.position_y += ALIEN_DESCENT_AMOUNT
        self.movement_direction *= -1

    def render(self, surface):
        """Draw the alien invader"""
        pygame.draw.rect(
            surface,
            PRIMARY_COLOR,
            (self.position_x, self.position_y, self.rect_width, self.rect_height),
        )
        # Draw eyes
        pygame.draw.rect(
            surface, BACKGROUND_COLOR, (self.position_x + 4, self.position_y + 6, 6, 6)
        )
        pygame.draw.rect(
            surface,
            BACKGROUND_COLOR,
            (self.position_x + 18, self.position_y + 6, 6, 6),
        )

    def check_edge_collision(self):
        """Check if alien hit screen edge"""
        return (
            self.position_x <= 0 or self.position_x >= DISPLAY_WIDTH - self.rect_width
        )


class GameController:
    """Main game controller and state manager"""

    def __init__(self):
        self.display_surface = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        pygame.display.set_caption("Space Invaders")
        self.game_clock = pygame.time.Clock()
        self.text_font = pygame.font.Font(None, 32)
        self.initialize_new_game()

    def initialize_new_game(self):
        """Setup new game state"""
        self.player_ship = PlayerShip()
        self.projectile_list = []
        self.alien_list = []
        self.current_score = 0
        self.game_has_ended = False
        self.player_won = False
        self.create_alien_formation()

    def create_alien_formation(self):
        """Generate grid of alien invaders"""
        for row_index in range(4):
            for column_index in range(9):
                alien_x = 90 + column_index * 65
                alien_y = 60 + row_index * 55
                self.alien_list.append(AlienInvader(alien_x, alien_y))

    def process_input_events(self):
        """Handle user input and window events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_has_ended:
                    self.fire_projectile()
                elif event.key == pygame.K_r and self.game_has_ended:
                    self.initialize_new_game()
                elif event.key == pygame.K_q and self.game_has_ended:
                    return False
        return True

    def fire_projectile(self):
        """Create a new projectile from player position"""
        projectile_x = self.player_ship.get_center_x()
        projectile_y = self.player_ship.position_y
        self.projectile_list.append(Projectile(projectile_x, projectile_y))

    def update_game_state(self):
        """Update all game entities"""
        if self.game_has_ended:
            return

        # Handle continuous player movement
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_a]:
            self.player_ship.move_to_left()
        if pressed_keys[pygame.K_RIGHT] or pressed_keys[pygame.K_d]:
            self.player_ship.move_to_right()

        # Update projectiles
        for projectile in self.projectile_list[:]:
            projectile.advance()
            if projectile.is_beyond_screen():
                self.projectile_list.remove(projectile)

        # Update aliens and check edge collision
        needs_to_descend = False
        for alien in self.alien_list:
            alien.advance()
            if alien.check_edge_collision():
                needs_to_descend = True

        if needs_to_descend:
            for alien in self.alien_list:
                alien.descend()

        # Check projectile-alien collisions
        self.check_collision_detection()

        # Check win condition
        if not self.alien_list:
            self.player_won = True
            self.game_has_ended = True

        # Check lose condition
        for alien in self.alien_list:
            if alien.position_y + alien.rect_height >= self.player_ship.position_y:
                self.game_has_ended = True
                break

    def check_collision_detection(self):
        """Detect and handle projectile-alien collisions"""
        for projectile in self.projectile_list[:]:
            for alien in self.alien_list[:]:
                if self.check_rectangles_overlap(projectile, alien):
                    if projectile in self.projectile_list:
                        self.projectile_list.remove(projectile)
                    if alien in self.alien_list:
                        self.alien_list.remove(alien)
                    self.current_score += 10
                    break

    def check_rectangles_overlap(self, projectile, alien):
        """Helper to check if two rectangles overlap"""
        return (
            projectile.position_x < alien.position_x + alien.rect_width
            and projectile.position_x + projectile.rect_width > alien.position_x
            and projectile.position_y < alien.position_y + alien.rect_height
            and projectile.position_y + projectile.rect_height > alien.position_y
        )

    def render_game(self):
        """Draw all visual elements"""
        self.display_surface.fill(BACKGROUND_COLOR)

        if not self.game_has_ended:
            self.player_ship.render(self.display_surface)

            for projectile in self.projectile_list:
                projectile.render(self.display_surface)

            for alien in self.alien_list:
                alien.render(self.display_surface)

        # Render score
        score_surface = self.text_font.render(
            f"Score: {self.current_score}", True, PRIMARY_COLOR
        )
        self.display_surface.blit(score_surface, (10, 10))

        # Render game over screen
        if self.game_has_ended:
            if self.player_won:
                status_text = self.text_font.render("VICTORY!", True, PRIMARY_COLOR)
            else:
                status_text = self.text_font.render("GAME OVER", True, PRIMARY_COLOR)

            instruction_text = self.text_font.render(
                "Press R to restart or Q to quit", True, PRIMARY_COLOR
            )

            status_rect = status_text.get_rect(
                center=(DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2 - 25)
            )
            instruction_rect = instruction_text.get_rect(
                center=(DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2 + 25)
            )

            self.display_surface.blit(status_text, status_rect)
            self.display_surface.blit(instruction_text, instruction_rect)

        pygame.display.flip()

    def execute_game_loop(self):
        """Main game loop"""
        is_running = True
        while is_running:
            is_running = self.process_input_events()
            self.update_game_state()
            self.render_game()
            self.game_clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    controller = GameController()
    controller.execute_game_loop()
