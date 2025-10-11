"""
Asset loading with AssetManager integration.

This module provides the asset loading functionality using the new AssetManager.
All assets are registered and loaded on-demand (lazy loading).
"""

import pygame
from typing import Any
from config import WIDTH, HEIGHT, SHIP_CONFIG, ENEMY_CONFIG, PROJECTILES_CONFIG, SHIELD_CONFIG
from manager.asset_manager import AssetManager


class AssetProxy:
    """
    Proxy object that behaves like a dict but uses AssetManager internally.
    Provides backward compatibility with old dict-based asset access.
    """

    def __init__(
        self,
        manager: AssetManager
    ):
        self._manager       = manager
        self._special_data  = {}  # For non-asset data like fps values, durations, etc.

    def get(
        self,
        key:     str,
        default: Any = None
    ) -> Any:
        """Get asset with fallback (dict-style)."""
        if key in self._special_data:
            return self._special_data[key]
        try:
            return self._manager.get(key)
        except Exception:
            return default

    def __getitem__(
        self,
        key: str
    ) -> Any:
        """Dict-style access: assets['key']"""
        if key in self._special_data:
            return self._special_data[key]
        return self._manager.get(key)

    def __setitem__(
        self,
        key:   str,
        value: Any
    ) -> None:
        """Allow setting special data (fps, durations, etc.)"""
        self._special_data[key] = value

    def __contains__(
        self,
        key: str
    ) -> bool:
        """Support 'key in assets' checks."""
        return key in self._special_data or key in self._manager._cache or key in self._manager._asset_registry


def load_assets() -> AssetProxy:
    """
    Load and register all game assets using AssetManager.
    Returns an AssetProxy that provides dict-like access.

    Assets are registered but NOT loaded immediately (lazy loading).
    They will be loaded on first access via get() or [].
    """
    manager = AssetManager()
    proxy   = AssetProxy(manager)

    # ===== Background =====
    try:
        manager.register_asset("background_img", "assets/images/background_gpt.png")
        # Load immediately and scale to screen size
        bg = manager.load_image("assets/images/background_gpt.png", (WIDTH, HEIGHT), trim=False)
        manager._cache["background_img"] = bg
    except Exception:
        manager._cache["background_img"] = None

    # ===== Player Ships (all stages) =====
    for stage, cfg in SHIP_CONFIG.items():
        key = f"player_stage{stage}"
        # Register with metadata for lazy loading with correct size
        manager.register_asset(key, cfg["img"])
        # Load immediately with size
        img = manager.load_image(cfg["img"], cfg["size"])
        manager._cache[key] = img

    # ===== Enemies =====
    for name, ecfg in ENEMY_CONFIG.items():
        key = f"enemy_{name}"
        manager.register_asset(key, ecfg["img"])
        img = manager.load_image(ecfg["img"], ecfg["size"])
        manager._cache[key] = img

    # ===== Projectiles (Images, Sounds, Explosions) =====
    for weapon_name, pcfg in PROJECTILES_CONFIG.items():
        # --- Projectile Image ---
        img_key = f"{weapon_name}_img"
        manager.register_asset(img_key, pcfg["img"])
        base_img = manager.load_image(pcfg["img"], pcfg.get("size"))
        manager._cache[img_key] = base_img

        # --- Special: Yellow laser for enemies ---
        if weapon_name == "laser":
            yellow_img     = base_img.copy()
            yellow_overlay = pygame.Surface(base_img.get_size(), pygame.SRCALPHA)
            yellow_overlay.fill((255, 255, 100, 200))
            yellow_img.blit(yellow_overlay, (0, 0), special_flags=pygame.BLEND_MULT)
            manager._cache["laser_yellow_img"] = yellow_img

        # --- Sounds ---
        if pcfg.get("sound_start"):
            key = f"{weapon_name}_sound_start"
            manager.register_asset(key, pcfg["sound_start"])
            try:
                snd = manager.load_sound(pcfg["sound_start"])
                manager._cache[key] = snd
            except Exception:
                manager._cache[key] = None

        if pcfg.get("sound_hit"):
            key = f"{weapon_name}_sound_hit"
            manager.register_asset(key, pcfg["sound_hit"])
            try:
                snd = manager.load_sound(pcfg["sound_hit"])
                manager._cache[key] = snd
            except Exception:
                manager._cache[key] = None

        if pcfg.get("sound_destroy"):
            key = f"{weapon_name}_sound_destroy"
            manager.register_asset(key, pcfg["sound_destroy"])
            try:
                snd = manager.load_sound(pcfg["sound_destroy"])
                manager._cache[key] = snd
            except Exception:
                manager._cache[key] = None

        if pcfg.get("sound_fly"):
            key = f"{weapon_name}_sound_fly"
            manager.register_asset(key, pcfg["sound_fly"])
            try:
                snd = manager.load_sound(pcfg["sound_fly"])
                manager._cache[key] = snd
            except Exception:
                manager._cache[key] = None

        # --- Explosion Frames ---
        ex = pcfg.get("explosion")
        if ex:
            expl_key = f"expl_{weapon_name}"
            manager.register_asset(expl_key, ex["sheet"])
            # Load spritesheet
            frames = manager.load_spritesheet(
                path       = ex["sheet"],
                cols       = ex["cols"],
                rows       = ex["rows"],
                frame_size = (ex["fw"], ex["fh"]),
                scale      = ex.get("scale", 1.0)
            )
            manager._cache[expl_key] = frames

            # Store fps and keep as special data
            proxy[f"expl_{weapon_name}_fps"]  = ex.get("fps", 24)
            proxy[f"expl_{weapon_name}_keep"] = ex.get("keep", None)

    # ===== Music Paths =====
    proxy["music_paths"] = {"raining_bits": "assets/music/raining_bits.ogg"}

    # ===== Shield =====
    scfg   = SHIELD_CONFIG[1]["shield"]
    frames = manager.load_spritesheet(
        path       = scfg["sheet"],
        cols       = scfg["cols"],
        rows       = scfg["rows"],
        frame_size = (scfg["fw"], scfg["fh"]),
        scale      = scfg.get("scale", 1.0)
    )
    manager._cache["shield_frames"] = frames

    # Shield metadata as special data
    proxy["shield_fps"]      = scfg.get("fps")
    proxy["shield_duration"] = scfg.get("duration")
    proxy["shield_cooldown"] = scfg.get("cooldown")
    proxy["shield_scale"]    = scfg.get("scale")

    # Shield sounds
    try:
        snd = manager.load_sound("assets/sound/shieldImpact.mp3")
        manager._cache["shield_hit_sound"] = snd
    except Exception:
        manager._cache["shield_hit_sound"] = None

    try:
        snd = manager.load_sound("assets/sound/shieldActivate.mp3")
        manager._cache["shield_activate_sound"] = snd
    except Exception:
        manager._cache["shield_activate_sound"] = None

    return proxy

