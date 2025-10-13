# config/fonts.py
"""
Font-Konfiguration für das Spiel

Fonts müssen als .ttf/.otf Dateien in assets/fonts/ vorhanden sein:
- Astralight.ttf
- White On Black.ttf  
- monofonto rg.otf
"""

# Font-Dateien (relativ zu assets/fonts/)
FONTS = {
    # Titel-Screen Font
    "title": {
        "file": "assets/fonts/Astralight.ttf",  # Großbuchstabe!
        "sizes": {
            "huge": 173,     # Haupttitel (96 * 1.8)
            "large": 115,    # Untertitel (64 * 1.8)
            "medium": 86,    # Kleinere Titel (48 * 1.8)
        },
        "fallback": None  # System font falls nicht vorhanden
    },
    
    # Menü Font
    "menu": {
        "file": "assets/fonts/White On Black.ttf",  # Mit Leerzeichen!
        "sizes": {
            "large": 86,     # Menü-Titel (48 * 1.8)
            "normal": 58,    # Menü-Optionen (32 * 1.8)
            "small": 43,     # Controls/Hints (24 * 1.8)
        },
        "fallback": None
    },
    
    # HUD/Gameplay Font
    "hud": {
        "file": "assets/fonts/monofonto rg.otf",  # .otf Datei!
        "sizes": {
            "large": 32,     # Score
            "normal": 24,    # Standard HUD
            "small": 20,     # Kleine Info
            "tiny": 16,      # Debug
        },
        "fallback": None
    }
}
