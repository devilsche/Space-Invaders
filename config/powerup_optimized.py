from typing import Dict, Optional, Tuple
import random
from .powerup import POWERUP_CONFIG

class PowerUpDropCalculator:
    """Optimierter PowerUp-Drop Calculator mit vorberechneten Wahrscheinlichkeiten"""
    
    def __init__(self, config):
        self.config = config
        self._prepare_cumulative_chances()
        
    def _prepare_cumulative_chances(self):
        """Berechnet kumulative Wahrscheinlichkeiten für schnellere Drops"""
        # Sortiere PowerUps nach Drop-Chance (absteigend)
        sorted_powerups = sorted(
            self.config.items(),
            key=lambda x: x[1]['drop_chance'],
            reverse=True
        )
        
        # Berechne kumulative Wahrscheinlichkeiten
        self.cum_chances = []
        cumsum = 0
        for name, cfg in sorted_powerups:
            cumsum += cfg['drop_chance']
            self.cum_chances.append((cumsum, name, cfg))
            
        # Gesamtwahrscheinlichkeit für "kein Drop"
        self.total_chance = cumsum
            
    def calculate_drop(self) -> Optional[Tuple[str, dict]]:
        """Berechnet einen einzelnen PowerUp-Drop mit nur einer Zufallszahl"""
        # Eine Zufallszahl für die Entscheidung
        roll = random.random()
        
        # Wenn roll > Gesamtwahrscheinlichkeit: Kein Drop
        if roll > self.total_chance:
            return None
            
        # Finde das PowerUp basierend auf der Zufallszahl
        for cum_chance, name, cfg in self.cum_chances:
            if roll <= cum_chance:
                return (name, cfg)
                
        return None

# Singleton-Instanz
calculator = PowerUpDropCalculator(POWERUP_CONFIG)
