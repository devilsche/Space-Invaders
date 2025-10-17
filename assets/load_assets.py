"""
Asset loading with AssetManager integration.

This module provides the asset loading functionality using the new AssetManager.
All assets are registered and loaded on-demand (lazy loading).
"""

import pygame
from config import SHIP_CONFIG, ENEMY_CONFIG, WEAPON_CONFIG, SHIELD_CONFIG
from config.settings import GAME_CONFIG
from manager.asset_manager import AssetManager

import os

# AssetProxy entfernt - verwende direkt AssetManager


def load_assets() -> AssetManager:
    """
    Load and register all game assets using AssetManager.
    Returns the AssetManager directly for modern usage.

    Assets are registered but NOT loaded immediately (lazy loading).
    They will be loaded on first access via get() or [].
    """
    manager = AssetManager()

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
    for weapon_name, pcfg in WEAPON_CONFIG.items():
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

            # Store fps and keep as configuration data
            manager.set(f"expl_{weapon_name}_fps", ex.get("fps", 24))
            manager.set(f"expl_{weapon_name}_keep", ex.get("keep", None))

    # ===== Music Paths =====
    manager.set("music_paths", {"raining_bits": "assets/music/raining_bits.ogg"})

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

    # Shield metadata as configuration data
    manager.set("shield_fps", scfg.get("fps"))
    manager.set("shield_duration", scfg.get("duration"))
    manager.set("shield_cooldown", scfg.get("cooldown"))
    manager.set("shield_scale", scfg.get("scale"))

    # ===== Fonts =====
    # Lade spezifische Fonts für verschiedene Bereiche:
    # - Astralight für Titel
    # - White on Black für Menü
    # - Monofonto für HUD/Rest


    try:
        from config.fonts import FONTS
        print("Font config loaded successfully")
    except Exception as e:
        print(f"Error loading font config: {e}")
        # Fallback: Nutze System-Fonts
        FONTS = {
            "title": {"file": None, "sizes": {"huge" : 96, "large" : 64, "medium": 48}},
            "menu":  {"file": None, "sizes": {"large": 48, "normal": 32, "small": 24}},
            "hud":   {"file": None, "sizes": {"large": 32, "normal": 24, "small": 20, "tiny": 16}}
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
        manager.set(key, load_font_with_fallback(
            title_config["file"],
            size_px,
            title_config.get("fallback")
        ))

    # Lade Menü-Fonts (White on Black)
    print("Loading menu fonts...")
    menu_config = FONTS["menu"]
    for size_name, size_px in menu_config["sizes"].items():
        key = f"menu_font_{size_name}"  # z.B. "menu_font_normal"
        manager.set(key, load_font_with_fallback(
            menu_config["file"],
            size_px,
            menu_config.get("fallback")
        ))

    # Lade HUD-Fonts (Monofonto)
    print("Loading HUD fonts...")
    hud_config = FONTS["hud"]
    for size_name, size_px in hud_config["sizes"].items():
        key = f"hud_font_{size_name}"  # z.B. "hud_font_normal"
        manager.set(key, load_font_with_fallback(
            hud_config["file"],
            size_px,
            hud_config.get("fallback")
        ))

    # Lade Controls-Fonts (KGRedHands)
    print("Loading controls fonts...")
    controls_config = FONTS["controls"]
    for size_name, size_px in controls_config["sizes"].items():
        key = f"controls_font_{size_name}"  # z.B. "controls_font_normal"
        manager.set(key, load_font_with_fallback(
            controls_config["file"],
            size_px,
            controls_config.get("fallback")
        ))

    # Backward compatibility: Alte Keys mit Pixel-Größen
    manager.set("menu_font_24", manager.get("menu_font_small"))
    manager.set("menu_font_32", manager.get("menu_font_normal"))
    manager.set("title_font_48", manager.get("title_font_medium"))
    manager.set("title_font_64", manager.get("title_font_large"))

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



    # Title fonts (Astralight)
    try:
        manager._cache["font_title_huge"] = pygame.font.Font(FONT_ASTRALIGHT, 120)
        manager._cache["font_title_large"] = pygame.font.Font(FONT_ASTRALIGHT, 80)
        manager._cache["font_title_medium"] = pygame.font.Font(FONT_ASTRALIGHT, 60)
    except:
        manager._cache["font_title_huge"] = pygame.font.Font(None, 120)
        manager._cache["font_title_large"] = pygame.font.Font(None, 80)
        manager._cache["font_title_medium"] = pygame.font.Font(None, 60)

    # Subtitle fonts (White On Black)
    try:
        manager._cache["font_subtitle_large"] = pygame.font.Font(FONT_WHITE_ON_BLACK, 50)
        manager._cache["font_subtitle_medium"] = pygame.font.Font(FONT_WHITE_ON_BLACK, 40)
        manager._cache["font_subtitle_small"] = pygame.font.Font(FONT_WHITE_ON_BLACK, 32)
    except:
        manager._cache["font_subtitle_large"] = pygame.font.Font(None, 50)
        manager._cache["font_subtitle_medium"] = pygame.font.Font(None, 40)
        manager._cache["font_subtitle_small"] = pygame.font.Font(None, 32)

    # Monospace fonts (monofonto rg)
    try:
        manager._cache["font_mono_large"] = pygame.font.Font(FONT_MONOFONTO, 70)
        manager._cache["font_mono_medium"] = pygame.font.Font(FONT_MONOFONTO, 60)
        manager._cache["font_mono_normal"] = pygame.font.Font(FONT_MONOFONTO, 32)
        manager._cache["font_mono_small"] = pygame.font.Font(FONT_MONOFONTO, 28)
        manager._cache["font_mono_tiny"] = pygame.font.Font(FONT_MONOFONTO, 24)
        manager._cache["font_mono_micro"] = pygame.font.Font(FONT_MONOFONTO, 14)
    except:
        manager._cache["font_mono_large"] = pygame.font.Font(None, 70)
        manager._cache["font_mono_medium"] = pygame.font.Font(None, 60)
        manager._cache["font_mono_normal"] = pygame.font.Font(None, 32)
        manager._cache["font_mono_small"] = pygame.font.Font(None, 28)
        manager._cache["font_mono_tiny"] = pygame.font.Font(None, 24)
        manager._cache["font_mono_micro"] = pygame.font.Font(None, 14)

    # Controls fonts (KGRedHands)
    try:
        manager._cache["font_controls_normal"] = pygame.font.Font(FONT_KGREDHANDS, 24)
        manager._cache["font_controls_small"] = pygame.font.Font(FONT_KGREDHANDS, 20)
    except:
        manager._cache["font_controls_normal"] = pygame.font.Font(None, 24)
        manager._cache["font_controls_small"] = pygame.font.Font(None, 20)

    # System fonts (None/default)
    manager._cache["font_system_large"]  = pygame.font.Font(None, 60)
    manager._cache["font_system_medium"] = pygame.font.Font(None, 40)
    manager._cache["font_system_normal"] = pygame.font.Font(None, 32)
    manager._cache["font_system_small"]  = pygame.font.Font(None, 28)

    return manager

def load_fonts(assets: AssetManager) -> AssetManager:
    """
    Load and register only fonts using AssetManager.
    Returns the AssetManager directly for modern usage.

    Assets are registered but NOT loaded immediately (lazy loading).
    They will be loaded on first access via get() or [].
    """
    manager = assets

    try:
        from config.fonts import FONTS
        print("Font config loaded successfully")
    except Exception as e:
        print(f"Error loading font config: {e}")
        FONTS = {
            "title"   : {"file": None, "sizes": {"huge" : 180, "large" : 120, "medium": 90}},
            "menu"    : {"file": None, "sizes": {"large": 96, "normal": 64, "small": 48}},
            "hud"     : {"file": None, "sizes": {"large": 32, "normal": 24, "small": 20, "tiny": 16}},
            "controls": {"file": None, "sizes": {"large": 48, "normal": 36, "small": 28}}
        }

    for category, config in FONTS.items():
        font_path = config["file"]

        for size_name, size_px in config["sizes"].items():
            key = f"font_{category}_{size_name}"

            try:
                font = manager.load_font(font_path, size_px)
                manager._cache[key] = font
                if font_path:
                    print(f"  [OK] {key}: {font_path} ({size_px}px)")
                else:
                    print(f"  [FALLBACK] {key}: System font ({size_px}px)")
            except:
                font = manager.load_font(None, size_px)
                manager._cache[key] = font
                print(f"  [FALLBACK] {key}: System font ({size_px}px)")

    return manager

def load_settings(assets: AssetManager) -> AssetManager:
    manager = assets
    print("Loading game settings...")
    for key, value in GAME_CONFIG.items():
        print(f"  [OK] {key}: {value}")
        manager.set(key, value)

    return manager

def load_ships(assets: AssetManager) -> AssetManager:
    manager = assets
    print("Loading ship assets...")
    for ship_number, ship in SHIP_CONFIG.items():
        img = manager.load_image(ship["img"], ship["size"])
        manager._cache[f"ship_{ship_number}_img"] = img
        print(f"  [OK] ship_{ship_number}: {ship['img']} {ship['size']} loaded... [CACHE]")

        for entry, value in ship.items():
            manager.set(f"ship_{ship_number}_{entry}", value)
            print(f"      [OK] ship_{ship_number}_{entry}: {value}")


        # entries = ('health','speed','shield')
        # for entry in entries:
        #     manager.set(f"ship_{ship_number}_{entry}", ship[entry])
        #     print(f"      [OK] ship_{ship_number}_{entry}: {ship[entry]}")

        #     deep_entries = ('weapons', 'muzzles', 'angle')
        #     for entry in deep_entries:
        #         if entry in ship:
        #             for deep_entry in ship[entry]:
        #                 manager.set(f"ship_{ship_number}_{entry}_{deep_entry}", ship[entry][deep_entry])
        #                 print(f"      [OK] ship_{ship_number}_{entry}_{deep_entry}: {ship[entry][deep_entry]}")

    return manager

def load_enemies(assets: AssetManager) -> AssetManager:
    manager = assets
    print("Loading enemy assets...")
    for enema_name, enemy in ENEMY_CONFIG.items():
        img = manager.load_image(enemy["img"], enemy["size"])
        manager._cache[f"enemy_{enema_name}_img"] = img
        print(f"  [OK] enemy_{enema_name}: {enemy['img']} {enemy['size']} loaded... [CACHE]")

        for entry, value in enemy.items():
            if entry != "img":  # Bild wurde bereits geladen
                manager.set(f"enemy_{enema_name}_{entry}", value)
                print(f"      [OK] enemy_{enema_name}_{entry}: {value}")

    return manager

def load_stages(assets: AssetManager) -> AssetManager:
    manager = assets
    print("Loading stage assets...")
    # Hier können spezifische Ladebefehle für Level-Assets hinzugefügt werden
    return manager

def load_weapons(assets: AssetManager) -> AssetManager:
    manager = assets
    print("Loading weapon assets...")
    # Hier können spezifische Ladebefehle für Waffen-Assets hinzugefügt werden
    return manager

def load_shields(assets: AssetManager) -> AssetManager:
    manager = assets
    print("Loading shield assets...")
    # Hier können spezifische Ladebefehle für Schild-Assets hinzugefügt werden
    return manager

def load_powerups(assets: AssetManager) -> AssetManager:
    manager = assets
    print("Loading power-up assets...")
    # Hier können spezifische Ladebefehle für Power-Up-Assets hinzugefügt werden
    return manager

def load_backgrounds(assets: AssetManager) -> AssetManager:
    manager = assets
    print("Loading background assets...")
    # Hier können spezifische Ladebefehle für Hintergrund-Assets hinzugefügt werden
    return manager

def load_explosions(assets: AssetManager) -> AssetManager:
    manager = assets
    print("Loading explosion assets...")
    # Hier können spezifische Ladebefehle für Explosions-Assets hinzugefügt werden
    return manager

def load_database(assets: AssetManager) -> AssetManager:
    manager = assets
    print("Loading database assets...")
    # Hier können spezifische Ladebefehle für Datenbank-Assets hinzugefügt werden
    return manager
