WIDTH              = 1920
HEIGHT             = 1080
FPS                = 60
FONT_SIZE          = 36

# Reference Resolution (Basis für Skalierung) - 1280x720 als perfekte Größe (16:9)
REFERENCE_WIDTH    = 1280
REFERENCE_HEIGHT   = 720

# Scale Factors basierend auf aktueller Auflösung
SCALE_X            = WIDTH / REFERENCE_WIDTH
SCALE_Y            = HEIGHT / REFERENCE_HEIGHT
SCALE_FACTOR       = min(SCALE_X, SCALE_Y)  # Uniform scaling für proportionale Größen
LIVES              = -1
LIVES_COOLDOWN     = 1000
RESPAWN_PROTECTION = 3000
MASTER_VOLUME      = 0.1
MUSIC_VOLUME       = 0.3
SFX_VOLUME         = 0.5
