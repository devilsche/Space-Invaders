POWERUP_CONFIG = {
    "health": {
        "img": "assets/images/icon/health.png",
        "size": (70, 70),         # Verdoppelt von 35x35
        "heal_percentage": 0.25,  # 25% der maximalen Health
        "drop_chance": 0.15,      # 15% Chance bei Enemy-Tod
        "fall_speed": 2,
        "duration": 8000,         # 8 Sekunden bis Verschwinden
        "points": 50,             # Bonus-Punkte beim Aufsammeln
    },
    "repair": {
        "img": "assets/images/icon/repair.png", 
        "size": (70, 70),         # Verdoppelt von 35x35
        "heal_percentage": 0.15,  # 15% der maximalen Health
        "drop_chance": 0.10,      # 10% Chance bei Enemy-Tod
        "fall_speed": 2,
        "duration": 8000,
        "points": 25,
    },
    "shield": {
        "img": "assets/images/icon/shield.png",
        "size": (70, 70),         # Verdoppelt von 35x35
        "drop_chance": 0.08,      # 8% Chance bei Enemy-Tod
        "fall_speed": 2,
        "duration": 8000,         # PowerUp Item Dauer (wie lange es am Boden liegt)
        "points": 75,
    }
}
