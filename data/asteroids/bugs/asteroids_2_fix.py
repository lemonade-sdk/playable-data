# CREATE: asteroids

"""
Asteroids Game

Classic arcade game where you pilot a spaceship through an asteroid field.
Destroy asteroids by shooting them while avoiding collisions. Uses pygame
with object-oriented design for clean code organization.

BUG FIX: The variable was initialized with an inconsistent name in the main() function.
Find where the score variable is initialized and make sure it uses the same name ('current_score') that's referenced elsewhere in the code.
"""

import pygame
import random
import math

pygame.init()


class Spaceship:
    """The player's ship"""

    ROTATION_SPEED = 6
    THRUST_POWER = 0.2
    FRICTION = 0.98

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rotation = 0
        self.vel_x = 0
        self.vel_y = 0

    def apply_thrust(self):
        """Accelerate the ship forward"""
        angle = math.radians(self.rotation)
        self.vel_x += math.cos(angle) * self.THRUST_POWER
        self.vel_y += math.sin(angle) * self.THRUST_POWER

    def rotate_left(self):
        """Rotate ship counterclockwise"""
        self.rotation -= self.ROTATION_SPEED

    def rotate_right(self):
        """Rotate ship clockwise"""
        self.rotation += self.ROTATION_SPEED

    def update(self):
        """Update ship position and apply friction"""
        self.vel_x *= self.FRICTION
        self.vel_y *= self.FRICTION
        self.x += self.vel_x
        self.y += self.vel_y

        # Wrap around screen edges
        self.x = self.x % 600
        self.y = self.y % 600

    def draw(self, surface):
        """Draw the ship as a triangle"""
        angle = math.radians(self.rotation)
        # Front point
        p1_x = self.x + math.cos(angle) * 12
        p1_y = self.y + math.sin(angle) * 12
        # Back left
        p2_x = self.x + math.cos(angle + 2.5) * 12
        p2_y = self.y + math.sin(angle + 2.5) * 12
        # Back right
        p3_x = self.x + math.cos(angle - 2.5) * 12
        p3_y = self.y + math.sin(angle - 2.5) * 12

        points = [(p1_x, p1_y), (p2_x, p2_y), (p3_x, p3_y)]
        pygame.draw.polygon(surface, (0, 255, 65), points, 2)


class Projectile:
    """Bullets fired by the spaceship"""

    SPEED = 8
    MAX_LIFETIME = 50

    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        angle_rad = math.radians(angle)
        self.vel_x = math.cos(angle_rad) * self.SPEED
        self.vel_y = math.sin(angle_rad) * self.SPEED
        self.lifetime = 0

    def update(self):
        """Move the projectile"""
        self.x += self.vel_x
        self.y += self.vel_y
        self.lifetime += 1

        # Wrap around screen
        self.x = self.x % 600
        self.y = self.y % 600

    def is_expired(self):
        """Check if projectile should be removed"""
        return self.lifetime > self.MAX_LIFETIME

    def draw(self, surface):
        """Draw the projectile"""
        pygame.draw.circle(surface, (0, 255, 65), (int(self.x), int(self.y)), 2)


class SpaceRock:
    """Asteroids floating in space"""

    def __init__(self, x, y, level):
        self.x = x
        self.y = y
        self.level = level  # 3 = large, 2 = medium, 1 = small
        self.size = level * 16

        # Random movement
        direction = random.uniform(0, 360)
        speed = random.uniform(0.5, 1.5)
        self.vel_x = math.cos(math.radians(direction)) * speed
        self.vel_y = math.sin(math.radians(direction)) * speed

    def update(self):
        """Move the asteroid"""
        self.x += self.vel_x
        self.y += self.vel_y

        # Wrap around screen
        self.x = self.x % 600
        self.y = self.y % 600

    def draw(self, surface):
        """Draw the asteroid as a circle"""
        pygame.draw.circle(
            surface, (0, 255, 65), (int(self.x), int(self.y)), self.size, 2
        )

    def split(self):
        """Break into smaller asteroids"""
        if self.level > 1:
            return [
                SpaceRock(self.x, self.y, self.level - 1),
                SpaceRock(self.x, self.y, self.level - 1),
            ]
        return []


def distance_between(x1, y1, x2, y2):
    """Calculate distance between two points"""
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def create_asteroid_field():
    """Generate starting asteroids"""
    rocks = []
    for _ in range(4):
        x = random.randint(0, 600)
        y = random.randint(0, 600)
        # Don't spawn too close to center
        while distance_between(x, y, 300, 300) < 100:
            x = random.randint(0, 600)
            y = random.randint(0, 600)
        rocks.append(SpaceRock(x, y, 3))
    return rocks


def main():
    # Setup
    screen = pygame.display.set_mode((600, 600))
    pygame.display.set_caption("Asteroids")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 40)

    # Game state
    ship = Spaceship(300, 300)
    rocks = create_asteroid_field()
    projectiles = []
    current_score = 0  # FIXED: Changed from 'curren_score' to 'current_score'
    is_game_over = False

    # Main loop
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not is_game_over:
                    projectiles.append(Projectile(ship.x, ship.y, ship.rotation))
                elif event.key == pygame.K_r and is_game_over:
                    # Restart
                    ship = Spaceship(300, 300)
                    rocks = create_asteroid_field()
                    projectiles = []
                    current_score = 0  # FIXED: Changed from 'curren_score' to 'current_score'
                    is_game_over = False
                elif event.key == pygame.K_q and is_game_over:
                    running = False

        if not is_game_over:
            # Input
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                ship.rotate_left()
            if keys[pygame.K_RIGHT]:
                ship.rotate_right()
            if keys[pygame.K_UP]:
                ship.apply_thrust()

            # Update
            ship.update()

            for rock in rocks:
                rock.update()

            for proj in projectiles:
                proj.update()

            # Remove expired projectiles
            projectiles = [p for p in projectiles if not p.is_expired()]

            # Check collisions between projectiles and rocks
            for proj in projectiles[:]:
                for rock in rocks[:]:
                    if distance_between(proj.x, proj.y, rock.x, rock.y) < rock.size:
                        if proj in projectiles:
                            projectiles.remove(proj)
                        if rock in rocks:
                            rocks.remove(rock)
                            # Score more points for smaller asteroids
                            current_score += (4 - rock.level) * 15
                            # Add fragments
                            rocks.extend(rock.split())
                        break

            # Check collisions between ship and rocks
            for rock in rocks:
                if distance_between(ship.x, ship.y, rock.x, rock.y) < rock.size + 10:
                    is_game_over = True

            # Spawn new wave
            if not rocks:
                rocks = create_asteroid_field()

        # Render
        screen.fill((0, 0, 0))

        if not is_game_over:
            ship.draw(screen)
            for rock in rocks:
                rock.draw(screen)
            for proj in projectiles:
                proj.draw(screen)

            # Score display
            score_surface = font.render(f"Score: {current_score}", True, (0, 255, 65))
            screen.blit(score_surface, (10, 10))
        else:
            # Game over display
            over_text = font.render("GAME OVER", True, (0, 255, 65))
            score_text = font.render(f"Score: {current_score}", True, (0, 255, 65))
            instruction_text = font.render("R: Restart  Q: Quit", True, (0, 255, 65))

            screen.blit(over_text, (300 - 100, 300 - 60))
            screen.blit(score_text, (300 - 80, 300 - 10))
            screen.blit(instruction_text, (300 - 120, 300 + 40))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
