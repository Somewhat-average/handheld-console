from ui.settings import *

from ui.screen_manager import ScreenManager

class App:
    def __init__(self):

        # general
        pygame.init()
        pygame.mixer.init()
        self.disp_surf = pygame.display.set_mode((win_w, win_h))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption('Retro Gaming System')
        self.running = True

        self.manager = ScreenManager(self)

        self.manager.push('Tetris')
        self.manager.stack[-1].sound.play_bg_music()
        pygame.key.set_repeat()
        
    def run(self):
        while self.running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.manager.handle_event(event)
            
            self.manager.draw()
            pygame.display.flip()

        pygame.quit()

if __name__ == '__main__':
    App().run()