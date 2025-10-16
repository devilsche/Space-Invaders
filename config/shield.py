SHIELD_CONFIG = {
    1: {
        "shield": {
            "sheet"    : "assets/images/shield2.png",
            "duration" : 5000,
            "cooldown" : 7000,
            "cols"     : 4,
            "rows"     : 4,
            "fw"       : 256,
            "fh"       : 256,
            "scale"    : 2.5,
            "fps"      : 20,
            "health_percentage"    : 0.5,
            "damage_reduction"     : 0.9,
            "regen_rate"           : 0.1,
            "min_health_percentage": 0.3,
            "duration_by_stage": {
                1: 5000,
                2: 6000,
                3: 7000,
                4: 8000
            }
        }
    },
    2: {
        "shield": {
            "sheet": "assets/images/shield2.png",
            "cols" : 4                          ,
            "rows" : 4,
            "fw"   : 256,
            "fh"   : 256,
            "scale": 2.5,
            "fps"  : 25,
            "health_percentage"    : 1.0 ,
            "damage_reduction"     : 1.0 ,
            "regen_rate"           : 1.0,
            "min_health_percentage": 1.0 ,

            "duration_by_stage": {
                1: 8000,
                2: 10000,
                3: 12000,
                4: 15000
            }
        }
    }
}
