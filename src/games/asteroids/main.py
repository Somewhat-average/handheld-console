from games.asteroids.settings import *
from games.asteroids.classes import *

from ui.base_screen import BaseScreen

class AsteroidsScreen(BaseScreen):
    def __init__(self, manager):
        
        # general
        super().__init__(manager)
        self.tag = 'Asteroids'
        self.disp_surf = pygame.display.get_surface()
        self.clock = self.manager.app.clock
        self.game_active = False
        self.post_game = False
        self.score = 0

        # Sprite Groups
        self.all_sprites = pygame.sprite.Group()
        self.asteroid_group = pygame.sprite.Group()
        self.alien_group = pygame.sprite.Group()
        self.player_bullet_group = pygame.sprite.Group()
        self.enemy_bullet_group = pygame.sprite.Group()
        self.lives_group = pygame.sprite.Group()

        # Object Creation
        self.player = Player(self.all_sprites)
        self.thrust = ThrustVisual(self.player, self.all_sprites)

        # UI
        self.font = get_font(12)
        self.title_font = get_font(48)

    def update_controls(self):
        gpio = getattr(self.manager.app, "gpio", None)

        if gpio:
            left = gpio.is_pressed("Left")
            right = gpio.is_pressed("Right")
            up = gpio.is_pressed("Up")
        else:
            left = right = up = False

        self.player.set_controls(left=left, right=right, up=up)


    def clear_game_objects(self):
        for group in [
            self.asteroid_group,
            self.alien_group,
            self.player_bullet_group,
            self.enemy_bullet_group,
            self.lives_group
        ]:
            for sprite in group:
                sprite.kill()


    def start_game(self):
        self.clear_game_objects()
        self.player.full_reset()
        self.round = 0
        self.score = 0
        self.post_game = False

        for i in range(self.player.lives):
            LifeMeter(
                (6 + 12 * i, 30),
                self.player,
                i,
                (self.lives_group, self.all_sprites)
            )

        self.game_active = True


    def quit_game(self):
        self.clear_game_objects()
        self.game_active = False
        self.post_game = False
        self.score = 0
        self.player.set_controls(False, False, False)
        self.manager.go_back()


    def game_over(self):
        self.clear_game_objects()
        game_over_sfx.play()
        self.game_active = False
        self.post_game = True
        self.player.set_controls(False, False, False)
    
    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if self.game_active:
            if event.key == pygame.K_a:
                if player.can_shoot:
                    shoot_sfx.play()
                    self.player_bullet_group.add(
                        Bullet(
                            self.player.rect.center,
                            self.player.vel,
                            self.player.angle,
                            [self.all_sprites, self.player_bullet_group]
                        )
                    )

            elif event.key == pygame.K_s:
                self.quit_game()

            else:
                player.reset_shooting()

        else:
            if event.key == pygame.K_RETURN:
                self.start_game()

            elif event.key == pygame.K_s:
                self.quit_game()

    def draw(self):
            
        self.disp_surf.fill('black')

        if self.game_active:
            self.update_controls()

            # Update
            self.all_sprites.update()

            #check for player death
            if pygame.sprite.spritecollideany(self.player, self.asteroid_group) and not self.player.invulnerable:
                self.player.respawn()

            if pygame.sprite.spritecollideany(self.player, self.enemy_bullet_group) and not self.player.invulnerable:
                self.player.respawn()

            if self.player.lives < 0:
                self.game_over()
                return


            if not self.asteroid_group:
                self.round += 1
                for i in range(self.round + 3):
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

                    self.asteroid_group.add(Asteroid((x, y), (vx, vy), 40, (self.asteroid_group, self.all_sprites)))

            mins_per_sec = 1/60
            if random.uniform() < Alien.spawn_frequency / fps * mins_per_sec:
                if random.uniform() < 0.005*np.sqrt(self.score):
                    alien = Alien(2, (self.alien_group, self.all_sprites))
                else:
                    alien = Alien(1, (self.alien_group, self.all_sprites))

                alien_spawn_sfx.play()
                self.alien_group.add(alien)

            Alien.set_spawn_freq(0.04*np.sqrt(self.score+50**2))

            for alien in self.alien_group:
                if alien.shoot:
                    if alien.size == 1:
                        firing_angle = random.uniform(0, 360)
                        self.enemy_bullet_group.add(Bullet(alien.rect.center, alien.vel, firing_angle, [self.all_sprites, self.enemy_bullet_group]))
                    else:
                        dist, firing_angle = (alien.pos - self.player.pos).as_polar()
                        firing_angle = 90 - firing_angle # complementary angle
                        self.enemy_bullet_group.add(Bullet(alien.rect.center, (0, 0), firing_angle, [self.all_sprites, self.enemy_bullet_group], 25))

            # --- ALL COLLISION DETECTION ---
            # destroy collided bullets
            collisions = pygame.sprite.groupcollide(self.enemy_bullet_group, self.player_bullet_group, True, True)

            # player bullet hits asteroid
            collisions = pygame.sprite.groupcollide(self.player_bullet_group, self.asteroid_group, True, True)
            for bullet, asteroids in collisions.items():
                for asteroid in asteroids:
                    explosion_visual(asteroid.pos, asteroid.vel, duration=asteroid.size//2, groups=self.all_sprites)
                    if asteroid.size == 40:
                        self.score += 20
                        new_size = 20
                    elif asteroid.size == 20:
                        self.score += 50
                        new_size = 10
                    else:
                        self.score += 100
                        new_size = 0
                    
                    if new_size:
                        for i in range(2):
                            # random added velocity
                            speed = asteroid.vel.magnitude()
                            mag = random.uniform(-0.8*speed, 0.8*speed)
                            dir = random.uniform(0, 2*math.pi)
                            dx, dy = polar_to_cartesian_radians(mag, dir)
                            change = Vector2(dx, dy)

                            self.asteroid_group.add(Asteroid(asteroid.pos, asteroid.vel + change, new_size, [self.all_sprites, self.asteroid_group]))

            # player bullet hits alien saucer
            collisions = pygame.sprite.groupcollide(self.player_bullet_group, self.alien_group, True, True)
            for bullet, aliens in collisions.items():
                for alien in aliens:
                    explosion_visual(
                        alien.pos,
                        alien.vel,
                        duration=alien.rect.width // 2,
                        groups=self.all_sprites
                    )

                    if alien.size == 1:
                        self.score += 200
                    elif alien.size == 2:
                        self.score += 1000

            # alien bullet hits asteroid
            collisions = pygame.sprite.groupcollide(self.enemy_bullet_group, self.asteroid_group, True, True)
            for bullet, asteroids in collisions.items():
                for asteroid in asteroids:
                    explosion_visual(asteroid.pos, asteroid.vel, duration=asteroid.size//2, groups=self.all_sprites)
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

                            self.asteroid_group.add(Asteroid(asteroid.pos, asteroid.vel + change, new_size, [self.all_sprites, self.asteroid_group]))

            # alien saucer hits asteroid
            collisions = pygame.sprite.groupcollide(self.alien_group, self.asteroid_group, True, True)
            for alien, asteroids in collisions.items():
                explosion_visual(alien.pos, alien.vel, duration=alien.rect.width//2, groups=self.all_sprites)
                for asteroid in asteroids:
                    explosion_visual(asteroid.pos, asteroid.vel, duration=asteroid.size//2, groups=self.all_sprites)
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

                            self.asteroid_group.add(Asteroid(asteroid.pos, asteroid.vel + change, new_size, [self.all_sprites, self.asteroid_group]))

            
            # Draw
            self.all_sprites.draw(self.disp_surf)
            
            # Score UI
            score_surf = self.font.render(f"{self.score}", False, "White")
            self.disp_surf.blit(score_surf, (10, 10))

            # fps for debugging
            fps_surf = self.font.render(f"{self.clock.get_fps():.0f}", False, "White")
            self.disp_surf.blit(fps_surf, (440, 10))

        else:
            title_surf = self.title_font.render("ASTEROIDS", False, "White")
            start_surf = self.font.render("Press Start", False, "White")
            self.disp_surf.blit(title_surf, title_surf.get_rect(center=(win_w/2, win_h/3)))
            self.disp_surf.blit(start_surf, start_surf.get_rect(center=(win_w/2, win_h/2)))
            if self.post_game: 
                post_game_score_surf = self.font.render(f"Score: {self.score}", False, "White")
                self.disp_surf.blit(post_game_score_surf, post_game_score_surf.get_rect(center=(win_w/2, win_h*2/3)))

