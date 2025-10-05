import pygame
from assets.load_assets import load_assets
from utils              import load_highscore, save_highscore
from config             import *
from entities           import *

class Game:
    def __init__(self):
        pygame.init()
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

        self.player = Player(WIDTH, HEIGHT, self.assets)
        self.player.rect.center = self.spawn_pos  


        if "music_paths" in self.assets and "raining_bits" in self.assets["music_paths"]:
            try:
                pygame.mixer.music.load(self.assets["music_paths"]["raining_bits"])
                pygame.mixer.music.set_volume(0.1)
                pygame.mixer.music.play(-1)
            except pygame.error:
                pass

        # self._build_wave("alien")

    # ---------------- Wellen ----------------
    def _build_wave(self, enemy_type: str):
        self.enemies.clear()
        form = ENEMY_CONFIG[enemy_type]["formation"]
        for r in range(form["rows"]):
            for c in range(form["cols"]):
                x = c * form["h_spacing"] + form["margin_x"]
                y = r * form["v_spacing"] + form["margin_y"]
                self.enemies.append(Enemy(enemy_type, self.assets, x, y))
        base = ENEMY_CONFIG[enemy_type]["move"]["speed_start"]
        self.enemy_speed = base + max(0, self.wave_num)
        self.enemy_dir = 1
        self.wave_num += 1

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
                elif e.key == pygame.K_2:
                    self.player.set_stage(2)
                elif e.key == pygame.K_3:
                    self.player.set_stage(3)
                elif e.key == pygame.K_4:
                    self.player.set_stage(4)
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
                    self.player_shots.extend(self.player.shoot_weapon("rocket"))
                elif e.key == pygame.K_e and not self.paused and not self.player_dead:
                    self.player_shots.extend(self.player.shoot_weapon("nuke"))

                elif e.key == pygame.K_q and not self.paused and not self.player_dead:
                    if self.shield:
                        self.shield = None
                        break
                    now = pygame.time.get_ticks()
                    if now >= self._shield_ready_at:
                        frames = self.assets["shield_frames"]
                        fps    = self.assets["shield_fps"]

                        scale = max(self.player.rect.w, self.player.rect.h) / frames[0].get_width() * self.assets["shield_scale"]
                        self.shield = Shield( *self.player.rect.center, frames, fps=fps, scale=scale, loop=True )
                        self.shield_until     = now + self.assets["shield_duration"]
                        self._shield_ready_at = now + self.assets["shield_cooldown"]



    # ---------------- Update ----------------
    def _update(self):
        keys = pygame.key.get_pressed()
        now  = pygame.time.get_ticks()

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
            p.update()
            if p.offscreen():
                self.player_shots.remove(p)
        for p in self.enemy_shots[:]:
            p.update()
            if p.offscreen():
                self.enemy_shots.remove(p)

        for e in self.enemies[:]:
            if e.offscreen():
                e.remove()

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


        # ---- Kollision: Gegner-Projektil -> Spieler ----
        if not self.player_dead and not self.shield:
            for p in self.enemy_shots[:]:
                # Schild fängt ab
                if self.shield and self.shield.hit_circle(p.rect.center):
                    self.enemy_shots.remove(p)
                    continue

                if p.rect.colliderect(self.player.rect):
                    # Unverwundbarkeit nach Respawn beachten
                    if now < getattr(self.player, "invincible_until", 0):
                        self.enemy_shots.remove(p)
                        continue

                    self.enemy_shots.remove(p)
                    if hasattr(p, "on_hit"): p.on_hit(self, self.player.rect.center)

                    frames = self.assets.get("expl_laser", [])
                    fps    = self.assets.get("expl_laser_fps", 24)
                    self.explosions.append(Explosion(self.player.rect.centerx,
                                                    self.player.rect.centery,
                                                    frames, fps=fps, scale=2.5))

                    self.player_dead       = True
                    self._respawn_ready_at = now + self.lives_cooldown
                    # self._build_wave("alien")  # falls gewollt, sonst entfernen
                    break


        # Kollision: Spieler-Projektile -> Gegner
        for p in self.player_shots[:]:
            hit_enemy = None
            for en in self.enemies:
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
            if hit_enemy not in self.enemies:
                continue

            # Direkt-Schaden anwenden und ggf. entfernen
            dead = hit_enemy.take_damage(getattr(p, "dmg", 10))
            if dead:
                self.score += hit_enemy.points
                self.highscore = max(self.highscore, self.score)
                frames = self.assets.get("expl_rocket", []) or self.assets.get("expl_laser", [])
                fps    = self.assets.get("expl_rocket_fps", 24)
                self.explosions.append(Explosion(hit_enemy.rect.centerx,
                                                hit_enemy.rect.centery,
                                                frames, fps=fps, scale=1.2))
                # Entfernen nur, wenn noch vorhanden
                if hit_enemy in self.enemies:
                    self.enemies.remove(hit_enemy)


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
        for ex in self.explosions:  ex.draw(self.screen)

        if not self.player_dead:
            self.player.draw(self.screen)
            if self.shield:
                self.shield.draw(self.screen)

        self.screen.blit(self.font.render(f"Score: {self.score}", True, (255,255,255)), (10, 10))
        self.screen.blit(self.font.render(f"High Score: {self.highscore}", True, (255,255,255)), (10, 50))
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
