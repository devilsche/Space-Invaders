# entities/projectile.py
import math
import pygame
from config import WIDTH, HEIGHT
from config.projectiles import PROJECTILES_CONFIG
from entities.explosion import Explosion

def _apply_aoe(game, cx, cy, radius, max_damage, expl_key: str, expl_scale: float = 1.0):
    # Feinde
    for en in game.enemies[:]:
        ex, ey = en.rect.center
        dist = math.hypot(ex - cx, ey - cy)
        if dist <= radius:
            dmg = int(max_damage * (1 - dist / radius))
            if dmg > 0 and en.take_damage(dmg):
                game.score += en.points
                game.highscore = max(game.highscore, game.score)
                frames = game.assets.get(expl_key, [])
                fps = game.assets.get(f"{expl_key}_fps", 24)
                game.explosions.append(Explosion(ex, ey, frames, fps=fps, scale=expl_scale))
                if en in game.enemies:
                    game.enemies.remove(en)
    # Boss optional
    if getattr(game, "boss", None):
        bx, by = game.boss.rect.center
        dist = math.hypot(bx - cx, by - cy)
        if dist <= radius:
            dmg = int(max_damage * (1 - dist / radius))
            if game.boss.take_damage(dmg):
                game.score += getattr(game.boss, "points", 600)
                game.highscore = max(game.highscore, game.score)
                frames = game.assets.get(expl_key, [])
                fps = game.assets.get(f"{expl_key}_fps", 24)
                game.explosions.append(Explosion(bx, by, frames, fps=fps, scale=expl_scale))
                game.boss = None




class Projectile:
    __slots__ = ("img","rect","vx","vy","dmg","owner","radius","kind", "accel","_dir","_speed")

    def __init__(self, x, y, vx, vy, img, dmg, owner="player", radius=0, kind="generic", accel=1.0):
        self.img   = img
        self.rect  = img.get_rect(center=(x, y))
        self.vx    = float(vx)
        self.vy    = float(vy)
        self.dmg   = int(dmg)
        self.owner = owner
        self.radius= int(radius)
        self.kind  = kind
        self.accel = float(accel)

        # Richtungs- und Skalar-Speed ableiten
        sp = math.hypot(self.vx, self.vy)
        if sp == 0:
            self._dir = (0.0, -1.0)  # Fallback
            self._speed = 0.0
        else:
            self._dir = (self.vx / sp, self.vy / sp)  # normiert
            self._speed = sp

    def update(self):
        # Beschleunigung skaliert NUR den Skalar-Speed, Winkel bleibt konstant
        if self.accel != 1.0:
            self._speed *= self.accel
            self.vx = self._dir[0] * self._speed
            self.vy = self._dir[1] * self._speed

        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)


    def offscreen(self):
        return (self.rect.right < 0 or self.rect.left > WIDTH or
                self.rect.bottom < 0 or self.rect.top > HEIGHT)

    def draw(self, screen):
        screen.blit(self.img, self.rect)

    def on_hit(self, game, hit_pos):
        pass


# Laser
class Laser(Projectile):
    kind = "laser"

    @classmethod
    def create(cls, x, y, assets, owner="player", angle_deg=0):
        cfg    = PROJECTILES_CONFIG["laser"]
        speed  = cfg.get("enemy_speed", cfg["speed"]) if owner == "enemy" else cfg["speed"]
        accel  = cfg.get("enemy_accel", cfg.get("accel", 1.0)) if owner == "enemy" else cfg.get("accel", 1.0)
        base   = -1 if owner == "player" else +1
        rad    = math.radians(angle_deg)
        vx     = speed * math.sin(rad)
        vy     = base * speed * math.cos(rad)
        img    = assets["laser_img"]
        if owner == "player" and assets.get("laser_sound_start"):
            assets["laser_sound_start"].play()
        return cls(x, y, vx, vy, img, cfg["dmg"], owner, radius=0, kind="laser", accel=accel)


# Rocket
class Rocket(Projectile):
    kind = "rocket"

    @classmethod
    def create(cls, x, y, assets, owner="player", angle_deg=0):
        cfg    = PROJECTILES_CONFIG["rocket"]
        speed  = cfg.get("enemy_speed", cfg["speed"]) if owner == "enemy" else cfg["speed"]
        accel  = cfg.get("enemy_accel", cfg.get("accel", 1.0)) if owner == "enemy" else cfg.get("accel", 1.0)
        base   = -1 if owner == "player" else +1
        rad    = math.radians(angle_deg)
        vx     = speed * math.sin(rad)
        vy     = base * speed * math.cos(rad)
        img    = assets["rocket_img"]
        if owner == "player" and assets.get("rocket_sound_start"):
            assets["rocket_sound_start"].play()
        return cls(x, y, vx, vy, img, cfg["dmg"], owner, radius=cfg.get("radius",0), kind="rocket", accel=accel)


# Nuke
class Nuke(Projectile):
    kind = "nuke"

    @classmethod
    def create(cls, x, y, assets, owner="player", angle_deg=0):
        cfg    = PROJECTILES_CONFIG["nuke"]
        speed  = cfg.get("enemy_speed", cfg["speed"]) if owner == "enemy" else cfg["speed"]
        accel  = cfg.get("enemy_accel", cfg.get("accel", 1.0)) if owner == "enemy" else cfg.get("accel", 1.0)
        base   = -1 if owner == "player" else +1
        rad    = math.radians(angle_deg)
        vx     = speed * math.sin(rad)
        vy     = base * speed * math.cos(rad)
        img    = assets["nuke_img"]
        if owner == "player" and assets.get("nuke_sound_start"):
            assets["nuke_sound_start"].play()
        return cls(x, y, vx, vy, img, cfg["dmg"], owner, radius=cfg.get("radius",0), kind="nuke", accel=accel)
