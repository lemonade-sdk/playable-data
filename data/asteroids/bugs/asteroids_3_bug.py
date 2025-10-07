# CREATE: asteroids
# ERROR: Traceback (most recent call last):
# ERROR:   File "C:\work\lsdk\playable-data\data\asteroids\bugs\asteroids_3_bug.py", line 328, in <module>
# ERROR:     main()
# ERROR:   File "C:\work\lsdk\playable-data\data\asteroids\bugs\asteroids_3_bug.py", line 288, in main
# ERROR:     player.x, player.y, 12, asteroid.x, asteroid.y, asteroid.size
# ERROR:                                                     ^^^^^^^^^^^^^
# ERROR: AttributeError: 'Asteroid' object has no attribute 'size'

"""
Asteroids Game

Space shooter game where you control a ship and destroy asteroids. Avoid
getting hit while clearing waves of asteroids. Built with pygame using
classes for game objects and collision detection.
"""

import pygame
import math
import random

# Initialize pygame
pygame.init()

# Constants
WIDTH = 800
HEIGHT = 600
BLACK = (0, 0, 0)
GREEN = (0, 255, 65)
FPS = 60


class PlayerShip:
    """Player controlled spaceship"""

    def __init__(self):
        self.x = WIDTH / 2
        self.y = HEIGHT / 2
        self.angle = 0
        self.velocity_x = 0
        self.velocity_y = 0
        self.shoot_cooldown = 0

    def draw(self, screen):
        # Triangle shape for ship
        points = []
        for offset in [0, 130, 230]:
            a = math.radians(self.angle + offset)
            size = 13
            px = self.x + math.cos(a) * size
            py = self.y + math.sin(a) * size
            points.append((px, py))
        pygame.draw.polygon(screen, GREEN, points, 2)

    def turn(self, direction):
        # Rotate the ship
        self.angle += direction * 5

    def move_forward(self):
        # Add thrust in facing direction
        a = math.radians(self.angle)
        self.velocity_x += math.cos(a) * 0.15
        self.velocity_y += math.sin(a) * 0.15

    def update(self):
        # Apply velocity
        self.x += self.velocity_x
        self.y += self.velocity_y

        # Friction
        self.velocity_x *= 0.99
        self.velocity_y *= 0.99

        # Keep on screen
        if self.x < 0:
            self.x = WIDTH
        if self.x > WIDTH:
            self.x = 0
        if self.y < 0:
            self.y = HEIGHT
        if self.y > HEIGHT:
            self.y = 0

        # Update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def shoot(self):
        """Create a bullet at ship position if cooldown is ready"""
        if self.shoot_cooldown == 0:
            self.shoot_cooldown = 10  # 10 frames between shots
            return Bullet(self.x, self.y, self.angle)
        return None


class Bullet:
    """Projectile shot from the ship"""

    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 9
        a = math.radians(angle)
        self.velocity_x = math.cos(a) * self.speed
        self.velocity_y = math.sin(a) * self.speed
        self.age = 0
        self.max_age = 45

    def draw(self, screen):
        pygame.draw.circle(screen, GREEN, (int(self.x), int(self.y)), 3)

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.age += 1

        # Keep on screen
        if self.x < 0:
            self.x = WIDTH
        if self.x > WIDTH:
            self.x = 0
        if self.y < 0:
            self.y = HEIGHT
        if self.y > HEIGHT:
            self.y = 0

    def is_dead(self):
        return self.age >= self.max_age


class Asteroid:
    """Space rock obstacle"""

    def __init__(self, x, y, tier):
        self.x = x
        self.y = y
        self.tier = tier
        self.radius = tier * 17

        # Random velocity
        angle = random.randrange(0, 360)
        vel = random.uniform(0.6, 1.8)
        a = math.radians(angle)
        self.velocity_x = math.cos(a) * vel
        self.velocity_y = math.sin(a) * vel

        # Generate shape
        self.shape = []
        segments = 9
        for i in range(segments):
            angle = (360 / segments) * i
            offset = random.randint(-6, 6)
            self.shape.append((angle, self.radius + offset))

    def draw(self, screen):
        # Draw irregular polygon
        points = []
        for angle, dist in self.shape:
            a = math.radians(angle)
            x = self.x + math.cos(a) * dist
            y = self.y + math.sin(a) * dist
            points.append((x, y))
        if len(points) > 2:
            pygame.draw.polygon(screen, GREEN, points, 2)

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y

        # Keep on screen
        if self.x < 0:
            self.x = WIDTH
        if self.x > WIDTH:
            self.x = 0
        if self.y < 0:
            self.y = HEIGHT
        if self.y > HEIGHT:
            self.y = 0

    def break_apart(self):
        """Split into smaller asteroids"""
        pieces = []
        if self.tier > 1:
            pieces.append(Asteroid(self.x, self.y, self.tier - 1))
            pieces.append(Asteroid(self.x, self.y, self.tier - 1))
        return pieces


def collision_check(x1, y1, r1, x2, y2, r2):
    """Check if two circles overlap"""
    dx = x1 - x2
    dy = y1 - y2
    dist = math.sqrt(dx * dx + dy * dy)
    return dist < (r1 + r2)


def spawn_wave(num):
    """Create asteroids for new wave"""
    wave = []
    for i in range(num):
        # Random position
        x = random.randrange(0, WIDTH)
        y = random.randrange(0, HEIGHT)
        # Make sure not near center
        cx = WIDTH / 2
        cy = HEIGHT / 2
        while math.sqrt((x - cx) ** 2 + (y - cy) ** 2) < 130:
            x = random.randrange(0, WIDTH)
            y = random.randrange(0, HEIGHT)
        wave.append(Asteroid(x, y, 3))
    return wave


def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Asteroids")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)

    # Initialize game objects
    player = PlayerShip()
    asteroids = spawn_wave(3)
    bullets = []
    points = 0
    game_active = True

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and not game_active:
                    # Restart game
                    player = PlayerShip()
                    asteroids = spawn_wave(3)
                    bullets = []
                    points = 0
                    game_active = True
                if event.key == pygame.K_q and not game_active:
                    running = False

        if game_active:
            # Get keyboard input
            keys = pygame.key.get_pressed()

            if keys[pygame.K_LEFT]:
                player.turn(-1)
            if keys[pygame.K_RIGHT]:
                player.turn(1)
            if keys[pygame.K_UP]:
                player.move_forward()
            if keys[pygame.K_SPACE]:
                # Continuous fire with cooldown
                bullet = player.shoot()
                if bullet:
                    bullets.append(bullet)

            # Update all objects
            player.update()

            for asteroid in asteroids:
                asteroid.update()

            for bullet in bullets:
                bullet.update()

            # Remove old bullets
            bullets = [b for b in bullets if not b.is_dead()]

            # Check bullet hits
            for bullet in bullets[:]:
                for asteroid in asteroids[:]:
                    if collision_check(
                        bullet.x, bullet.y, 3, asteroid.x, asteroid.y, asteroid.radius
                    ):
                        # Remove both
                        if bullet in bullets:
                            bullets.remove(bullet)
                        if asteroid in asteroids:
                            asteroids.remove(asteroid)
                            # Add score (smaller = more points)
                            points += (4 - asteroid.tier) * 25
                            # Break asteroid
                            for piece in asteroid.break_apart():
                                asteroids.append(piece)
                        break

            # Check ship collision
            for asteroid in asteroids:
                if collision_check(
                    player.x, player.y, 12, asteroid.x, asteroid.y, asteroid.size
                ):
                    game_active = False

            # Check for wave clear
            if not asteroids:
                asteroids = spawn_wave(4)

        # Drawing
        screen.fill(BLACK)

        if game_active:
            player.draw(screen)

            for asteroid in asteroids:
                asteroid.draw(screen)

            for bullet in bullets:
                bullet.draw(screen)

            # Show score
            score_label = font.render(f"Score: {points}", True, GREEN)
            screen.blit(score_label, (10, 10))
        else:
            # Game over screen
            game_over_label = font.render("GAME OVER", True, GREEN)
            score_label = font.render(f"Final Score: {points}", True, GREEN)
            restart_label = font.render("Press R to restart or Q to quit", True, GREEN)

            screen.blit(game_over_label, (WIDTH / 2 - 100, HEIGHT / 2 - 60))
            screen.blit(score_label, (WIDTH / 2 - 110, HEIGHT / 2 - 20))
            screen.blit(restart_label, (WIDTH / 2 - 200, HEIGHT / 2 + 20))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
