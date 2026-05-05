from games.tetris.settings import *

class Sound:
    def __init__(self):
        pygame.mixer.music.load(get_sound_path('music'))
        pygame.mixer.music.set_volume(bg_sound_vol)

        self.land_sound = pygame.mixer.Sound(get_sound_path('landing'))
        self.land_sound.set_volume(bg_sound_vol)

    def play_bg_music(self):
        pygame.mixer.music.play(-1)
    
    def play_land_sound(self):
        self.land_sound.play()

    def stop_bg_music(self):
        pygame.mixer.music.stop()