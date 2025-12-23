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

class Game(arcade.Window):
    """Classe principale du jeu"""

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        # Initialisation des systèmes
        self.data_manager = DataManager()
        self.data_manager.load_all()

        self.item_generator = ItemGenerator(self.data_manager)
        self.combat_system = CombatSystem(self.data_manager, self.item_generator)
        self.gathering_system = GatheringSystem(self.data_manager)
        self.crafting_system = CraftingSystem(self.data_manager, self.item_generator)
        self.skill_system = SkillSystem(self.data_manager)
        self.station_upgrade_system = StationUpgradeSystem(self.data_manager)
        self.save_system = SaveSystem()

        # Player
        self.player = None

        # Charger ou créer un nouveau joueur
        self._init_player()

        # Vue principale
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

        arcade.set_background_color(arcade.color.BLACK)

    def _init_player(self):
        """Initialise le joueur (charge ou crée nouveau)"""
        # Essayer de charger
        self.player = self.save_system.load_game(
            self.data_manager,
            self.skill_system,
            self.station_upgrade_system
        )

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
