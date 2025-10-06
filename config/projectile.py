# config/projectiles.py
PROJECTILES_CONFIG = {
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
    }
}
