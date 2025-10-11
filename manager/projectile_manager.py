from typing import List, Optional
import pygame
import logging

class ProjectileManager:
    """Zentraler Manager für alle Projektile im Spiel"""

    def clear_all(self):
        """Entfernt alle Projektile."""
        self.player_shots.clear()
        self.enemy_shots.clear()

    def __init__(self, max_projectiles=2000):  # Deutlich erhöht für mehr sichtbare Schüsse
        self.player_shots: List = []
        self.enemy_shots: List = []
        self.max_projectiles = max_projectiles
        self._last_cleanup = pygame.time.get_ticks()
        self._last_limit_warning = 0  # Für Limit-Warnungen

    def add_player_shot(self, shot) -> bool:
        """Fügt einen Spielerschuss hinzu, wenn Limit nicht überschritten"""
        total = len(self.player_shots) + len(self.enemy_shots)
        if total < self.max_projectiles:
            self.player_shots.append(shot)
            return True
        # Warnung nur alle 5 Sekunden
        now = pygame.time.get_ticks()
        if now - self._last_limit_warning > 5000:
            self._last_limit_warning = now
            logging.warning(f"⚠️ Projektil-Limit erreicht! {total}/{self.max_projectiles} - Player-Schuss blockiert")
        return False

    def add_enemy_shot(self, shot) -> bool:
        """Fügt einen Gegnerschuss hinzu, wenn Limit nicht überschritten"""
        total = len(self.player_shots) + len(self.enemy_shots)
        if total < self.max_projectiles:
            self.enemy_shots.append(shot)
            return True
        # Warnung nur alle 5 Sekunden
        now = pygame.time.get_ticks()
        if now - self._last_limit_warning > 5000:
            self._last_limit_warning = now
            logging.warning(f"⚠️ Projektil-Limit erreicht! {total}/{self.max_projectiles} - Enemy-Schuss blockiert")
        return False

    def physics_update(self, game):
        """Fixed timestep physics update für alle Projektile"""
        current_time = pygame.time.get_ticks()
        
        # Cleanup nur alle 3 Sekunden und mit größerem Bereich
        if current_time - self._last_cleanup >= 3000:
            self._last_cleanup = current_time
            screen_height = game.screen.get_height()
            # Entferne nur Projektile, die SEHR weit außerhalb des Bildschirms sind
            self.player_shots = [shot for shot in self.player_shots if 
                               shot.rect.bottom > -200 and shot.rect.top < screen_height + 200]
            self.enemy_shots = [shot for shot in self.enemy_shots if 
                              shot.rect.bottom > -200 and shot.rect.top < screen_height + 200]
        
        # Physics-Update für alle Projektile
        for shot in self.player_shots:
            shot.physics_update(game)
                
        for shot in self.enemy_shots:
            shot.physics_update(game)
            
    def update(self, dt: float, screen_height: int):
        """Legacy update - für nicht-physikalische Updates"""
        pass
                
        # Homing-Projektile werden in der Game-Klasse geupdated, damit sie Zugriff auf das Game-Objekt haben
            
    def draw(self, screen):
        """Zeichnet alle Projektile"""
        for shot in self.player_shots:
            shot.draw(screen)
        for shot in self.enemy_shots:
            shot.draw(screen)
            
    def clear_all(self):
        """Entfernt alle Projektile"""
        self.player_shots.clear()
        self.enemy_shots.clear()
        
    def get_player_shots(self) -> List:
        """Gibt Liste der Spieler-Projektile zurück"""
        return self.player_shots
        
    def get_enemy_shots(self) -> List:
        """Gibt Liste der Gegner-Projektile zurück"""
        return self.enemy_shots
        
    def remove_shot(self, shot):
        """Entfernt ein spezifisches Projektil"""
        if shot in self.player_shots:
            self.player_shots.remove(shot)
        elif shot in self.enemy_shots:
            self.enemy_shots.remove(shot)
