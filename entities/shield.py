# entities/shield.py
import pygame

class Shield:
    __slots__ = (
        "frames","center","fps","_t_last","_i","loop","done",
        "alpha","blend_add","radius_px","mask","mask_center","_last_hit_sound"
    )

    def __init__(self, x, y, frames, fps=18, scale=1.0, loop=True, alpha=150, blend_add=False, use_mask=True):
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

        # Sound-Cooldown initialisieren
        self._last_hit_sound = 0

    def set_center(self, pos):
        self.center = (int(pos[0]), int(pos[1]))

    def rescale_for_player(self, player_rect, base_frames, base_scale_factor):
        """Skaliert das Schild basierend auf der Spielergröße neu"""
        # Neue Skalierung basierend auf Spielergröße berechnen
        new_scale = max(player_rect.w, player_rect.h) / base_frames[0].get_width() * base_scale_factor

        # Frames neu skalieren
        if new_scale != 1.0:
            w, h = base_frames[0].get_width(), base_frames[0].get_height()
            tw, th = int(w * new_scale), int(h * new_scale)
            new_frames = [pygame.transform.smoothscale(f, (tw, th)) for f in base_frames]
        else:
            new_frames = base_frames.copy()

        # Alle Frames auf einheitliche Größe bringen
        fw, fh = new_frames[0].get_width(), new_frames[0].get_height()
        eq_frames = []
        for f in new_frames:
            if f.get_size() != (fw, fh):
                pad = pygame.Surface((fw, fh), pygame.SRCALPHA)
                pad.blit(f, f.get_rect(center=(fw//2, fh//2)))
                eq_frames.append(pad)
            else:
                eq_frames.append(f)

        # Frames und Radius aktualisieren
        self.frames = eq_frames
        self.radius_px = min(fw, fh) // 2

        # Maske neu erstellen falls verwendet
        if self.mask is not None:
            self.mask = pygame.mask.from_surface(self.frames[0])
            try:
                cx, cy = self.mask.centroid()
            except AttributeError:
                cx, cy = self.mask.get_bounding_rect().center
            self.mask_center = (cx, cy)

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

    def hit_by_projectile(self, projectile_rect):
        """Prüft ob ein Projektil das Schild trifft (sowohl Circle als auch Mask)"""
        # Erst Circle-Check für Performance
        if not self.hit_circle(projectile_rect.center):
            return False

        # Dann präziseren Mask-Check falls verfügbar
        if self.mask:
            return self.hit_mask(projectile_rect.center)

        return True

    def play_hit_sound(self, assets):
        """Spielt den Shield-Hit-Sound ab mit Cooldown"""
        now = pygame.time.get_ticks()
        # Sound-Cooldown: maximal alle 100ms einen Shield-Hit-Sound
        if now - self._last_hit_sound < 100:
            return

        if assets.get("shield_hit_sound"):
            from config import MASTER_VOLUME, SFX_VOLUME
            assets["shield_hit_sound"].set_volume(MASTER_VOLUME * SFX_VOLUME)
            assets["shield_hit_sound"].play()
            self._last_hit_sound = now
