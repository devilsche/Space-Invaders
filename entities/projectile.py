import math, pygame
from config import WIDTH, HEIGHT, MASTER_VOLUME, MUSIC_VOLUME, SFX_VOLUME
from config.weapon import PROJECTILES_CONFIG
from entities.explosion import Explosion

def _expl_frames(game, key):
    return game.assets.get(key, []), game.assets.get(f"{key}_fps", 24)

def _apply_aoe(
    game,
    cx:                int,
    cy:                int,
    radius:            float,
    max_damage:        int,
    expl_key:          str,
    expl_scale:        float = 1.0,
    weapon_type:       str | None = None,
    explosion_category: str | None = None
) -> int:
    """
    Wendet Area-of-Effect Schaden an und erstellt IMMER Explosionen für JEDEN getroffenen Gegner.
    
    Args:
        explosion_category: "hit" für Impact-Explosionen, "destroy" für Kill-Explosionen
    
    Returns:
        Anzahl der getroffenen Gegner
    """
    frames, fps = _expl_frames(game, expl_key)
    enemies_hit = 0

    # ===== Normale Feinde =====
    for en in game.enemies[:]:  # [:] erstellt Kopie der Liste
        ex, ey = en.rect.center
        dist   = math.hypot(ex - cx, ey - cy)
        
        if dist <= radius:
            dmg = int(max_damage * (1 - dist / radius))
            
            if dmg > 0:
                enemies_hit += 1
                is_dead = en.take_damage(dmg)
                
                if is_dead:
                    # Gegner ist tot - Score, PowerUp, Explosion
                    game.score     = game.score + en.points
                    game.highscore = max(game.highscore, game.score)
                    
                    if hasattr(game, '_total_kills'):
                        game._total_kills += 1
                    
                    # Weapon-Statistik: Kill registrieren
                    if weapon_type:
                        game.explosion_manager.register_enemy_death(weapon_type)
                    
                    game._try_drop_powerup(ex, ey)
                    
                    # EXPLOSION GARANTIERT!
                    game.explosion_manager.add_explosion(
                        x                  = ex,
                        y                  = ey,
                        frames             = frames,
                        fps                = fps,
                        scale              = expl_scale,
                        weapon_type        = weapon_type,
                        explosion_category = explosion_category
                    )
                    
                    # Gegner aus Liste entfernen
                    if en in game.enemies:
                        game.enemies.remove(en)

    # ===== Fly-In Feinde =====
    if hasattr(game, 'fly_in_enemies'):
        for en in game.fly_in_enemies[:]:  # [:] erstellt Kopie
            ex, ey = en.rect.center
            dist   = math.hypot(ex - cx, ey - cy)
            
            if dist <= radius:
                dmg = int(max_damage * (1 - dist / radius))
                
                if dmg > 0:
                    enemies_hit += 1
                    is_dead = en.take_damage(dmg)
                    
                    if is_dead:
                        # Gegner ist tot
                        game.score     = game.score + en.points
                        game.highscore = max(game.highscore, game.score)
                        
                        if hasattr(game, '_total_kills'):
                            game._total_kills += 1
                        
                        # Weapon-Statistik: Kill registrieren
                        if weapon_type:
                            game.explosion_manager.register_enemy_death(weapon_type)
                        
                        game._try_drop_powerup(ex, ey)
                        
                        # EXPLOSION GARANTIERT!
                        game.explosion_manager.add_explosion(
                            x                  = ex,
                            y                  = ey,
                            frames             = frames,
                            fps                = fps,
                            scale              = expl_scale,
                            weapon_type        = weapon_type,
                            explosion_category = explosion_category
                        )
                        
                        # Aus Liste entfernen
                        if en in game.fly_in_enemies:
                            game.fly_in_enemies.remove(en)
                            
                            if hasattr(game, '_fly_in_spawn_count'):
                                game._fly_in_spawn_count = max(0, game._fly_in_spawn_count - 1)

    # ===== Boss (falls vorhanden) =====
    if getattr(game, "boss", None):
        bx, by = game.boss.rect.center
        dist   = math.hypot(bx - cx, by - cy)
        
        if dist <= radius:
            dmg = int(max_damage * (1 - dist / radius))
            
            if dmg > 0:
                enemies_hit += 1
                is_dead = game.boss.take_damage(dmg)
                
                if is_dead:
                    # Boss ist tot
                    game.score     = game.score + getattr(game.boss, "points", 600)
                    game.highscore = max(game.highscore, game.score)
                    
                    # Weapon-Statistik: Kill registrieren
                    if weapon_type:
                        game.explosion_manager.register_enemy_death(weapon_type)
                    
                    game._try_drop_powerup(bx, by)
                    
                    # EXPLOSION GARANTIERT (größer für Boss)!
                    game.explosion_manager.add_explosion(
                        x                  = bx,
                        y                  = by,
                        frames             = frames,
                        fps                = fps,
                        scale              = expl_scale * 1.5,  # 50% größer für Boss
                        weapon_type        = weapon_type,
                        explosion_category = explosion_category
                    )
                    
                    game.boss = None

    return enemies_hit

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

    def physics_update(self, game):
        """Fixed timestep physics update"""
        if self.accel != 1.0:
            self._speed *= self.accel
            self.vx = self._dir[0] * self._speed
            self.vy = self._dir[1] * self._speed
            
        # Da wir fixen Timestep haben (z.B. 1/120), müssen wir nicht mehr mit dt multiplizieren
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)
    
    def update(self):
        """Legacy update - sollte nicht mehr für Bewegung verwendet werden"""
        pass

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
        """
        Laser HIT-Explosion: Nur 4 Frames für visuelles Feedback.
        DESTROY-Explosion wird in game.py für getötete Enemies erstellt.
        """
        frames, fps = _expl_frames(game, "expl_laser")
        
        # Nur erste 4 Frames für HIT-Explosion
        frames = frames[:4]
        
        # Nur Player-Projektile zählen für Statistiken
        weapon_type = "Laser" if self.owner == "player" else None
        explosion_cat = "hit" if self.owner == "player" else None
        
        game.explosion_manager.add_explosion(
            x                  = hit_pos[0],
            y                  = hit_pos[1],
            frames             = frames,
            fps                = fps,
            scale              = 1.0,
            weapon_type        = weapon_type,
            explosion_category = explosion_cat
        )

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
        """
        DoubleLaser HIT-Explosion: Nur 4 Frames für visuelles Feedback.
        DESTROY-Explosion wird in game.py für getötete Enemies erstellt.
        """
        frames, fps = _expl_frames(game, "expl_laser")
        
        # Nur erste 4 Frames für HIT-Explosion
        frames = frames[:4]
        
        # Nur Player-Projektile zählen für Statistiken
        weapon_type = "DoubleLaser" if self.owner == "player" else None
        explosion_cat = "hit" if self.owner == "player" else None
        
        game.explosion_manager.add_explosion(
            x                  = hit_pos[0],
            y                  = hit_pos[1],
            frames             = frames,
            fps                = fps,
            scale              = 1.0,
            weapon_type        = weapon_type,
            explosion_category = explosion_cat
        )

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
        """
        Rocket: HIT-Explosion am Einschlagspunkt + DESTROY-Explosionen für alle getöteten Enemies.
        """
        cx, cy = hit_pos
        if game.assets.get("rocket_sound_hit"):
            game.assets["rocket_sound_hit"].set_volume(MASTER_VOLUME * SFX_VOLUME)
            game.assets["rocket_sound_hit"].play()
        
        # Nur Player-Projektile zählen für Statistiken
        weapon_type = "Rocket" if self.owner == "player" else None
        
        # 1. HIT-Explosion am Einschlagspunkt (volle Frames, größer)
        frames, fps = _expl_frames(game, "expl_rocket")
        game.explosion_manager.add_explosion(
            x                  = cx,
            y                  = cy,
            frames             = frames,
            fps                = fps,
            scale              = 1.5,
            weapon_type        = weapon_type,
            explosion_category = "hit" if weapon_type else None
        )
        
        # 2. AoE Schaden mit DESTROY-Explosionen für getötete Enemies
        _apply_aoe(
            game               = game,
            cx                 = cx,
            cy                 = cy,
            radius             = self.radius,
            max_damage         = self.dmg,
            expl_key           = "expl_rocket",
            expl_scale         = 1.0,
            weapon_type        = weapon_type,
            explosion_category = "destroy" if weapon_type else None
        )

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
        """
        Blaster: HIT-Explosion am Einschlagspunkt + DESTROY-Explosionen für alle getöteten Enemies.
        """
        cx, cy = hit_pos
        if game.assets.get("laser_sound_destroy"):
            game.assets["laser_sound_destroy"].set_volume(MASTER_VOLUME * SFX_VOLUME)
            game.assets["laser_sound_destroy"].play()
        
        # Nur Player-Projektile zählen für Statistiken
        weapon_type = "Blaster" if self.owner == "player" else None
        
        # 1. HIT-Explosion am Einschlagspunkt (kleiner als Raketen)
        frames, fps = _expl_frames(game, "expl_rocket")
        game.explosion_manager.add_explosion(
            x                  = cx,
            y                  = cy,
            frames             = frames,
            fps                = fps,
            scale              = 0.8,  # Kleiner als normale Rakete
            weapon_type        = weapon_type,
            explosion_category = "hit" if weapon_type else None
        )
        
        # 2. AoE Schaden mit DESTROY-Explosionen für getötete Enemies (kleiner Radius)
        _apply_aoe(
            game               = game,
            cx                 = cx,
            cy                 = cy,
            radius             = 40,  # Kleiner als Raketen
            max_damage         = self.dmg,
            expl_key           = "expl_rocket",
            expl_scale         = 1.0,
            weapon_type        = weapon_type,
            explosion_category = "destroy" if weapon_type else None
        )

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
        """
        HomingRocket: HIT-Explosion am Einschlagspunkt + DESTROY-Explosionen für alle getöteten Enemies.
        Ring-Explosionen entfernt für klarere Statistiken.
        """
        cx, cy = hit_pos
        if game.assets.get("rocket_sound_hit"):
            game.assets["rocket_sound_hit"].set_volume(MASTER_VOLUME * SFX_VOLUME)
            game.assets["rocket_sound_hit"].play()
        
        # Nur Player-Projektile zählen für Statistiken
        weapon_type = "HomingRocket" if self.owner == "player" else None
        
        # 1. HIT-Explosion am Einschlagspunkt (volle Frames, größer als normale Rakete)
        frames, fps = _expl_frames(game, "expl_rocket")
        game.explosion_manager.add_explosion(
            x                  = cx,
            y                  = cy,
            frames             = frames,
            fps                = fps,
            scale              = 2.0,  # Größer als normale Rakete
            weapon_type        = weapon_type,
            explosion_category = "hit" if weapon_type else None
        )
        
        # 2. AoE Schaden mit DESTROY-Explosionen für getötete Enemies (größerer Radius)
        _apply_aoe(
            game               = game,
            cx                 = cx,
            cy                 = cy,
            radius             = self.radius * 1.2,  # 20% größerer Radius als normale Rakete
            max_damage         = self.dmg,
            expl_key           = "expl_rocket",
            expl_scale         = 1.0,
            weapon_type        = weapon_type,
            explosion_category = "destroy" if weapon_type else None
        )

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
        """
        Nuke: HIT-Explosion am Einschlagspunkt + DESTROY-Explosionen für alle Kills.
        Bei ≥10 Kills: Zusätzlich 1 große Explosion pro 10 Kills für visuellen Effekt.
        """
        cx, cy = hit_pos
        print(f"NUKE HIT at {cx},{cy}!")  # Debug
        
        if game.assets.get("nuke_sound_hit"):
            game.assets["nuke_sound_hit"].set_volume(MASTER_VOLUME * SFX_VOLUME)
            game.assets["nuke_sound_hit"].play()
        
        # Nur Player-Projektile zählen für Statistiken
        weapon_type = "Nuke" if self.owner == "player" else None
        
        # 1. HIT-Explosion am Einschlagspunkt (zentrale Mega-Explosion)
        frames, fps = _expl_frames(game, "expl_nuke")
        print(f"NUKE: Got frames={len(frames) if frames else 0}, fps={fps}")  # Debug
        
        game.explosion_manager.add_explosion(
            x                  = cx,
            y                  = cy,
            frames             = frames,
            fps                = fps,
            scale              = 2.5,
            weapon_type        = weapon_type,
            explosion_category = "hit" if weapon_type else None
        )
        print(f"NUKE: Added HIT explosion!")  # Debug
        
        # 2. AoE Schaden - erstellt DESTROY-Explosionen für jeden Kill
        enemies_killed = _apply_aoe(
            game               = game,
            cx                 = cx,
            cy                 = cy,
            radius             = self.radius,
            max_damage         = self.dmg,
            expl_key           = "expl_nuke",
            expl_scale         = 1.0,
            weapon_type        = weapon_type,
            explosion_category = "destroy" if weapon_type else None
        )
        
        print(f"NUKE: Killed {enemies_killed} enemies!")  # Debug
        
        # 3. Bei ≥10 Kills: Zusätzliche große gruppierte Explosionen für spektakulären Effekt
        if enemies_killed >= 10 and weapon_type:  # Nur für Player-Nukes
            num_groups = enemies_killed // 10
            
            print(f"NUKE: Creating {num_groups} additional large explosions")
            
            # Große gruppierte Explosionen (zusätzlich zu den individuellen)
            for i in range(num_groups):
                # Leicht versetzt vom Zentrum im Ring
                offset_angle = i * (2 * math.pi / num_groups) if num_groups > 1 else 0
                offset_x = 40 * math.cos(offset_angle) if num_groups > 1 else 0
                offset_y = 40 * math.sin(offset_angle) if num_groups > 1 else 0
                
                game.explosion_manager.add_explosion(
                    x                  = cx + offset_x,
                    y                  = cy + offset_y,
                    frames             = frames,
                    fps                = fps * 0.9,
                    scale              = 3.0,  # Große Explosion
                    weapon_type        = weapon_type,
                    explosion_category = "destroy"  # Zählt auch als DESTROY
                )
        
        print(f"NUKE: Complete!")  # Debug
        
        # Maximale visuelle Effekte
        now = pygame.time.get_ticks()
        game.flash_until     = now + 400   # Längerer Flash
        game.shake_until     = now + 1000  # Mehr Shake
        game.timescale_until = now + 600   # Längere Slow-Motion
