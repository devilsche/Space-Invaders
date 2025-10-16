#!/usr/bin/env python3
"""
ORIGINAL Space Invaders Spiel - DIREKT AUSFÜHRBAR

Dieses Script startet Ihr originales, funktionierendes Spiel
ohne das neue AppController-System.
"""

import sys
sys.path.insert(0, '.')

from game.game import Game

def main():
    """Startet Ihr originales Spiel direkt"""
    print("🚀 Starting ORIGINAL Space Invaders Game")
    
    # Erstelle und starte das originale Spiel
    game = Game()
    game.run()  # Das läuft Ihr komplettes, funktionierendes Spiel!

if __name__ == "__main__":
    main()
