# config/stages.py - Survivor Mode Stage Configuration

STAGE_NAMES = {
    1: "Rookie",
    2: "Veteran",
    3: "Elite",
    4: "Legend"
}

STAGE_SHIPS = {
    1: 1,  # Stage 1 → Ship 1
    2: 2,  # Stage 2 → Ship 2
    3: 3,  # Stage 3 → Ship 3
    4: 4   # Stage 4 → Ship 4
}

def get_stage_name(stage):
    """Gibt den Namen einer Stage zurück"""
    return STAGE_NAMES.get(stage, "Unknown")

def get_stage_ship(stage):
    """Gibt die Ship-ID für eine Stage zurück"""
    return STAGE_SHIPS.get(stage, 1)
