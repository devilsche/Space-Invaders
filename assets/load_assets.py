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

    # ===== Fonts =====
    # Lade spezifische Fonts für verschiedene Bereiche:
    # - Astralight für Titel
    # - White on Black für Menü
    # - Monofonto für HUD/Rest
    
    import os
    try:
        from config.fonts import FONTS
        print("Font config loaded successfully")
    except Exception as e:
        print(f"Error loading font config: {e}")
        # Fallback: Nutze System-Fonts
        FONTS = {
            "title": {"file": None, "sizes": {"huge": 96, "large": 64, "medium": 48}},
            "menu": {"file": None, "sizes": {"large": 48, "normal": 32, "small": 24}},
            "hud": {"file": None, "sizes": {"large": 32, "normal": 24, "small": 20, "tiny": 16}}
        }
    
    # Hilfsfunktion zum Laden mit Fallback
    def load_font_with_fallback(font_path, size, fallback_path=None):
        """Versucht Font zu laden, nutzt Fallback oder System-Font"""
        try:
            if font_path and os.path.exists(font_path):
                font = manager.load_font(font_path, size)
                print(f"  [OK] Loaded: {os.path.basename(font_path)} ({size}px)")
                return font
            elif fallback_path and os.path.exists(fallback_path):
                font = manager.load_font(fallback_path, size)
                print(f"  [OK] Loaded fallback: {os.path.basename(fallback_path)} ({size}px)")
                return font
            else:
                font = manager.load_font(None, size)  # System font
                print(f"  [WARN] Using system font ({size}px)")
                return font
        except Exception as e:
            print(f"  [ERROR] Error loading font: {e}")
            return manager.load_font(None, size)
    
    # Lade Titel-Fonts (Astralight)
    print("Loading title fonts...")
    title_config = FONTS["title"]
    for size_name, size_px in title_config["sizes"].items():
        key = f"title_font_{size_name}"  # z.B. "title_font_huge"
        proxy[key] = load_font_with_fallback(
            title_config["file"], 
            size_px,
            title_config.get("fallback")
        )
    
    # Lade Menü-Fonts (White on Black)
    print("Loading menu fonts...")
    menu_config = FONTS["menu"]
    for size_name, size_px in menu_config["sizes"].items():
        key = f"menu_font_{size_name}"  # z.B. "menu_font_normal"
        proxy[key] = load_font_with_fallback(
            menu_config["file"],
            size_px,
            menu_config.get("fallback")
        )
    
    # Lade HUD-Fonts (Monofonto)
    print("Loading HUD fonts...")
    hud_config = FONTS["hud"]
    for size_name, size_px in hud_config["sizes"].items():
        key = f"hud_font_{size_name}"  # z.B. "hud_font_normal"
        proxy[key] = load_font_with_fallback(
            hud_config["file"],
            size_px,
            hud_config.get("fallback")
        )
    
    # Lade Controls-Fonts (KGRedHands)
    print("Loading controls fonts...")
    controls_config = FONTS["controls"]
    for size_name, size_px in controls_config["sizes"].items():
        key = f"controls_font_{size_name}"  # z.B. "controls_font_normal"
        proxy[key] = load_font_with_fallback(
            controls_config["file"],
            size_px,
            controls_config.get("fallback")
        )
    
    # Backward compatibility: Alte Keys mit Pixel-Größen
    proxy["menu_font_24"] = proxy.get("menu_font_small")
    proxy["menu_font_32"] = proxy.get("menu_font_normal")
    proxy["title_font_48"] = proxy.get("title_font_medium")
    proxy["title_font_64"] = proxy.get("title_font_large")

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

    # Menu sounds
    try:
        snd = manager.load_sound("assets/sound/menu-backghround-sound.mp3")
        manager._cache["menu_background_sound"] = snd
    except Exception:
        manager._cache["menu_background_sound"] = None

    try:
        snd = manager.load_sound("assets/sound/menu-switch.mp3")
        manager._cache["menu_switch_sound"] = snd
    except Exception:
        manager._cache["menu_switch_sound"] = None

    # Powerup sound
    try:
        snd = manager.load_sound("assets/sound/powerup-pickup.mp3")
        manager._cache["powerup_pickup_sound"] = snd
    except Exception:
        manager._cache["powerup_pickup_sound"] = None

    # EMP sound
    try:
        snd = manager.load_sound("assets/sound/emp-fire.mp3")
        manager._cache["emp_fire_sound"] = snd
    except Exception:
        manager._cache["emp_fire_sound"] = None

    # Rocket fly loop sound
    try:
        snd = manager.load_sound("assets/sound/rocket-fly-loop.mp3")
        manager._cache["rocket_fly_loop_sound"] = snd
    except Exception:
        manager._cache["rocket_fly_loop_sound"] = None

    return proxy

