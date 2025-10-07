# entities/enemy.py
import math, random, pygame
from config import WIDTH, HEIGHT
from config.enemy import ENEMY_CONFIG

from entities.projectile import Laser, Rocket, Nuke, Blaster, HomingRocket

KIND2CLS = {"laser": Laser, "rocket": Rocket, "nuke": Nuke, "blaster": Blaster, "homing_rocket": HomingRocket}

BAR_W = 40
BAR_H = 5
BAR_PAD_Y = 6
HIT_SHOW_MS = 800

def _norm_weapons(w):
    """Beliebiges weapons-Feld -> dict {name: count}."""
    if isinstance(w, dict):
        out = {}
        for k, v in w.items():
            try:
                n = int(v)
            except Exception:
                n = 1
            if n > 0:
                out[str(k)] = n
        return out
    if isinstance(w, str):
        return {w: 1}
    if isinstance(w, (list, tuple)):
        flat = []
        for item in w:
            if isinstance(item, (list, tuple)):
                flat.extend(item)
            else:
                flat.append(item)
        out = {}
        for k in flat:
            out[str(k)] = out.get(str(k), 0) + 1
        return out
    return {}

class Enemy:
    def __init__(self, etype: str, assets, x=None, y=None):
        if etype not in ENEMY_CONFIG:
            raise ValueError(f"Unknown enemy type: {etype}")
        self.assets = assets
        self.etype  = etype
        self.cfg    = ENEMY_CONFIG[etype]

        # Bild
        self.img = assets.get(f"enemy_{etype}")
        if self.img is None:
            raw = pygame.image.load(self.cfg["img"]).convert_alpha()
            self.img = pygame.transform.smoothscale(raw, self.cfg["size"])

        # Stats
        self.max_hp = int(self.cfg["hp"])
        self.hp     = int(self.cfg["hp"])
        self.points = int(self.cfg["points"])

        # Position
        spawn_y = self.cfg["spawn"].get("y", 0)
        self.rect = self.img.get_rect()
        if x is None: x = self.cfg["formation"].get("margin_x", 0)
        if y is None: y = spawn_y
        self.rect.topleft = (x, y)

        # Bewegung
        self.move_cfg = self.cfg["move"]
        self._phase   = random.uniform(0, 2*math.pi)

        # Waffen normalisieren + Cooldowns
        self.weapons = _norm_weapons(self.cfg.get("weapons", {"laser": 1}))
        self._last   = {w: 0 for w in self.weapons.keys()}

        # HP-Bar Timer
        self._show_hp_until = 0

    # --- Bewegung ---
    def update(self, dx=0):
        if self.move_cfg["type"] == "grid":
            self.rect.x += dx
        elif self.move_cfg["type"] == "float":
            # Verwende aktuelle Bildschirmgröße für float-Bewegung
            screen = pygame.display.get_surface()
            if screen:
                current_width, _ = screen.get_size()
                amp = int(self.move_cfg.get("amp_frac", 0) * current_width * 0.5)
                hz  = float(self.move_cfg.get("hz", 0.25))
                offset = int(math.sin(pygame.time.get_ticks()*hz*0.001 + self._phase) * amp)
                self.rect.x = current_width//2 + offset - self.rect.width//2
            else:
                # Fallback zu Konstanten
                amp = int(self.move_cfg.get("amp_frac", 0) * WIDTH * 0.5)
                hz  = float(self.move_cfg.get("hz", 0.25))
                offset = int(math.sin(pygame.time.get_ticks()*hz*0.001 + self._phase) * amp)
                self.rect.x = WIDTH//2 + offset - self.rect.width//2
        elif self.move_cfg["type"] == "fly_in":
            # Fliegt von oben rein und folgt dann einer Laufbahn
            self._update_fly_in()

    def _update_fly_in(self):
        """Bewegung für 'fly_in' Typ - von oben reinfliegend mit individueller Laufbahn"""
        now = pygame.time.get_ticks()

        # Zeit seit Spawn
        if not hasattr(self, '_spawn_time'):
            self._spawn_time = now
            self._target_y = self.move_cfg.get("target_y", 100)  # Ziel Y-Position
            self._path_type = self.move_cfg.get("path", "straight")  # Laufbahn-Typ
            self._speed = self.move_cfg.get("speed", 2)

        elapsed = (now - self._spawn_time) / 1000.0  # Sekunden

        # Phase 1: Von oben einfliegend
        if self.rect.y < self._target_y:
            self.rect.y += self._speed * 2  # Schneller von oben

        # Phase 2: Horizontale Laufbahn
        else:
            if self._path_type == "straight":
                self.rect.x += self._speed * (1 if self._phase > 0 else -1)
            elif self._path_type == "sine":
                # Sinusförmige Bewegung
                amp = self.move_cfg.get("amplitude", 50)
                frequency = self.move_cfg.get("frequency", 0.5)
                base_x = getattr(self, '_base_x', self.rect.x)
                if not hasattr(self, '_base_x'):
                    self._base_x = base_x
                self.rect.x = base_x + int(amp * math.sin(elapsed * frequency + self._phase))
            elif self._path_type == "circle":
                # Kreisförmige Bewegung (sanfter)
                radius = self.move_cfg.get("radius", 40)  # Kleinerer Radius
                frequency = self.move_cfg.get("frequency", 0.8)  # Schnellere Frequenz
                center_x = getattr(self, '_center_x', self.rect.x)
                center_y = getattr(self, '_center_y', self.rect.y)
                if not hasattr(self, '_center_x'):
                    self._center_x = center_x
                    self._center_y = center_y

                angle = elapsed * frequency + self._phase
                self.rect.x = center_x + int(radius * math.cos(angle))
                # Sehr kleine Y-Variation für sanfte Wellenbewegung
                self.rect.y = center_y + int(radius * math.sin(angle) * 0.2)

    def drop(self, dy):
        self.rect.y += dy

    # --- Schießen (nur shoot_weapon) ---
    def shoot_weapon(self, weapon: str, amount: int = 1):
        import pygame, random
        from config.projectile import PROJECTILES_CONFIG

        # 1) Cooldown check
        now = pygame.time.get_ticks()
        cd  = PROJECTILES_CONFIG[weapon]["cooldown"]
        last = self._last.get(weapon, 0)
        if now - last < cd:
            return []

        # 2) Probability check (aus ENEMY_CONFIG)
        # Erst individuelle Waffen-Wahrscheinlichkeit prüfen, dann fallback auf globale
        shoot_cfg = self.cfg.get("shoot", {})
        weapon_probs = shoot_cfg.get("weapon_probs", {})
        prob = weapon_probs.get(weapon) or shoot_cfg.get("prob", 0.0)
        prob = float(prob)
        if prob <= 0.0 or random.random() >= prob:
            return []

        # 3) Winkel anwenden
        angles = self.cfg.get("angle", {}).get(weapon, []) or [0]
        cls = KIND2CLS[weapon]
        shots = []
        use_amt = max(1, int(amount))
        for i in range(use_amt):
            ang = angles[i % len(angles)]
            shots.append(
                cls.create(
                    self.rect.centerx,
                    self.rect.bottom,
                    self.assets,
                    owner="enemy",
                    angle_deg=ang
                )
            )

        self._last[weapon] = now
        return shots

    def offscreen(self):
        # Für fly_in Enemies: vollständige Bildschirmrand-Prüfung mit aktueller Bildschirmgröße
        if self.move_cfg.get("type") == "fly_in":
            screen = pygame.display.get_surface()
            if screen:
                current_width, current_height = screen.get_size()
                return (self.rect.right < -50 or self.rect.left > current_width + 50 or
                        self.rect.bottom < -50 or self.rect.top > current_height + 50)
            else:
                # Fallback zu Konstanten
                return (self.rect.right < -50 or self.rect.left > WIDTH + 50 or
                        self.rect.bottom < -50 or self.rect.top > HEIGHT + 50)
        # Für normale Enemies: nur oben raus
        return self.rect.bottom < 0

    # --- Treffer/HP ---
    def take_damage(self, dmg: int) -> bool:
        self.hp = max(0, self.hp - int(dmg))
        self._show_hp_until = pygame.time.get_ticks() + HIT_SHOW_MS
        return self.hp <= 0

    def _draw_hp_bar(self, screen):
        cx = self.rect.centerx
        top = self.rect.top - BAR_PAD_Y - BAR_H
        x = cx - BAR_W // 2
        pygame.draw.rect(screen, (40, 40, 40), (x, top, BAR_W, BAR_H))
        ratio = 0 if self.max_hp == 0 else self.hp / self.max_hp
        fill_w = int(BAR_W * ratio)
        color = (200, 60, 60) if ratio < 0.35 else (220, 180, 50) if ratio < 0.7 else (60, 200, 60)
        if fill_w > 0:
            pygame.draw.rect(screen, color, (x, top, fill_w, BAR_H))
        pygame.draw.rect(screen, (0, 0, 0), (x, top, BAR_W, BAR_H), 1)

    def draw(self, screen):
        screen.blit(self.img, self.rect)
        if pygame.time.get_ticks() < self._show_hp_until:
            self._draw_hp_bar(screen)
