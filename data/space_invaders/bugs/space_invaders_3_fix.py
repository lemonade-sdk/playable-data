# CREATE: space invaders

"""
Space Invaders

BUG FIX: When descending invaders, the loop range goes beyond the list length.
Check the loop that iterates through invaders to make them descend - the range
calculation is off by one.

A pygame implementation of the classic Space Invaders arcade game. The player
controls a defender ship that must eliminate all invading aliens. Aliens move
in formation across and down the screen. Victory is achieved by destroying all
aliens. Defeat occurs when aliens reach the bottom of the screen.
"""

import pygame
import sys

# Initialize pygame systems
pygame.init()

# Window settings
WINDOW_WIDTH = 750
WINDOW_HEIGHT = 580
COLOR_BLACK = (0, 0, 0)
COLOR_GREEN = (0, 255, 65)
COLOR_WHITE = (255, 255, 255)

# Physics constants
DEFENDER_SPEED = 6
MISSILE_SPEED = 7
INVADER_SPEED = 1.2
INVADER_DROP_DISTANCE = 22


class DefenderShip:
    """Player's defensive ship"""

    def __init__(self):
        self.width = 38
        self.height = 20
        self.pos_x = WINDOW_WIDTH // 2 - self.width // 2
        self.pos_y = WINDOW_HEIGHT - 50
        self.move_speed = DEFENDER_SPEED

    def shift_left(self):
        """Move defender left"""
        if self.pos_x > 0:
            self.pos_x -= self.move_speed

    def shift_right(self):
        """Move defender right"""
        if self.pos_x < WINDOW_WIDTH - self.width:
            self.pos_x += self.move_speed

    def render_to_screen(self, display):
        """Draw the defender"""
        pygame.draw.rect(
            display, COLOR_GREEN, (self.pos_x, self.pos_y, self.width, self.height)
        )

    def get_gun_position(self):
        """Get position to fire from"""
        center_x = self.pos_x + self.width // 2
        return (center_x, self.pos_y)


class Missile:
    """Projectile fired by defender"""

    def __init__(self, start_pos):
        self.pos_x = start_pos[0]
        self.pos_y = start_pos[1]
        self.width = 3
        self.height = 11
        self.move_speed = MISSILE_SPEED

    def update_position(self):
        """Move missile upward"""
        self.pos_y -= self.move_speed

    def render_to_screen(self, display):
        """Draw the missile"""
        pygame.draw.rect(
            display, COLOR_GREEN, (self.pos_x, self.pos_y, self.width, self.height)
        )

    def has_left_screen(self):
        """Check if missile is off screen"""
        return self.pos_y < 0

    def get_bounds(self):
        """Return bounding box"""
        return (self.pos_x, self.pos_y, self.width, self.height)


class InvaderAlien:
    """Enemy alien invader"""

    def __init__(self, grid_x, grid_y):
        self.pos_x = grid_x
        self.pos_y = grid_y
        self.width = 30
        self.height = 22
        self.move_speed = INVADER_SPEED
        self.travel_direction = 1

    def update_position(self):
        """Move alien horizontally"""
        self.pos_x += self.move_speed * self.travel_direction

    def descend_and_reverse(self):
        """Drop down and change direction"""
        self.pos_y += INVADER_DROP_DISTANCE
        self.travel_direction *= -1

    def render_to_screen(self, display):
        """Draw the alien"""
        pygame.draw.rect(
            display, COLOR_GREEN, (self.pos_x, self.pos_y, self.width, self.height)
        )
        # Eyes
        pygame.draw.rect(display, COLOR_BLACK, (self.pos_x + 5, self.pos_y + 5, 5, 5))
        pygame.draw.rect(display, COLOR_BLACK, (self.pos_x + 20, self.pos_y + 5, 5, 5))

    def has_hit_edge(self):
        """Check if alien touched screen edge"""
        return self.pos_x <= 0 or self.pos_x >= WINDOW_WIDTH - self.width

    def get_bounds(self):
        """Return bounding box"""
        return (self.pos_x, self.pos_y, self.width, self.height)

    def get_bottom(self):
        """Return bottom y position"""
        return self.pos_y + self.height


class GameEngine:
    """Main game engine managing all game logic"""

    def __init__(self):
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Space Invaders")
        self.game_clock = pygame.time.Clock()
        self.display_font = pygame.font.Font(None, 34)
        self._setup_new_game()

    def _setup_new_game(self):
        """Initialize game entities"""
        self.defender = DefenderShip()
        self.missiles = []
        self.invaders = []
        self.score = 0
        self.is_game_over = False
        self.is_victory = False
        self._create_invader_formation()

    def _create_invader_formation(self):
        """Build grid of invaders"""
        rows = 4
        cols = 10
        for row_num in range(rows):
            for col_num in range(cols):
                x_position = 70 + col_num * 60
                y_position = 60 + row_num * 48
                invader = InvaderAlien(x_position, y_position)
                self.invaders.append(invader)

    def process_events(self):
        """Handle input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.is_game_over:
                    self._fire_missile()
                elif event.key == pygame.K_r and self.is_game_over:
                    self._setup_new_game()
                elif event.key == pygame.K_q and self.is_game_over:
                    return False

        return True

    def _fire_missile(self):
        """Create new missile from defender position"""
        gun_pos = self.defender.get_gun_position()
        new_missile = Missile(gun_pos)
        self.missiles.append(new_missile)

    def update_game(self):
        """Update all game entities"""
        if self.is_game_over:
            return

        self._handle_player_movement()
        self._update_missiles()
        self._update_invaders()
        self._check_collisions()
        self._check_game_conditions()

    def _handle_player_movement(self):
        """Process continuous keyboard input"""
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a]:
            self.defender.shift_left()
        if keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]:
            self.defender.shift_right()

    def _update_missiles(self):
        """Update all active missiles"""
        for missile in self.missiles[:]:
            missile.update_position()
            if missile.has_left_screen():
                self.missiles.remove(missile)

    def _update_invaders(self):
        """Update invader movement"""
        should_descend = False

        for invader in self.invaders:
            invader.update_position()
            if invader.has_hit_edge():
                should_descend = True

        if should_descend:
            # Fixed: use correct range or iterate directly over invaders list
            for invader in self.invaders:
                invader.descend_and_reverse()

    def _check_collisions(self):
        """Detect missile-invader collisions"""
        for missile in self.missiles[:]:
            missile_bounds = missile.get_bounds()
            for invader in self.invaders[:]:
                invader_bounds = invader.get_bounds()
                if self._bounds_overlap(missile_bounds, invader_bounds):
                    if missile in self.missiles:
                        self.missiles.remove(missile)
                    if invader in self.invaders:
                        self.invaders.remove(invader)
                    self.score += 10
                    break

    def _bounds_overlap(self, bounds1, bounds2):
        """Check if two bounding boxes overlap"""
        x1, y1, w1, h1 = bounds1
        x2, y2, w2, h2 = bounds2
        return x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2

    def _check_game_conditions(self):
        """Check win/lose conditions"""
        # Victory condition
        if not self.invaders:
            self.is_victory = True
            self.is_game_over = True
            return

        # Defeat condition
        for invader in self.invaders:
            if invader.get_bottom() >= self.defender.pos_y:
                self.is_game_over = True
                return

    def render(self):
        """Draw all visual elements"""
        self.display_surface.fill(COLOR_BLACK)

        if not self.is_game_over:
            self.defender.render_to_screen(self.display_surface)

            for missile in self.missiles:
                missile.render_to_screen(self.display_surface)

            for invader in self.invaders:
                invader.render_to_screen(self.display_surface)

        # Score display
        score_surface = self.display_font.render(
            f"Score: {self.score}", True, COLOR_GREEN
        )
        self.display_surface.blit(score_surface, (10, 10))

        # Game over overlay
        if self.is_game_over:
            if self.is_victory:
                message = "VICTORY!"
            else:
                message = "GAME OVER"

            message_surface = self.display_font.render(message, True, COLOR_GREEN)
            instruction_surface = self.display_font.render(
                "Press R to restart or Q to quit", True, COLOR_GREEN
            )

            message_rect = message_surface.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 28)
            )
            instruction_rect = instruction_surface.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 28)
            )

            self.display_surface.blit(message_surface, message_rect)
            self.display_surface.blit(instruction_surface, instruction_rect)

        pygame.display.flip()

    def execute(self):
        """Run main game loop"""
        is_running = True
        while is_running:
            is_running = self.process_events()
            self.update_game()
            self.render()
            self.game_clock.tick(60)

        pygame.quit()
        sys.exit()


def main():
    """Entry point"""
    engine = GameEngine()
    engine.execute()


if __name__ == "__main__":
    main()
