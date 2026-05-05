from games.tetris.settings import *

class Score:
    def __init__(self):
        self.surf = pygame.Surface((sb_w, g_h * score_h_frac - vert_padding))
        self.rect = self.surf.get_rect(bottomright = (win_w - hori_padding, win_h - vert_padding))
        self.disp_surf = pygame.display.get_surface()

        # font
        self.font = get_font(15)

        # increment
        self.incr_h =self.surf.get_height() / 3

        # data
        self.score = 0
        self.level = 1
        self.lines = 0

    def disp_text(self, pos, text):
        text_surf = self.font.render(f'{text[0]}: {text[1]}', True, 'white')
        text_rect = text_surf.get_rect(center = pos)
        self.surf.blit(text_surf, text_rect)

    def run(self):

        self.surf.fill(GRAY)
        for idx, text in enumerate([('Score', self.score), ('Level', self.level), ('Lines', self.lines)]):
            x = self.surf.get_width() / 2
            y = self.incr_h / 2 + idx * self.incr_h
            self.disp_text((x, y), text)

        self.disp_surf.blit(self.surf, self.rect)
        pygame.draw.rect(self.disp_surf, LINE_COLOR, self.rect, 2, 2)