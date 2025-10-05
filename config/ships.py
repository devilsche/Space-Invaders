SHIP_CONFIG = {
    1: {
        "img": "assets/images/player/stage1.png",
        "size": (40, 40),
        "speed": 4,
        "weapons": {"laser": 1, "rocket": 0, "nuke": 0},
        "muzzles": {
            "laser":  [(0, 5)],
            "rocket": [(0, 5)],
            "nuke":   [(0, 5)]
        }
    },
    2: {
        "img": "assets/images/player/stage2.png",
        "size": (40, 40),
        "speed": 5,
        "weapons": {"laser": 2, "rocket": 1, "nuke": 0},
        "muzzles": {
            "laser":  [(-12, 20), (12, 20)],
            "rocket": [(0, 12)],
            "nuke":   [(0, 14)]
        }
    },
    3: {
        "img": "assets/images/player/stage3.png",
        "size": (55, 55),
        "speed": 7,
        "weapons": {"laser": 3, "rocket": 2, "nuke": 1},
        "muzzles": {
            "laser":  [(0, 5), (-17, 24), (16, 24)],
            "rocket": [(-15, 24), (15, 24)],
            "nuke":   [(0, 5)]
        },
        "angle": {
            "laser":[ -1, 0, 1 ]
        }
    },
    4: {
        "img": "assets/images/player/millennium_falcon.png",
        "size": (70, 70),
        "speed": 10,
        "weapons": {"laser": 5, "rocket": 4, "nuke": 1},
        "muzzles": {
            "laser":  [(-8, 4), (6, 4), (-12, 4), (10, 4),(27, 20)],
            "rocket": [(-16, 20), (16, 20), (-8, 28), (8, 28)],
            "nuke":   [(0, 26)]
        },
        "angle": {
            "laser":[ -3, -1, 1, 3, 0 ]
        }
    }
}
