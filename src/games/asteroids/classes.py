from ui.settings import *
from games.asteroids.settings import *

def polar_to_cartesian_degrees(magnitude, angle):
    rad = math.radians(angle)
    return magnitude * math.cos(rad), magnitude * math.sin(rad)

def polar_to_cartesian_radians(magnitude, angle):
    return magnitude * math.cos(angle), magnitude * math.sin(angle)

def wrap(pos: Vector2, rect: pygame.Rect, buffer: int = 0) -> Vector2:
    half_width = rect.width//2
    half_height = rect.height//2
    if pos.x > win_w + half_width + buffer: pos.x = 0 - rect.width//2
    if pos.x < -half_width - buffer: pos.x = win_w + rect.width//2
    if pos.y > win_h + half_height + buffer: pos.y = 0 - rect.height//2
    if pos.y < -half_height - buffer: pos.y = win_h + rect.height//2
    return pos

def explosion_visual(pos, vel, duration, groups):
    explosion_sfx.play()
    for i in range(4):
        dir = random.uniform(0, 360)
        Bullet(pos, vel, dir, groups, life=duration, speed = 2)

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        # Load images
        self.original_surf = pygame.image.load(get_graphic_path('player', 'player')).convert_alpha()
        
        self.image = self.original_surf
        self.rect = self.image.get_rect(center=(win_w/2, win_h/2))
        
        # Physics
        self.pos = Vector2(win_w/2, win_h/2)
        self.vel = Vector2(0, 0)
        self.drag = 0.016
        self.thrust_force = 0.05
        self.turn_speed = 5
        self.angle = 0

        self.__frames_per_bullet = 30
        self.__bullet_timer = 1
        self.__can_shoot = True
        
        self.lives = 3
        self.invulnerable = False
        self.invulnerable_start = 0
        self.show_thrust = False

    @property
    def can_shoot(self):
        self.__bullet_timer -= 1
        if self.__bullet_timer == 0:
            self.__can_shoot = True
            self.__bullet_timer = self.__frames_per_bullet
        else:
            self.__can_shoot = False

        return self.__can_shoot

    def reset_shooting(self):
        self.__bullet_timer = 1

    def state_reset(self):
        self.pos = Vector2(win_w/2, win_h/2)
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
        self.original_surf = pygame.image.load(get_graphic_path('player', 'thrust')).convert_alpha()
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
        self.image = pygame.image.load(get_graphic_path('player', 'life_icon'))
        self.rect = self.image.get_rect(topleft = pos)
        self.condition = condition
        self.player = player

    def update(self):
        if self.player.lives <= self.condition:
            self.kill()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, shooter_vel, angle, groups, life = 50, speed = 5):
        super().__init__(groups)

        self.image = pygame.image.load(get_graphic_path('player', 'bullet')).convert_alpha()
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

        path = get_graphic_path(f'asteroids/{size}', f'asteroid_{type_idx}')
        self.image = pygame.image.load(path).convert_alpha()
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

        img_path = get_graphic_path('aliens', f'alien_{self.size}')
        self.image = pygame.image.load(img_path).convert_alpha()
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

        if self.counter == fps:
            self.shoot = True
            self.counter = 0
