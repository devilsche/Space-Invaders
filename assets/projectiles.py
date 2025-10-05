# assets/projectiles.py
import pygame
import os
from config.projectiles import PROJECTILES_CONFIG


def load_projectile_assets():
    """
    Lädt Bilder und Sounds basierend auf PROJECTILES_CONFIG.
    Gibt ein Dict zurück, das direkt von den Projectile-Klassen benutzt werden kann.
    """
    assets = {}

    for key, cfg in PROJECTILES_CONFIG.items():
        # Bild laden
        if "img" in cfg and cfg["img"]:
            if os.path.exists(cfg["img"]):
                img = pygame.image.load(cfg["img"]).convert_alpha()
                if "size" in cfg and cfg["size"]:
                    img = pygame.transform.scale(img, cfg["size"])
                assets[f"{key}_img"] = img
            else:
                print(f"[WARN] Missing image for {key}: {cfg['img']}")

        # Sounds laden
        for sound_key in ("sound_start", "sound_hit", "sound_fly"):
            if sound_key in cfg and cfg[sound_key]:
                if os.path.exists(cfg[sound_key]):
                    assets[f"{key}_{sound_key}"] = pygame.mixer.Sound(cfg[sound_key])
                else:
                    print(f"[WARN] Missing sound for {key}: {cfg[sound_key]}")

    return assets
