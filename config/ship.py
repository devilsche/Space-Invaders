SHIP_CONFIG = {
    1: {
        "img": "assets/images/player/stage1.png",
        "size": (40, 40),
        "health": 1000,
        "speed": 4,
        "weapons": {"laser": 1, "rocket": 0, "nuke": 0},
        "muzzles": {
            "laser":  [(0, 5)],
            "rocket": [(0, 5)],
            "nuke":   [(0, 5)]
        },
        "shield": 0,
    },
    2: {
        "img": "assets/images/player/stage2.png",
        "size": (40, 40),
        "health": 2000,
        "speed": 5,
        "weapons": {"laser": 2, "rocket": 1, "nuke": 0},
        "muzzles": {
            "laser":  [(-12, 20), (12, 20)],
            "rocket": [(0, 12)],
            "nuke":   [(0, 14)]
        },
        "shield": 1,
    },
    3: {
        "img": "assets/images/player/stage3.png",
        "size": (55, 55),
        "health": 4000,
        "speed": 7,
        "weapons": {"laser": 3, "rocket": 2, "homing_rocket": 1, "blaster": 1, "nuke": 1},
        "muzzles": {
            "laser":  [(-17, 24), (0, 5), (16, 24)],
            "rocket": [(-15, 24), (15, 24)],
            "homing_rocket": [(0, 8)],
            "blaster": [(0, 15)],
            "nuke":   [(0, 5)]
        },
        "angle": {
            "laser":[ -5, 0, 5 ]
        },
        "shield": 1,
    },
    4: {
        "img": "assets/images/player/millennium_falcon.png",
        "size": (70, 70),
        "health": 10000,
        "speed": 10,
        "weapons": {"laser": 5, "rocket": 4, "homing_rocket": 2, "blaster": 2, "nuke": 1},
        "muzzles": {
            "laser"        : [(-12, 4), (-8, 4), (6, 4), (10, 4),(27, 20)],
            "rocket"       : [(-25, 50), (-8, 45), (8, 45), (25, 50)],
            "homing_rocket": [(-10, 30), (10, 30)],
            "blaster"      : [(-10, 35), (10, 35)],
            "nuke"         : [(0, 10)]
        },
        "angle": {
            "laser":[ -10, -7, 7, 10, 0 ],
            "rocket":[ -7, -5, 5, 7 ],
            "blaster":[ -10, 10 ]
        },
        "shield": 1,
    }
}
