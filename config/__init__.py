from .enemy import ENEMY_CONFIG
from .weapon import WEAPON_CONFIG, WEAPON_CONFIG, EMP_CONFIG
from .settings import GAME_CONFIG
from .shield import SHIELD_CONFIG
from .ship import SHIP_CONFIG
from .levels import LEVEL_CONFIG, UPGRADE_CONFIG

# Einzelne Settings aus GAME_CONFIG exportieren (Kompatibilität mit game.py etc.)
WIDTH              = GAME_CONFIG["WIDTH"]
HEIGHT             = GAME_CONFIG["HEIGHT"]
FPS                = GAME_CONFIG["FPS"]
FONT_SIZE          = GAME_CONFIG["FONT_SIZE"]
LIVES              = GAME_CONFIG["LIVES"]
LIVES_COOLDOWN     = GAME_CONFIG["LIVES_COOLDOWN"]
RESPAWN_PROTECTION = GAME_CONFIG["RESPAWN_PROTECTION"]
MASTER_VOLUME      = GAME_CONFIG["MASTER_VOLUME"]
MUSIC_VOLUME       = GAME_CONFIG["MUSIC_VOLUME"]
SFX_VOLUME         = GAME_CONFIG["SFX_VOLUME"]
