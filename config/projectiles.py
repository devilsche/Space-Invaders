# config/projectiles.py
PROJECTILES_CONFIG = {
    "laser": {
        "dmg": 50,
        "size": (5, 18),
        "radius": 0,
        "cooldown": 150,
        "amount": -1,
        "speed": 10,
        "accel": 1,
        "img": "assets/images/laser_vertical.png",
        "sound_start": "assets/sounds/laser_shoot.wav",
        "sound_hit": "assets/sounds/laser_explosion.wav",
        "sound_destroy": "assets/sounds/laser_explosion.wav",
        "explosion": {
            "sheet": "assets/images/exp2.png",
            "cols": 4, "rows": 4,
            "fw": 64, "fh": 64,
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
        "img": "assets/images/rocket.png",
        "sound_start": "assets/sounds/rocket_launch.wav",
        "sound_fly": "assets/sounds/rocket_zisch.wav",
        "sound_hit": "assets/sounds/rocket_hit.wav",
        "sound_destroy": "assets/sounds/rocket_explosion.wav",
        "explosion": {
            "sheet": "assets/images/exp2.png",
            "cols": 4, "rows": 4,
            "fw": 64, "fh": 64,
            "scale": 1.4,
            "fps": 24
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
        "img": "assets/images/nuke.png",
        "sound_start": "assets/sounds/nuke_launch.wav",
        "sound_fly": "assets/sounds/nuke_zisch.wav",
        "sound_hit": "assets/sounds/nuke_explosion.wav",
        "sound_destroy": "assets/sounds/nuke_explosion.wav",
        "explosion": {
            "sheet": "assets/images/exp2.png",
            "cols": 4, "rows": 4,
            "fw": 64, "fh": 64,
            "scale": 2.5,
            "fps": 20
        }
    }
}
