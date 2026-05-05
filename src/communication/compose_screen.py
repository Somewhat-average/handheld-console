from ui.settings import *

from ui.base_screen import BaseScreen
from ui.keyboard import Keyboard


class ComposeScreen(BaseScreen):
    def __init__(self, manager):
        
        # general
        super().__init__(manager)
        self.tag = "Compose"
        self.disp_surf = pygame.display.get_surface()
        self.title_font = get_font(20)
        self.font = get_font(15)
        self.small_font = get_font(12)

        # components
        self.text = ""
        self.status_msg = ""

        self.keyboard = Keyboard(self, len_lim=64)
        self.keyboard.rect.bottom = win_h - vert_padding

    def is_connected(self):
        return hasattr(self.manager, "comm") and self.manager.comm.is_connected

    def send_current_message(self):
        if not self.is_connected():
            self.status_msg = "Not connected"
            return

        text = self.keyboard.text.strip()
        if not text:
            self.status_msg = "Empty message"
            return

        success, msg = self.manager.comm.send_message(text)

        if success:
            self.text = ""
            self.keyboard.text = ""
            self.keyboard.selc_idx = [0, 0]
            self.status_msg = "Sent"
        else:
            self.status_msg = msg

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
                result = self.keyboard.activate()

                if result == "ok":
                    self.send_current_message()

            elif event.key == pygame.K_s:
                self.text = self.keyboard.text
                self.keyboard.selc_idx = [0, 0]
                self.manager.go_back()

    def draw_status(self):
        if self.is_connected():
            conn_text = "Connected"
            conn_color = "white"
        elif hasattr(self.manager, "comm") and self.manager.comm.connecting:
            conn_text = "Connecting..."
            conn_color = MUTED_TEXT
        else:
            conn_text = "Not connected"
            conn_color = "red"

        conn_surf = self.small_font.render(conn_text, True, conn_color)
        conn_rect = conn_surf.get_rect(center=(win_w / 2, 2 * vert_padding))
        self.disp_surf.blit(conn_surf, conn_rect)

        if self.status_msg:
            msg_surf = self.small_font.render(self.status_msg, True, MUTED_TEXT)
            msg_rect = msg_surf.get_rect(center=(win_w / 2, 4 * vert_padding))
            self.disp_surf.blit(msg_surf, msg_rect)

    def wrap_text(self, text, font, max_width):
        words = text.split()
        lines = []

        if not words:
            return [""]

        current_line = ""

        for word in words:
            test_line = word if current_line == "" else current_line + " " + word

            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)

                if font.size(word)[0] > max_width:
                    chunk = ""
                    for ch in word:
                        test_chunk = chunk + ch
                        if font.size(test_chunk)[0] <= max_width:
                            chunk = test_chunk
                        else:
                            lines.append(chunk)
                            chunk = ch
                    current_line = chunk
                else:
                    current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    def draw_text_box(self):
        self.keyboard.timer.update()

        frame = pygame.Rect(0, 0, win_w - 4 * hori_padding, 2 * name_h - 2*vert_padding)
        frame.midbottom = (win_w / 2, self.keyboard.rect.top - vert_padding)
        pygame.draw.rect(self.disp_surf, LINE_COLOR, frame, 1, 2)

        text_max_width = frame.width - 2 * hori_padding
        wrapped_lines = self.wrap_text(self.keyboard.text, self.font, text_max_width)

        line_height = self.font.get_height() + 2
        max_lines = max(1, (frame.height - 2 * vert_padding) // line_height)
        visible_lines = wrapped_lines[-max_lines:]

        start_y = frame.top + vert_padding

        for i, line in enumerate(visible_lines):
            line_surf = self.font.render(line, True, "white")
            line_rect = line_surf.get_rect(
                topleft=(frame.left + hori_padding, start_y + i * line_height)
            )
            self.disp_surf.blit(line_surf, line_rect)

        if self.keyboard.blink and not getattr(self.manager.comm, "connecting", False):
            curs_surf = self.font.render("_", True, "white")

            if visible_lines:
                last_line = visible_lines[-1]
                last_line_width = self.font.size(last_line)[0]
                cursor_x = frame.left + hori_padding + last_line_width
                cursor_y = start_y + (len(visible_lines) - 1) * line_height
                curs_rect = curs_surf.get_rect(topleft=(cursor_x, cursor_y))
            else:
                curs_rect = curs_surf.get_rect(topleft=(frame.left + hori_padding, start_y))

            self.disp_surf.blit(curs_surf, curs_rect)

    def draw(self):
        self.disp_surf.fill(GRAY)

        self.draw_status()
        self.draw_text_box()
        self.keyboard.draw()