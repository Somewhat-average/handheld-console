from ui.settings import *

from ui.base_screen import BaseScreen
from ui.topbar import TopBar
from ui.buttonbar import ButtonBar
from ui.menu import MenuItem, MenuList

class RecvFileScreen(BaseScreen):
    def __init__(self, manager):
        
        # general
        super().__init__(manager)
        self.tag = 'Received'
        self.disp_surf = pygame.display.get_surface()
        self.font = get_font(15)
        self.small_font = get_font(12)

        self.status_msg = ""

        # components
        self.recvpath = Path(__file__).parent / 'data' / 'received_files'
        self.files = []
        self.menu = None
        self.status_msg = ""
        self.refresh_files()

        self.surf = pygame.Surface((menu_w, menu_h))
        self.rect = self.surf.get_rect(topleft = (hori_padding, tb_h+tag_h))

        self.topbar = TopBar(self.manager)
        self.butbar = ButtonBar()

    def refresh_files(self):
        if not self.recvpath.exists():
            self.files = []
        else:
            self.files = [p for p in self.recvpath.iterdir() if p.is_file()]
            self.files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

        if self.files:
            self.menu = MenuList([
                MenuItem(file.name, lambda f=file: self.select_file(f))
                for file in self.files
            ])
            self.status_msg = f"{len(self.files)} file(s)"
        else:
            self.menu = None
            self.status_msg = "No files"

    def select_file(self, filepath):
        self.manager.push('FileDetails')
        self.manager.current.filepath = filepath

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN and self.menu:
                self.menu.move_down()
            elif event.key == pygame.K_UP and self.menu:
                self.menu.move_up()
            elif event.key == pygame.K_a and self.menu:
                self.menu.activate()
            elif event.key == pygame.K_s:
                self.manager.go_back()

    def draw_empty(self):
        self.surf.fill(GRAY)

        text_surf = self.font.render("No received files", True, MUTED_TEXT)
        text_rect = text_surf.get_rect(center=(menu_w / 2, menu_h / 2))
        self.surf.blit(text_surf, text_rect)
        self.disp_surf.blit(self.surf, self.rect)
        pygame.draw.rect(self.disp_surf, LINE_COLOR, self.rect, 2, 2)

    def draw(self):
        self.disp_surf.fill(GRAY)

        self.topbar.draw()
        self.draw_tags()
        self.butbar.draw()

        if self.menu:
            self.menu.draw()
        else:
            self.draw_empty()