# CREATE: asteroids

"""
Asteroids Game

A space shooter game where the player controls a ship to destroy asteroids.
The ship can rotate, thrust forward, and shoot. Asteroids break into smaller
pieces when hit. Game uses object-oriented design with separate classes.
"""

import pygame
import math
import random

pygame.init()

# Screen settings
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700
BLACK = (0, 0, 0)
GREEN = (0, 255, 65)


class Ship:
    """Player's spaceship"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed_x = 0
        self.speed_y = 0
        self.rotation_speed = 4

    def draw(self, screen):
        # Draw ship as a diamond shape
        points = []
        angles = [0, 90, 180, 270]
        sizes = [15, 8, 15, 8]
        for i, angle_offset in enumerate(angles):
            angle_rad = math.radians(self.angle + angle_offset)
            px = self.x + math.cos(angle_rad) * sizes[i]
            py = self.y + math.sin(angle_rad) * sizes[i]
            points.append((px, py))
        pygame.draw.polygon(screen, GREEN, points, 2)

    def rotate(self, direction):
        self.angle += direction * self.rotation_speed

    def thrust(self):
        # Add velocity in the direction ship is facing
        rad = math.radians(self.angle)
        self.speed_x += math.cos(rad) * 0.25
        self.speed_y += math.sin(rad) * 0.25

    def update(self):
        # Apply friction
        self.speed_x *= 0.99
        self.speed_y *= 0.99

        # Update position
        self.x += self.speed_x
        self.y += self.speed_y

        # Wrap around screen
        if self.x < 0:
            self.x = SCREEN_WIDTH
        elif self.x > SCREEN_WIDTH:
            self.x = 0
        if self.y < 0:
            self.y = SCREEN_HEIGHT
        elif self.y > SCREEN_HEIGHT:
            self.y = 0


class Bullet:
    """Projectile fired by the ship"""

    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.speed = 10
        rad = math.radians(angle)
        self.speed_x = math.cos(rad) * self.speed
        self.speed_y = math.sin(rad) * self.speed
        self.lifetime = 40

    def draw(self, screen):
        pygame.draw.circle(screen, GREEN, (int(self.x), int(self.y)), 3)

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.lifetime -= 1

        # Wrap around screen
        if self.x < 0:
            self.x = SCREEN_WIDTH
        elif self.x > SCREEN_WIDTH:
            self.x = 0
        if self.y < 0:
            self.y = SCREEN_HEIGHT
        elif self.y > SCREEN_HEIGHT:
            self.y = 0


class Asteroid:
    """Space rock that the player must destroy"""

    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.radius = size * 18

        # Random velocity
        angle = random.uniform(0, 360)
        speed = random.uniform(0.8, 2.0)
        rad = math.radians(angle)
        self.speed_x = math.cos(rad) * speed
        self.speed_y = math.sin(rad) * speed

        # Create random shape points
        self.points = []
        num_points = 8
        for i in range(num_points):
            angle = (360 / num_points) * i
            variation = random.uniform(-5, 5)
            self.points.append((angle, self.radius + variation))

    def draw(self, screen):
        # Draw as irregular polygon
        shape_points = []
        for angle, radius in self.points:
            rad = math.radians(angle)
            px = self.x + math.cos(rad) * radius
            py = self.y + math.sin(rad) * radius
            shape_points.append((px, py))
        pygame.draw.polygon(screen, GREEN, shape_points, 2)

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y

        # Wrap around screen
        if self.x < 0:
            self.x = SCREEN_WIDTH
        elif self.x > SCREEN_WIDTH:
            self.x = 0
        if self.y < 0:
            self.y = SCREEN_HEIGHT
        elif self.y > SCREEN_HEIGHT:
            self.y = 0


def check_collision(x1, y1, r1, x2, y2, r2):
    """Check if two circular objects collide"""
    distance = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    return distance < r1 + r2


def spawn_asteroids(count):
    """Create initial asteroids away from center"""
    asteroids = []
    for _ in range(count):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        # Make sure not too close to center
        while (
            math.sqrt((x - SCREEN_WIDTH / 2) ** 2 + (y - SCREEN_HEIGHT / 2) ** 2) < 150
        ):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
        asteroids.append(Asteroid(x, y, 3))
    return asteroids


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Asteroids")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)

    # Game objects
    player = Ship(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    asteroids = spawn_asteroids(5)
    bullets = []
    score = 0
    game_over = False

    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    bullets.append(Bullet(player.x, player.y, player.angle))
                elif event.key == pygame.K_r and game_over:
                    player = Ship(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
                    asteroids = spawn_asteroids(5)
                    bullets = []
                    score = 0
                    game_over = False
                elif event.key == pygame.K_q and game_over:
                    running = False

        if not game_over:
            # Handle input
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                player.rotate(-1)
            if keys[pygame.K_RIGHT]:
                player.rotate(1)
            if keys[pygame.K_UP]:
                player.thrust()

            # Update everything
            player.update()

            for asteroid in asteroids:
                asteroid.update()

            for bullet in bullets:
                bullet.update()

            # Remove old bullets
            bullets = [b for b in bullets if b.lifetime > 0]

            # Check bullet-asteroid collisions
            for bullet in bullets[:]:
                for asteroid in asteroids[:]:
                    if check_collision(
                        bullet.x, bullet.y, 3, asteroid.x, asteroid.y, asteroid.radius
                    ):
                        if bullet in bullets:
                            bullets.remove(bullet)
                        if asteroid in asteroids:
                            asteroids.remove(asteroid)
                            # Add points based on size
                            score += asteroid.size * 20
                            # Split asteroid if large enough
                            if asteroid.size > 1:
                                for _ in range(2):
                                    asteroids.append(
                                        Asteroid(
                                            asteroid.x, asteroid.y, asteroid.size - 1
                                        )
                                    )
                        break

            # Check ship-asteroid collisions
            for asteroid in asteroids:
                if check_collision(
                    player.x, player.y, 12, asteroid.x, asteroid.y, asteroid.radius
                ):
                    game_over = True

            # New wave if all asteroids destroyed
            if len(asteroids) == 0:
                asteroids = spawn_asteroids(6)

        # Draw everything
        screen.fill(BLACK)

        if not game_over:
            player.draw(screen)
            for asteroid in asteroids:
                asteroid.draw(screen)
            for bullet in bullets:
                bullet.draw(screen)

            # Draw score
            score_text = font.render(f"Score: {score}", True, GREEN)
            screen.blit(score_text, (10, 10))
        else:
            # Game over screen
            game_over_text = font.render("GAME OVER", True, GREEN)
            final_score_text = font.render(f"Final Score: {score}", True, GREEN)
            restart_text = font.render("Press R to restart or Q to quit", True, GREEN)

            screen.blit(
                game_over_text, (SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2 - 60)
            )
            screen.blit(
                final_score_text, (SCREEN_WIDTH / 2 - 120, SCREEN_HEIGHT / 2 - 20)
            )
            screen.blit(restart_text, (SCREEN_WIDTH / 2 - 200, SCREEN_HEIGHT / 2 + 20))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
