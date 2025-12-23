"""
Configuration centralisée de la difficulté et des réglages de pacing.

Cette couche évite de dupliquer des multiplicateurs un peu partout et permet
de renforcer la sensation « hardcore mais juste » en contrôlant la montée des
coûts, la robustesse des ennemis et la cadence des ressources.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class DifficultySettings:
    """Valeurs de tuning globales pour un mode plus exigeant."""

    enemy_hp_mult: float = 1.35
    enemy_atk_mult: float = 1.2
    boss_hp_mult: float = 1.65
    boss_atk_mult: float = 1.35
    scaling_per_level: float = 0.08

    reward_xp_mult: float = 0.65
    reward_gold_mult: float = 0.55
    overlevel_penalty: float = 0.18
    underlevel_bonus: float = 0.08

    gather_node_hp_mult: float = 1.25
    gather_yield_mult: float = 0.85
    gather_respawn_mult: float = 1.2

    crafting_gold_mult: float = 1.15
    crafting_resource_mult: float = 1.1

    def level_scaling_factor(self, player_level: int, recommended_level: int) -> float:
        """Augmente la difficulté quand le joueur dépasse la zone."""
        level_gap = max(0, player_level - recommended_level)
        return 1.0 + (level_gap * self.scaling_per_level)

    def reward_factor(self, player_level: int, recommended_level: int) -> float:
        """Réduit les gains quand on sur-niveau, bonus léger si on est en retard."""
        gap = player_level - recommended_level
        if gap > 0:
            penalty = min(0.7, gap * self.overlevel_penalty)
            return max(0.35, 1.0 - penalty)
        if gap < 0:
            bonus = min(0.4, abs(gap) * self.underlevel_bonus)
            return 1.0 + bonus
        return 1.0

    def scaled_enemy_stats(self, stats: Dict[str, float], player_level: int, recommended_level: int,
                            is_boss: bool) -> Dict[str, float]:
        """Applique les multiplicateurs de difficulté aux stats ennemies."""
        factor = self.level_scaling_factor(player_level, recommended_level)
        hp_mult = self.enemy_hp_mult * (self.boss_hp_mult if is_boss else 1.0)
        atk_mult = self.enemy_atk_mult * (self.boss_atk_mult if is_boss else 1.0)

        return {
            "hp": stats.get("hp", 0) * hp_mult * factor,
            "atk": stats.get("atk", 0) * atk_mult * factor,
            "def": stats.get("def", 0) * factor,
            "armor": stats.get("armor", 0) * factor,
            "attack_speed": stats.get("attack_speed", 1.0),
            "crit_chance": stats.get("crit_chance", 0.0)
        }

    def scaled_node_hp(self, base_hp: float, tier_number: int) -> float:
        """Rend les nodes de récolte plus résistants sur la durée."""
        tier_bonus = 1.0 + ((tier_number - 1) * 0.12)
        return base_hp * self.gather_node_hp_mult * tier_bonus

    def scaled_respawn(self, base_respawn: float) -> float:
        """Allonge le temps de respawn pour limiter le spam de nodes."""
        return base_respawn * self.gather_respawn_mult

    def scaled_gather_yield(self, base_yield: int) -> int:
        """Réduit légèrement la quantité moyenne de ressources par node."""
        return max(1, int(round(base_yield * self.gather_yield_mult)))

    def scaled_recipe_costs(self, recipe: Dict) -> Dict:
        """Retourne une copie des coûts de recette augmentés pour le mode hard."""
        scaled_inputs = []
        for res in recipe.get("inputs", []):
            scaled_inputs.append({
                "resource": res["resource"],
                "qty": int(round(res.get("qty", 0) * self.crafting_resource_mult))
            })

        return {
            "gold_cost": int(round(recipe.get("gold_cost", 0) * self.crafting_gold_mult)),
            "inputs": scaled_inputs
        }
