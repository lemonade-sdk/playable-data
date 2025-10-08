# CREATE: galaga

"""
Galaga - Arcade-style shooting game

A fighter ship defends against alien invaders that fly in formation and dive-bomb.
Uses sprite collision and parametric curves for enemy movement patterns.

BUG FIX: In the game loop where the dive timer is reset, the random.randint() call is
missing its closing parenthesis. Add the closing parenthesis after 150.
"""

import pygame
import random
import math

pygame.init()

WIDTH = 500
HEIGHT = 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galaga")
clock = pygame.time.Clock()

BLACK = (0, 0, 0)
GREEN = (0, 255, 65)
CYAN = (0, 220, 220)
YELLOW = (255, 240, 0)


class Fighter(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((28, 28))
        self.image.fill(BLACK)
        # Diamond shape
        pygame.draw.polygon(self.image, GREEN, [(14, 0), (28, 14), (14, 28), (0, 14)])
        pygame.draw.polygon(self.image, GREEN, [(14, 8), (20, 14), (14, 20), (8, 14)])
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 45))
        
    def tick(self):
        keys = pygame.key.get_pressed()
        movement = 5
        if keys[pygame.K_LEFT]:
            self.rect.x = max(0, self.rect.x - movement)
        if keys[pygame.K_RIGHT]:
            self.rect.x = min(WIDTH - self.rect.width, self.rect.x + movement)


class Shot(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((3, 12))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction
        
    def tick(self):
        self.rect.y += self.direction * 11
        if self.rect.y < -20 or self.rect.y > HEIGHT + 20:
            self.kill()


class Invader(pygame.sprite.Sprite):
    def __init__(self, x, y, anchor_x, anchor_y, variant):
        super().__init__()
        self.variant = variant
        self.image = pygame.Surface((26, 26))
        self.image.fill(BLACK)
        
        if variant == 0:
            self.tint = YELLOW
            self.worth = 180
            pygame.draw.ellipse(self.image, self.tint, (3, 8, 20, 14), 2)
            pygame.draw.circle(self.image, self.tint, (9, 13), 3, 2)
            pygame.draw.circle(self.image, self.tint, (17, 13), 3, 2)
        elif variant == 1:
            self.tint = CYAN
            self.worth = 90
            pygame.draw.polygon(self.image, self.tint, [(13, 5), (3, 18), (13, 16), (23, 18)], 2)
        else:
            self.tint = GREEN
            self.worth = 45
            pygame.draw.circle(self.image, self.tint, (13, 13), 9, 2)
            
        self.rect = self.image.get_rect(center=(x, y))
        self.anchor_x = anchor_x
        self.anchor_y = anchor_y
        self.diving = False
        self.arriving = True
        self.trajectory = []
        self.arrival_path = []
        self.step = 0
        
        self.build_arrival(anchor_x, anchor_y)
        
    def build_arrival(self, dest_x, dest_y):
        spawn_x = dest_x + random.choice([-180, 180])
        spawn_y = -40
        
        for i in range(71):
            t = i / 70
            wave = math.cos(t * math.pi * 5) * 60 * (1 - t)
            px = spawn_x + (dest_x - spawn_x) * t + wave
            py = spawn_y + (dest_y - spawn_y) * t
            self.arrival_path.append((px, py))
        self.arrival_path[-1] = (dest_x, dest_y)
        self.rect.center = self.arrival_path[0]
        
    def launch_dive(self, target_x, spread=0):
        self.diving = True
        self.step = 0
        sx, sy = self.rect.centerx, self.rect.centery
        self.trajectory = []
        
        for i in range(95):
            t = i / 95
            angle = t * math.pi * 3
            px = sx + math.cos(angle) * 130 + (target_x - sx) * t + spread
            py = sy + t * 480 + math.sin(angle * 1.5) * 70
            self.trajectory.append((px, py))
        
        last_x, last_y = self.trajectory[-1]
        for i in range(65):
            t = i / 65
            arc = math.cos(t * math.pi) * 90
            px = last_x + (self.anchor_x - last_x) * t + arc
            py = last_y + (self.anchor_y - last_y) * t
            self.trajectory.append((px, py))
    
    def tick(self, offset):
        if self.arriving:
            if self.step < len(self.arrival_path):
                self.rect.center = self.arrival_path[self.step]
                self.step += 1
            else:
                self.arriving = False
                self.step = 0
            return None
        elif self.diving:
            if self.step < len(self.trajectory):
                self.rect.center = self.trajectory[self.step]
                self.step += 1
                if self.step % 18 == 0:
                    return Shot(self.rect.centerx, self.rect.bottom, 1)
            else:
                self.diving = False
            return None
        else:
            self.rect.centerx = self.anchor_x + offset
            self.rect.centery = self.anchor_y
            return None


class GameController:
    def __init__(self):
        self.restart()
        
    def restart(self):
        self.fighter = Fighter()
        self.shots = pygame.sprite.Group()
        self.invaders = pygame.sprite.Group()
        self.enemy_shots = pygame.sprite.Group()
        self.sprites = pygame.sprite.Group(self.fighter)
        
        # Fewer invaders but more aggressive
        for r in range(3):
            for c in range(6):
                px = 80 + c * 65
                py = 90 + r * 50
                v = 0 if r == 0 else (1 if r == 1 else 2)
                inv = Invader(px, py, px, py, v)
                self.invaders.add(inv)
                self.sprites.add(inv)
        
        self.points = 0
        self.lives = 3
        self.ended = False
        self.sway = 0
        self.sway_dir = 1
        self.dive_timer = 80
        self.shot_delay = 0
        
    def spawn_next_wave(self):
        if not self.invaders:
            for r in range(3):
                for c in range(6):
                    px = 80 + c * 65
                    py = 90 + r * 50
                    v = 0 if r == 0 else (1 if r == 1 else 2)
                    inv = Invader(px, py, px, py, v)
                    self.invaders.add(inv)
                    self.sprites.add(inv)


def main():
    game = GameController()
    running = True
    
    while running:
        clock.tick(60)
        
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                running = False
            if evt.type == pygame.KEYDOWN:
                if game.ended:
                    if evt.key == pygame.K_r:
                        game.restart()
                    elif evt.key == pygame.K_q:
                        running = False
        
        if not game.ended:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] and game.shot_delay <= 0:
                # Double shot
                s1 = Shot(game.fighter.rect.centerx - 8, game.fighter.rect.top, -1)
                s2 = Shot(game.fighter.rect.centerx + 8, game.fighter.rect.top, -1)
                game.shots.add(s1, s2)
                game.sprites.add(s1, s2)
                game.shot_delay = 18
            game.shot_delay -= 1
            
            game.fighter.tick()
            
            for s in game.shots:
                s.tick()
            for s in game.enemy_shots:
                s.tick()
            
            game.sway += game.sway_dir * 0.7
            if abs(game.sway) > 45:
                game.sway_dir *= -1
            
            game.dive_timer -= 1
            if game.dive_timer <= 0 and game.invaders:
                game.dive_timer = random.randint(70, 150)  # Fixed: was missing closing parenthesis
                ready = [i for i in game.invaders if not i.diving and not i.arriving]
                if ready:
                    num = min(random.randint(2, 3), len(ready))
                    divers = random.sample(ready, num)
                    for idx, d in enumerate(divers):
                        d.launch_dive(game.fighter.rect.centerx, (idx - num // 2) * 35)
            
            for inv in game.invaders:
                bullet = inv.tick(game.sway)
                if bullet:
                    game.enemy_shots.add(bullet)
            
            for shot in game.shots:
                hits = pygame.sprite.spritecollide(shot, game.invaders, True)
                if hits:
                    shot.kill()
                    game.points += hits[0].worth
            
            if pygame.sprite.spritecollide(game.fighter, game.enemy_shots, True):
                game.lives -= 1
                if game.lives <= 0:
                    game.ended = True
            
            if pygame.sprite.spritecollide(game.fighter, game.invaders, True):
                game.lives -= 1
                if game.lives <= 0:
                    game.ended = True
            
            for inv in list(game.invaders):
                if inv.rect.top > HEIGHT:
                    inv.kill()
            
            game.spawn_next_wave()
        
        screen.fill(BLACK)
        game.sprites.draw(screen)
        game.shots.draw(screen)
        game.enemy_shots.draw(screen)
        
        font = pygame.font.Font(None, 32)
        pts_text = font.render(f"Score: {game.points}", True, GREEN)
        life_text = font.render(f"Lives: {game.lives}", True, GREEN)
        screen.blit(pts_text, (12, 12))
        screen.blit(life_text, (12, 45))
        
        if game.ended:
            big_font = pygame.font.Font(None, 70)
            over_text = big_font.render("GAME OVER", True, GREEN)
            info_text = font.render("Press R to Restart or Q to Quit", True, GREEN)
            screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 50))
            screen.blit(info_text, (WIDTH // 2 - info_text.get_width() // 2, HEIGHT // 2 + 20))
        
        pygame.display.flip()
    
    pygame.quit()


if __name__ == "__main__":
    main()

