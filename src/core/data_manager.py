"""
Data Manager - Charge et gère toutes les données JSON du jeu
"""

import json
from pathlib import Path
from typing import Dict, List, Any

class DataManager:
    """Gère le chargement et l'accès à toutes les données de configuration du jeu"""

    def __init__(self):
        self.data_path = Path("info")
        self.stats: List[Dict] = []
        self.tiers: List[Dict] = []
        self.rarities: List[Dict] = []
        self.qualities: List[Dict] = []
        self.resources: List[Dict] = []
        self.nodes: List[Dict] = []
        self.items_base: List[Dict] = []
        self.affixes: List[Dict] = []
        self.sets: List[Dict] = []
        self.stations: List[Dict] = []
        self.recipes: List[Dict] = []
        self.enemies: List[Dict] = []
        self.zones: List[Dict] = []
        self.collectibles: Dict = {}
        self.lore: Dict = {}
        self.skills: List[Dict] = []
        self.station_upgrades: List[Dict] = []

        # Dictionnaires pour accès rapide par ID
        self._stats_by_id: Dict[str, Dict] = {}
        self._tiers_by_id: Dict[str, Dict] = {}
        self._rarities_by_id: Dict[str, Dict] = {}
        self._qualities_by_id: Dict[str, Dict] = {}
        self._resources_by_id: Dict[str, Dict] = {}
        self._items_base_by_id: Dict[str, Dict] = {}
        self._affixes_by_id: Dict[str, Dict] = {}
        self._enemies_by_id: Dict[str, Dict] = {}
        self._zones_by_id: Dict[str, Dict] = {}
        self._stations_by_id: Dict[str, Dict] = {}
        self._recipes_by_id: Dict[str, Dict] = {}

    def load_all(self):
        """Charge tous les fichiers JSON"""
        print("Chargement des données du jeu...")

        self.stats = self._load_json("stats.json")
        self.tiers = self._load_json("tiers.json")
        self.rarities = self._load_json("rarities.json")
        self.qualities = self._load_json("qualities.json")
        self.resources = self._load_json("resources.json")
        self.nodes = self._load_json("nodes.json")
        self.items_base = self._load_json("items_base.json")
        self.affixes = self._load_json("affixes.json")
        self.sets = self._load_json("sets.json")
        self.stations = self._load_json("stations.json")
        self.recipes = self._load_json("recipes.json")
        self.enemies = self._load_json("enemies.json")
        self.zones = self._load_json("zones.json")
        self.collectibles = self._load_json("collectibles.json")
        self.lore = self._load_json("lore.json")
        self.skills = self._load_json("skills.json")
        self.station_upgrades = self._load_json("station_upgrades.json")

        # Construction des dictionnaires d'accès rapide
        self._build_lookup_dicts()

        print("Données chargées avec succès!")

    def _load_json(self, filename: str) -> Any:
        """Charge un fichier JSON depuis le dossier info/"""
        file_path = self.data_path / filename
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"ATTENTION: Fichier {filename} non trouvé!")
            return [] if filename != "lore.json" and filename != "collectibles.json" else {}
        except json.JSONDecodeError as e:
            print(f"ERREUR: Impossible de parser {filename}: {e}")
            return [] if filename != "lore.json" and filename != "collectibles.json" else {}

    def _build_lookup_dicts(self):
        """Construit les dictionnaires pour accès rapide par ID"""
        self._stats_by_id = {stat["id"]: stat for stat in self.stats}
        self._tiers_by_id = {tier["id"]: tier for tier in self.tiers}
        self._rarities_by_id = {rarity["id"]: rarity for rarity in self.rarities}
        self._qualities_by_id = {quality["id"]: quality for quality in self.qualities}
        self._resources_by_id = {res["id"]: res for res in self.resources}
        self._items_base_by_id = {item["id"]: item for item in self.items_base}
        self._affixes_by_id = {affix["id"]: affix for affix in self.affixes}
        self._enemies_by_id = {enemy["id"]: enemy for enemy in self.enemies}
        self._zones_by_id = {zone["id"]: zone for zone in self.zones}
        self._stations_by_id = {station["id"]: station for station in self.stations}
        self._recipes_by_id = {recipe["id"]: recipe for recipe in self.recipes}

    # Méthodes d'accès rapide
    def get_stat(self, stat_id: str) -> Dict:
        """Récupère une stat par son ID"""
        return self._stats_by_id.get(stat_id, {})

    def get_tier(self, tier_id: str) -> Dict:
        """Récupère un tier par son ID"""
        return self._tiers_by_id.get(tier_id, {})

    def get_rarity(self, rarity_id: str) -> Dict:
        """Récupère une rareté par son ID"""
        return self._rarities_by_id.get(rarity_id, {})

    def get_quality(self, quality_id: str) -> Dict:
        """Récupère une qualité par son ID"""
        return self._qualities_by_id.get(quality_id, {})

    def get_resource(self, resource_id: str) -> Dict:
        """Récupère une ressource par son ID"""
        return self._resources_by_id.get(resource_id, {})

    def get_item_base(self, item_id: str) -> Dict:
        """Récupère un item de base par son ID"""
        return self._items_base_by_id.get(item_id, {})

    def get_affix(self, affix_id: str) -> Dict:
        """Récupère un affixe par son ID"""
        return self._affixes_by_id.get(affix_id, {})

    def get_enemy(self, enemy_id: str) -> Dict:
        """Récupère un ennemi par son ID"""
        return self._enemies_by_id.get(enemy_id, {})

    def get_zone(self, zone_id: str) -> Dict:
        """Récupère une zone par son ID"""
        return self._zones_by_id.get(zone_id, {})

    def get_station(self, station_id: str) -> Dict:
        """Récupère une station par son ID"""
        return self._stations_by_id.get(station_id, {})

    def get_recipe(self, recipe_id: str) -> Dict:
        """Récupère une recette par son ID"""
        return self._recipes_by_id.get(recipe_id, {})

    def get_affixes_by_tags(self, tags: List[str], tier: str) -> List[Dict]:
        """Récupère tous les affixes correspondant aux tags et tier donnés"""
        tier_num = int(tier.replace("t", ""))
        result = []

        for affix in self.affixes:
            # Vérifie que l'affixe a au moins un tag en commun
            if any(tag in affix.get("tags", []) for tag in tags):
                # Vérifie que le tier min est respecté
                if tier_num >= affix.get("tier_min", 1):
                    result.append(affix)

        return result

    def get_tier_number(self, tier_id: str) -> int:
        """Retourne le numéro du tier (t1 -> 1, t10 -> 10)"""
        return int(tier_id.replace("t", ""))
