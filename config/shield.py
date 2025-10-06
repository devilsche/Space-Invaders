SHIELD_CONFIG = {
    1: {
        "shield": {
            "sheet": "assets/images/shield2.png",
            "duration": 5000,              # Fallback-Wert
            "cooldown": 7000,
            "cols": 4,
            "rows": 4,
            "fw": 256,
            "fh": 256,
            "scale": 2.5,
            "fps": 20,
            # Health-System Konfiguration
            "health_percentage": 0.5,       # 50% der Schiffs-Health
            "damage_reduction": 0.9,        # 90% Schadensreduktion
            "regen_rate": 0.1,              # 10% Health pro Sekunde Regeneration
            "min_health_percentage": 0.3,   # Mindestens 30% der Schild-Health beim Reaktivieren
            # Stage-abhängige Dauer für normales Q-Shield (in Millisekunden)
            "duration_by_stage": {
                1: 5000,   # 5 Sekunden
                2: 6000,   # 6 Sekunden
                3: 7000,   # 7 Sekunden
                4: 8000    # 8 Sekunden
            }
        }
    },
    2: {
        "shield": {
            "sheet": "assets/images/shield2.png",
            "cols": 4,
            "rows": 4,
            "fw": 256,
            "fh": 256,
            "scale": 2.5,                   # Gleiche Größe wie normales Shield
            "fps": 25,
            # PowerUp Shield Konfiguration - 100% Absorption, 2% Regen
            "health_percentage": 1.0,       # 100% der Schiffs-Health
            "damage_reduction": 1.0,        # 100% Schadensabsorption (kein Durchschlag)
            "regen_rate": 0.02,             # 2% Health pro Sekunde Regeneration
            "min_health_percentage": 1.0,   # Immer bei 100% starten
            # Stage-abhängige Dauer (in Millisekunden)
            "duration_by_stage": {
                1: 8000,   # 8 Sekunden
                2: 10000,  # 10 Sekunden
                3: 12000,  # 12 Sekunden
                4: 15000   # 15 Sekunden
            }
        }
    }
}
