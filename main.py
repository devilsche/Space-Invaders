"""
Space Invaders - Main Entry Point

Neue Architektur mit AppController:
- Saubere Trennung von Menu-Logic und Game-Logic
- Zentrales State-Management
- Modulare Screen-Architektur
"""

import pygame
import time
from system.screens.loading import LoadingScreen
from assets.load_assets import load_assets
from system.app_controller import AppController
from system.firebase_manager import initialize_firebase


def main():
    """Hauptfunktion - Initialisiert und startet die Anwendung"""
    # Pygame initialisieren
    pygame.init()

    # Screen erstellen (Initial-Größe)
    screen = pygame.display.set_mode((1920, 1080), pygame.RESIZABLE)
    pygame.display.set_caption("Space Invaders - New Architecture")
    clock = pygame.time.Clock()

    # LoadingScreen erstellen
    loading_screen = LoadingScreen()

    # Phase 1: Initializing pygame
    loading_screen.draw(screen, 'assets', 0.0, 'Initializing pygame...')
    pygame.display.flip()
    clock.tick(60)  # Warte einen Frame
    time.sleep(0.3)

    # Phase 2: Loading Assets
    loading_screen.draw(screen, 'assets', 0.5, 'Loading game assets...')
    pygame.display.flip()
    assets = load_assets()
    time.sleep(0.3)

    # Phase 3: Firebase Check - ZENTRALE EINMALIGE PRÜFUNG
    loading_screen.draw(screen, 'firebase', 0.8, 'Checking online connection...')
    pygame.display.flip()
    
    # Zentrale Firebase-Verfügbarkeitsprüfung
    firebase_status = initialize_firebase()
    
    if firebase_status:
        loading_screen.draw(screen, 'firebase', 0.9, '✅ Online features available')
    else:
        loading_screen.draw(screen, 'firebase', 0.9, '⚠️ Offline mode - local saves only')
    pygame.display.flip()
    time.sleep(0.5)

    # Phase 4: Initialisiere App Controller
    loading_screen.draw(screen, 'done', 0.95, 'Initializing app controller...')
    pygame.display.flip()
    
    # Erstelle App Controller (neue Architektur!)
    app = AppController(assets=assets, screen=screen)
    
    # Phase 5: Done
    loading_screen.draw(screen, 'done', 1.0, 'Ready to play!')
    pygame.display.flip()
    time.sleep(0.8)

    print("🚀 Starting Space Invaders with new architecture (AppController + Screens)")
    
    # Starte Anwendung mit der neuen Architektur
    try:
        app.run()
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("👋 Space Invaders shutting down")
        pygame.quit()


if __name__ == "__main__":
    main()
