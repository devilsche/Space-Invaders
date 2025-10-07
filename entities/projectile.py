import math, pygame
from config import WIDTH, HEIGHT, MASTER_VOLUME, MUSIC_VOLUME, SFX_VOLUME
from config.weapon import PROJECTILES_CONFIG
from entities.explosion import Explosion

def _expl_frames(game, key):
    return game.assets.get(key, []), game.assets.get(f"{key}_fps", 24)

def _apply_aoe(game, cx, cy, radius, max_damage, expl_key: str, expl_scale: float = 1.0):
    # Sammle alle zu zerstörenden Gegner zuerst (Performance-Optimierung)
    enemies_to_destroy = []

    # Normale Feinde
    for en in game.enemies[:]:
        ex, ey = en.rect.center
        dist = math.hypot(ex - cx, ey - cy)
        if dist <= radius:
            dmg = int(max_damage * (1 - dist / radius))
            if dmg > 0 and en.take_damage(dmg):
                game.score += en.points
                game.highscore = max(game.highscore, game.score)
                # Kill-Counter erhöhen
                if hasattr(game, '_total_kills'):
                    game._total_kills += 1
                # Power-Up Drop-Chance prüfen
                game._try_drop_powerup(ex, ey)
                enemies_to_destroy.append((en, ex, ey, "enemies"))

    # Batch-Entfernung und Explosion-Erstellung
    frames, fps = _expl_frames(game, expl_key)
    for en, ex, ey, list_type in enemies_to_destroy:
        game.explosion_manager.add_explosion(ex, ey, frames, fps=fps, scale=expl_scale)
        if en in game.enemies:
            game.enemies.remove(en)

    # Fly-In Feinde
    fly_in_enemies_to_destroy = []
    if hasattr(game, 'fly_in_enemies'):
        for en in game.fly_in_enemies[:]:
            ex, ey = en.rect.center
            dist = math.hypot(ex - cx, ey - cy)
            if dist <= radius:
                dmg = int(max_damage * (1 - dist / radius))
                if dmg > 0 and en.take_damage(dmg):
                    game.score += en.points
                    game.highscore = max(game.highscore, game.score)
                    # Kill-Counter erhöhen
                    if hasattr(game, '_total_kills'):
                        game._total_kills += 1
                    # Power-Up Drop-Chance prüfen
                    game._try_drop_powerup(ex, ey)
                    fly_in_enemies_to_destroy.append((en, ex, ey))

        # Batch-Entfernung für Fly-In Enemies
        for en, ex, ey in fly_in_enemies_to_destroy:
            game.explosion_manager.add_explosion(ex, ey, frames, fps=fps, scale=expl_scale)
            if en in game.fly_in_enemies:
                game.fly_in_enemies.remove(en)
                # Count dekrementieren
                if hasattr(game, '_fly_in_spawn_count'):
                    game._fly_in_spawn_count = max(0, game._fly_in_spawn_count - 1)
    # Boss optional
    if getattr(game, "boss", None):
        bx, by = game.boss.rect.center
        dist = math.hypot(bx - cx, by - cy)
        if dist <= radius:
            dmg = int(max_damage * (1 - dist / radius))
            if game.boss.take_damage(dmg):
                game.score += getattr(game.boss, "points", 600)
                game.highscore = max(game.highscore, game.score)
                # Power-Up Drop-Chance prüfen (Boss kann auch Power-Ups droppen)
                game._try_drop_powerup(bx, by)
                game.explosion_manager.add_explosion(bx, by, frames, fps=fps, scale=expl_scale)
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
        # Verwende aktuelle Bildschirmgröße statt Konstanten
        screen = pygame.display.get_surface()
        if screen:
            current_width, current_height = screen.get_size()
            return (self.rect.right < 0 or self.rect.left > current_width or
                    self.rect.bottom < 0 or self.rect.top > current_height)
        else:
            # Fallback zu Konstanten falls kein Screen verfügbar
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
        if game.assets.get("laser_sound_destroy"):
            game.assets["laser_sound_destroy"].set_volume(MASTER_VOLUME * SFX_VOLUME)
            game.assets["laser_sound_destroy"].play()
        keep = game.assets.get("expl_laser_keep")
        if keep:
            frames = frames[:keep]

        game.explosion_manager.add_explosion(hit_pos[0], hit_pos[1], frames, fps=fps)

class DoubleLaser(Projectile):
    kind = "double_laser"
    @classmethod
    def create(cls, x, y, assets, owner="player", angle_deg=0):
        cfg    = PROJECTILES_CONFIG["laser"]  # Verwende normale Laser-Konfiguration
        speed  = cfg.get("enemy_speed", cfg["speed"]) if owner=="enemy" else cfg["speed"]
        accel  = cfg.get("enemy_accel", cfg.get("accel",1.0)) if owner=="enemy" else cfg.get("accel",1.0)
        base   = -1 if owner=="player" else +1
        rad    = math.radians(angle_deg)
        vx     =  speed * math.sin(rad)
        vy     =  base  * speed * math.cos(rad)

        # Double Laser Bild
        img = assets.get("double_laser_img", assets.get("laser_img"))  # Fallback auf normalen Laser

        if owner=="player" and assets.get("laser_sound_start"):
            assets["laser_sound_start"].set_volume(MASTER_VOLUME * SFX_VOLUME)
            assets["laser_sound_start"].play()
        return cls(x, y, vx, vy, img, cfg["dmg"], owner, kind="double_laser", accel=accel)

    def on_hit(self, game, hit_pos):
        frames, fps = _expl_frames(game, "expl_laser")
        if game.assets.get("laser_sound_destroy"):
            game.assets["laser_sound_destroy"].set_volume(MASTER_VOLUME * SFX_VOLUME)
            game.assets["laser_sound_destroy"].play()
        keep = game.assets.get("expl_laser_keep")
        if keep:
            frames = frames[:keep]
        game.explosion_manager.add_explosion(hit_pos[0], hit_pos[1], frames, fps=fps)

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

    def draw(self, screen):
        # Raketen rotieren basierend auf ihrer Bewegungsrichtung
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
        _apply_aoe(game, cx, cy, self.radius, self.dmg, "expl_rocket", expl_scale=1.0)
        frames, fps = _expl_frames(game, "expl_rocket")
        game.explosion_manager.add_explosion(cx, cy, frames, fps=fps, scale=1.4)

class Blaster(Projectile):
    kind = "blaster"

    def __init__(self, x, y, vx, vy, img, dmg, owner="enemy", radius=0, kind="blaster", accel=1.0):
        super().__init__(x, y, vx, vy, img, dmg, owner, radius, kind, accel)
        self.homing = True
        self.homing_strength  = 0.12  # Noch schwächere Lenkung
        self.max_turn_rate    = 0.06  # Sehr begrenzte Wendegeschwindigkeit
        self.launch_time      = pygame.time.get_ticks()
        self.homing_delay     = 200   # Kurze Verzögerung
        self.homing_duration  = 4000  # Nur 2 Sekunden lang lenken
        self.current_target   = None
        self.target_lost_time = 0
        self.max_course_corrections = 10  # Maximal 8 Richtungsänderungen
        self.course_corrections = 0

    @classmethod
    def create(cls, x, y, assets, owner="player", angle_deg=0):
        cfg = PROJECTILES_CONFIG["blaster"]
        speed = cfg.get("enemy_speed", cfg["speed"]) if owner=="enemy" else cfg["speed"]
        accel = cfg.get("enemy_accel", cfg.get("accel",1.0)) if owner=="enemy" else cfg.get("accel",1.0)
        base = -1 if owner=="player" else +1
        rad = math.radians(angle_deg)
        vx = speed * math.sin(rad)
        vy = base * speed * math.cos(rad)

        # Blaster-Bild verwenden
        img = assets["blaster_img"]

        return cls(x, y, vx, vy, img, cfg["dmg"], owner, radius=0, kind="blaster", accel=accel)

    def _find_nearest_target(self, game):
        """Findet das nächste Ziel für Blaster"""
        if self.owner == "player":
            # Player-Blaster suchen Enemies - alle Listen prüfen
            all_enemies = []

            # Normale Enemies
            if hasattr(game, 'enemies') and game.enemies:
                all_enemies.extend(game.enemies)

            # Fly-in Enemies
            if hasattr(game, 'fly_in_enemies') and game.fly_in_enemies:
                all_enemies.extend(game.fly_in_enemies)

            # Boss
            if hasattr(game, 'boss') and game.boss:
                all_enemies.append(game.boss)

            if not all_enemies:
                return None

            closest_enemy = None
            closest_dist = float('inf')
            mx, my = self.rect.center

            for enemy in all_enemies:
                if hasattr(enemy, 'rect'):
                    ex, ey = enemy.rect.center
                    dist = math.hypot(ex - mx, ey - my)
                    if dist < closest_dist:
                        closest_dist = dist
                        closest_enemy = enemy

            return closest_enemy
        elif self.owner == "enemy":
            # Enemy-Blaster suchen Player
            if hasattr(game, 'player') and not getattr(game, 'player_dead', False):
                return game.player
        return None

    def _is_target_valid(self, target, game):
        """Prüft ob das Ziel noch gültig ist"""
        if self.owner == "player":
            # Prüfe alle Enemy-Listen
            all_enemies = []
            if hasattr(game, 'enemies'):
                all_enemies.extend(game.enemies)
            if hasattr(game, 'fly_in_enemies'):
                all_enemies.extend(game.fly_in_enemies)
            if hasattr(game, 'boss') and game.boss:
                all_enemies.append(game.boss)
            return target in all_enemies
        elif self.owner == "enemy":
            return target == getattr(game, 'player', None) and not getattr(game, 'player_dead', False)
        return False

    def update(self, game=None):
        # Normale Beschleunigung
        if self.accel != 1.0:
            self._speed *= self.accel

        # Lenkung für alle Blaster (Player und Enemy)
        if self.homing and game:
            now = pygame.time.get_ticks()

            # Prüfe ob Lenkung noch aktiv sein soll
            time_since_launch = now - self.launch_time

            # Kurze Verzögerung vor Lenkbeginn
            if time_since_launch < self.homing_delay:
                self.vx = self._dir[0] * self._speed
                self.vy = self._dir[1] * self._speed
            # Lenkung nur für begrenzte Zeit und begrenzte Korrekturen
            elif (time_since_launch < self.homing_delay + self.homing_duration and
                  self.course_corrections < self.max_course_corrections):

                target = None

                # Aktuelles Ziel prüfen
                if self._is_target_valid(self.current_target, game):
                    target = self.current_target
                else:
                    # Neues Ziel suchen
                    target = self._find_nearest_target(game)
                    if target:
                        self.current_target = target

                if target:
                    # Richtung zum Player berechnen
                    tx, ty = target.rect.center
                    mx, my = self.rect.center
                    target_dx = tx - mx
                    target_dy = ty - my
                    target_dist = math.hypot(target_dx, target_dy)

                    if target_dist > 0:
                        # Normalisierte Zielrichtung
                        target_dir_x = target_dx / target_dist
                        target_dir_y = target_dy / target_dist

                        # Prüfe ob eine Richtungsänderung nötig ist
                        angle_diff = abs(math.atan2(target_dir_y, target_dir_x) - math.atan2(self._dir[1], self._dir[0]))
                        if angle_diff > 0.1:  # Nur bei signifikantem Richtungsunterschied
                            # Sanfte Lenkung - sehr schwach
                            blend_factor = min(self.homing_strength, self.max_turn_rate)
                            new_dir_x = self._dir[0] + (target_dir_x - self._dir[0]) * blend_factor
                            new_dir_y = self._dir[1] + (target_dir_y - self._dir[1]) * blend_factor

                            # Richtung normalisieren
                            new_dir_len = math.hypot(new_dir_x, new_dir_y)
                            if new_dir_len > 0:
                                self._dir = (new_dir_x / new_dir_len, new_dir_y / new_dir_len)
                                self.vx = self._dir[0] * self._speed
                                self.vy = self._dir[1] * self._speed
                                self.course_corrections += 1  # Korrekturen zählen
                        else:
                            # Geradeaus wenn Richtung passt
                            self.vx = self._dir[0] * self._speed
                            self.vy = self._dir[1] * self._speed
                else:
                    # Kein Ziel -> geradeaus
                    self.vx = self._dir[0] * self._speed
                    self.vy = self._dir[1] * self._speed
            else:
                # Nach Homing-Zeit oder max Korrekturen -> geradeaus
                self.vx = self._dir[0] * self._speed
                self.vy = self._dir[1] * self._speed
        else:
            # Kein Game-Context -> geradeaus
            self.vx = self._dir[0] * self._speed
            self.vy = self._dir[1] * self._speed

        # Bewegung ausführen (von Basisklasse)
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)

    def on_hit(self, game, hit_pos):
        frames, fps = _expl_frames(game, "expl_laser")
        ex = Explosion(hit_pos[0], hit_pos[1], frames, fps=fps)
        if game.assets.get("laser_sound_destroy"):
            game.assets["laser_sound_destroy"].set_volume(MASTER_VOLUME * SFX_VOLUME)
            game.assets["laser_sound_destroy"].play()
        keep = game.assets.get("expl_laser_keep")
        if keep:
            ex.frames = ex.frames[:keep]
        game.explosion_manager.add_explosion(hit_pos[0], hit_pos[1], frames, fps=fps)

class HomingRocket(Projectile):
    kind = "homing_rocket"

    def __init__(self, x, y, vx, vy, img, dmg, owner="player", radius=0, kind="homing_rocket", accel=1.0):
        super().__init__(x, y, vx, vy, img, dmg, owner, radius, kind, accel)
        self.homing = True
        self.homing_strength  = 0.3                     # Stärkere      Lenkung              als normale Raketen
        self.max_turn_rate    = 0.25                    # Maximale      Wendegeschwindigkeit pro Frame
        self.launch_time      = pygame.time.get_ticks() # Zeitpunkt     des                  Abschusses
        self.homing_delay     = 300                     # Millisekunden geradeaus            fliegen bevor Suche beginnt
        self.current_target   = None                    # Aktuelles     Ziel
        self.target_lost_time = 0                       # Wann          das                  letzte Ziel verloren wurde

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

    def _find_nearest_target(self, game, exclude_current=False):
        """Findet das nächste Ziel basierend auf dem Owner"""
        if self.owner == "player":
            # Player-Raketen zielen auf Enemies
            all_enemies = []
            if hasattr(game, 'enemies') and game.enemies:
                all_enemies.extend(game.enemies)
            if hasattr(game, 'fly_in_enemies') and game.fly_in_enemies:
                all_enemies.extend(game.fly_in_enemies)

            if not all_enemies:
                return None

            my_center = self.rect.center
            nearest_target = None
            min_distance = float('inf')

            for enemy in all_enemies:
                # Aktuelles Ziel ausschließen wenn gewünscht
                if exclude_current and enemy == self.current_target:
                    continue

                enemy_center = enemy.rect.center
                distance = math.hypot(enemy_center[0] - my_center[0], enemy_center[1] - my_center[1])
                if distance < min_distance:
                    min_distance = distance
                    nearest_target = enemy

            return nearest_target

        elif self.owner == "enemy":
            # Enemy-Raketen zielen auf Player
            if hasattr(game, 'player') and not getattr(game, 'player_dead', False):
                return game.player
            return None

    def _is_target_valid(self, target, game):
        """Prüft ob das aktuelle Ziel noch existiert"""
        if target is None:
            return False

        if self.owner == "player":
            # Prüfe sowohl normale Enemies als auch Fly-In Enemies
            if hasattr(game, 'enemies') and target in game.enemies:
                return True
            if hasattr(game, 'fly_in_enemies') and target in game.fly_in_enemies:
                return True
            return False

        elif self.owner == "enemy":
            # Prüfe ob Player noch lebt
            return target == getattr(game, 'player', None) and not getattr(game, 'player_dead', False)

    def update(self, game=None):
        # Normale Beschleunigung
        if self.accel != 1.0:
            self._speed *= self.accel

        # Wärmelenkung für beide Player- und Enemy-Raketen
        if self.homing and game:
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
                    target = self._find_nearest_target(game)
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
        # Verwende aktuelle Bildschirmgröße statt Konstanten
        screen = pygame.display.get_surface()
        if screen:
            current_width, current_height = screen.get_size()
            return (self.rect.right < -margin or self.rect.left > current_width + margin or
                    self.rect.bottom < -margin or self.rect.top > current_height + margin)
        else:
            # Fallback zu Konstanten falls kein Screen verfügbar
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
        game.explosion_manager.add_explosion(cx, cy, frames, fps=fps, scale=1.6)

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
        _apply_aoe(game, cx, cy, self.radius, self.dmg, "expl_nuke", expl_scale=1.5)  # Kleinere Explosionen
        now = pygame.time.get_ticks()
        game.flash_until     = now + 200   # Kürzerer Flash
        game.shake_until     = now + 600   # Kürzerer Shake
        game.timescale_until = now + 400   # Kürzere Slow-Motion
        frames, fps = _expl_frames(game, "expl_nuke")
        game.explosion_manager.add_explosion(cx, cy, frames, fps=fps, scale=2.5)
