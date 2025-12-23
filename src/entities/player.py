"""
Entité Joueur - Gère le personnage du joueur, équipement, inventaire, stats
"""

from typing import Dict, List, Optional
from src.systems.stats_system import StatsContainer
from src.systems.item_system import Item

class Player:
    """Représente le joueur avec ses stats, équipement, inventaire et progression"""

    def __init__(self, data_manager):
        self.data = data_manager

        # Informations de base
        self.name: str = "Aventurier"
        self.level: int = 1
        self.xp: int = 0
        self.xp_to_next_level: int = 100

        # Stats de base (avant équipement)
        self.base_stats: StatsContainer = StatsContainer()
        self._init_base_stats()

        # Équipement (par slot)
        self.equipment: Dict[str, Optional[Item]] = {
            "weapon": None,
            "helmet": None,
            "chest": None,
            "legs": None,
            "boots": None,
            "gloves": None,
            "ring1": None,
            "ring2": None,
            "amulet": None,
            # Outils de récolte
            "tool_ore": None,
            "tool_wood": None,
            "tool_herb": None,
        }

        # Inventaire
        self.inventory: List[Item] = []
        self.inventory_size: int = 40

        # Consommables
        self.potions: Dict[str, int] = {}  # {potion_id: quantity}

        # Ressources
        self.resources: Dict[str, int] = {}  # {resource_id: quantity}
        self.gold: int = 0

        # Statuts de combat
        self.buffs: List[Dict] = []
        self.debuffs: List[Dict] = []

        # Zone actuelle
        self.current_zone_id: str = "prairie_des_jeunes_pousses"

        # Stations débloquées
        self.unlocked_stations: List[str] = []

        # Stats de combat (tracking)
        self.combat_stats = {
            "kills": 0,
            "deaths": 0,
            "damage_dealt": 0,
            "damage_taken": 0,
            "crits": 0,
            "boss_kills": 0
        }

    def _init_base_stats(self):
        """Initialise les stats de base du joueur niveau 1"""
        # Stats de départ ULTRA faibles (VRAIMENT hardcore)
        self.base_stats.hp_max = 30.0
        self.base_stats.hp_current = 30.0
        self.base_stats.hp_regen = 0.2
        self.base_stats.atk = 3.0
        self.base_stats.def_stat = 0.0
        self.base_stats.vitesse_attaque = 0.8
        self.base_stats.crit_chance = 2.0
        self.base_stats.crit_degats = 150.0

    def get_total_stats(self) -> StatsContainer:
        """Calcule les stats totales (base + équipement + zone effects + buffs)"""
        total = self.base_stats.copy()

        # Ajouter les stats de l'équipement
        for slot, item in self.equipment.items():
            if item:
                item_stats = item.get_total_stats()
                total.apply_stats_dict(item_stats.to_dict())

        # Ajouter les effets de zone
        zone = self.data.get_zone(self.current_zone_id)
        if zone:
            for effect in zone.get("environment_effects", []):
                stat = effect.get("stat")
                value = effect.get("value", 0)
                if stat and value != 0:
                    total.add_stat(stat, value)

        # Ajouter les buffs actifs
        for buff in self.buffs:
            buff_type = buff.get("type")
            buff_value = buff.get("value", 0)
            if buff_type and buff_value != 0:
                total.add_stat(buff_type, buff_value)

        # S'assurer que HP current ne dépasse pas HP max
        total.hp_current = min(total.hp_current, total.hp_max)

        return total

    def equip_item(self, item: Item) -> Optional[Item]:
        """
        Équipe un item, retourne l'item déséquipé si applicable

        Returns:
            L'item qui était équipé dans ce slot, ou None
        """
        slot = item.slot

        # Gérer les anneaux (2 slots)
        if slot == "ring":
            if not self.equipment["ring1"]:
                slot = "ring1"
            elif not self.equipment["ring2"]:
                slot = "ring2"
            else:
                # Les deux slots sont occupés, remplacer ring1
                slot = "ring1"

        old_item = self.equipment.get(slot)

        if old_item:
            old_item.is_equipped = False

        self.equipment[slot] = item
        item.is_equipped = True

        # Recalculer HP actuel proportionnellement
        self._adjust_hp_on_equip()

        return old_item

    def unequip_item(self, slot: str) -> Optional[Item]:
        """
        Déséquipe un item d'un slot

        Returns:
            L'item déséquipé, ou None
        """
        item = self.equipment.get(slot)

        if item:
            item.is_equipped = False
            self.equipment[slot] = None
            self._adjust_hp_on_equip()

        return item

    def _adjust_hp_on_equip(self):
        """Ajuste les HP actuels quand l'équipement change"""
        stats = self.get_total_stats()
        # Garder le même pourcentage de HP
        hp_percent = self.base_stats.hp_current / max(1, self.base_stats.hp_max)
        self.base_stats.hp_current = stats.hp_max * hp_percent

    def add_item_to_inventory(self, item: Item) -> bool:
        """Ajoute un item à l'inventaire si il y a de la place"""
        if len(self.inventory) >= self.inventory_size:
            return False

        self.inventory.append(item)
        return True

    def remove_item_from_inventory(self, item_id: str) -> Optional[Item]:
        """Retire un item de l'inventaire par son ID"""
        for i, item in enumerate(self.inventory):
            if item.id == item_id:
                return self.inventory.pop(i)
        return None

    def add_resource(self, resource_id: str, quantity: int):
        """Ajoute des ressources"""
        current = self.resources.get(resource_id, 0)
        self.resources[resource_id] = current + quantity

    def has_resource(self, resource_id: str, quantity: int) -> bool:
        """Vérifie si le joueur a assez d'une ressource"""
        return self.resources.get(resource_id, 0) >= quantity

    def consume_resource(self, resource_id: str, quantity: int) -> bool:
        """Consomme une ressource si disponible"""
        if self.has_resource(resource_id, quantity):
            self.resources[resource_id] -= quantity
            return True
        return False

    def add_xp(self, amount: int):
        """Ajoute de l'XP et gère le level up"""
        stats = self.get_total_stats()
        xp_bonus = stats.gain_xp_pct / 100.0
        actual_xp = int(amount * (1.0 + xp_bonus))

        self.xp += actual_xp

        # Level up
        while self.xp >= self.xp_to_next_level:
            self.level_up()

    def level_up(self):
        """Monte le joueur de niveau"""
        self.xp -= self.xp_to_next_level
        self.level += 1

        # Augmenter les stats de base (scaling TRÈS lent - hardcore)
        self.base_stats.hp_max += 4
        self.base_stats.hp_current = self.base_stats.hp_max  # Full heal on level up
        self.base_stats.atk += 0.8
        self.base_stats.def_stat += 0.3
        self.base_stats.hp_regen += 0.05

        # Nouvelle courbe XP (TRÈS exponentielle - hardcore)
        self.xp_to_next_level = int(150 * (1.35 ** self.level))

        print(f"LEVEL UP! Niveau {self.level} atteint!")

    def add_gold(self, amount: int):
        """Ajoute de l'or"""
        stats = self.get_total_stats()
        gold_bonus = stats.gain_or_pct / 100.0
        actual_gold = int(amount * (1.0 + gold_bonus))
        self.gold += actual_gold

    def take_damage(self, damage: float) -> bool:
        """
        Prend des dégâts

        Returns:
            True si le joueur est mort
        """
        self.base_stats.hp_current -= damage
        if self.base_stats.hp_current <= 0:
            self.base_stats.hp_current = 0
            return True
        return False

    def heal(self, amount: float):
        """Soigne le joueur"""
        stats = self.get_total_stats()
        self.base_stats.hp_current = min(
            stats.hp_max,
            self.base_stats.hp_current + amount
        )

    def is_alive(self) -> bool:
        """Vérifie si le joueur est vivant"""
        return self.base_stats.hp_current > 0

    def unlock_station(self, station_id: str):
        """Débloque une station de craft"""
        if station_id not in self.unlocked_stations:
            self.unlocked_stations.append(station_id)

    def add_potion(self, potion_id: str, quantity: int = 1):
        """Ajoute des potions à l'inventaire"""
        current = self.potions.get(potion_id, 0)
        self.potions[potion_id] = current + quantity

    def use_potion(self, potion_id: str, item_base_data: Dict) -> bool:
        """
        Utilise une potion si disponible

        Returns:
            True si la potion a été utilisée avec succès
        """
        if self.potions.get(potion_id, 0) <= 0:
            return False

        effect = item_base_data.get("effect", {})
        effect_type = effect.get("type")
        value = effect.get("value", 0)

        if effect_type == "heal":
            # Soigne le joueur
            self.heal(value)
        elif effect_type == "buff_atk":
            # Ajoute un buff d'attaque temporaire
            duration = effect.get("duration", 60)
            self.buffs.append({
                "type": "atk",
                "value": value,
                "duration": duration,
                "remaining": duration
            })
        elif effect_type == "buff_def":
            # Ajoute un buff de défense temporaire
            duration = effect.get("duration", 60)
            self.buffs.append({
                "type": "def",
                "value": value,
                "duration": duration,
                "remaining": duration
            })
        elif effect_type == "buff_speed":
            # Ajoute un buff de vitesse temporaire
            duration = effect.get("duration", 60)
            self.buffs.append({
                "type": "vitesse_attaque",
                "value": value,
                "duration": duration,
                "remaining": duration
            })

        # Consommer la potion
        self.potions[potion_id] -= 1
        if self.potions[potion_id] <= 0:
            del self.potions[potion_id]

        return True

    def update_buffs(self, delta_time: float):
        """Met à jour les buffs temporaires"""
        buffs_to_remove = []

        for i, buff in enumerate(self.buffs):
            buff["remaining"] -= delta_time
            if buff["remaining"] <= 0:
                buffs_to_remove.append(i)

        # Retirer les buffs expirés (en ordre inverse pour ne pas casser les indices)
        for i in reversed(buffs_to_remove):
            self.buffs.pop(i)

    def to_dict(self) -> Dict:
        """Convertit le joueur en dictionnaire pour sauvegarde"""
        return {
            "name": self.name,
            "level": self.level,
            "xp": self.xp,
            "xp_to_next_level": self.xp_to_next_level,
            "base_stats": self.base_stats.to_dict(),
            "equipment": {
                slot: item.to_dict() if item else None
                for slot, item in self.equipment.items()
            },
            "inventory": [item.to_dict() for item in self.inventory],
            "potions": self.potions,
            "resources": self.resources,
            "gold": self.gold,
            "buffs": self.buffs,
            "current_zone_id": self.current_zone_id,
            "unlocked_stations": self.unlocked_stations,
            "combat_stats": self.combat_stats
        }

    @classmethod
    def from_dict(cls, data: Dict, data_manager):
        """Crée un joueur depuis un dictionnaire"""
        player = cls(data_manager)
        player.name = data["name"]
        player.level = data["level"]
        player.xp = data["xp"]
        player.xp_to_next_level = data["xp_to_next_level"]

        # Reconstruire les stats de base
        player.base_stats = StatsContainer()
        player.base_stats.apply_stats_dict(data["base_stats"])

        # Reconstruire l'équipement
        for slot, item_data in data["equipment"].items():
            if item_data:
                player.equipment[slot] = Item.from_dict(item_data)

        # Reconstruire l'inventaire
        player.inventory = [Item.from_dict(item_data) for item_data in data["inventory"]]

        player.potions = data.get("potions", {})
        player.resources = data["resources"]
        player.gold = data["gold"]
        player.buffs = data.get("buffs", [])
        player.current_zone_id = data["current_zone_id"]
        player.unlocked_stations = data.get("unlocked_stations", [])
        player.combat_stats = data.get("combat_stats", {
            "kills": 0,
            "deaths": 0,
            "damage_dealt": 0,
            "damage_taken": 0,
            "crits": 0,
            "boss_kills": 0
        })

        return player
