from ui.settings import *

from ui.main_screen import MainScreen
from ui.games_screen import GamesScreen

from communication.comm_service import CommService
from ui.comm_screen import CommScreen
from communication.connection_screen import ConnectionScreen
from communication.host_screen import HostScreen
from communication.connect_screen import ConnectScreen
from communication.compose_screen import ComposeScreen
from communication.inbox_screen import InboxScreen
from communication.transferfile_screen import TransferFileScreen
from communication.sendfile_screen import SendFileScreen
from communication.recvfile_screen import RecvFileScreen
from communication.filedetail_screen import FileDetailScreen
from communication.file_transfer_progress_screen import FileTransferProgressScreen

from ui.settings_screen import SettingsScreen
from ui.devname_screen import DevNameScreen
from ui.shutdown_screen import ShutdownScreen

from games.tetris.tetris_screen import TetrisScreen
from games.tetris.tetris_pause_screen import TetrisPauseScreen
from games.tetris.tetris_settings_screen import TetrisSettingsScreen
from games.tetris.tetris_gameover_screen import TetrisGameOverScreen

from games.asteroids.main import AsteroidsScreen

class ScreenManager:
    def __init__(self, app):
        self.app = app
        self.clock = self.app.clock
        self.stack = []
        self.comm = CommService(self, "tcp")
        self.tag_links = {
            'Menu': MainScreen(self),
            'Games': GamesScreen(self),
            'Tetris': TetrisScreen(self),
            'TetrisPause': TetrisPauseScreen(self),
            'TetrisSettings': TetrisSettingsScreen(self),
            'TetrisGameOver': TetrisGameOverScreen(self),
            'Asteroids': AsteroidsScreen(self),
            'Communication': CommScreen(self),
            'Connection': ConnectionScreen(self),
            'Host': HostScreen(self),
            'Connect': ConnectScreen(self),
            'Compose': ComposeScreen(self),
            'Inbox': InboxScreen(self),
            'Transfer': TransferFileScreen(self),
            'Send': SendFileScreen(self),
            'Received': RecvFileScreen(self),
            'FileDetails': FileDetailScreen(self),
            'TransferPopup': FileTransferProgressScreen(self),
            'Settings': SettingsScreen(self),
            'DevName': DevNameScreen(self),
            'Shutdown': ShutdownScreen(self)
        }

        self.overlay = pygame.Surface((win_w, win_h), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 120))
        pygame.key.set_repeat(first_delay, repeat_delay)

    @property
    def current(self):
        return self.stack[-1]
    
    @property
    def tag_history(self):
        return [screen.tag for screen in self.stack if not screen.is_overlay]

    def push(self, tag):
        self.stack.append(self.tag_links[tag])

    def go_back(self):
        if len(self.stack) > 1:
            self.stack.pop()

    def handle_event(self, event):
        self.current.handle_event(event)

    def _handle_comm_requests(self):
        if self.comm.request_open_transfer_popup:
            self.comm.request_open_transfer_popup = False

            if self.current.tag != 'TransferPopup':
                self.push('TransferPopup')

    def draw(self):
        self._handle_comm_requests()

        # draw underlying screen if top screen is overlay
        if len(self.stack) > 1 and self.current.is_overlay and not self.stack[-2].is_overlay:
            self.stack[-2].draw()
            pygame.display.get_surface().blit(self.overlay, (0, 0))

        self.current.draw()
        self.clock.tick(fps)