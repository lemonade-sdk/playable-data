# CREATE: asteroids where I can ram the asteroids and hold space to rapid fire

"""
Asteroids Ramming Rapid Game

A space shooter where the player controls a ship to destroy asteroids by both ramming
into them and rapid-fire shooting. The ship can destroy asteroids through direct contact
while staying within screen boundaries, and holding spacebar fires bullets continuously
with a controlled rate timer. Implementation uses pygame with vector-based movement,
inverted collision mechanics, rapid-fire bullet systems, and boundary collision detection.
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
RED = (255, 0, 0)
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
        # Rotate the ship
        self.angle += direction * 5

    def can_fire(self):
        return self.fire_timer <= 0

    def fire(self):
        if self.can_fire():
            self.fire_timer = FIRE_RATE
            return True
        return False

    def is_out_of_bounds(self):
        """Check if ship is outside screen boundaries"""
        return (
            self.x < 0 or self.x > SCREEN_WIDTH or self.y < 0 or self.y > SCREEN_HEIGHT
        )

    def draw(self, screen):
        # Calculate ship points
        points = []
        ship_points = [(-10, -5), (15, 0), (-10, 5), (-5, 0)]

        for px, py in ship_points:
            # Rotate point
            rotated_x = px * math.cos(math.radians(self.angle)) - py * math.sin(
                math.radians(self.angle)
            )
            rotated_y = px * math.sin(math.radians(self.angle)) + py * math.cos(
                math.radians(self.angle)
            )
            points.append((self.x + rotated_x, self.y + rotated_y))

        pygame.draw.polygon(screen, GREEN, points)


class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.vel_x = math.cos(math.radians(angle)) * 8
        self.vel_y = math.sin(math.radians(angle)) * 8
        self.size = 2

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y

    def is_off_screen(self):
        return (
            self.x < 0 or self.x > SCREEN_WIDTH or self.y < 0 or self.y > SCREEN_HEIGHT
        )

    def draw(self, screen):
        pygame.draw.circle(screen, GREEN, (int(self.x), int(self.y)), self.size)


class Asteroid:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.vel_x = random.uniform(-2, 2)
        self.vel_y = random.uniform(-2, 2)
        self.angle = 0
        self.rotation_speed = random.uniform(-5, 5)

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.angle += self.rotation_speed

        # Wrap around screen edges
        self.x %= SCREEN_WIDTH
        self.y %= SCREEN_HEIGHT

    def split(self):
        # Return smaller asteroids when this one is destroyed
        if self.size > 20:
            new_asteroids = []
            for _ in range(2):
                new_asteroid = Asteroid(self.x, self.y, self.size // 2)
                new_asteroid.vel_x = random.uniform(-3, 3)
                new_asteroid.vel_y = random.uniform(-3, 3)
                new_asteroids.append(new_asteroid)
            return new_asteroids
        return []

    def draw(self, screen):
        # Draw asteroid as a polygon
        points = []
        num_points = 8
        for i in range(num_points):
            angle = (360 / num_points) * i + self.angle
            radius = self.size + random.uniform(-3, 3)
            px = self.x + math.cos(math.radians(angle)) * radius
            py = self.y + math.sin(math.radians(angle)) * radius
            points.append((px, py))

        pygame.draw.polygon(screen, GREEN, points, 2)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Asteroids - Ramming Rapid")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)

        self.ship = Ship(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.bullets = []
        self.asteroids = []
        self.score = 0
        self.game_over = False

        # Create initial asteroids
        for _ in range(5):
            while True:
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT)
                # Make sure asteroid doesn't spawn too close to ship
                if math.sqrt((x - self.ship.x) ** 2 + (y - self.ship.y) ** 2) > 100:
                    self.asteroids.append(Asteroid(x, y, 40))
                    break

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_r:
                        self.__init__()  # Restart game
                    elif event.key == pygame.K_q:
                        return False
        return True

    def update(self):
        if not self.game_over:
            keys = pygame.key.get_pressed()

            # Ship controls
            if keys[pygame.K_LEFT]:
                self.ship.rotate(-1)
            if keys[pygame.K_RIGHT]:
                self.ship.rotate(1)
            if keys[pygame.K_UP]:
                self.ship.thrust()
            if keys[pygame.K_SPACE]:
                if self.ship.fire():
                    bullet = Bullet(self.ship.x, self.ship.y, self.ship.angle)
                    self.bullets.append(bullet)

            self.ship.update()

            # Check if ship is out of bounds (ramming mechanic)
            if self.ship.is_out_of_bounds():
                self.game_over = True

            # Update bullets
            self.bullets = [
                bullet for bullet in self.bullets if not bullet.is_off_screen()
            ]
            for bullet in self.bullets:
                bullet.update()

            # Update asteroids
            for asteroid in self.asteroids:
                asteroid.update()

            # Check ship-asteroid collisions (ramming destroys asteroids)
            asteroids_to_remove = []
            for i, asteroid in enumerate(self.asteroids):
                ship_dist = math.sqrt(
                    (self.ship.x - asteroid.x) ** 2 + (self.ship.y - asteroid.y) ** 2
                )
                if ship_dist < self.ship.size + asteroid.size:
                    asteroids_to_remove.append(i)
                    self.score += 50  # Bonus points for ramming
                    # Split asteroid
                    new_asteroids = asteroid.split()
                    self.asteroids.extend(new_asteroids)

            # Remove rammed asteroids
            for i in reversed(asteroids_to_remove):
                del self.asteroids[i]

            # Check bullet-asteroid collisions
            bullets_to_remove = []
            asteroids_to_remove = []

            for i, bullet in enumerate(self.bullets):
                for j, asteroid in enumerate(self.asteroids):
                    bullet_dist = math.sqrt(
                        (bullet.x - asteroid.x) ** 2 + (bullet.y - asteroid.y) ** 2
                    )
                    if bullet_dist < bullet.size + asteroid.size:
                        bullets_to_remove.append(i)
                        asteroids_to_remove.append(j)
                        self.score += 10
                        # Split asteroid
                        new_asteroids = asteroid.split()
                        self.asteroids.extend(new_asteroids)
                        break

            # Remove hit bullets and asteroids
            for i in reversed(sorted(set(bullets_to_remove))):
                if i < len(self.bullets):
                    del self.bullets[i]
            for i in reversed(sorted(set(asteroids_to_remove))):
                if i < len(self.asteroids):
                    del self.asteroids[i]

            # Check win condition
            if not self.asteroids:
                # Spawn new wave
                for _ in range(5):
                    while True:
                        x = random.randint(0, SCREEN_WIDTH)
                        y = random.randint(0, SCREEN_HEIGHT)
                        if (
                            math.sqrt((x - self.ship.x) ** 2 + (y - self.ship.y) ** 2)
                            > 100
                        ):
                            self.asteroids.append(Asteroid(x, y, 40))
                            break

    def draw(self):
        self.screen.fill(BLACK)

        if not self.game_over:
            # Draw game objects
            self.ship.draw(self.screen)
            for bullet in self.bullets:
                bullet.draw(self.screen)
            for asteroid in self.asteroids:
                asteroid.draw(self.screen)

        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, GREEN)
        self.screen.blit(score_text, (10, 10))

        # Draw game over screen
        if self.game_over:
            game_over_text = self.font.render("GAME OVER!", True, RED)
            restart_text = self.font.render(
                "Press R to restart or Q to quit", True, GREEN
            )

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
            self.clock.tick(FPS)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
