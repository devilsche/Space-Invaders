# config/weapon.py - Konsolidierte Waffen- und EMP-Konfiguration
# Ersetzt: config/projectile.py und config/emp.py

# Projektil/Waffen-Konfiguration (für Player und Enemy Waffen)
WEAPON_CONFIG = {
    "laser": {
        "dmg": 50,
        "size": (5, 18),
        "radius": 0,
        "cooldown": 150,
        "amount": -1,
        "speed": 15,
        "accel": 1,
        "img": "assets/images/weapon/laser_vertical.png",
        "sound_start": "assets/sound/laser_shoot.wav",
        "sound_hit": "assets/sound/laser_explosion.wav",
        "sound_destroy": "assets/sound/laser_explosion.wav",
        "explosion": {
            "sheet": "assets/images/exp2.png",
            "cols": 4,
            "rows": 4,
            "fw": 64,
            "fh": 64,
            "scale": 0.8,
            "fps": 10,
            "keep": 4
        }
    },
    "double_laser": {
        "dmg": 50,
        "size": (10, 18),  # Etwas breiter als normaler Laser
        "radius": 0,
        "cooldown": 200,   # Etwas langsamer als normaler Laser
        "amount": -1,
        "speed": 15,
        "accel": 1,
        "img": "assets/images/weapon/laser_vertical.png",
        "sound_start": "assets/sound/laser_shoot.wav",
        "sound_hit": "assets/sound/laser_explosion.wav",
        "sound_destroy": "assets/sound/laser_explosion.wav",
        "explosion": {
            "sheet": "assets/images/exp2.png",
            "cols": 4,
            "rows": 4,
            "fw": 64,
            "fh": 64,
            "scale": 0.8,
            "fps": 10,
            "keep": 4
        }
    },
    "rocket": {
        "dmg": 200,
        "size": (12, 24),
        "radius": 120,
        "cooldown": 1000,
        "amount": 7,
        "speed": 5,
        "accel": 1.03,
        "img": "assets/images/weapon/rocket.png",
        "sound_start": "assets/sound/rocket_launch.wav",
        "sound_fly": "assets/sound/rocket_zisch.wav",
        "sound_hit": "assets/sound/rocket_hit.wav",
        "sound_destroy": "assets/sound/rocket_explosion.wav",
        "explosion": {
            "sheet": "assets/images/exp2.png",
            "cols": 4, "rows": 4,
            "fw": 64, "fh": 64,
            "scale": 1.4,
            "fps": 24
        }
    },
    "homing_rocket": {
        "dmg": 150,
        "size": (12, 24),
        "radius": 140,
        "cooldown": 1200,
        "amount": 4,
        "speed": 6,
        "accel": 1.02,
        "img": "assets/images/weapon/homingRocket.png",
        "sound_start": "assets/sound/rocket_launch.wav",
        "sound_fly": "assets/sound/rocket_zisch.wav",
        "sound_hit": "assets/sound/rocket_hit.wav",
        "sound_destroy": "assets/sound/rocket_explosion.wav",
        "explosion": {
            "sheet": "assets/images/exp2.png",
            "cols": 4, "rows": 4,
            "fw": 64, "fh": 64,
            "scale": 1.6,
            "fps": 24
        }
    },
    "blaster": {
        "dmg": 80,
        "size": (15, 15),
        "radius": 0,
        "cooldown": 300,  # Längerer Cooldown wegen Lenkfähigkeit
        "amount": -1,
        "speed": 13,      # Mittlere Geschwindigkeit
        "accel": 1.02,    # Leichte Beschleunigung
        "enemy_speed": 11, # Enemy-Version
        "img": "assets/images/weapon/blaster.png",  # Neue Blaster-Grafik
        "sound_start": "assets/sound/laser_shoot.wav",
        "sound_hit": "assets/sound/laser_explosion.wav",
        "sound_destroy": "assets/sound/laser_explosion.wav",
        "explosion": {
            "sheet": "assets/images/exp2.png",
            "cols": 4,
            "rows": 4,
            "fw": 64,
            "fh": 64,
            "scale": 0.9,
            "fps": 12,
            "keep": 4
        }
    },
    "nuke": {
        "dmg": 600,
        "size": (20, 36),
        "radius": 300,
        "cooldown": 5000,
        "amount": 3,
        "speed": 3,
        "accel": 1.01, 
        "img": "assets/images/weapon/nuke.png",
        "sound_start": "assets/sound/nuke_launch.wav",
        "sound_fly": "assets/sound/nuke_zisch.wav",
        "sound_hit": "assets/sound/nuke_explosion.wav",
        "sound_destroy": "assets/sound/nuke_explosion.wav",
        "explosion": {
            "sheet": "assets/images/exp2.png",
            "cols": 4, "rows": 4,
            "fw": 64, "fh": 64,
            "scale": 2.5,
            "fps": 20
        }
    },
    "emp": {
        "dmg": 0,                    # Kein direkter Schaden
        "size": (64, 64),            # Start-Größe (entspricht start_diameter)
        "radius": 800,               # Maximum-Reichweite (entspricht max_diameter)
        "cooldown": 5000,            # 5 Sekunden zwischen EMP-Einsätzen
        "amount": 0,                 # Keine Startladungen - nur via Power-Up
        "speed": 1600,               # Expansions-Geschwindigkeit: 800px in 0.5s = 1600px/s
        "accel": 1.0,                # Konstante Expansion
        "type": "emp_pulse",         # Spezieller EMP-Typ
        "img": "assets/images/shield3.png",  # 1024x1024 4x4 Spritesheet
        
        # EMP-spezifische Eigenschaften (nutzen bestehende Felder kreativ)
        "weapon_disable_duration": 10.0,     # Sekunden ohne Schießen
        "movement_disable_duration": 7.0,    # Sekunden gestörte Bewegung  
        "movement_speed_factor": 0.1,        # 10% der normalen Geschwindigkeit (90% Verlangsamung)
        "visual_effect_duration": 10.0,      # Sekunden für blauen Indikator
        "score_bonus": 50,                   # Punkte pro betroffenem Gegner
        "charges_max": 99,                   # Maximum 99 EMP-Ladungen
        "charges_per_powerup": 1,            # +1 Ladung pro Power-Up (nicht 3)
        "drop_chance": 0.05,                 # 5% Chance bei Enemy-Tod
        "activation_key": "V",               # V-Taste für EMP-Aktivierung
        
        # Sound & Explosion wie andere Waffen strukturiert
        "sound_start": "assets/sound/laser_shoot.wav",  # Placeholder
        "sound_hit": "assets/sound/laser_explosion.wav", # Placeholder
        "explosion": {
            "sheet": "assets/images/exp2.png",
            "cols": 4,
            "rows": 4,
            "fw": 64,
            "fh": 64,
            "scale": 1.0,
            "fps": 16,
            "keep": 4
        }
    }
}

# Alias für Rückwärtskompatibilität
PROJECTILES_CONFIG = WEAPON_CONFIG

# EMP-Konfiguration als Alias für einheitliche Nutzung
EMP_CONFIG = WEAPON_CONFIG["emp"]
