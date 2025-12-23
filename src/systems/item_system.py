"""
Système d'items - Génération procédurale d'items avec bases, qualités, raretés et affixes
"""

import random
import uuid
from typing import Dict, List, Optional
from src.systems.stats_system import StatsContainer

class Item:
    """Représente un item généré avec ses stats, affixes et propriétés"""

    def __init__(self, item_id: str = None):
        self.id: str = item_id or str(uuid.uuid4())
        self.base_id: str = ""
        self.name: str = ""
        self.slot: str = ""  # weapon, helmet, chest, legs, boots, gloves, ring, amulet
        self.tier: str = "t1"
        self.rarity_id: str = "common"
        self.quality_id: str = "normal"

        # Stats de base de l'item
        self.base_stats: StatsContainer = StatsContainer()

        # Affixes
        self.affixes: List[Dict] = []  # {affix_id, rolled_value, stat_id}

        # Set
        self.set_id: Optional[str] = None

        # Valeur et level requirement
        self.gold_value: int = 1
        self.level_requirement: int = 1

        # Métadonnées
        self.power_score: float = 0.0
        self.is_equipped: bool = False

    def get_total_stats(self) -> StatsContainer:
        """Calcule et retourne les stats totales de l'item (base + affixes)"""
        total = self.base_stats.copy()

        for affix in self.affixes:
            total.add_stat(affix["stat_id"], affix["rolled_value"])

        return total

    def get_display_name(self) -> str:
        """Retourne le nom complet de l'item avec rareté"""
        return f"{self.name}"

    def to_dict(self) -> Dict:
        """Convertit l'item en dictionnaire pour sauvegarde"""
        return {
            "id": self.id,
            "base_id": self.base_id,
            "name": self.name,
            "slot": self.slot,
            "tier": self.tier,
            "rarity_id": self.rarity_id,
            "quality_id": self.quality_id,
            "base_stats": self.base_stats.to_dict(),
            "affixes": self.affixes,
            "set_id": self.set_id,
            "gold_value": self.gold_value,
            "level_requirement": self.level_requirement,
            "power_score": self.power_score,
            "is_equipped": self.is_equipped
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Item':
        """Crée un item depuis un dictionnaire"""
        item = cls(data["id"])
        item.base_id = data["base_id"]
        item.name = data["name"]
        item.slot = data["slot"]
        item.tier = data["tier"]
        item.rarity_id = data["rarity_id"]
        item.quality_id = data["quality_id"]

        # Reconstruire les stats de base
        item.base_stats = StatsContainer()
        item.base_stats.apply_stats_dict(data["base_stats"])

        item.affixes = data["affixes"]
        item.set_id = data.get("set_id")
        item.gold_value = data["gold_value"]
        item.level_requirement = data["level_requirement"]
        item.power_score = data["power_score"]
        item.is_equipped = data.get("is_equipped", False)

        return item


class ItemGenerator:
    """Génère des items procéduralement basé sur les données JSON"""

    def __init__(self, data_manager):
        self.data = data_manager

    def generate_item(self, base_id: str, tier: str = None,
                     rarity_id: str = None, quality_id: str = None,
                     force_set: str = None) -> Item:
        """
        Génère un item complet

        Args:
            base_id: ID de la base d'item
            tier: Tier forcé (sinon utilise celui de la base)
            rarity_id: Rareté forcée (sinon aléatoire)
            quality_id: Qualité forcée (sinon aléatoire)
            force_set: Set forcé (optionnel)
        """
        base = self.data.get_item_base(base_id)
        if not base:
            raise ValueError(f"Base d'item inconnue: {base_id}")

        item = Item()
        item.base_id = base_id
        item.slot = base["slot"]
        item.tier = tier or base["tier"]

        # Déterminer la rareté
        if rarity_id:
            item.rarity_id = rarity_id
        else:
            item.rarity_id = self._roll_rarity()

        # Déterminer la qualité
        if quality_id:
            item.quality_id = quality_id
        else:
            item.quality_id = self._roll_quality()

        # Récupérer les données
        rarity = self.data.get_rarity(item.rarity_id)
        quality = self.data.get_quality(item.quality_id)
        tier_data = self.data.get_tier(item.tier)

        # Construire le nom
        prefix = rarity.get("prefix", "")
        item.name = f"{prefix} {base['name']}".strip()

        # Set
        item.set_id = force_set

        # Calculer les stats de base
        self._generate_base_stats(item, base, tier_data, quality, rarity)

        # Générer les affixes
        num_affixes = rarity.get("max_affixes", 0)
        if num_affixes > 0:
            self._generate_affixes(item, base, tier_data, rarity, num_affixes)

        # Calculer le power score et la valeur
        item.power_score = self._calculate_power_score(item, tier_data)
        item.gold_value = int(tier_data.get("base_power", 10) *
                              rarity.get("gold_mult", 1.0) *
                              quality.get("gold_mult", 1.0))
        item.level_requirement = tier_data.get("recommended_level", 1)

        return item

    def _roll_rarity(self) -> str:
        """Tire aléatoirement une rareté"""
        # Probabilités ULTRA hardcore (quasi impossible d'avoir du rare)
        roll = random.random() * 100
        if roll < 85:  # 85%
            return "common"
        elif roll < 96:  # 11%
            return "uncommon"
        elif roll < 99:  # 3%
            return "rare"
        elif roll < 99.8:  # 0.8%
            return "epic"
        else:  # 0.2%
            return "legendary"

    def _roll_quality(self) -> str:
        """Tire aléatoirement une qualité"""
        roll = random.random() * 100
        if roll < 60:  # 60%
            return "poor"
        elif roll < 88:  # 28%
            return "normal"
        elif roll < 97:  # 9%
            return "superior"
        elif roll < 99.5:  # 2.5%
            return "masterwork"
        else:  # 0.5%
            return "perfect"

    def _generate_base_stats(self, item: Item, base: Dict, tier_data: Dict,
                            quality: Dict, rarity: Dict):
        """Génère les stats de base de l'item"""
        base_power = tier_data.get("base_power", 10)
        quality_mult = quality.get("stat_mult", 1.0)
        rarity_mult = rarity.get("stat_mult", 1.0)

        # Les stats de base viennent de la définition de l'item
        for stat_id, stat_range in base.get("base_stats", {}).items():
            # Roll entre min et max
            min_val = stat_range.get("min", 0)
            max_val = stat_range.get("max", min_val)

            base_roll = random.uniform(min_val, max_val)
            final_value = base_roll * quality_mult * rarity_mult

            item.base_stats.add_stat(stat_id, final_value)

    def _generate_affixes(self, item: Item, base: Dict, tier_data: Dict,
                         rarity: Dict, num_affixes: int):
        """Génère les affixes de l'item"""
        tier_num = self.data.get_tier_number(item.tier)
        tags = base.get("tags", [])

        # Récupérer les affixes possibles
        available_affixes = self.data.get_affixes_by_tags(tags, item.tier)

        if not available_affixes:
            return

        # Tirer aléatoirement N affixes uniques
        selected = random.sample(
            available_affixes,
            min(num_affixes, len(available_affixes))
        )

        for affix_data in selected:
            # Roll la valeur de l'affixe
            min_val = affix_data.get("min", 1)
            max_val = affix_data.get("max", min_val)

            base_roll = random.uniform(min_val, max_val)

            # Scaling par tier (formule: tier^0.35)
            tier_scaling = tier_num ** 0.35

            # Multiplicateur de rareté
            rarity_mult = rarity.get("affix_mult", 1.0)

            final_value = base_roll * tier_scaling * rarity_mult

            item.affixes.append({
                "affix_id": affix_data["id"],
                "name": affix_data["name"],
                "stat_id": affix_data["stat"],
                "rolled_value": round(final_value, 2)
            })

    def _calculate_power_score(self, item: Item, tier_data: Dict) -> float:
        """Calcule un score de puissance pour l'item"""
        total_stats = item.get_total_stats()
        base_power = tier_data.get("base_power", 10)

        # Somme pondérée des stats principales
        score = 0.0
        score += total_stats.hp_max * 0.1
        score += total_stats.atk * 2.0
        score += total_stats.def_stat * 1.5
        score += total_stats.armure * 1.2
        score += total_stats.crit_chance * 3.0
        score += total_stats.crit_degats * 0.5

        return score + base_power

    def generate_random_drop(self, zone_tier: str, player_level: int) -> Optional[Item]:
        """
        Génère un drop aléatoire approprié pour une zone

        Args:
            zone_tier: Tier de la zone actuelle
            player_level: Niveau du joueur
        """
        # Filter items by tier
        valid_bases = [
            item for item in self.data.items_base
            if item["tier"] == zone_tier
        ]

        if not valid_bases:
            return None

        # Sélectionner une base aléatoire
        base = random.choice(valid_bases)

        return self.generate_item(base["id"])

    def generate_starter_equipment(self) -> List[Item]:
        """Génère l'équipement de départ du joueur (tier 1, common, poor quality)"""
        starter_items = []

        # Arme de départ
        weapon_bases = [item for item in self.data.items_base
                       if item["slot"] == "weapon" and item["tier"] == "t1"]
        if weapon_bases:
            weapon = self.generate_item(
                weapon_bases[0]["id"],
                rarity_id="common",
                quality_id="poor"
            )
            starter_items.append(weapon)

        # Armure de départ simple
        armor_slots = ["chest", "helmet"]
        for slot in armor_slots:
            armor_bases = [item for item in self.data.items_base
                          if item["slot"] == slot and item["tier"] == "t1"]
            if armor_bases:
                armor = self.generate_item(
                    armor_bases[0]["id"],
                    rarity_id="common",
                    quality_id="poor"
                )
                starter_items.append(armor)

        return starter_items
