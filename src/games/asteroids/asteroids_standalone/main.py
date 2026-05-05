import pygame
from pygame.math import Vector2
import math
import numpy as np
import numpy.random as random
from sys import exit
import os

# Global constants
WIDTH, HEIGHT, FPS = 480, 320, 60

#initialization
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

curr_dir = os.path.dirname(__file__)
explosion_sfx = pygame.mixer.Sound(os.path.join(curr_dir, "audio", "explosion.wav"))
game_over_sfx = pygame.mixer.Sound(os.path.join(curr_dir, "audio", "game_over.wav"))
die_sfx = pygame.mixer.Sound(os.path.join(curr_dir, "audio", "die.wav"))
shoot_sfx = pygame.mixer.Sound(os.path.join(curr_dir, "audio", "shoot.wav"))
alien_spawn_sfx = pygame.mixer.Sound(os.path.join(curr_dir, "audio", "alien_spawn.wav"))


def polar_to_cartesian_degrees(magnitude, angle):
    rad = math.radians(angle)
    return magnitude * math.cos(rad), magnitude * math.sin(rad)

def polar_to_cartesian_radians(magnitude, angle):
    return magnitude * math.cos(angle), magnitude * math.sin(angle)

def wrap(pos: Vector2, rect: pygame.Rect, buffer: int = 0) -> Vector2:
    half_width = rect.width//2
    half_height = rect.height//2
    if pos.x > WIDTH + half_width + buffer: pos.x = 0 - rect.width//2
    if pos.x < -half_width - buffer: pos.x = WIDTH + rect.width//2
    if pos.y > HEIGHT + half_height + buffer: pos.y = 0 - rect.height//2
    if pos.y < -half_height - buffer: pos.y = HEIGHT + rect.height//2
    return pos
    

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        # Load images
        self.original_surf = pygame.image.load(os.path.join(curr_dir, "graphics", "player", "player.png")).convert_alpha()
        
        self.image = self.original_surf
        self.rect = self.image.get_rect(center=(WIDTH/2, HEIGHT/2))
        
        # Physics
        self.pos = Vector2(WIDTH/2, HEIGHT/2)
        self.vel = Vector2(0, 0)
        self.drag = 0.016
        self.thrust_force = 0.05
        self.turn_speed = 5
        self.angle = 0
        
        self.lives = 3
        self.invulnerable = False
        self.invulnerable_start = 0
        self.show_thrust = False

    def state_reset(self):
        self.pos = Vector2(WIDTH/2, HEIGHT/2)
        self.vel = Vector2(0, 0)
        self.angle = 0


    def full_reset(self):
        self.state_reset()
        
        self.lives = 3
        self.invulnerable = False
        self.invulnerable_start = 0
        self.show_thrust = False

    def get_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: self.angle += self.turn_speed
        if keys[pygame.K_RIGHT]: self.angle -= self.turn_speed
        
        if keys[pygame.K_UP]:
            # Apply thrust
            accel_x, accel_y = polar_to_cartesian_degrees(self.thrust_force, self.angle)
            self.vel.x += -accel_y # Matching original inverted logic
            self.vel.y += -accel_x
            self.show_thrust = (pygame.time.get_ticks() // 100) % 2 == 0 # every 10ms
        else:
            self.show_thrust = False

    def apply_physics(self):
        self.vel *= (1 - self.drag)
        self.pos += self.vel
        
        self.pos = wrap(self.pos, self.rect)
        self.rect.center = self.pos

    def respawn(self):
        die_sfx.play()
        self.state_reset()
        self.lives -= 1
        self.invulnerable = True
        self.invulnerable_start = pygame.time.get_ticks()

    def rotate(self):
        self.image = pygame.transform.rotate(self.original_surf, self.angle)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self):
        self.get_input()
        self.apply_physics()
        self.rotate()
        if self.invulnerable:
            fifth_seconds = ( pygame.time.get_ticks() - self.invulnerable_start ) / 200
            if fifth_seconds > 20:
                self.invulnerable = False
            if fifth_seconds // 1 % 2 == 0:
                # flashing when invulnerable
                self.image = pygame.Surface((0,0))


class ThrustVisual(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        super().__init__(groups)
        self.player = player # Reference to follow the player
        self.original_surf = pygame.image.load(os.path.join(curr_dir, "graphics", "player", "thrust.png")).convert_alpha()
        self.image = self.original_surf
        self.rect = self.image.get_rect()

    def update(self):
        if self.player.show_thrust:
            self.image = pygame.transform.rotate(self.original_surf, self.player.angle)
            self.rect = self.image.get_rect(center=self.player.pos)
        else:
            # hide the sprite by giving it an empty surface
            self.image = pygame.Surface((0,0))


class LifeMeter(pygame.sprite.Sprite):
    def __init__(self, pos, player, condition, groups):
        super().__init__(groups)
        self.image = pygame.image.load(os.path.join(curr_dir, "graphics", "player", "life_icon.png")).convert_alpha()
        self.rect = self.image.get_rect(topleft = pos)
        self.condition = condition
        self.player = player

    def update(self):
        if self.player.lives <= self.condition:
            self.kill()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, shooter_vel, angle, groups, life = 50, speed = 5):
        super().__init__(groups)

        self.image = pygame.image.load(os.path.join(curr_dir, "graphics", "player", "bullet.png")).convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        
        self.speed = speed
        self.pos = Vector2(pos)
        # Calculate velocity based on player direction + player momentum
        vx, vy = polar_to_cartesian_degrees(self.speed, angle)
        self.vel = Vector2(-vy, -vx) + shooter_vel
        
        self.life = life 

    def update(self):
        self.pos += self.vel
        self.pos = wrap(self.pos, self.rect)
        self.rect.center = self.pos
        
        self.life -= 1
        if self.life <= 0:
            self.kill()

class Asteroid(pygame.sprite.Sprite):
    def __init__(self, pos, vel, size, groups):
        super().__init__(groups)
        type_idx = random.randint(1, 4)
        if size in [10, 20]: self.size = size
        else: self.size = 40

        path = os.path.join(curr_dir, "graphics", "asteroids", str(size), f"asteroid_{type_idx}.png")
        self.image = pygame.image.load(path).convert_alpha()
        # self.image = pygame.image.load("graphics/asteroids/amogus.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        
        self.pos = Vector2(pos)
        self.vel = Vector2(vel)
        self.size = size

    def update(self):
        self.pos += self.vel
        self.pos = wrap(self.pos, self.rect)
        self.rect.center = self.pos


class Alien(pygame.sprite.Sprite):
    spawn_frequency = 1 # avg times / min (n * p)
    speed = 1.0
    eps = 5 
    OUT_OF_BOUNDS = 30
    # make sure last waypoint will make alien wrap around but also
    # "gets there" to reset the waypoint by using proper epsilon
    paths = [
        [(40, -10), (140, 85), (340, 85), (440, -10), (480 + OUT_OF_BOUNDS, -10)], # top trapezoid (left -> right)
        [(40, 330), (140, 235), (340, 235), (440, 330), (480 + OUT_OF_BOUNDS, 330)], # bottom trapezoid (left -> right)
        [(440, -10), (340, 85), (140, 85), (40, -10), (-OUT_OF_BOUNDS, -10)], # top trapezoid (right -> left)
        [(440, 330), (340, 235), (140, 235), (40, 330), (-OUT_OF_BOUNDS, 330)], # bottom trapezoid (right -> left)
        [(-10, 40), (480 + OUT_OF_BOUNDS, 40)], # top line (left -> right)
        [(490, 40), (-OUT_OF_BOUNDS, 40)], # top line (right -> left)
        [(-10, 280), (480 + OUT_OF_BOUNDS, 280)], # bottom line (left -> right)
        [(490, 280), (-OUT_OF_BOUNDS, 280)], # bottom line (right -> left)
        [(-10, 40), (50, 40), (140, 130), (340, 130), (440, 260), (480 + OUT_OF_BOUNDS, 260)], # stair (topleft -> bottomright)
        [(-10, 280), (50, 280), (140, 190), (340, 190), (440, 60), (480 + OUT_OF_BOUNDS, 60)], # stair (bottomleft -> topright)
        [(490, 280), (430, 280), (340, 190), (140, 190), (40, 60), (-OUT_OF_BOUNDS, 60)], # stair (bottomright -> topleft)
        [(490, 40), (430, 40), (340, 140), (140, 140), (40, 260), (-OUT_OF_BOUNDS, 260)] # stair (topright -> bottomleft)
    ]

    def __init__(self, size, groups):
        super().__init__(groups)
        if size == 2: self.size = 2
        else: self.size = 1

        self.path_idx = random.randint(0, len(self.paths) - 1)
        self.target_idx = 1
        self.pos = Vector2(self.paths[self.path_idx][0])
        self.waypoint = Vector2(self.paths[self.path_idx][self.target_idx])
        self.heading = self.waypoint - self.pos
        vel = self.heading
        vel.scale_to_length(self.speed)
        self.vel = vel

        self.counter = 0
        self.shoot = False

        img_path = f"graphics/aliens/alien_{self.size}.png"
        self.image = pygame.image.load(os.path.join(curr_dir, img_path)).convert_alpha()
        self.rect = self.image.get_rect(center=self.pos)

    @classmethod
    def set_spawn_freq(cls, mu: float):
        cls.spawn_frequency = mu

    def update(self):
        self.pos += self.vel
        self.rect.center = self.pos
        # self.pos = wrap(self.pos, self.rect, buffer = 15)

        self.heading = self.waypoint - self.pos
        if self.heading.magnitude() <= self.eps:
            if self.target_idx < len(self.paths[self.path_idx]) - 1:
                self.target_idx += 1
            else: 
                self.kill()

            self.waypoint = self.paths[self.path_idx][self.target_idx] 
            self.heading = self.waypoint - self.pos
            vel = self.heading
            vel.scale_to_length(self.speed)
            self.vel = vel

        self.shoot = False
        self.counter += 1

        if self.counter == FPS:
            self.shoot = True
            self.counter = 0

def explosion_visual(pos, vel, duration, groups):
    explosion_sfx.play()
    for i in range(4):
        dir = random.uniform(0, 360)
        Bullet(pos, vel, dir, groups, life=duration, speed = 2)

def main():
    game_active = False
    post_game = False
    score = 0

    # Sprite Groups
    all_sprites = pygame.sprite.Group()
    asteroid_group = pygame.sprite.Group()
    alien_group = pygame.sprite.Group()
    player_bullet_group = pygame.sprite.Group()
    enemy_bullet_group = pygame.sprite.Group()
    lives_group = pygame.sprite.Group()

    # Object Creation
    player = Player(all_sprites)
    thrust = ThrustVisual(player, all_sprites)

    # UI
    font = pygame.font.Font(os.path.join(curr_dir, "font", "VectorBattle-e9XO.ttf"), 12)
    title_font = pygame.font.Font(os.path.join(curr_dir, "font", "VectorBattle-e9XO.ttf"), 48)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            
            if game_active:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        shoot_sfx.play()
                        player_bullet_group.add(Bullet(player.rect.center, player.vel, player.angle, [all_sprites, player_bullet_group]))
                    #if event.key == pygame.K_a:
                    #    player.lives -= 1
            else:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_d:
                    player.full_reset()
                    round = 0
                    score = 0
                    for i in range(player.lives):
                        LifeMeter((6+12*i, 30), player, i, (lives_group, all_sprites))
                    game_active = True

        screen.fill("Black")

        if game_active:
            # Update
            all_sprites.update()

            #check for player death
            if pygame.sprite.spritecollideany(player, asteroid_group) and not player.invulnerable:
                player.respawn()

            if pygame.sprite.spritecollideany(player, enemy_bullet_group) and not player.invulnerable:
                player.respawn()

            if player.lives < 0:
                for asteroid in asteroid_group:
                    asteroid.kill()
                for bullet in player_bullet_group:
                    bullet.kill()
                for bullet in enemy_bullet_group:
                    bullet.kill()
                for alien in alien_group:
                    alien.kill()
                game_over_sfx.play()
                game_active = False
                post_game = True


            if not asteroid_group:
                round += 1
                for i in range(round + 3):
                    x, y = 0, 0
                    if random.randint(0, 1):
                        # horzontal wall
                        x = random.uniform(0, 480)
                        y = -40
                    else:
                        # vertical wall
                        x = -40
                        y = random.uniform(0, 320)

                    speed = 1
                    dir = random.uniform(0, 2*math.pi)
                    vx, vy = polar_to_cartesian_radians(speed, dir)

                    asteroid_group.add(Asteroid((x, y), (vx, vy), 40, (asteroid_group, all_sprites)))

            mins_per_sec = 1/60
            if random.uniform() < Alien.spawn_frequency / FPS * mins_per_sec:
                if random.uniform() < 0.005*np.sqrt(score):
                    alien = Alien(2, (alien_group, all_sprites))
                else:
                    alien = Alien(1, (alien_group, all_sprites))

                alien_spawn_sfx.play()
                alien_group.add(alien)

            Alien.set_spawn_freq(0.04*np.sqrt(score+50**2))

            for alien in alien_group:
                if alien.shoot:
                    if alien.size == 1:
                        firing_angle = random.uniform(0, 360)
                        enemy_bullet_group.add(Bullet(alien.rect.center, alien.vel, firing_angle, [all_sprites, enemy_bullet_group]))
                    else:
                        dist, firing_angle = (alien.pos - player.pos).as_polar()
                        firing_angle = 90 - firing_angle # complementary angle
                        enemy_bullet_group.add(Bullet(alien.rect.center, (0, 0), firing_angle, [all_sprites, enemy_bullet_group], 25))

            # --- ALL COLLISION DETECTION ---
            # destroy collided bullets
            collisions = pygame.sprite.groupcollide(enemy_bullet_group, player_bullet_group, True, True)

            # player bullet hits asteroid
            collisions = pygame.sprite.groupcollide(player_bullet_group, asteroid_group, True, True)
            for bullet, asteroids in collisions.items():
                for asteroid in asteroids:
                    explosion_visual(asteroid.pos, asteroid.vel, duration=asteroid.size//2, groups=all_sprites)
                    if asteroid.size == 40:
                        score += 20
                        new_size = 20
                    elif asteroid.size == 20:
                        score += 50
                        new_size = 10
                    else:
                        score += 100
                        new_size = 0
                    
                    if new_size:
                        for i in range(2):
                            # random added velocity
                            speed = asteroid.vel.magnitude()
                            mag = random.uniform(-0.8*speed, 0.8*speed)
                            dir = random.uniform(0, 2*math.pi)
                            dx, dy = polar_to_cartesian_radians(mag, dir)
                            change = Vector2(dx, dy)

                            asteroid_group.add(Asteroid(asteroid.pos, asteroid.vel + change, new_size, [all_sprites, asteroid_group]))

            # player bullet hits alien saucer
            collisions = pygame.sprite.groupcollide(player_bullet_group, alien_group, True, True)
            for bullet, aliens in collisions.items():
                explosion_visual(alien.pos, alien.vel, duration=alien.rect.width//2, groups=all_sprites)
                for alien in aliens:
                    if alien.size == 1: score += 200
                    if alien.size == 2: score += 1000

            # alien bullet hits asteroid
            collisions = pygame.sprite.groupcollide(enemy_bullet_group, asteroid_group, True, True)
            for bullet, asteroids in collisions.items():
                for asteroid in asteroids:
                    explosion_visual(asteroid.pos, asteroid.vel, duration=asteroid.size//2, groups=all_sprites)
                    if asteroid.size == 40: new_size = 20
                    elif asteroid.size == 20: new_size = 10
                    else: new_size = 0
                    
                    if new_size:
                        for i in range(2):
                            # random added velocity
                            speed = asteroid.vel.magnitude()
                            mag = random.uniform(-0.8*speed, 0.8*speed)
                            dir = random.uniform(0, 2*math.pi)
                            dx, dy = polar_to_cartesian_radians(mag, dir)
                            change = Vector2(dx, dy)

                            asteroid_group.add(Asteroid(asteroid.pos, asteroid.vel + change, new_size, [all_sprites, asteroid_group]))

            # alien saucer hits asteroid
            collisions = pygame.sprite.groupcollide(alien_group, asteroid_group, True, True)
            for alien, asteroids in collisions.items():
                explosion_visual(alien.pos, alien.vel, duration=alien.rect.width//2, groups=all_sprites)
                for asteroid in asteroids:
                    explosion_visual(asteroid.pos, asteroid.vel, duration=asteroid.size//2, groups=all_sprites)
                    if asteroid.size == 40: new_size = 20
                    elif asteroid.size == 20: new_size = 10
                    else: new_size = 0
                    
                    if new_size:
                        for i in range(2):
                            # random added velocity
                            speed = asteroid.vel.magnitude()
                            mag = random.uniform(-0.8*speed, 0.8*speed)
                            dir = random.uniform(0, 2*math.pi)
                            dx, dy = polar_to_cartesian_radians(mag, dir)
                            change = Vector2(dx, dy)

                            asteroid_group.add(Asteroid(asteroid.pos, asteroid.vel + change, new_size, [all_sprites, asteroid_group]))

            
            # Draw
            all_sprites.draw(screen)
            
            # Score UI
            score_surf = font.render(f"{score}", False, "White")
            screen.blit(score_surf, (10, 10))

            # fps for debugging
            fps_surf = font.render(f"{clock.get_fps():.0f}", False, "White")
            screen.blit(fps_surf, (440, 10))

            # testing alien functionality
            #if alien:
            #    pygame.draw.circle(screen, "red", alien.waypoint, alien.eps)
            #    pygame.draw.line(screen, "red", alien.pos, alien.waypoint, 2)
        else:
            title_surf = title_font.render("ASTEROIDS", False, "White")
            start_surf = font.render("Press Enter to Start", False, "White")
            screen.blit(title_surf, title_surf.get_rect(center=(WIDTH/2, HEIGHT/3)))
            screen.blit(start_surf, start_surf.get_rect(center=(WIDTH/2, HEIGHT/2)))
            if post_game: 
                post_game_score_surf = font.render(f"Score: {score}", False, "White")
                screen.blit(post_game_score_surf, post_game_score_surf.get_rect(center=(WIDTH/2, HEIGHT*2/3)))

        pygame.display.update()
        clock.tick(FPS)

import cProfile as profile
profile.run('main()')

#if __name__ == "__main__":
#    main()
