from ui.settings import *
from random import choice

from ui.base_screen import BaseScreen

from settings import *
from game import Game
from score import Score
from preview import Preview
from sound_effect import Sound

class TetrisScreen(BaseScreen):
    def __init__(self, manager):
        
        # general
        super().__init__(manager)
        self.tag = 'Tetris'
        self.disp_surf = pygame.display.get_surface()
        self.paused = False

        # shapes
        self.next_shapes = [choice(list(TETROMINOES.keys())) for shape in range(3)]

        # components
        self.sound = Sound()
        self.score = Score()
        self.preview = Preview()
        self.game = Game(self.get_next_shape, self.update_score, self.sound.play_land_sound)
    
    def update_score(self, score, level, lines):
        self.score.score = score
        self.score.level = level
        self.score.lines = lines
    
    def get_next_shape(self):
        next_shape = self.next_shapes.pop(0)
        self.next_shapes.append(choice(list(TETROMINOES.keys())))
        return next_shape
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                self.paused = True
                self.manager.push('TetrisPause')
                pygame.key.set_repeat(first_delay, repeat_delay)

    def restart(self):
        # shapes
        self.next_shapes = [choice(list(TETROMINOES.keys())) for shape in range(3)]

        # components
        self.sound = Sound()
        self.score = Score()
        self.preview = Preview()
        self.game = Game(self.get_next_shape, self.update_score, self.sound.play_land_sound)

        self.sound.play_bg_music()
        pygame.mixer.music.set_volume(bg_sound_vol if self.manager.tag_links['TetrisSettings'].menu.sound_en else 0)
        self.sound.land_sound.set_volume(bg_sound_vol if self.manager.tag_links['TetrisSettings'].menu.sound_en else 0)

    def draw(self):

        # update game
        if self.manager.current.tag == self.tag:
            self.game.update()
        if not self.game.running:
            self.manager.push('TetrisGameOver')
            
        self.disp_surf.fill(GRAY)
        self.game.draw()
        self.score.run()
        self.preview.run(self.next_shapes)