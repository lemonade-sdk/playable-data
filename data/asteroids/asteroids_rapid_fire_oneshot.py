# CREATE: asteroids where I can hold space to rapid fire

"""
Asteroids Rapid Fire Game

A space shooter where the player controls a ship to destroy asteroids with rapid-fire shooting.
Holding spacebar fires bullets continuously with a controlled rate timer. Implementation uses
pygame with vector-based movement, collision detection, and enhanced firing mechanics that
allow sustained bullet streams while maintaining game balance through fire rate limiting.
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
FPS = 60
FIRE_RATE = 8  # Frames between shots when holding spacebar


class Ship:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.vel_x = 0
        self.vel_y = 0
        self.size = 10
        self.fire_timer = 0  # Timer for controlling fire rate

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

        # Update fire timer
        if self.fire_timer > 0:
            self.fire_timer -= 1

    def thrust(self):
        # Add thrust in the direction the ship is facing
        thrust_power = 0.2
        self.vel_x += math.cos(math.radians(self.angle)) * thrust_power
        self.vel_y += math.sin(math.radians(self.angle)) * thrust_power

    def rotate(self, direction):
        self.angle += direction * 5

    def can_fire(self):
        # Check if ship can fire based on fire rate timer
        return self.fire_timer <= 0

    def fire(self):
        # Fire a bullet and reset fire timer
        if self.can_fire():
            self.fire_timer = FIRE_RATE
            return Bullet(self.x, self.y, self.angle)
        return None

    def draw(self, screen):
        # Calculate ship points (triangle)
        points = []
        for angle_offset in [0, 140, 220]:
            point_angle = math.radians(self.angle + angle_offset)
            point_x = self.x + math.cos(point_angle) * self.size
            point_y = self.y + math.sin(point_angle) * self.size
            points.append((point_x, point_y))

        pygame.draw.polygon(screen, GREEN, points)


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
    def __init__(self, x, y, size):
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
        # Draw asteroid using fixed shape points
        points = []
        for angle_offset, radius_variation in self.shape_points:
            angle = angle_offset + self.angle
            point_x = self.x + math.cos(math.radians(angle)) * radius_variation
            point_y = self.y + math.sin(math.radians(angle)) * radius_variation
            points.append((point_x, point_y))

        pygame.draw.polygon(screen, GREEN, points, 2)

    def split(self):
        # Return smaller asteroids when this one is destroyed
        if self.size > 1:
            new_asteroids = []
            for _ in range(2):
                new_asteroid = Asteroid(self.x, self.y, self.size - 1)
                new_asteroid.vel_x = random.uniform(-3, 3)
                new_asteroid.vel_y = random.uniform(-3, 3)
                new_asteroids.append(new_asteroid)
            return new_asteroids
        return []


def check_collision(obj1_x, obj1_y, obj1_radius, obj2_x, obj2_y, obj2_radius):
    distance = math.sqrt((obj1_x - obj2_x) ** 2 + (obj1_y - obj2_y) ** 2)
    return distance < (obj1_radius + obj2_radius)


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
    pygame.display.set_caption("Asteroids Rapid Fire Remix")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)

    # Game state
    game_over = False
    score = 0

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
                if event.key == pygame.K_r and game_over:
                    # Restart game
                    game_over = False
                    score = 0
                    ship = Ship(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                    bullets = []
                    asteroids = create_initial_asteroids()
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

            # Continuous firing when spacebar is held
            if keys[pygame.K_SPACE]:
                new_bullet = ship.fire()
                if new_bullet:
                    bullets.append(new_bullet)

            # Update game objects
            ship.update()

            # Update bullets
            bullets = [bullet for bullet in bullets if bullet.update()]

            # Update asteroids
            for asteroid in asteroids:
                asteroid.update()

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
