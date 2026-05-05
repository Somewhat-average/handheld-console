from ui.settings import *

from ui.base_screen import BaseScreen
from ui.menu import MenuItem, MenuList

class ShutdownScreen(BaseScreen):
    def __init__(self, manager):
        
        # general
        super().__init__(manager)
        self.is_overlay = True
        self.tag = 'Shutdown'

        self.surf = pygame.Surface((sd_w, sd_h))
        self.rect = self.surf.get_rect(center = (win_w//2, win_h//2))
        self.disp_surf = pygame.display.get_surface()

        self.font = get_font(20)

        self.menu_surf = pygame.Surface((sdm_w, sdm_h))
        self.menu_rect = self.menu_surf.get_rect(topleft=(0, sdt_h))

        # components
        self.menu = ShutdownMenuList([
            MenuItem('Cancel', self.cancel),
            MenuItem('Confirm', self.confirm)
            ],
            self.menu_surf
            )
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.menu.move_down()
            elif event.key == pygame.K_LEFT:
                self.menu.move_up()
            elif event.key == pygame.K_a:
                self.menu.activate()

    def cancel(self):
        self.manager.go_back()

    def confirm(self):
        self.manager.app.running = False
    
    def draw(self):

        # self.disp_surf.fill(GRAY)

        self.surf.fill(GRAY)
        text_surf = self.font.render('Shutdown console?', True, 'white')
        text_rect = text_surf.get_rect(center=(sd_w/2, sdt_h/2))

        # pause box
        self.menu.draw()
        self.surf.blit(self.menu_surf, self.menu_rect)
        self.surf.blit(text_surf, text_rect)
        self.disp_surf.blit(self.surf, self.rect.topleft)
        pygame.draw.rect(self.disp_surf, LINE_COLOR, self.rect, 2, 15)

class ShutdownMenuList(MenuList):
    def __init__(self, items, disp_surf):
        
        # general
        self.surf = pygame.Surface((sdm_w, sdm_h))
        self.rect = self.surf.get_rect(topleft = (0,0))
        self.disp_surf = disp_surf
        self.font = get_font(15)

        self.items = items
        self.selc_idx = 0

    def draw(self):
        
        self.surf.fill(GRAY)
        for idx, item in enumerate(self.items):
            
            rect = pygame.Rect(sdm_w*(2*idx + 1)/4 - sd_item_w/2, 0, sd_item_w, item_h)
            
            if idx == self.selc_idx:
                pygame.draw.rect(self.surf, LINE_COLOR, rect, 2, 2)
                text_color = 'white'
            else:
                pygame.draw.rect(self.surf, MUTED_TEXT, rect, 2, 2)
                text_color = MUTED_TEXT
            
            text_surf = self.font.render(item.label, True, text_color)
            text_rect = text_surf.get_rect(center = rect.center)
            self.surf.blit(text_surf, text_rect)

        self.disp_surf.blit(self.surf, self.rect)