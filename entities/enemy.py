# entities/enemy.py
import math, random, pygame
from config import WIDTH, HEIGHT
from config.enemy import ENEMY_CONFIG

from entities.projectile import Laser, Rocket, Nuke

KIND2CLS = {"laser": Laser, "rocket": Rocket, "nuke": Nuke}

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
            amp = int(self.move_cfg.get("amp_frac", 0) * WIDTH * 0.5)
            hz  = float(self.move_cfg.get("hz", 0.25))
            offset = int(math.sin(pygame.time.get_ticks()*hz*0.001 + self._phase) * amp)
            self.rect.x = WIDTH//2 + offset - self.rect.width//2

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
        prob = float(self.cfg.get("shoot", {}).get("prob", 0.0))
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
        return (self.rect.right < 0 or self.rect.left > WIDTH or
                self.rect.bottom < 0 or self.rect.top > HEIGHT)

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
