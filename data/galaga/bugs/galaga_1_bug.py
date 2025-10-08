# CREATE: galaga
# ERROR: Traceback (most recent call last):
# ERROR:   File "C:\work\lsdk\playable-data\data\galaga\bugs\galaga_1_bug.py", line 311, in <module>
# ERROR:     main()
# ERROR:   File "C:\work\lsdk\playable-data\data\galaga\bugs\galaga_1_bug.py", line 273, in main
# ERROR:     hit_aliens = pygame.sprite.spritecollide(proj, game.spaceship, True)
# ERROR:                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# ERROR: AttributeError: 'Spaceship' object has no attribute 'sprites'

"""
Galaga - Space shooter arcade game

Player controls a spaceship that shoots enemies in formation. Enemies swoop down
to attack. Uses pygame sprite groups for entity management and collision detection.
"""

import pygame
import random
import math

# Display settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
FPS = 60

# Movement constants
SHIP_VELOCITY = 6
PROJECTILE_VELOCITY = 12
ENEMY_PROJECTILE_VELOCITY = 7

# Colors
COLOR_BLACK = (0, 0, 0)
COLOR_PRIMARY = (0, 255, 65)
COLOR_SECONDARY = (100, 200, 255)
COLOR_ACCENT = (255, 220, 0)

pygame.init()
display = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Galaga")
game_clock = pygame.time.Clock()


class Spaceship(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((35, 35))
        self.image.fill(COLOR_BLACK)
        pygame.draw.rect(self.image, COLOR_PRIMARY, (12, 0, 11, 35))
        pygame.draw.rect(self.image, COLOR_PRIMARY, (0, 25, 35, 10))
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))
        self.velocity = SHIP_VELOCITY
        
    def move(self):
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.velocity
        if pressed_keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.velocity


class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, velocity):
        super().__init__()
        self.image = pygame.Surface((4, 18))
        self.image.fill(COLOR_PRIMARY)
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity = velocity
        
    def move(self):
        self.rect.y += self.velocity
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Alien(pygame.sprite.Sprite):
    def __init__(self, x, y, home_x, home_y, alien_tier):
        super().__init__()
        self.tier = alien_tier
        self.image = pygame.Surface((32, 32))
        self.image.fill(COLOR_BLACK)
        
        if alien_tier == 0:
            self.color = COLOR_ACCENT
            self.score_value = 200
            pygame.draw.rect(self.image, self.color, (4, 4, 24, 24), 3)
            pygame.draw.circle(self.image, self.color, (12, 16), 4)
            pygame.draw.circle(self.image, self.color, (20, 16), 4)
        elif alien_tier == 1:
            self.color = COLOR_SECONDARY
            self.score_value = 100
            pygame.draw.rect(self.image, self.color, (6, 6, 20, 20), 3)
            pygame.draw.line(self.image, self.color, (6, 16), (26, 16), 3)
        else:
            self.color = COLOR_PRIMARY
            self.score_value = 60
            pygame.draw.rect(self.image, self.color, (8, 8, 16, 16), 3)
            
        self.rect = self.image.get_rect(center=(x, y))
        self.home_x = home_x
        self.home_y = home_y
        self.is_attacking = False
        self.is_entering = True
        self.attack_waypoints = []
        self.entry_waypoints = []
        self.waypoint_counter = 0
        
        self.generate_entry_path(home_x, home_y)
        
    def generate_entry_path(self, dest_x, dest_y):
        origin_x = dest_x + random.choice([-250, 250])
        origin_y = -60
        self.entry_waypoints = []
        
        for step in range(91):
            progress = step / 90
            curve = math.sin(progress * math.pi * 4) * 80 * (1 - progress)
            x = origin_x + (dest_x - origin_x) * progress + curve
            y = origin_y + (dest_y - origin_y) * progress
            self.entry_waypoints.append((x, y))
        self.entry_waypoints[-1] = (dest_x, dest_y)
        self.rect.center = self.entry_waypoints[0]
        
    def begin_attack(self, target_x, lateral_offset=0):
        self.is_attacking = True
        self.waypoint_counter = 0
        origin_x, origin_y = self.rect.centerx, self.rect.centery
        self.attack_waypoints = []
        
        for step in range(110):
            progress = step / 110
            theta = progress * math.pi * 2.5
            x = origin_x + math.sin(theta * 2) * 140 + (target_x - origin_x) * progress + lateral_offset
            y = origin_y + progress * 550 + math.cos(theta * 2) * 60
            self.attack_waypoints.append((x, y))
        
        final_x, final_y = self.attack_waypoints[-1]
        for step in range(70):
            progress = step / 70
            x = final_x + (self.home_x - final_x) * progress
            y = final_y + (self.home_y - final_y) * progress - math.sin(progress * math.pi) * 120
            self.attack_waypoints.append((x, y))
    
    def move(self, formation_drift, projectile_group):
        bullet = None
        if self.is_entering:
            if self.waypoint_counter < len(self.entry_waypoints):
                self.rect.center = self.entry_waypoints[self.waypoint_counter]
                self.waypoint_counter += 1
            else:
                self.is_entering = False
                self.waypoint_counter = 0
        elif self.is_attacking:
            if self.waypoint_counter < len(self.attack_waypoints):
                self.rect.center = self.attack_waypoints[self.waypoint_counter]
                self.waypoint_counter += 1
                
                if self.waypoint_counter % 25 == 0:
                    bullet = Projectile(self.rect.centerx, self.rect.bottom, ENEMY_PROJECTILE_VELOCITY)
            else:
                self.is_attacking = False
        else:
            self.rect.centerx = self.home_x + formation_drift
            self.rect.centery = self.home_y
            
        return bullet


class GameState:
    def __init__(self):
        self.initialize()
        
    def initialize(self):
        self.spaceship = Spaceship()
        self.player_projectiles = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.alien_projectiles = pygame.sprite.Group()
        self.all_entities = pygame.sprite.Group(self.spaceship)
        
        for row_idx in range(5):
            for col_idx in range(8):
                pos_x = 120 + col_idx * 70
                pos_y = 80 + row_idx * 55
                if row_idx == 0:
                    tier = 0
                elif row_idx <= 2:
                    tier = 1
                else:
                    tier = 2
                alien = Alien(pos_x, pos_y, pos_x, pos_y, tier)
                self.aliens.add(alien)
                self.all_entities.add(alien)
        
        self.player_score = 0
        self.remaining_lives = 3
        self.is_game_over = False
        self.formation_drift = 0
        self.drift_direction = 1
        self.attack_countdown = 140
        self.fire_cooldown = 0
        
    def respawn_wave(self):
        if len(self.aliens) == 0:
            for row_idx in range(5):
                for col_idx in range(8):
                    pos_x = 120 + col_idx * 70
                    pos_y = 80 + row_idx * 55
                    if row_idx == 0:
                        tier = 0
                    elif row_idx <= 2:
                        tier = 1
                    else:
                        tier = 2
                    alien = Alien(pos_x, pos_y, pos_x, pos_y, tier)
                    self.aliens.add(alien)
                    self.all_entities.add(alien)


def main():
    game = GameState()
    active = True
    
    while active:
        game_clock.tick(FPS)
        
        for game_event in pygame.event.get():
            if game_event.type == pygame.QUIT:
                active = False
            
            if game_event.type == pygame.KEYDOWN:
                if game.is_game_over:
                    if game_event.key == pygame.K_r:
                        game.initialize()
                    elif game_event.key == pygame.K_q:
                        active = False
        
        if not game.is_game_over:
            pressed_keys = pygame.key.get_pressed()
            if pressed_keys[pygame.K_SPACE] and game.fire_cooldown <= 0:
                projectile = Projectile(game.spaceship.rect.centerx, game.spaceship.rect.top, -PROJECTILE_VELOCITY)
                game.player_projectiles.add(projectile)
                game.all_entities.add(projectile)
                game.fire_cooldown = 20
            game.fire_cooldown -= 1
            
            game.spaceship.move()
            game.player_projectiles.update()
            
            for proj in game.player_projectiles:
                proj.move()
            for proj in game.alien_projectiles:
                proj.move()
            
            game.formation_drift += game.drift_direction * 0.6
            if abs(game.formation_drift) > 60:
                game.drift_direction *= -1
            
            game.attack_countdown -= 1
            if game.attack_countdown <= 0 and len(game.aliens) > 0:
                game.attack_countdown = random.randint(100, 200)
                ready_aliens = [a for a in game.aliens if not a.is_attacking and not a.is_entering]
                if ready_aliens:
                    squad_size = min(random.randint(1, 2), len(ready_aliens))
                    attackers = random.sample(ready_aliens, squad_size)
                    for idx, attacker in enumerate(attackers):
                        attacker.begin_attack(game.spaceship.rect.centerx, idx * 50 - 25)
            
            for alien in game.aliens:
                new_bullet = alien.move(game.formation_drift, game.all_entities)
                if new_bullet:
                    game.alien_projectiles.add(new_bullet)
            
            for proj in game.player_projectiles:
                hit_aliens = pygame.sprite.spritecollide(proj, game.spaceship, True)
                if hit_aliens:
                    proj.kill()
                    game.player_score += hit_aliens[0].score_value
            
            if pygame.sprite.spritecollide(game.spaceship, game.alien_projectiles, True):
                game.remaining_lives -= 1
                if game.remaining_lives <= 0:
                    game.is_game_over = True
            
            if pygame.sprite.spritecollide(game.spaceship, game.aliens, True):
                game.remaining_lives -= 1
                if game.remaining_lives <= 0:
                    game.is_game_over = True
            
            for alien in list(game.aliens):
                if alien.rect.top > SCREEN_HEIGHT:
                    alien.kill()
            
            game.respawn_wave()
        
        display.fill(COLOR_BLACK)
        game.all_entities.draw(display)
        game.player_projectiles.draw(display)
        game.alien_projectiles.draw(display)
        
        text_font = pygame.font.Font(None, 38)
        score_surface = text_font.render(f"Score: {game.player_score}", True, COLOR_PRIMARY)
        lives_surface = text_font.render(f"Lives: {game.remaining_lives}", True, COLOR_PRIMARY)
        display.blit(score_surface, (15, 15))
        display.blit(lives_surface, (15, 55))
        
        if game.is_game_over:
            large_font = pygame.font.Font(None, 80)
            game_over_surface = large_font.render("GAME OVER", True, COLOR_PRIMARY)
            restart_surface = text_font.render("Press R to Restart or Q to Quit", True, COLOR_PRIMARY)
            display.blit(game_over_surface, (SCREEN_WIDTH // 2 - game_over_surface.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
            display.blit(restart_surface, (SCREEN_WIDTH // 2 - restart_surface.get_width() // 2, SCREEN_HEIGHT // 2 + 30))
        
        pygame.display.flip()
    
    pygame.quit()


if __name__ == "__main__":
    main()

