# entities/explosion.py
import pygame

class Explosion:
    __slots__ = ("frames", "rect", "fps", "_t_last", "_i", "done", "_current_frame")

    def __init__(self, x, y, frames, fps=24, scale=1.0, keep=None):
        if not frames:
            surf = pygame.Surface((1, 1), pygame.SRCALPHA)
            frames = [surf]
        if scale != 1.0:
            frames = [pygame.transform.smoothscale(f, (int(f.get_width() * scale), int(f.get_height() * scale))) for f in frames]
        if keep is not None:
            frames = frames[:max(1, int(keep))]
        self.frames  = frames
        self.rect    = frames[0].get_rect(center=(x, y))
        self.fps     = max(1, int(fps))
        self._t_last = pygame.time.get_ticks()
        self._i      = 0
        self.done    = False
        self._current_frame = frames[0]  # Cache für aktuellen Frame

    def update(self):
        if self.done:
            return
        now = pygame.time.get_ticks()
        step_ms = 1000 // self.fps
        
        if now - self._t_last >= step_ms:
            # Berechne die Anzahl der zu überspringenden Frames
            steps = (now - self._t_last) // step_ms
            new_i = self._i + steps
            
            # Update Timer und Index
            self._t_last += steps * step_ms
            
            # Prüfe ob Animation fertig
            if new_i >= len(self.frames):
                self.done = True
                self._i = len(self.frames) - 1
            else:
                self._i = new_i
                self._current_frame = self.frames[self._i]

    def draw(self, screen):
        if not self.done:
            screen.blit(self._current_frame, self.rect)
