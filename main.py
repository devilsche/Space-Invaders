"""
Ironblast - Main Entry Point

Neue Architektur mit AppController:
- Saubere Trennung von Menu-Logic und Game-Logic
- Zentrales State-Management
- Modulare Screen-Architektur
"""

import sys
import os
import pygame
from system.screens.loading import Loading
from system.app_controller import AppController
from system.firebase_manager import initialize_firebase
from system.utils import resource_path


def main():
    """Hauptfunktion - Initialisiert und startet die Anwendung"""

    # PyInstaller: Arbeitsverzeichnis auf den Entpack-Ordner setzen
    if getattr(sys, 'frozen', False):
        os.chdir(sys._MEIPASS)

    pygame.init()

    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    icon = pygame.image.load(resource_path("assets/images/player/stage4.png")).convert_alpha()

    pygame.display.set_caption("Ironblast")
    pygame.display.set_icon(icon)

    # Loading Screen - lädt alle Assets
    assets = Loading(screen).run()

    # Firebase Check
    firebase_status = initialize_firebase()

    # App Controller starten
    app = AppController(assets=assets, screen=screen, firebase_available=firebase_status)
    app.is_fullscreen = True

    print("🚀 Starting Ironblast")

    try:
        app.run()
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("👋 Ironblast shutting down")
        pygame.quit()


if __name__ == "__main__":
    main()
