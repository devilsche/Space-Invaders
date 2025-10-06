import json
import os
import pygame
from config.settings import REFERENCE_WIDTH, REFERENCE_HEIGHT

HIGHSCORE_FILE = "data/highscore.json"

# Dynamische Skalierungs-Utilities
def get_current_scale_factors():
    """Berechnet aktuelle Skalierungsfaktoren basierend auf Bildschirmgröße"""
    screen = pygame.display.get_surface()
    if screen is None:
        return 1.0, 1.0, 1.0

    current_width, current_height = screen.get_size()
    scale_x = current_width / REFERENCE_WIDTH
    scale_y = current_height / REFERENCE_HEIGHT
    scale_factor = min(scale_x, scale_y)

    return scale_factor, scale_x, scale_y

def scale(value):
    """Skaliert einen Wert uniform basierend auf aktueller Bildschirmgröße"""
    scale_factor, _, _ = get_current_scale_factors()
    return int(value * scale_factor)

def scale_x(value):
    """Skaliert einen X-Wert basierend auf aktuellem Breiten-Verhältnis"""
    _, scale_x_factor, _ = get_current_scale_factors()
    return int(value * scale_x_factor)

def scale_y(value):
    """Skaliert einen Y-Wert basierend auf aktuellem Höhen-Verhältnis"""
    _, _, scale_y_factor = get_current_scale_factors()
    return int(value * scale_y_factor)

def scale_pos(x, y):
    """Skaliert eine Position (x, y)"""
    return (scale_x(x), scale_y(y))

def scale_size(width, height):
    """Skaliert eine Größe (width, height) uniform"""
    return (scale(width), scale(height))

def load_highscore():
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r") as f:
                data = json.load(f)
                return data.get("highscore", 0)
        except Exception:
            return 0
    return 0

def save_highscore(value):
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            json.dump({"highscore": value}, f)
    except Exception:
        pass
