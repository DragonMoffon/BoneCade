from time import time


class GlobalGameClock:
    """
    The GlobalGameClock separates the internal clock used by the game. This removes issues with event syncing, pausing,
    and timing. It also allows for modification of run speed. This is particularly useful for debugging/slo-mo.
    """

    def __init__(self):
        self.run_speed = 1
        self.time_step = 0
        self.start_time = 0
        self.run_time = 0
        self.concurrent_run_time = 0
        self.is_counting = False

    def begin(self):
        self.start_time = time()
        self.run_time = 0
        self.concurrent_run_time = 0
        self.is_counting = True

    def increment(self, delta_time: float = 1 / 60):
        self.time_step = delta_time * self.run_speed
        if self.is_counting:
            self.run_time += self.time_step
            self.concurrent_run_time += self.time_step

    def toggle(self):
        if self.is_counting:
            self.pause()
        else:
            self.play()

    def pause(self):
        self.is_counting = False

    def play(self):
        self.is_counting = True
        self.concurrent_run_time = 0


GAME_CLOCK = GlobalGameClock()
