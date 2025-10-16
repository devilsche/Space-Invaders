"""
Game Screen - Wrapper um die echte Game-Klasse

Verbindet das neue AppController-System mit Ihrem funktionierenden Spiel.
"""

import pygame
from manager.asset_manager import AssetManager
from game.game import Game


class GameScreen:
    """
    Game-Screen der Ihr echtes Spiel startet.
    
    Wrapper um die bestehende Game-Klasse mit der neuen Screen-API.
    """

    def __init__(self, assets: AssetManager):
        self.assets = assets
        self.game = None
        self.is_active = False

    def start_new_game(self, mode: str = "normal", stage: int = 1, ship: int = 1):
        """
        Startet Ihr echtes Spiel!
        
        Args:
            mode: "normal" oder "survivor"
            stage: Stage-Nummer (nur für Survivor Mode relevant)
            ship: Schiff-Typ (1-3)
        """
        # Erstelle neue Game-Instanz mit Ihren Assets
        self.game = Game(assets=self.assets)
        
        # Konfiguriere Game-Mode
        if mode == "survivor":
            self.game.game_mode = "survivor"
            self.game.survivor_selected_stage = stage
        else:
            self.game.game_mode = "normal"
            
        # Setze Game-State auf playing
        self.game.game_state = "playing"
        self.game._start_new_game()
        
        self.is_active = True
        print(f"ECHTES SPIEL gestartet! Mode: {mode}, Stage: {stage}, Ship: {ship}")

    def handle_event(self, event) -> str | None:
        """
        Behandelt Game-Events - delegiert an Ihr echtes Spiel.
        
        Args:
            event: pygame.Event
            
        Returns:
            str | None: Aktion für den AppController oder None
        """
        if not self.is_active or not self.game:
            return None
            
        # Verarbeite Event für das echte Spiel
        # Erstelle temporär eine Event-Liste für das Spiel
        pygame.event.clear()
        pygame.event.post(event)
        
        # Prüfe ob das Spiel beendet werden soll
        if not self.game.running or self.game.game_state == "menu":
            return "back_to_menu"
                
        return None

    def update(self, dt: float, paused: bool = False):
        """
        Updated Ihr echtes Spiel.
        
        Args:
            dt: Delta time in Sekunden
            paused: Ob das Spiel pausiert ist
        """
        if not self.is_active or not self.game or paused:
            return None
            
        # Update Ihr echtes Spiel
        if self.game.game_state == "playing" and not self.game.paused:
            # Rufe die Game-Update-Logic auf
            self.game._physics_update()
            self.game._update()
        
        return None

    def draw(self, screen: pygame.Surface):
        """
        Zeichnet Ihr echtes Spiel!
        
        Args:
            screen: Pygame Surface zum Zeichnen
        """
        if not self.is_active or not self.game:
            screen.fill((0, 0, 0))
            return
            
        # Zeichne Ihr echtes Spiel
        self.game._draw()

    def stop_game_music(self):
        """Stoppt die Game-Musik"""
        if self.game:
            # Stoppe Musik über pygame.mixer
            pygame.mixer.music.stop()

    def cleanup(self):
        """Cleanup beim Beenden des Spiels"""
        if self.game:
            self.game.running = False
        self.is_active = False
