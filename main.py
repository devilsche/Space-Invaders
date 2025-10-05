import pygame
from game import Game

def main():
    # Pygame initialisieren (macht auch Game selbst, aber hier sauber halten)
    pygame.init()

    # Spiel starten
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
