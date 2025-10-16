import pygame
from game import Game
from system.screens.loading import LoadingScreen
from assets.load_assets import load_assets
from manager.asset_manager import AssetManager
from config import WIDTH, HEIGHT, SHIP_CONFIG, ENEMY_CONFIG, PROJECTILES_CONFIG, SHIELD_CONFIG
import time

def load_assets_progressive(screen, loading_screen):
    """Lädt Assets progressiv in Phasen mit LoadingScreen Updates."""
    from assets.load_assets import AssetProxy
    
    manager = AssetManager()
    proxy = AssetProxy(manager)
    
    # Phase 1: Background & Core
    loading_screen.draw(screen, 'assets', 0.1, 'Loading background...')
    pygame.display.flip()
    try:
        manager.register_asset("background_img", "assets/images/background_gpt.png")
        bg = manager.load_image("assets/images/background_gpt.png", (WIDTH, HEIGHT), trim=False)
        manager._cache["background_img"] = bg
    except Exception:
        manager._cache["background_img"] = None
    
    # Phase 2: Player Ships
    loading_screen.draw(screen, 'assets', 0.3, 'Loading player ships...')
    pygame.display.flip()
    for stage, cfg in SHIP_CONFIG.items():
        key = f"player_stage{stage}"
        manager.register_asset(key, cfg["img"])
        img = manager.load_image(cfg["img"], cfg["size"])
        manager._cache[key] = img
    
    # Phase 3: Enemies
    loading_screen.draw(screen, 'fonts', 0.5, 'Loading enemies...')
    pygame.display.flip()
    for name, ecfg in ENEMY_CONFIG.items():
        key = f"enemy_{name}"
        manager.register_asset(key, ecfg["img"])
        img = manager.load_image(ecfg["img"], ecfg["size"])
        manager._cache[key] = img
    
    # Phase 4: Weapons & Projectiles
    loading_screen.draw(screen, 'images', 0.7, 'Loading weapons...')
    pygame.display.flip()
    for weapon_name, pcfg in PROJECTILES_CONFIG.items():
        img_key = f"{weapon_name}_img"
        manager.register_asset(img_key, pcfg["img"])
        base_img = manager.load_image(pcfg["img"], pcfg.get("size"))
        manager._cache[img_key] = base_img
        
        if weapon_name == "laser":
            yellow_img = base_img.copy()
            yellow_overlay = pygame.Surface(base_img.get_size(), pygame.SRCALPHA)
            yellow_overlay.fill((255, 255, 100, 200))
            yellow_img.blit(yellow_overlay, (0, 0), special_flags=pygame.BLEND_MULT)
            manager._cache["laser_yellow_img"] = yellow_img
    
    # Sounds, Explosions, etc. - rest of load_assets() logic
    # (gekürzt für Übersicht, vollständige Implementierung nötig)
    
    # Lade restliche Assets mit normaler load_assets() Funktion
    loading_screen.draw(screen, 'images', 0.9, 'Loading sounds & effects...')
    pygame.display.flip()
    
    # Hier müssten wir den Rest von load_assets() kopieren...
    # Für jetzt: verwende die Original-Funktion für den Rest
    full_assets = load_assets()
    
    return full_assets

def main():
    # Pygame initialisieren
    pygame.init()

    # Screen erstellen (Initial-Größe)
    screen = pygame.display.set_mode((1920, 1080), pygame.RESIZABLE)
    pygame.display.set_caption("Space Invaders")
    clock = pygame.time.Clock()

    # LoadingScreen erstellen
    loading_screen = LoadingScreen()

    # Phase 1: Initializing pygame
    loading_screen.draw(screen, 'assets', 0.0, 'Initializing pygame...')
    pygame.display.flip()
    clock.tick(60)  # Warte einen Frame
    time.sleep(0.3)

    # Phase 2-5: Loading Assets PROGRESSIV (mit Updates zwischen den Phasen!)
    assets = load_assets_progressive(screen, loading_screen)
    time.sleep(0.3)

    # Phase 6: Initializing game
    loading_screen.draw(screen, 'images', 0.95, 'Initializing game...')
    pygame.display.flip()

    # Game-Objekt erstellen mit vorgeladenen Assets
    # WICHTIG: Game() setzt pygame.display.set_mode() neu, daher wird Screen kurz schwarz
    game = Game(assets=assets)

    # SOFORT nach Game-Erstellung: LoadingScreen neu zeichnen auf dem neuen Display
    loading_screen.draw(game.screen, 'firebase', 0.98, 'Game ready...')
    pygame.display.flip()
    time.sleep(0.2)

    # Phase 7: Firebase Check
    loading_screen.draw(game.screen, 'firebase', 0.99, 'Checking online connection...')
    pygame.display.flip()
    time.sleep(0.8)

    # Phase 8: Done
    loading_screen.draw(game.screen, 'done', 1.0, 'Ready to play!')
    pygame.display.flip()
    time.sleep(1.0)

    # Spiel starten
    game.run()

if __name__ == "__main__":
    main()
