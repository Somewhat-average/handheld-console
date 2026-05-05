from games.tetris.settings import *

from ui.menu import MenuItem, MenuList

class Pause:
    def __init__(self):

        # general
        self.surf = pygame.Surface((p_w, p_h))
        self.disp_surf = pygame.display.get_surface()
        self.rect = self.surf.get_rect(center = (win_w//2, win_h//2))
        
        self.font = get_font(20)
        
        self.menu_surf = pygame.Surface((pm_w, pm_h))
        self.menu_rect = self.menu_surf.get_rect(topleft=(0, pt_h))

        self.menu = PauseMenuList([
            MenuItem('Resume', self.resume),
            MenuItem('Restart', self.restart),
            MenuItem('Quit', self.quit),
            ],
            self.menu_surf
            )

        # pause overlay
        self.overlay = pygame.Surface((win_w, win_h), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 120))

    def handle_event(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.menu.move_down()
                elif event.key == pygame.K_UP:
                    self.menu.move_up()
                elif event.key == pygame.K_a:
                    self.menu.activate()

    def resume(self):
        pass

    def restart(self):
        pass

    def quit(self):
        pass
    
    def run(self):

        self.handle_event()

        self.disp_surf.blit(self.overlay, (0, 0))
        self.surf.fill(GRAY)
        text_surf = self.font.render('Paused', True, 'white')
        text_rect = text_surf.get_rect(center=(p_w/2, pt_h/2))

        # pause box
        self.menu.draw()
        self.surf.blit(self.menu_surf, self.menu_rect)
        self.surf.blit(text_surf, text_rect)
        self.disp_surf.blit(self.surf, self.rect.topleft)
        pygame.draw.rect(self.disp_surf, LINE_COLOR, self.rect, 2, 2)

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
            
            rect = pygame.Rect(p_padding, idx * item_h, pm_w-2*p_padding, item_h - p_padding/2)
            
            if idx == self.selc_idx:
                pygame.draw.rect(self.surf, LINE_COLOR, rect, 2, 2)
                self.draw_equi_tria((3*p_padding, rect.center[1]), 10)
                text_color = 'white'
                text_x = 5*p_padding
            else:
                text_color = MUTED_TEXT
                text_x = 2*p_padding
            
            text_surf = self.font.render(item.label, True, text_color)
            text_rect = text_surf.get_rect(midleft = (text_x, rect.center[1]))
            self.surf.blit(text_surf, text_rect)

        self.disp_surf.blit(self.surf, self.rect)