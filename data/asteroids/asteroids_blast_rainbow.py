# SOURCE: asteroids_blast.py
# REMIX: use rainbow colors

"""
Asteroids Blast Rainbow - A remix combining blast ability and rainbow visual effects.
Press Enter to destroy all asteroids within 150 pixels of your ship with a spectacular blast!
Asteroids display vibrant rainbow colors that change when they split, creating a colorful space battle.

This remix combines features from asteroids_blast.py and asteroids_rainbow.py,
creating visually stunning gameplay with powerful area-of-effect destruction.

Implementation uses pygame with vector-based movement and collision detection.
"""

import pygame
import math
import random

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLACK = (0, 0, 0)
GREEN = (0, 255, 65)
WHITE = (255, 255, 255)
BLAST_RADIUS = 150
FPS = 60

# Rainbow color palette
RAINBOW_COLORS = [
    (255, 0, 0),  # Red
    (255, 127, 0),  # Orange
    (255, 255, 0),  # Yellow
    (127, 255, 0),  # Yellow-Green
    (0, 255, 0),  # Green
    (0, 255, 127),  # Green-Cyan
    (0, 255, 255),  # Cyan
    (0, 127, 255),  # Blue-Cyan
    (0, 0, 255),  # Blue
    (127, 0, 255),  # Blue-Magenta
    (255, 0, 255),  # Magenta
    (255, 0, 127),  # Red-Magenta
]


class Ship:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.vel_x = 0
        self.vel_y = 0
        self.size = 10
        self.blast_cooldown = 0  # Cooldown timer in frames
        self.blast_ready = True

    def update(self):
        # Apply movement
        self.x += self.vel_x
        self.y += self.vel_y

        # Wrap around screen edges
        self.x %= SCREEN_WIDTH
        self.y %= SCREEN_HEIGHT

        # Apply friction
        self.vel_x *= 0.98
        self.vel_y *= 0.98

        # Update blast cooldown
        if self.blast_cooldown > 0:
            self.blast_cooldown -= 1
            self.blast_ready = False
        else:
            self.blast_ready = True

    def thrust(self):
        # Add thrust in the direction the ship is facing
        thrust_power = 0.2
        self.vel_x += math.cos(math.radians(self.angle)) * thrust_power
        self.vel_y += math.sin(math.radians(self.angle)) * thrust_power

    def rotate(self, direction):
        self.angle += direction * 5

    def draw(self, screen):
        # Calculate ship points (triangle)
        points = []
        for angle_offset in [0, 140, 220]:
            point_angle = math.radians(self.angle + angle_offset)
            point_x = self.x + math.cos(point_angle) * self.size
            point_y = self.y + math.sin(point_angle) * self.size
            points.append((point_x, point_y))

        # Color ship based on blast availability
        ship_color = GREEN if self.blast_ready else WHITE
        pygame.draw.polygon(screen, ship_color, points)

    def use_blast(self):
        # Trigger blast and start cooldown
        if self.blast_ready:
            self.blast_cooldown = 5 * FPS  # 5 seconds at 60 FPS
            self.blast_ready = False
            return True
        return False


class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        speed = 10
        self.vel_x = math.cos(math.radians(angle)) * speed
        self.vel_y = math.sin(math.radians(angle)) * speed
        self.lifetime = 60  # Bullets disappear after 1 second at 60 FPS

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.lifetime -= 1

        # Wrap around screen edges
        self.x %= SCREEN_WIDTH
        self.y %= SCREEN_HEIGHT

        return self.lifetime > 0

    def draw(self, screen):
        pygame.draw.circle(screen, GREEN, (int(self.x), int(self.y)), 2)


class Asteroid:
    def __init__(self, x, y, size, color_index=None):
        self.x = x
        self.y = y
        self.size = size  # 3=large, 2=medium, 1=small
        self.radius = size * 15
        self.vel_x = random.uniform(-1.5, 1.5)
        self.vel_y = random.uniform(-1.5, 1.5)
        self.angle = 0
        self.rotation_speed = random.uniform(-2, 2)
        # Generate fixed shape points to prevent wobbling
        self.shape_points = self._generate_shape()
        self.color_index = (
            color_index
            if color_index is not None
            else random.randint(0, len(RAINBOW_COLORS) - 1)
        )

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.angle += self.rotation_speed

        # Wrap around screen edges
        self.x %= SCREEN_WIDTH
        self.y %= SCREEN_HEIGHT

    def _generate_shape(self):
        # Generate fixed shape points to prevent wobbling
        points = []
        num_points = 8
        for i in range(num_points):
            angle = (360 / num_points) * i
            # Add some randomness but keep it fixed per asteroid
            radius_variation = self.radius + random.uniform(-8, 8)
            points.append((angle, radius_variation))
        return points

    def draw(self, screen):
        # Draw asteroid using fixed shape points with rainbow color
        points = []
        for angle_offset, radius_variation in self.shape_points:
            angle = angle_offset + self.angle
            point_x = self.x + math.cos(math.radians(angle)) * radius_variation
            point_y = self.y + math.sin(math.radians(angle)) * radius_variation
            points.append((point_x, point_y))

        color = RAINBOW_COLORS[self.color_index]
        pygame.draw.polygon(screen, color, points, 2)

    def split(self):
        # Return smaller asteroids when this one is destroyed
        if self.size > 1:
            new_asteroids = []
            for _ in range(2):
                # Change color when splitting
                new_color_index = (self.color_index + random.randint(1, 3)) % len(
                    RAINBOW_COLORS
                )
                new_asteroid = Asteroid(self.x, self.y, self.size - 1, new_color_index)
                new_asteroid.vel_x = random.uniform(-3, 3)
                new_asteroid.vel_y = random.uniform(-3, 3)
                new_asteroids.append(new_asteroid)
            return new_asteroids
        return []


class BlastEffect:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 0
        self.max_radius = BLAST_RADIUS
        self.duration = 20  # frames
        self.current_frame = 0

    def update(self):
        self.current_frame += 1
        # Expand blast radius over time
        self.radius = (self.current_frame / self.duration) * self.max_radius
        return self.current_frame < self.duration

    def draw(self, screen):
        # Draw expanding blast circle with rainbow colors
        alpha = 255 - (self.current_frame / self.duration) * 255
        if self.radius > 0:
            # Draw multiple circles for a more dramatic effect with rainbow colors
            for i in range(3):
                radius = max(1, int(self.radius - i * 10))
                color_intensity = max(50, int(alpha - i * 50))
                # Cycle through rainbow colors based on frame and circle layer
                color_index = (self.current_frame + i * 2) % len(RAINBOW_COLORS)
                base_color = RAINBOW_COLORS[color_index]
                # Apply intensity to the rainbow color
                color = tuple(
                    min(255, int(c * color_intensity / 255)) for c in base_color
                )
                pygame.draw.circle(screen, color, (int(self.x), int(self.y)), radius, 2)


def check_collision(obj1_x, obj1_y, obj1_radius, obj2_x, obj2_y, obj2_radius):
    distance = math.sqrt((obj1_x - obj2_x) ** 2 + (obj1_y - obj2_y) ** 2)
    return distance < (obj1_radius + obj2_radius)


def check_blast_collision(ship_x, ship_y, asteroid_x, asteroid_y):
    # Check if asteroid is within blast radius of ship
    distance = math.sqrt((ship_x - asteroid_x) ** 2 + (ship_y - asteroid_y) ** 2)
    return distance <= BLAST_RADIUS


def create_initial_asteroids():
    asteroids = []
    for _ in range(5):
        # Spawn asteroids away from the center where the ship starts
        while True:
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            # Make sure asteroid doesn't spawn too close to ship
            if (
                math.sqrt((x - SCREEN_WIDTH // 2) ** 2 + (y - SCREEN_HEIGHT // 2) ** 2)
                > 100
            ):
                asteroids.append(Asteroid(x, y, 3))
                break
    return asteroids


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Asteroids Blast Rainbow Remix")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)

    # Game state
    game_over = False
    score = 0
    blast_effects = []

    # Initialize game objects
    ship = Ship(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    bullets = []
    asteroids = create_initial_asteroids()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    # Shoot bullet
                    bullets.append(Bullet(ship.x, ship.y, ship.angle))
                elif event.key == pygame.K_RETURN and not game_over:
                    # Blast ability - destroy asteroids within radius (if ready)
                    if ship.use_blast():
                        blast_effects.append(BlastEffect(ship.x, ship.y))
                        asteroids_to_remove = []
                        new_asteroids = []

                        for asteroid in asteroids:
                            if check_blast_collision(
                                ship.x, ship.y, asteroid.x, asteroid.y
                            ):
                                asteroids_to_remove.append(asteroid)
                                score += (4 - asteroid.size) * 10
                                # Split asteroids caught in blast
                                split_asteroids = asteroid.split()
                                new_asteroids.extend(split_asteroids)

                        # Remove blasted asteroids and add split pieces
                        for asteroid in asteroids_to_remove:
                            asteroids.remove(asteroid)
                        asteroids.extend(new_asteroids)

                elif event.key == pygame.K_r and game_over:
                    # Restart game
                    game_over = False
                    score = 0
                    ship = Ship(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                    bullets = []
                    asteroids = create_initial_asteroids()
                    blast_effects = []
                elif event.key == pygame.K_q and game_over:
                    running = False

        if not game_over:
            # Handle continuous key presses
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                ship.rotate(-1)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                ship.rotate(1)
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                ship.thrust()

            # Update game objects
            ship.update()

            # Update bullets
            bullets = [bullet for bullet in bullets if bullet.update()]

            # Update asteroids
            for asteroid in asteroids:
                asteroid.update()

            # Update blast effects
            blast_effects = [effect for effect in blast_effects if effect.update()]

            # Check bullet-asteroid collisions
            for bullet in bullets[:]:
                for asteroid in asteroids[:]:
                    if check_collision(
                        bullet.x, bullet.y, 2, asteroid.x, asteroid.y, asteroid.radius
                    ):
                        bullets.remove(bullet)
                        asteroids.remove(asteroid)
                        score += (
                            4 - asteroid.size
                        ) * 10  # Smaller asteroids worth more points

                        # Split asteroid
                        new_asteroids = asteroid.split()
                        asteroids.extend(new_asteroids)
                        break

            # Check ship-asteroid collisions
            for asteroid in asteroids:
                if check_collision(
                    ship.x, ship.y, ship.size, asteroid.x, asteroid.y, asteroid.radius
                ):
                    game_over = True
                    break

            # Check win condition
            if not asteroids:
                # Spawn new wave with more asteroids
                asteroids = create_initial_asteroids()
                for _ in range(2):  # Add 2 more asteroids each wave
                    x = random.randint(0, SCREEN_WIDTH)
                    y = random.randint(0, SCREEN_HEIGHT)
                    asteroids.append(Asteroid(x, y, 3))

        # Draw everything
        screen.fill(BLACK)

        if not game_over:
            ship.draw(screen)
            for bullet in bullets:
                bullet.draw(screen)
            for asteroid in asteroids:
                asteroid.draw(screen)

            # Draw blast effects
            for effect in blast_effects:
                effect.draw(screen)

            # Draw score
            score_text = font.render(f"Score: {score}", True, GREEN)
            screen.blit(score_text, (10, 10))
        else:
            # Game over screen
            game_over_text = font.render("GAME OVER", True, GREEN)
            score_text = font.render(f"Final Score: {score}", True, GREEN)
            restart_text = font.render("Press R to restart or Q to quit", True, GREEN)

            screen.blit(
                game_over_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 60)
            )
            screen.blit(score_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 20))
            screen.blit(
                restart_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 20)
            )

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
