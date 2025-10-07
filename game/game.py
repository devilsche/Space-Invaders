import pygame
import random
from assets.load_assets import load_assets
from system.utils       import load_highscore, save_highscore, scale, scale_pos, scale_size
from system.hud         import HUD
from system.health_bar  import HealthBar
from system.explosion_manager import ExplosionManager
from config             import *
from config.powerup     import POWERUP_CONFIG
from config.shield      import SHIELD_CONFIG
from entities           import *

class Game:
    def __init__(self):
        pygame.init()

        # Mehr Mixer-Kanäle für gleichzeitige Sounds
        pygame.mixer.set_num_channels(32)  # Erhöhe von 8 auf 32 Kanäle

        # Reserviere Kanäle für wichtige Sounds
        self.shield_channel = pygame.mixer.Channel(30)  # Kanal 30 für Shield-Hits
        self.music_channel = pygame.mixer.Channel(31)   # Kanal 31 für Musik

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Space Invaders")
        self.clock = pygame.time.Clock()
        self.font  = pygame.font.Font(None, FONT_SIZE)
        
        # Display-Modi
        self.is_fullscreen = False
        self.is_maximized = False
        self.original_size = (WIDTH, HEIGHT)
        
        # 16:9 Aspect Ratio
        self.aspect_ratio = 16 / 9

        self.assets = load_assets()

        self.player_shots = []
        self.enemy_shots  = []
        self.enemies      = []
        self.explosion_manager = ExplosionManager(max_explosions=25)  # Optimierter Explosion-Manager

        self.enemy_dir   = 1
        self.enemy_speed = 0.0
        self.wave_num    = 0

        self.score              = 0
        self.highscore          = load_highscore()
        self.paused             = False
        self.pause_start_time   = 0
        self.total_pause_time   = 0
        self.running            = True
        self.shield             = None
        self.shield_until       = 0
        self._shield_ready_at   = 0
        self.player_dead        = False
        self.lives              = LIVES
        self.lives_cooldown     = LIVES_COOLDOWN
        self.respawn_protection = RESPAWN_PROTECTION
        self._respawn_ready_at  = 0
        self.spawn_pos          = (WIDTH // 2, HEIGHT - 80)   # NEU: feste Spawn-Position

        # Weapon Cooldown Tracking
        self.weapon_cooldowns = {
            "rocket_last_used": 0,
            "homing_rocket_last_used": 0,
            "blaster_last_used": 0,
            "nuke_last_used": 0,
            "shield_ready_at": 0
        }

        # Schild-Zerstörungs-Tracking
        self._last_shield_destroyed = 0

        # Fly-In Enemy Spawning System
        self.fly_in_enemies = []  # Separate Liste für einfliegende Gegner
        self._last_fly_in_spawn = 0
        self._fly_in_spawn_interval = 3000  # 3 Sekunden zwischen Spawns
        self._fly_in_spawn_count = 0
        self._max_fly_in_enemies = 20  # Maximal 20 einfliegende Gegner

        # Kill-Tracking für Boss-Spawn
        self._total_kills = 0
        self._boss_spawned = False

        # Power-Up System
        self.powerups = []

        # Power-Up Shield System
        self.powerup_shield = None
        self.powerup_shield_until = 0

        # DoubleLaser Power-Up System
        self.double_laser_active = False
        self.double_laser_until = 0

        # Speed Boost Power-Up System
        self.speed_boost_active = False
        self.speed_boost_until = 0
        self.speed_boost_multiplier = 1.0
        self.original_player_speed = None

        # Kill Counter Display System
        self.kill_display_text = ""
        self.kill_display_timer = 0
        self.kill_display_duration = 2000  # 2 Sekunden

        # Player mit aktueller Bildschirmgröße initialisieren
        current_width, current_height = self.screen.get_size() 
        self.player = Player(current_width, current_height, self.assets)
        self.player.rect.center = self.spawn_pos

        # HUD initialisieren
        self.hud = HUD(current_width, current_height)
        self.hud.load_icons(self.assets)

        # Health Bar initialisieren (oben rechts)
        health_bar_width = scale(200)
        health_bar_height = scale(20)
        health_bar_x = WIDTH - health_bar_width - scale(70)  # 20px vom rechten Rand
        health_bar_y = scale(20)  # 20px von oben
        self.health_bar = HealthBar(health_bar_x, health_bar_y, health_bar_width, health_bar_height)
        
        # Schild Health Bar (oben rechts, unter Player Health)
        shield_bar_width = scale(200)
        shield_bar_height = scale(15)
        shield_bar_x = WIDTH - shield_bar_width - scale(70)
        shield_bar_y = scale(50)  # Unter der Health Bar
        self.shield_health_bar = HealthBar(shield_bar_x, shield_bar_y, shield_bar_width, shield_bar_height)
    
    def _show_kill_counter(self):
        """Zeigt den Kill-Counter kurz in der Bildschirmmitte an"""
        if self._total_kills < 50:
            self.kill_display_text = f"Kill {self._total_kills}/50"
        else:
            self.kill_display_text = f"Kill {self._total_kills}"
        self.kill_display_timer = pygame.time.get_ticks()

        if "music_paths" in self.assets and "raining_bits" in self.assets["music_paths"]:
            try:
                pygame.mixer.music.load(self.assets["music_paths"]["raining_bits"])
                pygame.mixer.music.set_volume(MASTER_VOLUME * MUSIC_VOLUME)
                pygame.mixer.music.play(-1)
            except pygame.error:
                pass

        # self._build_wave("alien")

    def toggle_fullscreen(self):
        """Wechselt zwischen Vollbild und Fenster-Modus - nutzt komplette Bildschirmfläche ohne schwarze Ränder"""
        # Speichere aktuelle Player-Position vor Resize
        old_player_pos = None
        if self.player:
            current_screen = pygame.display.get_surface()
            if current_screen:
                old_width, old_height = current_screen.get_size()
                old_player_pos = (
                    self.player.rect.centerx / old_width,
                    self.player.rect.centery / old_height
                )
        
        if self.is_fullscreen:
            # Zu Fenster-Modus wechseln
            self.screen = pygame.display.set_mode(self.original_size)
            self.is_fullscreen = False
            self.is_maximized = False
            print("Switched to windowed mode")
        else:
            # Zu ECHTEM Vollbild wechseln - nutzt native Bildschirmauflösung ohne schwarze Ränder
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.is_fullscreen = True
            self.is_maximized = False
            fullscreen_width, fullscreen_height = self.screen.get_size()
            print(f"Switched to fullscreen mode: {fullscreen_width}x{fullscreen_height} (native resolution)")
        
        # Nach Auflösungs-Wechsel: Player-Position wiederherstellen und UI neu initialisieren
        self._reinitialize_ui(old_player_pos)

    def toggle_maximize(self):
        """Wechselt zwischen normalem Fenster und maximiertem Fenster mit 16:9 Aspect Ratio"""
        # Speichere aktuelle Player-Position vor Resize
        old_player_pos = None
        old_width, old_height = 0, 0
        if self.player:
            current_screen = pygame.display.get_surface()
            if current_screen:
                old_width, old_height = current_screen.get_size()
                old_player_pos = (
                    self.player.rect.centerx / old_width,
                    self.player.rect.centery / old_height
                )
        
        if self.is_maximized or self.is_fullscreen:
            # Zurück zu normaler Fenstergröße
            self.screen = pygame.display.set_mode(self.original_size)
            self.is_maximized = False
            self.is_fullscreen = False
            print(f"Switched to normal window mode: {self.original_size}")
        else:
            # Maximiertes Fenster mit 16:9 Aspect Ratio
            # Verwende aktuelle Fenster-Position und aktuellen Monitor
            window_pos = pygame.display.get_window_position() if hasattr(pygame.display, 'get_window_position') else (0, 0)
            
            # Heuristische Berechnung für maximale Fenstergröße
            # Da wir nicht direkt den aktuellen Monitor abfragen können,
            # verwenden wir eine konservative Schätzung
            current_screen = pygame.display.get_surface()
            if current_screen:
                current_width, current_height = current_screen.get_size()
                
                # Berechne größere Auflösung basierend auf aktuellem Fenster
                # Typische Monitor-Größen für bessere Schätzung
                if current_width <= 1280:
                    # Vermutlich 1920x1080 Monitor
                    max_width, max_height = 1920, 1080
                elif current_width <= 1920:
                    # Vermutlich 2560x1440 Monitor  
                    max_width, max_height = 2560, 1440
                else:
                    # Größerer Monitor - verwende konservative Werte
                    max_width, max_height = current_width + 400, current_height + 200
            else:
                # Fallback für häufigste Auflösung
                max_width, max_height = 1920, 1080
            
            # Berechne 16:9 Größe basierend auf verfügbarem Platz
            # Berücksichtige Taskbar/Titelleiste (etwa 100px Overhead)
            available_height = max_height - 100
            available_width = max_width - 50
            
            # Berechne maximale Größe mit 16:9 Ratio
            if available_width / available_height > self.aspect_ratio:
                # Höhe ist limitierend
                new_height = available_height
                new_width = int(new_height * self.aspect_ratio)
            else:
                # Breite ist limitierend
                new_width = available_width
                new_height = int(new_width / self.aspect_ratio)
            
            # Stelle sicher, dass die Größe nicht zu klein wird
            min_width, min_height = 800, 450  # Minimum 16:9 Größe
            new_width = max(new_width, min_width)
            new_height = max(new_height, min_height)
            
            self.screen = pygame.display.set_mode((new_width, new_height))
            self.is_maximized = True
            self.is_fullscreen = False
            print(f"Switched to maximized window mode: {new_width}x{new_height} (16:9 ratio)")
        
        # Nach Auflösungs-Wechsel: Player-Position wiederherstellen und UI neu initialisieren
        self._reinitialize_ui(old_player_pos)
    
    def _reinitialize_ui(self, old_player_pos=None):
        """Initialisiert UI-Elemente nach Auflösungs-Wechsel neu"""
        # HUD mit neuer Bildschirmgröße neu erstellen
        current_width, current_height = self.screen.get_size()
        
        # Aktualisiere globale WIDTH/HEIGHT für alle Spielelemente
        import config.settings
        config.settings.WIDTH = current_width
        config.settings.HEIGHT = current_height
        
        # Aktualisiere system.utils scale-System
        import system.utils
        system.utils.update_screen_size(current_width, current_height)
        
        self.hud = HUD(current_width, current_height)
        self.hud.load_icons(self.assets)
        
        # Aggressivere Skalierungsfaktoren für bessere Bildschirmnutzung
        # Base-Auflösung: 1920x1080
        base_width, base_height = 1920, 1080
        width_scale = current_width / base_width
        height_scale = current_height / base_height
        
        # Verwende größeren Skalierungsfaktor für UI-Elemente
        ui_scale = max(width_scale, height_scale) * 1.2  # 20% größer für bessere Sichtbarkeit
        
        # HealthBar neu skalieren (oben rechts) - deutlich größer
        health_bar_width = int(300 * ui_scale)  # von 200 auf 300
        health_bar_height = int(25 * ui_scale)  # von 20 auf 25
        health_bar_x = current_width - health_bar_width - int(50 * ui_scale)  # weniger Abstand vom Rand
        health_bar_y = int(20 * ui_scale)
        self.health_bar = HealthBar(health_bar_x, health_bar_y, health_bar_width, health_bar_height, ui_scale)
        
        # Shield Health Bar (oben rechts, unter Player Health) - mit extra Abstand für Text
        shield_bar_width = int(300 * ui_scale)  # von 200 auf 300
        shield_bar_height = int(20 * ui_scale)  # von 15 auf 20
        shield_bar_x = current_width - shield_bar_width - int(50 * ui_scale)
        # Berechne Y-Position: HealthBar Ende + Text-Höhe + zusätzlicher Puffer
        text_height = int(20 * ui_scale)  # Höhe des HealthBar-Texts
        shield_bar_y = health_bar_y + health_bar_height + text_height + int(10 * ui_scale)  # Text-Höhe + 10px Puffer
        self.shield_health_bar = HealthBar(shield_bar_x, shield_bar_y, shield_bar_width, shield_bar_height, ui_scale)
        
        # Player-Position relativ zur neuen Bildschirmgröße neu berechnen
        self._reposition_player(current_width, current_height, old_player_pos)
        
        # Spawn-Position an neue Auflösung anpassen - mit aggressiverer Skalierung
        self.spawn_pos = (current_width // 2, current_height - int(60 * ui_scale))  # weniger Abstand vom Rand
        
        # Schilde neu skalieren wenn aktiv
        if self.shield:
            self._update_shield_scale()
        if self.powerup_shield:
            self._update_shield_scale()
            
        # Font-Größe an neue Auflösung anpassen
        scaled_font_size = int(FONT_SIZE * ui_scale)
        self.font = pygame.font.Font(None, scaled_font_size)
        
        print(f"UI reinitialized for resolution: {current_width}x{current_height} (UI scale: {ui_scale:.2f}, Font: {scaled_font_size}px)")

    def _reposition_player(self, new_width, new_height, old_player_pos=None):
        """Positioniert Player relativ zur neuen Bildschirmgröße"""
        if not self.player:
            return
            
        # Verwende gespeicherte relative Position oder berechne sie
        if old_player_pos:
            rel_x, rel_y = old_player_pos
        else:
            # Fallback: zentriere Player unten
            rel_x, rel_y = 0.5, 0.85
        
        # Neue absolute Position
        new_x = int(rel_x * new_width)  
        new_y = int(rel_y * new_height)
        
        # Stelle sicher, dass Player im sichtbaren Bereich bleibt
        margin = self.player.rect.width // 2
        new_x = max(margin, min(new_width - margin, new_x))
        new_y = max(margin, min(new_height - margin, new_y))
        
        # Setze neue Position
        old_pos = self.player.rect.center
        self.player.rect.center = (new_x, new_y)
        
        print(f"Player repositioned from {old_pos} to ({new_x}, {new_y}) (relative: {rel_x:.2f}, {rel_y:.2f})")

    # ---------------- Power-Up System ----------------
    def _try_drop_powerup(self, x, y):
        """Versucht ein Power-Up zu droppen mit konfigurierten Wahrscheinlichkeiten"""
        # Power-Ups können immer droppen (entferne Health-Einschränkung)
        
        # Erstelle gewichtete Liste basierend auf drop_chance
        weighted_powerups = []
        for powerup_type, config in POWERUP_CONFIG.items():
            # Jede drop_chance wird als Gewicht verwendet
            weight = int(config["drop_chance"] * 1000)  # Skaliere für bessere Genauigkeit
            weighted_powerups.extend([powerup_type] * weight)
        
        # Wenn kein Power-Up gewählt wird (basierend auf Gesamtwahrscheinlichkeit)
        total_chance = sum(config["drop_chance"] for config in POWERUP_CONFIG.values())
        if random.random() > total_chance:
            return  # Kein Drop
            
        # Wähle zufällig aus gewichteter Liste
        if weighted_powerups:
            chosen_type = random.choice(weighted_powerups)
            powerup = PowerUp(x, y, chosen_type, self.assets)
            self.powerups.append(powerup)

    def _update_powerups(self):
        """Aktualisiert alle Power-Ups"""
        for powerup in self.powerups[:]:
            powerup.update()

            # Entfernen wenn abgelaufen oder vom Bildschirm gefallen
            if powerup.is_expired() or powerup.offscreen():
                self.powerups.remove(powerup)
                continue

            # Kollision mit Player prüfen
            if powerup.rect.colliderect(self.player.rect):
                # Effekt anwenden
                effect_result = powerup.apply_effect(self.player)

                # Shield Power-Up spezielle Behandlung
                if isinstance(effect_result, dict) and effect_result.get("type") == "shield":
                    self._activate_powerup_shield(effect_result["duration"], effect_result["config"])
                    print(f"Power-Up Shield activated for {effect_result['duration']/1000:.1f}s!")
                elif isinstance(effect_result, dict) and effect_result.get("type") == "double_laser":
                    self._activate_double_laser(effect_result["duration"])
                    print(f"Double Laser activated for {effect_result['duration']/1000:.1f}s!")
                elif isinstance(effect_result, dict) and effect_result.get("type") == "speed_boost":
                    self._activate_speed_boost(effect_result["duration"], effect_result["multiplier"])
                    print(f"Speed Boost activated for {effect_result['duration']/1000:.1f}s! ({effect_result['multiplier']}x speed)")
                else:
                    print(f"Power-Up collected: {effect_result}")

                # Punkte geben
                self.score += powerup.get_points()
                self.highscore = max(self.highscore, self.score)

                # Power-Up entfernen
                self.powerups.remove(powerup)

    def _activate_powerup_shield(self, duration, shield_config):
        """Aktiviert das gelbe Power-Up Shield"""
        now = self.get_game_time()

        # Power-Up Shield erstellen mit gleicher Skalierung wie normales Shield
        frames = self.assets["shield_frames"]
        fps = shield_config.get("fps", 20)
        # Gleiche dynamische Skalierung wie beim normalen Q-Shield
        scale = max(self.player.rect.w, self.player.rect.h) / frames[0].get_width() * self.assets["shield_scale"]

        self.powerup_shield = Shield(
            *self.player.rect.center, frames, fps=fps, scale=scale,
            loop=True, player_health=self.player.max_health, is_powerup_shield=True,
            shield_config=shield_config
        )
        self.powerup_shield_until = now + duration

    def _activate_double_laser(self, duration):
        """Aktiviert den DoubleLaser Power-Up Modus"""
        now = self.get_game_time()
        self.double_laser_active = True
        self.double_laser_until = now + duration

    def _activate_speed_boost(self, duration, multiplier):
        """Aktiviert den Speed Boost Power-Up Modus"""
        now = self.get_game_time()
        
        # Speichere ursprüngliche Geschwindigkeit beim ersten Aktivieren
        if self.original_player_speed is None:
            self.original_player_speed = self.player.speed
        
        # Aktiviere Speed Boost
        self.speed_boost_active = True
        self.speed_boost_until = now + duration
        self.speed_boost_multiplier = multiplier
        
        # Wende Speed-Multiplikator an
        self.player.speed = self.original_player_speed * multiplier

    # ---------------- Enemy Bewegung ----------------
    def _update_wave_enemies(self):
        """Aktualisiert Wave-Enemies mit gruppenbasierter Bewegung"""
        if not hasattr(self, 'wave_movements'):
            return
        
        # Gruppiere Enemies nach Wave-ID
        wave_groups = {}
        for enemy in self.enemies:
            if hasattr(enemy, 'movement_type') and enemy.movement_type == "wave":
                wave_id = getattr(enemy, 'wave_id', 'default')
                if wave_id not in wave_groups:
                    wave_groups[wave_id] = []
                wave_groups[wave_id].append(enemy)
        
        # Bewege jede Wave separat
        for wave_id, enemies in wave_groups.items():
            if not enemies or wave_id not in self.wave_movements:
                continue
                
            wave_data = self.wave_movements[wave_id]
            direction = wave_data["direction"]
            speed = wave_data["speed"]
            
            dx = direction * max(1, int(speed))
            left = min(en.rect.left for en in enemies)
            right = max(en.rect.right for en in enemies)
            
            # Richtungsänderung bei Bildschirmrand
            if (direction == 1 and right + dx >= WIDTH) or (direction == -1 and left - dx <= 0):
                wave_data["direction"] *= -1
                # Drop distance aus Config holen
                enemy_type = wave_data["enemy_type"]
                move_cfg = ENEMY_CONFIG[enemy_type]["move"]
                drop_px = move_cfg.get("drop_px", 20)
                for en in enemies:
                    en.drop(drop_px)
            else:
                for en in enemies:
                    en.update(dx)

    def _update_fly_in_enemies(self):
        """Aktualisiert Fly-in Enemies mit individueller Bewegung"""
        for enemy in self.enemies[:]:
            if hasattr(enemy, 'movement_type') and enemy.movement_type == "fly_in":
                enemy.update()  # Individuelle Bewegung
                
                # Prüfe, ob Enemy den Bildschirm verlassen hat und zurückkommen soll
                if enemy.rect.right < 0 or enemy.rect.left > WIDTH:
                    # Enemy ist seitlich raus - zurückbringen
                    if enemy.rect.right < 0:
                        enemy.rect.x = WIDTH  # Von rechts reinkommen
                    else:
                        enemy.rect.x = -enemy.rect.width  # Von links reinkommen

    # ---------------- Wellen ----------------
    def _build_wave(self, enemy_type: str):
        # self.enemies.clear()
        form = ENEMY_CONFIG[enemy_type]["formation"]
        wave_id = f"wave_{self.wave_num}"
        
        for r in range(form["rows"]):
            for c in range(form["cols"]):
                x = c * scale(form["h_spacing"]) + scale(form["margin_x"])
                y = r * scale(form["v_spacing"]) + scale(form["margin_y"])
                enemy = Enemy(enemy_type, self.assets, x, y)
                enemy.wave_id = wave_id  # Wave-ID zuweisen
                enemy.movement_type = "wave"  # Bewegungstyp
                self.enemies.append(enemy)
        
        # Wave-spezifische Bewegungsdaten initialisieren
        if not hasattr(self, 'wave_movements'):
            self.wave_movements = {}
        
        base = ENEMY_CONFIG[enemy_type]["move"]["speed_start"]
        self.wave_movements[wave_id] = {
            "speed": base,
            "direction": 1,  # Jede Wave startet nach rechts
            "enemy_type": enemy_type
        }
        
        self.wave_num += 1

    def _spawn_fly_in_enemy(self):
        """Spawnt einen einfliegenden Gegner von oben"""
        if self._fly_in_spawn_count >= self._max_fly_in_enemies:
            return  # Maximale Anzahl erreicht

        import random

        # Zufällige X-Position am oberen Bildschirmrand
        spawn_x = random.randint(50, WIDTH - 50)
        spawn_y = -50  # Über dem Bildschirm

        # Zufällige Laufbahn wählen (weniger Kreisbewegung für weniger Wackeln)
        path_types = ["straight", "straight", "sine", "sine", "circle"]  # Gewichtung
        path = random.choice(path_types)

        # Zufälligen Enemy-Typ wählen (außer boss)
        enemy_types = ["alien", "drone", "tank", "sniper"]
        enemy_type = random.choice(enemy_types)

        # Enemy erstellen mit dynamischer Konfiguration
        enemy = Enemy(enemy_type, self.assets, spawn_x, spawn_y)
        
        # Fly-in spezifische Eigenschaften
        enemy.wave_id = f"fly_in_{self._fly_in_spawn_count}"
        enemy.movement_type = "fly_in"

        # Fly-In Bewegung aktivieren (überschreibt die normale Konfiguration)
        enemy.move_cfg = enemy.move_cfg.copy()  # Kopie erstellen
        enemy.move_cfg["type"] = "fly_in"

        # Bewegungsparameter anpassen
        enemy.move_cfg["path"] = path
        if path == "sine":
            enemy.move_cfg["amplitude"] = random.randint(30, 50)  # Kleinere Amplitude
            enemy.move_cfg["frequency"] = random.uniform(0.8, 1.5)  # Höhere Frequenz
        elif path == "circle":
            enemy.move_cfg["radius"] = random.randint(25, 40)  # Viel kleinerer Radius
            enemy.move_cfg["frequency"] = random.uniform(0.6, 1.0)  # Höhere Frequenz
        elif path == "straight":
            # Zufällige Richtung für gerade Bewegung
            enemy._phase = random.choice([-1, 1]) * random.uniform(0.5, 2.0)

        # Zufällige Ziel-Y-Position
        enemy.move_cfg["target_y"] = random.randint(80, 150)

        self.fly_in_enemies.append(enemy)
        self._fly_in_spawn_count += 1

    def _spawn_boss_group(self):
        """Spawnt 2 Boss-Enemies nach 50 Kills"""
        import random

        for i in range(2):
            spawn_x = random.randint(100, WIDTH - 100)
            spawn_y = -80  # Höher über dem Bildschirm für Boss

            # Boss erstellen
            boss = Enemy("boss", self.assets, spawn_x, spawn_y)

            # Fly-In Bewegung für Boss (langsamer und majestätischer)
            boss.move_cfg = boss.move_cfg.copy()
            boss.move_cfg["type"] = "fly_in"
            boss.move_cfg["target_y"] = random.randint(100, 140)  # Höhere Position
            boss.move_cfg["path"] = "sine"  # Sanfte Bewegung für Boss
            boss.move_cfg["speed"] = 1.5  # Langsamer
            boss.move_cfg["amplitude"] = 30  # Kleine Bewegung
            boss.move_cfg["frequency"] = 0.5  # Langsame Frequenz

            self.fly_in_enemies.append(boss)
            self._fly_in_spawn_count += 1

        self._boss_spawned = True
        # Spawning komplett stoppen nach Boss-Spawn
        self._max_fly_in_enemies = len(self.fly_in_enemies)

    def _update_fly_in_spawning(self):
        """Updated das Spawning-System für einfliegende Gegner"""
        now = pygame.time.get_ticks()

        # Prüfe ob Boss gespawnt werden soll
        if (self._total_kills >= 50 and
            not self._boss_spawned and
            len(self.fly_in_enemies) == 0):  # Nur wenn alle normalen Enemies weg sind
            print(f"DEBUG: Spawning boss! Kills: {self._total_kills}, Boss spawned: {self._boss_spawned}, Enemies left: {len(self.fly_in_enemies)}")
            self._spawn_boss_group()
            return

        # Stoppe normales Spawning nach 50 Kills
        if self._total_kills >= 50:
            return

        # Spawne neue Gegner basierend auf Intervall
        if (now - self._last_fly_in_spawn > self._fly_in_spawn_interval and
            self._fly_in_spawn_count < self._max_fly_in_enemies):

            # Spawne 2-4 Gegner gleichzeitig in einer Gruppe
            import random
            group_size = random.randint(2, 4)
            for i in range(group_size):
                if self._fly_in_spawn_count < self._max_fly_in_enemies:
                    self._spawn_fly_in_enemy()

            self._last_fly_in_spawn = now

            # Intervall leicht variieren für natürlicheres Spawning
            self._fly_in_spawn_interval = random.randint(4000, 6000)  # Längere Pause zwischen Gruppen

    def get_game_time(self):
        """Gibt die echte Spielzeit zurück (ohne Pause-Zeit)"""
        current_time = pygame.time.get_ticks()
        if self.paused:
            # Während Pause: Pause-Zeit bis jetzt nicht mitzählen
            pause_time_so_far = current_time - self.pause_start_time
            return current_time - self.total_pause_time - pause_time_so_far
        else:
            # Normal: Nur die gesamte bisherige Pause-Zeit abziehen
            return current_time - self.total_pause_time

    # ---------------- Events ----------------
    def _handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    if self.paused:
                        # Resume: Pause-Zeit zu total_pause_time hinzufügen
                        self.total_pause_time += pygame.time.get_ticks() - self.pause_start_time
                    else:
                        # Pause: Pause-Start-Zeit merken
                        self.pause_start_time = pygame.time.get_ticks()
                    
                    self.paused = not self.paused
                    try:
                        pygame.mixer.music.pause() if self.paused else pygame.mixer.music.unpause()
                    except pygame.error:
                        pass
                elif e.key == pygame.K_F11:
                    self.toggle_maximize()  # F11 für maximiertes Fenster mit 16:9
                elif e.key == pygame.K_RETURN and (pygame.key.get_pressed()[pygame.K_LALT] or pygame.key.get_pressed()[pygame.K_RALT]):
                    # Alt+Enter für echtes Vollbild
                    self.toggle_fullscreen()
                elif e.key == pygame.K_1:
                    self.player.set_stage(1)
                    self._update_shield_scale()
                elif e.key == pygame.K_2:
                    self.player.set_stage(2)
                    self._update_shield_scale()
                elif e.key == pygame.K_3:
                    self.player.set_stage(3)
                    self._update_shield_scale()
                elif e.key == pygame.K_4:
                    self.player.set_stage(4)
                    self._update_shield_scale()
                elif e.key == pygame.K_F1:
                    self._build_wave( 'alien' )
                elif e.key == pygame.K_F2:
                    self._build_wave( 'drone' )
                elif e.key == pygame.K_F3:
                    self._build_wave( 'tank' )
                elif e.key == pygame.K_F4:
                    self._build_wave( 'sniper' )
                elif e.key == pygame.K_F5:
                    self._build_wave( 'boss' )
                elif e.key == pygame.K_F12 and not (pygame.key.get_pressed()[pygame.K_LALT] or pygame.key.get_pressed()[pygame.K_RALT]):
                    self.enemies = []  # F12 allein für Enemies clear

                elif e.key == pygame.K_SPACE and not self.paused and not self.player_dead:
                    # Immer Laser schießen, aber mit DoubleLaser-Geschossen wenn Power-Up aktiv
                    shots = self.player.shoot_weapon("laser")
                    if self.double_laser_active and shots:
                        # Laser-Geschosse durch DoubleLaser-Geschosse ersetzen
                        enhanced_shots = []
                        for shot in shots:
                            # DoubleLaser mit gleicher Position und Geschwindigkeit erstellen
                            double_shot = DoubleLaser.create(shot.rect.centerx, shot.rect.centery, 
                                                           self.assets, owner="player", angle_deg=0)
                            enhanced_shots.append(double_shot)
                        self.player_shots.extend(enhanced_shots)
                    else:
                        self.player_shots.extend(shots)
                elif e.key == pygame.K_r and not self.paused and not self.player_dead:
                    shots = self.player.shoot_weapon("rocket")
                    if shots:  # Nur wenn tatsächlich geschossen wurde
                        self.player_shots.extend(shots)
                        current_time = pygame.time.get_ticks()
                        self.weapon_cooldowns["rocket_last_used"] = current_time
                elif e.key == pygame.K_t and not self.paused and not self.player_dead:
                    shots = self.player.shoot_weapon("homing_rocket")
                    if shots:  # Nur wenn tatsächlich geschossen wurde
                        self.player_shots.extend(shots)
                        current_time = pygame.time.get_ticks()
                        self.weapon_cooldowns["homing_rocket_last_used"] = current_time
                elif e.key == pygame.K_b and not self.paused and not self.player_dead:
                    shots = self.player.shoot_weapon("blaster")
                    if shots:  # Nur wenn tatsächlich geschossen wurde
                        self.player_shots.extend(shots)
                        current_time = pygame.time.get_ticks()
                        self.weapon_cooldowns["blaster_last_used"] = current_time
                elif e.key == pygame.K_e and not self.paused and not self.player_dead:
                    shots = self.player.shoot_weapon("nuke")
                    if shots:  # Nur wenn tatsächlich geschossen wurde
                        self.player_shots.extend(shots)
                        current_time = pygame.time.get_ticks()
                        self.weapon_cooldowns["nuke_last_used"] = current_time

                elif e.key == pygame.K_q and not self.paused and not self.player_dead:
                    # Prüfen, ob das aktuelle Schiff einen Schild hat
                    from config.ship import SHIP_CONFIG
                    current_ship_config = SHIP_CONFIG.get(self.player.stage, {})
                    has_shield = current_ship_config.get("shield", 0) == 1

                    if not has_shield:
                        # Kein Schild verfügbar für dieses Schiff
                        break

                    if self.shield:
                        self.shield = None
                        break
                    now = pygame.time.get_ticks()
                    if now >= self._shield_ready_at:
                        frames = self.assets["shield_frames"]
                        fps    = self.assets["shield_fps"]

                        scale = max(self.player.rect.w, self.player.rect.h) / frames[0].get_width() * self.assets["shield_scale"]
                        new_shield = Shield( *self.player.rect.center, frames, fps=fps, scale=scale, loop=True,
                                           player_health=self.player.max_health )

                        # Schild sollte mit reduzierter Health starten wenn es kürzlich zerstört wurde
                        from config.shield import SHIELD_CONFIG
                        shield_cfg = SHIELD_CONFIG[1]["shield"]
                        regen_rate = shield_cfg.get("regen_rate", 0.2)  # 20% pro Sekunde
                        min_health_percent = shield_cfg.get("min_health_percentage", 0.3)   # Mindestens 30% der Schild-Health
                        min_health = int(new_shield.max_health * min_health_percent)

                        time_since_last_shield = max(0, now - getattr(self, '_last_shield_destroyed', 0))
                        regen_time_seconds = time_since_last_shield / 1000.0
                        health_regen = min(new_shield.max_health, new_shield.max_health * regen_rate * regen_time_seconds)
                        new_shield.current_health = max(min_health, int(health_regen))

                        self.shield = new_shield
                        self.shield_until     = now + self.assets["shield_duration"]
                        self._shield_ready_at = now + self.assets["shield_cooldown"]

                        # Shield-Aktivierungs-Sound abspielen
                        if self.assets.get("shield_activate_sound"):
                            from config import MASTER_VOLUME, SFX_VOLUME
                            self.assets["shield_activate_sound"].set_volume(MASTER_VOLUME * SFX_VOLUME)
                            self.assets["shield_activate_sound"].play()



    # ---------------- Update ----------------
    def _update(self):
        keys = pygame.key.get_pressed()
        now  = pygame.time.get_ticks()

        # Fly-In Enemy Spawning System
        self._update_fly_in_spawning()

        # HUD mit aktuellen Weapon-Status aktualisieren
        self.weapon_cooldowns["shield_ready_at"] = self._shield_ready_at
        self.hud.update_weapon_status(self.player, now, self.weapon_cooldowns)
        
        # Power-Up Status aktualisieren - mit Spielzeit (ohne Pause)
        game_time = self.get_game_time()
        super_shield_active = self.powerup_shield is not None
        super_shield_until = self.powerup_shield_until if super_shield_active else 0
        self.hud.update_powerup_status(self.double_laser_active, self.double_laser_until, 
                                     super_shield_active, super_shield_until,
                                     self.speed_boost_active, self.speed_boost_until,
                                     game_time)

        # Health Bar aktualisieren
        if not self.player_dead:
            self.health_bar.update(self.player.get_health_percentage())

        # während tot: kein Input, keine Kollisionen
        if self.player_dead:
            if (self.lives == -1 or self.lives > 0) and now >= self._respawn_ready_at:
                self._respawn()

        if not self.player_dead:
            # Verwende aktuelle Bildschirmgröße statt Konstanten
            current_width, current_height = self.screen.get_size()
            self.player.handle_input(keys, current_width, current_height)

        if keys[pygame.K_SPACE] and not self.paused and not self.player_dead:
            # Immer Laser schießen, aber mit DoubleLaser-Geschossen wenn Power-Up aktiv
            shots = self.player.shoot_weapon("laser")
            if self.double_laser_active and shots:
                # Laser-Geschosse durch DoubleLaser-Geschosse ersetzen
                enhanced_shots = []
                for shot in shots:
                    # DoubleLaser mit gleicher Position und Geschwindigkeit erstellen
                    double_shot = DoubleLaser.create(shot.rect.centerx, shot.rect.centery, 
                                                   self.assets, owner="player", angle_deg=0)
                    enhanced_shots.append(double_shot)
                self.player_shots.extend(enhanced_shots)
            else:
                self.player_shots.extend(shots)

        # Projektile bewegen
        for p in self.player_shots[:]:
            # Wärmelenkraketen brauchen Zugriff auf das Game-Objekt
            if hasattr(p, 'homing') and p.homing:
                p.update(self)
            else:
                p.update()
            if p.offscreen():
                self.player_shots.remove(p)
        for p in self.enemy_shots[:]:
            # GuidedLaser braucht Zugriff auf das Game-Objekt für Lenkung
            if hasattr(p, 'homing') and p.homing:
                p.update(self)
            else:
                p.update()
            if p.offscreen():
                self.enemy_shots.remove(p)

        for e in self.enemies[:]:
            if e.offscreen():
                self.enemies.remove(e)

        # Update Fly-In Enemies
        for enemy in self.fly_in_enemies[:]:
            enemy.update()
            # Entferne Enemies die den Bildschirm verlassen haben
            if (enemy.rect.y > HEIGHT + 50 or
                enemy.rect.x < -100 or
                enemy.rect.x > WIDTH + 100):
                self.fly_in_enemies.remove(enemy)
                self._fly_in_spawn_count = max(0, self._fly_in_spawn_count - 1)  # Count dekrementieren

        # Power-Ups aktualisieren
        self._update_powerups()

        if self.shield:
            self.shield.set_center(self.player.rect.center)
            self.shield.update()
            if pygame.time.get_ticks() >= self.shield_until or self.shield.done:
                self.shield = None

        # Power-Up Shield Update
        if self.powerup_shield:
            self.powerup_shield.set_center(self.player.rect.center)
            self.powerup_shield.update()
            if self.get_game_time() >= self.powerup_shield_until or self.powerup_shield.done:
                self.powerup_shield = None

        # DoubleLaser Power-Up Update
        if self.double_laser_active:
            if self.get_game_time() >= self.double_laser_until:
                self.double_laser_active = False

        # Speed Boost Power-Up Update
        if self.speed_boost_active:
            if self.get_game_time() >= self.speed_boost_until:
                self.speed_boost_active = False
                # Stelle ursprüngliche Geschwindigkeit wieder her
                if self.original_player_speed is not None:
                    self.player.speed = self.original_player_speed

        # Gegner bewegen - getrennt nach Bewegungstyp
        self._update_wave_enemies()
        self._update_fly_in_enemies()

        # Alle Gegner schießen lassen - sowohl normale als auch Fly-In Enemies
        for en in self.enemies:
            for w, amt in en.weapons.items():
                if amt > 0:
                    self.enemy_shots.extend(en.shoot_weapon(w, amt))
        
        # Fly-In Enemies schießen lassen
        for en in self.fly_in_enemies:
            for w, amt in en.weapons.items():
                if amt > 0:
                    self.enemy_shots.extend(en.shoot_weapon(w, amt))


        # ---- Kollision: Gegner-Projektil -> Spieler ----
        if not self.player_dead:
            for p in self.enemy_shots[:]:
                # Schild-Kollision prüfen (wenn Schild aktiv ist)
                hit_shield = False
                hit_powerup_shield = False
                
                # Normales Schild prüfen
                if self.shield and not self.shield.is_broken() and self.shield.hit_by_projectile(p.rect):
                    damage = getattr(p, "dmg", 100)
                    
                    # Normales Schild absorbiert nur den Anteil, den es blockiert (90%)
                    shield_config = SHIELD_CONFIG[1]["shield"]  # Normales Shield Config
                    damage_reduction = shield_config.get("damage_reduction", 0.9)
                    absorbed_damage = min(damage * damage_reduction, self.shield.current_health)
                    
                    shield_still_active = self.shield.take_damage(absorbed_damage)

                    self.shield.play_hit_sound(self.assets)
                    hit_shield = True

                    # Wenn Schild zerstört wird, entferne es
                    if not shield_still_active:
                        self._last_shield_destroyed = now  # Zeitpunkt der Zerstörung tracken
                        self.shield = None

                # PowerUp-Schild prüfen (hat Priorität und absorbiert 100% des Schadens)
                if self.powerup_shield and not self.powerup_shield.is_broken() and self.powerup_shield.hit_by_projectile(p.rect):
                    damage = getattr(p, "dmg", 100)
                    
                    # PowerUp-Schild absorbiert 100% des Schadens
                    absorbed_damage = min(damage, self.powerup_shield.current_health)
                    shield_still_active = self.powerup_shield.take_damage(absorbed_damage)

                    self.powerup_shield.play_hit_sound(self.assets)
                    hit_powerup_shield = True

                    # Wenn PowerUp-Schild zerstört wird, entferne es
                    if not shield_still_active:
                        self.powerup_shield = None

                    # PowerUp-Schild blockiert das Projektil vollständig (100% absorption)
                    self.enemy_shots.remove(p)
                    continue

                if p.rect.colliderect(self.player.rect):
                    # Unverwundbarkeit nach Respawn beachten
                    if now < getattr(self.player, "invincible_until", 0):
                        self.enemy_shots.remove(p)
                        continue

                    self.enemy_shots.remove(p)

                    # Schaden berechnen (verschiedene Projektile machen unterschiedlich viel Schaden)
                    damage = getattr(p, "dmg", 100)  # Standard-Schaden 100

                    # Schild-Schutz: Reduzierter Schaden wenn Schild aktiv ist
                    # PowerUp-Shield hat Priorität und blockiert 100% (sollte aber schon oben abgefangen worden sein)
                    has_powerup_shield = hit_powerup_shield or (self.powerup_shield is not None and not self.powerup_shield.is_broken())
                    has_normal_shield = hit_shield or (self.shield is not None and not self.shield.is_broken())
                    
                    # Wenn PowerUp-Shield aktiv ist, sollte diese Stelle nie erreicht werden
                    # Aber als Backup: PowerUp-Shield blockiert 100% des Schadens
                    if has_powerup_shield:
                        player_destroyed = False  # Kein Schaden
                    else:
                        player_destroyed = self.player.take_damage(damage, has_normal_shield)

                    if hasattr(p, "on_hit"):
                        p.on_hit(self, self.player.rect.center)

                    # Explosion nur bei Zerstörung
                    if player_destroyed:
                        frames = self.assets.get("expl_laser", [])
                        fps    = self.assets.get("expl_laser_fps", 24)
                        self.explosion_manager.add_explosion(self.player.rect.centerx,
                                                           self.player.rect.centery,
                                                           frames, fps=fps, scale=2.5)

                        self.player_dead       = True
                        self._respawn_ready_at = now + self.lives_cooldown

                    break


        # Kollision: Spieler-Projektile -> Gegner (normale Enemies + Fly-In Enemies)
        for p in self.player_shots[:]:
            hit_enemy = None
            # Prüfe normale Enemies
            for en in self.enemies:
                if p.rect.colliderect(en.rect):
                    hit_enemy = en
                    break
            # Prüfe Fly-In Enemies
            if not hit_enemy:
                for en in self.fly_in_enemies:
                    if p.rect.colliderect(en.rect):
                        hit_enemy = en
                        break
            if not hit_enemy:
                continue

            # Projektil raus
            self.player_shots.remove(p)

            # Projektil-spezifischer Hit (kann Gegner via AoE schon entfernen!)
            if hasattr(p, "on_hit"):
                p.on_hit(self, hit_enemy.rect.center)

            # Wenn der eben getroffene Gegner durch AoE schon entfernt wurde -> weiter
            if hit_enemy not in self.enemies and hit_enemy not in self.fly_in_enemies:
                continue

            # Direkt-Schaden anwenden und ggf. entfernen
            dead = hit_enemy.take_damage(getattr(p, "dmg", 10))
            if dead:
                self.score += hit_enemy.points
                self.highscore = max(self.highscore, self.score)

                # Kill-Counter erhöhen
                self._total_kills += 1
                
                # Kill-Display aktivieren
                self._show_kill_counter()

                # Power-Up Drop-Chance prüfen
                self._try_drop_powerup(hit_enemy.rect.centerx, hit_enemy.rect.centery)

                frames = self.assets.get("expl_rocket", []) or self.assets.get("expl_laser", [])
                fps    = self.assets.get("expl_rocket_fps", 24)
                self.explosion_manager.add_explosion(hit_enemy.rect.centerx,
                                                    hit_enemy.rect.centery,
                                                    frames, fps=fps, scale=1.2)
                # Entfernen nur, wenn noch vorhanden
                if hit_enemy in self.enemies:
                    self.enemies.remove(hit_enemy)
                elif hit_enemy in self.fly_in_enemies:
                    self.fly_in_enemies.remove(hit_enemy)
                    self._fly_in_spawn_count = max(0, self._fly_in_spawn_count - 1)  # Count dekrementieren


        # Explosionen updaten - optimiert
        self.explosion_manager.update()

        # Welle fertig -> neue bauen
        # if not self.enemies and not self.player_dead:
            # self._build_wave("alien")

    # ---------------- Draw ----------------
    def _draw(self):
        bg = self.assets.get("background_img")
        if bg:
            # Skaliere Hintergrund auf aktuelle Bildschirmgröße
            current_width, current_height = self.screen.get_size()
            if bg.get_size() != (current_width, current_height):
                bg = pygame.transform.smoothscale(bg, (current_width, current_height))
            self.screen.blit(bg, (0, 0))
        else:
            self.screen.fill((0, 0, 0))

        for p in self.player_shots: p.draw(self.screen)
        for p in self.enemy_shots:  p.draw(self.screen)
        for en in self.enemies:     en.draw(self.screen)
        for en in self.fly_in_enemies: en.draw(self.screen)  # Fly-In Enemies zeichnen
        for powerup in self.powerups: powerup.draw(self.screen)  # Power-Ups zeichnen
        self.explosion_manager.draw(self.screen)  # Optimiertes Explosion-Drawing

        if not self.player_dead:
            self.player.draw(self.screen)
            if self.shield:
                self.shield.draw(self.screen)
            if self.powerup_shield:
                self.powerup_shield.draw(self.screen)

        # Score-Anzeige skaliert positionieren (oben links)
        current_width, current_height = self.screen.get_size()
        ui_scale = max(current_width / 1920, current_height / 1080) * 1.2
        score_x = int(15 * ui_scale)
        score_y = int(15 * ui_scale)
        highscore_y = int(55 * ui_scale)
        
        self.screen.blit(self.font.render(f"Score: {self.score}", True, (255,255,255)), (score_x, score_y))
        self.screen.blit(self.font.render(f"High Score: {self.highscore}", True, (255,255,255)), (score_x, highscore_y))

        # Temporärer Kill-Counter in der Mitte (nur kurz nach Kill)
        current_time = pygame.time.get_ticks()
        if (self.kill_display_timer > 0 and 
            current_time - self.kill_display_timer < self.kill_display_duration):
            
            # Kill-Text in der Bildschirmmitte anzeigen - mit aktueller Auflösung
            kill_surface = self.font.render(self.kill_display_text, True, (255, 255, 0))
            current_width, current_height = self.screen.get_size()
            ui_scale = max(current_width / 1920, current_height / 1080) * 1.2
            kill_rect = kill_surface.get_rect(center=(current_width // 2, int(100 * ui_scale)))
            self.screen.blit(kill_surface, kill_rect)

        # Health Bar zeichnen (nur wenn Spieler lebt)
        if not self.player_dead:
            self.health_bar.draw(self.screen, self.player.get_health_percentage(),
                               self.player.current_health, self.player.max_health)

            # Schild Health Bar (nur wenn aktiv)
            if self.shield and not self.shield.is_broken():
                # Schild-Health Bar mit blauer Farbe
                old_colors = self.shield_health_bar.health_colors.copy()
                self.shield_health_bar.health_colors = {
                    "high": (0, 150, 255),     # Blau
                    "medium": (100, 200, 255), # Hellblau
                    "low": (255, 150, 0),      # Orange
                    "critical": (255, 0, 0)    # Rot
                }
                self.shield_health_bar.draw(self.screen, self.shield.get_health_percentage(),
                                          self.shield.current_health, self.shield.max_health, "SHIELD")
                self.shield_health_bar.health_colors = old_colors

        # HUD zeichnen
        self.hud.draw(self.screen)

        pygame.display.flip()


    def kill_player(self):
        if self.player_dead:
            return
        self.player_dead = True
        self._respawn_ready_at = pygame.time.get_ticks() + self.lives_cooldown


    def _respawn(self):
        if self.lives > 0:
            self.lives -= 1

        # Player neu erzeugen mit aktueller Bildschirmgröße
        current_width, current_height = self.screen.get_size()
        self.player = Player(current_width, current_height, self.assets)
        self.player.rect.center = self.spawn_pos
        # # Schutzphase
        # self.player.invincible_until = pygame.time.get_ticks() + self.respawn_protection
        # # optionales Blinken
        # self.player.blink_until = self.player.invincible_until

        self.player_dead = False
        self._respawn_ready_at = 0







    # ---------------- Loop ----------------
    def run(self):
        while self.running:
            self._handle_events()
            if not self.paused:
                self._update()
            self._draw()
            self.clock.tick(FPS)
        save_highscore(self.highscore)
        pygame.quit()

    def _update_shield_scale(self):
        """Aktualisiert die Schild-Skalierung basierend auf der aktuellen Spielergröße"""
        if self.shield:
            base_frames = self.assets["shield_frames"]
            base_scale_factor = self.assets["shield_scale"]

            # Shield-Objekt die neue Skalierung durchführen lassen
            self.shield.rescale_for_player(self.player.rect, base_frames, base_scale_factor)
        
        # Auch PowerUp Shield (Super Shield) aktualisieren
        if self.powerup_shield:
            base_frames = self.assets["shield_frames"]
            base_scale_factor = self.assets["shield_scale"]

            # PowerUp Shield-Objekt die neue Skalierung durchführen lassen
            self.powerup_shield.rescale_for_player(self.player.rect, base_frames, base_scale_factor)
