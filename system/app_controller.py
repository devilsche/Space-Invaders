"""
App Controller - Zentraler State-Manager für das Space Invaders Spiel

Verwaltet alle Screen-Übergänge und States:
- Menu States (Hauptmenü, Modus-Auswahl, Highscores)
- Game States (Normal, Survivor, Pause, Game Over)
- Loading States

Trennt sauber Menu-Logic von Game-Logic.
"""

import pygame
from manager.asset_manager import AssetManager

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

    Verantwortlichkeiten:
    - State-Management zwischen verschiedenen Screens
    - Screen-Initialisierung und -Verwaltung
    - Event-Routing an die entsprechenden Screens
    - Globale Settings (Fullscreen, Auflösung, etc.)
    """

    def __init__(self, assets: AssetManager, screen: pygame.Surface):
        # Core Components
        self.assets = assets
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True

        # State Management
        self.current_state  = AppState.MENU
        self.previous_state = None

        # Screen-spezifische Daten
        self.game_mode: str = None
        self.survivor_stage: int = 1
        self.survivor_ship_stage: int = 1

        # Initialisiere Screens (Lazy Loading)
        self._menu_screen      = None
        self._game_screen      = None
        self._loading_screen   = None
        self._game_over_screen = None
        self._victory_screen   = None
        self._top10_screen     = None

        # Globale Settings
        self.is_fullscreen = False
        self.is_maximized = False

    def get_menu_screen(self):
        """Lazy-Load MenuScreen"""
        if self._menu_screen is None:
            from system.screens.menu_screen import MenuScreen
            self._menu_screen = MenuScreen(self.assets)
        return self._menu_screen

    def get_game_screen(self):
        """Lazy-Load GameScreen"""
        if self._game_screen is None:
            from system.screens.game_screen import GameScreen
            self._game_screen = GameScreen(self.assets)
        return self._game_screen

    def get_loading_screen(self):
        """Lazy-Load LoadingScreen"""
        if self._loading_screen is None:
            from system.screens.loading import LoadingScreen
            self._loading_screen = LoadingScreen()
        return self._loading_screen

    # Später implementieren - erst mal nur Menu und Game funktionsfähig machen
    # def get_game_over_screen(self):
    # def get_victory_screen(self):
    # def get_top10_screen(self):

    def transition_to(self, new_state: str, **kwargs):
        """
        Wechselt zu einem neuen State.

        Args:
            new_state: Der neue State (AppState.*)
            **kwargs: Zusätzliche State-spezifische Parameter
        """
        print(f"State transition: {self.current_state} → {new_state}")

        self.previous_state = self.current_state
        self.current_state  = new_state

        # State-spezifische Initialisierung
        if new_state == AppState.PLAYING:
            self.game_mode = kwargs.get('mode', 'normal')
            if self.game_mode == 'survivor':
                self.survivor_stage = kwargs.get('stage', 1)
                self.survivor_ship_stage = kwargs.get('ship_stage', 1)

            # Initialisiere neues Spiel
            game_screen = self.get_game_screen()
            game_screen.start_new_game(self.game_mode, self.survivor_stage, self.survivor_ship_stage)

        elif new_state == AppState.MENU:
            # Zurück zum Menu - stoppe Game-Musik falls nötig
            if self._game_screen:
                self._game_screen.stop_game_music()

            # Starte Menu-Musik
            menu_screen = self.get_menu_screen()
            menu_screen.start_menu_music()

    def handle_global_events(self, event):
        """
        Behandelt globale Events (F11, Alt+Enter, etc.)

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

    def toggle_fullscreen(self):
        """Schaltet zwischen Fullscreen und Windowed um"""
        self.is_fullscreen = not self.is_fullscreen

        if self.is_fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((1920, 1080), pygame.RESIZABLE)

        print(f"Fullscreen: {'ON' if self.is_fullscreen else 'OFF'}")

    def toggle_maximize(self):
        """Maximiert/Minimiert das Fenster"""
        if not self.is_fullscreen:
            self.is_maximized = not self.is_maximized

            if self.is_maximized:
                # Hole Bildschirmgröße
                info = pygame.display.Info()
                self.screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.RESIZABLE)
            else:
                self.screen = pygame.display.set_mode((1920, 1080), pygame.RESIZABLE)

            print(f"Maximized: {'ON' if self.is_maximized else 'OFF'}")

    def run(self):
        """
        Hauptloop der Anwendung.
        Routet Events und Updates an die entsprechenden Screens.
        """
        while self.running:
            dt = self.clock.tick(60) / 1000.0  # Delta time in Sekunden

            # Event-Handling
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                    break

                # Globale Events behandeln
                if self.handle_global_events(event):
                    continue

                # Screen-spezifische Events
                self._handle_screen_events(event)

            if not self.running:
                break

            # Screen-Updates
            self._update_current_screen(dt)

            # Rendering
            self._render_current_screen()

            pygame.display.flip()

        # Cleanup
        self._cleanup()

    def _handle_screen_events(self, event):
        """Routet Events an den aktuellen Screen"""
        if self.current_state == AppState.MENU:
            action = self.get_menu_screen().handle_event(event)
            self._process_menu_action(action)

        elif self.current_state in [AppState.PLAYING, AppState.PAUSED]:
            action = self.get_game_screen().handle_event(event)
            self._process_game_action(action)

        elif self.current_state in [AppState.TOP10_NORMAL, AppState.TOP10_SURVIVOR]:
            self._handle_top10_event(event)

        # Weitere States später implementieren
        # elif self.current_state == AppState.GAME_OVER:
        # elif self.current_state == AppState.VICTORY:

    def _process_menu_action(self, action):
        """Verarbeitet Aktionen vom MenuScreen"""
        if not action:
            return

        if action == "start_normal":
            # Starte das originale Spiel direkt
            self._start_original_game("normal")

        elif action == "start_survivor":
            self.transition_to(AppState.SURVIVOR_SHIP_SELECT)

        elif action.startswith("start_survivor_"):
            # Extrahiere Parameter und starte originales Spiel
            parts = action.split("_")
            stage = int(parts[-2].replace("stage", "")) if len(parts) >= 3 else 1
            ship = int(parts[-1].replace("ship", "")) if len(parts) >= 4 else 1
            self._start_original_game("survivor", stage, ship)

        elif action == "show_normal_top10":
            self.transition_to(AppState.TOP10_NORMAL)

        elif action.startswith("show_survivor_top10"):
            # Extract stage number from action like "show_survivor_top10_3"
            stage_num = int(action.split("_")[-1]) if "_" in action else 1
            self.survivor_stage = stage_num
            self.transition_to(AppState.TOP10_SURVIVOR)

        elif action == "quit":
            self.running = False

    def _start_original_game(self, mode: str, stage: int = 1, ship: int = 1):
        """Startet das originale Spiel direkt ohne Menu - kehrt bei Pause/Game Over zum AppController zurück"""
        from game.game import Game

        print(f"🎮 Starting ORIGINAL Space Invaders: {mode} mode, stage {stage}, ship {ship}")

        # Erstelle und konfiguriere das originale Spiel
        original_game = Game(assets=self.assets)
        
        # WICHTIG: Setze AppController als Return-Point für das originale Game
        original_game.app_controller = self

        # Konfiguriere den Game-Mode
        if mode == "survivor":
            original_game.game_mode = "survivor"
            original_game.survivor_selected_stage = stage
            # Setze Spiel-State direkt auf playing und starte
            original_game.game_state = "playing"
            original_game._start_new_game()
        else:
            original_game.game_mode = "normal"
            # Normal Mode: Auch direkt ins Spiel springen, kein Menu mehr!
            original_game.game_state = "playing"
            original_game._start_new_game()

        # Starte das originale Spiel mit Menu-Skip
        print("🚀 Starting original game in DIRECT mode (no menu)...")
        original_game.run()
        
        # Wenn das originale Spiel zurückkehrt, starte AppController Menu wieder
        print("🔄 Original game finished - returning to AppController menu")
        self.running = True
        self.transition_to(AppState.MENU)

    def _process_game_action(self, action):
        """Verarbeitet Aktionen vom GameScreen"""
        if not action:
            return

        if action == "pause":
            if self.current_state == AppState.PLAYING:
                self.transition_to(AppState.PAUSED)
            elif self.current_state == AppState.PAUSED:
                self.transition_to(AppState.PLAYING)

        elif action == "game_over":
            # Temporär: Zurück zum Menu
            print("Game Over - returning to menu")
            self.transition_to(AppState.MENU)

        elif action == "victory":
            # Temporär: Zurück zum Menu
            print("Victory - returning to menu")
            self.transition_to(AppState.MENU)

        elif action == "back_to_menu":
            self.transition_to(AppState.MENU)

    def _handle_top10_event(self, event):
        """Behandelt Events für Top10-Screens"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                # Zurück zum Menu
                self.transition_to(AppState.MENU)

    def _process_game_over_action(self, action):
        """Verarbeitet Aktionen vom GameOverScreen"""
        if not action:
            return

        if action == "restart":
            # Starte das gleiche Spiel nochmal
            self.transition_to(
                AppState.PLAYING,
                mode=self.game_mode,
                stage=self.survivor_stage,
                ship_stage=self.survivor_ship_stage
            )
        elif action == "back_to_menu":
            self.transition_to(AppState.MENU)
        elif action == "show_highscores":
            if self.game_mode == "normal":
                self.transition_to(AppState.NORMAL_TOP10)
            else:
                self.transition_to(AppState.SURVIVOR_TOP10, stage=self.survivor_stage)

    def _process_victory_action(self, action):
        """Verarbeitet Aktionen vom VictoryScreen"""
        if not action:
            return

        if action == "continue":
            # Nächstes Level oder zurück zum Menu
            self.transition_to(AppState.MENU)
        elif action == "back_to_menu":
            self.transition_to(AppState.MENU)

    def _process_top10_action(self, action):
        """Verarbeitet Aktionen von Top10-Screens"""
        if not action:
            return

        if action == "back_to_menu":
            self.transition_to(AppState.MENU)

    def _update_current_screen(self, dt):
        """Updated den aktuellen Screen"""
        if self.current_state == AppState.MENU:
            self.get_menu_screen().update(dt)

        elif self.current_state in [AppState.PLAYING, AppState.PAUSED]:
            paused = (self.current_state == AppState.PAUSED)
            action = self.get_game_screen().update(dt, paused)
            if action:
                self._process_game_action(action)

        elif self.current_state in [AppState.TOP10_NORMAL, AppState.TOP10_SURVIVOR]:
            # Top10-Screens haben meist kein Update
            pass

        # Weitere States später implementieren
        # elif self.current_state == AppState.GAME_OVER:
        # elif self.current_state == AppState.VICTORY:

    def _render_current_screen(self):
        """Rendert den aktuellen Screen"""
        if self.current_state == AppState.MENU:
            self.get_menu_screen().draw(self.screen)

        elif self.current_state in [AppState.PLAYING, AppState.PAUSED]:
            self.get_game_screen().draw(self.screen)

            # Pause-Overlay
            if self.current_state == AppState.PAUSED:
                self._draw_pause_overlay()

        elif self.current_state in [AppState.TOP10_NORMAL, AppState.TOP10_SURVIVOR]:
            self._draw_top10_screen()

        # Weitere States später implementieren
        # elif self.current_state == AppState.GAME_OVER:
        # elif self.current_state == AppState.VICTORY:

    def _draw_top10_screen(self):
        """Zeichnet die Top10-Screens"""
        # Schwarzer Hintergrund
        self.screen.fill((0, 0, 0))

        # Title
        if self.assets.has("title_font_large"):
            font = self.assets.get("title_font_large")
            if self.current_state == AppState.TOP10_NORMAL:
                title_text = "NORMAL MODE - TOP 10"
            else:
                title_text = f"SURVIVOR MODE - STAGE {self.survivor_stage} - TOP 10"

            title = font.render(title_text, True, (255, 255, 255))
            title_rect = title.get_rect(center=(self.screen.get_width() // 2, 100))
            self.screen.blit(title, title_rect)

        # Placeholder für Highscore-Liste
        if self.assets.has("menu_font_medium"):
            font = self.assets.get("menu_font_medium")

            # Zeige Platzhalter-Text
            placeholder_text = "Highscore-Liste wird geladen..."
            text = font.render(placeholder_text, True, (200, 200, 200))
            text_rect = text.get_rect(center=(self.screen.get_width() // 2, 300))
            self.screen.blit(text, text_rect)

            # Instruktion
            instruction_text = "ESC oder ENTER = Zurück zum Menu"
            instruction = font.render(instruction_text, True, (150, 150, 150))
            instruction_rect = instruction.get_rect(center=(self.screen.get_width() // 2, 500))
            self.screen.blit(instruction, instruction_rect)

    def _draw_pause_overlay(self):
        """Zeichnet das Pause-Overlay"""
        # Semi-transparentes Overlay
        overlay = pygame.Surface(self.screen.get_size())
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # "PAUSED" Text
        if self.assets.has("title_font_large"):
            font = self.assets.get("title_font_large")
            text = font.render("PAUSED", True, (255, 255, 255))
            rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
            self.screen.blit(text, rect)

    def _cleanup(self):
        """Cleanup beim Beenden der Anwendung"""
        print("App Controller shutting down...")

        # Stoppe alle Sounds/Musik
        pygame.mixer.stop()
        pygame.mixer.music.stop()

        # Cleanup Screens
        if self._game_screen:
            self._game_screen.cleanup()
        if self._menu_screen:
            self._menu_screen.cleanup()
