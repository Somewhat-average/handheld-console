from ui.settings import *
import socket
import re

from ui.base_screen import BaseScreen
from ui.keyboard import Keyboard

class ConnectScreen(BaseScreen):
    def __init__(self, manager):
        
        # general
        super().__init__(manager)
        self.tag = 'Connect'
        self.disp_surf = pygame.display.get_surface()
        self.font = get_font(15)
        self.title_font = get_font(20)

        self.text = ''
        self.ok_locked = False
        self.error_msg = ""

        self.keyboard = Keyboard(self, len_lim=17)
        self.keyboard.rect.bottom = win_h - vert_padding

    @property
    def mode(self):
        return self.manager.comm.mode

    @property
    def port(self):
        return 4 if self.mode == "bluetooth" else 5555
    
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
                if not self.ok_locked:
                    self.ok_locked = True
                    result = self.keyboard.activate()
                    if result == "ok":
                        self.connect()
                    else:
                        self.ok_locked = False

            elif event.key == pygame.K_s:
                if not self.manager.comm.connecting:
                    self.ok_locked = False
                    self.keyboard.selc_idx = [0, 0]
                    self.keyboard.text = self.text
                    self.manager.go_back()

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                self.ok_locked = False
    
    def parse_addr(self, text):
        text = text.strip()

        if self.mode == "tcp":
            try:
                socket.inet_aton(text)
                return text
            except OSError:
                return None

        if self.mode == "bluetooth":
            if re.fullmatch(r"([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}", text):
                return text.upper()
            return None

        return None
    
    def connect(self):
        host = self.parse_addr(self.keyboard.text)
        if not host:
            self.error_msg = "Invalid address"
            self.ok_locked = False
            return

        ok = self.manager.comm.connect_to_peer(host, self.port)
        if ok:
            self.text = self.keyboard.text
            self.error_msg = ""
            self.ok_locked = False
            self.manager.go_back()
        else:
            self.error_msg = self.manager.comm.status_msg
            self.ok_locked = False

    def get_display_addr(self):
        parsed = self.parse_addr(self.keyboard.text)
        return parsed if parsed else self.keyboard.text

    def draw_text(self):
        self.keyboard.timer.update()

        display_text = self.get_display_addr()
        text_surf = self.font.render(display_text, True, 'white')
        text_rect = text_surf.get_rect(center=(win_w / 2, self.keyboard.rect.top - vert_padding - name_h / 2))
        self.disp_surf.blit(text_surf, text_rect)

        name_frame = pygame.Rect(0, 0, win_w - 4 * hori_padding, name_h)
        name_frame.center = text_rect.center
        pygame.draw.rect(self.disp_surf, LINE_COLOR, name_frame, 1, 2)

        if self.keyboard.blink and not self.manager.comm.connecting:
            curs_surf = self.font.render('_', True, 'white')
            curs_rect = curs_surf.get_rect()
            curs_rect.midleft = text_rect.midright
            self.disp_surf.blit(curs_surf, curs_rect)

    def draw_message(self):
        msg = self.error_msg if self.error_msg else self.manager.comm.status_msg
        if not msg:
            return

        color = 'red' if self.error_msg else MUTED_TEXT
        msg_surf = self.font.render(msg, True, color)
        msg_rect = msg_surf.get_rect(center=(win_w / 2, tb_h + 2 * vert_padding))
        self.disp_surf.blit(msg_surf, msg_rect)

    def draw(self):
        self.disp_surf.fill(GRAY)

        title_text = "Enter Bluetooth address" if self.mode == "bluetooth" else "Enter IP address"
        title_surf = self.title_font.render(title_text, True, 'white')
        title_rect = title_surf.get_rect(center=(win_w / 2, 2 * vert_padding))
        self.disp_surf.blit(title_surf, title_rect)

        self.draw_message()
        self.draw_text()
        self.keyboard.draw()