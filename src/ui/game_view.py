"""
Vue principale du jeu avec UI fantasy sombre
"""

import arcade
import arcade.gui
from typing import Optional
from src.ui.tooltip import ItemTooltip

class GameView(arcade.View):
    """Vue principale du jeu avec toutes les interfaces"""

    def __init__(self, player, data_manager, item_generator,
                 combat_system, gathering_system, crafting_system,
                 skill_system, station_upgrade_system, save_system):
        super().__init__()

        self.player = player
        self.data = data_manager
        self.item_gen = item_generator
        self.combat = combat_system
        self.gathering = gathering_system
        self.crafting = crafting_system
        self.skills = skill_system
        self.station_upgrades = station_upgrade_system
        self.save = save_system

        # UI Manager
        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()

        # Mode actuel
        self.current_mode = "combat"  # combat, gathering, crafting, inventory, upgrades

        # Initialiser les nodes de récolte pour la zone actuelle
        self.gathering.spawn_nodes_for_zone(self.player.current_zone_id, 5)

        # Démarrer un combat automatiquement
        self.combat.start_combat(self.player.current_zone_id, spawn_boss=False)

        # UI State
        self.selected_item_index: Optional[int] = None
        self.selected_recipe_index: Optional[int] = None
        self.show_player_stats: bool = False
        self.hovered_item: Optional[tuple] = None  # (item, x, y) pour tooltip
        self.tooltip = ItemTooltip()
        self.recipe_scroll_offset: int = 0  # Pour scroller les recettes

        # Crafting en cours
        self.crafting_in_progress: bool = False
        self.craft_timer: float = 0.0
        self.craft_duration: float = 0.0
        self.current_recipe_id: Optional[str] = None

        # Couleurs fantasy sombre
        self.COLOR_BG = (15, 10, 15)
        self.COLOR_PANEL = (30, 25, 30)
        self.COLOR_PANEL_LIGHT = (45, 35, 45)
        self.COLOR_BORDER = (80, 60, 50)
        self.COLOR_TEXT = (220, 200, 180)
        self.COLOR_TEXT_DIM = (150, 130, 110)
        self.COLOR_HIGHLIGHT = (200, 150, 50)

        self.COLOR_HP = (180, 40, 40)
        self.COLOR_HP_BG = (80, 20, 20)
        self.COLOR_XP = (50, 150, 200)
        self.COLOR_XP_BG = (20, 60, 80)

        # Rareté colors
        self.RARITY_COLORS = {
            "common": (180, 180, 180),
            "uncommon": (100, 200, 100),
            "rare": (100, 150, 255),
            "epic": (200, 100, 255),
            "legendary": (255, 180, 50)
        }

    def on_show_view(self):
        """Appelé quand la vue devient active"""
        arcade.set_background_color(self.COLOR_BG)

    def on_hide_view(self):
        """Appelé quand la vue devient inactive"""
        self.ui_manager.disable()

    def on_update(self, delta_time: float):
        """Update de la logique du jeu"""
        # Update gathering
        self.gathering.update(delta_time)

        # Update player buffs
        self.player.update_buffs(delta_time)

        # Update combat si actif
        if self.combat.combat_active and self.current_mode == "combat":
            result = self.combat.update(delta_time, self.player)

            if result.get("player_dead"):
                self._handle_player_death()

            if result.get("enemy_dead"):
                # Spawn un nouvel ennemi après 1 seconde
                # Pour l'instant, spawn immédiatement
                self.combat.start_combat(self.player.current_zone_id, spawn_boss=False)

        # Auto-save
        self.save.update_auto_save(delta_time, self.player, self.skills, self.station_upgrades)

    def _handle_player_death(self):
        """Gère la mort du joueur"""
        # Respawn avec pénalité
        self.player.base_stats.hp_current = self.player.base_stats.hp_max * 0.5
        self.player.gold = int(self.player.gold * 0.9)  # Perd 10% de l'or
        print("Vous êtes mort! -10% or")

    def on_draw(self):
        """Dessine l'interface"""
        self.clear()

        # Dessiner selon le mode
        if self.current_mode == "combat":
            self._draw_combat_view()
        elif self.current_mode == "gathering":
            self._draw_gathering_view()
        elif self.current_mode == "crafting":
            self._draw_crafting_view()
        elif self.current_mode == "inventory":
            self._draw_inventory_view()
        elif self.current_mode == "upgrades":
            self._draw_upgrades_view()

        # HUD permanent (en haut)
        self._draw_hud()

        # Boutons de navigation (en bas)
        self._draw_nav_buttons()

    def _draw_rect_filled(self, x, y, width, height, color):
        """Helper pour dessiner un rectangle rempli (x, y, width, height)"""
        arcade.draw_lrbt_rectangle_filled(x, x + width, y, y + height, color)

    def _draw_rect_outline(self, x, y, width, height, color, border_width=2):
        """Helper pour dessiner un contour de rectangle"""
        arcade.draw_lrbt_rectangle_outline(x, x + width, y, y + height, color, border_width)

    def _draw_hud(self):
        """Dessine le HUD en haut de l'écran"""
        width = self.window.width
        hud_height = 100
        hud_y = self.window.height - hud_height

        # Panel du HUD
        self._draw_rect_filled(0, hud_y, width, hud_height, self.COLOR_PANEL)
        self._draw_rect_outline(0, hud_y, width, hud_height, self.COLOR_BORDER, 2)

        # Stats du joueur
        stats = self.player.get_total_stats()
        y = self.window.height - 25

        # Nom et niveau
        arcade.draw_text(f"{self.player.name} - Niveau {self.player.level}",
                        20, y, self.COLOR_HIGHLIGHT, 16, bold=True)

        # Barre de HP
        y -= 25
        hp_percent = stats.hp_current / stats.hp_max
        self._draw_bar(20, y, 250, 20, hp_percent, self.COLOR_HP, self.COLOR_HP_BG)
        arcade.draw_text(f"HP: {int(stats.hp_current)}/{int(stats.hp_max)}",
                        30, y + 3, self.COLOR_TEXT, 12, bold=True)

        # Barre d'XP
        y -= 25
        xp_percent = self.player.xp / self.player.xp_to_next_level
        self._draw_bar(20, y, 250, 20, xp_percent, self.COLOR_XP, self.COLOR_XP_BG)
        arcade.draw_text(f"XP: {self.player.xp}/{self.player.xp_to_next_level}",
                        30, y + 3, self.COLOR_TEXT, 12, bold=True)

        # Or et zone
        y = self.window.height - 25
        x = 320
        arcade.draw_text(f"Or: {self.player.gold}", x, y, self.COLOR_HIGHLIGHT, 14, bold=True)

        zone = self.data.get_zone(self.player.current_zone_id)
        if zone:
            y -= 25
            arcade.draw_text(f"Zone: {zone['name']}", x, y, self.COLOR_TEXT, 12)
            y -= 20
            arcade.draw_text(f"{zone['desc']}", x, y, self.COLOR_TEXT_DIM, 10, width=400)

        # Stats de combat (droite)
        x = width - 300
        y = self.window.height - 25
        arcade.draw_text(f"ATK: {int(stats.atk)}  DEF: {int(stats.def_stat)}", x, y, self.COLOR_TEXT, 12)
        y -= 20
        arcade.draw_text(f"Crit: {stats.crit_chance:.1f}%  Esq: {stats.esquive:.1f}%", x, y, self.COLOR_TEXT, 12)

    def _draw_nav_buttons(self):
        """Dessine les boutons de navigation"""
        width = self.window.width
        button_width = width // 5  # 5 boutons maintenant
        button_height = 50

        buttons = [
            ("COMBAT", "combat"),
            ("RÉCOLTE", "gathering"),
            ("CRAFT", "crafting"),
            ("INVENTAIRE", "inventory"),
            ("UPGRADES", "upgrades")
        ]

        for i, (label, mode) in enumerate(buttons):
            x = i * button_width
            color = self.COLOR_HIGHLIGHT if mode == self.current_mode else self.COLOR_PANEL_LIGHT

            arcade.draw_lrbt_rectangle_filled(x, x + button_width, 0, button_height, color)
            arcade.draw_lrbt_rectangle_outline(x, x + button_width, 0, button_height, self.COLOR_BORDER, 2)

            text_x = x + button_width // 2
            arcade.draw_text(label, text_x, button_height // 2 - 7, self.COLOR_TEXT, 14,
                           bold=(mode == self.current_mode), anchor_x="center")

    def _draw_combat_view(self):
        """Vue de combat"""
        width = self.window.width
        height = self.window.height - 150  # HUD + nav buttons

        # Zone de combat principale
        combat_y = height - 200
        combat_x = width // 2

        if self.combat.current_enemy:
            enemy = self.combat.current_enemy

            # Nom de l'ennemi
            name_color = self.COLOR_HIGHLIGHT if enemy.is_boss else self.COLOR_TEXT
            arcade.draw_text(enemy.name, combat_x, combat_y + 80, name_color, 20,
                           bold=enemy.is_boss, anchor_x="center")

            # Barre de HP de l'ennemi
            hp_percent = enemy.stats.hp_current / enemy.stats.hp_max
            bar_width = 400
            self._draw_bar(combat_x - bar_width // 2, combat_y + 50, bar_width, 30,
                          hp_percent, self.COLOR_HP, self.COLOR_HP_BG)
            arcade.draw_text(f"{int(enemy.stats.hp_current)}/{int(enemy.stats.hp_max)}",
                           combat_x, combat_y + 58, self.COLOR_TEXT, 14,
                           bold=True, anchor_x="center")

            # Représentation visuelle de l'ennemi (placeholder)
            enemy_size = 100 if enemy.is_boss else 60
            arcade.draw_circle_filled(combat_x, combat_y - 50, enemy_size, (120, 40, 40))
            arcade.draw_circle_outline(combat_x, combat_y - 50, enemy_size, self.COLOR_BORDER, 3)

        # Log de combat
        log_x = 50
        log_y = combat_y - 200
        arcade.draw_text("Combat Log:", log_x, log_y + 180, self.COLOR_HIGHLIGHT, 14, bold=True)

        arcade.draw_lrbt_rectangle_filled(log_x, log_x + 500, log_y, log_y + 160,
                                         self.COLOR_PANEL)
        arcade.draw_lrbt_rectangle_outline(log_x, log_x + 500, log_y, log_y + 160,
                                          self.COLOR_BORDER, 2)

        combat_log = self.combat.get_combat_log()
        for i, message in enumerate(reversed(combat_log)):
            arcade.draw_text(message, log_x + 10, log_y + 140 - i * 15, self.COLOR_TEXT, 11)

        # Boutons d'action de combat
        button_y = combat_y - 180
        button_width = 140
        button_height = 45
        button_spacing = 15

        # Bouton PAUSE/RESUME
        pause_button_x = width - 500
        pause_color = self.COLOR_HIGHLIGHT if self.combat.combat_paused else self.COLOR_PANEL_LIGHT
        pause_text = "REPRENDRE" if self.combat.combat_paused else "PAUSE"

        arcade.draw_lrbt_rectangle_filled(pause_button_x, pause_button_x + button_width,
                                         button_y, button_y + button_height, pause_color)
        arcade.draw_lrbt_rectangle_outline(pause_button_x, pause_button_x + button_width,
                                          button_y, button_y + button_height, self.COLOR_BORDER, 2)
        arcade.draw_text(pause_text, pause_button_x + button_width // 2, button_y + 15,
                        self.COLOR_TEXT, 11, bold=True, anchor_x="center")

        # Bouton FUIR
        flee_button_x = pause_button_x + button_width + button_spacing
        arcade.draw_lrbt_rectangle_filled(flee_button_x, flee_button_x + button_width,
                                         button_y, button_y + button_height, (140, 40, 40))
        arcade.draw_lrbt_rectangle_outline(flee_button_x, flee_button_x + button_width,
                                          button_y, button_y + button_height, self.COLOR_BORDER, 2)
        arcade.draw_text("FUIR (-20% OR)", flee_button_x + button_width // 2, button_y + 15,
                        self.COLOR_TEXT, 11, bold=True, anchor_x="center")

        # Bouton SPAWN BOSS
        boss_button_x = flee_button_x + button_width + button_spacing
        arcade.draw_lrbt_rectangle_filled(boss_button_x, boss_button_x + button_width,
                                         button_y, button_y + button_height, self.COLOR_PANEL_LIGHT)
        arcade.draw_lrbt_rectangle_outline(boss_button_x, boss_button_x + button_width,
                                          button_y, button_y + button_height, self.COLOR_BORDER, 2)
        arcade.draw_text("SPAWN BOSS", boss_button_x + button_width // 2, button_y + 15,
                        self.COLOR_HIGHLIGHT, 11, bold=True, anchor_x="center")

        # Panneau de stats de combat (à droite)
        stats_x = width - 350
        stats_y = combat_y + 80
        stats_width = 320
        stats_height = 200

        arcade.draw_lrbt_rectangle_filled(stats_x, stats_x + stats_width,
                                         stats_y, stats_y + stats_height, self.COLOR_PANEL)
        arcade.draw_lrbt_rectangle_outline(stats_x, stats_x + stats_width,
                                          stats_y, stats_y + stats_height, self.COLOR_BORDER, 2)

        arcade.draw_text("Stats de Combat", stats_x + 10, stats_y + stats_height - 25,
                        self.COLOR_HIGHLIGHT, 13, bold=True)

        # Stats du combat actuel
        current_y = stats_y + stats_height - 50
        if self.combat.combat_active and self.combat.current_enemy:
            arcade.draw_text("Combat actuel:", stats_x + 10, current_y, self.COLOR_TEXT, 11, bold=True)
            current_y -= 20

            fight_time = int(self.combat.current_fight_time)
            arcade.draw_text(f"Duree: {fight_time}s", stats_x + 15, current_y, self.COLOR_TEXT, 10)
            current_y -= 18

            dmg_dealt = int(self.combat.current_fight_damage_dealt)
            arcade.draw_text(f"Degats infliges: {dmg_dealt}", stats_x + 15, current_y, (100, 200, 100), 10)
            current_y -= 18

            dmg_taken = int(self.combat.current_fight_damage_taken)
            arcade.draw_text(f"Degats recus: {dmg_taken}", stats_x + 15, current_y, (200, 100, 100), 10)
            current_y -= 25

        # Stats globales
        arcade.draw_text("Stats totales:", stats_x + 10, current_y, self.COLOR_TEXT, 11, bold=True)
        current_y -= 20

        arcade.draw_text(f"Kills: {self.player.combat_stats['kills']}",
                        stats_x + 15, current_y, self.COLOR_TEXT, 10)
        current_y -= 18

        arcade.draw_text(f"Boss vaincus: {self.player.combat_stats['boss_kills']}",
                        stats_x + 15, current_y, self.COLOR_HIGHLIGHT, 10)
        current_y -= 18

        arcade.draw_text(f"Morts: {self.player.combat_stats['deaths']}",
                        stats_x + 15, current_y, (200, 100, 100), 10)
        current_y -= 18

        total_dmg = self.player.combat_stats['damage_dealt']
        arcade.draw_text(f"Degats total: {total_dmg}",
                        stats_x + 15, current_y, (150, 150, 150), 9)

        # SÉLECTEUR DE ZONE (en bas à droite)
        zone_panel_width = 400
        zone_panel_height = 150
        zone_panel_x = width - zone_panel_width - 20
        zone_panel_y = 70  # Juste au-dessus des boutons de nav

        arcade.draw_lrbt_rectangle_filled(
            zone_panel_x, zone_panel_x + zone_panel_width,
            zone_panel_y, zone_panel_y + zone_panel_height,
            self.COLOR_PANEL
        )
        arcade.draw_lrbt_rectangle_outline(
            zone_panel_x, zone_panel_x + zone_panel_width,
            zone_panel_y, zone_panel_y + zone_panel_height,
            self.COLOR_BORDER, 2
        )

        arcade.draw_text("Sélection de Zone", zone_panel_x + 10, zone_panel_y + zone_panel_height - 20,
                        self.COLOR_HIGHLIGHT, 13, bold=True)

        # Zone actuelle
        current_zone = self.data.get_zone(self.player.current_zone_id)
        if current_zone:
            arcade.draw_text(f"Actuelle: {current_zone['name']} (T{current_zone['tier'][1:]})",
                           zone_panel_x + 10, zone_panel_y + zone_panel_height - 45,
                           self.COLOR_TEXT, 11)

        # Boutons de navigation de zone
        btn_width = 120
        btn_height = 35
        btn_y = zone_panel_y + 20

        # Bouton ZONE PRÉCÉDENTE
        prev_btn_x = zone_panel_x + 20
        arcade.draw_lrbt_rectangle_filled(
            prev_btn_x, prev_btn_x + btn_width,
            btn_y, btn_y + btn_height,
            self.COLOR_PANEL_LIGHT
        )
        arcade.draw_lrbt_rectangle_outline(
            prev_btn_x, prev_btn_x + btn_width,
            btn_y, btn_y + btn_height,
            self.COLOR_BORDER, 2
        )
        arcade.draw_text("◄ ZONE PRÉC", prev_btn_x + btn_width // 2, btn_y + 10,
                        self.COLOR_TEXT, 10, bold=True, anchor_x="center")

        # Bouton ZONE SUIVANTE
        next_btn_x = prev_btn_x + btn_width + 20
        # Vérifier si la zone suivante est débloquée
        zones = self.data.zones
        current_idx = next((i for i, z in enumerate(zones) if z["id"] == self.player.current_zone_id), 0)
        next_zone = zones[(current_idx + 1) % len(zones)]
        can_access = self.player.level >= next_zone.get("level_requirement", 1)

        btn_color = self.COLOR_HIGHLIGHT if can_access else (60, 60, 60)
        arcade.draw_lrbt_rectangle_filled(
            next_btn_x, next_btn_x + btn_width,
            btn_y, btn_y + btn_height,
            btn_color
        )
        arcade.draw_lrbt_rectangle_outline(
            next_btn_x, next_btn_x + btn_width,
            btn_y, btn_y + btn_height,
            self.COLOR_BORDER, 2
        )
        arcade.draw_text("ZONE SUIV ►", next_btn_x + btn_width // 2, btn_y + 10,
                        self.COLOR_TEXT if can_access else self.COLOR_TEXT_DIM,
                        10, bold=True, anchor_x="center")

        # Info zone suivante
        if not can_access:
            arcade.draw_text(f"Requis: Level {next_zone.get('level_requirement', 1)}",
                           next_btn_x + btn_width // 2, btn_y - 15,
                           (200, 100, 100), 9, anchor_x="center")

    def _draw_gathering_view(self):
        """Vue de récolte"""
        width = self.window.width
        height = self.window.height - 150

        # Titre
        arcade.draw_text("Nodes de Récolte", width // 2, height - 30, self.COLOR_HIGHLIGHT, 18,
                        bold=True, anchor_x="center")

        # Grille de nodes
        nodes = self.gathering.get_nodes_status()
        cols = 3
        node_width = 250
        node_height = 120
        spacing = 20

        start_x = (width - (cols * node_width + (cols - 1) * spacing)) // 2
        start_y = height - 100

        for i, node_status in enumerate(nodes):
            row = i // cols
            col = i % cols

            x = start_x + col * (node_width + spacing)
            y = start_y - row * (node_height + spacing)

            # Panel du node
            color = self.COLOR_PANEL if not node_status["depleted"] else self.COLOR_PANEL_LIGHT
            arcade.draw_lrbt_rectangle_filled(x, x + node_width, y, y + node_height, color)
            arcade.draw_lrbt_rectangle_outline(x, x + node_width, y, y + node_height, self.COLOR_BORDER, 2)

            if node_status["depleted"]:
                # Node déplété
                arcade.draw_text("ÉPUISÉ", x + node_width // 2, y + node_height // 2,
                               self.COLOR_TEXT_DIM, 14, bold=True, anchor_x="center")
                arcade.draw_text(f"Respawn: {node_status['respawn_time']:.1f}s",
                               x + node_width // 2, y + node_height // 2 - 20,
                               self.COLOR_TEXT_DIM, 11, anchor_x="center")
            else:
                # Nom du node
                arcade.draw_text(node_status["name"], x + node_width // 2, y + node_height - 20,
                               self.COLOR_TEXT, 12, bold=True, anchor_x="center")

                # Ressource
                res = self.data.get_resource(node_status["resource_id"])
                res_name = res.get("name", node_status["resource_id"]) if res else node_status["resource_id"]
                arcade.draw_text(f"→ {res_name}", x + node_width // 2, y + node_height - 40,
                               self.COLOR_HIGHLIGHT, 10, anchor_x="center")

                # Barre de HP
                hp_pct = node_status["hp_percent"] / 100.0
                self._draw_bar(x + 10, y + 30, node_width - 20, 20, hp_pct,
                             (100, 150, 100), (40, 60, 40))

                # Bouton cliquer
                arcade.draw_text("[ Cliquer pour récolter ]", x + node_width // 2, y + 8,
                               self.COLOR_TEXT_DIM, 10, anchor_x="center")

    def _draw_crafting_view(self):
        """Vue de crafting"""
        width = self.window.width
        height = self.window.height - 150

        # Stations débloquées
        arcade.draw_text("Stations de Craft", 20, height - 30, self.COLOR_HIGHLIGHT, 16, bold=True)

        y = height - 60
        for station_id in self.player.unlocked_stations:
            station = self.data.get_station(station_id)
            if station:
                arcade.draw_text(f"• {station['name']}", 30, y, self.COLOR_TEXT, 12)
                y -= 20

        # Recettes disponibles
        recipes = self.crafting.get_available_recipes(self.player)
        total_recipes = len(recipes)

        arcade.draw_text(f"Recettes ({total_recipes} disponibles)", width // 2, height - 30,
                        self.COLOR_HIGHLIGHT, 16, bold=True, anchor_x="center")

        # Instructions de navigation
        if total_recipes > 8:
            arcade.draw_text("[ UP/DOWN ou Molette pour naviguer ]", width // 2, height - 50,
                           self.COLOR_TEXT_DIM, 10, anchor_x="center")

        recipe_y = height - 80
        recipe_width = 600
        recipe_height = 70  # Réduit pour afficher plus
        recipe_x = (width - recipe_width) // 2
        max_display = 8  # Afficher 8 recettes à la fois

        # Assurer que l'offset reste dans les limites
        max_offset = max(0, total_recipes - max_display)
        self.recipe_scroll_offset = max(0, min(self.recipe_scroll_offset, max_offset))

        # Afficher les recettes avec offset
        displayed_recipes = recipes[self.recipe_scroll_offset:self.recipe_scroll_offset + max_display]
        for i, recipe_info in enumerate(displayed_recipes):
            recipe = recipe_info["recipe"]
            can_craft = recipe_info["can_craft"]

            y = recipe_y - i * (recipe_height + 10)

            # Panel
            color = self.COLOR_PANEL_LIGHT if can_craft else self.COLOR_PANEL
            arcade.draw_lrbt_rectangle_filled(recipe_x, recipe_x + recipe_width, y, y + recipe_height, color)
            arcade.draw_lrbt_rectangle_outline(recipe_x, recipe_x + recipe_width, y, y + recipe_height,
                                              self.COLOR_BORDER, 2)

            # Nom de la recette (depuis l'output)
            outputs = recipe.get("outputs", [])
            if outputs and "item_base" in outputs[0]:
                item_base = self.data.get_item_base(outputs[0]["item_base"])
                output_name = item_base.get("name", "???") if item_base else "???"
            else:
                output_name = recipe.get("id", "???")

            arcade.draw_text(output_name, recipe_x + 10, y + recipe_height - 25,
                           self.COLOR_HIGHLIGHT if can_craft else self.COLOR_TEXT_DIM, 14, bold=True)

            # Coûts (format: inputs avec resource et qty)
            cost_text = ""
            for res in recipe.get("inputs", [])[:3]:  # Afficher 3 premières ressources
                res_data = self.data.get_resource(res["resource"])
                res_name = res_data.get("name", res["resource"]) if res_data else res["resource"]
                cost_text += f"{res['qty']}x {res_name}, "

            if recipe.get("gold_cost", 0) > 0:
                cost_text += f"{recipe['gold_cost']} or"

            arcade.draw_text(cost_text.rstrip(", "), recipe_x + 10, y + recipe_height - 50,
                           self.COLOR_TEXT if can_craft else self.COLOR_TEXT_DIM, 10)

            # Status
            if can_craft:
                arcade.draw_text("[ Cliquer pour crafter ]", recipe_x + recipe_width - 150, y + 20,
                               self.COLOR_HIGHLIGHT, 11)
            else:
                arcade.draw_text(recipe_info["reason"], recipe_x + recipe_width - 200, y + 20,
                               self.COLOR_TEXT_DIM, 10)

        # Scroll bar visuelle si plus de 8 recettes
        if total_recipes > max_display:
            scrollbar_x = recipe_x + recipe_width + 15
            scrollbar_height = max_display * (recipe_height + 10) - 10
            scrollbar_y_top = recipe_y
            scrollbar_y_bottom = scrollbar_y_top - scrollbar_height
            scrollbar_width = 12

            # Background de la scrollbar
            arcade.draw_lrbt_rectangle_filled(
                scrollbar_x, scrollbar_x + scrollbar_width,
                scrollbar_y_bottom, scrollbar_y_top,
                self.COLOR_PANEL
            )
            arcade.draw_lrbt_rectangle_outline(
                scrollbar_x, scrollbar_x + scrollbar_width,
                scrollbar_y_bottom, scrollbar_y_top,
                self.COLOR_BORDER, 1
            )

            # Thumb de la scrollbar
            scroll_percent = self.recipe_scroll_offset / max_offset if max_offset > 0 else 0
            visible_percent = max_display / total_recipes
            thumb_height = max(20, scrollbar_height * visible_percent)
            thumb_travel = scrollbar_height - thumb_height
            thumb_y_top = scrollbar_y_top - (thumb_travel * scroll_percent)
            thumb_y_bottom = thumb_y_top - thumb_height

            arcade.draw_lrbt_rectangle_filled(
                scrollbar_x + 2, scrollbar_x + scrollbar_width - 2,
                thumb_y_bottom, thumb_y_top,
                self.COLOR_HIGHLIGHT
            )

            # Indicateur de position
            arcade.draw_text(
                f"{self.recipe_scroll_offset + 1}-{min(self.recipe_scroll_offset + max_display, total_recipes)} / {total_recipes}",
                scrollbar_x, scrollbar_y_bottom - 20,
                self.COLOR_TEXT_DIM, 9, anchor_x="left"
            )

    def _draw_inventory_view(self):
        """Vue d'inventaire et équipement"""
        width = self.window.width
        height = self.window.height - 150

        # Équipement (gauche)
        equip_x = 50
        equip_y = height - 50

        arcade.draw_text("Équipement", equip_x, equip_y, self.COLOR_HIGHLIGHT, 16, bold=True)

        slot_names = {
            "weapon": "Arme",
            "helmet": "Casque",
            "chest": "Armure",
            "legs": "Jambes",
            "boots": "Bottes",
            "gloves": "Gants",
            "ring1": "Anneau 1",
            "ring2": "Anneau 2",
            "amulet": "Amulette"
        }

        y = equip_y - 30
        for slot, label in slot_names.items():
            item = self.player.equipment.get(slot)

            if item and hasattr(item, 'name'):
                rarity_color = self.RARITY_COLORS.get(item.rarity_id, self.COLOR_TEXT)
                arcade.draw_text(f"{label}: {item.name}", equip_x, y, rarity_color, 11)
            else:
                arcade.draw_text(f"{label}: [Vide]", equip_x, y, self.COLOR_TEXT_DIM, 11)

            y -= 25

        # Potions et buffs (gauche, en dessous équipement)
        potion_y = y - 30
        arcade.draw_text("Potions", equip_x, potion_y, self.COLOR_HIGHLIGHT, 14, bold=True)
        potion_y -= 25

        if self.player.potions:
            for potion_id, qty in list(self.player.potions.items())[:5]:  # Afficher 5 premières
                item_base = self.data.get_item_base(potion_id)
                potion_name = item_base.get("name", potion_id) if item_base else potion_id
                arcade.draw_text(f"[{qty}x] {potion_name}", equip_x, potion_y, (100, 200, 255), 10)
                potion_y -= 18
        else:
            arcade.draw_text("Aucune potion", equip_x, potion_y, self.COLOR_TEXT_DIM, 10)

        # Buffs actifs
        if self.player.buffs:
            buff_y = potion_y - 20
            arcade.draw_text("Buffs actifs:", equip_x, buff_y, self.COLOR_HIGHLIGHT, 12, bold=True)
            buff_y -= 20

            for buff in self.player.buffs[:3]:  # Afficher 3 premiers buffs
                buff_type = buff.get("type")
                buff_value = buff.get("value")
                time_left = int(buff.get("remaining", 0))
                arcade.draw_text(f"+{buff_value} {buff_type} ({time_left}s)",
                               equip_x, buff_y, (255, 200, 100), 10)
                buff_y -= 18

        # Inventaire (centre-droit)
        inv_x = 350
        inv_y = height - 50

        arcade.draw_text(f"Inventaire ({len(self.player.inventory)}/{self.player.inventory_size})",
                        inv_x, inv_y, self.COLOR_HIGHLIGHT, 16, bold=True)

        # Grille d'inventaire
        cols = 5
        item_size = 60
        spacing = 10

        for i, item in enumerate(self.player.inventory):
            row = i // cols
            col = i % cols

            x = inv_x + col * (item_size + spacing)
            y = inv_y - 40 - row * (item_size + spacing)

            # Case d'item
            rarity_color = self.RARITY_COLORS.get(item.rarity_id, self.COLOR_TEXT)
            arcade.draw_lrbt_rectangle_filled(x, x + item_size, y, y + item_size, self.COLOR_PANEL)
            arcade.draw_lrbt_rectangle_outline(x, x + item_size, y, y + item_size, rarity_color, 2)

            # Icône simplifiée (première lettre du slot)
            icon = item.slot[0].upper()
            arcade.draw_text(icon, x + item_size // 2, y + item_size // 2 - 8,
                           rarity_color, 20, bold=True, anchor_x="center")

        # Ressources (bas) - Couleurs selon rareté
        res_y = 200
        arcade.draw_text("Ressources:", 50, res_y, self.COLOR_HIGHLIGHT, 14, bold=True)

        res_x = 50
        res_y -= 25
        col = 0

        # Couleurs selon rareté de ressource
        rarity_colors_res = {
            "commun": self.COLOR_TEXT,
            "rare": (100, 150, 255),  # Bleu
            "epic": (200, 100, 255),   # Violet
            "legendary": (255, 180, 50)  # Or
        }

        for res_id, quantity in list(self.player.resources.items())[:20]:  # 20 ressources
            res_data = self.data.get_resource(res_id)
            res_name = res_data.get("name", res_id) if res_data else res_id
            res_rarity = res_data.get("rarity", "commun") if res_data else "commun"

            color = rarity_colors_res.get(res_rarity, self.COLOR_TEXT)
            arcade.draw_text(f"{res_name}: {quantity}", res_x + col * 210, res_y - (col // 4) * 18,
                           color, 9)
            col += 1

    def _draw_bar(self, x, y, width, height, percent, color, bg_color):
        """Dessine une barre de progression"""
        # Fond
        arcade.draw_lrbt_rectangle_filled(x, x + width, y, y + height, bg_color)

        # Remplissage
        fill_width = width * max(0.0, min(1.0, percent))
        if fill_width > 0:
            arcade.draw_lrbt_rectangle_filled(x, x + fill_width, y, y + height, color)

        # Bordure
        arcade.draw_lrbt_rectangle_outline(x, x + width, y, y + height, self.COLOR_BORDER, 2)

    def on_mouse_press(self, x, y, button, modifiers):
        """Gère les clics de souris"""
        width = self.window.width
        height = self.window.height

        # Navigation buttons
        if y < 50:
            button_width = width // 5  # 5 boutons maintenant
            button_index = int(x // button_width)
            modes = ["combat", "gathering", "crafting", "inventory", "upgrades"]
            if 0 <= button_index < len(modes):
                self.current_mode = modes[button_index]

                # Respawn nodes si on va sur gathering
                if self.current_mode == "gathering":
                    if not self.gathering.active_nodes:
                        self.gathering.spawn_nodes_for_zone(self.player.current_zone_id, 5)

                # Redémarrer un combat si on revient sur combat et qu'il n'y en a pas
                elif self.current_mode == "combat":
                    if not self.combat.combat_active:
                        self.combat.start_combat(self.player.current_zone_id, spawn_boss=False)

                return

        # Clics spécifiques selon le mode
        if self.current_mode == "combat":
            self._handle_combat_click(x, y, button)
        elif self.current_mode == "gathering":
            self._handle_gathering_click(x, y, button)
        elif self.current_mode == "crafting":
            self._handle_crafting_click(x, y, button)
        elif self.current_mode == "inventory":
            self._handle_inventory_click(x, y, button)
        elif self.current_mode == "upgrades":
            self._handle_upgrades_click(x, y, button)

    def _handle_combat_click(self, x, y, button):
        """Gère les clics en mode combat"""
        if button != arcade.MOUSE_BUTTON_LEFT:
            return
        width = self.window.width
        height = self.window.height - 150

        combat_y = height - 200
        button_y = combat_y - 180
        button_width = 140
        button_height = 45
        button_spacing = 15

        # Bouton PAUSE
        pause_button_x = width - 500
        if (pause_button_x <= x <= pause_button_x + button_width and
            button_y <= y <= button_y + button_height):
            if self.combat.combat_active:
                self.combat.toggle_pause()
            return

        # Bouton FUIR
        flee_button_x = pause_button_x + button_width + button_spacing
        if (flee_button_x <= x <= flee_button_x + button_width and
            button_y <= y <= button_y + button_height):
            if self.combat.combat_active:
                self.combat.flee_combat(self.player)
            return

        # Bouton SPAWN BOSS
        boss_button_x = flee_button_x + button_width + button_spacing
        if (boss_button_x <= x <= boss_button_x + button_width and
            button_y <= y <= button_y + button_height):
            # Spawn un boss
            self.combat.combat_active = False
            self.combat.start_combat(self.player.current_zone_id, spawn_boss=True)
            return

        # Boutons de changement de zone (en bas à droite)
        zone_panel_width = 400
        zone_panel_x = width - zone_panel_width - 20
        zone_panel_y = 70
        zone_btn_width = 120
        zone_btn_height = 35
        zone_btn_y = zone_panel_y + 20

        # Bouton ZONE PRÉCÉDENTE
        prev_btn_x = zone_panel_x + 20
        if (prev_btn_x <= x <= prev_btn_x + zone_btn_width and
            zone_btn_y <= y <= zone_btn_y + zone_btn_height):
            self._change_zone(-1)
            return

        # Bouton ZONE SUIVANTE
        next_btn_x = prev_btn_x + zone_btn_width + 20
        if (next_btn_x <= x <= next_btn_x + zone_btn_width and
            zone_btn_y <= y <= zone_btn_y + zone_btn_height):
            # Vérifier si on peut accéder à la zone suivante
            zones = self.data.zones
            current_idx = next((i for i, z in enumerate(zones) if z["id"] == self.player.current_zone_id), 0)
            next_zone = zones[(current_idx + 1) % len(zones)]

            if self.player.level >= next_zone.get("level_requirement", 1):
                self._change_zone(1)
            else:
                print(f"Zone verrouillée! Requis: Level {next_zone.get('level_requirement', 1)}")
            return

    def _handle_gathering_click(self, x, y, button):
        """Gère les clics en mode récolte"""
        if button != arcade.MOUSE_BUTTON_LEFT:
            return
        width = self.window.width
        height = self.window.height - 150

        nodes = self.gathering.get_nodes_status()
        cols = 3
        node_width = 250
        node_height = 120
        spacing = 20

        start_x = (width - (cols * node_width + (cols - 1) * spacing)) // 2
        start_y = height - 100

        for i, node_status in enumerate(nodes):
            if node_status["depleted"]:
                continue

            row = i // cols
            col = i % cols

            nx = start_x + col * (node_width + spacing)
            ny = start_y - row * (node_height + spacing)

            if nx <= x <= nx + node_width and ny <= y <= ny + node_height:
                # Clic sur ce node
                reward = self.gathering.harvest_node(i, self.player)
                if reward:
                    print(f"Récolté: {reward['quantity']}x {reward['resource_id']} (+{reward['xp']} XP)")
                break

    def _handle_crafting_click(self, x, y, button):
        """Gère les clics en mode crafting"""
        if button != arcade.MOUSE_BUTTON_LEFT:
            return
        width = self.window.width
        height = self.window.height - 150

        recipes = self.crafting.get_available_recipes(self.player)
        recipe_y = height - 80
        recipe_width = 600
        recipe_height = 70
        recipe_x = (width - recipe_width) // 2
        max_display = 8

        # Utiliser le même offset que pour l'affichage
        displayed_recipes = recipes[self.recipe_scroll_offset:self.recipe_scroll_offset + max_display]
        for i, recipe_info in enumerate(displayed_recipes):
            if not recipe_info["can_craft"]:
                continue

            ry = recipe_y - i * (recipe_height + 10)

            if recipe_x <= x <= recipe_x + recipe_width and ry <= y <= ry + recipe_height:
                # Craft!
                item = self.crafting.craft_item(recipe_info["recipe"]["id"], self.player)
                if item:
                    self.player.add_item_to_inventory(item)
                    print(f"Crafté: {item.name}")
                break

    def _handle_inventory_click(self, x, y, button):
        """Gère les clics en mode inventaire"""
        height = self.window.height - 150
        equip_x = 50

        # Clic droit sur équipement pour déséquiper
        if button == arcade.MOUSE_BUTTON_RIGHT:
            equip_y = height - 50
            slot_names = {
                "weapon": "Arme",
                "helmet": "Casque",
                "chest": "Armure",
                "legs": "Jambes",
                "boots": "Bottes",
                "gloves": "Gants",
                "ring1": "Anneau 1",
                "ring2": "Anneau 2",
                "amulet": "Amulette"
            }

            y_pos = equip_y - 30
            for slot, label in slot_names.items():
                if equip_x <= x <= equip_x + 250 and y_pos - 25 <= y <= y_pos:
                    item = self.player.equipment.get(slot)
                    if item:
                        # Déséquiper l'item
                        self.player.equipment[slot] = None
                        item.is_equipped = False
                        self.player.add_item_to_inventory(item)
                        print(f"Déséquipé: {item.name}")
                        return
                y_pos -= 25

            # Clic droit sur inventaire pour inspecter
            inv_x = 350
            inv_y = height - 50
            cols = 5
            item_size = 60
            spacing = 10

            for i, item in enumerate(self.player.inventory):
                row = i // cols
                col = i % cols
                ix = inv_x + col * (item_size + spacing)
                iy = inv_y - 40 - row * (item_size + spacing)

                if ix <= x <= ix + item_size and iy <= y <= iy + item_size:
                    # Afficher stats de l'item
                    print(f"\n=== {item.name} ===")
                    print(f"Tier: {item.tier} | Rareté: {item.rarity_id} | Qualité: {item.quality_id}")
                    stats = item.get_total_stats()
                    if stats.atk > 0: print(f"ATK: +{stats.atk}")
                    if stats.def_stat > 0: print(f"DEF: +{stats.def_stat}")
                    if stats.hp_max > 0: print(f"HP Max: +{stats.hp_max}")
                    if stats.crit_chance > 0: print(f"Crit: +{stats.crit_chance}%")
                    if stats.crit_dmg > 0: print(f"Crit Dmg: +{stats.crit_dmg}%")
                    if item.affixes:
                        print("Affixes:")
                        for affix in item.affixes:
                            affix_data = self.data.get_affix(affix["affix_id"])
                            print(f"  - {affix_data.get('name', 'Unknown')}: +{affix['rolled_value']}")
                    print(f"Valeur: {item.gold_value} or")
                    return

        # Clic gauche - potions et équiper items
        if button != arcade.MOUSE_BUTTON_LEFT:
            return

        # Vérifier clics sur les potions (gauche, sous équipement)
        # Calculer la position Y approximative des potions
        potion_start_y = height - 50 - (9 * 25) - 30 - 25  # équipement + marge + titre potions
        potion_height = 18

        potion_list = list(self.player.potions.items())[:5]
        for i, (potion_id, qty) in enumerate(potion_list):
            py = potion_start_y - i * potion_height
            if equip_x <= x <= equip_x + 250 and py - potion_height <= y <= py:
                # Utiliser la potion
                item_base = self.data.get_item_base(potion_id)
                if item_base and self.player.use_potion(potion_id, item_base):
                    print(f"Utilisé: {item_base.get('name', potion_id)}")
                return

        # Clics sur l'inventaire normal
        inv_x = 350
        inv_y = height - 50

        cols = 5
        item_size = 60
        spacing = 10

        for i, item in enumerate(self.player.inventory):
            row = i // cols
            col = i % cols

            ix = inv_x + col * (item_size + spacing)
            iy = inv_y - 40 - row * (item_size + spacing)

            if ix <= x <= ix + item_size and iy <= y <= iy + item_size:
                # Équiper l'item
                old_item = self.player.equip_item(item)
                self.player.inventory.remove(item)
                if old_item:
                    self.player.add_item_to_inventory(old_item)
                print(f"Équipé: {item.name}")
                break

    def on_key_press(self, symbol, modifiers):
        """Gère les touches du clavier"""
        # Sauvegarder avec S
        if symbol == arcade.key.S:
            self.save.save_game(self.player, self.skills, self.station_upgrades)
            print("Jeu sauvegardé manuellement")

        # Scroller les recettes avec UP/DOWN (si en mode crafting)
        if self.current_mode == "crafting":
            if symbol == arcade.key.UP:
                self.recipe_scroll_offset = max(0, self.recipe_scroll_offset - 1)
            elif symbol == arcade.key.DOWN:
                recipes = self.crafting.get_available_recipes(self.player)
                max_offset = max(0, len(recipes) - 8)
                self.recipe_scroll_offset = min(max_offset, self.recipe_scroll_offset + 1)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        """Gère le scroll de la molette de la souris"""
        # Scroll dans le craft
        if self.current_mode == "crafting":
            recipes = self.crafting.get_available_recipes(self.player)
            max_offset = max(0, len(recipes) - 8)

            # scroll_y > 0 = scroll up, scroll_y < 0 = scroll down
            self.recipe_scroll_offset -= int(scroll_y)
            self.recipe_scroll_offset = max(0, min(max_offset, self.recipe_scroll_offset))

    def _change_zone(self, direction: int):
        """Change de zone"""
        zones = self.data.zones
        current_index = next((i for i, z in enumerate(zones) if z["id"] == self.player.current_zone_id), 0)

        new_index = (current_index + direction) % len(zones)
        new_zone_id = zones[new_index]["id"]
        new_zone = zones[new_index]

        self.player.current_zone_id = new_zone_id

        # Respawn les nodes de la nouvelle zone
        self.gathering.spawn_nodes_for_zone(new_zone_id, 5)

        # Arrêter le combat actuel et en démarrer un nouveau avec les ennemis de la nouvelle zone
        if self.combat.combat_active:
            self.combat.combat_active = False
        self.combat.start_combat(new_zone_id, spawn_boss=False)

        print(f"Voyage vers: {new_zone['name']} (Tier {new_zone['tier']})")
        print(f"Ennemis: {', '.join(new_zone.get('enemies', []))}")

    def _draw_upgrades_view(self):
        """Vue des skills et upgrades de stations"""
        width = self.window.width
        height = self.window.height - 150

        # Titre
        arcade.draw_text("SKILLS & UPGRADES", width // 2, height - 20,
                        self.COLOR_HIGHLIGHT, 20, bold=True, anchor_x="center")

        # Colonne gauche: Skills
        skill_x = 50
        skill_y = height - 60

        arcade.draw_text("COMPETENCES", skill_x, skill_y, self.COLOR_HIGHLIGHT, 16, bold=True)
        skill_y -= 30

        # Skills deja debloques
        unlocked_skills = self.skills.get_unlocked_skills()
        if unlocked_skills:
            arcade.draw_text("Actives:", skill_x, skill_y, (100, 200, 100), 12, bold=True)
            skill_y -= 20
            for skill in unlocked_skills[:3]:
                arcade.draw_text(f"[OK] {skill['name']}", skill_x + 10, skill_y, (100, 200, 100), 10)
                skill_y -= 16
            skill_y -= 10

        # Skills disponibles
        available_skills = self.skills.get_available_skills(self.player)
        arcade.draw_text("Disponibles:", skill_x, skill_y, self.COLOR_TEXT, 12, bold=True)
        skill_y -= 25

        for i, skill_info in enumerate(available_skills[:5]):
            skill = skill_info["skill"]
            can_unlock = skill_info["can_unlock"]

            panel_width = 350
            panel_height = 80
            panel_y = skill_y - panel_height

            color = self.COLOR_PANEL_LIGHT if can_unlock else self.COLOR_PANEL
            arcade.draw_lrbt_rectangle_filled(skill_x, skill_x + panel_width,
                                             panel_y, skill_y, color)
            arcade.draw_lrbt_rectangle_outline(skill_x, skill_x + panel_width,
                                              panel_y, skill_y, self.COLOR_BORDER, 2)

            # Nom + type
            type_colors = {"combat": (255, 100, 100), "crafting": (100, 200, 255), 
                           "gathering": (100, 255, 100), "general": (255, 200, 100)}
            type_color = type_colors.get(skill.get("type"), self.COLOR_TEXT)

            arcade.draw_text(skill["name"], skill_x + 5, skill_y - 20, type_color, 12, bold=True)
            arcade.draw_text(f"[{skill['type']}]", skill_x + 5, skill_y - 35, type_color, 9)

            # Description
            arcade.draw_text(skill["desc"], skill_x + 5, skill_y - 52, self.COLOR_TEXT_DIM, 9)

            # Status
            if can_unlock:
                arcade.draw_text("[CLIQUER POUR DEBLOQUER]", skill_x + panel_width - 140,
                               skill_y - 70, self.COLOR_HIGHLIGHT, 9)
            else:
                arcade.draw_text(skill_info["reason"], skill_x + panel_width - 140,
                               skill_y - 70, self.COLOR_TEXT_DIM, 8)

            skill_y -= panel_height + 10

        # Colonne droite: Station Upgrades
        station_x = width - 550
        station_y = height - 60

        arcade.draw_text("AMELIORATIONS DE STATIONS", station_x, station_y,
                        self.COLOR_HIGHLIGHT, 16, bold=True)
        station_y -= 30

        available_upgrades = self.station_upgrades.get_available_upgrades(self.player)

        for i, upgrade_info in enumerate(available_upgrades[:6]):
            station_id = upgrade_info["station_id"]
            station_data = self.data.get_station(station_id)
            station_name = station_data.get("name", station_id) if station_data else station_id

            current_level = upgrade_info["current_level"]
            upgrade = upgrade_info["upgrade"]
            can_upgrade = upgrade_info["can_upgrade"]

            panel_width = 500
            panel_height = 90
            panel_y = station_y - panel_height

            color = self.COLOR_PANEL_LIGHT if can_upgrade else self.COLOR_PANEL
            arcade.draw_lrbt_rectangle_filled(station_x, station_x + panel_width,
                                             panel_y, station_y, color)
            arcade.draw_lrbt_rectangle_outline(station_x, station_x + panel_width,
                                              panel_y, station_y, self.COLOR_BORDER, 2)

            # Nom station + level
            arcade.draw_text(f"{station_name} LVL {current_level} -> {upgrade['level']}",
                           station_x + 5, station_y - 20, self.COLOR_HIGHLIGHT, 12, bold=True)

            # Nom upgrade
            arcade.draw_text(upgrade["name"], station_x + 5, station_y - 38,
                           self.COLOR_TEXT, 10)

            # Bonus
            bonus_text = "Bonus: " + ", ".join([f"+{v} {k}" for k, v in upgrade.get("bonus", {}).items()])
            arcade.draw_text(bonus_text, station_x + 5, station_y - 55,
                           (100, 200, 255), 9)

            # Status
            if can_upgrade:
                arcade.draw_text("[CLIQUER POUR AMELIORER]", station_x + panel_width - 160,
                               station_y - 75, self.COLOR_HIGHLIGHT, 9)
            else:
                arcade.draw_text(upgrade_info["reason"], station_x + panel_width - 160,
                               station_y - 75, self.COLOR_TEXT_DIM, 8)

            station_y -= panel_height + 10

    def _handle_upgrades_click(self, x, y, button):
        """Gère les clics en mode upgrades"""
        if button != arcade.MOUSE_BUTTON_LEFT:
            return
        width = self.window.width
        height = self.window.height - 150

        # Skills (gauche)
        skill_x = 50
        skill_y = height - 90
        unlocked_count = len(self.skills.get_unlocked_skills())
        if unlocked_count > 0:
            skill_y -= 20 + unlocked_count * 16 + 10
        skill_y -= 25

        available_skills = self.skills.get_available_skills(self.player)
        panel_width = 350
        panel_height = 80

        for i, skill_info in enumerate(available_skills[:5]):
            panel_y = skill_y - panel_height

            if (skill_x <= x <= skill_x + panel_width and
                panel_y <= y <= skill_y):
                if skill_info["can_unlock"]:
                    if self.skills.unlock_skill(skill_info["skill"]["id"], self.player):
                        print(f"Skill debloque: {skill_info['skill']['name']}")
                return

            skill_y -= panel_height + 10

        # Station Upgrades (droite)
        station_x = width - 550
        station_y = height - 90

        available_upgrades = self.station_upgrades.get_available_upgrades(self.player)
        panel_width = 500
        panel_height = 90

        for i, upgrade_info in enumerate(available_upgrades[:6]):
            panel_y = station_y - panel_height

            if (station_x <= x <= station_x + panel_width and
                panel_y <= y <= station_y):
                if upgrade_info["can_upgrade"]:
                    if self.station_upgrades.upgrade_station(upgrade_info["station_id"], self.player):
                        print(f"Station amelioree: {upgrade_info['station_id']} -> LVL {upgrade_info['current_level'] + 1}")
                return

            station_y -= panel_height + 10
