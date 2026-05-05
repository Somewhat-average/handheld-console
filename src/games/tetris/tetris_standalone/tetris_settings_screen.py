from ui.settings import *
from settings import *

from ui.base_screen import BaseScreen
from ui.menu import MenuItem, MenuList

class TetrisSettingsScreen(BaseScreen):
    def __init__(self, manager):
        
        # general
        super().__init__(manager)
        self.is_overlay = True
        self.tag = 'TetrisSettings'

        self.surf = pygame.Surface((p_w, p_h))
        self.rect = self.surf.get_rect(center = (win_w//2, win_h//2))
        self.disp_surf = pygame.display.get_surface()

        self.font = get_font(20)

        self.menu_surf = pygame.Surface((pm_w, pm_h))
        self.menu_rect = self.menu_surf.get_rect(topleft=(0, pt_h))

        self.sound_surf = pygame.Surface((pm_w, pm_h))
        self.sound_rect = self.sound_surf.get_rect(topleft=(0, self.menu_rect.bottom))

        # components
        self.menu = SettingsMenuList([
            MenuItem('Sound Volume', {'decr': self.sound_decr, 'incr': self.sound_incr}),
            MenuItem('Toggle Sound', self.tog_sound)
            ],
            self.menu_surf
            )
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.menu.move_down()
            elif event.key == pygame.K_UP:
                self.menu.move_up()
            elif event.key == pygame.K_LEFT and self.menu.selc_idx == 0:
                self.menu.activate('decr')
            elif event.key == pygame.K_RIGHT and self.menu.selc_idx == 0:
                self.menu.activate('incr')
            elif event.key == pygame.K_a and self.menu.selc_idx == 1:
                self.menu.activate()
            elif event.key == pygame.K_s:
                self.manager.go_back()
                self.menu.selc_idx = 0

    def sound_incr(self):
        if round(self.menu.sound_vol, 1) < 1:
            self.menu.sound_vol += 0.1
            self.menu.sound_vol = round(self.menu.sound_vol, 1)
        if self.menu.sound_en:
            pygame.mixer.music.set_volume(self.menu.sound_vol)
            self.manager.tag_links['Tetris'].sound.land_sound.set_volume(self.menu.sound_vol)

    def sound_decr(self):
        if round(self.menu.sound_vol, 1) > 0:
            self.menu.sound_vol -= 0.1
            self.menu.sound_vol = round(self.menu.sound_vol, 1)
        if self.menu.sound_en:
            pygame.mixer.music.set_volume(self.menu.sound_vol)
            self.manager.tag_links['Tetris'].sound.land_sound.set_volume(self.menu.sound_vol)

    def tog_sound(self):
        self.menu.sound_en = not self.menu.sound_en
        pygame.mixer.music.set_volume(self.menu.sound_vol if self.menu.sound_en else 0)
        self.manager.tag_links['Tetris'].sound.land_sound.set_volume(self.menu.sound_vol if self.menu.sound_en else 0)
    
    def draw(self):

        self.surf.fill(GRAY)
        text_surf = self.font.render('Settings', True, 'white')
        text_rect = text_surf.get_rect(center=(p_w/2, pt_h/2))

        # settings box
        self.menu.draw()
        self.surf.blit(self.menu_surf, self.menu_rect)
        self.surf.blit(self.sound_surf, self.sound_rect)
        self.surf.blit(text_surf, text_rect)
        self.disp_surf.blit(self.surf, self.rect.topleft)
        pygame.draw.rect(self.disp_surf, LINE_COLOR, self.rect, 2, 15)

class SettingsMenuList(MenuList):
    def __init__(self, items, disp_surf):
        
        # general
        self.surf = pygame.Surface((pm_w, pm_h))
        self.rect = self.surf.get_rect(topleft = (0,0))
        self.disp_surf = disp_surf
        self.font = get_font(15)

        self.sound_en = True
        self.sound_vol = bg_sound_vol

        self.items = items
        self.selc_idx = 0

    def draw(self):
        
        self.surf.fill(GRAY)

        # sound bar
        text_surf1 = self.font.render(self.items[0].label, True, 'white')
        text_rect1 = text_surf1.get_rect(topleft = (2*p_padding, p_padding))
        self.surf.blit(text_surf1, text_rect1)

        if self.selc_idx == 0:
            line_sound_color = 'white'
        else:
            line_sound_color = MUTED_TEXT

        pygame.draw.line(self.surf, line_sound_color, (text_rect1.right + 2*p_padding, text_rect1.centery), (pm_w - 3*p_padding, text_rect1.centery), 2)
        pygame.draw.line(self.surf, line_sound_color, (text_rect1.right + 2*p_padding, text_rect1.centery - 3), (text_rect1.right + 2*p_padding, text_rect1.centery + 3), 2)
        pygame.draw.line(self.surf, line_sound_color, (pm_w - 3*p_padding, text_rect1.centery - 3), (pm_w - 3*p_padding, text_rect1.centery + 3), 2)
        pygame.draw.circle(self.surf, line_sound_color, (text_rect1.right + 2*p_padding + self.sound_vol * (pm_w - 5*p_padding - text_rect1.right), text_rect1.centery + 1), 5, 5)

        # toggle music
        text_surf2 = self.font.render(self.items[1].label, True, 'white')
        text_rect2 = text_surf2.get_rect(topleft = (2*p_padding, text_rect1.height + 2*p_padding))
        self.surf.blit(text_surf2, text_rect2)
        
        if self.selc_idx == 1:
            text_color = 'white'
        else:
            text_color = MUTED_TEXT
            
        text_surf = self.font.render('On' if self.sound_en else 'Off', True, text_color)
        text_rect = text_surf.get_rect(center = (text_rect1.right + p_padding + 0.5 * (pm_w - 4*p_padding - text_rect1.right), text_rect2.centery))
        self.surf.blit(text_surf, text_rect)

        self.disp_surf.blit(self.surf, self.rect)