import pygame
import random
from assets.load_assets import load_assets
from system.utils       import load_highscore, save_highscore, scale
from system.hud         import HUD
from system.health_bar  import HealthBar
from config             import *
from config.powerup     import POWERUP_CONFIG
from config.shield      import SHIELD_CONFIG
from entities           import *
from manager import ExplosionManager, PowerUpManager, ProjectileManager
from system.menu import GameMenu

class Game:
    def __init__(self):
        pygame.init()

        # Pygame Setup (optional: vsync wenn verfügbar)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))  # , pygame.SCALED, vsync=1
        pygame.display.set_caption("Space Invaders")
        self.clock = pygame.time.Clock()

        # Game State
        self.running    = True
        self.paused     = False
        self.game_state = "menu"
        self.score      = 0
        self.highscore  = load_highscore()
        self.lives      = LIVES

        # Display-Modi
        self.is_fullscreen = False
        self.is_maximized  = False
        self.original_size = (WIDTH, HEIGHT)
        self.aspect_ratio  = 16 / 9

        # Assets
        self.assets = load_assets()
        self.font   = pygame.font.Font(None, FONT_SIZE)
        self._bg_scaled = self.assets.get("background_img")  # wird in _reinitialize_ui() skaliert

        # Menü
        self.menu = GameMenu()
        self.menu.load_assets(self.assets)
        self.menu.set_pause_mode(False)

        # Audio
        pygame.mixer.set_num_channels(32)
        self.shield_channel = pygame.mixer.Channel(30)
        self.music_channel  = pygame.mixer.Channel(31)
        # Musik einmal laden
        if "music_paths" in self.assets and "raining_bits" in self.assets["music_paths"]:
            try:
                pygame.mixer.music.load(self.assets["music_paths"]["raining_bits"])
            except pygame.error:
                pass

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
        if self._total_kills < 50:
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
        self.powerup_manager.queue_drop_check(x, y)

    def _update_powerups(self):
        # PowerUpManager Update (verarbeitet Queue und updatet PowerUps)
        dt = self.clock.get_time() / 1000.0
        self.powerup_manager.update(dt, HEIGHT)
        
        # Kollisionserkennung mit Player
        for powerup in self.powerup_manager.powerups[:]:
            if powerup.rect.colliderect(self.player.rect):
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
        now = self.get_game_time()
        frames = self.assets["shield_frames"]
        fps = shield_config.get("fps", 20)
        scale_f = max(self.player.rect.w, self.player.rect.h) / frames[0].get_width() * self.assets["shield_scale"]
        self.powerup_shield = Shield(
            *self.player.rect.center, frames, fps=fps, scale=scale_f,
            loop=True, player_health=self.player.max_health, is_powerup_shield=True,
            shield_config=shield_config
        )
        self.powerup_shield_until = now + duration

    def _activate_double_laser(self, duration):
        now = self.get_game_time()
        self.double_laser_active = True
        self.double_laser_until = now + duration

    def _activate_speed_boost(self, duration, multiplier):
        now = self.get_game_time()
        if self.original_player_speed is None:
            self.original_player_speed = self.player.speed
        self.speed_boost_active = True
        self.speed_boost_until = now + duration
        self.speed_boost_multiplier = multiplier
        self.player.speed = self.original_player_speed * multiplier

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
        for enemy in self.enemies[:]:
            if getattr(enemy, 'movement_type', None) == "fly_in":
                enemy.update()
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

    def _spawn_fly_in_enemy(self):
        if self._fly_in_spawn_count >= self._max_fly_in_enemies: return
        spawn_x = random.randint(50, WIDTH - 50)
        spawn_y = -50
        path = random.choice(["straight", "straight", "sine", "sine", "circle"])
        enemy_type = random.choice(["alien", "drone", "tank", "sniper"])
        enemy = Enemy(enemy_type, self.assets, spawn_x, spawn_y)
        enemy.wave_id = f"fly_in_{self._fly_in_spawn_count}"
        enemy.movement_type = "fly_in"
        enemy.move_cfg = enemy.move_cfg.copy()
        enemy.move_cfg["type"] = "fly_in"
        enemy.move_cfg["path"] = path
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

    def _spawn_boss_group(self):
        for _ in range(2):
            spawn_x = random.randint(100, WIDTH - 100)
            spawn_y = -80
            boss = Enemy("boss", self.assets, spawn_x, spawn_y)
            boss.move_cfg = boss.move_cfg.copy()
            boss.move_cfg["type"] = "fly_in"
            boss.move_cfg["target_y"] = random.randint(100, 140)
            boss.move_cfg["path"] = "sine"
            boss.move_cfg["speed"] = 1.5
            boss.move_cfg["amplitude"] = 30
            boss.move_cfg["frequency"] = 0.5
            self.fly_in_enemies.append(boss)
            self._fly_in_spawn_count += 1
        self._boss_spawned = True
        self._max_fly_in_enemies = len(self.fly_in_enemies)

    def _update_fly_in_spawning(self):
        now = pygame.time.get_ticks()
        if self._total_kills >= 50 and not self._boss_spawned and len(self.fly_in_enemies) == 0:
            self._spawn_boss_group()
            return
        if self._total_kills >= 50:
            return
        if (now - self._last_fly_in_spawn > self._fly_in_spawn_interval and
            self._fly_in_spawn_count < self._max_fly_in_enemies):
            group_size = random.randint(2, 4)
            for _ in range(group_size):
                if self._fly_in_spawn_count < self._max_fly_in_enemies:
                    self._spawn_fly_in_enemy()
            self._last_fly_in_spawn = now
            self._fly_in_spawn_interval = random.randint(4000, 6000)

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
                elif e.key == pygame.K_2:
                    self.player.set_stage(2); self._update_shield_scale()
                elif e.key == pygame.K_3:
                    self.player.set_stage(3); self._update_shield_scale()
                elif e.key == pygame.K_4:
                    self.player.set_stage(4); self._update_shield_scale()
                elif e.key == pygame.K_F1:
                    self._build_wave('alien')
                elif e.key == pygame.K_F2:
                    self._build_wave('drone')
                elif e.key == pygame.K_F3:
                    self._build_wave('tank')
                elif e.key == pygame.K_F4:
                    self._build_wave('sniper')
                elif e.key == pygame.K_F5:
                    self._build_wave('boss')
                elif e.key == pygame.K_F12 and not (pygame.key.get_pressed()[pygame.K_LALT] or pygame.key.get_pressed()[pygame.K_RALT]):
                    self.enemies = []
                elif e.key == pygame.K_SPACE and not self.paused and not self.player_dead:
                    shots = self.player.shoot_weapon("laser")
                    if self.double_laser_active and shots:
                        enhanced = []
                        for shot in shots:
                            ds = DoubleLaser.create(shot.rect.centerx, shot.rect.centery, self.assets, owner="player", angle_deg=0)
                            enhanced.append(ds)
                        for s in enhanced: self.projectile_manager.add_player_shot(s)
                    else:
                        for s in shots: self.projectile_manager.add_player_shot(s)
                elif e.key == pygame.K_r and not self.paused and not self.player_dead:
                    shots = self.player.shoot_weapon("rocket")
                    if shots:
                        for s in shots: self.projectile_manager.add_player_shot(s)
                        self.weapon_cooldowns["rocket_last_used"] = pygame.time.get_ticks()
                elif e.key == pygame.K_t and not self.paused and not self.player_dead:
                    shots = self.player.shoot_weapon("homing_rocket")
                    if shots:
                        for s in shots: self.projectile_manager.add_player_shot(s)
                        self.weapon_cooldowns["homing_rocket_last_used"] = pygame.time.get_ticks()
                elif e.key == pygame.K_b and not self.paused and not self.player_dead:
                    shots = self.player.shoot_weapon("blaster")
                    if shots:
                        for s in shots: self.projectile_manager.add_player_shot(s)
                        self.weapon_cooldowns["blaster_last_used"] = pygame.time.get_ticks()
                elif e.key == pygame.K_e and not self.paused and not self.player_dead:
                    shots = self.player.shoot_weapon("nuke")
                    if shots:
                        for s in shots: self.projectile_manager.add_player_shot(s)
                        self.weapon_cooldowns["nuke_last_used"] = pygame.time.get_ticks()
                elif e.key == pygame.K_q and not self.paused and not self.player_dead:
                    from config.ship import SHIP_CONFIG
                    has_shield = SHIP_CONFIG.get(self.player.stage, {}).get("shield", 0) == 1
                    if not has_shield: break
                    if self.shield:
                        self.shield = None
                        break
                    now = pygame.time.get_ticks()
                    if now >= self._shield_ready_at:
                        frames = self.assets["shield_frames"]
                        fps    = self.assets["shield_fps"]
                        scale_f = max(self.player.rect.w, self.player.rect.h) / frames[0].get_width() * self.assets["shield_scale"]
                        new_shield = Shield(*self.player.rect.center, frames, fps=fps, scale=scale_f, loop=True, player_health=self.player.max_health)
                        shield_cfg = SHIELD_CONFIG[1]["shield"]
                        regen_rate = shield_cfg.get("regen_rate", 0.2)
                        min_health = int(new_shield.max_health * shield_cfg.get("min_health_percentage", 0.3))
                        time_since_last = max(0, now - getattr(self, '_last_shield_destroyed', 0))
                        health_regen = min(new_shield.max_health, new_shield.max_health * regen_rate * (time_since_last/1000.0))
                        new_shield.current_health = max(min_health, int(health_regen))
                        self.shield = new_shield
                        self.shield_until     = now + self.assets["shield_duration"]
                        self._shield_ready_at = now + self.assets["shield_cooldown"]
                        if self.assets.get("shield_activate_sound"):
                            self.assets["shield_activate_sound"].set_volume(MASTER_VOLUME * SFX_VOLUME)
                            self.assets["shield_activate_sound"].play()

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

        if not self.player_dead:
            self.health_bar.update(self.player.get_health_percentage())

        if self.player_dead:
            if (self.lives == -1 or self.lives > 0) and now >= self._respawn_ready_at:
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
                for s in enhanced: self.projectile_manager.add_player_shot(s)
            else:
                for s in shots: self.projectile_manager.add_player_shot(s)

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

        for enemy in self.fly_in_enemies[:]:
            enemy.update()
            if hasattr(enemy, 'update_emp_effects'): enemy.update_emp_effects(dt)
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
            if hasattr(p, "on_hit"):
                p.on_hit(self, hit_enemy.rect.center)
                self.explosion_manager.log_weapon_explosion(p.__class__.__name__)
            self.projectile_manager.remove_shot(p)
            if hit_enemy not in self.enemies and hit_enemy not in self.fly_in_enemies:
                continue
            dead = hit_enemy.take_damage(getattr(p, "dmg", 10))
            if dead:
                self.explosion_manager.register_enemy_death(p.__class__.__name__)
                self.score += hit_enemy.points
                self.highscore = max(self.highscore, self.score)
                self._total_kills += 1
                self._show_kill_counter()
                self._try_drop_powerup(hit_enemy.rect.centerx, hit_enemy.rect.centery)
                wtype = getattr(p, "weapon_type", "default")
                if wtype in ("nuke", "rocket", "homing_rocket"):
                    frames = self.assets.get("expl_rocket", [])
                    fps = self.assets.get("expl_rocket_fps", 30 if wtype=="nuke" else 28)
                    scale_e = 5.0 if wtype=="nuke" else 3.5
                else:
                    frames = self.assets.get("expl_laser", [])
                    fps    = self.assets.get("expl_laser_fps", 26)
                    scale_e = 2.0
                self.explosion_manager.add_explosion(hit_enemy.rect.centerx, hit_enemy.rect.centery, frames, fps=fps, scale=scale_e)
                if hit_enemy in self.enemies:
                    self.enemies.remove(hit_enemy)
                elif hit_enemy in self.fly_in_enemies:
                    self.fly_in_enemies.remove(hit_enemy)
                    self._fly_in_spawn_count = max(0, self._fly_in_spawn_count - 1)

        self.explosion_manager.update()

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
        self.screen.blit(self.font.render(f"Score: {self.score}", True, (255,255,255)), (score_x, score_y))
        self.screen.blit(self.font.render(f"High Score: {self.highscore}", True, (255,255,255)), (score_x, highscore_y))

        current_time = pygame.time.get_ticks()
        if self.kill_display_timer > 0 and current_time - self.kill_display_timer < self.kill_display_duration:
            kill_surface = self.font.render(self.kill_display_text, True, (255, 255, 0))
            kill_rect = kill_surface.get_rect(center=(cw // 2, int(100 * ui_scale)))
            self.screen.blit(kill_surface, kill_rect)

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
        pygame.display.flip()

    def kill_player(self):
        if self.player_dead: return
        self.player_dead = True
        self._respawn_ready_at = pygame.time.get_ticks() + self.lives_cooldown

    def _respawn(self):
        if self.lives > 0:
            self.lives -= 1
        cw, ch = self.screen.get_size()
        self.player = Player(cw, ch, self.assets)
        self.player.rect.center = self.spawn_pos
        self.player_dead = False
        self._respawn_ready_at = 0

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
            elif self.game_state == "game_over":
                self.game_state = "menu"

            current_time = pygame.time.get_ticks()
            if not hasattr(self, '_last_stats_log'):
                self._last_stats_log = current_time
            elif current_time - self._last_stats_log >= 60000:
                self.explosion_manager.print_stats()
                self._last_stats_log = current_time

        self.explosion_manager.print_stats()
        save_highscore(self.highscore)
        pygame.quit()

    def _handle_menu(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False; return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False; return
                elif event.key == pygame.K_F11:
                    self.toggle_maximize()
                elif event.key == pygame.K_RETURN and (pygame.key.get_pressed()[pygame.K_LALT] or pygame.key.get_pressed()[pygame.K_RALT]):
                    self.toggle_fullscreen()
                else:
                    action = self.menu.handle_input(event)
                    if action == "start_game":
                        self.game_state = "playing"
                        self._start_new_game()
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
                        self.game_state = "menu"
                        self.paused = False
                        self.menu.set_pause_mode(False)
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
        self.powerups.clear()
        self.double_laser_active = False
        self.speed_boost_active  = False
        self.powerup_shield = None

    def _reset_game(self):
        self.paused = False
        self.score = 0
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

    def _update_shield_scale(self):
        if self.shield:
            base_frames = self.assets["shield_frames"]
            base_scale_factor = self.assets["shield_scale"]
            self.shield.rescale_for_player(self.player.rect, base_frames, base_scale_factor)
        if self.powerup_shield:
            base_frames = self.assets["shield_frames"]
            base_scale_factor = self.assets["shield_scale"]
            self.powerup_shield.rescale_for_player(self.player.rect, base_frames, base_scale_factor)
