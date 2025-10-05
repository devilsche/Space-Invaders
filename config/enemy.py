ENEMY_CONFIG = {
    # --- Standard-Alien, leicht zu besiegen ---
    "alien": {
        "img"   : "assets/images/enemy/alien.png",
        "size"  : (45, 45),
        "hp"    : 100,
        "points": 10,
        "move"  : {
            "type"       : "grid", # bewegt sich im Schwarm
            "amp_frac"   : 0.0,
            "hz"         : 0.0,
            "drop_px"    : 30,
            "speed_start": 2
        },
        "formation": {
            "cols"     : 8,
            "rows"     : 4,
            "h_spacing": 60,
            "v_spacing": 70,
            "margin_x" : 50,
            "margin_y" : 50
        },
        "shoot": {
            "prob": 0.008
        },
        "weapons": [
            "laser"
        ],
        "spawn": {
            "y": 80
        }
    },

    # --- Schneller Gegner, wenig HP ---
    "drone": {
        "img"   : "assets/images/enemy/drone.png",
        "size"  : (30, 30),
        "hp"    : 50,
        "points": 20,
        "move": {
            "type"       : "grid",
            "amp_frac"   : 0.0,
            "hz"         : 0.0,
            "drop_px"    : 20,
            "speed_start": 4
        },
        "formation": {
            "cols"     : 10,
            "rows"     : 2,
            "h_spacing": 40,
            "v_spacing": 40,
            "margin_x" : 50,
            "margin_y" : 50
        },
        "shoot": {
            "prob": 0.02,
        },
        "weapons": [
            "laser"
        ],
        "spawn": {
            "y": 70
        }
    },

    # --- Starker Gegner, Tank ---
    "tank": {
        "img"   : "assets/images/enemy/tank.png",
        "size"  : (60, 60),
        "hp"    : 300,
        "points": 50,
        "move"  : {
            "type"       : "grid",
            "amp_frac"   : 0.0,
            "hz"         : 0.0,
            "drop_px"    : 25,
            "speed_start": 1
        },
        "formation": {
            "cols"     : 4,
            "rows"     : 2,
            "h_spacing": 80,
            "v_spacing": 60,
            "margin_x" : 100,
            "margin_y" : 50
        },
        "shoot": {
            "bullet_speed": 4,
            "prob"        : 0.005,
            "cooldown_ms" : 0
        },
        "weapons": [
            "rocket"
        ],
        "spawn": {
            "y": 60
        }
    },

    # --- Präzisionsschütze ---
    "sniper": {
        "img"   : "assets/images/enemy/sniper.png",
        "size"  : (40, 40),
        "hp"    : 120,
        "points": 30,
        "move"  : {
            "type"       : "grid",
            "amp_frac"   : 0.0,
            "hz"         : 0.0,
            "drop_px"    : 30,
            "speed_start": 2
        },
        "formation": {
            "cols"     : 6,
            "rows"     : 2,
            "h_spacing": 60,
            "v_spacing": 50,
            "margin_x" : 80,
            "margin_y" : 50
        },
        "shoot": {
            "prob"        : 0.015
        },
        "weapons": [
            "laser"
        ],
        "spawn": {
            "y": 60
        }
    },

    # --- Endgegner ---
    "boss": {
        "img"   : "assets/images/enemy/boss.png",
        "size"  : (140, 100),
        "hp"    : 1000,
        "points": 1000,
        "move"  : {
            "type"       : "float",
            "amp_frac"   : 0.20,
            "hz"         : 0.25,
            "drop_px"    : 0,
            "speed_start": 0
        },
        "formation": {
            "cols"     : 1,
            "rows"     : 1,
            "h_spacing": 0,
            "v_spacing": 0,
            "margin_x" : 0,
            "margin_y" : 140
        },
        "aim": {
            "swing_hz"        : 0.30,
            "rotate_deg_per_s": 0.0
        },
        "shoot": {
            "prob": 0.0,
        },
        "weapons": [
            "laser",
            "rocket",
            "nuke"
        ],
        "spawn": {
            "y": 140
        }
    }
}
