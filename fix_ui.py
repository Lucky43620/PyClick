"""
Fix UI coordinates - Arcade uses (left, right, bottom, top) format
"""

import re

# Lire le fichier
with open('src/ui/game_view.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remplacer les draw_lrbt_rectangle_filled avec les bons paramètres
# Pattern: arcade.draw_lrbt_rectangle_filled(x, x2, y2, y, ...)
# On veut: arcade.draw_lrbt_rectangle_filled(x, x2, y, y2, ...)

# Simple: remplacer tous les appels directs par nos helpers
replacements = [
    # Navigation buttons (inverser 0 et button_height)
    (r'arcade\.draw_lrbt_rectangle_filled\(x, x \+ button_width, button_height, 0,',
     'arcade.draw_lrbt_rectangle_filled(x, x + button_width, 0, button_height,'),
    (r'arcade\.draw_lrbt_rectangle_outline\(x, x \+ button_width, button_height, 0,',
     'arcade.draw_lrbt_rectangle_outline(x, x + button_width, 0, button_height,'),

    # Combat log (inverser log_y et log_y + 160)
    (r'arcade\.draw_lrbt_rectangle_filled\(log_x, log_x \+ 500, log_y \+ 160, log_y,',
     'arcade.draw_lrbt_rectangle_filled(log_x, log_x + 500, log_y, log_y + 160,'),
    (r'arcade\.draw_lrbt_rectangle_outline\(log_x, log_x \+ 500, log_y \+ 160, log_y,',
     'arcade.draw_lrbt_rectangle_outline(log_x, log_x + 500, log_y, log_y + 160,'),

    # Boss button (inverser boss_button_y et boss_button_y + 50)
    (r'arcade\.draw_lrbt_rectangle_filled\(boss_button_x, boss_button_x \+ 150, boss_button_y \+ 50, boss_button_y,',
     'arcade.draw_lrbt_rectangle_filled(boss_button_x, boss_button_x + 150, boss_button_y, boss_button_y + 50,'),
    (r'arcade\.draw_lrbt_rectangle_outline\(boss_button_x, boss_button_x \+ 150, boss_button_y \+ 50, boss_button_y,',
     'arcade.draw_lrbt_rectangle_outline(boss_button_x, boss_button_x + 150, boss_button_y, boss_button_y + 50,'),

    # Nodes (inverser y et y + node_height)
    (r'arcade\.draw_lrbt_rectangle_filled\(x, x \+ node_width, y \+ node_height, y,',
     'arcade.draw_lrbt_rectangle_filled(x, x + node_width, y, y + node_height,'),
    (r'arcade\.draw_lrbt_rectangle_outline\(x, x \+ node_width, y \+ node_height, y,',
     'arcade.draw_lrbt_rectangle_outline(x, x + node_width, y, y + node_height,'),

    # Recipes (inverser y et y + recipe_height)
    (r'arcade\.draw_lrbt_rectangle_filled\(recipe_x, recipe_x \+ recipe_width, y \+ recipe_height, y,',
     'arcade.draw_lrbt_rectangle_filled(recipe_x, recipe_x + recipe_width, y, y + recipe_height,'),
    (r'arcade\.draw_lrbt_rectangle_outline\(recipe_x, recipe_x \+ recipe_width, y \+ recipe_height, y,',
     'arcade.draw_lrbt_rectangle_outline(recipe_x, recipe_x + recipe_width, y, y + recipe_height,'),

    # Items (inverser y et y + item_size)
    (r'arcade\.draw_lrbt_rectangle_filled\(x, x \+ item_size, y \+ item_size, y,',
     'arcade.draw_lrbt_rectangle_filled(x, x + item_size, y, y + item_size,'),
    (r'arcade\.draw_lrbt_rectangle_outline\(x, x \+ item_size, y \+ item_size, y,',
     'arcade.draw_lrbt_rectangle_outline(x, x + item_size, y, y + item_size,'),
]

for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content)

# Écrire le fichier corrigé
with open('src/ui/game_view.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("UI fixée!")
