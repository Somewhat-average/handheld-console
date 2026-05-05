from ui.settings import *

class ButtonBar:
    def __init__(self, selc_en = True, back_en = True):

        # general
        self.surf = pygame.Surface((bb_w, bb_h))
        self.rect = self.surf.get_rect(bottomleft = (0, win_h))
        self.disp_surf = pygame.display.get_surface()
        self.selc_en = selc_en
        self.back_en = back_en

        # font
        self.font = get_font(15)
    
    def draw(self):
        self.surf.fill(GRAY)

        if self.selc_en:
            text_surf1 = self.font.render(f'A: Select', True, MUTED_TEXT)
            text_rect1 = text_surf1.get_rect(center = (self.surf.get_width()/4, self.surf.get_height()/2))
            self.surf.blit(text_surf1, text_rect1)
        if self.back_en:
            text_surf2 = self.font.render(f'S: Back', True, MUTED_TEXT)
            text_rect2 = text_surf2.get_rect(center = (self.surf.get_width()*3/4, self.surf.get_height()/2))
            self.surf.blit(text_surf2, text_rect2)

        self.disp_surf.blit(self.surf, self.rect)