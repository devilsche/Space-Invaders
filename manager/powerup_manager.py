# manager/powerup_manager.py
import pygame
import random
from typing import Optional, List, Tuple
from config.powerup_optimized import calculator
from entities.powerup import PowerUp

class PowerUpManager:
    """Zentrale Verwaltung für PowerUp-Drops"""
    
    def clear_all(self):
        """Entfernt alle PowerUps und leert die Queue."""
        self.powerups.clear()
        self._queued_drops.clear()
    
    def __init__(self, assets):
        self.assets = assets
        self.powerups: List[PowerUp] = []
        self._queued_drops = []  # [(x, y), ...] - Verzögerte PowerUp-Erstellung
        self._last_process = pygame.time.get_ticks()
        
    def queue_drop_check(self, x: int, y: int):
        """Fügt eine Position zur PowerUp-Drop-Prüfung hinzu"""
        self._queued_drops.append((x, y))
        
    def process_queued_drops(self):
        """Verarbeitet die Queue in Batches"""
        current_time = pygame.time.get_ticks()
        # Verarbeite Drops nur alle 16ms (ca. 60fps)
        if current_time - self._last_process < 16:
            return
            
        self._last_process = current_time
        
        # Verarbeite maximal 10 Drops pro Frame
        batch = self._queued_drops[:10]
        self._queued_drops = self._queued_drops[10:]
        
        for x, y in batch:
            drop = calculator.calculate_drop()
            if drop:
                name, cfg = drop
                self.powerups.append(PowerUp(name, cfg, self.assets, x, y))
                
    def update(self, dt: float, screen_height: int):
        """Update alle aktiven PowerUps"""
        self.process_queued_drops()
        
        # Update PowerUps und entferne abgelaufene
        now = pygame.time.get_ticks()
        self.powerups = [p for p in self.powerups if now - p.spawn_time < p.duration and p.rect.top < screen_height]
        
        for powerup in self.powerups:
            powerup.update()
            
    def draw(self, screen):
        """Zeichnet alle aktiven PowerUps"""
        for powerup in self.powerups:
            powerup.draw(screen)
            
    def get_colliding_powerup(self, rect) -> Optional[PowerUp]:
        """Prüft Kollision mit PowerUps und gibt das erste kollidierende zurück"""
        for powerup in self.powerups:
            if rect.colliderect(powerup.rect):
                self.powerups.remove(powerup)
                return powerup
        return None
