import json
import os
import pygame
from config.settings import REFERENCE_WIDTH, REFERENCE_HEIGHT

HIGHSCORE_FILE = "data/highscore.json"

# Dynamische Bildschirmgrößen-Tracking (zur Laufzeit änderbar)
_current_width = None
_current_height = None

def update_screen_size(width, height):
    """Aktualisiert die aktuellen Bildschirmabmessungen zur Laufzeit"""
    global _current_width, _current_height
    _current_width = width
    _current_height = height
    print(f"Screen size updated to: {width}x{height}")

# Dynamische Skalierungs-Utilities
def get_current_scale_factors():
    """Berechnet aktuelle Skalierungsfaktoren basierend auf Bildschirmgröße"""
    global _current_width, _current_height
    
    # Verwende Runtime-Größe falls verfügbar, sonst Pygame-Surface
    if _current_width is not None and _current_height is not None:
        current_width, current_height = _current_width, _current_height
    else:
        screen = pygame.display.get_surface()
        if screen is None:
            return 1.0, 1.0, 1.0
        current_width, current_height = screen.get_size()

    scale_x = current_width / REFERENCE_WIDTH
    scale_y = current_height / REFERENCE_HEIGHT
    
    # Verwende einen aggressiveren Skalierungsfaktor um schwarze Ränder zu vermeiden
    # Verwende den Durchschnitt statt minimum für bessere Ausnutzung
    scale_factor = (scale_x + scale_y) / 2.0
    
    # Mindest-Skalierung für bessere Lesbarkeit
    scale_factor = max(scale_factor, 1.2)

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
