STAGE_NAMES = {
    1: "Rookie",
    2: "Veteran",
    3: "Elite",
    4: "Legend",
    5: "Mythic"
}

# Mapping von Stage zu Ship-ID
STAGE_SHIPS = {
    1: 1,
    2: 2,
    3: 3,
    4: 4,
    5: 5
}

def get_stage_name(stage):
    """Gibt den Namen einer Stage zurück"""
    return STAGE_NAMES.get(stage, "Unknown")

def get_stage_ship(stage):
    """Gibt die Ship-ID für eine Stage zurück"""
    return STAGE_SHIPS.get(stage, 1)
