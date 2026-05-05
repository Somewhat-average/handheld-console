from ui.settings import *

from ui.base_screen import BaseScreen
from ui.topbar import TopBar
from ui.buttonbar import ButtonBar
from ui.menu import MenuItem, MenuList

class TransferFileScreen(BaseScreen):
    def __init__(self, manager):
        
        # general
        super().__init__(manager)
        self.tag = 'Transfer'
        self.disp_surf = pygame.display.get_surface()

        # components
        self.topbar = TopBar(self.manager)
        self.menu = MenuList([
            MenuItem('Send files', self.open_sendfile),
            MenuItem('Received files', self.open_receivedfile),
            ])
        self.butbar = ButtonBar()
    
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

    def open_sendfile(self):
        self.manager.push('Send')

    def open_receivedfile(self):
        self.manager.push('Received')
        self.manager.current.refresh_files()

    def draw(self):
        self.disp_surf.fill(GRAY)

        self.topbar.draw()
        self.draw_tags()
        self.menu.draw()
        self.butbar.draw()