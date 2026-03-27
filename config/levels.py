# config/levels.py - Level-Definitionen für Normal Mode
#
# Jedes Level hat:
# - name: Anzeigename
# - waves: Liste von Wellen mit Gegner-Zusammensetzung
#   - enemies: Liste von (enemy_type, count) Tupeln
#   - spawn_delay: ms zwischen Spawns innerhalb der Wave
# - boss: Boss-Config am Ende des Levels
# - enemy_hp_multiplier: Skaliert HP aller Gegner
# - spawn_speed_multiplier: Beschleunigt Spawn-Intervall (kleiner = schneller)

LEVEL_CONFIG = {
    1: {
        "name": "First Contact",
        "waves": [
            {"enemies": [("alien", 6), ("drone", 4)], "spawn_delay": 4000},
            {"enemies": [("alien", 8), ("drone", 6)], "spawn_delay": 3500},
            {"enemies": [("alien", 10), ("drone", 5), ("sniper", 2)], "spawn_delay": 3000},
        ],
        "boss": {"type": "boss", "count": 1, "hp_multiplier": 1.0},
        "enemy_hp_multiplier": 1.0,
        "spawn_speed_multiplier": 1.0,
    },
    2: {
        "name": "Rising Threat",
        "waves": [
            {"enemies": [("alien", 10), ("drone", 6), ("sniper", 3)], "spawn_delay": 3500},
            {"enemies": [("tank", 3), ("sniper", 5), ("drone", 8)], "spawn_delay": 3000},
            {"enemies": [("alien", 12), ("tank", 4), ("sniper", 4)], "spawn_delay": 2800},
            {"enemies": [("interceptor", 6), ("drone", 10)], "spawn_delay": 2500},
        ],
        "boss": {"type": "boss", "count": 2, "hp_multiplier": 1.5},
        "enemy_hp_multiplier": 1.3,
        "spawn_speed_multiplier": 0.85,
    },
    3: {
        "name": "Deep Space",
        "waves": [
            {"enemies": [("tank", 5), ("sniper", 6), ("drone", 8)], "spawn_delay": 3000},
            {"enemies": [("interceptor", 8), ("alien", 10), ("sniper", 4)], "spawn_delay": 2500},
            {"enemies": [("tank", 6), ("interceptor", 6), ("drone", 12)], "spawn_delay": 2200},
            {"enemies": [("sniper", 8), ("tank", 4), ("alien", 12)], "spawn_delay": 2000},
        ],
        "boss": {"type": "boss", "count": 2, "hp_multiplier": 2.0},
        "enemy_hp_multiplier": 1.6,
        "spawn_speed_multiplier": 0.7,
    },
    4: {
        "name": "War Zone",
        "waves": [
            {"enemies": [("tank", 6), ("interceptor", 8), ("sniper", 6)], "spawn_delay": 2500},
            {"enemies": [("alien", 15), ("drone", 10), ("tank", 5)], "spawn_delay": 2200},
            {"enemies": [("interceptor", 10), ("sniper", 8), ("tank", 6)], "spawn_delay": 2000},
            {"enemies": [("tank", 8), ("interceptor", 8), ("alien", 12), ("sniper", 6)], "spawn_delay": 1800},
            {"enemies": [("drone", 15), ("interceptor", 10), ("tank", 4)], "spawn_delay": 1500},
        ],
        "boss": {"type": "boss", "count": 3, "hp_multiplier": 2.5},
        "enemy_hp_multiplier": 2.0,
        "spawn_speed_multiplier": 0.6,
    },
    5: {
        "name": "Final Stand",
        "waves": [
            {"enemies": [("tank", 8), ("interceptor", 10), ("sniper", 8)], "spawn_delay": 2000},
            {"enemies": [("alien", 18), ("drone", 12), ("tank", 6), ("sniper", 6)], "spawn_delay": 1800},
            {"enemies": [("interceptor", 12), ("tank", 8), ("sniper", 8), ("drone", 10)], "spawn_delay": 1500},
            {"enemies": [("tank", 10), ("interceptor", 10), ("alien", 15), ("sniper", 8)], "spawn_delay": 1300},
            {"enemies": [("interceptor", 15), ("tank", 8), ("sniper", 10), ("drone", 15)], "spawn_delay": 1000},
        ],
        "boss": {"type": "boss", "count": 3, "hp_multiplier": 3.5},
        "enemy_hp_multiplier": 2.5,
        "spawn_speed_multiplier": 0.5,
    },
}

# Upgrade-Kosten (Score-Punkte)
UPGRADE_CONFIG = {
    "next_ship": {
        "name": "Ship Upgrade",
        "description": "Upgrade to next ship stage",
        "base_cost": 2000,
        "cost_multiplier": 1.5,
        "max_level": 3,  # Stage 1→2→3→4 (max 3 upgrades)
    },
    "extra_life": {
        "name": "Extra Life",
        "description": "+1 Life",
        "base_cost": 1500,
        "cost_multiplier": 2.0,
        "max_level": 3,
        "effect": 1,
    },
    "damage": {
        "name": "Firepower",
        "description": "+20% Weapon Damage",
        "base_cost": 800,
        "cost_multiplier": 1.8,
        "max_level": 5,
        "effect": 0.20,
    },
    "fire_rate": {
        "name": "Rapid Fire",
        "description": "-15% Cooldown",
        "base_cost": 600,
        "cost_multiplier": 1.6,
        "max_level": 4,
        "effect": 0.15,
    },
    "emp_charges": {
        "name": "EMP Charges",
        "description": "+3 EMP Charges",
        "base_cost": 400,
        "cost_multiplier": 1.3,
        "max_level": 5,
        "effect": 3,
    },
    "shield_duration": {
        "name": "Shield Duration",
        "description": "+25% Shield Duration",
        "base_cost": 700,
        "cost_multiplier": 1.5,
        "max_level": 4,
        "effect": 0.25,
    },
}
