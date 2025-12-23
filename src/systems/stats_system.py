"""
Système de statistiques - Gère toutes les stats du jeu
"""

from typing import Dict, Optional
import random

class StatsContainer:
    """Conteneur pour toutes les statistiques d'une entité (joueur, ennemi, item)"""

    def __init__(self):
        # Stats de combat
        self.hp_max: float = 100.0
        self.hp_current: float = 100.0
        self.hp_regen: float = 0.0
        self.atk: float = 10.0
        self.def_stat: float = 0.0  # 'def' est un mot-clé en Python
        self.armure: float = 0.0
        self.resistance_elementaire: float = 0.0
        self.vitesse_attaque: float = 1.0
        self.crit_chance: float = 5.0
        self.crit_degats: float = 150.0
        self.precision: float = 0.0
        self.esquive: float = 0.0
        self.blocage: float = 0.0
        self.vol_vie: float = 0.0
        self.epines: float = 0.0
        self.bouclier: float = 0.0
        self.cooldown_reduc: float = 0.0

        # Stats de récolte
        self.ressources_gagnees_pct: float = 0.0
        self.chance_double_drop_pct: float = 0.0
        self.gather_power_wood: float = 0.0
        self.gather_power_ore: float = 0.0
        self.gather_power_herb: float = 0.0
        self.vitesse_recolte_pct: float = 0.0

        # Stats de craft
        self.vitesse_craft_pct: float = 0.0
        self.cout_reroll_pct: float = 0.0
        self.rendement_demantelement_pct: float = 0.0

        # Stats utilitaires
        self.gain_or_pct: float = 0.0
        self.gain_xp_pct: float = 0.0

        # Procs (chances en %)
        self.proc_saignement_chance: float = 0.0
        self.proc_poison_chance: float = 0.0
        self.proc_etourdissement_chance: float = 0.0
        self.proc_double_coup_chance: float = 0.0

        # Flags spéciaux
        self.flag_execute: float = 0.0
        self.flag_boss_slayer: float = 0.0
        self.flag_resource_spirit: float = 0.0
        self.flag_reroll_free_chance: float = 0.0

        # Dégâts élémentaires
        self.degats_physique: float = 0.0
        self.degats_feu: float = 0.0
        self.degats_glace: float = 0.0
        self.degats_foudre: float = 0.0
        self.degats_poison: float = 0.0
        self.degats_ombre: float = 0.0
        self.degats_lumiere: float = 0.0

    def add_stat(self, stat_id: str, value: float):
        """Ajoute une valeur à une statistique"""
        # Utilise 'def_stat' au lieu de 'def' qui est un mot-clé
        actual_stat_id = "def_stat" if stat_id == "def" else stat_id

        if hasattr(self, actual_stat_id):
            current = getattr(self, actual_stat_id)
            setattr(self, actual_stat_id, current + value)

    def get_stat(self, stat_id: str) -> float:
        """Récupère la valeur d'une statistique"""
        actual_stat_id = "def_stat" if stat_id == "def" else stat_id
        return getattr(self, actual_stat_id, 0.0)

    def set_stat(self, stat_id: str, value: float):
        """Définit la valeur d'une statistique"""
        actual_stat_id = "def_stat" if stat_id == "def" else stat_id
        if hasattr(self, actual_stat_id):
            setattr(self, actual_stat_id, value)

    def apply_stats_dict(self, stats_dict: Dict[str, float]):
        """Applique un dictionnaire de stats à ce conteneur"""
        for stat_id, value in stats_dict.items():
            self.add_stat(stat_id, value)

    def copy(self) -> 'StatsContainer':
        """Crée une copie de ce conteneur de stats"""
        new_stats = StatsContainer()
        for attr in dir(self):
            if not attr.startswith('_') and not callable(getattr(self, attr)):
                setattr(new_stats, attr, getattr(self, attr))
        return new_stats

    def to_dict(self) -> Dict[str, float]:
        """Convertit les stats en dictionnaire"""
        result = {}
        for attr in dir(self):
            if not attr.startswith('_') and not callable(getattr(self, attr)):
                result[attr] = getattr(self, attr)
        return result


class CombatCalculator:
    """Calcule les dégâts, la défense et les effets de combat"""

    @staticmethod
    def calculate_damage(attacker: StatsContainer, defender: StatsContainer,
                        is_boss: bool = False) -> Dict:
        """
        Calcule les dégâts d'une attaque
        Retourne un dict avec: damage, is_crit, procs, blocked, dodged
        """
        result = {
            "damage": 0.0,
            "is_crit": False,
            "procs": [],
            "blocked": False,
            "dodged": False,
            "lifesteal": 0.0
        }

        # 1. Vérifier l'esquive
        dodge_chance = defender.esquive - (attacker.precision * 0.5)
        if random.random() * 100 < dodge_chance:
            result["dodged"] = True
            return result

        # 2. Calcul des dégâts de base
        base_damage = attacker.atk

        # Ajouter les dégâts élémentaires
        base_damage += attacker.degats_physique
        base_damage += attacker.degats_feu
        base_damage += attacker.degats_glace
        base_damage += attacker.degats_foudre
        base_damage += attacker.degats_poison
        base_damage += attacker.degats_ombre
        base_damage += attacker.degats_lumiere

        # 3. Vérifier le coup critique
        if random.random() * 100 < attacker.crit_chance:
            result["is_crit"] = True
            base_damage *= (attacker.crit_degats / 100.0)

        # 4. Appliquer les bonus spéciaux
        if is_boss and attacker.flag_boss_slayer > 0:
            base_damage *= (1.0 + attacker.flag_boss_slayer / 100.0)

        # Execute (cible <30% HP)
        if defender.hp_current < (defender.hp_max * 0.3) and attacker.flag_execute > 0:
            base_damage *= (1.0 + attacker.flag_execute / 100.0)

        # 5. Vérifier le blocage
        if random.random() * 100 < defender.blocage:
            result["blocked"] = True
            base_damage *= 0.2  # Blocage réduit 80% des dégâts

        # 6. Réduction par défense et armure
        # Formule: dégâts * (100 / (100 + def + armure))
        reduction = 100.0 / (100.0 + defender.def_stat + defender.armure)
        base_damage *= reduction

        # Réduction par résistance élémentaire (simple pour l'instant)
        elemental_damage = (attacker.degats_feu + attacker.degats_glace +
                          attacker.degats_foudre + attacker.degats_poison +
                          attacker.degats_ombre + attacker.degats_lumiere)
        if elemental_damage > 0:
            elemental_reduction = defender.resistance_elementaire / 100.0
            base_damage *= (1.0 - elemental_reduction * 0.5)

        result["damage"] = max(1.0, base_damage)  # Minimum 1 dégât

        # 7. Vol de vie
        if attacker.vol_vie > 0:
            result["lifesteal"] = result["damage"] * (attacker.vol_vie / 100.0)

        # 8. Épines (dégâts de retour)
        if defender.epines > 0:
            result["thorns_damage"] = defender.epines

        # 9. Vérifier les procs
        CombatCalculator._check_procs(attacker, result)

        return result

    @staticmethod
    def _check_procs(attacker: StatsContainer, result: Dict):
        """Vérifie les déclenchements de procs"""
        procs = []

        if random.random() * 100 < attacker.proc_saignement_chance:
            procs.append({"type": "bleed", "duration": 5.0, "damage_per_sec": attacker.atk * 0.2})

        if random.random() * 100 < attacker.proc_poison_chance:
            procs.append({"type": "poison", "duration": 6.0, "damage_per_sec": attacker.atk * 0.15})

        if random.random() * 100 < attacker.proc_etourdissement_chance:
            procs.append({"type": "stun", "duration": 1.5})

        if random.random() * 100 < attacker.proc_double_coup_chance:
            procs.append({"type": "double_hit"})

        result["procs"] = procs

    @staticmethod
    def apply_regen(entity_stats: StatsContainer, delta_time: float):
        """Applique la régénération de vie"""
        if entity_stats.hp_regen > 0:
            entity_stats.hp_current = min(
                entity_stats.hp_max,
                entity_stats.hp_current + entity_stats.hp_regen * delta_time
            )
