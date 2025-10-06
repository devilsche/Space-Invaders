import math, pygame
from config import WIDTH, HEIGHT, MASTER_VOLUME, MUSIC_VOLUME, SFX_VOLUME
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
        # Unterschiedliche Bilder für Player und Enemy
        if owner == "enemy":
            img = assets["laser_yellow_img"]  # Gelbe Version für Enemies
        else:
            img = assets["laser_img"]         # Normale Version für Player
        
        if owner=="player" and assets.get("laser_sound_start"):
            assets["laser_sound_start"].set_volume(MASTER_VOLUME * SFX_VOLUME)
            assets["laser_sound_start"].play()
        return cls(x, y, vx, vy, img, cfg["dmg"], owner, radius=0, kind="laser", accel=accel)

    def on_hit(self, game, hit_pos):
        frames, fps = _expl_frames(game, "expl_laser")
        ex = Explosion(hit_pos[0], hit_pos[1], frames, fps=fps)
        if game.assets.get("laser_sound_destroy"):
            game.assets["laser_sound_destroy"].set_volume(MASTER_VOLUME * SFX_VOLUME)
            game.assets["laser_sound_destroy"].play()
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
        if owner=="player" and assets.get("rocket_sound_start"):
            assets["rocket_sound_start"].set_volume(MASTER_VOLUME * SFX_VOLUME)
            assets["rocket_sound_start"].play()
        return cls(x, y, vx, vy, img, cfg["dmg"], owner, radius=cfg.get("radius",0), kind="rocket", accel=accel)

    def on_hit(self, game, hit_pos):
        cx, cy = hit_pos
        if game.assets.get("rocket_sound_hit"):
            game.assets["rocket_sound_hit"].set_volume(MASTER_VOLUME * SFX_VOLUME)
            game.assets["rocket_sound_hit"].play()
        _apply_aoe(game, cx, cy, self.radius, self.dmg, "expl_rocket", expl_scale=1.0)
        frames, fps = _expl_frames(game, "expl_rocket")
        game.explosions.append(Explosion(cx, cy, frames, fps=fps, scale=1.4))

class HomingRocket(Projectile):
    kind = "homing_rocket"

    def __init__(self, x, y, vx, vy, img, dmg, owner="player", radius=0, kind="homing_rocket", accel=1.0):
        super().__init__(x, y, vx, vy, img, dmg, owner, radius, kind, accel)
        self.homing = True
        self.homing_strength = 0.3  # Stärkere Lenkung als normale Raketen
        self.max_turn_rate = 0.05   # Maximale Wendegeschwindigkeit pro Frame
        self.launch_time = pygame.time.get_ticks()  # Zeitpunkt des Abschusses
        self.homing_delay = 500  # Millisekunden geradeaus fliegen bevor Suche beginnt
        self.current_target = None  # Aktuelles Ziel
        self.target_lost_time = 0  # Wann das letzte Ziel verloren wurde

    @classmethod
    def create(cls, x, y, assets, owner="player", angle_deg=0):
        cfg    = PROJECTILES_CONFIG.get("homing_rocket", PROJECTILES_CONFIG["rocket"])
        speed  = cfg.get("enemy_speed", cfg["speed"]) if owner=="enemy" else cfg["speed"]
        accel  = cfg.get("enemy_accel", cfg.get("accel",1.0)) if owner=="enemy" else cfg.get("accel",1.0)
        base   = -1 if owner=="player" else +1
        rad    = math.radians(angle_deg)
        vx     =  speed * math.sin(rad)
        vy     =  base  * speed * math.cos(rad)
        img    = assets["homing_rocket_img"]  # Verwendet das spezielle HomingRocket-Bild
        if owner=="player" and assets.get("rocket_sound_start"):
            assets["rocket_sound_start"].set_volume(MASTER_VOLUME * SFX_VOLUME)
            assets["rocket_sound_start"].play()
        return cls(x, y, vx, vy, img, cfg["dmg"], owner, radius=cfg.get("radius",0), kind="homing_rocket", accel=accel)

    def _find_nearest_enemy(self, game, exclude_current=False):
        """Findet das nächstgelegene Enemy zum aktuellen Raketenzentrum"""
        if not hasattr(game, 'enemies') or not game.enemies:
            return None

        my_center = self.rect.center
        nearest_enemy = None
        min_distance = float('inf')

        for enemy in game.enemies:
            # Aktuelles Ziel ausschließen wenn gewünscht
            if exclude_current and enemy == self.current_target:
                continue

            enemy_center = enemy.rect.center
            distance = math.hypot(enemy_center[0] - my_center[0], enemy_center[1] - my_center[1])
            if distance < min_distance:
                min_distance = distance
                nearest_enemy = enemy

        return nearest_enemy

    def _is_target_valid(self, target, game):
        """Prüft ob das aktuelle Ziel noch existiert"""
        return target is not None and hasattr(game, 'enemies') and target in game.enemies

    def update(self, game=None):
        # Normale Beschleunigung
        if self.accel != 1.0:
            self._speed *= self.accel

        # Wärmelenkung nur für Spieler-Raketen
        if self.homing and game and self.owner == "player":
            now = pygame.time.get_ticks()

            # Erst nach Verzögerung mit der Suche beginnen
            if now - self.launch_time < self.homing_delay:
                # Geradeaus fliegen während der Startverzögerung
                self.vx = self._dir[0] * self._speed
                self.vy = self._dir[1] * self._speed
            else:
                # Zielsuche und -verfolgung
                target = None

                # Aktuelles Ziel prüfen
                if self._is_target_valid(self.current_target, game):
                    target = self.current_target
                else:
                    # Ziel verloren oder noch keins -> neues suchen
                    if self.current_target is not None:
                        self.target_lost_time = now
                        self.current_target = None

                    # Neues Ziel suchen
                    target = self._find_nearest_enemy(game)
                    if target:
                        self.current_target = target

                if target:
                    # Richtung zum Ziel berechnen
                    tx, ty = target.rect.center
                    mx, my = self.rect.center
                    target_dx = tx - mx
                    target_dy = ty - my
                    target_dist = math.hypot(target_dx, target_dy)

                    if target_dist > 0:
                        # Normalisierte Zielrichtung
                        target_dir_x = target_dx / target_dist
                        target_dir_y = target_dy / target_dist

                        # Aktuelle Richtung mit Zielrichtung mischen
                        blend_factor = min(self.homing_strength, self.max_turn_rate)
                        new_dir_x = self._dir[0] + (target_dir_x - self._dir[0]) * blend_factor
                        new_dir_y = self._dir[1] + (target_dir_y - self._dir[1]) * blend_factor

                        # Richtung normalisieren
                        new_dir_len = math.hypot(new_dir_x, new_dir_y)
                        if new_dir_len > 0:
                            self._dir = (new_dir_x / new_dir_len, new_dir_y / new_dir_len)
                            self.vx = self._dir[0] * self._speed
                            self.vy = self._dir[1] * self._speed
                else:
                    # Kein Ziel gefunden -> weiterfliegen in aktueller Richtung
                    self.vx = self._dir[0] * self._speed
                    self.vy = self._dir[1] * self._speed
        else:
            # Normale Bewegung ohne Lenkung
            self.vx = self._dir[0] * self._speed
            self.vy = self._dir[1] * self._speed

        # Position aktualisieren
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)

    def offscreen(self):
        # Wärmelenkraketen bleiben länger aktiv als normale Projektile
        margin = 100  # Zusätzlicher Rand
        return (self.rect.right < -margin or self.rect.left > WIDTH + margin or
                self.rect.bottom < -margin or self.rect.top > HEIGHT + margin)

    def draw(self, screen):
        # Einfache und direkte Winkelberechnung
        # Berechne den Winkel basierend auf der Bewegungsrichtung
        angle_rad = math.atan2(-self.vx, -self.vy)  # Beide negativ für korrekte Orientierung
        angle_deg = math.degrees(angle_rad)

        # Rakete rotieren
        rotated_img = pygame.transform.rotate(self.img, angle_deg)
        rotated_rect = rotated_img.get_rect(center=self.rect.center)

        screen.blit(rotated_img, rotated_rect)

    def on_hit(self, game, hit_pos):
        cx, cy = hit_pos
        if game.assets.get("rocket_sound_hit"):
            game.assets["rocket_sound_hit"].set_volume(MASTER_VOLUME * SFX_VOLUME)
            game.assets["rocket_sound_hit"].play()
        _apply_aoe(game, cx, cy, self.radius, self.dmg, "expl_rocket", expl_scale=1.2)
        frames, fps = _expl_frames(game, "expl_rocket")
        game.explosions.append(Explosion(cx, cy, frames, fps=fps, scale=1.6))

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
        if owner=="player" and assets.get("nuke_sound_start"):
            assets["nuke_sound_start"].set_volume(MASTER_VOLUME * SFX_VOLUME)
            assets["nuke_sound_start"].play()
        return cls(x, y, vx, vy, img, cfg["dmg"], owner, radius=cfg.get("radius",0), kind="nuke", accel=accel)

    def on_hit(self, game, hit_pos):
        cx, cy = hit_pos
        if game.assets.get("nuke_sound_hit"):
            game.assets["nuke_sound_hit"].set_volume(MASTER_VOLUME * SFX_VOLUME)
            game.assets["nuke_sound_hit"].play()
        _apply_aoe(game, cx, cy, self.radius, self.dmg, "expl_nuke", expl_scale=2.0)
        now = pygame.time.get_ticks()
        game.flash_until     = now + 350
        game.shake_until     = now + 1000
        game.timescale_until = now + 800
        frames, fps = _expl_frames(game, "expl_nuke")
        game.explosions.append(Explosion(cx, cy, frames, fps=fps, scale=2.5))
