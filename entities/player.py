# entities/player.py
import pygame
from config.ships import SHIP_CONFIG
from config.projectiles import PROJECTILES_CONFIG
from config.ships import SHIP_CONFIG
from entities.projectile import Laser, Rocket, Nuke

WEAPON_CLS = {"laser": Laser, "rocket": Rocket, "nuke": Nuke}

MAX_TILT_DEG = 8          # Rotationsgrenze
TILT_LERP    = 0.25       # Annäherung pro Frame
SQUASH_X     = 0.90       # horizontales Stauchen bei Neigung


class Player:
    def __init__(self, width, height, assets):
        self.assets = assets
        self.stage = 1
        self._last_shots = {}

        cfg = SHIP_CONFIG[self.stage]
        self.speed = cfg.get("speed", 5)

        img = self.assets.get(f"player_stage{self.stage}")
        if img is None:
            raw = pygame.image.load(cfg["img"]).convert_alpha()
            img = pygame.transform.smoothscale(raw, cfg["size"])
        self.base_img = img
        self.rect = img.get_rect(midbottom=(width // 2, height - 50))

        self.tilt_deg = 0.0   # aktueller Winkel
        self.tilt_dir = 0     # -1, 0, +1

    # Hilfen
    def _muzzles(self, weapon: str, amount: int):
        cfg = SHIP_CONFIG[self.stage]
        cx, top = self.rect.centerx, self.rect.top
        offs = (cfg.get("muzzles", {}).get(weapon, []) or [(0, 6)]).copy()
        # falls zu wenig Offsets, zyklisch auffüllen
        i = 0
        out = []
        while len(out) < amount:
            dx, dy = offs[i % len(offs)]
            out.append((cx + dx, top + dy))
            i += 1
        return out[:amount]

    def _angles(self, weapon: str, amount: int):
        angs = SHIP_CONFIG[self.stage].get("angle", {}).get(weapon, []) or [0]
        i = 0
        out = []
        while len(out) < amount:
            out.append(angs[i % len(angs)])
            i += 1
        return out[:amount]

    def _stage_weapons(self):
        w = SHIP_CONFIG[self.stage]["weapons"]
        return {k: 1 for k in w} if isinstance(w, list) else dict(w)

    # API
    def set_stage(self, stage: int):
        self.stage = stage
        cfg = SHIP_CONFIG[self.stage]
        self.speed = cfg.get("speed", self.speed)

        img = self.assets.get(f"player_stage{self.stage}")
        if img is None:
            raw = pygame.image.load(cfg["img"]).convert_alpha()
            img = pygame.transform.smoothscale(raw, cfg["size"])

        center = self.rect.center
        self.base_img = img
        self.rect = self.base_img.get_rect(center=center)
        self._last_shots.clear()

    def handle_input(self, keys, width, height):
        hdir = 0
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
            hdir = -1
        if keys[pygame.K_RIGHT] and self.rect.right < width:
            self.rect.x += self.speed
            hdir = 1
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < height:
            self.rect.y += self.speed

        # Bounds-Hardening
        self.rect.clamp_ip(pygame.Rect(0, 0, width, height))

        self.tilt_dir = hdir
        target = hdir * MAX_TILT_DEG
        self.tilt_deg += (target - self.tilt_deg) * TILT_LERP

    def shoot_weapon(self, weapon: str, amount: int = None):
        # Stage-Gate
        allowed = self._stage_weapons().get(weapon, 0)
        if allowed <= 0:
            return []
        shots, now = [], pygame.time.get_ticks()
        cfg = PROJECTILES_CONFIG[weapon]
        last = self._last_shots.get(weapon, 0)
        if now - last < cfg["cooldown"]:
            return shots
        amount = max(1, amount if amount is not None else allowed)
        coords = self._muzzles(weapon, amount)
        angles = self._angles(weapon, amount)
        for (mx, my), ang in zip(coords, angles):
            shots.append(WEAPON_CLS[weapon].create(mx, my, self.assets, owner="player", angle_deg=ang))
        self._last_shots[weapon] = now
        return shots


    def draw(self, screen):
        img = self.base_img
        if self.tilt_dir != 0:
            w, h = img.get_width(), img.get_height()
            img = pygame.transform.smoothscale(img, (int(w * SQUASH_X), h))

        # Neigung. Minus dreht optisch nach links bei hdir<0.
        rotated = pygame.transform.rotate(img, -self.tilt_deg)
        r = rotated.get_rect(center=self.rect.center)
        screen.blit(rotated, r)
