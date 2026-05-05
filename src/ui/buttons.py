import pygame

try:
    from gpiozero import Button
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False


class GPIOInputBridge:
    def __init__(self):
        self.enabled = GPIO_AVAILABLE

        self.states = {
            "A": False,
            "B": False,
            "Start": False,
            "Select": False,
            "Up": False,
            "Down": False,
            "Left": False,
            "Right": False,
        }

        if not self.enabled:
            print("GPIO not available. Keyboard-only mode.")
            self.buttons = {}
            return

        self.bindings = {
            "A":      (Button(6, pull_up=False, bounce_time=0.03), pygame.K_a),
            "B":      (Button(26, pull_up=False, bounce_time=0.03), pygame.K_d),
            "Start":  (Button(23, pull_up=False, bounce_time=0.03), pygame.K_RETURN),
            "Select": (Button(24, pull_up=False, bounce_time=0.03), pygame.K_s),
            "Up":     (Button(17, pull_up=False, bounce_time=0.03), pygame.K_UP),
            "Down":   (Button(27, pull_up=False, bounce_time=0.03), pygame.K_DOWN),
            "Left":   (Button(22, pull_up=False, bounce_time=0.03), pygame.K_LEFT),
            "Right":  (Button(5, pull_up=False, bounce_time=0.03), pygame.K_RIGHT),
        }

    def update(self):
        if not self.enabled:
            return

        for name, (button, key) in self.bindings.items():
            pressed = button.is_pressed
            previous = self.states[name]

            if pressed and not previous:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=key))

            elif not pressed and previous:
                pygame.event.post(pygame.event.Event(pygame.KEYUP, key=key))

            self.states[name] = pressed

    def is_pressed(self, name):
        return self.states.get(name, False)

