"""
App Controller - Zentraler State-Manager für Ironblast

Initialisiert ALLE Komponenten beim Start:
- Assets (bereits in main.py geladen)
- Game-Instanz (das originale Spiel)
- Menu-System
- Firebase-Status
- Manager (Explosion, PowerUp, etc.)

Verwaltet Screen-Übergänge zwischen Menu und Game.
Das originale Game wird direkt genutzt, keine Wrapper!
"""

import pygame
from manager.asset_manager import AssetManager
from game.game import Game

class AppState:
    """Enum-ähnliche Klasse für App-States"""
    LOADING               = "loading"
    MENU                  = "menu"
    PLAYING               = "playing"
    PAUSED                = "paused"
    GAME_OVER             = "game_over"
    TOP10_NORMAL          = "top10_normal"
    TOP10_SURVIVOR        = "top10_survivor"
    SURVIVOR_SHIP_SELECT  = "survivor_ship_select"
    SURVIVOR_STAGE_SELECT = "survivor_stage_select"
    VICTORY               = "victory"


class AppController:
    """
    Zentraler Controller für die gesamte Anwendung.

    Initialisiert ALLES beim Start:
    - Game-Instanz (einmal erstellt, immer wiederverwendet)
    - Menu-System
    - Alle Manager
    - Screen, Clock, Assets (geteilt zwischen Menu und Game)

    Verantwortlichkeiten:
    - Zentrale Initialisierung aller Komponenten
    - State-Management zwischen Menu und Game
    - Globale Settings (Fullscreen, etc.)
    - Screen-Referenz für alle Komponenten
    """

    def __init__(self, assets: AssetManager, screen: pygame.Surface, firebase_available: bool):
        """
        Initialisiert den AppController und ALLE Spiel-Komponenten.

        Args:
            assets: Der AssetManager mit allen geladenen Assets
            screen: Das pygame Display Surface
            firebase_available: Ob Firebase verfügbar ist (einmal geprüft in main.py)
        """
        print("🎮 Initializing AppController - Setting up ALL components...")

        # Core Components (geteilt zwischen Menu und Game)
        self.assets = assets
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True

        # Firebase Status (einmal geprüft, überall verfügbar)
        self.firebase_available = firebase_available
        print(f"   Firebase: {'🌐 ONLINE' if firebase_available else '📴 OFFLINE'}")

        # State Management
        self.current_state  = AppState.MENU
        self.previous_state = None

        # Game-Instanz (EINMAL erstellt, immer wiederverwendet!)
        print("   Creating Game instance...")
        self.game = Game(assets=self.assets)
        self.game.screen = self.screen  # Nutze den gleichen Screen!
        self.game.clock = self.clock    # Nutze die gleiche Clock!
        self.game.online_available = firebase_available
        self.game.app_controller = self  # Rückverweise für Fullscreen etc.
        print("   ✅ Game instance created")

        # Menu-System (nutzt auch den gleichen Screen)
        print("   Creating Menu system...")
        self._menu_screen = None  # Lazy-Load
        print("   ✅ Menu system ready")

        # Globale Display-Settings (geteilt zwischen Menu und Game)
        self.is_fullscreen = False
        self.is_maximized = False
        self.original_size = (1920, 1080)

        print("✅ AppController initialization complete!")

    def get_menu_screen(self):
        """Lazy-Load MenuScreen mit geteiltem Screen"""
        if self._menu_screen is None:
            from system.screens.menu import GameMenu
            self._menu_screen = GameMenu()
            self._menu_screen.load_assets(self.assets)
            self._menu_screen.set_pause_mode(False)
            print("   ✅ Menu screen loaded")
        return self._menu_screen

    def toggle_fullscreen(self):
        """
        Schaltet zwischen Fullscreen und Windowed um.
        Aktualisiert den Screen für ALLE Komponenten (Menu + Game).
        """
        self.is_fullscreen = not self.is_fullscreen

        if self.is_fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            print("✅ Fullscreen: ON")
        else:
            self.screen = pygame.display.set_mode(self.original_size, pygame.RESIZABLE)
            print("❌ Fullscreen: OFF")

        # Aktualisiere Screen-Referenz für Game
        self.game.screen = self.screen

    def toggle_maximize(self):
        """
        Maximiert/Minimiert das Fenster (nur im Windowed Mode).
        Aktualisiert den Screen für ALLE Komponenten (Menu + Game).
        """
        if self.is_fullscreen:
            return  # Nicht im Fullscreen verfügbar

        self.is_maximized = not self.is_maximized

        if self.is_maximized:
            # Hole Bildschirmgröße
            info = pygame.display.Info()
            self.screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.RESIZABLE)
            print("⬆️ Window: MAXIMIZED")
        else:
            self.screen = pygame.display.set_mode(self.original_size, pygame.RESIZABLE)
            print("⬇️ Window: RESTORED")

        # Aktualisiere Screen-Referenz für Game
        self.game.screen = self.screen

    def handle_global_events(self, event):
        """
        Behandelt globale Events (F11, Alt+Enter, etc.)

        Diese Events funktionieren ÜBERALL - im Menu UND im Game!

        Returns:
            bool: True wenn Event behandelt wurde, False sonst
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                self.toggle_maximize()
                return True
            elif event.key == pygame.K_RETURN and (
                pygame.key.get_pressed()[pygame.K_LALT] or
                pygame.key.get_pressed()[pygame.K_RALT]
            ):
                self.toggle_fullscreen()
                return True

        return False

    def transition_to_menu(self):
        """Wechselt zurück zum Menu (wird vom Game aufgerufen)"""
        print("🔄 Transitioning to Menu...")
        self.current_state = AppState.MENU

        # Stoppe Game-Musik
        pygame.mixer.music.stop()

        # Starte Menu-Musik
        menu = self.get_menu_screen()
        menu.start_menu_music()

    def start_game(self, mode: str, stage: int = 1):
        """
        Startet das Spiel im angegebenen Modus.

        Args:
            mode: "normal" oder "survivor"
            stage: Stage-Level für Survivor Mode
        """
        print(f"🎮 Starting Game: {mode} mode, stage {stage}")

        # Stoppe Menu-Musik BEVOR das Spiel startet
        menu = self.get_menu_screen()
        menu.stop_menu_music()
        try:
            pygame.mixer.Channel(29).stop()
        except Exception:
            pass

        self.current_state = AppState.PLAYING

        # Konfiguriere das Game
        self.game.game_mode = mode
        self.game.game_state = "playing"

        if mode == "survivor":
            self.game.survivor_selected_stage = stage
            self.game._start_survivor_mode()
        else:
            self.game._start_new_game()

    def run(self):
        """
        Hauptloop der Anwendung.
        Routet Events und Updates zwischen Menu und Game.
        """
        # Starte Menu-Musik
        menu = self.get_menu_screen()
        menu.start_menu_music()

        while self.running:
            dt = self.clock.tick(60) / 1000.0  # Delta time in Sekunden

            # Event-Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break

                # Globale Events behandeln (funktioniert überall!)
                if self.handle_global_events(event):
                    continue

                # Screen-spezifische Events
                if self.current_state == AppState.MENU:
                    self._handle_menu_events(event)
                elif self.current_state == AppState.PLAYING:
                    self._handle_game_events(event)

            if not self.running:
                break

            # Updates
            if self.current_state == AppState.MENU:
                menu.update(dt)
            elif self.current_state == AppState.PLAYING:
                # Game update - direkt aus dem originalen Game!
                self.game._handle_events()
                self.game._update()

            # Rendering
            if self.current_state == AppState.MENU:
                menu.draw(self.screen)
            elif self.current_state == AppState.PLAYING:
                # Game rendering - direkt aus dem originalen Game!
                self.game._draw()


            pygame.display.flip()

        # Cleanup
        self._cleanup()

    def _handle_menu_events(self, event):
        """Behandelt Menu-Events"""
        menu = self.get_menu_screen()
        action = menu.handle_input(event)

        if not action:
            return

        # Ignoriere "navigate" Actions (nur für Sound-Effekte)
        if action == "navigate":
            return

        print(f"🎯 Menu action received: {action}")

        # Hauptmenü-Aktionen
        if action == "show_mode_select":
            # Spielmodus-Auswahl anzeigen
            menu.set_mode_select(True)

        elif action == "show_highscores":
            # Highscore-Menü anzeigen
            menu.set_highscore_menu(True)

        elif action == "quit_game":
            self.running = False

        # Spielmodus-Auswahl-Aktionen
        elif action == "start_game":
            # Normal Mode starten
            self.start_game("normal")

        elif action == "start_survivor":
            # Survivor Mode starten (erstmal Stage 1)
            self.start_game("survivor", stage=1)

        elif action == "back_to_menu":
            # Zurück zum Hauptmenü
            menu.reset_to_main_menu()

        # Highscore-Menü-Aktionen
        elif action == "show_normal_highscores":
            # TODO: Normal Highscores anzeigen
            print("📊 Show Normal Highscores (TODO)")
            menu.reset_to_main_menu()

        elif action == "show_survivor_stage_select":
            # Survivor Stage-Auswahl anzeigen
            menu.set_survivor_stage_select(True)

        # Survivor Stage-Select-Aktionen (z.B. "show_survivor_highscores_1")
        elif action.startswith("show_survivor_highscores_"):
            # Survivor Highscores für spezifische Stage anzeigen
            stage = int(action.split("_")[-1])
            print(f"📊 Show Survivor Highscores Stage {stage} (TODO)")
            menu.reset_to_main_menu()

        elif action == "back_to_highscore_menu":
            # Von Stage-Select zurück zu Highscore-Menu
            menu.set_highscore_menu(True)

        # Pause-Menü-Aktionen
        elif action == "resume":
            # Zurück zum Spiel
            pass

        elif action == "quit_to_menu":
            # Zurück zum Hauptmenü
            self.transition_to_menu()

        else:
            print(f"⚠️ Unhandled menu action: {action}")

    def _handle_game_events(self, event):
        """Behandelt Game-Events"""
        # ESC für Pause/Menu
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.game.game_state == "playing":
                # Pause
                self.game.paused = not self.game.paused
            elif self.game.game_state in ["game_over", "victory"]:
                # Zurück zum Menu
                self.transition_to_menu()

        # Game Over / Victory → Menu
        if self.game.game_state in ["game_over", "victory"]:
            # Check ob User zurück zum Menu will
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.transition_to_menu()

    def _cleanup(self):
        """Cleanup beim Beenden der Anwendung"""
        print("🔌 App Controller shutting down...")

        # Stoppe alle Sounds/Musik
        pygame.mixer.stop()
        pygame.mixer.music.stop()

        print("✅ Cleanup complete")
