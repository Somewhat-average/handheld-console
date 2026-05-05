from ui.settings import *
import numpy as np

from dataclasses import dataclass
from typing import Callable, Union

@dataclass
class MenuItem:
    label: str
    action: Union[Callable, dict[str: Callable]]
    enabled: bool = True
    

class MenuList:
    def __init__(self, items):
        
        # general
        self.surf = pygame.Surface((menu_w, menu_h))
        self.rect = self.surf.get_rect(topleft = (hori_padding, tb_h+tag_h))
        self.disp_surf = pygame.display.get_surface()
        self.font = get_font(15)

        self.items = items
        self.selc_idx = 0

    def move_up(self):
        if not self.selc_idx == 0:
            self.selc_idx -= 1

    def move_down(self):
        if not self.selc_idx == len(self.items) - 1:
            self.selc_idx += 1

    def activate(self, key=None):
        item = self.items[self.selc_idx]
        if item.enabled:
            if isinstance(item.action, dict):
                action = item.action[key]
            else:
                action = item.action
            if action:
                action()

    def draw_equi_tria(self, center_pos, side_len):
        v1 = (center_pos[0] - side_len*np.sqrt(3)/4, center_pos[1] - side_len/2)
        v2 = (center_pos[0] - side_len*np.sqrt(3)/4, center_pos[1] + side_len/2)
        v3 = (center_pos[0] + side_len*np.sqrt(3)/4, center_pos[1])
        pygame.draw.polygon(self.surf, LINE_COLOR, [v1, v2, v3])

    def draw(self):
        
        self.surf.fill(GRAY)
        for idx, item in enumerate(self.items):
            
            rect = pygame.Rect(hori_padding, vert_padding*3/2 + idx * item_h, menu_w-2*hori_padding, item_h - vert_padding)
            
            if not item.enabled:
                text_color = MUTED_TEXT
                text_x = 2 * hori_padding
            elif idx == self.selc_idx:
                pygame.draw.rect(self.surf, LINE_COLOR, rect, 2, 2)
                self.draw_equi_tria((3 * hori_padding, rect.center[1]), 15)
                text_color = 'white'
                text_x = 5 * hori_padding
            else:
                text_color = MUTED_TEXT
                text_x = 2 * hori_padding
            
            text_surf = self.font.render(item.label, True, text_color)
            text_rect = text_surf.get_rect(midleft = (text_x, rect.center[1]))
            self.surf.blit(text_surf, text_rect)

        self.disp_surf.blit(self.surf, self.rect)
        pygame.draw.rect(self.disp_surf, LINE_COLOR, self.rect, 2, 2)