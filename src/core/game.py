"""
Game Core - Orchestre tous les systèmes du jeu
"""

import arcade
from src.core.data_manager import DataManager
from src.entities.player import Player
from src.systems.item_system import ItemGenerator
from src.systems.combat_system import CombatSystem
from src.systems.gathering_system import GatheringSystem
from src.systems.crafting_system import CraftingSystem
from src.systems.skill_system import SkillSystem, StationUpgradeSystem
from src.utils.save_system import SaveSystem
from src.ui.game_view import GameView
from src.core.difficulty import DifficultySettings

class Game(arcade.Window):
    """Classe principale du jeu"""

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        # Initialisation des systèmes
        self.data_manager = DataManager()
        self.data_manager.load_all()

        self.difficulty = DifficultySettings()
        self.item_generator = ItemGenerator(self.data_manager)
        self.combat_system = CombatSystem(self.data_manager, self.item_generator, self.difficulty)
        self.gathering_system = GatheringSystem(self.data_manager, self.difficulty)
        self.crafting_system = CraftingSystem(self.data_manager, self.item_generator, self.difficulty)
        self.skill_system = SkillSystem(self.data_manager)
        self.station_upgrade_system = StationUpgradeSystem(self.data_manager)
        self.save_system = SaveSystem()

        # Player
        self.player = None

        # Afficher le menu principal
        self.menu_view = None
        self._show_menu()

        arcade.set_background_color(arcade.color.BLACK)

    def _show_menu(self, message: str = ""):
        """Affiche la vue de menu principal"""
        from src.ui.menu_view import MenuView
        self.menu_view = MenuView(self, self.save_system, message)
        self.show_view(self.menu_view)

    def start_new_game(self):
        """Démarre une nouvelle partie et écrase l'ancienne sauvegarde"""
        self.save_system.delete_save()
        self._init_player(force_new=True)
        self._show_game_view()

    def continue_game(self):
        """Charge la partie existante si disponible"""
        if not self.save_system.has_save():
            self._show_menu("Aucune sauvegarde trouvée")
            return

        self._init_player(force_new=False)
        if not self.player:
            self._show_menu("Chargement impossible, sauvegarde corrompue?")
            return
        self._show_game_view()

    def import_and_start(self, source_path: str):
        """Importe une sauvegarde externe puis lance la partie"""
        success, msg = self.save_system.import_save(source_path)
        if not success:
            self._show_menu(msg)
            return
        self._init_player(force_new=False)
        if not self.player:
            self._show_menu("Import réussi mais chargement impossible")
            return
        self._show_game_view()

    def _init_player(self, force_new: bool = False):
        """Initialise le joueur (charge ou crée nouveau)"""
        if not force_new:
            # Essayer de charger
            self.player = self.save_system.load_game(
                self.data_manager,
                self.skill_system,
                self.station_upgrade_system
            )
        else:
            self.player = None

        if not self.player:
            # Créer un nouveau joueur
            print("Création d'un nouveau personnage...")
            self.player = Player(self.data_manager)

            # Équipement de départ
            starter_items = self.item_generator.generate_starter_equipment()
            for item in starter_items:
                equipped = self.player.equip_item(item)
                if equipped:
                    self.player.add_item_to_inventory(equipped)

            # Ressources de départ (PRESQUE RIEN - hardcore extrême)
            self.player.add_resource("bois_tendre", 3)
            self.player.add_resource("pierre_brute", 3)
            self.player.add_resource("fibres_sauvages", 2)
            self.player.gold = 10

            # Débloquer la première station (atelier = workbench en français)
            self.player.unlock_station("atelier")

            # Sauvegarder
            self.save_system.save_game(self.player, self.skill_system, self.station_upgrade_system)

    def _show_game_view(self):
        """Instancie et affiche la vue de jeu principale"""
        game_view = GameView(
            self.player,
            self.data_manager,
            self.item_generator,
            self.combat_system,
            self.gathering_system,
            self.crafting_system,
            self.skill_system,
            self.station_upgrade_system,
            self.save_system
        )
        self.show_view(game_view)
