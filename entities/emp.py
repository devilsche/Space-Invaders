import math
import pygame
from config import WIDTH, HEIGHT
from config.weapon import EMP_CONFIG
from system.utils import get_current_scale_factors

class EMPPulseWave:
    """EMP-Pulse-Welle basierend auf shield.png mit expandierendem Effekt"""

    # Klassen-weite statische Assets (werden einmal geladen)
    _spritesheet = None
    _frames = []
    _assets_loaded = False

    @classmethod
    def load_static_assets(cls):
        """Lade EMP-Assets einmalig für alle Instanzen"""
        if not cls._assets_loaded:
            try:
                cls._spritesheet = pygame.image.load(EMP_CONFIG["img"]).convert_alpha()

                # Schneide Spritesheet in einzelne Frames
                cls._frames = cls._slice_spritesheet_static(cls._spritesheet)
                cls._assets_loaded = True
                print(f"EMP: Static assets loaded - {len(cls._frames)} frames from {cls._spritesheet.get_size()} spritesheet")
            except Exception as e:
                print(f"EMP Static asset loading failed: {e}")
                cls._spritesheet = None
                cls._frames = []
                cls._assets_loaded = True

    @staticmethod
    def _slice_spritesheet_static(spritesheet):
        """Statische Methode zum Schneiden des Spritesheets"""
        frames = []
        sheet_w, sheet_h = spritesheet.get_size()

        # Für 1024x1024 Shield-Spritesheet mit 4x4 Grid
        cols, rows = 4, 4
        frame_size = 256  # Jedes Frame ist 256x256 (1024 / 4 = 256)

        try:
            for row in range(rows):
                for col in range(cols):
                    x = col * frame_size
                    y = row * frame_size

                    if x + frame_size <= sheet_w and y + frame_size <= sheet_h:
                        frame_rect = pygame.Rect(x, y, frame_size, frame_size)
                        frame = spritesheet.subsurface(frame_rect).copy()
                        frames.append(frame)

        except Exception as e:
            print(f"EMP: Static frame slicing failed: {e}")
            frames = [spritesheet.copy()]

        return frames

    def __init__(self, position):
        """EMP Pulse Wave - expandiert basierend auf Konfiguration"""
        self.position = position  # Zentrum des Schiffs

        # Konfiguration aus config/weapon.py - EMP als Waffe
        self.current_diameter = EMP_CONFIG["size"][0]       # Startet bei size (64x64)
        self.max_diameter = EMP_CONFIG["radius"]            # Endet bei radius (800)
        self.duration = 0.5                                 # Feste 0.5s für Expansion
        self.timer = 0

        # Betroffene Entitäten verfolgen (für einmalige Effekte)
        self.affected_entities = set()

        # Animation
        self.current_frame = 0
        self.animation_timer = 0

        # Lade statische Assets falls noch nicht geladen
        EMPPulseWave.load_static_assets()





    def update(self, dt, game):
        """Update EMP-Welle"""
        self.timer += dt

        # 1. Durchmesser expandiert linear basierend auf Waffen-Konfiguration
        progress = min(self.timer / self.duration, 1.0)
        start_diameter = EMP_CONFIG["size"][0]  # 64px aus size
        self.current_diameter = (self.max_diameter - start_diameter) * progress + start_diameter

        # 2. Spritesheet-Animation
        if EMPPulseWave._frames:
            animation_fps = EMP_CONFIG["explosion"]["fps"]  # 16 FPS aus explosion config
            self.animation_timer += dt * animation_fps
            self.current_frame = int(self.animation_timer) % len(EMPPulseWave._frames)

        # 3. EMP-Effekt auf Gegner und Projektile anwenden
        self.apply_emp_collision_detection(game)

        # 4. Fertig wenn Zeit abgelaufen
        return self.timer < self.duration

    def apply_emp_collision_detection(self, game):
        """EMP-Kollisionserkennung für Gegner und Projektile"""
        emp_radius = self.current_diameter / 2

        # Alle Gegner-Listen sammeln
        all_enemies = []
        if hasattr(game, 'enemies'):
            all_enemies.extend(game.enemies)
        if hasattr(game, 'fly_in_enemies'):
            all_enemies.extend(game.fly_in_enemies)

        # Gegner-Effekte für ALLE Gegner
        for enemy in all_enemies:
            # Distanz zum EMP-Zentrum prüfen (verwende rect.center für korrekte Position)
            dx = enemy.rect.centerx - self.position[0]
            dy = enemy.rect.centery - self.position[1]
            distance = math.sqrt(dx*dx + dy*dy)

            # Wenn in Reichweite, EMP-Effekt anwenden
            if distance <= emp_radius:
                # Verhindere mehrfache Anwendung auf denselben Gegner
                if enemy not in self.affected_entities:
                    enemy.apply_emp_effect()
                    self.affected_entities.add(enemy)

        # Projektile-Effekte (verwende enemy_shots, nicht enemy_projectiles)
        if hasattr(game, 'enemy_shots'):
            for projectile in game.enemy_shots[:]:  # Copy for safe removal
                dx = projectile.rect.centerx - self.position[0]
                dy = projectile.rect.centery - self.position[1]
                distance = math.sqrt(dx*dx + dy*dy)

                if distance <= emp_radius:
                    # Laser/Blaster verschwinden sofort
                    if projectile.kind in ['laser', 'blaster']:
                        game.enemy_shots.remove(projectile)
                    # Raketen explodieren bei EMP-Kontakt
                    elif projectile.kind in ['rocket', 'homing_rocket']:
                        # Triggere Explosion an der Projektilposition
                        projectile.on_hit(game, projectile.rect.center)
                        game.enemy_shots.remove(projectile)

    def apply_emp_to_enemy(self, enemy):
        """Wende EMP-Effekte auf einen einzelnen Gegner an"""
        # Waffen temporär deaktivieren
        if hasattr(enemy, 'can_shoot'):
            enemy.can_shoot = False
            enemy.emp_disable_timer = EMP_CONFIG["weapon_disable_duration"]

        # Bewegung für alle Gegner stören
        if hasattr(enemy, 'movement_speed'):
            enemy.movement_speed *= EMP_CONFIG["movement_speed_factor"]
        enemy.emp_movement_timer = EMP_CONFIG["movement_disable_duration"]

        # Visuelle Störung hinzufügen
        enemy.emp_effect_timer = EMP_CONFIG["visual_effect_duration"]

        # Score für EMP-Treffer
        if hasattr(enemy, 'game'):
            enemy.game.score += EMP_CONFIG["score_bonus"]

    def draw(self, screen):
        """EMP-Welle rendern - 256x256 Frame zentriert expandieren"""
        if not EMPPulseWave._frames or self.current_frame >= len(EMPPulseWave._frames):
            return

        # Aktueller 256x256 Frame aus der statischen Animation
        current_sprite = EMPPulseWave._frames[self.current_frame]

        # Skaliere Frame auf aktuellen Durchmesser (startet bei 5px, endet bei 600px)
        scaled_size = int(self.current_diameter)
        if scaled_size <= 0:
            return

        # Skaliere das 256x256 Frame auf die gewünschte Größe
        scaled_sprite = pygame.transform.scale(current_sprite, (scaled_size, scaled_size))

        # Zentral um die exakte Schiffs-Position rendern
        draw_rect = scaled_sprite.get_rect(center=self.position)
        screen.blit(scaled_sprite, draw_rect)



    def draw_simple_ring(self, screen, scale):
        """Fallback - einfacher EMP-Ring"""
        center = (int(self.center_x * scale), int(self.center_y * scale))
        radius = int(self.current_radius * scale)

        if radius > 0:
            # Äußerer Ring (blau)
            color = (0, 150, 255, self.alpha)
            pygame.draw.circle(screen, color[:3], center, radius, 3)

            # Innerer Ring (weiß)
            inner_radius = max(1, radius - 10)
            inner_alpha = min(255, self.alpha + 50)
            inner_color = (255, 255, 255, inner_alpha)
            pygame.draw.circle(screen, inner_color[:3], center, inner_radius, 2)

    def draw_pulse_effects(self, screen, scale):
        """Zusätzliche Pulse-Effekte"""
        center = (int(self.center_x * scale), int(self.center_y * scale))

        # Mehrere konzentrische Ringe
        for i in range(3):
            delay_factor = 1.0 - (i * 0.15)
            ring_radius = int(self.current_radius * scale * delay_factor)
            ring_alpha = max(0, self.alpha // (i + 2))

            if ring_radius > 5 and ring_alpha > 20:
                color = (100, 200, 255, ring_alpha)
                pygame.draw.circle(screen, color[:3], center, ring_radius, 1)

    def _draw_emp_glow_ring(self, screen, scale, progress):
        """Zusätzlicher Glüh-Ring am Rand der EMP-Welle"""
        center = (int(self.center_x * scale), int(self.center_y * scale))
        radius = int(self.current_radius * scale)

        if radius > 5:
            # Äußerer Glüh-Ring
            glow_alpha = int(self.alpha * 0.8)
            glow_color = (100, 200, 255, glow_alpha)

            # Mehrere konzentrische Glüh-Ringe für Smooth-Effekt
            for i in range(3):
                ring_radius = radius - (i * 2)
                ring_alpha = max(20, glow_alpha // (i + 1))
                if ring_radius > 0:
                    try:
                        pygame.draw.circle(screen, glow_color[:3], center, ring_radius, 1)
                    except:
                        pass


class EMPPowerUp:
    """EMP Power-Up System"""

    def __init__(self):
        # Konfiguration aus config/weapon.py - EMP als Waffe
        self.name = "EMP Pulse"
        self.cooldown = EMP_CONFIG["cooldown"]
        self.last_used = 0
        self.charges = EMP_CONFIG["amount"]         # 0 Startladungen
        self.max_charges = EMP_CONFIG["charges_max"]
        self.consume_charges = True  # Immer verbrauchen

    def can_use(self, current_time):
        """Prüfe ob EMP verwendet werden kann"""
        return (current_time - self.last_used >= self.cooldown and
                self.charges > 0)

    def use(self, game, player_pos, current_time):
        """Verwende EMP Power-Up"""
        if not self.can_use(current_time):
            return False

        # EMP-Welle erstellen (Assets werden automatisch statisch geladen)
        emp_wave = EMPPulseWave(player_pos)

        # Zur Spiel-Engine hinzufügen
        if not hasattr(game, 'emp_waves'):
            game.emp_waves = []
        game.emp_waves.append(emp_wave)

        # Sound-Effekt (falls vorhanden)
        try:
            if hasattr(game, 'sound_manager'):
                game.sound_manager.play_sound("emp_pulse")
        except:
            pass

        # Screen-Shake-Effekt
        if hasattr(game, 'screen_shake_intensity'):
            game.screen_shake_intensity = 3
            game.screen_shake_duration = 0.5

        # Verbrauch basierend auf Konfiguration
        if self.consume_charges:
            self.charges -= 1
        self.last_used = current_time

        return True

    def add_charge(self):
        """Füge eine Ladung hinzu (Power-Up gefunden)"""
        self.charges = min(self.max_charges, self.charges + 1)

    def get_cooldown_progress(self, current_time):
        """Cooldown-Fortschritt für UI"""
        if self.charges >= self.max_charges:
            return 1.0

        elapsed = current_time - self.last_used
        return min(1.0, elapsed / self.cooldown)
