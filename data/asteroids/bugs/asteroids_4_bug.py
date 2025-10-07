# CREATE: asteroids
# ERROR: Traceback (most recent call last):
# ERROR:   File "C:\work\lsdk\playable-data\data\asteroids\bugs\asteroids_4_bug.py", line 264, in <module>
# ERROR:     main()
# ERROR:   File "C:\work\lsdk\playable-data\data\asteroids\bugs\asteroids_4_bug.py", line 242, in main
# ERROR:     "Score: " + player_score, True, (0, 255, 65)
# ERROR: TypeError: can only concatenate str (not "int") to str

"""
Asteroids Game

A pygame implementation of the classic Asteroids arcade game. Player controls
a triangular ship that can rotate and thrust. Shoot asteroids to break them
into smaller pieces. Avoid collisions with asteroids to survive.
"""

import pygame
import math
import random

pygame.init()


class Ship:
    """Represents the player's ship"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.heading = 0
        self.dx = 0
        self.dy = 0

    def update(self):
        """Update ship position based on velocity"""
        self.x = self.x + self.dx
        self.y = self.y + self.dy
        self.dx = self.dx * 0.97
        self.dy = self.dy * 0.97

        if self.x > 800:
            self.x = 0
        elif self.x < 0:
            self.x = 800
        if self.y > 600:
            self.y = 0
        elif self.y < 0:
            self.y = 600

    def rotate(self, amount):
        """Rotate ship by given amount"""
        self.heading = self.heading + amount

    def accelerate(self):
        """Apply thrust in current heading direction"""
        radians = math.radians(self.heading)
        self.dx = self.dx + math.cos(radians) * 0.22
        self.dy = self.dy + math.sin(radians) * 0.22

    def render(self, surface):
        """Draw the ship on screen"""
        point_list = []
        for angle in [0, 150, 210]:
            rad = math.radians(self.heading + angle)
            dist = 11
            point_x = self.x + math.cos(rad) * dist
            point_y = self.y + math.sin(rad) * dist
            point_list.append((point_x, point_y))
        pygame.draw.polygon(surface, (0, 255, 65), point_list, 2)


class Shot:
    """Represents a bullet fired from the ship"""

    def __init__(self, x, y, heading):
        self.x = x
        self.y = y
        radians = math.radians(heading)
        velocity = 7
        self.dx = math.cos(radians) * velocity
        self.dy = math.sin(radians) * velocity
        self.life = 60

    def update(self):
        """Update bullet position"""
        self.x = self.x + self.dx
        self.y = self.y + self.dy
        self.life = self.life - 1

        if self.x > 800:
            self.x = 0
        elif self.x < 0:
            self.x = 800
        if self.y > 600:
            self.y = 0
        elif self.y < 0:
            self.y = 600

    def render(self, surface):
        """Draw bullet on screen"""
        pygame.draw.circle(surface, (0, 255, 65), (int(self.x), int(self.y)), 2)

    def alive(self):
        """Check if bullet is still active"""
        return self.life > 0


class Rock:
    """Represents an asteroid"""

    def __init__(self, x, y, size_level):
        self.x = x
        self.y = y
        self.size_level = size_level
        self.hit_radius = size_level * 19
        movement_angle = random.randint(0, 359)
        movement_speed = random.uniform(0.7, 1.6)
        rad = math.radians(movement_angle)
        self.dx = math.cos(rad) * movement_speed
        self.dy = math.sin(rad) * movement_speed

    def update(self):
        """Update asteroid position"""
        self.x = self.x + self.dx
        self.y = self.y + self.dy

        if self.x > 800:
            self.x = 0
        elif self.x < 0:
            self.x = 800
        if self.y > 600:
            self.y = 0
        elif self.y < 0:
            self.y = 600

    def render(self, surface):
        """Draw asteroid on screen"""
        pygame.draw.circle(
            surface, (0, 255, 65), (int(self.x), int(self.y)), self.hit_radius, 2
        )

    def destroy(self):
        """Break asteroid into smaller pieces"""
        fragments = []
        if self.size_level > 1:
            new_size = self.size_level - 1
            fragments.append(Rock(self.x, self.y, new_size))
            fragments.append(Rock(self.x, self.y, new_size))
        return fragments


def calculate_distance(x1, y1, x2, y2):
    """Get distance between two points"""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def make_asteroid_field(count):
    """Create initial asteroids"""
    field = []
    for _ in range(count):
        pos_x = random.randint(0, 800)
        pos_y = random.randint(0, 600)
        while calculate_distance(pos_x, pos_y, 400, 300) < 120:
            pos_x = random.randint(0, 800)
            pos_y = random.randint(0, 600)
        field.append(Rock(pos_x, pos_y, 3))
    return field


def main():
    display = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Asteroids")
    timer = pygame.time.Clock()
    text_font = pygame.font.Font(None, 36)

    ship = Ship(400, 300)
    rocks = make_asteroid_field(5)
    shots = []
    player_score = 0
    alive = True

    keep_running = True
    while keep_running:
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                keep_running = False
            if evt.type == pygame.KEYDOWN:
                if evt.key == pygame.K_SPACE and alive:
                    shots.append(Shot(ship.x, ship.y, ship.heading))
                if not alive:
                    if evt.key == pygame.K_r:
                        ship = Ship(400, 300)
                        rocks = make_asteroid_field(5)
                        shots = []
                        player_score = 0
                        alive = True
                    elif evt.key == pygame.K_q:
                        keep_running = False

        if alive:
            pressed_keys = pygame.key.get_pressed()
            if pressed_keys[pygame.K_LEFT]:
                ship.rotate(-5)
            if pressed_keys[pygame.K_RIGHT]:
                ship.rotate(5)
            if pressed_keys[pygame.K_UP]:
                ship.accelerate()

            ship.update()
            for rock in rocks:
                rock.update()
            for shot in shots:
                shot.update()

            shots = [s for s in shots if s.alive()]

            for shot in shots[:]:
                for rock in rocks[:]:
                    dist = calculate_distance(shot.x, shot.y, rock.x, rock.y)
                    if dist < rock.hit_radius:
                        if shot in shots:
                            shots.remove(shot)
                        if rock in rocks:
                            rocks.remove(rock)
                            player_score = player_score + rock.size_level * 10
                            for fragment in rock.destroy():
                                rocks.append(fragment)
                        break

            for rock in rocks:
                dist = calculate_distance(ship.x, ship.y, rock.x, rock.y)
                if dist < rock.hit_radius + 11:
                    alive = False

            if len(rocks) == 0:
                rocks = make_asteroid_field(6)

        display.fill((0, 0, 0))

        if alive:
            ship.render(display)
            for rock in rocks:
                rock.render(display)
            for shot in shots:
                shot.render(display)
            score_display = text_font.render(
                "Score: " + player_score, True, (0, 255, 65)
            )
            display.blit(score_display, (10, 10))
        else:
            over_msg = text_font.render("GAME OVER", True, (0, 255, 65))
            score_msg = text_font.render(
                f"Final Score: {player_score}", True, (0, 255, 65)
            )
            help_msg = text_font.render(
                "Press R to restart or Q to quit", True, (0, 255, 65)
            )
            display.blit(over_msg, (400 - 90, 300 - 60))
            display.blit(score_msg, (400 - 110, 300 - 20))
            display.blit(help_msg, (400 - 200, 300 + 20))

        pygame.display.flip()
        timer.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
