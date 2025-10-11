from typing import Dict, Optional, Tuple
import random
from .powerup import POWERUP_CONFIG

class PowerUpDropCalculator:
    """Zwei-stufiger PowerUp-Drop Calculator:
    1. Wähle zufällig einen PowerUp-Typ (gleiche Chance für alle)
    2. Würfle ob dieser Typ wirklich droppt (basierend auf drop_chance)
    """
    
    def __init__(self, config):
        self.config = config
        self.powerup_types = list(config.keys())
        
    def calculate_drop(self) -> Optional[Tuple[str, dict]]:
        """Berechnet einen einzelnen PowerUp-Drop mit zwei-stufigem System"""
        # Stufe 1: Wähle zufällig einen PowerUp-Typ (alle gleiche Chance)
        chosen_type = random.choice(self.powerup_types)
        chosen_config = self.config[chosen_type]
        
        # Stufe 2: Würfle ob dieser Typ wirklich droppt
        drop_chance = chosen_config.get('drop_chance', 0.0)
        roll = random.random()
        
        if roll <= drop_chance:
            return (chosen_type, chosen_config)
        
        return None

# Singleton-Instanz
calculator = PowerUpDropCalculator(POWERUP_CONFIG)

