from ui.settings import *
import platform
import subprocess
import re

from ui.base_screen import BaseScreen
from ui.topbar import TopBar
from ui.buttonbar import ButtonBar
from ui.menu import MenuItem

class HostScreen(BaseScreen):
    def __init__(self, manager):
        
        # general
        super().__init__(manager)
        self.tag = 'Host'
        self.disp_surf = pygame.display.get_surface()
        self.font = get_font(15)
        self.title_font = get_font(20)
        
        self.surf = pygame.Surface((menu_w, menu_h))
        self.rect = self.surf.get_rect(topleft=(hori_padding, tb_h + tag_h))

        # components
        self.topbar = TopBar(self.manager)
        self.butbar = ButtonBar()

    @property
    def mode(self):
        return self.manager.comm.mode

    @property
    def addr(self):
        if self.mode == "bluetooth":
            return get_bluetooth_mac()
        return "127.0.0.1"

    @property
    def port(self):
        return 4 if self.mode == "bluetooth" else 5555
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                self.manager.go_back()
            elif event.key == pygame.K_a:
                if self.manager.comm.is_hosting:
                    self.stop()
                else:
                    self.start()

    def start(self):
        if not self.addr:
            self.manager.comm.status_msg = "Address unavailable"
            return

        self.manager.comm.start_host(self.addr, self.port)

    def stop(self):
        self.manager.comm.stop_host()

    def draw(self):
        self.disp_surf.fill(GRAY)
        self.topbar.draw()
        self.draw_tags()
        self.butbar.draw()

        self.surf.fill(GRAY)

        title_text = "Bluetooth address" if self.mode == "bluetooth" else "TCP address"
        title = self.title_font.render(title_text, True, "white")
        title_rect = title.get_rect(center=(self.surf.get_width() / 2, self.surf.get_height() / 2 - 5 * vert_padding))
        self.surf.blit(title, title_rect)

        addr_text = self.addr if self.addr else "Unavailable"
        addr_surf = self.font.render(addr_text, True, "white")
        addr_rect = addr_surf.get_rect(center=(self.surf.get_width() / 2, self.surf.get_height() / 2 - vert_padding))
        self.surf.blit(addr_surf, addr_rect)

        status_surf = self.font.render(self.manager.comm.status_msg, True, MUTED_TEXT)
        status_rect = status_surf.get_rect(center=(self.surf.get_width() / 2, addr_rect.bottom + vert_padding))
        self.surf.blit(status_surf, status_rect)

        rect = pygame.Rect(0, 0, sd_item_w, item_h)
        rect.midtop = (menu_w / 2, status_rect.bottom + vert_padding)
        pygame.draw.rect(self.surf, LINE_COLOR, rect, 2, 6)

        button_label = "Stop" if self.manager.comm.is_hosting else "Start"
        text_surf = self.font.render(button_label, True, "white")
        text_rect = text_surf.get_rect(center=rect.center)
        self.surf.blit(text_surf, text_rect)

        self.disp_surf.blit(self.surf, self.rect)
        pygame.draw.rect(self.disp_surf, LINE_COLOR, self.rect, 2, 2)



def get_bluetooth_mac():
    system = platform.system()

    if system == "Linux":
        try:
            out = subprocess.check_output(
                ["bluetoothctl", "show"],
                text=True,
                stderr=subprocess.DEVNULL
            )
            match = re.search(
                r"^Controller\s+([0-9A-F:]{17})\s",
                out,
                re.IGNORECASE | re.MULTILINE
            )
            if match:
                return match.group(1).upper()
        except Exception:
            pass

        try:
            out = subprocess.check_output(
                ["hciconfig"],
                text=True,
                stderr=subprocess.DEVNULL
            )
            match = re.search(
                r"BD Address:\s*([0-9A-F:]{17})",
                out,
                re.IGNORECASE
            )
            if match:
                return match.group(1).upper()
        except Exception:
            pass

        return None

    elif system == "Windows":
        try:
            out = subprocess.check_output(
                [
                    "powershell",
                    "-Command",
                    "Get-NetAdapter | Where-Object {$_.InterfaceDescription -like '*Bluetooth*'} | Select-Object -ExpandProperty MacAddress"
                ],
                text=True,
                stderr=subprocess.DEVNULL
            )
            mac = out.strip().replace("-", ":")
            if mac:
                return mac.upper()
        except Exception:
            pass

        return None

    return None