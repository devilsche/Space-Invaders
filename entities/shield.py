# entities/shield.py
import pygame

class Shield:
    __slots__ = (
        "frames","center","fps","_t_last","_i","loop","done",
        "alpha","blend_add","radius_px","mask","mask_center","_last_hit_sound",
        "max_health","current_health","damaged_until","_last_regen_time","is_powerup_shield",
        "damage_reduction","regen_rate","min_health_percentage"
    )

    def __init__(self, x, y, frames, fps=18, scale=1.0, loop=True, alpha=150, blend_add=False, use_mask=True, player_health=1000, is_powerup_shield=False, shield_config=None):
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

        # Schild-Health System basierend auf Config
        if shield_config:
            # Power-Up Shield Config verwenden
            config = shield_config
        else:
            # Standard Shield Config laden
            from config.shield import SHIELD_CONFIG
            config = SHIELD_CONFIG[1]["shield"]  # Erstmal Stage 1 Config

        health_percentage = config.get("health_percentage", 0.5)
        self.max_health = int(player_health * health_percentage)
        self.current_health = self.max_health
        self.damaged_until = 0  # Für visuellen Schaden-Effekt

        # Config für Regeneration und Schadenssystem speichern
        self.damage_reduction = config.get("damage_reduction", 0.9)
        self.regen_rate = config.get("regen_rate", 0.1)
        self.min_health_percentage = config.get("min_health_percentage", 0.3)

        # Für Health-Regeneration
        self._last_regen_time = pygame.time.get_ticks()

        # Power-Up Shield Eigenschaften
        self.is_powerup_shield = is_powerup_shield
        if is_powerup_shield:
            # Gelb färben für Power-Up Shield
            self._apply_yellow_tint()

    def _apply_yellow_tint(self):
        """Färbt das Shield gelb für Power-Up Shields"""
        yellow_tinted = []
        for frame in self.frames:
            # Kopie des Frames erstellen
            tinted = frame.copy()
            # Gelbe Färbung anwenden
            yellow_overlay = pygame.Surface(frame.get_size(), pygame.SRCALPHA)
            yellow_overlay.fill((255, 255, 0, 80))  # Gelb mit 80 Alpha
            tinted.blit(yellow_overlay, (0, 0), special_flags=pygame.BLEND_MULT)
            yellow_tinted.append(tinted)
        self.frames = yellow_tinted

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

        # Health-Regeneration über Zeit
        self._regenerate_health(now)

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

    def _regenerate_health(self, current_time):
        """Regeneriert Schild-Health über Zeit"""
        if self.current_health >= self.max_health:
            return  # Schon bei voller Health

        # Zeit seit letzter Regeneration
        time_diff = current_time - self._last_regen_time
        if time_diff < 100:  # Alle 100ms regenerieren (10 FPS Regeneration)
            return

        # Config laden
        from config.shield import SHIELD_CONFIG
        shield_cfg = SHIELD_CONFIG[1]["shield"]
        regen_rate = shield_cfg.get("regen_rate", 0.2)  # 20% pro Sekunde

        # Health pro Update berechnen (time_diff ist in Millisekunden)
        regen_per_second = self.max_health * regen_rate
        regen_amount = regen_per_second * (time_diff / 1000.0)

        # Health hinzufügen
        self.current_health = min(self.max_health, self.current_health + regen_amount)
        self._last_regen_time = current_time

    def _current_rect(self):
        return self.frames[self._i].get_rect(center=self.center)

    def draw(self, screen):
        if self.done: return
        frame = self.frames[self._i]

        # Alpha basierend auf Health anpassen
        health_percentage = self.get_health_percentage()
        base_alpha = self.alpha

        # Schild wird transparenter bei weniger Health
        alpha = int(base_alpha * (0.3 + 0.7 * health_percentage))

        # Schaden-Effekt: Kurzzeitig rötlich blinken
        now = pygame.time.get_ticks()
        if now < self.damaged_until:
            # Rötlicher Schaden-Effekt
            damage_frame = frame.copy()
            red_overlay = pygame.Surface(frame.get_size(), pygame.SRCALPHA)
            red_overlay.fill((255, 100, 100, 100))
            damage_frame.blit(red_overlay, (0, 0), special_flags=pygame.BLEND_MULT)
            damage_frame.set_alpha(alpha)
            frame = damage_frame
        else:
            frame.set_alpha(alpha)

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

    def take_damage(self, damage):
        """Schild nimmt Schaden und gibt zurück ob es noch aktiv ist"""
        self.current_health -= damage
        self.current_health = max(0, self.current_health)

        # Visueller Schaden-Effekt für 200ms
        self.damaged_until = pygame.time.get_ticks() + 200

        return self.current_health > 0  # True wenn noch aktiv

    def get_health_percentage(self):
        """Gibt Schild-Health als Prozentsatz zurück"""
        return self.current_health / self.max_health if self.max_health > 0 else 0.0

    def is_broken(self):
        """Prüft ob das Schild kaputt ist"""
        return self.current_health <= 0

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
