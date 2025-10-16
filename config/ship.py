SHIP_CONFIG = {
    1: {
        "img"   : "assets/images/player/stage1.png",
        "size"  : (40, 40),
        "health": 1000,
        "speed" : 4,
        "weapons": {
            "laser"  : 1,
            "blaster": 1
        },
        "muzzles": {
            "laser"  : [(0, 5)],
            "blaster": [(0, 5)]
        },
        "shield": 0,
    },
    2: {
        "img"   : "assets/images/player/stage2.png",
        "size"  : (40, 40),
        "health": 2000,
        "speed" : 5,
        "weapons": {
            "laser"  : 2,
            "rocket" : 1,
            "blaster": 1
        },
        "muzzles": {
            "laser":  [(-12, 20), (12, 20)],
            "rocket": [(0, 12)],
            "blaster": [(0, 12)]
        },
        "shield": 1,
    },
    3: {
        "img"   : "assets/images/player/stage3.png",
        "size"  : (55, 55),
        "health": 4000,
        "speed" : 7,
        "weapons": {
            "laser"        : 3,
            "rocket"       : 2,
            "homing_rocket": 1,
            "blaster"      : 2,
            "nuke"         : 1
        },
        "muzzles": {
            "laser"        : [(-21, 24), (0, 5), (21, 24)],
            "rocket"       : [(-13, 30), (13, 30)],
            "homing_rocket": [(0, 10)],
            "blaster"      : [(-2, 20), (2, 20)],
            "nuke"         : [(0, 5)]
        },
        "angle": {
            "laser"  :[ -5, 0, 5 ],
            "blaster":[ -10, 10 ]
        },
        "shield": 1,
    },
    4: {
        "img"   : "assets/images/player/stage4.png",
        "size"  : (65, 65),
        "health": 6000,
        "speed" : 6,
        "weapons": {
            "laser"        : 4,
            "rocket"       : 4,
            "homing_rocket": 4,
            "blaster"      : 1,
            "nuke"         : 1
        },
        "muzzles": {
            "laser"        : [(-16, 30), (-16, 28), (16, 28), (16, 30)],
            "rocket"       : [(-28, 45), (-25, 45), (25, 45), (28, 45)],
            "homing_rocket": [(-25, 50), (-23, 50), (23, 50), (25, 50)],
            "blaster"      : [(-5, 15), (5, 15)],
            "nuke"         : [(0, 5)]
        },
        "angle": {
            "laser"        :[ -5, -2, 2, 5 ],
            "rocket"       :[ -9, -5, 5, 9 ],
            "homing_rocket":[ -20, -10, 10, 20 ],
            "blaster"      :[ -10, 10 ]
        },
        "shield": 1,
    },
    5: {
        "img"   : "assets/images/player/millennium_falcon.png",
        "size"  : (70, 70),
        "health": 10000,
        "speed" : 10,
        "weapons": {
            "laser"        : 5,
            "rocket"       : 4,
            "homing_rocket": 2,
            "blaster"      : 2,
            "nuke"         : 1
        },
        "muzzles": {
            "laser"        : [(-9, 4), (-5, 4), (5, 4), (9, 4),(22, 20)],
            "rocket"       : [(-20, 50), (-10, 45), (10, 45), (20, 50)],
            "homing_rocket": [(-10, 30), (10, 30)],
            "blaster"      : [(-10, 45), (10, 45)],
            "nuke"         : [(0, 10)]
        },
        "angle": {
            "laser"  :[ -10, -7, 7, 10, 0 ],
            "rocket" :[ -10, -5, 5, 10 ],
            "homing_rocket":[ -10, 10 ],
            "blaster":[ -10, 10 ]
        },
        "shield": 1,
    }
}
