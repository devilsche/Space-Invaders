import math, pygame
from config import WIDTH, HEIGHT
from config.projectile import PROJECTILES_CONFIG
from entities.explosion import Explosion

def _expl_frames(game, key):
    return game.assets.get(key, []), game.assets.get(f"{key}_fps", 24)

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
                frames, fps = _expl_frames(game, expl_key)
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
                frames, fps = _expl_frames(game, expl_key)
                game.explosions.append(Explosion(bx, by, frames, fps=fps, scale=expl_scale))
                game.boss = None

class Projectile:
    __slots__ = ("img","rect","vx","vy","dmg","owner","radius","kind","accel","_dir","_speed")

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
        sp = math.hypot(self.vx, self.vy)
        if sp == 0:
            self._dir = (0.0, -1.0); self._speed = 0.0
        else:
            self._dir = (self.vx/sp, self.vy/sp); self._speed = sp

    def update(self):
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

    def on_hit(self, game, hit_pos):  # optional überschreiben
        pass

class Laser(Projectile):
    kind = "laser"
    @classmethod
    def create(cls, x, y, assets, owner="player", angle_deg=0):
        cfg    = PROJECTILES_CONFIG["laser"]
        speed  = cfg.get("enemy_speed", cfg["speed"]) if owner=="enemy" else cfg["speed"]
        accel  = cfg.get("enemy_accel", cfg.get("accel",1.0)) if owner=="enemy" else cfg.get("accel",1.0)
        base   = -1 if owner=="player" else +1
        rad    = math.radians(angle_deg)
        vx     =  speed * math.sin(rad)
        vy     =  base  * speed * math.cos(rad)
        img    = assets["laser_img"]
        if owner=="player" and assets.get("laser_sound_start"): assets["laser_sound_start"].play()
        return cls(x, y, vx, vy, img, cfg["dmg"], owner, radius=0, kind="laser", accel=accel)

    def on_hit(self, game, hit_pos):
        frames, fps = _expl_frames(game, "expl_laser")
        ex = Explosion(hit_pos[0], hit_pos[1], frames, fps=fps)
        if game.assets.get("laser_sound_destroy"): game.assets["laser_sound_destroy"].play()
        keep = game.assets.get("expl_laser_keep")
        if keep:
            ex.frames = ex.frames[:keep]


        game.explosions.append(ex)

class Rocket(Projectile):
    kind = "rocket"
    @classmethod
    def create(cls, x, y, assets, owner="player", angle_deg=0):
        cfg    = PROJECTILES_CONFIG["rocket"]
        speed  = cfg.get("enemy_speed", cfg["speed"]) if owner=="enemy" else cfg["speed"]
        accel  = cfg.get("enemy_accel", cfg.get("accel",1.0)) if owner=="enemy" else cfg.get("accel",1.0)
        base   = -1 if owner=="player" else +1
        rad    = math.radians(angle_deg)
        vx     =  speed * math.sin(rad)
        vy     =  base  * speed * math.cos(rad)
        img    = assets["rocket_img"]
        if owner=="player" and assets.get("rocket_sound_start"): assets["rocket_sound_start"].play()
        return cls(x, y, vx, vy, img, cfg["dmg"], owner, radius=cfg.get("radius",0), kind="rocket", accel=accel)

    def on_hit(self, game, hit_pos):
        cx, cy = hit_pos
        if game.assets.get("rocket_sound_hit"): game.assets["rocket_sound_hit"].play()
        _apply_aoe(game, cx, cy, self.radius, self.dmg, "expl_rocket", expl_scale=1.0)
        frames, fps = _expl_frames(game, "expl_rocket")
        game.explosions.append(Explosion(cx, cy, frames, fps=fps, scale=1.4))

class Nuke(Projectile):
    kind = "nuke"
    @classmethod
    def create(cls, x, y, assets, owner="player", angle_deg=0):
        cfg    = PROJECTILES_CONFIG["nuke"]
        speed  = cfg.get("enemy_speed", cfg["speed"]) if owner=="enemy" else cfg["speed"]
        accel  = cfg.get("enemy_accel", cfg.get("accel",1.0)) if owner=="enemy" else cfg.get("accel",1.0)
        base   = -1 if owner=="player" else +1
        rad    = math.radians(angle_deg)
        vx     =  speed * math.sin(rad)
        vy     =  base  * speed * math.cos(rad)
        img    = assets["nuke_img"]
        if owner=="player" and assets.get("nuke_sound_start"): assets["nuke_sound_start"].play()
        return cls(x, y, vx, vy, img, cfg["dmg"], owner, radius=cfg.get("radius",0), kind="nuke", accel=accel)

    def on_hit(self, game, hit_pos):
        cx, cy = hit_pos
        if game.assets.get("nuke_sound_hit"): game.assets["nuke_sound_hit"].play()
        _apply_aoe(game, cx, cy, self.radius, self.dmg, "expl_nuke", expl_scale=2.0)
        now = pygame.time.get_ticks()
        game.flash_until     = now + 350
        game.shake_until     = now + 1000
        game.timescale_until = now + 800
        frames, fps = _expl_frames(game, "expl_nuke")
        game.explosions.append(Explosion(cx, cy, frames, fps=fps, scale=2.5))
