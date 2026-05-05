from ui.settings import *
import psutil
import platform

class TopBar:
    def __init__(self, manager):

        # general
        self.surf = pygame.Surface((tb_w, tb_h))
        self.rect = self.surf.get_rect(topleft = (0, 0))
        self.disp_surf = pygame.display.get_surface()
        self.manager = manager

        # font
        self.font = get_font(15)

    def update(self):

        # display info
        system = platform.system()

        if system == "Linux":
            try:
                with open("/sys/class/power_supply/BAT0/capacity") as f:    # for Ras Pi Zero 2W
                    self.battery = int(f.read().strip())
            except Exception:
                pass

        elif system == "Windows":
            try:
                self.battery = psutil.sensors_battery().percent             # for Windows PC
            except Exception:
                pass

        self.text = self.manager.tag_links['DevName'].text

    def draw(self):
        self.surf.fill(GRAY)
        self.update()

        text_surf1 = self.font.render(f'Device name: {self.text}', True, MUTED_TEXT)
        text_rect1 = text_surf1.get_rect(midleft = (3*hori_padding, self.surf.get_height()/2))
        self.surf.blit(text_surf1, text_rect1)

        # No battery Info
        # text_surf2 = self.font.render(f'Battery: {self.battery}%', True, MUTED_TEXT)
        # text_rect2 = text_surf2.get_rect(midright = (win_w - 3*hori_padding, self.surf.get_height()/2))
        # self.surf.blit(text_surf2, text_rect2)

        self.disp_surf.blit(self.surf, self.rect)
