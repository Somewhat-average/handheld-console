from ui.settings import *

from ui.base_screen import BaseScreen
from ui.topbar import TopBar
from ui.buttonbar import ButtonBar
from ui.menu import MenuItem, MenuList

class MainScreen(BaseScreen):
    def __init__(self, manager):
        
        # general
        super().__init__(manager)
        self.tag = 'Menu'
        self.disp_surf = pygame.display.get_surface()

        # components
        self.topbar = TopBar(self.manager)
        self.menu = MenuList([
            MenuItem('Games', self.open_games),
            MenuItem('Communication', self.open_comm),
            MenuItem('Settings', self.open_settings),
            MenuItem('Shutdown', self.open_shutdown_dialog)
            ])
        self.butbar = ButtonBar(back_en = False)
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.menu.move_down()
            elif event.key == pygame.K_UP:
                self.menu.move_up()
            elif event.key == pygame.K_a:
                self.menu.activate()

    def open_games(self):
        self.manager.push('Games')

    def open_comm(self):
        self.manager.push('Communication')

    def open_settings(self):
        self.manager.push('Settings')

    def open_shutdown_dialog(self):
        self.manager.push('Shutdown')

    def draw(self):
        self.disp_surf.fill(GRAY)

        self.topbar.draw()
        self.draw_tags()
        self.menu.draw()
        self.butbar.draw()