# Beispiel für skalierte Enemy-Config
from system.utils import scale, scale_pos, scale_size

# Basis-Werte bei 1920x1080
BASE_ENEMY_CONFIG = {
    "alien": {
        "img": "assets/images/enemy/alien.png",
        "size": (45, 45),  # Basis-Größe
        "hp": 100,
        "points": 10,
        "move": {
            "type": "grid",
            "amp_frac": 0.0,
            "hz": 0.0,
            "drop_px": 30,      # Basis-Drop-Distanz
            "speed_start": 2    # Basis-Geschwindigkeit
        },
        "formation": {
            "cols": 8,
            "rows": 4,
            "h_spacing": 60,    # Basis-Horizontal-Abstand
            "v_spacing": 70,    # Basis-Vertikal-Abstand
            "margin_x": 50,     # Basis-X-Rand
            "margin_y": 50      # Basis-Y-Rand
        },
        "shoot": {
            "prob": 0.008
        },
        "weapons": ["laser"],
        "spawn": {
            "y": 80            # Basis-Spawn-Y
        }
    }
}

def get_scaled_enemy_config():
    """Gibt skalierte Enemy-Config basierend auf aktueller Auflösung zurück"""
    scaled_config = {}
    
    for enemy_type, config in BASE_ENEMY_CONFIG.items():
        scaled_config[enemy_type] = {
            "img": config["img"],
            "size": scale_size(*config["size"]),
            "hp": config["hp"],
            "points": config["points"],
            "move": {
                "type": config["move"]["type"],
                "amp_frac": config["move"]["amp_frac"],
                "hz": config["move"]["hz"],
                "drop_px": scale(config["move"]["drop_px"]),
                "speed_start": max(1, scale(config["move"]["speed_start"]))
            },
            "formation": {
                "cols": config["formation"]["cols"],
                "rows": config["formation"]["rows"],
                "h_spacing": scale(config["formation"]["h_spacing"]),
                "v_spacing": scale(config["formation"]["v_spacing"]),
                "margin_x": scale(config["formation"]["margin_x"]),
                "margin_y": scale(config["formation"]["margin_y"])
            },
            "shoot": config["shoot"],
            "weapons": config["weapons"],
            "spawn": {
                "y": scale(config["spawn"]["y"])
            }
        }
    
    return scaled_config

# Skalierte Config für den Import
ENEMY_CONFIG = get_scaled_enemy_config()
