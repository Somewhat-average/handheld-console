import pygame
from pathlib import Path
from dataclasses import dataclass
from typing import Callable, Union, Dict, Optional

# Windows
vert_padding = 10
hori_padding = 10
win_w = 480
win_h = 320
fps = 60

# Top bar size
tb_w = win_w
tb_h = 48

# Button bar size
bb_w = win_w
bb_h = 48

# Menu size
tag_w_incr = 10
tag_h = 20
tag_xoffset = 8
tag_yoffset = 5
menu_w = win_w - 2*hori_padding
menu_h = win_h - tb_h - bb_h - tag_h
item_h = 46

first_delay = 500
repeat_delay = 120

# Shutdown size
sd_w = 320
sd_h = 130
sdt_h = 60
sdm_w = 320
sdm_h = sd_h - sdt_h
sd_padding = 10
sd_item_w = 80

# Keyboard
name_h = 60
k_rows = 4
k_cols = int(40 / k_rows)
k_w = menu_w
k_cols_spc = 45
k_rows_spc = 30
k_h = 200 - name_h
keys_list = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') + ['SPC', 'DEL', 'CLR', 'OK']
keys = [[keys_list[i*k_cols + j] for j in range(k_cols)] for i in range(k_rows)]

# Font
project_root = Path(__file__).resolve().parent.parent
font_path = project_root / 'graphics' / 'Russo_One.ttf'
def get_font(size):
    return pygame.font.Font(str(font_path), size)

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

BG_COLOR = (18, 18, 24)
PANEL_COLOR = (28, 30, 40)
TEXT_COLOR = (235, 235, 240)
MUTED_TEXT = (170, 170, 180)
HIGHLIGHT = (80, 170, 255)
OVERLAY_BG = (0, 0, 0, 150)
DIVIDER = (55, 58, 70)