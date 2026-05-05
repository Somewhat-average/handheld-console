import pygame
import math
import random
from sys import exit

class Game:

    def __init__(self):
        self.done = False
        self.screen_width = 480
        self.screen_height = 320
        self.image = pygame.Surface((self.screen_width, self.screen_height))
        self.image.fill((0, 0, 0))
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))

        # all_sprites is used to update and draw all sprites together.
        self.all_sprites = pygame.sprite.Group()
        # You'll probably need a separate bullet_group
        # later for collision detection with enemies.
        self.bullet_group = pygame.sprite.Group()

        self.ship = Ship()
        self.all_sprites.add(self.ship)

    def handle_events(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.ship.rect.centerx -= 5
        if keys[pygame.K_RIGHT]:
            self.ship.rect.centerx += 5
        if keys[pygame.K_UP]:
            self.ship.rect.centery -= 5
        if keys[pygame.K_DOWN]:
            self.ship.rect.centery += 5

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.done = True
                if event.key == pygame.K_SPACE:
                    bullet = Bullet(self.ship)
                    self.bullet_group.add(bullet)
                    self.all_sprites.add(bullet)

    def update(self):
        # Calls `update` methods of all contained sprites.
        self.all_sprites.update()

    def draw(self):
        self.screen.blit(self.image, (0, 0))
        self.all_sprites.draw(self.screen)  # Draw the contained sprites.
        pygame.display.update()


class Ship(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("graphics/player/player.png").convert_alpha()
        self.rect = self.image.get_rect(center = (480/2, 320/2))


class Bullet(pygame.sprite.Sprite):
    __speed = 5

    def __init__(self, ship):
        super().__init__(self)
        self.image = pygame.Surface((7, 7))
        self.image.fill((230, 140, 30))
        self.rect = self.image.get_rect()
        self.rect.centerx = ship.rect.centerx
        self.rect.centery = ship.rect.centery - 25

    def update(self):
        self.rect.y -= 5  # Move up 5 pixels per frame.

    def __init__(self, pos: [float, float], v_0: [float, float], dir: float):
        self.__life = 60 # ticks until despawn
        self.__pos = list(pos)
        self.__vel = list(polarToCartesian(Bullet.__speed, dir))[::-1]
        self.__vel = [x + y for x, y in zip(self.__vel, list(v_0))]

    def correct_out_of_bounds(self):
        if self.__pos[0] > width:
            self.__pos[0] = 0
        elif self.__pos[0] < 0:
            self.__pos[0] = width
        if self.__pos[1] > height:
            self.__pos[1] = 0
        elif self.__pos[1] < 0:
            self.__pos[1] = height

    def update(self):
        self.__pos[0] -= self.__vel[0]
        self.__pos[1] -= self.__vel[1]
        self.correct_out_of_bounds()
        self.__life -= 1

    def despawn(self) -> bool:
        if self.__life <= 0:
            return True
        if self.__pos[0] < 2 or self.__pos[0] > width - 2:
            return True

        return False


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Space Game')
    clock = pygame.time.Clock()
    game = Game()

    while not game.done:
        game.handle_events()
        game.update()
        game.draw()
        clock.tick(30)

    pygame.quit()
    exit()

