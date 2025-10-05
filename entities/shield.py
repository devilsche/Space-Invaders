# entities/shield.py
import pygame

class Shield:
    __slots__ = (
        "frames","center","fps","_t_last","_i","loop","done",
        "alpha","blend_add","radius_px","mask","mask_center"
    )

    def __init__(self, x, y, frames, fps=18, scale=1.0,
                 loop=True, alpha=100, blend_add=False, use_mask=False):
        if not frames:
            blank = pygame.Surface((1,1), pygame.SRCALPHA)
            frames = [blank]

        # einheitlich skalieren
        if scale != 1.0:
            w, h = frames[0].get_width(), frames[0].get_height()
            tw, th = int(w*scale), int(h*scale)
            frames = [pygame.transform.smoothscale(f, (tw, th)) for f in frames]

        # alle Frames exakt gleiche Größe → kein Wobble
        fw, fh = frames[0].get_width(), frames[0].get_height()
        eq = []
        for f in frames:
            if f.get_size() != (fw, fh):
                pad = pygame.Surface((fw, fh), pygame.SRCALPHA)
                pad.blit(f, f.get_rect(center=(fw//2, fh//2)))
                eq.append(pad)
            else:
                eq.append(f)
        self.frames = eq

        # Referenz
        self.center = (int(x), int(y))
        self.radius_px = min(fw, fh) // 2

        # Animation
        self.fps     = max(1, int(fps))
        self._t_last = pygame.time.get_ticks()
        self._i      = 0
        self.loop    = loop
        self.done    = False

        # Render
        self.alpha     = max(0, min(255, int(alpha)))
        self.blend_add = bool(blend_add)

        # optionale Maske (nur für Kollision)
        if use_mask:
            self.mask = pygame.mask.from_surface(self.frames[0])
            try:
                cx, cy = self.mask.centroid()
            except AttributeError:
                cx, cy = self.mask.get_bounding_rect().center
            self.mask_center = (cx, cy)
        else:
            self.mask = None
            self.mask_center = None

    def set_center(self, pos):
        self.center = (int(pos[0]), int(pos[1]))

    def update(self):
        if self.done: return
        now = pygame.time.get_ticks()
        step = 1000 // self.fps
        while now - self._t_last >= step and not self.done:
            self._t_last += step
            self._i += 1
            if self._i >= len(self.frames):
                if self.loop:
                    self._i = 0
                else:
                    self._i = len(self.frames) - 1
                    self.done = True

    def _current_rect(self):
        return self.frames[self._i].get_rect(center=self.center)

    def draw(self, screen):
        if self.done: return
        frame = self.frames[self._i]
        frame.set_alpha(self.alpha)
        r = self._current_rect()
        if self.blend_add:
            screen.blit(frame, r, special_flags=pygame.BLEND_ADD)
        else:
            screen.blit(frame, r)

    # schneller Kreis-Hit
    def hit_circle(self, point):
        px, py = point; cx, cy = self.center
        return (px - cx)**2 + (py - cy)**2 <= self.radius_px**2

    # optionale Pixelmaske
    def hit_mask(self, point):
        if not self.mask:
            return self.hit_circle(point)
        r = self._current_rect()
        lx = int(point[0] - r.left); ly = int(point[1] - r.top)
        if lx < 0 or ly < 0 or lx >= r.width or ly >= r.height:
            return False
        return self.mask.get_at((lx, ly)) != 0
