from ui.settings import *

from ui.base_screen import BaseScreen
from ui.buttonbar import ButtonBar
from ui.keyboard import Keyboard

class DevNameScreen(BaseScreen):
    def __init__(self, manager):
        
        # general
        super().__init__(manager)
        self.tag = 'DevName'
        self.disp_surf = pygame.display.get_surface()
        self.text = 'DEV1'
        self.font = get_font(15)
        self.title_font = get_font(20)

        # components
        self.keyboard = Keyboard(self, 15)
        self.butbar = ButtonBar()
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.keyboard.move_up()
            elif event.key == pygame.K_DOWN:
                self.keyboard.move_down()
            elif event.key == pygame.K_LEFT:
                self.keyboard.move_left()
            elif event.key == pygame.K_RIGHT:
                self.keyboard.move_right()
            elif event.key == pygame.K_a:
                self.keyboard.activate()
            elif event.key == pygame.K_s:
                self.manager.go_back()
                self.keyboard.selc_idx = [0,0]
                self.keyboard.text = self.text

    def draw_text(self):
        self.keyboard.timer.update()

        text_surf = self.font.render(self.keyboard.text, True, 'white')
        text_rect = text_surf.get_rect(center=(win_w / 2, tb_h + name_h / 2))
        self.disp_surf.blit(text_surf, text_rect)

        name_frame = pygame.Rect(0, 0, win_w - 4 * hori_padding, name_h)
        name_frame.center = text_rect.center
        pygame.draw.rect(self.disp_surf, LINE_COLOR, name_frame, 1, 2)

        if self.keyboard.blink:
            curs_surf = self.font.render('_', True, 'white')
            curs_rect = curs_surf.get_rect()
            curs_rect.midleft = text_rect.midright
            self.disp_surf.blit(curs_surf, curs_rect)

    def draw(self):
        self.disp_surf.fill(GRAY)

        text_surf = self.title_font.render('Device name', True, 'white')
        text_rect = text_surf.get_rect(center=(win_w/2, 2*vert_padding))
        self.disp_surf.blit(text_surf, text_rect)

        self.draw_text()
        self.keyboard.draw()
        self.butbar.draw()