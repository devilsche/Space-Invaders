# game/game.py
import pygame
import random

from assets.load_assets import load_assets
from config import WIDTH, HEIGHT, FPS, FONT_SIZE, ENEMY_CONFIG
from entities import Player, Enemy, Explosion
from utils import load_highscore, save_highscore


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Space Invaders")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, FONT_SIZE)

        self.assets = load_assets()
        self.player = Player(WIDTH, HEIGHT, self.assets)

        self.player_shots = []
        self.enemy_shots = []
        self.enemies = []
        self.explosions = []

        self.enemy_dir = 1
        self.enemy_speed = 0

        self.score = 0
        self.highscore = load_highscore()
        self.paused = False
        self.running = True
        self.player_dead = False

        self.wave_num = 0              # 0 = erste Welle
        self.wave_speed_add = 0.5      # Zuwachs pro Welle


        if "music_paths" in self.assets and "raining_bits" in self.assets["music_paths"]:
            try:
                pygame.mixer.music.load(self.assets["music_paths"]["raining_bits"])
                pygame.mixer.music.set_volume(0.3)
                pygame.mixer.music.play(-1)
            except pygame.error:
                pass

        # self._build_wave("alien")

    def _build_wave(self, enemy_type: str):
        self.enemies.clear()

        form = ENEMY_CONFIG[enemy_type]["formation"]
        for r in range(form["rows"]):
            for c in range(form["cols"]):
                x = c * form["h_spacing"] + form["margin_x"]
                y = r * form["v_spacing"] + form["margin_y"]
                self.enemies.append(Enemy(enemy_type, self.assets, x, y))

        # Basisgeschwindigkeit aus Config
        base = ENEMY_CONFIG[enemy_type]["move"]["speed_start"]
        # Wellenzuwachs: erste Welle unverändert, danach +wave_speed_add je Welle
        self.enemy_speed = base + max(0, self.wave_num) * self.wave_speed_add

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
                        if self.paused: pygame.mixer.music.pause()
                        else:           pygame.mixer.music.unpause()
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
                elif e.key == pygame.K_SPACE and not self.paused and not self.player_dead:
                    self.player_shots.extend(self.player.shoot_weapon("laser"))
                elif e.key == pygame.K_r and not self.paused and not self.player_dead:
                    self.player_shots.extend(self.player.shoot_weapon("rocket"))
                elif e.key == pygame.K_n and not self.paused and not self.player_dead:
                    self.player_shots.extend(self.player.shoot_weapon("nuke"))
                elif e.key == pygame.K_F1:
                    self._build_wave("alien")
                elif e.key == pygame.K_F2:
                    self._build_wave("drone")
                elif e.key == pygame.K_F3:
                    self._build_wave("tank")
                elif e.key == pygame.K_F4:
                    self._build_wave("sniper")
                elif e.key == pygame.K_F5:
                    self._build_wave("boss")


    # ---------------- Update ----------------
    def _update(self):
        keys = pygame.key.get_pressed()
        if not self.player_dead:
            self.player.handle_input(keys, WIDTH, HEIGHT)

        # Projektile bewegen
        for p in self.player_shots[:]:
            p.update()
            if p.offscreen():
                self.player_shots.remove(p)
        for p in self.enemy_shots[:]:
            p.update()
            if p.offscreen():
                self.enemy_shots.remove(p)

        # Gegner bewegen mit Drop am Rand
        if self.enemies:
            move_cfg = self.enemies[0].cfg["move"]
            dx = self.enemy_dir * max(1, move_cfg["speed_start"])

            left = min(en.rect.left for en in self.enemies)
            right = max(en.rect.right for en in self.enemies)

            hit_right = (self.enemy_dir == 1) and (right + dx >= WIDTH)
            hit_left  = (self.enemy_dir == -1) and (left  - dx <= 0)

            if hit_right or hit_left:
                self.enemy_dir *= -1
                drop = move_cfg["drop_px"]
                for en in self.enemies:
                    en.drop(drop)
            else:
                for en in self.enemies:
                    en.update(dx)

            # Gegner feuern
            for en in self.enemies:
                shots = en.shoot()
                if shots:
                    self.enemy_shots.extend(shots)

        # Kollision: Gegner-Projektile -> Spieler
        if not self.player_dead:
            for p in self.enemy_shots[:]:
                if p.rect.colliderect(self.player.rect):
                    self.enemy_shots.remove(p)
                    if hasattr(p, "on_hit"):
                        p.on_hit(self, self.player.rect.center)
                    # Spieler-Explosion
                    frames = self.assets.get("explosion_frames", [])
                    self.explosions.append(Explosion(self.player.rect.centerx, self.player.rect.centery, frames, fps=24, scale=3.0))
                    self.player_dead = True
                    self.running = False
                    break


        # Kollision: Spieler-Projektile -> Gegner
        for p in self.player_shots[:]:
            # erst Treffer suchen
            hit_idx = -1
            for i, en in enumerate(self.enemies):
                if p.rect.colliderect(en.rect):
                    hit_idx = i
                    break
            if hit_idx == -1:
                continue

            hit_enemy = self.enemies[hit_idx]
            self.player_shots.remove(p)

            # AoE/SFX vom Projektil (kann Gegner bereits aus self.enemies löschen)
            if hasattr(p, "on_hit"):
                p.on_hit(self, hit_enemy.rect.center)

            # Nur wenn er noch existiert, Direktschaden anwenden und ggf. entfernen
            if hit_enemy in self.enemies:
                direct = getattr(p, "dmg", 10) if getattr(p, "radius", 0) == 0 else 0
                dead = hit_enemy.take_damage(direct)
                if dead:
                    self.score += hit_enemy.points
                    self.highscore = max(self.highscore, self.score)
                    frames = self.assets.get("explosion_frames", [])
                    self.explosions.append(Explosion(hit_enemy.rect.centerx,
                                                    hit_enemy.rect.centery,
                                                    frames, fps=24, scale=1.2))
                    self.enemies.pop(hit_idx)


        # Explosionen updaten
        for ex in self.explosions[:]:
            ex.update()
            if ex.done:
                self.explosions.remove(ex)

        # Welle fertig -> neue bauen
        # if not self.enemies and not self.player_dead:
        #     self._build_wave("alien")

    # ---------------- Draw ----------------
    def _draw(self):
        bg = self.assets.get("background_img")
        if bg:
            self.screen.blit(bg, (0, 0))
        else:
            self.screen.fill((0, 0, 0))

        if not self.player_dead:
            self.player.draw(self.screen)

        for p in self.player_shots:
            p.draw(self.screen)
        for p in self.enemy_shots:
            p.draw(self.screen)
        for en in self.enemies:
            en.draw(self.screen)
        for ex in self.explosions:
            ex.draw(self.screen)

        # HUD
        txt1 = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        txt2 = self.font.render(f"High Score: {self.highscore}", True, (255, 255, 255))
        self.screen.blit(txt1, (10, 10))
        self.screen.blit(txt2, (10, 50))

        pygame.display.flip()

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
