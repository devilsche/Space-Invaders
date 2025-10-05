# entities/explosion.py
import pygame

class Explosion:
    __slots__ = ("frames", "rect", "fps", "_t_last", "_i", "done")

    def __init__(self, x, y, frames, fps=24, scale=1.0, keep=None):
        if not frames:
            surf = pygame.Surface((1, 1), pygame.SRCALPHA)
            frames = [surf]
        if scale != 1.0:
            frames = [pygame.transform.smoothscale(f, (int(f.get_width() * scale), int(f.get_height() * scale))) for f in frames]
        if keep is not None:
            frames = frames[:max(1, int(keep))]
        self.frames = frames
        self.rect = frames[0].get_rect(center=(x, y))
        self.fps = max(1, int(fps))
        self._t_last = pygame.time.get_ticks()
        self._i = 0
        self.done = False

    def update(self):
        if self.done:
            return
        now = pygame.time.get_ticks()
        step_ms = 1000 // self.fps
        while now - self._t_last >= step_ms and not self.done:
            self._t_last += step_ms
            self._i += 1
            if self._i >= len(self.frames):
                self.done = True

    def draw(self, screen):
        if not self.done:
            screen.blit(self.frames[self._i], self.rect)
