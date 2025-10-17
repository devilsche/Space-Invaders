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
        "file": "assets/fonts/Astralight.ttf",
        "sizes": {
            "huge"  : 180, # Haupttitel
            "large" : 120, # Untertitel
            "medium": 90 , # Kleinere Titel
        }
    },

    # Menü Font
    "menu": {
        "file": "assets/fonts/White On Black.ttf",
        "sizes": {
            "large" : 96,
            "normal": 64,
            "small" : 48,
        }
    },

    "hud": {
        "file": "assets/fonts/monofonto rg.otf",
        "sizes": {
            "large" : 32,
            "normal": 24,
            "small" : 20,
            "tiny"  : 16,
        }
    },

    # Controls Font
    "controls": {
        "file": "assets/fonts/monofonto rg.otf",
        "sizes": {
            "large" : 48,
            "normal": 36,
            "small" : 28,
        }
    }
}
