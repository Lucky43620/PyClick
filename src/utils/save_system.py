"""
Système de sauvegarde/chargement
"""

import json
import os
from pathlib import Path
from typing import Optional, Tuple
import shutil
from src.entities.player import Player

class SaveSystem:
    """Gère la sauvegarde et le chargement du jeu"""

    def __init__(self):
        self.save_dir = Path("saves")
        self.save_dir.mkdir(exist_ok=True)
        self.save_file = self.save_dir / "savegame.json"
        self.auto_save_timer: float = 0.0
        self.auto_save_interval: float = 30.0  # Sauvegarde auto toutes les 30 secondes

    def save_game(self, player: Player, skill_system=None, station_upgrade_system=None) -> bool:
        """
        Sauvegarde le jeu

        Returns:
            True si succès
        """
        try:
            save_data = {
                "version": "1.1",
                "player": player.to_dict()
            }

            # Sauvegarder les skills si fournis
            if skill_system:
                save_data["skills"] = skill_system.to_dict()

            # Sauvegarder les station upgrades si fournis
            if station_upgrade_system:
                save_data["station_upgrades"] = station_upgrade_system.to_dict()

            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)

            print(f"Jeu sauvegardé: {self.save_file}")
            return True

        except Exception as e:
            print(f"ERREUR lors de la sauvegarde: {e}")
            return False

    def load_game(self, data_manager, skill_system=None, station_upgrade_system=None) -> Optional[Player]:
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

            # Charger les skills
            if skill_system and "skills" in save_data:
                skill_system.from_dict(save_data["skills"])

            # Charger les station upgrades
            if station_upgrade_system and "station_upgrades" in save_data:
                station_upgrade_system.from_dict(save_data["station_upgrades"])

            print(f"Jeu chargé: {self.save_file}")
            return player

        except Exception as e:
            print(f"ERREUR lors du chargement: {e}")
            return None

    def has_save(self) -> bool:
        """Vérifie si une sauvegarde existe"""
        return self.save_file.exists()

    def import_save(self, source_path: str) -> Tuple[bool, str]:
        """
        Importe un fichier de sauvegarde externe et le copie dans l'emplacement local.

        Returns:
            (success, message)
        """
        try:
            src = Path(source_path).expanduser()
            if not src.exists():
                return False, f"Fichier introuvable: {src}"

            # Vérifier que le JSON est valide avant de l'écraser
            with open(src, "r", encoding="utf-8") as f:
                json.load(f)

            shutil.copy(src, self.save_file)
            return True, f"Sauvegarde importée depuis {src}"
        except Exception as exc:
            return False, f"Import impossible: {exc}"

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

    def update_auto_save(self, delta_time: float, player: Player, skill_system=None, station_upgrade_system=None):
        """Met à jour le timer de sauvegarde automatique"""
        self.auto_save_timer += delta_time
        if self.auto_save_timer >= self.auto_save_interval:
            self.auto_save_timer = 0.0
            self.save_game(player, skill_system, station_upgrade_system)
