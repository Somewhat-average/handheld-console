from ui.settings import *
from ui.base_screen import BaseScreen

class FileTransferProgressScreen(BaseScreen):
    def __init__(self, manager):
        
        # general
        super().__init__(manager)
        self.tag = 'TransferPopup'
        self.is_overlay = True

        self.disp_surf = pygame.display.get_surface()
        self.font = get_font(15)
        self.small_font = get_font(12)
        self.title_font = get_font(20)

        self.done_time = None
        self.auto_close_delay = 1200
        
    def get_transfer(self):
        if getattr(self.manager.comm, "outgoing_transfer", None) is not None:
            return self.manager.comm.outgoing_transfer
        if getattr(self.manager.comm, "incoming_transfer_status", None) is not None:
            return self.manager.comm.incoming_transfer_status
        return None
    
    def get_percent(self, current, total):
        if total <= 0:
            return 0
        return int((current / total) * 100)
    
    def get_percent_step(self, current, total, step=10):
        percent = self.get_percent(current, total)
        return min(100, (percent // step) * step)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s and self.get_transfer() is None:
                send_screen = self.manager.tag_links.get("Send")
                if send_screen is not None:
                    send_screen.send_locked = False
                self.manager.go_back()

    def update(self):
        transfer = self.get_transfer()
        status = getattr(self.manager.comm, "status_msg", "")

        if transfer is None and status in ("File sent", "File received", "File transfer complete"):
            if self.done_time is None:
                self.done_time = pygame.time.get_ticks()
            elif pygame.time.get_ticks() - self.done_time >= self.auto_close_delay:
                self.done_time = None

                send_screen = self.manager.tag_links.get("Send")
                if send_screen is not None:
                    send_screen.send_locked = False

                self.manager.go_back()
        else:
            self.done_time = None

    def draw_progress_bar(self, x, y, w, h, current, total):
        pygame.draw.rect(self.disp_surf, LINE_COLOR, (x, y, w, h), 2, 2)

        percent = self.get_percent_step(current, total, step=10)
        fill_w = int((percent / 100) * (w - 4))

        if fill_w > 0:
            pygame.draw.rect(self.disp_surf, LINE_COLOR, (x + 2, y + 2, fill_w, h - 4), 0, 2)

    def draw(self):
        self.update()

        popup_w = win_w - 6 * hori_padding
        popup_h = 180
        popup = pygame.Rect(0, 0, popup_w, popup_h)
        popup.center = (win_w // 2, win_h // 2)

        pygame.draw.rect(self.disp_surf, GRAY, popup, 0, 8)
        pygame.draw.rect(self.disp_surf, LINE_COLOR, popup, 2, 8)

        title_surf = self.title_font.render("File Transfer", True, "white")
        title_rect = title_surf.get_rect(center=(popup.centerx, popup.top + 20))
        self.disp_surf.blit(title_surf, title_rect)

        transfer = self.get_transfer()
        status = getattr(self.manager.comm, "status_msg", "")

        if transfer is None:
            msg = status if status else "No active transfer"
            msg_surf = self.font.render(msg, True, MUTED_TEXT)
            msg_rect = msg_surf.get_rect(center=popup.center)
            self.disp_surf.blit(msg_surf, msg_rect)
            return

        name = transfer["name"]
        current = transfer["current"]
        total = transfer["total"]
        direction = transfer.get("direction", "out")

        dir_text = "Sending" if direction == "out" else "Receiving"
        dir_surf = self.font.render(dir_text, True, "white")
        dir_rect = dir_surf.get_rect(center=(popup.centerx, popup.top + 55))
        self.disp_surf.blit(dir_surf, dir_rect)

        name_surf = self.small_font.render(name, True, MUTED_TEXT)
        name_rect = name_surf.get_rect(center=(popup.centerx, popup.top + 80))
        self.disp_surf.blit(name_surf, name_rect)

        percent = self.get_percent_step(current, total, step=10)
        counter_surf = self.font.render(f"{percent}%", True, "white")
        counter_rect = counter_surf.get_rect(center=(popup.centerx, popup.top + 110))
        self.disp_surf.blit(counter_surf, counter_rect)

        self.draw_progress_bar(
            popup.left + 20,
            popup.top + 130,
            popup.width - 40,
            20,
            current,
            total
        )

        status_surf = self.small_font.render(status, True, MUTED_TEXT)
        status_rect = status_surf.get_rect(center=(popup.centerx, popup.top + 160))
        self.disp_surf.blit(status_surf, status_rect)