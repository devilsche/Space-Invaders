# system/screens/__init__.py - Screen System Module
"""
Screens Module - Alle UI-Bildschirme und Menüs

Enthält:
- menu.py: Haupt- und Pausenmenü mit zentralen Rendering-Methoden
- survivor_screens.py: Survivor Mode spezifische Screens (Game Over, Name Input)
- game_over.py: Unified Game Over Screen für beide Modi
- top10_normal.py: Normal Mode Top 10 Leaderboard
- top10_survivor.py: Survivor Mode Top 10 Leaderboard (stage-specific)
- loading.py: Startup Loading Screen
- victory_screen.py: Siegesbildschirm nach Level-Abschluss
- ship_select.py: Schiffsauswahl für Survivor Mode
"""

from .menu import GameMenu
from .survivor_screens import SurvivorGameOverScreen, SurvivorNameInputScreen
from .game_over import GameOverScreen
from .top10_normal import NormalTop10Screen
from .top10_survivor import SurvivorTop10Screen
from .loading import Loading
from .victory_screen import VictoryScreen
from .ship_select import ShipSelectScreen

__all__ = [
    'GameMenu',
    'SurvivorGameOverScreen',
    'SurvivorNameInputScreen',
    'GameOverScreen',
    'NormalTop10Screen',
    'SurvivorTop10Screen',
    'LoadingScreen',
    'VictoryScreen',
    'ShipSelectScreen'
]
