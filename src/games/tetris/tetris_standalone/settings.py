import pygame
from pathlib import Path

# Game size
cols = 10
rows = 20
cell_sz = 15
g_w, g_h = cols * cell_sz, rows * cell_sz

# Windows
vert_padding = 10
hori_padding = 85
# win_w = g_w + sb_w + 3 * padding
win_w = 480
win_h = g_h + 2 * vert_padding

# Sidebar size
sb_w = 150
preview_h_frac = 0.7
score_h_frac = 1 - preview_h_frac

# Pause windows
p_w = 255
p_h = 170
pt_h = 45
pm_w = p_w
pm_h = p_h - pt_h
item_h = 30
p_padding = 10

# Game over windows
go_w = 255
go_h = 120
got_h = 45
gom_w = go_w
gom_h = go_h - got_h

# Game behavior
update_start_speed = 800
update_start_speed_fast_perc = 0.1
level_down_speed_perc = 0.75
move_wait_time = 200
rotate_wait_time = 200
block_offset = pygame.Vector2(cols // 2, 0)
bg_sound_vol = round(0.09, 1)

# Get paths
project_root = Path(__file__).resolve().parent
font_path = project_root / 'graphics' / 'Russo_One.ttf'
def get_font(size):
    return pygame.font.Font(str(font_path), size)

def get_shape_path(shape):
    return project_root / 'graphics' / f'{shape}.png'

def get_sound_path(sound):
    return project_root / 'sound' / f'{sound}.wav'

# Colors
YELLOW = '#f1e60d'
RED = '#e51b20'
BLUE = '#204b9b'
GREEN = '#65b32e'
PURPLE = '#7b217f'
CYAN = '#6cc6d9'
ORANGE = '#f07e13'
GRAY = '#1C1C1C'
LINE_COLOR = '#FFFFFF'
MUTED_TEXT = (170, 170, 180)

# Shapes
TETROMINOES = {
    'T': {'shape' : [(0, 0), (-1, 0), (1, 0), (0, -1)], 'color' : PURPLE},
    'O': {'shape' : [(0, 0), (0, -1), (1, 0), (1, -1)], 'color' : YELLOW},
    'J': {'shape' : [(0, 0), (0, -1), (0, 1), (-1, 1)], 'color' : BLUE},
    'L': {'shape' : [(0, 0), (0, -1), (0, 1), (1, 1)], 'color' : ORANGE},
    'I': {'shape' : [(0, 0), (0, -1), (0, -2), (0, 1)], 'color' : CYAN},
    'S': {'shape' : [(0, 0), (-1, 0), (0, -1), (1, -1)], 'color' : GREEN},
    'Z': {'shape' : [(0, 0), (1, 0), (0, -1), (-1, -1)], 'color' : RED}
}

score_data = {1: 40, 2: 100, 3: 300, 4: 1200}