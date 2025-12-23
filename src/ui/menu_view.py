"""
Menu principal : Continuer, Nouvelle partie, Importer.
"""

import arcade
import arcade.gui
from pathlib import Path


class MenuView(arcade.View):
    """Vue de menu principal simple."""

    def __init__(self, game_window, save_system, message: str = ""):
        super().__init__()
        self.game_window = game_window
        self.save_system = save_system
        self.message = message

        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()

        self.import_input = arcade.gui.UIInputText(text="", width=320)

        self._build_layout()

    def _build_layout(self):
        """Construit les widgets du menu."""
        v_box = arcade.gui.UIBoxLayout(space_between=12)

        title = arcade.gui.UILabel(
            text="PyClick",
            font_size=32,
            text_color=(230, 200, 170),
            bold=True
        )
        subtitle = arcade.gui.UILabel(
            text="Idle RPG - Mode hardcore",
            font_size=16,
            text_color=(180, 160, 140)
        )
        v_box.add(title)
        v_box.add(subtitle)
        v_box.add(arcade.gui.UILabel(text=""))

        # Boutons principaux
        continue_button = arcade.gui.UIFlatButton(text="Continuer", width=280)
        new_button = arcade.gui.UIFlatButton(text="Nouvelle partie", width=280)
        import_button = arcade.gui.UIFlatButton(text="Importer et jouer", width=280)

        continue_button.on_click = lambda _: self._on_continue()
        new_button.on_click = lambda _: self._on_new_game()
        import_button.on_click = lambda _: self._on_import()

        v_box.add(continue_button)
        v_box.add(new_button)

        # Bloc import
        import_box = arcade.gui.UIBoxLayout(space_between=6)
        import_box.add(self.import_input)
        import_box.add(import_button)
        v_box.add(import_box)

        # Message de status
        self.message_label = arcade.gui.UILabel(
            text=self.message,
            font_size=12,
            text_color=(220, 120, 100)
        )
        v_box.add(self.message_label)

        # arcade 2.6+: UIAnchorLayout remplace UIAnchorWidget
        anchor_layout = arcade.gui.UIAnchorLayout()
        anchor_layout.add(child=v_box, anchor_x="center", anchor_y="center")
        self.ui_manager.add(anchor_layout)

    def set_message(self, message: str):
        """Met à jour le message d'état du menu."""
        self.message = message
        if self.message_label:
            self.message_label.text = message

    def _on_continue(self):
        if not self.save_system.has_save():
            self.set_message("Aucune sauvegarde détectée.")
            return
        self.game_window.continue_game()

    def _on_new_game(self):
        self.set_message("Nouvelle partie en cours...")
        self.game_window.start_new_game()

    def _on_import(self):
        path = self.import_input.text.strip()
        if not path:
            self.set_message("Entrez un chemin de fichier pour importer.")
            return
        self.set_message(f"Import depuis {Path(path).expanduser()}...")
        self.game_window.import_and_start(path)

    def on_show_view(self):
        arcade.set_background_color((15, 10, 15))
        self.ui_manager.enable()

    def on_hide_view(self):
        self.ui_manager.disable()

    def on_draw(self):
        self.clear()
        width, height = self.window.width, self.window.height

        # Fond
        arcade.draw_lrbt_rectangle_filled(0, width, 0, height, (12, 8, 12))
        arcade.draw_lrbt_rectangle_outline(60, width - 60, 40, height - 40, (90, 70, 60), 3)

        self.ui_manager.draw()

        # Tips
        arcade.draw_text(
            "Conseil: les modes hardcore récompensent la patience. Préparez vos crafts avant d'affronter les boss!",
            width // 2, 80, (180, 150, 120), 12, anchor_x="center", width=width - 160, align="center"
        )
