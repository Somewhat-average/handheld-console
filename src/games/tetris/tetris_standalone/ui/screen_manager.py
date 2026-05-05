from ui.settings import *

from tetris_screen import TetrisScreen
from tetris_pause_screen import TetrisPauseScreen
from tetris_settings_screen import TetrisSettingsScreen
from tetris_gameover_screen import TetrisGameOverScreen

class ScreenManager:
    def __init__(self, app):
        self.app = app
        self.clock = self.app.clock
        self.stack = []
        self.tag_links = {
            'Tetris': TetrisScreen(self),
            'TetrisPause': TetrisPauseScreen(self),
            'TetrisSettings': TetrisSettingsScreen(self),
            'TetrisGameOver': TetrisGameOverScreen(self)
        }

        self.overlay = pygame.Surface((win_w, win_h), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 120))

    @property
    def current(self):
        return self.stack[-1]
    
    @property
    def tag_history(self):
        return [screen.tag for screen in self.stack]

    def push(self, tag):
        self.stack.append(self.tag_links[tag])

    def go_back(self):
        if len(self.stack) > 1:
            self.stack.pop()

    def handle_event(self, event):
        self.current.handle_event(event)

    def draw(self):

        # draw underlying screen if top screen is overlay
        if len(self.stack) > 1 and self.current.is_overlay and not self.stack[-2].is_overlay:
            self.stack[-2].draw()
            pygame.display.get_surface().blit(self.overlay, (0, 0))
        self.current.draw()
        self.clock.tick(fps)