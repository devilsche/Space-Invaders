"""
Menu Screen - Isolierte Menu-Logic ohne Game-Dependencies

Verwaltet alle Menu-States:
- Hauptmenü (Start, Highscores, Quit)
- Modus-Auswahl (Normal, Survivor)
- Highscore-Menüs (Normal, Survivor mit Stage-Auswahl)
- Schiff-Auswahl für Survivor Mode

Komplett entkoppelt von der Game-Logic.
"""

import pygame
from system.screens.menu import GameMenu
from manager.asset_manager import AssetManager


class MenuScreen:
    """
    Zentraler Menu-Screen der alle Menu-Funktionalitäten kapselt.

    Verantwortlichkeiten:
    - Menu-Navigation und -States
    - Menu-Musik
    - Highscore-Anzeige
    - Input-Handling für alle Menu-Bereiche
    """

    def __init__(self, assets: AssetManager):
        self.assets = assets

        # Menu-System (nutze die existierende GameMenu-Klasse)
        self.menu = GameMenu()
        self.menu.load_assets(assets)
        self.menu.set_pause_mode(False)

        # Menu-State Tracking
        self.current_menu_state = "main"  # main, mode_select, highscores, etc.

        # Menu-Musik Status
        self.menu_music_playing = False

        # Highscore-bezogene States
        self._survivor_highscore_stage = 1

        # Schiff-Auswahl für Survivor Mode
        self.survivor_selected_stage = 1
        self.survivor_selected_ship = 1

    def start_menu_music(self):
        """Startet die Menu-Musik wenn nicht bereits aktiv"""
        if not self.menu_music_playing:
            self.menu.start_menu_music()
            self.menu_music_playing = True

    def stop_menu_music(self):
        """Stoppt die Menu-Musik"""
        if self.menu_music_playing:
            self.menu.stop_menu_music()
            self.menu_music_playing = False

    def handle_event(self, event) -> str | None:
        """
        Behandelt Menu-Events und gibt Aktionen zurück.

        Args:
            event: pygame.Event

        Returns:
            str | None: Aktion für den AppController oder None
        """
        if event.type != pygame.KEYDOWN:
            return None

        # ESC-Handling je nach Menu-State
        if event.key == pygame.K_ESCAPE:
            return self._handle_escape()

        # Delegiere an das Menu-System
        action = self.menu.handle_input(event)
        return self._process_menu_action(action)

    def _handle_escape(self) -> str | None:
        """Behandelt ESC-Taste je nach aktuellem Menu-State"""
        if self.menu.is_mode_select:
            self.menu.set_mode_select(False)
            self.current_menu_state = "main"
            return None

        elif self.menu.is_highscore_menu:
            self.menu.set_highscore_menu(False)
            self.current_menu_state = "main"
            return None

        elif self.menu.is_survivor_stage_select:
            self.menu.set_survivor_stage_select(False)
            self.menu.set_highscore_menu(True)
            self.current_menu_state = "highscores"
            return None

        else:
            # ESC im Hauptmenü: Spiel beenden
            return "quit"

    def _process_menu_action(self, action) -> str | None:
        """
        Verarbeitet Menu-Aktionen und mappt sie auf App-Controller-Aktionen.

        Args:
            action: Aktion vom GameMenu

        Returns:
            str | None: Aktion für den AppController
        """
        if not action:
            return None

        # Navigation Actions
        if action == "show_mode_select":
            self.menu.set_mode_select(True)
            self.current_menu_state = "mode_select"
            return None

        elif action == "show_highscores":
            self.menu.set_highscore_menu(True)
            self.current_menu_state = "highscores"
            return None

        elif action == "show_survivor_stage_select":
            self.menu.set_survivor_stage_select(True)
            self.current_menu_state = "survivor_stage_select"
            return None

        # Back Actions
        elif action == "back_to_menu":
            self.menu.reset_to_main_menu()
            self.current_menu_state = "main"
            return None

        elif action == "back_to_highscore_menu":
            self.menu.set_survivor_stage_select(False)
            self.menu.set_highscore_menu(True)
            self.current_menu_state = "highscores"
            return None

        # Game Start Actions
        elif action == "start_game":
            self.stop_menu_music()
            return "start_normal"

        elif action == "start_survivor":
            self.stop_menu_music()
            return "start_survivor"

        # Highscore Actions
        elif action == "show_normal_highscores":
            return "show_normal_top10"

        elif action.startswith("show_survivor_highscores_"):
            stage_num = int(action.split("_")[-1])
            self._survivor_highscore_stage = stage_num
            return f"show_survivor_top10_{stage_num}"

        # Quit Action
        elif action == "quit_game":
            return "quit"

        return None

    def update(self, dt: float):
        """
        Updated den Menu-Screen.

        Args:
            dt: Delta time in Sekunden
        """
        # Starte Menu-Musik falls noch nicht aktiv
        if not self.menu_music_playing:
            self.start_menu_music()

        # Menu-System Update (falls nötig)
        # Das GameMenu hat aktuell keine update() Methode
        pass

    def draw(self, screen: pygame.Surface):
        """
        Zeichnet das komplette Menu.

        Args:
            screen: Pygame Surface zum Zeichnen
        """
        self.menu.draw(screen)

    def reset_to_main_menu(self):
        """Setzt das Menu komplett auf den Hauptmenü-State zurück"""
        self.menu.reset_to_main_menu()
        self.current_menu_state = "main"
        self.start_menu_music()

    def cleanup(self):
        """Cleanup beim Beenden der Anwendung"""
        self.stop_menu_music()

        # Falls das GameMenu cleanup benötigt
        if hasattr(self.menu, 'cleanup'):
            self.menu.cleanup()
