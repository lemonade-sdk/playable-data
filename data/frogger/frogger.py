"""
Frogger - A classic arcade game where the player controls a frog crossing roads and rivers.
The frog must avoid cars on roads and jump on logs to cross water sections. Game ends when
the frog is hit by a car, falls in water, or successfully reaches the goal area.
Uses grid-based movement and collision detection.
Implementation uses pygame with minimal graphics and clean object-oriented design.
"""

import pygame

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 65)
DARK_GREEN = (0, 150, 30)
BLUE = (0, 100, 200)
GRAY = (128, 128, 128)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

# Game constants
GRID_SIZE = 40
FROG_SIZE = 30
CAR_WIDTH = 60
CAR_HEIGHT = 35
LOG_WIDTH = 120
LOG_HEIGHT = 35


class Frog:
    def __init__(self):
        self.start_x = SCREEN_WIDTH // 2
        self.start_y = SCREEN_HEIGHT - GRID_SIZE
        self.rect = pygame.Rect(
            self.start_x - FROG_SIZE // 2,
            self.start_y - FROG_SIZE // 2,
            FROG_SIZE,
            FROG_SIZE,
        )
        self.on_log = None

    def move(self, dx, dy):
        new_x = self.rect.x + dx * GRID_SIZE
        new_y = self.rect.y + dy * GRID_SIZE

        # Keep frog on screen
        if 0 <= new_x <= SCREEN_WIDTH - FROG_SIZE:
            self.rect.x = new_x
        if 0 <= new_y <= SCREEN_HEIGHT - FROG_SIZE:
            self.rect.y = new_y

    def update(self):
        # Move with log if on one
        if self.on_log:
            self.rect.x += self.on_log.speed
            # Check if frog went off screen while on log
            if self.rect.x < -FROG_SIZE or self.rect.x > SCREEN_WIDTH:
                return False
        return True

    def reset(self):
        self.rect.x = self.start_x - FROG_SIZE // 2
        self.rect.y = self.start_y - FROG_SIZE // 2
        self.on_log = None

    def draw(self, screen):
        # Draw frog as simple green square
        pygame.draw.rect(screen, GREEN, self.rect)


class Car:
    def __init__(self, x, y, speed):
        self.rect = pygame.Rect(x, y, CAR_WIDTH, CAR_HEIGHT)
        self.speed = speed

    def update(self):
        self.rect.x += self.speed
        # Wrap around screen
        if self.speed > 0 and self.rect.x > SCREEN_WIDTH:
            self.rect.x = -CAR_WIDTH
        elif self.speed < 0 and self.rect.right < 0:
            self.rect.x = SCREEN_WIDTH

    def draw(self, screen):
        # Draw car as simple red rectangle
        pygame.draw.rect(screen, RED, self.rect)


class Log:
    def __init__(self, x, y, speed):
        self.rect = pygame.Rect(x, y, LOG_WIDTH, LOG_HEIGHT)
        self.speed = speed

    def update(self):
        self.rect.x += self.speed
        # Wrap around screen
        if self.speed > 0 and self.rect.x > SCREEN_WIDTH:
            self.rect.x = -LOG_WIDTH
        elif self.speed < 0 and self.rect.right < 0:
            self.rect.x = SCREEN_WIDTH

    def draw(self, screen):
        # Draw log as simple brown rectangle
        pygame.draw.rect(screen, BROWN, self.rect)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Frogger")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.reset_game()

    def reset_game(self):
        self.frog = Frog()
        self.game_over = False
        self.won = False

        # Create cars for road sections
        self.cars = []
        # Bottom road (moving right)
        for i in range(3):
            x = i * 250
            y = SCREEN_HEIGHT - 3 * GRID_SIZE
            self.cars.append(Car(x, y, 2))

        # Middle road (moving left)
        for i in range(3):
            x = i * 250
            y = SCREEN_HEIGHT - 5 * GRID_SIZE
            self.cars.append(Car(x, y, -3))

        # Top road (moving right)
        for i in range(2):
            x = i * 300
            y = SCREEN_HEIGHT - 7 * GRID_SIZE
            self.cars.append(Car(x, y, 4))

        # Create logs for river sections
        self.logs = []
        # Bottom river (moving right)
        for i in range(3):
            x = i * 280
            y = SCREEN_HEIGHT - 10 * GRID_SIZE
            self.logs.append(Log(x, y, 1))

        # Middle river (moving left)
        for i in range(3):
            x = i * 280
            y = SCREEN_HEIGHT - 12 * GRID_SIZE
            self.logs.append(Log(x, y, -2))

        # Top river (moving right)
        for i in range(2):
            x = i * 350
            y = SCREEN_HEIGHT - 14 * GRID_SIZE
            self.logs.append(Log(x, y, 1.5))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if self.game_over or self.won:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_q:
                        return False
                else:
                    # Frog movement
                    if event.key == pygame.K_UP:
                        self.frog.move(0, -1)
                    elif event.key == pygame.K_DOWN:
                        self.frog.move(0, 1)
                    elif event.key == pygame.K_LEFT:
                        self.frog.move(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.frog.move(1, 0)

        return True

    def check_collisions(self):
        # Check if frog reached goal
        if self.frog.rect.y < GRID_SIZE:
            self.won = True
            return

        # Check car collisions
        for car in self.cars:
            if self.frog.rect.colliderect(car.rect):
                self.game_over = True
                return

        # Check if in water zone
        frog_y = self.frog.rect.centery
        in_water_zone = (
            SCREEN_HEIGHT - 14 * GRID_SIZE <= frog_y <= SCREEN_HEIGHT - 9 * GRID_SIZE
        )

        if in_water_zone:
            # Check if on a log
            self.frog.on_log = None
            for log in self.logs:
                if self.frog.rect.colliderect(log.rect):
                    self.frog.on_log = log
                    break

            # If in water but not on a log, game over
            if not self.frog.on_log:
                self.game_over = True
        else:
            self.frog.on_log = None

    def update(self):
        if not self.game_over and not self.won:
            # Update cars
            for car in self.cars:
                car.update()

            # Update logs
            for log in self.logs:
                log.update()

            # Update frog
            if not self.frog.update():
                self.game_over = True

            # Check collisions
            self.check_collisions()

    def draw_background(self):
        self.screen.fill(BLACK)

        # Draw goal area
        pygame.draw.rect(self.screen, DARK_GREEN, (0, 0, SCREEN_WIDTH, GRID_SIZE))

        # Draw water zones
        water_top = SCREEN_HEIGHT - 14 * GRID_SIZE
        water_height = 5 * GRID_SIZE
        pygame.draw.rect(self.screen, BLUE, (0, water_top, SCREEN_WIDTH, water_height))

        # Draw roads
        road_positions = [
            SCREEN_HEIGHT - 7 * GRID_SIZE,
            SCREEN_HEIGHT - 5 * GRID_SIZE,
            SCREEN_HEIGHT - 3 * GRID_SIZE,
        ]
        for y in road_positions:
            pygame.draw.rect(self.screen, GRAY, (0, y, SCREEN_WIDTH, GRID_SIZE))

        # Draw safe zones
        safe_zones = [SCREEN_HEIGHT - GRID_SIZE, SCREEN_HEIGHT - 8 * GRID_SIZE]
        for y in safe_zones:
            pygame.draw.rect(self.screen, DARK_GREEN, (0, y, SCREEN_WIDTH, GRID_SIZE))

    def draw(self):
        self.draw_background()

        # Draw logs (behind frog)
        for log in self.logs:
            log.draw(self.screen)

        # Draw cars
        for car in self.cars:
            car.draw(self.screen)

        # Draw frog
        self.frog.draw(self.screen)

        # Draw game over screen
        if self.game_over:
            game_over_text = self.font.render("GAME OVER", True, RED)
            text_rect = game_over_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            )
            self.screen.blit(game_over_text, text_rect)

            restart_text = self.font.render(
                "Press R to restart or Q to quit", True, WHITE
            )
            text_rect = restart_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            )
            self.screen.blit(restart_text, text_rect)

        # Draw win screen
        elif self.won:
            win_text = self.font.render("YOU WIN!", True, WHITE)
            text_rect = win_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            )
            self.screen.blit(win_text, text_rect)

            restart_text = self.font.render(
                "Press R to restart or Q to quit", True, WHITE
            )
            text_rect = restart_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            )
            self.screen.blit(restart_text, text_rect)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()


# Main game execution
if __name__ == "__main__":
    game = Game()
    game.run()
