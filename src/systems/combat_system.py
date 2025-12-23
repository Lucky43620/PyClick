"""
Système de Combat - Gère les combats automatiques contre les ennemis
"""

import random
from typing import Dict, List, Optional
from src.systems.stats_system import StatsContainer, CombatCalculator
from src.systems.item_system import Item, ItemGenerator

class Enemy:
    """Représente un ennemi en combat"""

    def __init__(self, enemy_data: Dict, tier_data: Dict):
        self.id: str = enemy_data["id"]
        self.name: str = enemy_data["name"]
        self.is_boss: bool = enemy_data.get("is_boss", False)
        self.tier: str = enemy_data["tier"]

        # Stats
        self.stats: StatsContainer = StatsContainer()
        self._init_stats(enemy_data, tier_data)

        # Loot (nouveau format)
        loot_data = enemy_data.get("loot", {})
        gold_data = loot_data.get("gold", {})
        self.gold_min: int = gold_data.get("min", 1)
        self.gold_max: int = gold_data.get("max", 5)

        self.resource_drops: List[Dict] = loot_data.get("resource_drops", [])
        self.item_drop_chance: float = loot_data.get("item_drop_chance_pct", 10)

        # XP basé sur le tier (TRÈS réduit - hardcore)
        tier_num = int(tier_data.get("base_power", 10))
        self.xp_reward: int = enemy_data.get("xp", max(3, tier_num // 2))

        # Status effects
        self.debuffs: List[Dict] = []

    def _init_stats(self, enemy_data: Dict, tier_data: Dict):
        """Initialise les stats de l'ennemi basé sur le tier"""
        # Les stats sont dans un sous-objet dans le JSON
        enemy_stats = enemy_data.get("stats", {})

        # Utiliser les stats du JSON ou les valeurs par défaut du tier
        self.stats.hp_max = enemy_stats.get("hp", tier_data.get("enemy_hp", 40))
        self.stats.hp_current = self.stats.hp_max
        self.stats.atk = enemy_stats.get("atk", tier_data.get("enemy_atk", 6))

        # Stats additionnelles de l'ennemi
        self.stats.def_stat = enemy_stats.get("def", 0)
        self.stats.armure = enemy_stats.get("armor", 0)
        self.stats.vitesse_attaque = enemy_stats.get("attack_speed", 1.0)
        self.stats.crit_chance = enemy_stats.get("crit_chance", 0)

        # Boss bonus (ENCORE PLUS FORT - hardcore)
        if self.is_boss:
            self.stats.hp_max *= 8.0
            self.stats.hp_current = self.stats.hp_max
            self.stats.atk *= 2.0
            self.stats.def_stat *= 3.0
            self.stats.armure *= 2.0

    def take_damage(self, damage: float) -> bool:
        """
        L'ennemi prend des dégâts

        Returns:
            True si l'ennemi est mort
        """
        self.stats.hp_current -= damage
        return self.stats.hp_current <= 0

    def is_alive(self) -> bool:
        """Vérifie si l'ennemi est vivant"""
        return self.stats.hp_current > 0


class CombatSystem:
    """Gère le système de combat automatique"""

    def __init__(self, data_manager, item_generator: ItemGenerator):
        self.data = data_manager
        self.item_generator = item_generator
        self.current_enemy: Optional[Enemy] = None
        self.combat_active: bool = False
        self.combat_paused: bool = False
        self.auto_attack_timer: float = 0.0
        self.enemy_attack_timer: float = 0.0

        # Combat log (derniers événements)
        self.combat_log: List[str] = []
        self.max_log_entries: int = 10

        # Stats du combat actuel
        self.current_fight_damage_dealt: float = 0.0
        self.current_fight_damage_taken: float = 0.0
        self.current_fight_time: float = 0.0

    def start_combat(self, zone_id: str, spawn_boss: bool = False):
        """Démarre un combat dans une zone donnée"""
        zone = self.data.get_zone(zone_id)
        if not zone:
            return

        # Sélectionner un ennemi
        if spawn_boss:
            enemy_id = zone.get("boss")
        else:
            enemies = zone.get("enemies", [])
            if not enemies:
                return
            enemy_id = random.choice(enemies)

        enemy_data = self.data.get_enemy(enemy_id)
        if not enemy_data:
            return

        tier_data = self.data.get_tier(zone["tier"])

        self.current_enemy = Enemy(enemy_data, tier_data)
        self.combat_active = True
        self.combat_paused = False
        self.auto_attack_timer = 0.0
        self.enemy_attack_timer = 0.0

        # Reset stats du combat
        self.current_fight_damage_dealt = 0.0
        self.current_fight_damage_taken = 0.0
        self.current_fight_time = 0.0

        self.add_log(f"Combat commencé contre {self.current_enemy.name}!")

    def toggle_pause(self):
        """Met en pause ou reprend le combat"""
        if self.combat_active:
            self.combat_paused = not self.combat_paused
            if self.combat_paused:
                self.add_log("Combat mis en PAUSE")
            else:
                self.add_log("Combat REPRIS")

    def flee_combat(self, player) -> bool:
        """Fuit le combat avec pénalité"""
        if not self.combat_active:
            return False

        # Pénalité: perd 20% de l'or
        gold_lost = int(player.gold * 0.2)
        player.gold -= gold_lost

        self.add_log(f"Fuite! Vous perdez {gold_lost} or")
        self.combat_active = False
        self.combat_paused = False
        self.current_enemy = None

        player.combat_stats["deaths"] += 1

        return True

    def update(self, delta_time: float, player) -> Dict:
        """
        Met à jour le combat

        Returns:
            Dict avec les résultats: {
                "player_dead": bool,
                "enemy_dead": bool,
                "rewards": {...}
            }
        """
        if not self.combat_active or not self.current_enemy:
            return {"player_dead": False, "enemy_dead": False}

        # Si combat en pause, ne rien faire
        if self.combat_paused:
            return {"player_dead": False, "enemy_dead": False}

        self.current_fight_time += delta_time

        player_stats = player.get_total_stats()

        # Régénération
        CombatCalculator.apply_regen(player_stats, delta_time)
        player.base_stats.hp_current = player_stats.hp_current

        # Attaques du joueur
        self.auto_attack_timer += delta_time
        attack_interval = 1.0 / player_stats.vitesse_attaque

        if self.auto_attack_timer >= attack_interval:
            self.auto_attack_timer = 0.0
            self._player_attack(player_stats)

        # Attaques de l'ennemi
        self.enemy_attack_timer += delta_time
        enemy_attack_interval = 1.0 / self.current_enemy.stats.vitesse_attaque

        if self.enemy_attack_timer >= enemy_attack_interval:
            self.enemy_attack_timer = 0.0
            player_dead = self._enemy_attack(player, player_stats)

            if player_dead:
                return self._handle_player_death()

        # Vérifier si l'ennemi est mort
        if not self.current_enemy.is_alive():
            return self._handle_enemy_death(player)

        return {"player_dead": False, "enemy_dead": False}

    def _player_attack(self, player_stats: StatsContainer):
        """Le joueur attaque l'ennemi"""
        result = CombatCalculator.calculate_damage(
            player_stats,
            self.current_enemy.stats,
            self.current_enemy.is_boss
        )

        if result["dodged"]:
            self.add_log("Attaque esquivée!")
            return

        damage = result["damage"]
        crit_text = " CRITIQUE!" if result["is_crit"] else ""
        block_text = " (bloqué)" if result["blocked"] else ""

        self.current_enemy.take_damage(damage)
        self.current_fight_damage_dealt += damage
        self.add_log(f"Vous infligez {int(damage)} dégâts{crit_text}{block_text}")

        # Track stats
        if result["is_crit"]:
            # Stats de crit trackées via player dans le handler

        # Vol de vie
        if result.get("lifesteal", 0) > 0:
            pass  # Géré directement sur player dans update

        # Double coup proc
        if any(proc["type"] == "double_hit" for proc in result["procs"]):
            self.current_enemy.take_damage(damage * 0.5)
            self.add_log(f"Double coup! +{int(damage * 0.5)} dégâts")

    def _enemy_attack(self, player, player_stats: StatsContainer) -> bool:
        """L'ennemi attaque le joueur"""
        result = CombatCalculator.calculate_damage(
            self.current_enemy.stats,
            player_stats,
            False
        )

        if result["dodged"]:
            self.add_log(f"{self.current_enemy.name} manque son attaque!")
            return False

        damage = result["damage"]
        crit_text = " CRITIQUE!" if result["is_crit"] else ""

        player_dead = player.take_damage(damage)
        self.current_fight_damage_taken += damage
        self.add_log(f"{self.current_enemy.name} inflige {int(damage)} dégâts{crit_text}")

        # Épines
        if result.get("thorns_damage", 0) > 0:
            thorns = result["thorns_damage"]
            self.current_enemy.take_damage(thorns)
            self.add_log(f"Épines: {int(thorns)} dégâts renvoyés!")

        return player_dead

    def _handle_enemy_death(self, player) -> Dict:
        """Gère la mort de l'ennemi et les récompenses"""
        self.add_log(f"{self.current_enemy.name} vaincu!")

        # Track stats
        player.combat_stats["kills"] += 1
        player.combat_stats["damage_dealt"] += int(self.current_fight_damage_dealt)
        player.combat_stats["damage_taken"] += int(self.current_fight_damage_taken)
        if self.current_enemy.is_boss:
            player.combat_stats["boss_kills"] += 1

        # XP
        player.add_xp(self.current_enemy.xp_reward)

        # Or
        gold = random.randint(self.current_enemy.gold_min, self.current_enemy.gold_max)
        player.add_gold(gold)

        # Loot
        rewards = {
            "xp": self.current_enemy.xp_reward,
            "gold": gold,
            "items": [],
            "resources": []
        }

        # Items (selon chance)
        if random.random() * 100 < self.current_enemy.item_drop_chance:
            item = self.item_generator.generate_random_drop(
                self.current_enemy.tier,
                player.level
            )
            if item:
                player.add_item_to_inventory(item)
                rewards["items"].append(item)

        # Ressources (resource_drops)
        for res_drop in self.current_enemy.resource_drops:
            if random.random() * 100 < res_drop.get("chance_pct", 25):
                res_id = res_drop["resource"]
                quantity = random.randint(1, 3)
                player.add_resource(res_id, quantity)
                rewards["resources"].append({"id": res_id, "quantity": quantity})

        self.combat_active = False
        self.current_enemy = None

        return {
            "player_dead": False,
            "enemy_dead": True,
            "rewards": rewards
        }

    def _handle_player_death(self, player) -> Dict:
        """Gère la mort du joueur"""
        self.add_log("VOUS ÊTES MORT!")
        self.combat_active = False

        player.combat_stats["deaths"] += 1

        return {
            "player_dead": True,
            "enemy_dead": False
        }

    def add_log(self, message: str):
        """Ajoute un message au log de combat"""
        self.combat_log.append(message)
        if len(self.combat_log) > self.max_log_entries:
            self.combat_log.pop(0)

    def get_combat_log(self) -> List[str]:
        """Retourne les derniers messages du log"""
        return self.combat_log.copy()
