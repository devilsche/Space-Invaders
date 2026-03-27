import pygame
import random
from assets.load_assets import load_assets
from system.utils       import load_highscore, scale, load_survivor_highscores
from system.hud         import HUD
from system.health_bar  import HealthBar
from config             import *
from config.powerup     import POWERUP_CONFIG
from config.shield      import SHIELD_CONFIG
from entities           import *
from manager import ExplosionManager, PowerUpManager, ProjectileManager
from system.screens.menu import GameMenu
from system.screens.ship_select import ShipSelectScreen
from system.screens.victory_screen import VictoryScreen
from system.screens.survivor_screens import SurvivorNameInputScreen, SurvivorGameOverScreen
from system.screens.game_over import GameOverScreen
from system.screens.top10_normal import NormalTop10Screen
from system.screens.top10_survivor import SurvivorTop10Screen
from system.saving_overlay import SavingOverlay

class Game:
    def __init__(self, assets=None, screen=None):
        pygame.init()

        # Pygame Setup - bestehendes Display nutzen oder neues erstellen
        if screen is not None:
            self.screen = screen
        else:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Ironblast")
        self.clock = pygame.time.Clock()

        # Game State
        self.running    = True
        self.paused     = False
        self.game_state = "menu"  # 'loading', 'menu', 'playing', 'game_over', 'top10_normal', 'top10_survivor', etc.
        self.current_screen = "menu"  # Tracking des aktuellen Screens
        self.came_from = None  # Woher kamen wir (für Navigation)
        self.game_mode  = "normal"  # "normal" oder "survivor"
        self.score      = 0
        self.highscore  = load_highscore()
        self.lives      = LIVES
        self.kills      = 0  # Kills für Normal Mode
        self.level      = 1  # Aktuelles Level im Normal Mode

        # Online Verfügbarkeit (wird EINMAL beim Start geprüft)
        self.online_available = False

        # Survivor Mode
        self.survivor_start_time = 0
        self.survivor_time = 0
        self.survivor_kills = 0
        self.survivor_player_name = ""
        self.survivor_selected_stage = 1  # Vorausgewählte Schiffsklasse

        # Display-Modi
        self.is_fullscreen = False
        self.is_maximized  = False
        self.original_size = (WIDTH, HEIGHT)
        self.aspect_ratio  = 16 / 9

        # Assets - entweder übergeben oder selbst laden (Fallback)
        if assets is not None:
            self.assets = assets
        else:
            self.assets = load_assets()
        self.font   = pygame.font.Font(None, FONT_SIZE)
        self._bg_scaled = self.assets.get("background_img")  # wird in _reinitialize_ui() skaliert

        # AppController Integration - für Menu-freie Nutzung
        self.app_controller = None  # Wird vom AppController gesetzt

        # Menü
        self.menu = GameMenu()
        self.menu.load_assets(self.assets)
        self.menu.set_pause_mode(False)

        # Screen Modules (mit Assets für Font-Caching)
        self.ship_select_screen         = ShipSelectScreen()
        self.victory_screen             = VictoryScreen()
        self.survivor_name_input_screen = SurvivorNameInputScreen()
        self.survivor_game_over_screen  = SurvivorGameOverScreen()

        # New unified screens (mit Assets)
        self.game_over_screen = GameOverScreen(assets=self.assets)
        self.saving_overlay = SavingOverlay()
        self.top10_normal_screen = NormalTop10Screen(assets=self.assets)
        self.top10_survivor_screen = SurvivorTop10Screen(assets=self.assets)

        # Audio
        pygame.mixer.set_num_channels(32)
        self.shield_channel = pygame.mixer.Channel(30)
        self.music_channel  = pygame.mixer.Channel(31)
        # Musik einmal laden
        if self.assets.has("music_paths"):
            music_paths = self.assets.get("music_paths")
            if music_paths and "raining_bits" in music_paths:
                try:
                    pygame.mixer.music.load(music_paths["raining_bits"])
                except pygame.error:
                    pass

        # Firebase-Status aus zentraler Verwaltung holen
        from system.firebase_manager import is_firebase_available
        self.online_available = is_firebase_available()
        if self.online_available:
            print('✓ Using pre-initialized online mode')
        else:
            print('✓ Using pre-initialized offline mode')

        # Fixed timestep
        self.fixed_timestep      = 1.0 / 60.0
        self.accumulated_time    = 0.0
        self.max_steps_per_frame = 2

        # Gameplay Container
        self.enemies = []
        self.enemy_dir   = 1
        self.enemy_speed = 0.0
        self.wave_num    = 0

        self.shield           = None
        self.shield_until     = 0
        self._shield_ready_at = 0
        self._last_shield_destroyed = 0

        self.player_dead = False
        self.lives_cooldown     = LIVES_COOLDOWN
        self.respawn_protection = RESPAWN_PROTECTION
        self._respawn_ready_at  = 0
        self.spawn_pos          = (WIDTH // 2, HEIGHT - 80)

        # Manager
        self.powerup_manager    = PowerUpManager(self.assets)
        self.explosion_manager  = ExplosionManager(max_explosions=10000)
        self.projectile_manager = ProjectileManager(max_projectiles=10000)  # Sehr hoch für extreme Situationen

        # Pausen-Zeitmessung
        self.total_pause_time = 0
        self.pause_start_time = 0

        # Runtime-Status für HUD und Waffen
        self.weapon_cooldowns = {
            "rocket_last_used":        0,
            "homing_rocket_last_used": 0,
            "blaster_last_used":       0,
            "nuke_last_used":          0,
            "shield_ready_at":         0
        }

        # Fly-In/Spawn Status
        self.fly_in_enemies         = []
        self._last_fly_in_spawn     = 0
        self._fly_in_spawn_interval = 1000
        self._fly_in_spawn_count    = 0
        self._max_fly_in_enemies    = 30

        # Kills/Boss
        self._total_kills  = 0
        self._boss_spawned = False

        # Wave/Level System (Normal Mode)
        self._current_wave       = 0      # Aktuelle Wave (0-basiert)
        self._wave_enemy_queue   = []     # Noch zu spawnende Gegner der aktuellen Wave
        self._wave_total_enemies = 0      # Gesamtgegner der aktuellen Wave
        self._wave_kills         = 0      # Kills in aktueller Wave
        self._level_config       = None   # Aktuelle Level-Config
        self._all_waves_done     = False  # Alle Waves gespawnt?

        # Upgrade-Multiplikatoren
        self._damage_multiplier          = 1.0
        self._fire_rate_multiplier       = 1.0
        self._shield_duration_multiplier = 1.0

        # Power-Ups
        self.powerups = []
        self.powerup_shield       = None
        self.powerup_shield_until = 0
        self.double_laser_active  = False
        self.double_laser_until   = 0
        self.speed_boost_active   = False
        self.speed_boost_until    = 0
        self.speed_boost_multiplier = 1.0
        self.original_player_speed  = None

        # EMP
        from entities.emp import EMPPowerUp
        self.emp_powerup = EMPPowerUp()
        self.emp_waves   = []

        # Kill-Overlay
        self.kill_display_text     = ""
        self.kill_display_timer    = 0
        self.kill_display_duration = 2000

        # Life Lost Overlay
        self.life_lost_display_text = ""
        self.life_lost_display_timer = 0
        self.life_lost_display_duration = 2000

        # Player+HUD
        current_width, current_height = self.screen.get_size()
        self.player = Player(current_width, current_height, self.assets)
        self.player.rect.center = self.spawn_pos

        self.hud = HUD(current_width, current_height)
        self.hud.load_icons(self.assets)

        health_bar_width  = scale(200)
        health_bar_height = scale(20)
        health_bar_x = WIDTH - health_bar_width - scale(70)
        health_bar_y = scale(20)
        self.health_bar = HealthBar(health_bar_x, health_bar_y, health_bar_width, health_bar_height)

        shield_bar_width  = scale(200)
        shield_bar_height = scale(15)
        shield_bar_x = WIDTH - shield_bar_width - scale(70)
        shield_bar_y = scale(50)
        self.shield_health_bar = HealthBar(shield_bar_x, shield_bar_y, shield_bar_width, shield_bar_height)

        # Start-UI auf aktuelle Größe bringen
        self._reinitialize_ui()

    def _physics_update(self):
        """Nur Physik, keine Neu-Initialisierung."""
        self.projectile_manager.physics_update(self)

    def _show_kill_counter(self):
        if self.game_mode == "normal" and self._level_config:
            waves = self._level_config.get("waves", [])
            if self._boss_spawned:
                self.kill_display_text = f"Lv{self.level} BOSS"
            elif self._current_wave > 0:
                self.kill_display_text = f"Lv{self.level} Wave {self._current_wave}/{len(waves)}"
            else:
                self.kill_display_text = f"Lv{self.level} Kill {self._total_kills}"
        elif self._total_kills < 50:
            self.kill_display_text = f"Kill {self._total_kills}/50"
        else:
            self.kill_display_text = f"Kill {self._total_kills}"
        self.kill_display_timer = pygame.time.get_ticks()

        # Musik nur starten, nicht neu laden
        try:
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.set_volume(MASTER_VOLUME * MUSIC_VOLUME)
                pygame.mixer.music.play(-1)
        except pygame.error:
            pass

    def toggle_fullscreen(self):
        old_player_pos = None
        if self.player:
            current_screen = pygame.display.get_surface()
            if current_screen:
                ow, oh = current_screen.get_size()
                old_player_pos = (self.player.rect.centerx / ow, self.player.rect.centery / oh)

        if self.is_fullscreen:
            self.screen = pygame.display.set_mode(self.original_size)
            self.is_fullscreen = False
            self.is_maximized  = False
        else:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.is_fullscreen = True
            self.is_maximized  = False

        self._reinitialize_ui(old_player_pos)

    def toggle_maximize(self):
        old_player_pos = None
        if self.player:
            current_screen = pygame.display.get_surface()
            if current_screen:
                ow, oh = current_screen.get_size()
                old_player_pos = (self.player.rect.centerx / ow, self.player.rect.centery / oh)

        if self.is_maximized or self.is_fullscreen:
            self.screen = pygame.display.set_mode(self.original_size)
            self.is_maximized = False
            self.is_fullscreen = False
        else:
            current_screen = pygame.display.get_surface()
            if current_screen:
                cw, ch = current_screen.get_size()
                if cw <= 1280:
                    max_w, max_h = 1920, 1080
                elif cw <= 1920:
                    max_w, max_h = 2560, 1440
                else:
                    max_w, max_h = cw + 400, ch + 200
            else:
                max_w, max_h = 1920, 1080

            avail_h = max_h - 100
            avail_w = max_w - 50
            if avail_w / avail_h > self.aspect_ratio:
                new_h = avail_h
                new_w = int(new_h * self.aspect_ratio)
            else:
                new_w = avail_w
                new_h = int(new_w / self.aspect_ratio)

            new_w = max(new_w, 800)
            new_h = max(new_h, 450)

            self.screen = pygame.display.set_mode((new_w, new_h))
            self.is_maximized = True
            self.is_fullscreen = False

        self._reinitialize_ui(old_player_pos)

    def _reinitialize_ui(self, old_player_pos=None):
        cw, ch = self.screen.get_size()

        import config.settings
        config.settings.WIDTH  = cw
        config.settings.HEIGHT = ch

        # Modul-Level WIDTH/HEIGHT in game.py aktualisieren
        global WIDTH, HEIGHT
        WIDTH  = cw
        HEIGHT = ch

        import system.utils
        system.utils.update_screen_size(cw, ch)

        self.hud = HUD(cw, ch)
        self.hud.load_icons(self.assets)

        base_w, base_h = 1920, 1080
        ui_scale = max(cw / base_w, ch / base_h) * 1.2

        hb_w = int(300 * ui_scale)
        hb_h = int(25 * ui_scale)
        hb_x = cw - hb_w - int(50 * ui_scale)
        hb_y = int(20 * ui_scale)
        self.health_bar = HealthBar(hb_x, hb_y, hb_w, hb_h, ui_scale)

        sb_w = int(300 * ui_scale)
        sb_h = int(20 * ui_scale)
        sb_x = cw - sb_w - int(50 * ui_scale)
        text_h = int(20 * ui_scale)
        sb_y = hb_y + hb_h + text_h + int(10 * ui_scale)
        self.shield_health_bar = HealthBar(sb_x, sb_y, sb_w, sb_h, ui_scale)

        self._reposition_player(cw, ch, old_player_pos)
        self.spawn_pos = (cw // 2, ch - int(60 * ui_scale))

        if self.shield:
            self._update_shield_scale()
        if self.powerup_shield:
            self._update_shield_scale()

        self.font = pygame.font.Font(None, int(FONT_SIZE * ui_scale))

        # Hintergrund einmalig skalieren
        bg = self.assets.get("background_img")
        if bg:
            if bg.get_size() != (cw, ch):
                self._bg_scaled = pygame.transform.smoothscale(bg, (cw, ch))
            else:
                self._bg_scaled = bg

    def _reposition_player(self, new_width, new_height, old_player_pos=None):
        if not self.player:
            return
        if old_player_pos:
            rel_x, rel_y = old_player_pos
        else:
            rel_x, rel_y = 0.5, 0.85
        new_x = int(rel_x * new_width)
        new_y = int(rel_y * new_height)
        margin = self.player.rect.width // 2
        new_x = max(margin, min(new_width - margin, new_x))
        new_y = max(margin, min(new_height - margin, new_y))
        self.player.rect.center = (new_x, new_y)

    # ---------------- Power-Up System ----------------
    def _try_drop_powerup(self, x, y):
        self.powerup_manager.add_drop_to_queue(x, y)

    def _update_powerups(self):
        # PowerUpManager Update (verarbeitet Queue und updatet PowerUps)
        dt = self.clock.get_time() / 1000.0
        self.powerup_manager.update(dt, HEIGHT)

        # Survivor Mode: Entferne Shield und Health PowerUps
        if self.game_mode == "survivor":
            self.powerup_manager.powerups = [
                p for p in self.powerup_manager.powerups
                if p.type not in ["shield", "health", "repair"]
            ]

        # Kollisionserkennung mit Player
        for powerup in self.powerup_manager.powerups[:]:
            if powerup.rect.colliderect(self.player.rect):
                # Powerup-Pickup Sound abspielen (mit reduzierter Lautstärke)
                if self.assets.get("powerup_pickup_sound"):
                    sound = self.assets.get("powerup_pickup_sound")
                    sound.set_volume(0.4)  # Reduzierte Lautstärke (40%)
                    sound.play()

                effect_result = powerup.apply_effect(self.player)
                if isinstance(effect_result, dict) and effect_result.get("type") == "shield":
                    self._activate_powerup_shield(effect_result["duration"], effect_result["config"])
                elif isinstance(effect_result, dict) and effect_result.get("type") == "double_laser":
                    self._activate_double_laser(effect_result["duration"])
                elif isinstance(effect_result, dict) and effect_result.get("type") == "speed_boost":
                    self._activate_speed_boost(effect_result["duration"], effect_result["multiplier"])
                elif isinstance(effect_result, dict) and effect_result.get("type") == "emp":
                    self.emp_powerup.add_charge()
                self.score += powerup.get_points()
                self.highscore = max(self.highscore, self.score)
                self.powerup_manager.powerups.remove(powerup)

    def _activate_powerup_shield(self, duration, shield_config):
        # Survivor Mode: Keine Shields
        if self.game_mode == "survivor":
            return

        now = self.get_game_time()

        # Zeit-Stacking: Addiere Duration zur verbleibenden Zeit
        remaining_time = max(0, self.powerup_shield_until - now) if self.powerup_shield is not None else 0
        new_duration = remaining_time + duration

        # Maximum: 5x der einzelnen Duration
        max_duration = duration * 5
        if new_duration > max_duration:
            new_duration = max_duration
            print(f"[WARNING] Shield: Maximum {max_duration/1000:.1f}s erreicht!")

        # Shield erstellen (nur wenn noch keins aktiv ist)
        if self.powerup_shield is None:
            frames = self.assets.get("shield_frames")
            fps = shield_config.get("fps", 20)
            scale_f = max(self.player.rect.w, self.player.rect.h) / frames[0].get_width() * self.assets.get("shield_scale")
            self.powerup_shield = Shield(
                *self.player.rect.center, frames, fps=fps, scale=scale_f,
                loop=True, player_health=self.player.max_health, is_powerup_shield=True,
                shield_config=shield_config
            )

        self.powerup_shield_until = now + new_duration
        print(f"[POWERUP] Shield activated! Duration: {new_duration/1000:.1f}s (max: {max_duration/1000:.1f}s)")

    def _activate_double_laser(self, duration):
        now = self.get_game_time()

        # Zeit-Stacking: Addiere Duration zur verbleibenden Zeit
        remaining_time = max(0, self.double_laser_until - now) if self.double_laser_active else 0
        new_duration = remaining_time + duration

        # Maximum: 5x der einzelnen Duration
        max_duration = duration * 5
        if new_duration > max_duration:
            new_duration = max_duration
            print(f"[WARNING] Double Laser: Maximum {max_duration/1000:.1f}s erreicht!")

        self.double_laser_active = True
        self.double_laser_until = now + new_duration

        print(f"[POWERUP] Double Laser activated! Duration: {new_duration/1000:.1f}s (max: {max_duration/1000:.1f}s)")

    def _activate_speed_boost(self, duration, multiplier):
        now = self.get_game_time()
        if self.original_player_speed is None:
            self.original_player_speed = self.player.speed

        # Zeit-Stacking: Addiere Duration zur verbleibenden Zeit
        remaining_time = max(0, self.speed_boost_until - now) if self.speed_boost_active else 0
        new_duration = remaining_time + duration

        # Maximum: 5x der einzelnen Duration
        max_duration = duration * 5
        if new_duration > max_duration:
            new_duration = max_duration
            print(f"[WARNING] Speed Boost: Maximum {max_duration/1000:.1f}s erreicht!")

        self.speed_boost_active = True
        self.speed_boost_until = now + new_duration
        self.speed_boost_multiplier = multiplier
        self.player.speed = self.original_player_speed * multiplier

        print(f"[POWERUP] Speed Boost activated! Duration: {new_duration/1000:.1f}s (max: {max_duration/1000:.1f}s)")

    # ---------------- Enemy Bewegung ----------------
    def _update_wave_enemies(self):
        if not hasattr(self, 'wave_movements'):
            return
        wave_groups = {}
        for enemy in self.enemies:
            if getattr(enemy, 'movement_type', None) == "wave":
                wave_groups.setdefault(getattr(enemy, 'wave_id', 'default'), []).append(enemy)
        for wave_id, enemies in wave_groups.items():
            if not enemies or wave_id not in self.wave_movements: continue
            wave_data = self.wave_movements[wave_id]
            direction = wave_data["direction"]
            speed = wave_data["speed"]
            dx = direction * max(1, int(speed))
            left = min(en.rect.left for en in enemies)
            right = max(en.rect.right for en in enemies)
            if (direction == 1 and right + dx >= WIDTH) or (direction == -1 and left - dx <= 0):
                wave_data["direction"] *= -1
                enemy_type = wave_data["enemy_type"]
                drop_px = ENEMY_CONFIG[enemy_type]["move"].get("drop_px", 20)
                for en in enemies: en.drop(drop_px)
            else:
                for en in enemies: en.update(dx)

    def _update_fly_in_enemies(self):
        for enemy in self.fly_in_enemies[:]:
            # Übergebe Spieler-Position für sanftes Tracking
            player_x = self.player.rect.centerx if self.player else None
            enemy.update(player_x=player_x)
            if hasattr(enemy, 'update_emp_effects'):
                enemy.update_emp_effects(0.016)  # ~60 FPS
            if enemy.rect.right < 0 or enemy.rect.left > WIDTH:
                enemy.rect.x = WIDTH if enemy.rect.right < 0 else -enemy.rect.width

    # ---------------- Wellen ----------------
    def _build_wave(self, enemy_type: str):
        form = ENEMY_CONFIG[enemy_type]["formation"]
        wave_id = f"wave_{self.wave_num}"
        for r in range(form["rows"]):
            for c in range(form["cols"]):
                x = c * scale(form["h_spacing"]) + scale(form["margin_x"])
                y = r * scale(form["v_spacing"]) + scale(form["margin_y"])
                enemy = Enemy(enemy_type, self.assets, x, y)
                enemy.wave_id = wave_id
                enemy.movement_type = "wave"
                self.enemies.append(enemy)
        if not hasattr(self, 'wave_movements'):
            self.wave_movements = {}
        base = ENEMY_CONFIG[enemy_type]["move"]["speed_start"]
        self.wave_movements[wave_id] = {"speed": base, "direction": 1, "enemy_type": enemy_type}
        self.wave_num += 1

    def _spawn_fly_in_enemy(self, enemy_type=None):
        if self._fly_in_spawn_count >= self._max_fly_in_enemies: return
        spawn_x = random.randint(50, WIDTH - 50)
        spawn_y = -50
        path = random.choice(["straight", "straight", "sine", "sine", "circle"])
        if enemy_type is None:
            enemy_type = random.choice(["alien", "drone", "tank", "sniper"])
        enemy = Enemy(enemy_type, self.assets, spawn_x, spawn_y)
        # HP-Multiplikator aus Level-Config anwenden
        if self._level_config and self.game_mode == "normal":
            hp_mult = self._level_config.get("enemy_hp_multiplier", 1.0)
            if hp_mult != 1.0:
                enemy.max_hp = int(enemy.max_hp * hp_mult)
                enemy.hp = enemy.max_hp
        enemy.wave_id = f"fly_in_{self._fly_in_spawn_count}"
        enemy.movement_type = "fly_in"
        enemy.move_cfg = enemy.move_cfg.copy()
        enemy.move_cfg["type"] = "fly_in"
        enemy.move_cfg["path"] = path
        # Player-Tracking Parameter hinzufügen
        enemy.move_cfg["player_tracking_speed"] = 1.0
        enemy.move_cfg["player_tracking_threshold"] = 150
        if path == "sine":
            enemy.move_cfg["amplitude"] = random.randint(30, 50)
            enemy.move_cfg["frequency"] = random.uniform(0.8, 1.5)
        elif path == "circle":
            enemy.move_cfg["radius"] = random.randint(25, 40)
            enemy.move_cfg["frequency"] = random.uniform(0.6, 1.0)
        elif path == "straight":
            enemy._phase = random.choice([-1, 1]) * random.uniform(0.5, 2.0)
        enemy.move_cfg["target_y"] = random.randint(80, 150)
        self.fly_in_enemies.append(enemy)
        self._fly_in_spawn_count += 1

    def _spawn_boss_group(self, count=2, hp_multiplier=1.0):
        for _ in range(count):
            spawn_x = random.randint(100, WIDTH - 100)
            spawn_y = -80
            boss = Enemy("boss", self.assets, spawn_x, spawn_y)
            if hp_multiplier != 1.0:
                boss.max_hp = int(boss.max_hp * hp_multiplier)
                boss.hp = boss.max_hp
            boss.move_cfg = boss.move_cfg.copy()
            boss.move_cfg["type"] = "fly_in"
            boss.move_cfg["target_y"] = random.randint(100, 140)
            boss.move_cfg["path"] = "sine"
            boss.move_cfg["speed"] = 3.0
            boss.move_cfg["amplitude"] = 30
            boss.move_cfg["frequency"] = 0.5
            self.fly_in_enemies.append(boss)
            self._fly_in_spawn_count += 1
        self._boss_spawned = True
        self._max_fly_in_enemies = len(self.fly_in_enemies)
        print(f">>> BOSS SPAWNED! {count}x boss (HP mult: {hp_multiplier}x)")

    def _update_fly_in_spawning(self):
        now = pygame.time.get_ticks()

        # Survivor Mode: Aggressive Spawning mit Schwierigkeitsanstieg
        if self.game_mode == "survivor":
            # Schwierigkeit basierend auf Überlebenszeit
            time_elapsed = self.survivor_time  # In Sekunden

            # Mindestanzahl Gegner steigt mit Zeit
            if time_elapsed < 30:
                min_enemies = 5
            elif time_elapsed < 60:
                min_enemies = 7
            elif time_elapsed < 120:
                min_enemies = 10
            else:
                min_enemies = 12

            current_enemies = len(self.fly_in_enemies)

            # Wenn zu wenige Gegner: Instant-Spawn
            if current_enemies < min_enemies:
                spawn_interval = 100  # Fast instant (0.1s)
                group_size = min(3, min_enemies - current_enemies)  # Spawne mehrere gleichzeitig
            else:
                # Normale Spawn-Rate wenn genug Gegner da sind
                spawn_interval = self._fly_in_spawn_interval
                group_size = random.randint(1, 2)

            if (now - self._last_fly_in_spawn > spawn_interval and
                self._fly_in_spawn_count < self._max_fly_in_enemies):
                for _ in range(group_size):
                    if self._fly_in_spawn_count < self._max_fly_in_enemies:
                        self._spawn_fly_in_enemy()
                self._last_fly_in_spawn = now
            return

        # Normal Mode: Wave-basiertes Spawning
        if self._level_config is None:
            return

        # Boss-Phase: Warte bis Boss besiegt
        if self._boss_spawned:
            return

        # Alle Waves gespawnt + keine Gegner mehr → Boss spawnen
        if self._all_waves_done and len(self.fly_in_enemies) == 0:
            boss_config = self._level_config.get("boss", {})
            boss_count = boss_config.get("count", 1)
            boss_hp_mult = boss_config.get("hp_multiplier", 1.0)
            self._spawn_boss_group(count=boss_count, hp_multiplier=boss_hp_mult)
            return

        # Wave-Queue leer → nächste Wave starten
        if len(self._wave_enemy_queue) == 0 and not self._all_waves_done:
            waves = self._level_config.get("waves", [])
            if self._current_wave < len(waves):
                # Lade nächste Wave
                wave = waves[self._current_wave]
                self._wave_enemy_queue = []
                for enemy_type, count in wave["enemies"]:
                    self._wave_enemy_queue.extend([enemy_type] * count)
                random.shuffle(self._wave_enemy_queue)
                self._wave_total_enemies = len(self._wave_enemy_queue)
                self._wave_kills = 0
                spawn_delay = wave.get("spawn_delay", 3000)
                self._fly_in_spawn_interval = int(spawn_delay * self._level_config.get("spawn_speed_multiplier", 1.0))
                self._current_wave += 1
                self._last_fly_in_spawn = now  # Kurze Pause vor Wave-Start
                print(f">>> Wave {self._current_wave}/{len(waves)} started: {len(self._wave_enemy_queue)} enemies")
            else:
                # Alle Waves gespawnt
                self._all_waves_done = True
            return

        # Spawne Gegner aus der Queue
        if (now - self._last_fly_in_spawn > self._fly_in_spawn_interval and
            self._fly_in_spawn_count < self._max_fly_in_enemies and
            len(self._wave_enemy_queue) > 0):
            group_size = min(random.randint(2, 4), len(self._wave_enemy_queue))
            for _ in range(group_size):
                if self._wave_enemy_queue and self._fly_in_spawn_count < self._max_fly_in_enemies:
                    enemy_type = self._wave_enemy_queue.pop(0)
                    self._spawn_fly_in_enemy(enemy_type=enemy_type)
            self._last_fly_in_spawn = now

    def get_game_time(self):
        current_time = pygame.time.get_ticks()
        if self.paused:
            pause_time_so_far = current_time - self.pause_start_time
            return current_time - self.total_pause_time - pause_time_so_far
        return current_time - self.total_pause_time

    # ---------------- Events ----------------
    def _handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    if not self.paused:
                        self.pause_start_time = pygame.time.get_ticks()
                        self.paused           = True
                        self.game_state       = "paused"
                        self.menu.set_pause_mode(True)
                        try: pygame.mixer.music.pause()
                        except pygame.error: pass
                    else:
                        self.total_pause_time += pygame.time.get_ticks() - self.pause_start_time
                        self.paused     = False
                        self.game_state = "playing"
                        try: pygame.mixer.music.unpause()
                        except pygame.error: pass
                elif e.key == pygame.K_F11:
                    self.toggle_maximize()
                elif e.key == pygame.K_RETURN and (pygame.key.get_pressed()[pygame.K_LALT] or pygame.key.get_pressed()[pygame.K_RALT]):
                    self.toggle_fullscreen()
                elif e.key == pygame.K_1:
                    self.player.set_stage(1); self._update_shield_scale()
                    if self.game_mode == "survivor":
                        self.player.current_health = 1
                        self.player.max_health = 1
                elif e.key == pygame.K_2:
                    self.player.set_stage(2); self._update_shield_scale()
                    if self.game_mode == "survivor":
                        self.player.current_health = 1
                        self.player.max_health = 1
                elif e.key == pygame.K_3:
                    self.player.set_stage(3); self._update_shield_scale()
                    if self.game_mode == "survivor":
                        self.player.current_health = 1
                        self.player.max_health = 1
                elif e.key == pygame.K_4:
                    self.player.set_stage(4); self._update_shield_scale()
                    if self.game_mode == "survivor":
                        self.player.current_health = 1
                        self.player.max_health = 1
                elif e.key == pygame.K_5:
                    self.player.set_stage(5); self._update_shield_scale()
                    if self.game_mode == "survivor":
                        self.player.current_health = 1
                        self.player.max_health = 1
                # elif e.key == pygame.K_F1:
                #     self._build_wave('alien')
                # elif e.key == pygame.K_F2:
                #     self._build_wave('drone')
                # elif e.key == pygame.K_F3:
                #     self._build_wave('tank')
                # elif e.key == pygame.K_F4:
                #     self._build_wave('sniper')
                # elif e.key == pygame.K_F5:
                #     self._build_wave('boss')
                # elif e.key == pygame.K_F12 and not (pygame.key.get_pressed()[pygame.K_LALT] or pygame.key.get_pressed()[pygame.K_RALT]):
                #     self.enemies = []
                elif e.key == pygame.K_SPACE and not self.paused and not self.player_dead:
                    shots = self.player.shoot_weapon("laser")
                    if self.double_laser_active and shots:
                        enhanced = []
                        for shot in shots:
                            ds = DoubleLaser.create(shot.rect.centerx, shot.rect.centery, self.assets, owner="player", angle_deg=0)
                            enhanced.append(ds)
                        self._add_player_shots(enhanced)
                    else:
                        self._add_player_shots(shots)
                elif e.key == pygame.K_r and not self.paused and not self.player_dead:
                    shots = self.player.shoot_weapon("rocket")
                    if shots:
                        self._add_player_shots(shots)
                        self.weapon_cooldowns["rocket_last_used"] = pygame.time.get_ticks()
                elif e.key == pygame.K_t and not self.paused and not self.player_dead:
                    shots = self.player.shoot_weapon("homing_rocket")
                    if shots:
                        self._add_player_shots(shots)
                        self.weapon_cooldowns["homing_rocket_last_used"] = pygame.time.get_ticks()
                elif e.key == pygame.K_b and not self.paused and not self.player_dead:
                    shots = self.player.shoot_weapon("blaster")
                    if shots:
                        self._add_player_shots(shots)
                        self.weapon_cooldowns["blaster_last_used"] = pygame.time.get_ticks()
                elif e.key == pygame.K_e and not self.paused and not self.player_dead:
                    shots = self.player.shoot_weapon("nuke")
                    if shots:
                        self._add_player_shots(shots)
                        self.weapon_cooldowns["nuke_last_used"] = pygame.time.get_ticks()
                elif e.key == pygame.K_q and not self.paused and not self.player_dead:
                    # Survivor Mode: Kein normales Shield
                    if self.game_mode == "survivor":
                        break

                    from config.ship import SHIP_CONFIG
                    has_shield = SHIP_CONFIG.get(self.player.stage, {}).get("shield", 0) == 1
                    if not has_shield: break
                    if self.shield:
                        self.shield = None
                        break
                    now = pygame.time.get_ticks()
                    if now >= self._shield_ready_at:
                        frames = self.assets.get("shield_frames")
                        fps    = self.assets.get("shield_fps")
                        scale_f = max(self.player.rect.w, self.player.rect.h) / frames[0].get_width() * self.assets.get("shield_scale")

                        new_shield = Shield(*self.player.rect.center, frames, fps=fps, scale=scale_f, loop=True, player_health=self.player.max_health)
                        shield_cfg = SHIELD_CONFIG[1]["shield"]
                        regen_rate = shield_cfg.get("regen_rate", 0.2)
                        min_health = int(new_shield.max_health * shield_cfg.get("min_health_percentage", 0.3))
                        time_since_last = max(0, now - getattr(self, '_last_shield_destroyed', 0))
                        health_regen = min(new_shield.max_health, new_shield.max_health * regen_rate * (time_since_last/1000.0))
                        new_shield.current_health = max(min_health, int(health_regen))
                        self.shield = new_shield
                        self.shield_until     = now + self.assets.get("shield_duration")
                        self._shield_ready_at = now + self.assets.get("shield_cooldown")
                        if self.assets.get("shield_activate_sound"):
                            self.assets.get("shield_activate_sound").set_volume(MASTER_VOLUME * SFX_VOLUME)
                            self.assets.get("shield_activate_sound").play()

    # ---------------- Update ----------------
    def _update(self):
        keys = pygame.key.get_pressed()
        now  = pygame.time.get_ticks()

        self._update_fly_in_spawning()

        self.weapon_cooldowns["shield_ready_at"] = self._shield_ready_at
        self.hud.update_weapon_status(self.player, now, self.weapon_cooldowns)
        self.hud.update_emp_status(self.emp_powerup, now)

        game_time = self.get_game_time()
        super_shield_active = self.powerup_shield is not None
        super_shield_until  = self.powerup_shield_until if super_shield_active else 0
        self.hud.update_powerup_status(
            self.double_laser_active, self.double_laser_until,
            super_shield_active, super_shield_until,
            self.speed_boost_active, self.speed_boost_until,
            game_time
        )

        # Survivor Mode: Timer aktualisieren
        if self.game_mode == "survivor" and not self.player_dead:
            self.survivor_time = (pygame.time.get_ticks() - self.survivor_start_time) / 1000.0

        if not self.player_dead:
            self.health_bar.update(self.player.get_health_percentage())

        # Respawn nur im Normal Mode, nicht im Survivor Mode
        if self.player_dead and self.game_mode != "survivor":
            if self.lives > 0 and now >= self._respawn_ready_at:
                self._respawn()

        if not self.player_dead:
            cw, ch = self.screen.get_size()
            self.player.handle_input(keys, cw, ch)

        if keys[pygame.K_SPACE] and not self.paused and not self.player_dead:
            shots = self.player.shoot_weapon("laser")
            if self.double_laser_active and shots:
                enhanced = []
                for shot in shots:
                    ds = DoubleLaser.create(shot.rect.centerx, shot.rect.centery, self.assets, owner="player", angle_deg=0)
                    enhanced.append(ds)
                self._add_player_shots(enhanced)
            else:
                self._add_player_shots(shots)

        if keys[pygame.K_v] and not self.paused and not self.player_dead:
            if self.emp_powerup.can_use(now):
                self.emp_powerup.use(self, self.player.rect.center, now)

        self.projectile_manager.update(self.clock.get_time() / 1000.0, HEIGHT)

        for shot in self.projectile_manager.get_player_shots():
            if getattr(shot, 'homing', False): shot.update(self)
        for shot in self.projectile_manager.get_enemy_shots():
            if getattr(shot, 'homing', False): shot.update(self)

        dt = self.clock.get_time() / 1000.0
        for enemy in self.enemies:
            if hasattr(enemy, 'update_emp_effects'): enemy.update_emp_effects(dt)

        for e in self.enemies[:]:
            if e.offscreen(): self.enemies.remove(e)

        for emp_wave in self.emp_waves[:]:
            if not emp_wave.update(dt, self): self.emp_waves.remove(emp_wave)

        # Fly-in enemies werden bereits in _update_fly_in_enemies() aktualisiert
        for enemy in self.fly_in_enemies[:]:
            if (enemy.rect.y > HEIGHT + 50 or enemy.rect.x < -100 or enemy.rect.x > WIDTH + 100):
                self.fly_in_enemies.remove(enemy)
                self._fly_in_spawn_count = max(0, self._fly_in_spawn_count - 1)

        self._update_powerups()

        if self.shield:
            self.shield.set_center(self.player.rect.center)
            self.shield.update()
            if now >= self.shield_until or self.shield.done:
                self._last_shield_destroyed = now
                self.shield = None

        if self.powerup_shield:
            self.powerup_shield.set_center(self.player.rect.center)
            self.powerup_shield.update()
            if self.get_game_time() >= self.powerup_shield_until or self.powerup_shield.done:
                self.powerup_shield = None

        if self.double_laser_active and self.get_game_time() >= self.double_laser_until:
            self.double_laser_active = False

        if self.speed_boost_active and self.get_game_time() >= self.speed_boost_until:
            self.speed_boost_active = False
            if self.original_player_speed is not None:
                self.player.speed = self.original_player_speed

        self._update_wave_enemies()
        self._update_fly_in_enemies()

        for en in self.enemies:
            for w, amt in en.weapons.items():
                if amt > 0:
                    for s in en.shoot_weapon(w, amt):
                        self.projectile_manager.add_enemy_shot(s)
        for en in self.fly_in_enemies:
            for w, amt in en.weapons.items():
                if amt > 0:
                    for s in en.shoot_weapon(w, amt):
                        self.projectile_manager.add_enemy_shot(s)

        # Enemy->Player
        if not self.player_dead:
            for p in self.projectile_manager.get_enemy_shots():
                hit_shield = False
                hit_powerup_shield = False
                if self.shield and not self.shield.is_broken() and self.shield.hit_by_projectile(p.rect):
                    dmg = getattr(p, "dmg", 100)
                    shield_cfg = SHIELD_CONFIG[1]["shield"]
                    absorbed = min(dmg * shield_cfg.get("damage_reduction", 0.9), self.shield.current_health)
                    active = self.shield.take_damage(absorbed)
                    self.shield.play_hit_sound(self.assets)
                    hit_shield = True
                    if not active:
                        self._last_shield_destroyed = now
                        self.shield = None
                if self.powerup_shield and not self.powerup_shield.is_broken() and self.powerup_shield.hit_by_projectile(p.rect):
                    dmg = getattr(p, "dmg", 100)
                    absorbed = min(dmg, self.powerup_shield.current_health)
                    active = self.powerup_shield.take_damage(absorbed)
                    self.powerup_shield.play_hit_sound(self.assets)
                    hit_powerup_shield = True
                    if not active:
                        self.powerup_shield = None
                    self.projectile_manager.remove_shot(p)
                    continue
                if p.rect.colliderect(self.player.rect):
                    if now < getattr(self.player, "invincible_until", 0):
                        self.projectile_manager.remove_shot(p)
                        continue
                    self.projectile_manager.remove_shot(p)
                    dmg = getattr(p, "dmg", 100)
                    has_power = hit_powerup_shield or (self.powerup_shield and not self.powerup_shield.is_broken())
                    has_norm  = hit_shield or (self.shield and not self.shield.is_broken())
                    destroyed = False if has_power else self.player.take_damage(dmg, has_norm)
                    if hasattr(p, "on_hit"): p.on_hit(self, self.player.rect.center)
                    if destroyed:
                        frames = self.assets.get("expl_laser", [])
                        fps    = self.assets.get("expl_laser_fps", 24)
                        self.explosion_manager.add_explosion(self.player.rect.centerx, self.player.rect.centery, frames, fps=fps, scale=2.5)
                        self.player_dead       = True

                        # Survivor Mode: Namen eingeben
                        if self.game_mode == "survivor":
                            self.survivor_player_name = ""
                            self.game_state = "survivor_name_input"
                        else:
                            # Normal Mode: Nur bei letztem Leben (Game Over) Namen eingeben
                            if self.lives <= 0:
                                self.game_state = "normal_name_input"
                            else:
                                self._respawn_ready_at = now + self.lives_cooldown
                    break

        # Player->Enemy
        for p in self.projectile_manager.get_player_shots():
            hit_enemy = None
            for en in self.enemies:
                if p.rect.colliderect(en.rect):
                    hit_enemy = en; break
            if not hit_enemy:
                for en in self.fly_in_enemies:
                    if p.rect.colliderect(en.rect):
                        hit_enemy = en; break
            if not hit_enemy: continue

            # Koordinaten SOFORT speichern - unabhängig von Enemy-Objekt!
            enemy_x = hit_enemy.rect.centerx
            enemy_y = hit_enemy.rect.centery
            hit_pos = (enemy_x, enemy_y)

            # Prüfe zuerst ob der Treffer tödlich ist (für Single-Target Waffen)
            weapon_kind = getattr(p, "kind", "generic")
            weapon_owner = getattr(p, "owner", "player")
            damage = getattr(p, "dmg", 10)
            will_die = (hit_enemy.hp <= damage)

            # DEBUG: Treffer registriert
            timestamp = pygame.time.get_ticks()
            print(f"[{timestamp}ms] HIT! {p.__class__.__name__} -> {hit_enemy.etype} | HP: {hit_enemy.hp}/{damage} | will_die={will_die} | pos=({enemy_x},{enemy_y})")

            # AoE-Waffen (Rocket, HomingRocket, Blaster, Nuke) rufen IMMER on_hit() auf
            # Single-Target Waffen (Laser, DoubleLaser) rufen on_hit() NUR auf wenn Enemy ÜBERLEBT
            is_single_target = weapon_kind in ("laser", "double_laser")

            if hasattr(p, "on_hit"):
                if not is_single_target or not will_die:
                    # AoE-Waffen: Immer on_hit() (handhaben eigene Explosionen)
                    # Single-Target: Nur wenn Enemy überlebt (HIT-Explosion)
                    print(f"[{timestamp}ms]   HIT-Explosion: {p.__class__.__name__}.on_hit() called")
                    p.on_hit(self, hit_pos)
                    # KEIN log_weapon_explosion() mehr - wird bereits in on_hit() mit Kategorie gezählt!
                else:
                    print(f"[{timestamp}ms]   HIT-Explosion: SKIPPED (enemy will die, waiting for DESTROY)")

            # DESTROY-Explosion für Single-Target Waffen MUSS IMMER erstellt werden
            # Verwendet gespeicherte Koordinaten - egal ob Enemy noch existiert!
            if is_single_target and will_die and weapon_owner == "player":
                print(f"[{timestamp}ms]   DESTROY-Explosion: Creating at ({enemy_x},{enemy_y})")
                # Sound abspielen
                if self.assets.get("laser_sound_destroy"):
                    self.assets.get("laser_sound_destroy").set_volume(MASTER_VOLUME * SFX_VOLUME)
                    self.assets.get("laser_sound_destroy").play()

                # Volle Explosion für getöteten Enemy (an gespeicherter Position)
                frames = self.assets.get("expl_laser", [])
                fps    = self.assets.get("expl_laser_fps", 30)  # SCHNELLER: 30 statt 26/10

                # Falls FPS zu langsam ist (von Asset), überschreiben
                if fps < 20:
                    print(f"[{timestamp}ms]   [WARNING] Asset FPS={fps} too slow, overriding to 30!")
                    fps = 30

                self.explosion_manager.add_explosion(
                    x                  = enemy_x,
                    y                  = enemy_y,
                    frames             = frames,
                    fps                = fps,
                    scale              = 1.5,
                    weapon_type        = p.__class__.__name__,
                    explosion_category = "destroy"
                )
                print(f"[{timestamp}ms]   DESTROY-Explosion: CREATED! Frames={len(frames)}, FPS={fps}, Duration={len(frames)/fps:.2f}s")
                print(f"[{timestamp}ms]   Explosion should finish at: {timestamp + (len(frames)/fps*1000):.0f}ms")
            elif is_single_target and will_die:
                print(f"[{timestamp}ms]   DESTROY-Explosion: SKIPPED (owner={weapon_owner}, not 'player')")
            elif not is_single_target and will_die and weapon_owner == "player":
                # AoE-Waffen: Direkt getroffener Enemy bekommt AUCH eine DESTROY-Explosion
                # (zusätzlich zu denen die _apply_aoe() erstellt)
                print(f"[{timestamp}ms]   DESTROY-Explosion (AoE direct hit): Creating at ({enemy_x},{enemy_y})")
                # Benutze passende Explosion für Waffe
                expl_key = "expl_rocket" if weapon_kind in ("rocket", "homing_rocket") else "expl_blaster" if weapon_kind == "blaster" else "expl_nuke"
                frames = self.assets.get(expl_key, [])
                fps = self.assets.get(f"{expl_key}_fps", 30)

                self.explosion_manager.add_explosion(
                    x                  = enemy_x,
                    y                  = enemy_y,
                    frames             = frames,
                    fps                = fps,
                    scale              = 1.5,
                    weapon_type        = p.__class__.__name__,
                    explosion_category = "destroy"
                )
                print(f"[{timestamp}ms]   DESTROY-Explosion (AoE): CREATED!")

            self.projectile_manager.remove_shot(p)

            # Prüfe ob Enemy noch existiert (könnte bereits von anderem Projektil getötet worden sein)
            enemy_exists = (hit_enemy in self.enemies) or (hit_enemy in self.fly_in_enemies)
            if not enemy_exists:
                # Enemy wurde bereits getötet -> Explosion wurde oben erstellt, jetzt skip
                print(f"[{timestamp}ms]   Enemy already removed from list (race condition) -> skipping damage/score")
                continue

            dead = hit_enemy.take_damage(damage)
            print(f"[{timestamp}ms]   take_damage({damage}) -> dead={dead}, HP now: {hit_enemy.hp}")

            if dead:
                print(f"[{timestamp}ms]   Enemy KILLED! Registering death, adding score +{hit_enemy.points}")

                # DESTROY-Explosion erstellen wenn noch keine existiert
                # (z.B. wenn Enemy erst durch AoE-Schaden stirbt, nicht durch direkten Treffer)
                if not will_die and weapon_owner == "player":
                    print(f"[{timestamp}ms]   DESTROY-Explosion (killed by AoE damage): Creating at ({enemy_x},{enemy_y})")

                    # Benutze passende Explosion für Waffe
                    if is_single_target:
                        expl_key = "expl_laser"
                        fps = 30
                    else:
                        expl_key = "expl_rocket" if weapon_kind in ("rocket", "homing_rocket") else "expl_blaster" if weapon_kind == "blaster" else "expl_nuke"
                        fps = self.assets.get(f"{expl_key}_fps", 30)

                    frames = self.assets.get(expl_key, [])

                    self.explosion_manager.add_explosion(
                        x                  = enemy_x,
                        y                  = enemy_y,
                        frames             = frames,
                        fps                = fps,
                        scale              = 1.5,
                        weapon_type        = p.__class__.__name__,
                        explosion_category = "destroy"
                    )
                    print(f"[{timestamp}ms]   DESTROY-Explosion: CREATED!")

                self.explosion_manager.register_enemy_death(p.__class__.__name__)
                self.score += hit_enemy.points
                self.highscore = max(self.highscore, self.score)
                self._total_kills += 1

                # Tracke Kills je nach Mode
                if self.game_mode == "survivor":
                    self.survivor_kills += 1
                else:
                    self.kills += 1  # Normal Mode

                self._show_kill_counter()
                self._try_drop_powerup(enemy_x, enemy_y)

                if hit_enemy in self.enemies:
                    self.enemies.remove(hit_enemy)
                    print(f"[{timestamp}ms]   Removed from self.enemies")
                elif hit_enemy in self.fly_in_enemies:
                    self.fly_in_enemies.remove(hit_enemy)
                    self._fly_in_spawn_count = max(0, self._fly_in_spawn_count - 1)
                    print(f"[{timestamp}ms]   Removed from self.fly_in_enemies")
            else:
                print(f"[{timestamp}ms]   Enemy survived (HP: {hit_enemy.hp})")
            print()  # Leerzeile für Übersichtlichkeit

        self.explosion_manager.update()

        # Victory Check: Boss spawned, all enemies defeated, no active explosions
        if (self.game_state == "playing" and
            self._boss_spawned and
            len(self.enemies) == 0 and
            len(self.fly_in_enemies) == 0 and
            len(self.explosion_manager.explosions) == 0):
            # Normal Mode → direkt zur Namenseingabe
            # Survivor Mode → Victory Screen (kann wiederholen)
            if self.game_mode == "normal":
                if self.level < 5:
                    self.game_state = "level_complete"
                    print(f">>> LEVEL {self.level} COMPLETE! → Upgrade Screen <<<")
                else:
                    self.game_state = "normal_name_input"
                    print(f">>> ALL LEVELS COMPLETE! → Name Input <<<")
            else:
                self.game_state = "victory"
                print(f">>> LEVEL COMPLETE! Victory Screen activated! <<<")

    # ---------------- Draw ----------------
    def _draw(self):
        if self._bg_scaled:
            self.screen.blit(self._bg_scaled, (0, 0))
        else:
            self.screen.fill((0, 0, 0))

        self.projectile_manager.draw(self.screen)
        for en in self.enemies: en.draw(self.screen)
        for en in self.fly_in_enemies: en.draw(self.screen)
        self.powerup_manager.draw(self.screen)
        self.explosion_manager.draw(self.screen)

        for emp_wave in self.emp_waves:
            emp_wave.draw(self.screen)

        if not self.player_dead:
            self.player.draw(self.screen)
            if self.shield: self.shield.draw(self.screen)
            if self.powerup_shield: self.powerup_shield.draw(self.screen)

        cw, ch = self.screen.get_size()
        ui_scale = max(cw / 1920, ch / 1080) * 1.2
        score_x = int(15 * ui_scale)
        score_y = int(15 * ui_scale)
        highscore_y = int(55 * ui_scale)

        if not self.game_mode == "survivor":
            self.screen.blit(self.font.render(f"Score: {self.score}", True, (255,255,255)), (score_x, score_y))
            self.screen.blit(self.font.render(f"High Score: {self.highscore}", True, (255,255,255)), (score_x, highscore_y))

            # Leben-Anzeige mit kleinen Schiffen (immer anzeigen)
            lives_y = int(95 * ui_scale)

            # Benutze das aktuelle Schiffsbild vom Player
            ship_icon = None
            if self.player and hasattr(self.player, 'base_img') and self.player.base_img:
                ship_icon = self.player.base_img

            if ship_icon:
                # Skaliere das Schiff auf Icon-Größe (30x30)
                icon_size = 30
                ship_icon_scaled = pygame.transform.scale(ship_icon, (icon_size, icon_size))

                # "Lives:" Label
                lives_label = self.font.render("Lives:", True, (255, 255, 255))
                self.screen.blit(lives_label, (score_x, lives_y))

                # Zeichne so viele Schiffe wie Leben übrig sind (nach dem Label)
                label_width = lives_label.get_width() + int(10 * ui_scale)
                for i in range(max(0, self.lives)):
                    icon_x = score_x + label_width + i * 35  # 35px Abstand zwischen Icons
                    self.screen.blit(ship_icon_scaled, (icon_x, lives_y))
            else:
                # Fallback: Text-Anzeige wenn Player noch nicht existiert
                lives_text = self.font.render(f"Lives: {self.lives}", True, (255, 255, 255))
                self.screen.blit(lives_text, (score_x, lives_y))

        current_time = pygame.time.get_ticks()
        if self.kill_display_timer > 0 and current_time - self.kill_display_timer < self.kill_display_duration:
            kill_surface = self.font.render(self.kill_display_text, True, (255, 255, 0))
            kill_rect = kill_surface.get_rect(center=(cw // 2, int(100 * ui_scale)))
            self.screen.blit(kill_surface, kill_rect)

        # Life Lost Anzeige (rot, unter Kill-Display)
        if self.life_lost_display_timer > 0 and current_time - self.life_lost_display_timer < self.life_lost_display_duration:
            life_lost_surface = self.font.render(self.life_lost_display_text, True, (255, 50, 50))
            life_lost_rect = life_lost_surface.get_rect(center=(cw // 2, int(150 * ui_scale)))
            self.screen.blit(life_lost_surface, life_lost_rect)

        if not self.player_dead:
            self.health_bar.draw(self.screen, self.player.get_health_percentage(), self.player.current_health, self.player.max_health)
            if self.shield and not self.shield.is_broken():
                old_colors = self.shield_health_bar.health_colors.copy()
                self.shield_health_bar.health_colors = {
                    "high": (0, 150, 255),
                    "medium": (100, 200, 255),
                    "low": (255, 150, 0),
                    "critical": (255, 0, 0)
                }
                self.shield_health_bar.draw(self.screen, self.shield.get_health_percentage(), self.shield.current_health, self.shield.max_health, "SHIELD")
                self.shield_health_bar.health_colors = old_colors

        self.hud.draw(self.screen)

        # Survivor Mode Timer anzeigen
        if self.game_mode == "survivor" and not self.player_dead:
            timer_font = pygame.font.Font(None, int(60 * ui_scale))
            minutes = int(self.survivor_time // 60)
            seconds = int(self.survivor_time % 60)
            millis = int((self.survivor_time % 1) * 100)
            timer_str = f"{minutes:02d}:{seconds:02d}.{millis:02d}"

            timer_text = timer_font.render(timer_str, True, (255, 100, 100))
            timer_rect = timer_text.get_rect(center=(cw // 2, int(50 * ui_scale)))

            # Schatten
            shadow = timer_font.render(timer_str, True, (0, 0, 0))
            shadow_rect = shadow.get_rect(center=(cw // 2 + 2, int(50 * ui_scale) + 2))
            self.screen.blit(shadow, shadow_rect)
            self.screen.blit(timer_text, timer_rect)

            # "SURVIVOR MODE" Text
            mode_font = pygame.font.Font(None, int(30 * ui_scale))
            mode_text = mode_font.render("SURVIVOR MODE", True, (255, 150, 150))
            mode_rect = mode_text.get_rect(center=(cw // 2, int(20 * ui_scale)))
            self.screen.blit(mode_text, mode_rect)

            # Rekord anzeigen (oben links)
            if hasattr(self, 'survivor_best_time') and self.survivor_best_time > 0:
                record_font = pygame.font.Font(None, int(28 * ui_scale))
                stage_names = ["ROOKIE", "VETERAN", "ELITE", "LEGEND"]
                stage_name = stage_names[self.survivor_selected_stage - 1]

                # Stage-Name
                stage_text = record_font.render(f"HIGHSCORE ({stage_name}):", True, (255, 200, 100))
                stage_rect = stage_text.get_rect(topleft=(int(20 * ui_scale), int(20 * ui_scale)))
                self.screen.blit(stage_text, stage_rect)

                # display_time  = max(best_time, self.survivor_time)
                # display_kills = best_kills if self.survivor_time < best_time else max(best_kills, self.survivor_kills)

                # Rekord-Zeit
                rec_mins  = int(self.survivor_best_time // 60)
                rec_secs  = int(self.survivor_best_time % 60)
                rec_millis = int((self.survivor_best_time % 1) * 100)
                record_time_str = f"{rec_mins:02d}:{rec_secs:02d}.{rec_millis:02d}"
                record_time_text = record_font.render(f"TIME: {record_time_str}", True, (255, 100, 100))
                record_time_rect = record_time_text.get_rect(topleft=(int(20 * ui_scale), int(50 * ui_scale)))
                self.screen.blit(record_time_text, record_time_rect)

                # Rekord-Kills
                record_kills_text = record_font.render(f"KILLS: {self.survivor_best_kills}", True, (255, 255, 255))
                record_kills_rect = record_kills_text.get_rect(topleft=(int(20 * ui_scale), int(80 * ui_scale)))
                self.screen.blit(record_kills_text, record_kills_rect)

                # Rekord-Name
                record_name_text = record_font.render(f"BY: {self.survivor_best_name}", True, (255, 255, 255))
                record_name_rect = record_name_text.get_rect(topleft=(int(20 * ui_scale), int(110 * ui_scale)))
                self.screen.blit(record_name_text, record_name_rect)

        pygame.display.flip()

    def kill_player(self):
        if self.player_dead: return
        self.player_dead = True

        # Survivor Mode: Sofort Game Over, Namen eingeben
        if self.game_mode == "survivor":
            self.survivor_player_name = ""
            self.game_state = "survivor_name_input"
        else:
            self._respawn_ready_at = pygame.time.get_ticks() + self.lives_cooldown

    def _respawn(self):
        if self.lives > 0:
            self.lives -= 1
            # Zeige "Life Lost" Nachricht
            self.life_lost_display_text = f"LIFE LOST! {self.lives} remaining"
            self.life_lost_display_timer = pygame.time.get_ticks()
        cw, ch = self.screen.get_size()
        self.player = Player(cw, ch, self.assets)
        self.player.rect.center = self.spawn_pos
        self.player_dead = False
        self._respawn_ready_at = 0

    def _run_sub_state(self):
        """Führt einen Frame des aktuellen Sub-States aus (alles außer playing/paused).
        Wird vom AppController aufgerufen für States wie survivor_name_input etc."""
        gs = self.game_state

        if gs == "survivor_ship_select":
            if not self.menu.menu_music_playing:
                self.menu.start_menu_music()
            self.ship_select_screen.selected_stage = self.survivor_selected_stage
            action = self.ship_select_screen.handle_and_draw(self.screen, self._bg_scaled, self.assets)
            if action == "quit":
                self.running = False
            elif action == "back":
                self.game_state = "menu"
            elif isinstance(action, int):
                self.survivor_selected_stage = action
                self.game_state = "playing"
                self.menu.stop_menu_music()
                self._start_game_mode()
            elif action is None:
                self.survivor_selected_stage = self.ship_select_screen.selected_stage

        elif gs == "level_complete":
            from system.screens.upgrade_screen import UpgradeScreen
            if not hasattr(self, '_upgrade_screen') or self._upgrade_screen is None:
                ship_stage = self.player.stage if hasattr(self.player, 'stage') else 1
                self._upgrade_screen = UpgradeScreen(ship_stage=ship_stage)
            result = self._upgrade_screen.handle_and_draw(
                self.screen, self.score, self.level, self._total_kills, self.assets
            )
            if result == "quit":
                self.running = False
            elif isinstance(result, tuple) and result[0] == "continue":
                _, new_score, upgrades = result
                self.score = new_score
                self._apply_upgrades(upgrades)
                self._upgrade_screen = None
                self._start_next_level()

        elif gs == "victory":
            if not self.menu.menu_music_playing:
                try: pygame.mixer.music.stop()
                except pygame.error: pass
                self.menu.start_menu_music()
            action = self.victory_screen.handle_and_draw(
                self.screen, self._bg_scaled, self.score, self._total_kills,
                self.projectile_manager, self.powerup_manager, self.explosion_manager,
                self.player, self.shield, self.powerup_shield, self.player_dead
            )
            if action == "quit":
                self.running = False
            elif action == "replay":
                self.menu.stop_menu_music()
                self.game_state = "playing"
                self._start_game_mode()
            elif action == "menu":
                if self.game_mode == "normal":
                    self.game_state = "normal_name_input"
                else:
                    self._handle_menu_return()

        elif gs == "survivor_name_input":
            if not self.menu.menu_music_playing:
                try: pygame.mixer.music.stop()
                except pygame.error: pass
                self.menu.start_menu_music()
            action = self.survivor_name_input_screen.handle_and_draw(
                self.screen, self._bg_scaled, self.survivor_time, self.survivor_kills,
                self.survivor_selected_stage
            )
            if action == "quit":
                self.running = False
            elif action == "submit":
                self.game_state = "survivor_game_over"
            elif action == "skip":
                self.game_state = "survivor_game_over"

        elif gs == "survivor_game_over":
            action = self.survivor_game_over_screen.handle_and_draw(
                self.screen, self._bg_scaled, self.survivor_time, self.survivor_kills,
                self.survivor_selected_stage
            )
            if action == "quit":
                self.running = False
            elif action == "retry":
                self.game_state = "survivor_ship_select"
            elif action == "menu":
                self._handle_menu_return()

        elif gs == "normal_name_input":
            if not self.menu.menu_music_playing:
                try: pygame.mixer.music.stop()
                except pygame.error: pass
                self.menu.start_menu_music()
            stats_dict = {'Score': self.score, 'Kills': self._total_kills, 'Level': self.level}
            action = self.game_over_screen.handle_and_draw(
                self.screen, self._bg_scaled, stats_dict, self.menu
            )
            if action == "quit":
                self.running = False
            elif action in ("submit", "skip"):
                self.came_from = 'game'
                self.game_state = "normal_top10"

        elif gs == "normal_top10":
            if not hasattr(self, '_normal_top10_loaded') or not self._normal_top10_loaded:
                from system.utils import load_normal_top10
                self._normal_top10_data = load_normal_top10()[:10]
                self._normal_top10_loaded = True
            action = self.top10_normal_screen.handle_and_draw(
                self.screen, self._bg_scaled, self._normal_top10_data, self.menu,
                came_from=self.came_from if self.came_from else 'menu'
            )
            if action == "quit":
                self.running = False
            elif action == "retry":
                self._normal_top10_loaded = False
                self.menu.stop_menu_music()
                self.game_state = "playing"
                self._start_game_mode()
            elif action == "menu":
                self._normal_top10_loaded = False
                self.came_from = None
                self._handle_menu_return()

        pygame.display.flip()

    # ---------------- Loop ----------------
    def run(self):
        while self.running:
            frame_time = self.clock.tick(FPS) / 1000.0
            self.accumulated_time += frame_time

            if self.game_state == "menu":
                self._handle_menu()
            elif self.game_state == "playing":
                self._handle_events()
                if not self.paused:
                    updates = 0
                    while self.accumulated_time >= self.fixed_timestep and updates < self.max_steps_per_frame:
                        self._physics_update()
                        self.accumulated_time -= self.fixed_timestep
                        updates += 1
                    if self.accumulated_time > self.fixed_timestep:
                        self.accumulated_time = 0.0
                    self._update()
                self._draw()
            elif self.game_state == "paused":
                self._handle_pause_menu()
            elif self.game_state == "survivor_ship_select":
                # Starte Menümusik wenn noch nicht gestartet
                if not self.menu.menu_music_playing:
                    self.menu.start_menu_music()
                # Synchronize stage selection between game and screen
                self.ship_select_screen.selected_stage = self.survivor_selected_stage
                action = self.ship_select_screen.handle_and_draw(self.screen, self._bg_scaled, self.assets)
                if action == "quit":
                    self.running = False
                elif action == "back":
                    self.game_state = "menu"
                    self.menu.set_mode_select(True)
                elif action == "maximize":
                    self.toggle_maximize()
                elif action == "fullscreen":
                    self.toggle_fullscreen()
                elif isinstance(action, int):  # Stage number selected
                    self.survivor_selected_stage = action
                    self.game_state = "playing"
                    self.menu.stop_menu_music()  # Stoppe Menümusik
                    self._start_game_mode()
                # Update game's selected stage to match screen selection (for arrow key changes)
                if action is None:
                    self.survivor_selected_stage = self.ship_select_screen.selected_stage
            elif self.game_state == "level_complete":
                from system.screens.upgrade_screen import UpgradeScreen
                if not hasattr(self, '_upgrade_screen') or self._upgrade_screen is None:
                    ship_stage = self.player.stage if hasattr(self.player, 'stage') else 1
                    self._upgrade_screen = UpgradeScreen(ship_stage=ship_stage)
                result = self._upgrade_screen.handle_and_draw(
                    self.screen, self.score, self.level, self._total_kills, self.assets
                )
                if result == "quit":
                    self.running = False
                elif isinstance(result, tuple) and result[0] == "continue":
                    _, new_score, upgrades = result
                    self.score = new_score
                    # Upgrades anwenden
                    self._apply_upgrades(upgrades)
                    # Reset Upgrade-Screen für nächstes Level
                    self._upgrade_screen = None
                    # Nächstes Level starten
                    self._start_next_level()

            elif self.game_state == "victory":
                # Starte Menümusik wenn noch nicht gestartet (Spielmusik stoppen)
                if not self.menu.menu_music_playing:
                    try:
                        pygame.mixer.music.stop()
                    except pygame.error:
                        pass
                    self.menu.start_menu_music()

                action = self.victory_screen.handle_and_draw(
                    self.screen, self._bg_scaled, self.score, self._total_kills,
                    self.projectile_manager, self.powerup_manager, self.explosion_manager,
                    self.player, self.shield, self.powerup_shield, self.player_dead
                )
                if action == "quit":
                    self.running = False
                elif action == "replay":
                    self.menu.stop_menu_music()  # Stoppe Menümusik
                    self.game_state = "playing"  # Setze State auf playing
                    self._start_game_mode()
                elif action == "menu":
                    # Nach Victory Screen → Namenseingabe für Normal Mode
                    if self.game_mode == "normal":
                        self.game_state = "normal_name_input"
                    else:
                        # Survivor Mode: Kehre zum AppController oder Original Menu zurück
                        if self._handle_menu_return():
                            return  # AppController übernimmt
                elif action == "maximize":
                    self.toggle_maximize()
                elif action == "fullscreen":
                    self.toggle_fullscreen()
            elif self.game_state == "survivor_name_input":
                # Starte Menümusik wenn noch nicht gestartet (Spielmusik stoppen)
                if not self.menu.menu_music_playing:
                    try:
                        pygame.mixer.music.stop()
                    except pygame.error:
                        pass
                    self.menu.start_menu_music()

                action = self.survivor_name_input_screen.handle_and_draw(
                    self.screen, self._bg_scaled, self.survivor_time, self.survivor_kills,
                    self.survivor_selected_stage
                )
                if action == "quit":
                    self.running = False
                elif action == "submit":
                    self.game_state = "survivor_game_over"
                elif action == "skip":
                    # ESC gedrückt - nicht speichern, direkt zu Game Over
                    self.game_state = "survivor_game_over"
                elif action == "maximize":
                    self.toggle_maximize()
                elif action == "fullscreen":
                    self.toggle_fullscreen()
            elif self.game_state == "survivor_game_over":
                # Menümusik läuft bereits von survivor_name_input
                action = self.survivor_game_over_screen.handle_and_draw(
                    self.screen, self._bg_scaled, self.survivor_time, self.survivor_kills,
                    self.survivor_selected_stage
                )
                if action == "quit":
                    self.running = False
                elif action == "retry":
                    self.game_state = "survivor_ship_select"
                    # Menümusik läuft weiter (kein Stop nötig)
                elif action == "menu":
                    if self._handle_menu_return():
                        return  # AppController übernimmt
                elif action == "maximize":
                    self.toggle_maximize()
                elif action == "fullscreen":
                    self.toggle_fullscreen()
            elif self.game_state == "normal_name_input":
                # Starte Menümusik wenn noch nicht gestartet (Spielmusik stoppen)
                if not self.menu.menu_music_playing:
                    try:
                        pygame.mixer.music.stop()
                    except pygame.error:
                        pass
                    self.menu.start_menu_music()

                # Verwende neuen unified GameOverScreen
                stats_dict = {
                    'Score': self.score,
                    'Kills': self._total_kills,
                    'Level': self.level
                }
                action = self.game_over_screen.handle_and_draw(
                    self.screen, self._bg_scaled, stats_dict, self.menu
                )
                if action == "quit":
                    self.running = False
                elif action == "submit":
                    # Score wurde gespeichert, zeige Top 10
                    self.came_from = 'game'
                    self.game_state = "normal_top10"
                elif action == "skip":
                    # ESC gedrückt - nicht speichern, zeige Top 10
                    self.came_from = 'game'
                    self.game_state = "normal_top10"
                elif action == "maximize":
                    self.toggle_maximize()
                elif action == "fullscreen":
                    self.toggle_fullscreen()
            elif self.game_state == "normal_top10":
                # Zeige Top 10 Liste - kombiniere lokale UND Online-Daten (EINMAL beim State-Wechsel)
                if not hasattr(self, '_normal_top10_loaded') or not self._normal_top10_loaded:
                    from system.utils import load_normal_top10

                    # Lade lokale Daten (immer verfügbar)
                    local_scores = load_normal_top10()
                    print(f"✓ Loaded {len(local_scores)} local highscores")

                    # Versuche Online-Daten zu holen (nur wenn zentral verfügbar)
                    online_scores = []
                    from system.firebase_manager import is_firebase_available, get_firebase_manager
                    if is_firebase_available():
                        manager = get_firebase_manager()
                        if manager:
                            try:
                                online_scores = manager.get_top_scores(stage=0, limit=100)  # Hole mehr, um zu vergleichen
                                print(f"✓ Loaded {len(online_scores)} online highscores from Firebase")
                            except Exception as e:
                                print(f"⚠ Failed to load online highscores: {e}")
                    else:
                        print(f"⚠ Firebase not available, using local scores only")

                    # Kombiniere beide Listen und entferne Duplikate
                    all_scores = []
                    seen = set()  # Track (name, score, kills) um Duplikate zu vermeiden

                    for score in local_scores + online_scores:
                        key = (score.get('name', ''), score.get('score', 0), score.get('kills', 0))
                        if key not in seen:
                            seen.add(key)
                            all_scores.append(score)

                    # Sortiere kombinierte Liste: Primär nach Score, Sekundär nach Kills
                    all_scores.sort(key=lambda x: (x.get('score', 0), x.get('kills', 0)), reverse=True)

                    # Nehme Top 10
                    self._normal_top10_data = all_scores[:10]
                    print(f"✓ Combined Top 10: {len(self._normal_top10_data)} unique entries (from {len(local_scores)} local + {len(online_scores)} online)")

                    self._normal_top10_loaded = True

                action = self.top10_normal_screen.handle_and_draw(
                    self.screen,
                    self._bg_scaled,
                    self._normal_top10_data,
                    self.menu,
                    came_from=self.came_from if self.came_from else 'menu'
                )
                if action == "quit":
                    self.running = False
                elif action == "retry":
                    self._normal_top10_loaded = False  # Reset für nächstes Mal
                    self.menu.stop_menu_music()  # Stoppe Menümusik
                    self.game_state = "playing"
                    self._start_game_mode()  # Starte Normal Mode neu
                elif action == "menu":
                    self._normal_top10_loaded = False # Reset für nächstes Mal
                    self.came_from            = None # Reset Navigation
                    if self._handle_menu_return():
                        return  # AppController übernimmt
                elif action == "maximize":
                    self.toggle_maximize()
                elif action == "fullscreen":
                    self.toggle_fullscreen()
            elif self.game_state == "survivor_highscores_view":
                # Survivor Mode Highscores ansehen
                from system.screens.survivor_screens import SurvivorGameOverScreen

                # Lade Top 10 für gewählte Stage (nur einmal)
                if not hasattr(self, '_survivor_highscores_loaded') or not self._survivor_highscores_loaded:
                    from system.utils import load_survivor_highscores
                    stage = getattr(self, '_survivor_highscore_stage', 1)
                    self._survivor_top10_data = load_survivor_highscores(stage)[:10]
                    self._survivor_highscores_loaded = True
                    # Leere Event-Queue beim ersten Laden, um versehentliche ENTER-Presses zu vermeiden
                    pygame.event.get()  # Hole alle Events ohne sie zu verarbeiten
                    self._survivor_view_just_opened = True  # Flag setzen
                    print(f"✓ Loaded {len(self._survivor_top10_data)} Survivor Mode highscores for Stage {stage}")

                # Übergebe Flag, ob View gerade erst geöffnet wurde
                just_opened = getattr(self, '_survivor_view_just_opened', False)

                # Zeige nur die Leaderboard-Liste mit neuem Screen
                action = self.top10_survivor_screen.handle_and_draw(
                    self.screen, self._bg_scaled,
                    self._survivor_top10_data,
                    getattr(self, '_survivor_highscore_stage', 1),
                    self.menu,
                    came_from=self.came_from if self.came_from else 'menu'
                )

                # Flag zurücksetzen nach erstem Frame
                if just_opened:
                    self._survivor_view_just_opened = False

                if action == "quit":
                    self.running = False
                elif action == "menu":
                    self._survivor_highscores_loaded = False
                    self.came_from  = None
                    self.game_state = "menu"
                    self.menu.set_pause_mode(False)
                    self.menu.set_survivor_stage_select(False)
                    self.menu.set_highscore_menu(True)

                elif action == "maximize":
                    self.toggle_maximize()
                elif action == "fullscreen":
                    self.toggle_fullscreen()
            elif self.game_state == "game_over":
                self.game_state = "menu"

            current_time = pygame.time.get_ticks()
            if not hasattr(self, '_last_stats_log'):
                self._last_stats_log = current_time
            elif current_time - self._last_stats_log >= 60000:
                self.explosion_manager.print_stats()
                self._last_stats_log = current_time

        self.explosion_manager.print_stats()
        # Nur pygame beenden wenn kein AppController (standalone Modus)
        if self.app_controller is None:
            pygame.quit()

    def _handle_menu(self):
        # Starte Menu-Musik wenn noch nicht gestartet
        if not self.menu.menu_music_playing:
            self.menu.start_menu_music()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False; return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # ESC im Hauptmenü: Spiel beenden
                    # ESC im Spielmodi-Menü: Zurück zum Hauptmenü
                    if self.menu.is_mode_select:
                        self.menu.set_mode_select(False)
                    else:
                        self.running = False
                    return
                elif event.key == pygame.K_F11:
                    self.toggle_maximize()
                elif event.key == pygame.K_RETURN and (pygame.key.get_pressed()[pygame.K_LALT] or pygame.key.get_pressed()[pygame.K_RALT]):
                    self.toggle_fullscreen()
                else:
                    action = self.menu.handle_input(event)
                    if action == "show_mode_select":
                        # Zeige Spielmodi-Auswahl
                        self.menu.set_mode_select(True)
                    elif action == "show_highscores":
                        # Zeige Highscore-Menü
                        self.menu.set_highscore_menu(True)
                    elif action == "show_normal_highscores":
                        # Zeige Normal Mode Top 10
                        self.game_state = "normal_top10"
                    elif action == "show_survivor_stage_select":
                        # Zeige Survivor Stage-Auswahl für Highscores
                        self.menu.set_survivor_stage_select(True)
                    elif action and action.startswith("show_survivor_highscores_"):
                        # Zeige Survivor Mode Top 10 für gewählte Stage
                        stage_num = int(action.split("_")[-1])
                        self._survivor_highscore_stage = stage_num
                        self.game_state = "survivor_highscores_view"
                    elif action == "back_to_menu":
                        # Zurück zum Hauptmenü - alle States richtig zurücksetzen
                        self.menu.reset_to_main_menu()
                    elif action == "back_to_highscore_menu":
                        # Zurück zum Highscore-Menü
                        self.menu.set_survivor_stage_select(False)
                        self.menu.set_highscore_menu(True)
                    elif action == "start_game":
                        self.menu.stop_menu_music()  # Stoppe Menu-Musik
                        self.game_state = "playing"
                        self.game_mode  = "normal"
                        self._start_new_game()
                    elif action == "start_survivor":
                        self.menu.stop_menu_music()  # Stoppe Menu-Musik
                        # Zeige Schiffsauswahl-Screen
                        self.game_mode  = "survivor"
                        self.game_state = "survivor_ship_select"
                        self.survivor_selected_stage = 1  # Standard: Stage 1
                    elif action == "quit_game":
                        self.running = False
        self.menu.draw(self.screen)
        pygame.display.flip()

    def _handle_pause_menu(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False; return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Pausenzeit aufsummieren
                    now = pygame.time.get_ticks()
                    self.total_pause_time += now - self.pause_start_time
                    self.game_state = "playing"
                    self.paused = False
                    try: pygame.mixer.music.unpause()
                    except pygame.error: pass
                    return
                elif event.key == pygame.K_F11:
                    self.toggle_maximize()
                elif event.key == pygame.K_RETURN and (pygame.key.get_pressed()[pygame.K_LALT] or pygame.key.get_pressed()[pygame.K_RALT]):
                    self.toggle_fullscreen()
                else:
                    action = self.menu.handle_input(event)
                    if action == "resume":
                        now = pygame.time.get_ticks()
                        self.total_pause_time += now - self.pause_start_time
                        self.game_state = "playing"
                        self.paused = False
                        try: pygame.mixer.music.unpause()
                        except pygame.error: pass
                    elif action == "quit_to_menu":
                        now = pygame.time.get_ticks()
                        self.total_pause_time += now - self.pause_start_time
                        self.paused = False
                        self.menu.set_pause_mode(False)

                        # Stoppe Spielmusik
                        try:
                            pygame.mixer.music.stop()
                        except pygame.error:
                            pass

                        # Wenn AppController verfügbar ist: zurück dorthin, sonst Original-Menu
                        if self.app_controller is not None:
                            print("🔄 Returning to AppController from pause menu")
                            self.running = False  # Beende Game-Loop
                            return
                        else:
                            # Fallback: Original Menu System
                            self.game_state = "menu"
                            self.menu.start_menu_music()
                            self._reset_game()
        self.menu.draw(self.screen)
        pygame.display.flip()

    def _start_new_game(self):
        self.paused = False
        self.score = 0
        self.lives = 3
        self.level = 1
        self.player_dead = False
        self._respawn_ready_at = 0

        cw, ch = self.screen.get_size()
        self.spawn_pos = (cw // 2, ch - 100)

        self.player = Player(cw, ch, self.assets)
        self.player.rect.center = self.spawn_pos

        self.enemies.clear()
        self.fly_in_enemies.clear()
        self.boss = None

        self.explosion_manager.clear_all()
        self.powerup_manager.clear_all()
        self.projectile_manager.clear_all()
        self._update_powerup_filter()

        # Reset Laufzeit-Status
        self.weapon_cooldowns.update({
            "rocket_last_used": 0,
            "homing_rocket_last_used": 0,
            "blaster_last_used": 0,
            "nuke_last_used": 0,
            "shield_ready_at": 0
        })
        self._total_kills        = 0
        self._boss_spawned       = False
        self._fly_in_spawn_count = 0
        self._last_fly_in_spawn  = pygame.time.get_ticks()

        # Wave/Level System initialisieren
        from config.levels import LEVEL_CONFIG
        self._current_wave       = 0
        self._wave_enemy_queue   = []
        self._wave_total_enemies = 0
        self._wave_kills         = 0
        self._all_waves_done     = False
        self._level_config       = LEVEL_CONFIG.get(self.level, None)
        if self._level_config:
            print(f">>> Level {self.level}: '{self._level_config['name']}' loaded ({len(self._level_config['waves'])} waves)")

        self.powerups.clear()
        self.double_laser_active = False
        self.speed_boost_active  = False
        self.powerup_shield      = None

        # Musik starten
        try:
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.set_volume(MASTER_VOLUME * MUSIC_VOLUME)
                pygame.mixer.music.play(-1)
        except pygame.error:
            pass

    def _add_player_shots(self, shots):
        """Fügt Spieler-Schüsse hinzu und wendet Damage-Multiplikator an"""
        if not shots:
            return
        for s in shots:
            if self._damage_multiplier != 1.0:
                s.dmg = int(s.dmg * self._damage_multiplier)
            self.projectile_manager.add_player_shot(s)

    def _update_powerup_filter(self):
        """Filtert PowerUp-Drops basierend auf Schiff-Waffen"""
        from config.ship import SHIP_CONFIG
        excluded = []
        stage = self.player.stage if hasattr(self.player, 'stage') else 1
        ship_cfg = SHIP_CONFIG.get(stage, {})
        weapons = ship_cfg.get("weapons", {})
        has_shield = ship_cfg.get("shield", 0) > 0

        # EMP/Nuke PowerUp nur wenn Schiff Nuke hat
        if weapons.get("nuke", 0) == 0:
            excluded.append("emp")

        # Shield PowerUp nur wenn Schiff Shield hat
        if not has_shield:
            excluded.append("shield")

        self.powerup_manager.set_excluded_types(excluded)
        if excluded:
            print(f"  PowerUp filter: excluded {excluded} for Stage {stage}")

    def _apply_upgrades(self, upgrades):
        """Wendet Upgrade-Levels auf den Spieler an"""
        from config.levels import UPGRADE_CONFIG

        # Ship Upgrade
        ship_upgrades = upgrades.get("next_ship", 0)
        if ship_upgrades > 0:
            new_stage = self.player.stage + ship_upgrades
            new_stage = min(new_stage, 4)
            self.player.set_stage(new_stage)
            self.player.current_health = self.player.max_health
            self._update_powerup_filter()
            print(f"  Ship upgraded to Stage {new_stage}")

        # Extra Life
        extra_lives = upgrades.get("extra_life", 0)
        if extra_lives > 0:
            self.lives += extra_lives
            print(f"  Extra lives: +{extra_lives} → {self.lives} lives")

        # Damage Multiplier
        damage_level = upgrades.get("damage", 0)
        if damage_level > 0:
            self._damage_multiplier = 1.0 + (UPGRADE_CONFIG["damage"]["effect"] * damage_level)
            print(f"  Damage multiplier: x{self._damage_multiplier:.1f}")

        # Fire Rate
        fire_rate_level = upgrades.get("fire_rate", 0)
        if fire_rate_level > 0:
            self._fire_rate_multiplier = 1.0 - (UPGRADE_CONFIG["fire_rate"]["effect"] * fire_rate_level)
            self._fire_rate_multiplier = max(0.3, self._fire_rate_multiplier)  # Min 30% cooldown
            print(f"  Fire rate multiplier: x{self._fire_rate_multiplier:.2f}")

        # EMP Charges
        emp_level = upgrades.get("emp_charges", 0)
        if emp_level > 0:
            charges = int(UPGRADE_CONFIG["emp_charges"]["effect"] * emp_level)
            if hasattr(self, 'emp_charges'):
                self.emp_charges += charges
            print(f"  EMP charges: +{charges}")

        # Shield Duration
        shield_level = upgrades.get("shield_duration", 0)
        if shield_level > 0:
            self._shield_duration_multiplier = 1.0 + (UPGRADE_CONFIG["shield_duration"]["effect"] * shield_level)
            print(f"  Shield duration multiplier: x{self._shield_duration_multiplier:.1f}")

    def _start_next_level(self):
        """Startet das nächste Level mit bestehenden Stats"""
        from config.levels import LEVEL_CONFIG
        self.level += 1
        self.game_state = "playing"

        # Reset Wave/Spawn State (aber behalte Score, Lives, Player)
        self.enemies.clear()
        self.fly_in_enemies.clear()
        self.explosion_manager.clear_all()
        self.projectile_manager.clear_all()
        self.powerup_manager.clear_all()
        self.powerups.clear()

        self._total_kills        = 0
        self._boss_spawned       = False
        self._fly_in_spawn_count = 0
        self._last_fly_in_spawn  = pygame.time.get_ticks()
        self._current_wave       = 0
        self._wave_enemy_queue   = []
        self._wave_total_enemies = 0
        self._wave_kills         = 0
        self._all_waves_done     = False

        self._level_config = LEVEL_CONFIG.get(self.level, None)
        if self._level_config:
            print(f">>> Level {self.level}: '{self._level_config['name']}' started ({len(self._level_config['waves'])} waves)")

    def _start_survivor_mode(self):
        """Starte Survivor Mode: 1 HP, kein Shield, Zeit-basiert"""
        self.paused = False
        self.score = 0
        self.lives = 1  # Nur 1 Leben
        self.level = 1
        self.player_dead = False
        self._respawn_ready_at = 0

        # Survivor Timer und Stats starten
        self.survivor_start_time = pygame.time.get_ticks()
        self.survivor_time = 0
        self.survivor_kills = 0
        self.survivor_player_name = ""
        self.survivor_time = 0

        # Lade den aktuellen Rekord für diese Stage
        from system.utils import load_survivor_highscores
        stage_highscores = load_survivor_highscores(self.survivor_selected_stage)
        if stage_highscores:
            self.survivor_best_time  = stage_highscores[0].get("time", 0)
            self.survivor_best_name  = stage_highscores[0].get("name", "---")
            self.survivor_best_kills = stage_highscores[0].get("kills", 0)
        else:
            self.survivor_best_time  = 0
            self.survivor_best_name  = "---"
            self.survivor_best_kills = 0

        cw, ch = self.screen.get_size()
        self.spawn_pos = (cw // 2, ch - 100)

        self.player = Player(cw, ch, self.assets)
        self.player.rect.center = self.spawn_pos

        # Setze ausgewählte Stage
        self.player.set_stage(self.survivor_selected_stage)

        # WICHTIG: Player auf 1 HP setzen (auch nach Stage-Wechsel)
        self.player.current_health = 1
        self.player.max_health = 1

        self.enemies.clear()
        self.fly_in_enemies.clear()
        self.boss = None

        self.explosion_manager.clear_all()
        self.powerup_manager.clear_all()
        self.projectile_manager.clear_all()
        self._update_powerup_filter()

        # Reset Laufzeit-Status
        self.weapon_cooldowns.update({
            "rocket_last_used": 0,
            "homing_rocket_last_used": 0,
            "blaster_last_used": 0,
            "nuke_last_used": 0,
            "shield_ready_at": 0
        })
        self._total_kills  = 0
        self._boss_spawned = False
        self._fly_in_spawn_count = 0
        self._last_fly_in_spawn = pygame.time.get_ticks()

        # Survivor Mode: Höheres Enemy-Limit für aggressive Spawns
        self._max_fly_in_enemies = 100  # Sehr hoch, damit Spawning nicht blockiert wird
        self._fly_in_spawn_interval = 2000  # Basis-Intervall (wird dynamisch überschrieben)

        self.powerups.clear()
        self.double_laser_active = False
        self.speed_boost_active  = False
        self.powerup_shield = None

        # WICHTIG: Kein Shield im Survivor Mode
        self.shield = None
        self.shield_until = 0

        # Musik starten
        try:
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.set_volume(MASTER_VOLUME * MUSIC_VOLUME)
                pygame.mixer.music.play(-1)
        except pygame.error:
            pass

    def _reset_game(self):
        self.paused = False
        self.score = 0
        self.kills = 0  # Normal Mode Kills zurücksetzen
        self.highscore = load_highscore()
        self.lives = 3
        self.level = 1
        self.player_dead = False
        self._respawn_ready_at = 0

        self.player = None
        self.enemies.clear()
        self.fly_in_enemies.clear()
        self.boss = None

        self.explosion_manager.clear_all()
        self.powerup_manager.clear_all()
        self.projectile_manager.clear_all()
        self._update_powerup_filter()

    def _start_game_mode(self):
        """Helper method to start the appropriate game mode"""
        if self.game_mode == "survivor":
            self._start_survivor_mode()
        else:
            self._start_new_game()

    def _update_shield_scale(self):
        if self.shield:
            base_frames = self.assets.get("shield_frames")
            base_scale_factor = self.assets.get("shield_scale")
            self.shield.rescale_for_player(self.player.rect, base_frames, base_scale_factor)
        if self.powerup_shield:
            base_frames = self.assets.get("shield_frames")
            base_scale_factor = self.assets.get("shield_scale")
            self.powerup_shield.rescale_for_player(self.player.rect, base_frames, base_scale_factor)

    def _handle_menu_return(self):
        """Hilfsfunktion: Kehre zum AppController oder Original Menu zurück"""
        if self.app_controller is not None:
            print("🔄 Returning to AppController from game")
            # Stoppe Musik
            try:
                pygame.mixer.music.stop()
            except pygame.error:
                pass
            self.running = False  # Beende Game-Loop, AppController übernimmt
            return True
        else:
            # Fallback: Original Menu System
            self.game_state = "menu"
            self.game_mode = "normal"
            self.paused = False
            self.menu.set_pause_mode(False)
            # Stoppe Spielmusik und starte Menümusik
            try:
                pygame.mixer.music.stop()
            except pygame.error:
                pass
            self.menu.start_menu_music()
            self._reset_game()
            return False
