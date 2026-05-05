from ui.settings import *

from ui.base_screen import BaseScreen
from ui.topbar import TopBar
from ui.buttonbar import ButtonBar
from ui.menu import MenuItem, MenuList

class ConnectionScreen(BaseScreen):
    def __init__(self, manager):
        
        # general
        super().__init__(manager)
        self.tag = 'Connection'
        self.disp_surf = pygame.display.get_surface()

        # components
        self.topbar = TopBar(self.manager)
        self.butbar = ButtonBar()
        self.menu = None
        self.refresh_menu()

    def refresh_menu(self):
        if self.manager.comm.is_connected:
            items = [
                MenuItem('Disconnect', self.disconnect_peer),
            ]
        elif self.manager.comm.connecting:
            items = [
                MenuItem('Connecting...', lambda: None, enabled=False),
            ]
        else:
            items = [
                MenuItem('Host', self.open_host),
                MenuItem('Connect', self.open_connect),
            ]

        old_idx = self.menu.selc_idx if self.menu else 0
        self.menu = MenuList(items)
        self.menu.selc_idx = min(old_idx, len(items) - 1)
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.menu.move_down()
            elif event.key == pygame.K_UP:
                self.menu.move_up()
            elif event.key == pygame.K_a:
                self.menu.activate()
            elif event.key == pygame.K_s:
                self.manager.go_back()
                self.menu.selc_idx = 0

    def open_host(self):
        self.manager.push('Host')

    def open_connect(self):
        self.manager.push('Connect')

    def disconnect_peer(self):
        self.manager.comm.disconnect()
        self.refresh_menu()

    def draw(self):
        self.refresh_menu()

        self.disp_surf.fill(GRAY)

        self.topbar.draw()
        self.draw_tags()
        self.menu.draw()
        self.butbar.draw()