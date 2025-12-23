"""
Système de Skills - Gère les compétences permanentes débloquables
"""

from typing import Dict, List, Optional

class SkillSystem:
    """Gère les skills (compétences permanentes) du joueur"""

    def __init__(self, data_manager):
        self.data = data_manager
        self.unlocked_skills: List[str] = []  # IDs des skills débloqués

    def get_available_skills(self, player) -> List[Dict]:
        """
        Retourne les skills disponibles pour le joueur

        Returns:
            Liste de dicts avec skill + can_unlock + reason
        """
        all_skills = self.data.skills
        available = []

        for skill in all_skills:
            # Déjà débloqué?
            if skill["id"] in self.unlocked_skills:
                continue

            # Vérifie level requis
            requires_level = skill.get("requires_level", 1)
            can_unlock = True
            reason = ""

            if player.level < requires_level:
                can_unlock = False
                reason = f"Niveau {requires_level} requis"
            else:
                # Vérifie les ressources
                for cost_item in skill.get("cost", []):
                    if "resource" in cost_item:
                        res_id = cost_item["resource"]
                        qty = cost_item["qty"]
                        if not player.has_resource(res_id, qty):
                            can_unlock = False
                            res_data = self.data.get_resource(res_id)
                            res_name = res_data.get("name", res_id) if res_data else res_id
                            reason = f"Manque: {qty}x {res_name}"
                            break

                    if "gold" in cost_item:
                        gold_cost = cost_item["gold"]
                        if player.gold < gold_cost:
                            can_unlock = False
                            reason = f"Manque: {gold_cost} or"
                            break

            available.append({
                "skill": skill,
                "can_unlock": can_unlock,
                "reason": reason
            })

        return available

    def unlock_skill(self, skill_id: str, player) -> bool:
        """
        Débloque un skill

        Returns:
            True si succès
        """
        # Trouver le skill
        skill = None
        for s in self.data.skills:
            if s["id"] == skill_id:
                skill = s
                break

        if not skill:
            return False

        # Vérifier si déjà débloqué
        if skill_id in self.unlocked_skills:
            return False

        # Vérifier level
        if player.level < skill.get("requires_level", 1):
            return False

        # Consommer les ressources
        for cost_item in skill.get("cost", []):
            if "resource" in cost_item:
                if not player.consume_resource(cost_item["resource"], cost_item["qty"]):
                    return False

            if "gold" in cost_item:
                if player.gold < cost_item["gold"]:
                    return False
                player.gold -= cost_item["gold"]

        # Débloquer
        self.unlocked_skills.append(skill_id)

        # Appliquer l'effet du skill (permanent)
        self._apply_skill_effect(skill, player)

        return True

    def _apply_skill_effect(self, skill: Dict, player):
        """Applique l'effet permanent d'un skill"""
        effect = skill.get("effect")

        if isinstance(effect, list):
            # Plusieurs effets
            for eff in effect:
                self._apply_single_effect(eff, player)
        else:
            # Un seul effet
            self._apply_single_effect(effect, player)

    def _apply_single_effect(self, effect: Dict, player):
        """Applique un effet unique"""
        stat = effect.get("stat")
        effect_type = effect.get("type")  # "flat" ou "percent"
        value = effect.get("value", 0)

        if effect_type == "flat":
            # Bonus direct sur la stat de base
            player.base_stats.add_stat(stat, value)
        elif effect_type == "percent":
            # Bonus en pourcentage (appliqué sur la stat actuelle)
            current = getattr(player.base_stats, stat, 0)
            bonus = current * (value / 100.0)
            player.base_stats.add_stat(stat, bonus)

    def get_unlocked_skills(self) -> List[Dict]:
        """Retourne les skills débloqués"""
        unlocked = []
        for skill_id in self.unlocked_skills:
            for skill in self.data.skills:
                if skill["id"] == skill_id:
                    unlocked.append(skill)
                    break
        return unlocked

    def to_dict(self) -> Dict:
        """Pour sauvegarde"""
        return {
            "unlocked_skills": self.unlocked_skills
        }

    def from_dict(self, data: Dict):
        """Depuis sauvegarde"""
        self.unlocked_skills = data.get("unlocked_skills", [])


class StationUpgradeSystem:
    """Gère les améliorations de stations de craft"""

    def __init__(self, data_manager):
        self.data = data_manager
        self.station_levels: Dict[str, int] = {}  # {station_id: level}

    def get_station_level(self, station_id: str) -> int:
        """Retourne le level actuel d'une station"""
        return self.station_levels.get(station_id, 0)

    def get_available_upgrades(self, player) -> List[Dict]:
        """Retourne les upgrades disponibles pour les stations débloquées"""
        available = []

        for station_config in self.data.station_upgrades:
            station_id = station_config["station_id"]

            # Station débloquée?
            if station_id not in player.unlocked_stations:
                continue

            current_level = self.get_station_level(station_id)
            upgrades = station_config.get("upgrades", [])

            # Trouver le prochain upgrade
            next_upgrade = None
            for upgrade in upgrades:
                if upgrade["level"] == current_level + 1:
                    next_upgrade = upgrade
                    break

            if not next_upgrade:
                continue

            # Vérifier si peut upgrade
            can_upgrade = True
            reason = ""

            for cost_item in next_upgrade.get("cost", []):
                if "resource" in cost_item:
                    res_id = cost_item["resource"]
                    qty = cost_item["qty"]
                    if not player.has_resource(res_id, qty):
                        can_upgrade = False
                        res_data = self.data.get_resource(res_id)
                        res_name = res_data.get("name", res_id) if res_data else res_id
                        reason = f"Manque: {qty}x {res_name}"
                        break

                if "gold" in cost_item:
                    gold_cost = cost_item["gold"]
                    if player.gold < gold_cost:
                        can_upgrade = False
                        reason = f"Manque: {gold_cost} or"
                        break

            available.append({
                "station_id": station_id,
                "current_level": current_level,
                "upgrade": next_upgrade,
                "can_upgrade": can_upgrade,
                "reason": reason
            })

        return available

    def upgrade_station(self, station_id: str, player) -> bool:
        """
        Améliore une station

        Returns:
            True si succès
        """
        current_level = self.get_station_level(station_id)

        # Trouver la config de la station
        station_config = None
        for sc in self.data.station_upgrades:
            if sc["station_id"] == station_id:
                station_config = sc
                break

        if not station_config:
            return False

        # Trouver l'upgrade correspondant
        upgrade = None
        for upg in station_config.get("upgrades", []):
            if upg["level"] == current_level + 1:
                upgrade = upg
                break

        if not upgrade:
            return False

        # Consommer les ressources
        for cost_item in upgrade.get("cost", []):
            if "resource" in cost_item:
                if not player.consume_resource(cost_item["resource"], cost_item["qty"]):
                    return False

            if "gold" in cost_item:
                if player.gold < cost_item["gold"]:
                    return False
                player.gold -= cost_item["gold"]

        # Appliquer l'upgrade
        self.station_levels[station_id] = current_level + 1

        return True

    def get_station_bonus(self, station_id: str) -> Dict:
        """Retourne les bonus totaux d'une station"""
        level = self.get_station_level(station_id)

        if level == 0:
            return {}

        # Trouver la config
        station_config = None
        for sc in self.data.station_upgrades:
            if sc["station_id"] == station_id:
                station_config = sc
                break

        if not station_config:
            return {}

        # Additionner tous les bonus jusqu'au level actuel
        total_bonus = {}
        for upgrade in station_config.get("upgrades", []):
            if upgrade["level"] <= level:
                for key, value in upgrade.get("bonus", {}).items():
                    total_bonus[key] = total_bonus.get(key, 0) + value

        return total_bonus

    def to_dict(self) -> Dict:
        """Pour sauvegarde"""
        return {
            "station_levels": self.station_levels
        }

    def from_dict(self, data: Dict):
        """Depuis sauvegarde"""
        self.station_levels = data.get("station_levels", {})
