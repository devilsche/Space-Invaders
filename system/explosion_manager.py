# system/explosion_manager.py
import pygame
from entities.explosion import Explosion

class ExplosionManager:
    """Optimierter Explosion-Manager mit Pooling und Performance-Limits"""
    
    def __init__(self, max_explosions=25):
        self.explosions = []
        self.max_explosions = max_explosions
        self.frame_cache = {}  # Cache für skalierte Frames
        
    def add_explosion(self, x, y, frames, fps=24, scale=1.0):
        """Fügt eine Explosion hinzu mit Performance-Optimierungen"""
        # Limit erreicht? Älteste Explosion ersetzen
        if len(self.explosions) >= self.max_explosions:
            # Finde die älteste (am weitesten fortgeschrittene) Explosion
            oldest_idx = 0
            oldest_progress = 0
            for i, exp in enumerate(self.explosions):
                if exp.done:
                    oldest_idx = i
                    break
                progress = exp._i / len(exp.frames)
                if progress > oldest_progress:
                    oldest_progress = progress
                    oldest_idx = i
            
            # Ersetze die älteste Explosion
            self.explosions[oldest_idx] = self._create_explosion(x, y, frames, fps, scale)
        else:
            # Normale Hinzufügung
            self.explosions.append(self._create_explosion(x, y, frames, fps, scale))
    
    def _create_explosion(self, x, y, frames, fps, scale):
        """Erstellt Explosion mit gecachten Frames"""
        if not frames:
            return Explosion(x, y, [pygame.Surface((1, 1), pygame.SRCALPHA)], fps)
        
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
        
        return Explosion(x, y, self.frame_cache[cache_key], fps)
    
    def update(self):
        """Effizientes Update ohne teure remove() Operationen"""
        # Update alle Explosionen
        for explosion in self.explosions:
            explosion.update()
        
        # Entferne fertige Explosionen mit List Comprehension (sicher und effizient)
        self.explosions = [exp for exp in self.explosions if not exp.done]
    
    def draw(self, screen):
        """Zeichnet alle aktiven Explosionen"""
        for explosion in self.explosions:
            if not explosion.done:
                explosion.draw(screen)
    
    def clear(self):
        """Leert alle Explosionen (für Levelwechsel etc.)"""
        self.explosions.clear()
    
    def get_count(self):
        """Gibt die Anzahl aktiver Explosionen zurück"""
        return len([exp for exp in self.explosions if not exp.done])
    
    def clear_cache(self):
        """Leert den Frame-Cache (für Memory-Management)"""
        self.frame_cache.clear()
