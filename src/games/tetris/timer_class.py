from pygame.time import get_ticks

class Timer:
    def __init__(self, duration, repeated = False, func = None):
        self.duration = duration
        self.repeated = repeated
        self.func = func

        self.start_time = 0
        self.active = False

    def activate(self):        
        self.active = True
        self.start_time = get_ticks()

    def deactivate(self):
        self.active = False
        self.start_time = 0

    def update(self):
        curr_t = get_ticks()
        if self.active and curr_t - self.start_time >= self.duration:

            # call function
            if self.func and self.start_time != 0:
                self.func()
            
            # reset timer
            self.deactivate()

            # repeat timer
            if self.repeated:
                self.activate()