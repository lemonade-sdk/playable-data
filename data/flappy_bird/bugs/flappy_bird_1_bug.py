# CREATE: flappy bird
# ERROR: Traceback (most recent call last):
# ERROR:   File "C:\work\lsdk\playable-data\data\flappy_bird\bugs\flappy_bird_1_bug.py", line 191, in <module>
# ERROR:     game = Game()
# ERROR:            ^^^^^^
# ERROR:   File "C:\work\lsdk\playable-data\data\flappy_bird\bugs\flappy_bird_1_bug.py", line 88, in __init__
# ERROR:     self.reset()
# ERROR:   File "C:\work\lsdk\playable-data\data\flappy_bird\bugs\flappy_bird_1_bug.py", line 96, in reset
# ERROR:     self.update_high_score()
# ERROR:   File "C:\work\lsdk\playable-data\data\flappy_bird\bugs\flappy_bird_1_bug.py", line 99, in update_high_score
# ERROR:     if self.points > high_score:
# ERROR:                      ^^^^^^^^^^
# ERROR: UnboundLocalError: cannot access local variable 'high_score' where it is not associated with a value

"""
Flappy Bird - Side-scrolling game where you guide a bird through pipes.
The bird constantly falls and you make it jump by pressing spacebar. Avoid hitting pipes or the ground.
Score points by passing through pipes successfully. Simple physics-based gameplay.
"""

import pygame
import random
import sys

pygame.init()

# Screen setup
WIDTH = 600
HEIGHT = 500
BIRD_SIZE = 25
PIPE_W = 70
GAP_SIZE = 180
PIPE_VEL = 2.5
GRAV = 0.4
JUMP = -7
BLACK = (0, 0, 0)
GREEN = (0, 255, 65)
WHITE = (255, 255, 255)

high_score = 0


class Bird:
    def __init__(self):
        self.x = 80
        self.y = HEIGHT // 2
        self.vel = 0

    def jump(self):
        self.vel = JUMP

    def move(self):
        self.vel += GRAV
        self.y += self.vel

    def draw(self, screen):
        # Draw as square
        half = BIRD_SIZE // 2
        pygame.draw.rect(
            screen, GREEN, (self.x - half, self.y - half, BIRD_SIZE, BIRD_SIZE)
        )

    def get_rect(self):
        half = BIRD_SIZE // 2
        return pygame.Rect(self.x - half, self.y - half, BIRD_SIZE, BIRD_SIZE)


class Pipe:
    def __init__(self, x_pos):
        self.x = x_pos
        self.gap_top = random.randint(120, HEIGHT - 120 - GAP_SIZE)
        self.scored = False

    def move(self):
        self.x -= PIPE_VEL

    def draw(self, screen):
        # Top pipe
        pygame.draw.rect(screen, GREEN, (self.x, 0, PIPE_W, self.gap_top))
        # Bottom pipe
        bottom_y = self.gap_top + GAP_SIZE
        pygame.draw.rect(screen, GREEN, (self.x, bottom_y, PIPE_W, HEIGHT - bottom_y))

    def get_collision_rects(self):
        top = pygame.Rect(self.x, 0, PIPE_W, self.gap_top)
        bottom_y = self.gap_top + GAP_SIZE
        bottom = pygame.Rect(self.x, bottom_y, PIPE_W, HEIGHT - bottom_y)
        return [top, bottom]

    def off_screen(self):
        return self.x + PIPE_W < 0


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Flappy Bird")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)
        self.reset()

    def reset(self):
        self.bird = Bird()
        self.pipes = []
        self.points = 0
        self.is_over = False
        self.frame_count = 0
        self.update_high_score()

    def update_high_score(self):
        if self.points > high_score:
            high_score = self.points

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if self.is_over:
                    if event.key == pygame.K_r:
                        self.reset()
                    elif event.key == pygame.K_q:
                        return False
                else:
                    if event.key == pygame.K_SPACE:
                        self.bird.jump()
        return True

    def update(self):
        if not self.is_over:
            self.bird.move()

            # Create new pipes
            self.frame_count += 1
            if self.frame_count > 100:  # Every ~1.67 seconds
                self.pipes.append(Pipe(WIDTH))
                self.frame_count = 0

            # Update pipes
            for pipe in self.pipes[:]:
                pipe.move()
                if pipe.off_screen():
                    self.pipes.remove(pipe)
                elif not pipe.scored and pipe.x + PIPE_W < self.bird.x:
                    pipe.scored = True
                    self.points += 1
                    self.update_high_score()

            # Check collisions
            bird_rect = self.bird.get_rect()

            # Check boundaries
            if self.bird.y <= 0 or self.bird.y >= HEIGHT:
                self.is_over = True

            # Check pipe hits
            for pipe in self.pipes:
                for rect in pipe.get_collision_rects():
                    if bird_rect.colliderect(rect):
                        self.is_over = True

    def render(self):
        self.screen.fill(BLACK)

        self.bird.draw(self.screen)
        for pipe in self.pipes:
            pipe.draw(self.screen)

        # Score
        score_surf = self.font.render(f"Score: {self.points}", True, WHITE)
        self.screen.blit(score_surf, (10, 10))

        # High score
        high_surf = self.font.render(f"High: {high_score}", True, WHITE)
        self.screen.blit(high_surf, (10, 40))

        # Game over
        if self.is_over:
            over_text = self.font.render("Game Over!", True, WHITE)
            info_text = self.font.render("Press R to restart or Q to quit", True, WHITE)

            over_rect = over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
            info_rect = info_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))

            self.screen.blit(over_text, over_rect)
            self.screen.blit(info_text, info_rect)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.render()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
