"""
Système de sauvegarde/chargement
"""

import json
import os
from pathlib import Path
from typing import Optional
from src.entities.player import Player

class SaveSystem:
    """Gère la sauvegarde et le chargement du jeu"""

    def __init__(self):
        self.save_dir = Path("saves")
        self.save_dir.mkdir(exist_ok=True)
        self.save_file = self.save_dir / "savegame.json"
        self.auto_save_timer: float = 0.0
        self.auto_save_interval: float = 30.0  # Sauvegarde auto toutes les 30 secondes

    def save_game(self, player: Player) -> bool:
        """
        Sauvegarde le jeu

        Returns:
            True si succès
        """
        try:
            save_data = {
                "version": "1.0",
                "player": player.to_dict()
            }

            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)

            print(f"Jeu sauvegardé: {self.save_file}")
            return True

        except Exception as e:
            print(f"ERREUR lors de la sauvegarde: {e}")
            return False

    def load_game(self, data_manager) -> Optional[Player]:
        """
        Charge le jeu

        Returns:
            Player si succès, None sinon
        """
        if not self.save_file.exists():
            print("Aucune sauvegarde trouvée")
            return None

        try:
            with open(self.save_file, 'r', encoding='utf-8') as f:
                save_data = json.load(f)

            player = Player.from_dict(save_data["player"], data_manager)
            print(f"Jeu chargé: {self.save_file}")
            return player

        except Exception as e:
            print(f"ERREUR lors du chargement: {e}")
            return None

    def has_save(self) -> bool:
        """Vérifie si une sauvegarde existe"""
        return self.save_file.exists()

    def delete_save(self) -> bool:
        """Supprime la sauvegarde"""
        try:
            if self.save_file.exists():
                os.remove(self.save_file)
                print("Sauvegarde supprimée")
            return True
        except Exception as e:
            print(f"ERREUR lors de la suppression: {e}")
            return False

    def update_auto_save(self, delta_time: float, player: Player):
        """Met à jour le timer de sauvegarde automatique"""
        self.auto_save_timer += delta_time
        if self.auto_save_timer >= self.auto_save_interval:
            self.auto_save_timer = 0.0
            self.save_game(player)
