from settings import *
from pygame.image import load

class Preview:
    def __init__(self):

        # general
        self.surf = pygame.Surface((sb_w, g_h * preview_h_frac))
        self.rect = self.surf.get_rect(topright = (win_w - hori_padding, vert_padding))
        self.disp_surf = pygame.display.get_surface()

        # font
        self.font = get_font(15)

        # shapes
        scale_factor = cell_sz / 45
        self.shape_surfs = {}
        for shape in TETROMINOES.keys():
            surf = load(get_shape_path(shape)).convert_alpha()
            w, h = surf.get_size()
            new_size = (int(w * scale_factor), int(h * scale_factor))
            self.shape_surfs[shape] = pygame.transform.smoothscale(surf, new_size)

        # image position data
        self.text_surf = self.font.render('Next', True, 'white')
        self.text_rect = self.text_surf.get_rect(midtop=(self.surf.get_width() / 2, vert_padding/2))
        self.incr_h = (self.surf.get_height() - self.text_rect.bottom - vert_padding/2) / 3

    def disp_pieces(self, shapes):

        self.surf.blit(self.text_surf, self.text_rect)

        for idx, shape in enumerate(shapes):
            shape_surf = self.shape_surfs[shape]
            x = self.surf.get_width() / 2
            y = self.text_rect.bottom + self.incr_h / 2 + idx * self.incr_h
            rect = shape_surf.get_rect(center = (x, y))
            self.surf.blit(shape_surf, rect)
    
    def run(self, next_shapes):
        self.surf.fill(GRAY)
        self.disp_pieces(next_shapes)   
        self.disp_surf.blit(self.surf, self.rect)
        pygame.draw.rect(self.disp_surf, LINE_COLOR, self.rect, 2, 2)