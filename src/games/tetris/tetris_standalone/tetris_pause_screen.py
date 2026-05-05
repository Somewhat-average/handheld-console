from ui.settings import *
from settings import *

from ui.base_screen import BaseScreen
from ui.menu import MenuItem, MenuList

class TetrisPauseScreen(BaseScreen):
    def __init__(self, manager):
        
        # general
        super().__init__(manager)
        self.is_overlay = True
        self.tag = 'TetrisPause'

        self.surf = pygame.Surface((p_w, p_h))
        self.rect = self.surf.get_rect(center = (win_w//2, win_h//2))
        self.disp_surf = pygame.display.get_surface()

        self.font = get_font(20)

        self.menu_surf = pygame.Surface((pm_w, pm_h))
        self.menu_rect = self.menu_surf.get_rect(topleft=(0, pt_h))

        # components
        self.menu = PauseMenuList([
            MenuItem('Resume', self.resume),
            MenuItem('Restart', self.restart),
            MenuItem('Settings', self.settings),
            MenuItem('Quit', self.quit)
            ],
            self.menu_surf
            )
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.menu.move_down()
            elif event.key == pygame.K_UP:
                self.menu.move_up()
            elif event.key == pygame.K_a:
                self.menu.activate()

    def resume(self):
        self.manager.go_back()

    def restart(self):
        self.manager.go_back()
        self.menu.selc_idx = 0
        self.manager.stack[-1].restart()

    def settings(self):
        self.manager.push('TetrisSettings')

    def quit(self):
        self.manager.app.running = False
    
    def draw(self):

        self.surf.fill(GRAY)
        text_surf = self.font.render('Paused', True, 'white')
        text_rect = text_surf.get_rect(center=(p_w/2, pt_h/2))

        # pause box
        self.menu.draw()
        self.surf.blit(self.menu_surf, self.menu_rect)
        self.surf.blit(text_surf, text_rect)
        self.disp_surf.blit(self.surf, self.rect.topleft)
        pygame.draw.rect(self.disp_surf, LINE_COLOR, self.rect, 2, 15)

class PauseMenuList(MenuList):
    def __init__(self, items, disp_surf):
        
        # general
        self.surf = pygame.Surface((pm_w, pm_h))
        self.rect = self.surf.get_rect(topleft = (0,0))
        self.disp_surf = disp_surf
        self.font = get_font(15)

        self.items = items
        self.selc_idx = 0

    def draw(self):
        
        self.surf.fill(GRAY)
        for idx, item in enumerate(self.items):
            
            rect = pygame.Rect(5*p_padding, idx * item_h, pm_w-10*p_padding, item_h - p_padding/2)
            
            if idx == self.selc_idx:
                pygame.draw.rect(self.surf, LINE_COLOR, rect, 2, 2)
                text_color = 'white'
            else:
                pygame.draw.rect(self.surf, MUTED_TEXT, rect, 2, 2)
                text_color = MUTED_TEXT
            
            text_surf = self.font.render(item.label, True, text_color)
            text_rect = text_surf.get_rect(center = (pm_w/2, rect.center[1]))
            self.surf.blit(text_surf, text_rect)

        self.disp_surf.blit(self.surf, self.rect)