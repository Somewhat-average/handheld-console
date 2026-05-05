from ui.settings import *
from settings import *

from tetris_pause_screen import TetrisPauseScreen, PauseMenuList
from ui.menu import MenuItem

class TetrisGameOverScreen(TetrisPauseScreen):
    def __init__(self, manager):
        
        # general
        super().__init__(manager)
        self.tag = 'TetrisGameOver'

        self.surf = pygame.Surface((go_w, go_h))
        self.rect = self.surf.get_rect(center = (win_w//2, win_h//2))
        self.disp_surf = pygame.display.get_surface()

        self.menu_surf = pygame.Surface((gom_w, gom_h))
        self.menu_rect = self.menu_surf.get_rect(topleft=(0, got_h))

        # components
        self.menu = PauseMenuList([
            MenuItem('Restart', self.restart),
            MenuItem('Quit', self.quit)
            ],
            self.menu_surf
            )
        
    def draw(self):

        self.surf.fill(GRAY)
        text_surf = self.font.render('Game Over', True, 'white')
        text_rect = text_surf.get_rect(center=(go_w/2, got_h/2))

        # game over box
        self.menu.draw()
        self.surf.blit(self.menu_surf, self.menu_rect)
        self.surf.blit(text_surf, text_rect)
        self.disp_surf.blit(self.surf, self.rect.topleft)
        pygame.draw.rect(self.disp_surf, LINE_COLOR, self.rect, 2, 15)