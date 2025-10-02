"""
Breakout - Arcade-style brick breaking game.
Guide your paddle to bounce the ball and eliminate all bricks from the screen.
Clear all bricks to win. If the ball drops below the paddle, the game is over.
Built with pygame featuring object-oriented design and basic collision physics.
"""

import pygame
import random
import sys

pygame.init()

BLACK = (0, 0, 0)
GREEN = (0, 255, 65)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)


class Paddle:
    def __init__(self, screen_width, screen_height):
        self.width = 105
        self.height = 16
        self.speed = 7
        self.screen_w = screen_width
        self.x_pos = screen_width // 2 - self.width // 2
        self.y_pos = screen_height - 55

    def tick(self, key_state):
        if key_state[pygame.K_LEFT] and self.x_pos > 0:
            self.x_pos -= self.speed
        if key_state[pygame.K_RIGHT] and self.x_pos < self.screen_w - self.width:
            self.x_pos += self.speed

    def draw(self, screen):
        pygame.draw.rect(
            screen, GREEN, (self.x_pos, self.y_pos, self.width, self.height)
        )

    def get_bounds(self):
        return pygame.Rect(self.x_pos, self.y_pos, self.width, self.height)


class Ball:
    def __init__(self, screen_width, screen_height):
        self.screen_w = screen_width
        self.screen_h = screen_height
        self.diameter = 13
        self.init_speed = 5
        self.restart()

    def restart(self):
        self.pos_x = self.screen_w // 2
        self.pos_y = self.screen_h // 2
        direction = random.choice([-1, 1])
        self.vel_x = direction * self.init_speed
        self.vel_y = self.init_speed

    def tick(self):
        self.pos_x += self.vel_x
        self.pos_y += self.vel_y

        # Bounce off side walls and top
        if self.pos_x <= 0 or self.pos_x >= self.screen_w - self.diameter:
            self.vel_x = -self.vel_x
        if self.pos_y <= 0:
            self.vel_y = -self.vel_y

    def draw(self, screen):
        center_x = int(self.pos_x)
        center_y = int(self.pos_y)
        pygame.draw.circle(screen, WHITE, (center_x, center_y), self.diameter // 2)

    def get_bounds(self):
        radius = self.diameter // 2
        return pygame.Rect(
            self.pos_x - radius, self.pos_y - radius, self.diameter, self.diameter
        )

    def off_screen(self):
        return self.pos_y > self.screen_h


class Brick:
    def __init__(self, x, y, w, h, color):
        self.pos_x = x
        self.pos_y = y
        self.brick_width = w
        self.brick_height = h
        self.brick_color = color
        self.hit = False

    def draw(self, screen):
        if not self.hit:
            pygame.draw.rect(
                screen,
                self.brick_color,
                (self.pos_x, self.pos_y, self.brick_width, self.brick_height),
            )
            pygame.draw.rect(
                screen,
                BLACK,
                (self.pos_x, self.pos_y, self.brick_width, self.brick_height),
                2,
            )

    def get_bounds(self):
        return pygame.Rect(self.pos_x, self.pos_y, self.brick_width, self.brick_height)

    def mark_hit(self):
        self.hit = True


class BreakoutGame:
    SCREEN_SIZE = 600
    BRICK_W = 65
    BRICK_H = 26
    NUM_ROWS = 6
    NUM_COLS = 8
    SPACING = 5

    def __init__(self):
        self.screen = pygame.display.set_mode((self.SCREEN_SIZE, self.SCREEN_SIZE))
        pygame.display.set_caption("Breakout")
        self.clock = pygame.time.Clock()
        self.display_font = pygame.font.Font(None, 32)
        self.reset_game()

    def reset_game(self):
        self.paddle = Paddle(self.SCREEN_SIZE, self.SCREEN_SIZE)
        self.ball = Ball(self.SCREEN_SIZE, self.SCREEN_SIZE)
        self.bricks = []
        self.player_score = 0
        self.finished = False
        self.victory = False
        self.create_brick_grid()

    def create_brick_grid(self):
        color_sequence = [RED, RED, YELLOW, YELLOW, BLUE, BLUE]

        grid_width = self.NUM_COLS * self.BRICK_W + (self.NUM_COLS - 1) * self.SPACING
        start_x = (self.SCREEN_SIZE - grid_width) // 2
        start_y = 55

        for row_idx in range(self.NUM_ROWS):
            for col_idx in range(self.NUM_COLS):
                brick_x = start_x + col_idx * (self.BRICK_W + self.SPACING)
                brick_y = start_y + row_idx * (self.BRICK_H + self.SPACING)
                brick_color = color_sequence[row_idx]
                brick = Brick(brick_x, brick_y, self.BRICK_W, self.BRICK_H, brick_color)
                self.bricks.append(brick)

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if self.finished:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_q:
                        return False
        return True

    def tick(self):
        if not self.finished:
            key_state = pygame.key.get_pressed()
            self.paddle.tick(key_state)
            self.ball.tick()

            # Ball and paddle collision
            if self.ball.get_bounds().colliderect(self.paddle.get_bounds()):
                if self.ball.vel_y > 0:
                    self.ball.vel_y = -self.ball.vel_y
                    # Adjust ball direction based on paddle hit location
                    hit_offset = (
                        self.ball.pos_x - self.paddle.x_pos
                    ) / self.paddle.width
                    self.ball.vel_x = self.ball.init_speed * (hit_offset - 0.5) * 2

            # Ball and brick collisions
            for brick in self.bricks:
                if not brick.hit:
                    if self.ball.get_bounds().colliderect(brick.get_bounds()):
                        brick.mark_hit()
                        self.ball.vel_y = -self.ball.vel_y
                        self.player_score += 18
                        break

            # Check if all bricks destroyed
            if all(b.hit for b in self.bricks):
                self.finished = True
                self.victory = True

            # Check if ball fell
            if self.ball.off_screen():
                self.finished = True

    def render(self):
        self.screen.fill(BLACK)

        # Draw all game entities
        self.paddle.draw(self.screen)
        self.ball.draw(self.screen)
        for brick in self.bricks:
            brick.draw(self.screen)

        # Draw score text
        score_text = self.display_font.render(
            f"Score: {self.player_score}", True, WHITE
        )
        self.screen.blit(score_text, (15, 15))

        # Draw end game overlay
        if self.finished:
            if self.victory:
                status_text = self.display_font.render("You Win!", True, GREEN)
            else:
                status_text = self.display_font.render("Game Over!", True, RED)

            help_text = self.display_font.render(
                "Press R to restart or Q to quit", True, WHITE
            )

            status_pos = status_text.get_rect(
                center=(self.SCREEN_SIZE // 2, self.SCREEN_SIZE // 2 - 30)
            )
            help_pos = help_text.get_rect(
                center=(self.SCREEN_SIZE // 2, self.SCREEN_SIZE // 2 + 30)
            )

            self.screen.blit(status_text, status_pos)
            self.screen.blit(help_text, help_pos)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.check_events()
            self.tick()
            self.render()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = BreakoutGame()
    game.run()
