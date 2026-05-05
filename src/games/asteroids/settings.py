import pygame
from pygame.math import Vector2
import math
import numpy as np
import numpy.random as random
from pathlib import Path

# Get paths
project_root = Path(__file__).resolve().parent.parent.parent.parent
font_path = project_root / 'assets' / 'asteroids' / 'font' / 'VectorBattle-e9XO.ttf'
def get_font(size):
    return pygame.font.Font(str(font_path), size)

def get_graphic_path(folder, graphic):
    return project_root / 'assets' / 'asteroids' / 'graphics' / folder / f'{graphic}.png'

def get_sound_path(sound):
    return project_root / 'assets' / 'asteroids' / 'audio' / f'{sound}.wav'

#initialization
pygame.init()
explosion_sfx = pygame.mixer.Sound(get_sound_path('explosion'))
game_over_sfx = pygame.mixer.Sound(get_sound_path('game_over'))
die_sfx = pygame.mixer.Sound(get_sound_path('die'))
shoot_sfx = pygame.mixer.Sound(get_sound_path('shoot'))
alien_spawn_sfx = pygame.mixer.Sound(get_sound_path('alien_spawn'))