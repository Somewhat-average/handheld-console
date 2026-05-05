from ui.settings import *

from games.tetris.timer_class import Timer

class Keyboard:
    def __init__(self, screen, len_lim):
        
        # general
        self.surf = pygame.Surface((k_w, k_h))
        self.rect = self.surf.get_rect(topleft = (hori_padding, tb_h + tag_h + name_h))
        self.disp_surf = pygame.display.get_surface()
        self.screen = screen
        self.manager = screen.manager
        self.len_lim = len_lim
        self.font = get_font(15)

        self.selc_idx = [0,0]
        self.text = self.screen.text

        # timer
        self.blink = True
        self.timer = Timer(1000, True, self.blinking)
        self.timer.activate()

    def move_up(self):
        if not self.selc_idx[0] == 0:
            self.selc_idx[0] -= 1

    def move_down(self):
        if not self.selc_idx[0] == k_rows - 1:
            self.selc_idx[0] += 1

    def move_left(self):
        if not self.selc_idx[1] == 0:
            self.selc_idx[1] -= 1

    def move_right(self):
        if not self.selc_idx[1] == k_cols - 1:
            self.selc_idx[1] += 1

    def activate(self):
        key = keys[self.selc_idx[0]][self.selc_idx[1]]

        if key == 'DEL':
            self.text = self.text[:-1]
            return None

        elif key == 'CLR':
            self.text = ''
            return None

        elif key == 'OK':
            self.screen.text = self.text
            return "ok"

        elif key == 'SPC':
            if len(self.text) < self.len_lim:
                if hasattr(self.screen, 'mode'):
                    if self.screen.mode == 'tcp':
                        self.text += '.'
                    elif self.screen.mode == 'bluetooth':
                        self.text += ':'
                    else:
                        self.text += ' '
                else:
                    self.text += ' '
            return None

        else:
            if len(self.text) < self.len_lim:
                self.text += key
            return None

    def blinking(self):
        self.blink = not self.blink

    def get_key_label(self, key):
        if key == 'SPC':
            if hasattr(self.screen, 'mode'):
                if self.screen.mode == 'tcp':
                    return '.'
                elif self.screen.mode == 'bluetooth':
                    return ':'
            return 'SPC'
        return key

    def draw(self):
        
        self.surf.fill(GRAY)

        for i in range(k_rows):
            for j in range(k_cols):
                is_selected = [i, j] == self.selc_idx

                key = keys[i][j]
                label = self.get_key_label(key)
                key_surf = self.font.render(label, True, 'black' if is_selected else MUTED_TEXT)
                key_rect = key_surf.get_rect()

                rect = pygame.Rect(0,0,key_rect.width + 10,key_rect.height + 10)
                rect.center = (25 + j*k_cols_spc, 25 + i*k_rows_spc)
                
                if is_selected:
                    pygame.draw.rect(self.surf, LINE_COLOR, rect, 0, 2)
                
                key_rect.center = rect.center
                self.surf.blit(key_surf, key_rect)
                
        self.disp_surf.blit(self.surf, self.rect)
        pygame.draw.rect(self.disp_surf, LINE_COLOR, self.rect, 2, 2)