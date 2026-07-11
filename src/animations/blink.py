import random

class BlinkAnimation:
    def __init__(self, blink_min_ms=4000, blink_max_ms=8000):
        self.blink_min_ms = blink_min_ms
        self.blink_max_ms = blink_max_ms

    def get_next_interval(self):
        """Returns the random duration in milliseconds until the next blink."""
        return random.randint(self.blink_min_ms, self.blink_max_ms)
