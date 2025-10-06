import pygame
from assets.load_assets import load_assets
from system.utils       import load_highscore, save_highscore
from system.hud         import HUD
from system.health_bar  import HealthBar
from config             import *
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

        self.assets = load_assets()

        self.player_shots = []
        self.enemy_shots  = []
        self.enemies      = []
        self.explosions   = []

        self.enemy_dir   = 1
        self.enemy_speed = 0.0
        self.wave_num    = 0

        self.score              = 0
        self.highscore          = load_highscore()
        self.paused             = False
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

        self.player = Player(WIDTH, HEIGHT, self.assets)
        self.player.rect.center = self.spawn_pos

        # HUD initialisieren
        self.hud = HUD(WIDTH, HEIGHT)
        self.hud.load_icons(self.assets)

        # Health Bar initialisieren (oben links)
        self.health_bar = HealthBar(10, 100, 200, 20)
        # Schild Health Bar (oben links, unter Player Health)
        self.shield_health_bar = HealthBar(10, 140, 200, 15)

        if "music_paths" in self.assets and "raining_bits" in self.assets["music_paths"]:
            try:
                pygame.mixer.music.load(self.assets["music_paths"]["raining_bits"])
                pygame.mixer.music.set_volume(MASTER_VOLUME * MUSIC_VOLUME)
                pygame.mixer.music.play(-1)
            except pygame.error:
                pass

        # self._build_wave("alien")

    # ---------------- Wellen ----------------
    def _build_wave(self, enemy_type: str):
        # self.enemies.clear()
        form = ENEMY_CONFIG[enemy_type]["formation"]
        for r in range(form["rows"]):
            for c in range(form["cols"]):
                x = c * form["h_spacing"] + form["margin_x"]
                y = r * form["v_spacing"] + form["margin_y"]
                self.enemies.append(Enemy(enemy_type, self.assets, x, y))
        base = ENEMY_CONFIG[enemy_type]["move"]["speed_start"]
        self.enemy_speed = base
        self.enemy_dir = 1
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

    # ---------------- Events ----------------
    def _handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.paused = not self.paused
                    try:
                        pygame.mixer.music.pause() if self.paused else pygame.mixer.music.unpause()
                    except pygame.error:
                        pass
                elif e.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
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
                elif e.key == pygame.K_F12:
                    self.enemies = []

                elif e.key == pygame.K_SPACE and not self.paused and not self.player_dead:
                    self.player_shots.extend(self.player.shoot_weapon("laser"))
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

        # Health Bar aktualisieren
        if not self.player_dead:
            self.health_bar.update(self.player.get_health_percentage())

        # während tot: kein Input, keine Kollisionen
        if self.player_dead:
            if (self.lives == -1 or self.lives > 0) and now >= self._respawn_ready_at:
                self._respawn()

        if not self.player_dead:
            self.player.handle_input(keys, WIDTH, HEIGHT)

        if keys[pygame.K_SPACE] and not self.paused and not self.player_dead:
            self.player_shots.extend(self.player.shoot_weapon("laser"))

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

        if self.shield:
            self.shield.set_center(self.player.rect.center)
            self.shield.update()
            if pygame.time.get_ticks() >= self.shield_until or self.shield.done:
                self.shield = None

        # Gegner bewegen + droppen am Rand
        if self.enemies:
            dx = self.enemy_dir * max(1, int(self.enemy_speed))
            left  = min(en.rect.left  for en in self.enemies)
            right = max(en.rect.right for en in self.enemies)
            move_cfg = self.enemies[0].cfg["move"]
            if (self.enemy_dir == 1 and right + dx >= WIDTH) or (self.enemy_dir == -1 and left - dx <= 0):
                self.enemy_dir *= -1
                for en in self.enemies: en.drop(move_cfg["drop_px"])
            else:
                for en in self.enemies: en.update(dx)

            # Gegner feuern: nur shoot_weapon
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
                if self.shield and not self.shield.is_broken() and self.shield.hit_by_projectile(p.rect):
                    # Schild nimmt Schaden
                    damage = getattr(p, "dmg", 100)
                    shield_still_active = self.shield.take_damage(damage)

                    self.shield.play_hit_sound(self.assets)
                    hit_shield = True

                    # Wenn Schild zerstört wird, entferne es
                    if not shield_still_active:
                        self._last_shield_destroyed = now  # Zeitpunkt der Zerstörung tracken
                        self.shield = None

                if p.rect.colliderect(self.player.rect):
                    # Unverwundbarkeit nach Respawn beachten
                    if now < getattr(self.player, "invincible_until", 0):
                        self.enemy_shots.remove(p)
                        continue

                    self.enemy_shots.remove(p)

                    # Schaden berechnen (verschiedene Projektile machen unterschiedlich viel Schaden)
                    damage = getattr(p, "dmg", 100)  # Standard-Schaden 100

                    # Schild-Schutz: Reduzierter Schaden wenn Schild aktiv ist (auch wenn es getroffen wurde)
                    has_shield = hit_shield or (self.shield is not None and not self.shield.is_broken())
                    player_destroyed = self.player.take_damage(damage, has_shield)

                    if hasattr(p, "on_hit"):
                        p.on_hit(self, self.player.rect.center)

                    # Explosion nur bei Zerstörung
                    if player_destroyed:
                        frames = self.assets.get("expl_laser", [])
                        fps    = self.assets.get("expl_laser_fps", 24)
                        self.explosions.append(Explosion(self.player.rect.centerx,
                                                        self.player.rect.centery,
                                                        frames, fps=fps, scale=2.5))

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

                frames = self.assets.get("expl_rocket", []) or self.assets.get("expl_laser", [])
                fps    = self.assets.get("expl_rocket_fps", 24)
                self.explosions.append(Explosion(hit_enemy.rect.centerx,
                                                hit_enemy.rect.centery,
                                                frames, fps=fps, scale=1.2))
                # Entfernen nur, wenn noch vorhanden
                if hit_enemy in self.enemies:
                    self.enemies.remove(hit_enemy)
                elif hit_enemy in self.fly_in_enemies:
                    self.fly_in_enemies.remove(hit_enemy)
                    self._fly_in_spawn_count = max(0, self._fly_in_spawn_count - 1)  # Count dekrementieren


        # Explosionen updaten
        for ex in self.explosions[:]:
            ex.update()
            if ex.done: self.explosions.remove(ex)

        # Welle fertig -> neue bauen
        # if not self.enemies and not self.player_dead:
            # self._build_wave("alien")

    # ---------------- Draw ----------------
    def _draw(self):
        bg = self.assets.get("background_img")
        self.screen.blit(bg, (0, 0)) if bg else self.screen.fill((0, 0, 0))

        for p in self.player_shots: p.draw(self.screen)
        for p in self.enemy_shots:  p.draw(self.screen)
        for en in self.enemies:     en.draw(self.screen)
        for en in self.fly_in_enemies: en.draw(self.screen)  # Fly-In Enemies zeichnen
        for ex in self.explosions:  ex.draw(self.screen)

        if not self.player_dead:
            self.player.draw(self.screen)
            if self.shield:
                self.shield.draw(self.screen)

        self.screen.blit(self.font.render(f"Score: {self.score}", True, (255,255,255)), (10, 10))
        self.screen.blit(self.font.render(f"High Score: {self.highscore}", True, (255,255,255)), (10, 50))

        # Kill-Counter anzeigen
        if self._total_kills < 50:
            kill_text = f"Kills: {self._total_kills}/50"
        elif self._boss_spawned:
            kill_text = "BOSS BATTLE!"
        elif len(self.fly_in_enemies) > 0:
            kill_text = f"Clear remaining enemies ({len(self.fly_in_enemies)} left)"
        else:
            kill_text = "Boss incoming..."
        self.screen.blit(self.font.render(kill_text, True, (255,255,0)), (WIDTH - 200, 10))

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

        # Player neu erzeugen mit deinen Parametern
        self.player = Player(WIDTH, HEIGHT, self.assets)
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
