from settings import *
from sys import exit
from random import choice

# Components
from game import Game
from score import Score
from preview import Preview
from sound_effect import Sound
from pause import Pause

class Main:
    def __init__(self):
        
        # general
        self.disp_surf = pygame.display.get_surface()
        self.paused = False

        # shapes
        self.next_shapes = [choice(list(TETROMINOES.keys())) for shape in range(3)]

        # components
        self.sound = Sound()
        self.score = Score()
        self.preview = Preview()
        self.game = Game(self.get_next_shape, self.update_score, self.sound.play_land_sound)
        self.pause = Pause()

    def update_score(self, score, level, lines):
        self.score.score = score
        self.score.level = level
        self.score.lines = lines
    
    def get_next_shape(self):
        next_shape = self.next_shapes.pop(0)
        self.next_shapes.append(choice(list(TETROMINOES.keys())))
        return next_shape
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d and self.game.running:
                    self.paused = not self.paused

    def draw_scene(self):
        self.disp_surf.fill(GRAY)
        self.game.draw()
        self.score.run()
        self.preview.run(self.next_shapes)

        if self.paused and self.game.running:
            self.pause.run()

        if not self.game.running:
            self.game.disp_game_over()

        pygame.display.update()
    
    def run(self):
        while True:
            self.handle_events()
            
            # display
            if self.game.running and not self.paused:
                self.game.update()
            
            # update game
            self.draw_scene()

            if not self.game.running:
                result = self.game_over_loop()
                if result == "restart":
                    return "restart"
                return "quit"
        
    def game_over_loop(self):
        while True:
            self.draw_scene()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        return "quit"
                    if event.key == pygame.K_a:
                        return "restart"