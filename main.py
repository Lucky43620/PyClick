"""
PyClick - Idle RPG Clicker/Crafter
Un monde où la matière garde mémoire
"""

import arcade
from src.core.game import Game

# Configuration de la fenêtre
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
SCREEN_TITLE = "PyClick - Idle RPG"

def main():
    """Point d'entrée principal du jeu"""
    game = Game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()

if __name__ == "__main__":
    main()
