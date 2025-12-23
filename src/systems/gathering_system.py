"""
Système de Récolte - Gère les nodes de ressources cliquables
"""

import random
from typing import Dict, List, Optional
from src.core.difficulty import DifficultySettings

class GatherNode:
    """Représente un node de récolte"""

    def __init__(self, node_data: Dict, tier_data: Dict, tier_number: int, difficulty: DifficultySettings):
        self.id: str = node_data["id"]
        self.name: str = node_data["name"]
        self.resource_id: str = node_data["resource"]
        self.recommended_level: int = tier_data.get("recommended_level", 1)

        # Déduire le type du node depuis la ressource
        self.node_type: str = self._deduce_type(node_data["resource"])
        self.tier: str = node_data["tier"]

        # HP du node (combien de fois il faut cliquer)
        base_hp = node_data.get("node_hp", tier_data.get("node_hp", 20))
        self.max_hp: float = difficulty.scaled_node_hp(base_hp, tier_number)
        self.current_hp: float = self.max_hp

        # Récompenses
        yield_data = node_data.get("yield", {})
        self.min_yield: int = yield_data.get("min", 1)
        self.max_yield: int = yield_data.get("max", 3)

        # Respawn
        self.respawn_time: float = difficulty.scaled_respawn(node_data.get("respawn_sec", 5.0))
        self.respawn_timer: float = 0.0
        self.depleted: bool = False

    def _deduce_type(self, resource_id: str) -> str:
        """Déduit le type de node depuis l'ID de la ressource"""
        if "bois" in resource_id or "wood" in resource_id or "seve" in resource_id:
            return "wood"
        elif ("minerai" in resource_id or "ore" in resource_id or
              "pierre" in resource_id or "obsidienne" in resource_id or
              "cristal" in resource_id):
            return "ore"
        elif ("plante" in resource_id or "herbe" in resource_id or
              "herb" in resource_id or "champignon" in resource_id or
              "fleur" in resource_id or "fibres" in resource_id):
            return "herb"
        else:
            return "ore"  # Par défaut

    def harvest(self, power: float) -> bool:
        """
        Récolte le node

        Args:
            power: Puissance de récolte du joueur

        Returns:
            True si le node est déplété
        """
        if self.depleted:
            return True

        self.current_hp -= power
        if self.current_hp <= 0:
            self.depleted = True
            self.respawn_timer = self.respawn_time
            return True

        return False

    def update(self, delta_time: float):
        """Met à jour le respawn du node"""
        if self.depleted:
            self.respawn_timer -= delta_time
            if self.respawn_timer <= 0:
                self.current_hp = self.max_hp
                self.depleted = False

    def get_hp_percent(self) -> float:
        """Retourne le pourcentage de HP restant"""
        return (self.current_hp / self.max_hp) * 100.0


class GatheringSystem:
    """Gère le système de récolte de ressources"""

    def __init__(self, data_manager, difficulty: DifficultySettings):
        self.data = data_manager
        self.difficulty = difficulty
        self.active_nodes: List[GatherNode] = []

    def spawn_nodes_for_zone(self, zone_id: str, num_nodes: int = 5):
        """Génère des nodes de récolte pour une zone"""
        zone = self.data.get_zone(zone_id)
        if not zone:
            return

        tier = zone["tier"]
        tier_data = self.data.get_tier(tier)
        tier_number = self.data.get_tier_number(tier)

        # Récupérer les nodes possibles pour cette zone
        zone_resources = zone.get("resources", [])
        if not zone_resources:
            return

        # Filtrer les nodes qui correspondent aux ressources de la zone
        valid_nodes = [
            node for node in self.data.nodes
            if node.get("resource") in zone_resources and node.get("tier") == tier
        ]

        if not valid_nodes:
            return

        # Spawn des nodes
        self.active_nodes.clear()
        for _ in range(num_nodes):
            node_data = random.choice(valid_nodes)
            node = GatherNode(node_data, tier_data, tier_number, self.difficulty)
            self.active_nodes.append(node)

    def harvest_node(self, node_index: int, player) -> Optional[Dict]:
        """
        Récolte un node

        Returns:
            Dict avec les récompenses si succès, None sinon
        """
        if node_index < 0 or node_index >= len(self.active_nodes):
            return None

        node = self.active_nodes[node_index]
        if node.depleted:
            return None

        player_stats = player.get_total_stats()

        # Calculer la puissance de récolte basée sur le type
        power = 10.0  # Base
        if node.node_type == "wood":
            power += player_stats.gather_power_wood
        elif node.node_type == "ore":
            power += player_stats.gather_power_ore
        elif node.node_type == "herb":
            power += player_stats.gather_power_herb

        # Vitesse de récolte
        speed_bonus = player_stats.vitesse_recolte_pct / 100.0
        power *= (1.0 + speed_bonus)

        # Harvest
        depleted = node.harvest(power)

        if depleted:
            # Calculer les récompenses
            base_yield = random.randint(node.min_yield, node.max_yield)
            scaled_yield = self.difficulty.scaled_gather_yield(base_yield)
            reward_factor = self.difficulty.reward_factor(
                player.level,
                node.recommended_level
            )

            # Bonus ressources
            bonus_mult = 1.0 + (player_stats.ressources_gagnees_pct / 100.0)
            final_yield = int(scaled_yield * bonus_mult * reward_factor)
            final_yield = max(1, final_yield)

            # Chance de double drop
            if random.random() * 100 < player_stats.chance_double_drop_pct:
                final_yield *= 2

            # Ajouter au joueur
            player.add_resource(node.resource_id, final_yield)

            # XP de récolte
            tier_num = self.data.get_tier_number(node.tier)
            xp_reward = int(5 * tier_num * reward_factor)
            player.add_xp(max(1, xp_reward))

            return {
                "resource_id": node.resource_id,
                "quantity": final_yield,
                "xp": max(1, xp_reward),
                "node_name": node.name
            }

        return None

    def update(self, delta_time: float):
        """Met à jour tous les nodes"""
        for node in self.active_nodes:
            node.update(delta_time)

    def get_nodes_status(self) -> List[Dict]:
        """Retourne le status de tous les nodes"""
        return [
            {
                "index": i,
                "name": node.name,
                "resource_id": node.resource_id,
                "depleted": node.depleted,
                "hp_percent": node.get_hp_percent(),
                "respawn_time": node.respawn_timer
            }
            for i, node in enumerate(self.active_nodes)
        ]
