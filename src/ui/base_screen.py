from ui.settings import *

class BaseScreen:
    def __init__(self, manager):
        self.manager = manager
        self.is_overlay = False
        self.tagbar = TagBar()

    def handle_event(self, event):
        pass

    def draw_tags(self):
        self.tagbar.draw(self.manager.tag_history)

    def draw(self, surf):
        pass

class TagBar:
    def __init__(self):

        # general
        self.disp_surf = pygame.display.get_surface()
        self.font = get_font(15)

    def draw(self, tags):
        
        tag_x = hori_padding

        for idx, tag in enumerate(tags):
            if idx ==  len(tags) - 1:
                text_color = 'white'
            else:
                text_color = MUTED_TEXT

            text_surf = self.font.render(tag, True, text_color)
            text_rect = text_surf.get_rect()
            tag_w = text_rect.width + 2*tag_w_incr
            text_rect.center = (tag_w/2, tag_h/2)

            tag_surf = pygame.Surface((tag_w, tag_h + tag_yoffset))
            tag_rect = tag_surf.get_rect(topleft = (tag_x, tb_h))
            tag_x = tag_rect.right - tag_xoffset

            tag_surf.fill(GRAY)
            tag_surf.blit(text_surf, text_rect)

            self.disp_surf.blit(tag_surf, tag_rect)
            pygame.draw.rect(self.disp_surf, text_color, tag_rect, 2, 2)