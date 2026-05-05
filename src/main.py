from ui.settings import *

from ui.screen_manager import ScreenManager
from ui.buttons import GPIOInputBridge
from communication.message_store import init_messages

class App:
    def __init__(self):

        # general
        pygame.init()
        pygame.mixer.init()
        self.disp_surf = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption('Retro Gaming System')
        self.running = True
        self.gpio = GPIOInputBridge()

        init_messages(clear_on_start=True)
        self.manager = ScreenManager(self)

        self.manager.push('Menu')
        
    def run(self):
        while self.running:

            self.gpio.update()

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

