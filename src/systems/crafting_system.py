"""
Système de Crafting - Gère le crafting d'items avec stations et recettes
"""

import random
from typing import Dict, List, Optional
from src.systems.item_system import Item, ItemGenerator

class CraftingSystem:
    """Gère le système de crafting"""

    def __init__(self, data_manager, item_generator: ItemGenerator):
        self.data = data_manager
        self.item_generator = item_generator

    def can_craft(self, recipe_id: str, player) -> tuple[bool, str]:
        """
        Vérifie si le joueur peut crafter une recette

        Returns:
            (can_craft: bool, reason: str)
        """
        recipe = self.data.get_recipe(recipe_id)
        if not recipe:
            return False, "Recette inconnue"

        # Vérifier la station
        required_station = recipe.get("station")
        if required_station and required_station not in player.unlocked_stations:
            station_data = self.data.get_station(required_station)
            station_name = station_data.get("name", required_station) if station_data else required_station
            return False, f"Nécessite: {station_name}"

        # Vérifier le niveau
        required_level = recipe.get("level_required", 1)
        if player.level < required_level:
            return False, f"Nécessite niveau {required_level}"

        # Vérifier les ressources (format: inputs avec resource et qty)
        for resource in recipe.get("inputs", []):
            res_id = resource["resource"]
            quantity = resource["qty"]
            if not player.has_resource(res_id, quantity):
                res_data = self.data.get_resource(res_id)
                res_name = res_data.get("name", res_id) if res_data else res_id
                return False, f"Manque: {quantity}x {res_name}"

        # Vérifier l'or
        gold_cost = recipe.get("gold_cost", 0)
        if player.gold < gold_cost:
            return False, f"Manque {gold_cost - player.gold} or"

        return True, "OK"

    def craft_item(self, recipe_id: str, player,
                   force_quality: str = None,
                   force_rarity: str = None) -> Optional[Item]:
        """
        Craft un item à partir d'une recette

        Returns:
            L'item crafté, ou None si échec
        """
        can_craft, reason = self.can_craft(recipe_id, player)
        if not can_craft:
            return None

        recipe = self.data.get_recipe(recipe_id)

        # Consommer les ressources (format: inputs avec resource et qty)
        for resource in recipe.get("inputs", []):
            player.consume_resource(resource["resource"], resource["qty"])

        # Consommer l'or
        player.gold -= recipe.get("gold_cost", 0)

        # Déterminer ce qui est crafté (format: outputs array)
        outputs = recipe.get("outputs", [])
        if not outputs:
            return None

        output = outputs[0]  # Prendre le premier output

        # Si c'est une ressource transformée
        if "resource" in output:
            quantity = output.get("qty", 1)
            player.add_resource(output["resource"], quantity)
            return None  # Pas d'item, juste des ressources

        # Si c'est un item (item_base)
        if "item_base" in output:
            player_stats = player.get_total_stats()
            craft_bonus = player_stats.vitesse_craft_pct / 100.0

            # Générer l'item
            item = self.item_generator.generate_item(
                output["item_base"],
                rarity_id=force_rarity,
                quality_id=force_quality
            )

            # Petit bonus de qualité si craft_bonus élevé
            if craft_bonus > 0.2 and random.random() < 0.1:
                # 10% de chance d'upgrade la qualité
                qualities = ["poor", "normal", "superior", "masterwork", "perfect"]
                current_idx = qualities.index(item.quality_id) if item.quality_id in qualities else 0
                if current_idx < len(qualities) - 1:
                    item.quality_id = qualities[current_idx + 1]

            # XP pour le craft
            tier_num = self.data.get_tier_number(item.tier)
            xp_reward = 20 * tier_num
            player.add_xp(xp_reward)

            # Si c'est une potion/consommable, l'ajouter à l'inventaire de potions
            if item.slot == "consumable":
                player.add_potion(item.base_id, 1)
                return None  # Pas d'item physique, juste ajouté aux potions

            return item

        return None

    def reforge_item(self, item: Item, player) -> bool:
        """
        Reforge un item (reroll ses affixes)

        Returns:
            True si succès
        """
        # Coût de base: gold_value de l'item
        base_cost = item.gold_value

        player_stats = player.get_total_stats()
        cost_reduction = player_stats.cout_reroll_pct / 100.0
        final_cost = int(base_cost * (1.0 - cost_reduction))

        # Chance de reforge gratuit
        if random.random() * 100 < player_stats.flag_reroll_free_chance:
            final_cost = 0

        if player.gold < final_cost:
            return False

        player.gold -= final_cost

        # Reroll l'item (regénérer les affixes)
        base = self.data.get_item_base(item.base_id)
        rarity = self.data.get_rarity(item.rarity_id)
        tier_data = self.data.get_tier(item.tier)
        tier_num = self.data.get_tier_number(item.tier)

        # Clear affixes
        item.affixes.clear()

        # Regénérer
        num_affixes = rarity.get("max_affixes", 0)
        if num_affixes > 0:
            tags = base.get("tags", [])
            available_affixes = self.data.get_affixes_by_tags(tags, item.tier)

            if available_affixes:
                selected = random.sample(
                    available_affixes,
                    min(num_affixes, len(available_affixes))
                )

                for affix_data in selected:
                    min_val = affix_data.get("min", 1)
                    max_val = affix_data.get("max", min_val)
                    base_roll = random.uniform(min_val, max_val)
                    tier_scaling = tier_num ** 0.35
                    rarity_mult = rarity.get("affix_mult", 1.0)
                    final_value = base_roll * tier_scaling * rarity_mult

                    item.affixes.append({
                        "affix_id": affix_data["id"],
                        "name": affix_data["name"],
                        "stat_id": affix_data["stat"],
                        "rolled_value": round(final_value, 2)
                    })

        return True

    def dismantle_item(self, item: Item, player) -> Dict[str, int]:
        """
        Démantèle un item pour récupérer des ressources

        Returns:
            Dict des ressources récupérées {resource_id: quantity}
        """
        player_stats = player.get_total_stats()
        dismantling_bonus = 1.0 + (player_stats.rendement_demantelement_pct / 100.0)

        # Ressources de base selon le tier et la rareté
        tier_num = self.data.get_tier_number(item.tier)
        rarity = self.data.get_rarity(item.rarity_id)

        base_amount = tier_num * rarity.get("affix_mult", 1.0)
        final_amount = int(base_amount * dismantling_bonus)

        # Récupérer des ressources génériques (à améliorer avec les matériaux spécifiques)
        recovered = {}

        # Pour l'instant, retourne des ressources basiques basées sur le slot
        base = self.data.get_item_base(item.base_id)
        material = base.get("material", "unknown")

        # Mapping simple matériau -> ressource
        material_map = {
            "wood": "bois_tendre",
            "metal": "minerai_fer",
            "cloth": "fibres_sauvages",
            "leather": "cuir_brut",
        }

        resource_id = material_map.get(material, "pierre_brute")
        recovered[resource_id] = max(1, final_amount)

        # Ajouter au joueur
        for res_id, qty in recovered.items():
            player.add_resource(res_id, qty)

        return recovered

    def get_available_recipes(self, player, station_id: str = None) -> List[Dict]:
        """
        Retourne toutes les recettes disponibles pour le joueur

        Args:
            station_id: Filtrer par station (optionnel)
        """
        available = []

        for recipe in self.data.recipes:
            # Filtrer par station si demandé
            if station_id and recipe.get("station") != station_id:
                continue

            # Vérifier si la station est débloquée
            required_station = recipe.get("station")
            if required_station and required_station not in player.unlocked_stations:
                continue

            # Vérifier le niveau
            if player.level < recipe.get("level_required", 1):
                continue

            can_craft, reason = self.can_craft(recipe["id"], player)

            available.append({
                "recipe": recipe,
                "can_craft": can_craft,
                "reason": reason
            })

        return available

    def unlock_station_cost(self, station_id: str) -> Dict:
        """Retourne le coût pour débloquer une station"""
        station = self.data.get_station(station_id)
        if not station:
            return {}

        return {
            "gold": station.get("unlock_cost_gold", 100),
            "resources": station.get("unlock_cost_resources", [])
        }

    def try_unlock_station(self, station_id: str, player) -> tuple[bool, str]:
        """
        Tente de débloquer une station

        Returns:
            (success: bool, message: str)
        """
        if station_id in player.unlocked_stations:
            return False, "Station déjà débloquée"

        station = self.data.get_station(station_id)
        if not station:
            return False, "Station inconnue"

        # Vérifier le niveau
        required_level = station.get("level_required", 1)
        if player.level < required_level:
            return False, f"Nécessite niveau {required_level}"

        # Vérifier l'or
        gold_cost = station.get("unlock_cost_gold", 100)
        if player.gold < gold_cost:
            return False, f"Manque {gold_cost - player.gold} or"

        # Vérifier les ressources
        for resource in station.get("unlock_cost_resources", []):
            if not player.has_resource(resource["id"], resource["quantity"]):
                res_data = self.data.get_resource(resource["id"])
                res_name = res_data.get("name", resource["id"]) if res_data else resource["id"]
                return False, f"Manque {resource['quantity']}x {res_name}"

        # Consommer
        player.gold -= gold_cost
        for resource in station.get("unlock_cost_resources", []):
            player.consume_resource(resource["id"], resource["quantity"])

        # Débloquer
        player.unlock_station(station_id)

        return True, f"{station['name']} débloquée!"
