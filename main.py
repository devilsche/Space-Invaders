"""
Space Invaders - Main Entry Point

Neue Architektur mit AppController:
- Saubere Trennung von Menu-Logic und Game-Logic
- Zentrales State-Management
- Modulare Screen-Architektur
"""

import pygame
import time
from system.screens.loading import Loading
from system.app_controller import AppController
from system.firebase_manager import initialize_firebase

def main():
    """Hauptfunktion - Initialisiert und startet die Anwendung"""

    pygame.init()

    screen = pygame.display.set_mode((1920, 1080), pygame.RESIZABLE)
    clock  = pygame.time.Clock()
    icon   = pygame.image.load("assets/images/player/stage4.png").convert_alpha()

    pygame.display.set_caption( "Nova Strike" )
    pygame.display.set_icon(icon)


    # LoadingScreen erstellen
    assets = Loading(screen).run()
    clock.tick(60)
    time.sleep(5)
    pygame.quit()

    # # Phase 1: Initializing pygame
    # loading_screen.draw(screen, 'assets', 0.0, 'Initializing pygame...')
    # pygame.display.flip()
    # clock.tick(60)  # Warte einen Frame
    # time.sleep(0.3)

    # # Phase 2: Loading Assets
    # loading_screen.draw(screen, 'assets', 0.5, 'Loading game assets...')
    # pygame.display.flip()
    # assets = load_assets()
    # time.sleep(0.3)

    # # Phase 3: Firebase Check - ZENTRALE EINMALIGE PRÜFUNG
    # loading_screen.draw(screen, 'firebase', 0.8, 'Checking online connection...')
    # pygame.display.flip()

    # # Zentrale Firebase-Verfügbarkeitsprüfung
    # firebase_status = initialize_firebase()

    # if firebase_status:
    #     loading_screen.draw(screen, 'firebase', 0.9, '✅ Online features available')
    # else:
    #     loading_screen.draw(screen, 'firebase', 0.9, '⚠️ Offline mode - local saves only')
    # pygame.display.flip()
    # time.sleep(0.5)

    # # Phase 4: Initialisiere App Controller
    # loading_screen.draw(screen, 'done', 0.95, 'Initializing app controller...')
    # pygame.display.flip()

    # # Erstelle App Controller (neue Architektur!)
    # # Übergebe Assets, Screen UND Firebase-Status
    # app = AppController(assets=assets, screen=screen, firebase_available=firebase_status)

    # # Phase 5: Done
    # loading_screen.draw(screen, 'done', 1.0, 'Ready to play!')
    # pygame.display.flip()
    # time.sleep(0.8)

    # print("🚀 Starting Space Invaders with new architecture (AppController + Screens)")

    # Starte Anwendung mit der neuen Architektur
    # try:
    #     app.run()
    # except Exception as e:
    #     print(f"Application error: {e}")
    #     import traceback
    #     traceback.print_exc()
    # finally:
    #     print("👋 Space Invaders shutting down")
    #     pygame.quit()


if __name__ == "__main__":
    main()
