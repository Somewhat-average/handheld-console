from ui.settings import *

from ui.base_screen import BaseScreen
from ui.topbar import TopBar
from ui.menu import MenuItem, MenuList

class SendFileScreen(BaseScreen):
    def __init__(self, manager):
        
        # general
        super().__init__(manager)
        self.tag = 'Send'
        self.disp_surf = pygame.display.get_surface()
        self.title_font = get_font(20)
        self.font = get_font(15)
        self.small_font = get_font(12)

        self.status_msg = ""
        self.send_locked = False

        # components
        curr_dir = Path(__file__).parent
        self.file_options = [
            ("tetris_standalone.zip", curr_dir / 'data' / 'game_files' / 'tetris_standalone.zip'),
            ("asteroids_standalone.zip", curr_dir / 'data' / 'game_files' / 'asteroids_standalone.zip'),
        ]

        self.menu = MenuList([
            MenuItem(label, lambda path=path: self.send_selected_file(path))
            for label, path in self.file_options
        ])

        self.topbar = TopBar(self.manager)

    def is_connected(self):
        return hasattr(self.manager, "comm") and self.manager.comm.is_connected

    def send_selected_file(self, filepath):
        if not self.is_connected():
            self.status_msg = "Not connected"
            return

        if getattr(self.manager.comm, "outgoing_transfer", None) is not None:
            self.status_msg = "Transfer in progress"
            return

        success, msg = self.manager.comm.send_file(filepath)
        self.status_msg = msg

        if success and self.manager.current.tag != 'TransferPopup':
            self.manager.push('TransferPopup')

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.menu.move_down()
            elif event.key == pygame.K_UP:
                self.menu.move_up()
            elif event.key == pygame.K_a:
                if not self.send_locked:
                    self.send_locked = True
                    self.menu.activate()
            elif event.key == pygame.K_s:
                self.manager.go_back()
                self.menu.selc_idx = 0

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                self.send_locked = False

    def draw(self):
        if getattr(self.manager.comm, "outgoing_transfer", None) is None:
            self.send_locked = False

        self.disp_surf.fill(GRAY)

        self.topbar.draw()
        self.draw_tags()
        self.menu.draw()