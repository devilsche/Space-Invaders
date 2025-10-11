# manager/explosion_manager.py
import pygame
import logging
import time
import os
from entities.explosion import Explosion

class ExplosionManager:
    """Optimierter Explosion-Manager mit Pooling und Performance-Limits"""

    def clear_all(self):
        """Entfernt alle Explosionen und leert den Pool."""
        self.explosions.clear()
        self.inactive_pool.clear()
        self._explosion_queue.clear()

    def __init__(self, max_explosions=5000):  # MASSIV erhöht für garantiert genug Explosionen!
        self.explosions               = []
        self.inactive_pool            = [] # Pool für inaktive Explosionen
        self.max_explosions           = max_explosions
        self.frame_cache              = {} # Cache für skalierte Frames
        self._last_cleanup            = pygame.time.get_ticks()
        self._last_log                = time.time()
        self._explosion_count         = 0 # Zähler für Explosionen seit letztem Log
        self._last_add_time           = 0 # Zeitpunkt der letzten Explosion
        self._min_explosion_interval  = 0 # KEINE Verzögerung zwischen Explosionen!
        self._performance_mode        = False # Performance-Modi deaktiviert
        self._severe_performance_mode = False
        self._last_fps_check          = pygame.time.get_ticks()
        self._frame_count             = 0
        self._current_fps             = 60
        self._consecutive_low_fps     = 0
        self._explosion_queue         = [] # Queue für den Fall der Fälle
        
        
        self._queue_next_at = 0
        self._queue_interval_ms = 10

        # Setup Logging
        self.weapon_stats = {}  # Dictionary für Waffen-Statistiken
        self.enemy_death_count = 0
        self.explosion_calls = 0
        self.skipped_explosions = 0

        # Logging konfigurieren
        log_path = os.path.join(os.path.dirname(__file__), '..', 'explosion_stats.log')

        # Stelle sicher, dass der Logger noch nicht existiert
        if not logging.getLogger().handlers:
            logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(message)s',
                            filename=log_path)

    def add_explosion(self, x, y, frames, fps=24, scale=1.0, weapon_type=None, explosion_category=None):
        """
        Fügt eine Explosion hinzu mit Performance-Optimierungen und Object Pooling
        
        Args:
            explosion_category: "hit" (Projektil-Treffer) oder "destroy" (Gegner-Tod)
        """
        current_tick = pygame.time.get_ticks()
        print(f"[{current_tick}ms] ExplosionManager.add_explosion() called: pos=({x},{y}), frames={len(frames)}, fps={fps}, category={explosion_category}")

        # Waffen-Explosion protokollieren mit Kategorie
        if weapon_type and explosion_category:
            if weapon_type not in self.weapon_stats:
                self.weapon_stats[weapon_type] = {
                    'kills': 0,
                    'hit_explosions': 0,
                    'destroy_explosions': 0,
                    'total_explosions': 0
                }
            
            if explosion_category == "hit":
                self.weapon_stats[weapon_type]['hit_explosions'] += 1
            elif explosion_category == "destroy":
                self.weapon_stats[weapon_type]['destroy_explosions'] += 1
            
            self.weapon_stats[weapon_type]['total_explosions'] += 1
            
            logging.info(f"Neue {explosion_category.upper()}-Explosion für {weapon_type} an Position ({x}, {y})")
        elif weapon_type:
            # Legacy support - ohne Kategorie
            self.log_weapon_explosion(weapon_type)
            logging.info(f"Neue Explosion für {weapon_type} an Position ({x}, {y})")

        # KEINE Größenanpassungen mehr - volle Größe immer!
        actual_scale = scale * 1.2  # Alles 20% größer!

        while self._explosion_queue and current_tick >= self._queue_next_at:
            xq, yq, fr, fpsq, sc = self._explosion_queue.pop(0)
            self._create_explosion(xq, yq, fr, fpsq, sc)
            self._queue_next_at = current_tick + self._queue_interval_ms

        self._last_add_time = current_tick
        self._explosion_count += 1

        # Performance Logging
        current_time = time.time()
        if current_time - self._last_log >= 1.0:  # Log jede Sekunde
            active_count = len([exp for exp in self.explosions if not exp.done])
            pool_size = len(self.inactive_pool)
            cache_size = len(self.frame_cache)

            logging.info("\n=== Performance-Statistiken ===")
            logging.info(f"Aktive Explosionen: {active_count}")
            logging.info(f"Pool-Größe: {pool_size}")
            logging.info(f"Cache-Größe: {cache_size}")
            logging.info(f"Explosionen/Sekunde: {self._explosion_count}")
            logging.info(f"FPS: {self._current_fps}")
            logging.info(f"Performance-Modus: {'Kritisch' if self._severe_performance_mode else 'Normal' if self._performance_mode else 'Aus'}")

            self._explosion_count = 0
            self._last_log = current_time

            # Zusätzlich Waffenstatistiken loggen
            logging.info("\n=== Waffen-Statistiken ===")
            for weapon, stats in self.weapon_stats.items():
                logging.info(f"\n{weapon}:")
                logging.info(f"- Kills: {stats['kills']}")
                logging.info(f"- HIT Explosionen: {stats['hit_explosions']}")
                logging.info(f"- DESTROY Explosionen: {stats['destroy_explosions']}")
                logging.info(f"- Total Explosionen: {stats['total_explosions']}")
                if stats['kills'] > 0:
                    destroy_ratio = stats['destroy_explosions'] / stats['kills'] * 100
                    logging.info(f"- DESTROY/Kill Ratio: {destroy_ratio:.1f}%")
                    total_ratio = stats['total_explosions'] / stats['kills'] * 100
                    logging.info(f"- Total/Kill Ratio: {total_ratio:.1f}%")

        # Versuche zuerst, eine inaktive Explosion wiederzuverwenden
        explosion = None
        if self.inactive_pool:
            explosion = self.inactive_pool.pop()
            print(f"[{current_tick}ms] Recycling explosion from pool (pool size: {len(self.inactive_pool)})")
            # Setze die Explosion zurück
            cached_frames = self._get_cached_frames(frames, scale)
            explosion.frames = cached_frames
            explosion.rect = cached_frames[0].get_rect(center=(x, y))
            explosion.fps = max(1, int(fps))
            explosion._t_last = pygame.time.get_ticks()
            explosion._i = 0
            explosion.done = False
            
            # WICHTIG: Recycelte Explosion muss zu self.explosions hinzugefügt werden!
            self.explosions.append(explosion)

        if explosion is None:
            print(f"[{current_tick}ms] Creating NEW explosion (active: {len(self.explosions)}/{self.max_explosions})")
            # Wenn kein Pool-Objekt verfügbar, erstelle neue Explosion
            if len(self.explosions) >= self.max_explosions:
                # Finde die älteste Explosion
                oldest_idx = next((i for i, exp in enumerate(self.explosions) if exp.done), 0)
                # Recycling: Verschiebe die älteste in den Pool
                self.inactive_pool.append(self.explosions[oldest_idx])
                # Erstelle neue an dieser Position
                explosion = self._create_explosion(x, y, frames, fps, scale)
                self.explosions[oldest_idx] = explosion
            else:
                explosion = self._create_explosion(x, y, frames, fps, scale)
                self.explosions.append(explosion)
        
        print(f"[{current_tick}ms] Explosion added! Total active: {len([e for e in self.explosions if not e.done])}, Total in list: {len(self.explosions)}")

    def _get_cached_frames(self, frames, scale):
        """Holt oder erstellt gecachte Frames"""
        if not frames:
            return [pygame.Surface((1, 1), pygame.SRCALPHA)]

        # Cache-Key für skalierte Frames
        cache_key = (id(frames[0]), scale, len(frames))

        if cache_key not in self.frame_cache:
            if scale != 1.0:
                # Skalierung nur einmal berechnen und cachen
                scaled_frames = []
                for frame in frames:
                    new_size = (int(frame.get_width() * scale), int(frame.get_height() * scale))
                    scaled_frame = pygame.transform.smoothscale(frame, new_size)
                    scaled_frames.append(scaled_frame)
                self.frame_cache[cache_key] = scaled_frames
            else:
                self.frame_cache[cache_key] = frames

        return self.frame_cache[cache_key]

    def _create_explosion(self, x, y, frames, fps, scale):
        """Erstellt Explosion mit gecachten Frames"""
        cached_frames = self._get_cached_frames(frames, scale)
        explosion = Explosion(x, y, cached_frames, fps)
        logging.info(f"Explosion erstellt bei ({x}, {y}) mit {len(cached_frames)} Frames bei {fps} FPS")
        return explosion

    def update(self):
        """Effizientes Update mit Object Pooling und Performance Monitoring"""
        update_start = time.time()
        current_time = pygame.time.get_ticks()

        # FPS Berechnung (nur für Statistiken, keine Performance-Anpassungen mehr)
        self._frame_count += 1
        if current_time - self._last_fps_check >= 1000:  # Jede Sekunde
            self._current_fps = self._frame_count
            self._frame_count = 0
            self._last_fps_check = current_time

            # Performance-Modi DEAKTIVIERT - alle Explosionen werden IMMER angezeigt!
            # if self._current_fps < 15:  # Sehr niedrige FPS
            #     self._consecutive_low_fps += 1
            #     if self._consecutive_low_fps >= 2:  # 2 Sekunden anhaltend niedrige FPS
            #         self._severe_performance_mode = True
            #         self._performance_mode = True
            #         logging.info(f"KRITISCHER Performance-Modus aktiviert - FPS: {self._current_fps}")
            # elif self._current_fps < 30:  # Niedrige FPS
            #     self._performance_mode = True
            #     logging.info(f"Performance-Modus aktiviert - FPS: {self._current_fps}")
            # else:  # Normale FPS
            #     self._performance_mode = False
            #     self._severe_performance_mode = False
            #     self._consecutive_low_fps = 0

        # Update alle Explosionen und verschiebe fertige in den Pool
        active_count = len([exp for exp in self.explosions if not exp.done])
        update_interval = 1  # IMMER jede Explosion updaten - keine Performance-Modi!

        # Performance-Modi komplett deaktiviert für volle Sichtbarkeit aller Explosionen
        # if self._severe_performance_mode:
        #     update_interval = 4  # Nur jede vierte Explosion updaten
        # elif self._performance_mode:
        #     update_interval = 2  # Nur jede zweite Explosion updaten

        for explosion in self.explosions:
            if not explosion.done:
                # IMMER updaten - keine Interval-Checks mehr!
                explosion.update()
                if explosion.done:
                    self.inactive_pool.append(explosion)

        # Cleanup nur alle 3000ms durchführen - mehr Zeit für Explosionen
        if current_time - self._last_cleanup >= 3000:
            cleanup_start = time.time()
            self._last_cleanup = current_time

            # Entferne fertige Explosionen aus der aktiven Liste
            old_count = len(self.explosions)
            self.explosions = [exp for exp in self.explosions if not exp.done]
            removed_count = old_count - len(self.explosions)

            # Begrenze Pool-Größe
            old_pool_size = len(self.inactive_pool)
            max_pool_size = self.max_explosions * 2
            if len(self.inactive_pool) > max_pool_size:
                self.inactive_pool = self.inactive_pool[:max_pool_size]

            cleanup_time = (time.time() - cleanup_start) * 1000
            if removed_count > 0 or old_pool_size != len(self.inactive_pool):
                logging.info(f"Cleanup: Entfernt {removed_count} Explosionen, "
                           f"Pool: {len(self.inactive_pool)}/{max_pool_size}, "
                           f"Zeit: {cleanup_time:.2f}ms")

    def register_enemy_death(self, weapon_type=None):
        """Registriert den Tod eines Gegners mit der verwendeten Waffe"""
        self.enemy_death_count += 1
        if weapon_type:
            if weapon_type not in self.weapon_stats:
                self.weapon_stats[weapon_type] = {
                    'kills': 0,
                    'hit_explosions': 0,
                    'destroy_explosions': 0,
                    'total_explosions': 0
                }
            self.weapon_stats[weapon_type]['kills'] += 1

    def log_weapon_explosion(self, weapon_type):
        """Legacy-Methode für Kompatibilität"""
        if weapon_type not in self.weapon_stats:
            self.weapon_stats[weapon_type] = {
                'kills': 0,
                'hit_explosions': 0,
                'destroy_explosions': 0,
                'total_explosions': 0
            }
        self.weapon_stats[weapon_type]['total_explosions'] += 1
        self.explosion_calls += 1

    def print_stats(self):
        """Gibt die gesammelten Statistiken mit HIT/DESTROY Trennung aus"""
        logging.info("\n=== Explosions-Statistiken ===")
        logging.info(f"Getötete Gegner insgesamt: {self.enemy_death_count}")
        
        # Gesamtstatistiken berechnen aus weapon_stats
        total_hit_explosions = sum(stats['hit_explosions'] for stats in self.weapon_stats.values())
        total_destroy_explosions = sum(stats['destroy_explosions'] for stats in self.weapon_stats.values())
        total_explosions = sum(stats['total_explosions'] for stats in self.weapon_stats.values())
        
        logging.info(f"HIT Explosionen gesamt: {total_hit_explosions}")
        logging.info(f"DESTROY Explosionen gesamt: {total_destroy_explosions}")
        logging.info(f"Explosionen gesamt: {total_explosions}")
        
        if self.enemy_death_count > 0:
            destroy_ratio = total_destroy_explosions / self.enemy_death_count * 100
            logging.info(f"DESTROY/Kill Ratio: {destroy_ratio:.1f}%")

        logging.info("\n=== Statistiken pro Waffe ===")
        for weapon, stats in self.weapon_stats.items():
            logging.info(f"\n{weapon}:")
            logging.info(f"- Kills: {stats['kills']}")
            logging.info(f"- HIT Explosionen (Projektil-Impact): {stats['hit_explosions']}")
            logging.info(f"- DESTROY Explosionen (Enemy-Tod): {stats['destroy_explosions']}")
            logging.info(f"- Total Explosionen: {stats['total_explosions']}")
            if stats['kills'] > 0:
                destroy_ratio = stats['destroy_explosions'] / stats['kills'] * 100
                logging.info(f"- DESTROY/Kill Ratio: {destroy_ratio:.1f}%")
                total_ratio = stats['total_explosions'] / stats['kills'] * 100
                logging.info(f"- Total/Kill Ratio: {total_ratio:.1f}%")

    def draw(self, screen):
        """Zeichnet alle aktiven Explosionen"""
        drawn_count = 0
        for explosion in self.explosions:
            if not explosion.done:
                explosion.draw(screen)
                drawn_count += 1
        
        # Debug: Nur loggen wenn Explosionen gezeichnet werden
        if drawn_count > 0:
            current_tick = pygame.time.get_ticks()
            print(f"[{current_tick}ms] Drawing {drawn_count} explosions")

    def clear(self):
        """Leert alle Explosionen und den Pool"""
        self.explosions.clear()
        self.inactive_pool.clear()
        self.frame_cache.clear()
