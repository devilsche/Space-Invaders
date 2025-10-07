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
    },
    "double_laser": {
        "img": "assets/images/icon/doubleLaser.png",
        "size": (70, 70),         # Größe für Power-Up Icon
        "drop_chance": 0.05,      # 5% Chance bei Enemy-Tod (seltener)
        "fall_speed": 2,
        "duration": 10000,        # 10 Sekunden bis Verschwinden
        "points": 100,            # Mehr Punkte für seltenes Power-Up
        "weapon_duration": 15000, # 15 Sekunden DoubleLaser-Modus
    },
    "speed_boost": {
        "img": "assets/images/icon/speedup.png",
        "size": (70, 70),         # Größe für Power-Up Icon
        "drop_chance": 0.06,      # 6% Chance bei Enemy-Tod
        "fall_speed": 2,
        "duration": 8000,         # 8 Sekunden bis Verschwinden
        "points": 75,             # Bonus-Punkte beim Aufsammeln
        "speed_duration": 10000,  # 10 Sekunden Speed Boost
        "speed_multiplier": 1.75, # 75% schneller
    },
    "emp": {
        "img": "assets/images/icon/nuke.png",  # Nutze Nuke-Icon für EMP (oder erstelle eigenes)
        "size": (70, 70),         # Größe für Power-Up Icon
        "drop_chance": 0.05,      # 5% Chance bei Enemy-Tod (seltenes Power-Up)
        "fall_speed": 2,
        "duration": 10000,        # 10 Sekunden bis Verschwinden
        "points": 150,            # Hohe Punkte für mächtiges Power-Up
        "min_stage": 1,           # Ab Stage 1 verfügbar
    }
}
