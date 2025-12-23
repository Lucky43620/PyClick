"""
Système de tooltip pour afficher les détails des items
"""

import arcade
from src.systems.item_system import Item

class ItemTooltip:
    """Affiche un tooltip avec les stats d'un item"""

    def __init__(self):
        self.COLOR_BG = (20, 15, 20, 230)
        self.COLOR_BORDER = (100, 80, 70)
        self.COLOR_TEXT = (220, 200, 180)
        self.COLOR_TEXT_DIM = (150, 130, 110)
        self.COLOR_STAT_POSITIVE = (100, 200, 100)
        self.COLOR_STAT_NEGATIVE = (200, 100, 100)

        self.RARITY_COLORS = {
            "common": (180, 180, 180),
            "uncommon": (100, 200, 100),
            "rare": (100, 150, 255),
            "epic": (200, 100, 255),
            "legendary": (255, 180, 50)
        }

    def draw(self, item: Item, x: int, y: int, data_manager):
        """Dessine le tooltip à la position donnée"""
        if not item:
            return

        # Dimensions
        width = 300
        base_height = 120
        num_affixes = len(item.affixes)
        height = base_height + num_affixes * 18 + 60  # Plus de place pour les stats de base

        # Ajuster position pour ne pas sortir de l'écran
        if x + width > 1600:
            x = 1600 - width - 10
        if y + height > 900:
            y = 900 - height - 10

        # Fond
        arcade.draw_lrbt_rectangle_filled(x, x + width, y, y + height, self.COLOR_BG)
        arcade.draw_lrbt_rectangle_outline(x, x + width, y, y + height, self.COLOR_BORDER, 2)

        # Nom de l'item (avec couleur de rareté)
        rarity_color = self.RARITY_COLORS.get(item.rarity_id, self.COLOR_TEXT)
        arcade.draw_text(item.name, x + 10, y + height - 25, rarity_color, 14, bold=True)

        # Ligne: Tier + Rareté + Qualité
        rarity_data = data_manager.get_rarity(item.rarity_id)
        quality_data = data_manager.get_quality(item.quality_id)
        rarity_name = rarity_data.get("name", item.rarity_id) if rarity_data else item.rarity_id
        quality_name = quality_data.get("name", item.quality_id) if quality_data else item.quality_id

        arcade.draw_text(f"{item.tier.upper()} | {rarity_name} | {quality_name}",
                        x + 10, y + height - 45, self.COLOR_TEXT_DIM, 10)

        # Slot et Level requirement
        arcade.draw_text(f"Slot: {item.slot} | Niveau requis: {item.level_requirement}",
                        x + 10, y + height - 60, self.COLOR_TEXT_DIM, 10)

        # Séparateur
        arcade.draw_line(x + 10, y + height - 70, x + width - 10, y + height - 70,
                        self.COLOR_BORDER, 1)

        # Stats de base
        current_y = y + height - 90
        total_stats = item.get_total_stats()

        # Afficher les stats principales non-nulles
        main_stats = [
            ("ATK", total_stats.atk),
            ("DEF", total_stats.def_stat),
            ("HP Max", total_stats.hp_max),
            ("Armure", total_stats.armure),
            ("Crit Chance", total_stats.crit_chance),
        ]

        for stat_name, stat_value in main_stats:
            if stat_value > 0:
                arcade.draw_text(f"+{stat_value:.1f} {stat_name}",
                               x + 10, current_y, self.COLOR_STAT_POSITIVE, 11)
                current_y -= 18

        # Affixes
        if item.affixes:
            arcade.draw_line(x + 10, current_y + 8, x + width - 10, current_y + 8,
                            self.COLOR_BORDER, 1)
            current_y -= 10

            for affix in item.affixes:
                arcade.draw_text(f"+{affix['rolled_value']:.1f} {affix['name']}",
                               x + 10, current_y, self.RARITY_COLORS.get(item.rarity_id, self.COLOR_TEXT), 10)
                current_y -= 18

        # Power score en bas
        arcade.draw_line(x + 10, current_y + 8, x + width - 10, current_y + 8,
                        self.COLOR_BORDER, 1)
        arcade.draw_text(f"Power: {int(item.power_score)} | Valeur: {item.gold_value} or",
                        x + 10, current_y - 8, self.COLOR_TEXT_DIM, 9)
