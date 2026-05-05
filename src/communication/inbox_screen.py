from ui.settings import *
from ui.base_screen import BaseScreen
from ui.buttonbar import ButtonBar
from communication.message_store import *


class InboxScreen(BaseScreen):
    def __init__(self, manager):
        super().__init__(manager)

        self.tag = "Inbox"
        self.disp_surf = pygame.display.get_surface()
        self.title_font = get_font(20)
        self.font = get_font(15)
        self.small_font = get_font(12)

        self.messages = []
        self.msg_idx = 0
        self.refresh_messages(jump_to_latest=True)

        self.butbar = ButtonBar(self)

    def move_prev(self):
        if self.messages and self.msg_idx > 0:
            self.msg_idx -= 1

    def move_next(self):
        if self.messages and self.msg_idx < len(self.messages) - 1:
            self.msg_idx += 1

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_UP):
                self.move_prev()
            elif event.key in (pygame.K_RIGHT, pygame.K_DOWN):
                self.move_next()
            elif event.key == pygame.K_s:
                self.manager.go_back()

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

                # If a single word is too wide, split it by characters
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

    def get_current_message(self):
        if not self.messages:
            return None
        return self.messages[self.msg_idx]
    
    def refresh_messages(self, jump_to_latest=False):
        self.messages = load_messages()

        if not self.messages:
            self.msg_idx = 0
            return

        if jump_to_latest:
            self.msg_idx = len(self.messages) - 1
        else:
            self.msg_idx = min(self.msg_idx, len(self.messages) - 1)

    def draw_message_box(self):
        box = pygame.Rect(
            hori_padding,
            tb_h,
            win_w - 2 * hori_padding,
            win_h - tb_h - bb_h + vert_padding
        )
        pygame.draw.rect(self.disp_surf, LINE_COLOR, box, 2, 2)

        msg = self.get_current_message()

        if not msg:
            text_surf = self.font.render("No messages", True, MUTED_TEXT)
            text_rect = text_surf.get_rect(center=box.center)
            self.disp_surf.blit(text_surf, text_rect)
            return

        direction = "Received" if msg["direction"] == "in" else "Sent"
        dir_surf = self.small_font.render(direction, True, MUTED_TEXT)
        dir_rect = dir_surf.get_rect(
            topleft=(box.left + hori_padding, box.top + vert_padding)
        )
        self.disp_surf.blit(dir_surf, dir_rect)

        # Wrap the message text
        text_max_width = box.width - 2 * hori_padding
        wrapped_lines = self.wrap_text(msg["text"], self.font, text_max_width)

        line_height = self.font.get_height() + 4
        start_y = dir_rect.bottom + vert_padding

        for i, line in enumerate(wrapped_lines):
            line_surf = self.font.render(line, True, "white")
            line_rect = line_surf.get_rect(
                topleft=(box.left + hori_padding, start_y + i * line_height)
            )
            self.disp_surf.blit(line_surf, line_rect)

    def draw_counter(self):
        if self.messages:
            counter = f"{self.msg_idx + 1}/{len(self.messages)}"
        else:
            counter = "0/0"

        counter_surf = self.small_font.render(counter, True, MUTED_TEXT)
        counter_rect = counter_surf.get_rect(
            midbottom=(win_w / 2, win_h - vert_padding)
        )
        self.disp_surf.blit(counter_surf, counter_rect)

    def draw(self):
        self.refresh_messages()
        self.disp_surf.fill(GRAY)

        title_surf = self.title_font.render("Inbox", True, "white")
        title_rect = title_surf.get_rect(center=(win_w / 2, 2 * vert_padding))
        self.disp_surf.blit(title_surf, title_rect)

        self.draw_message_box()
        self.draw_counter()