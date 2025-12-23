# Guide de Démarrage Rapide - PyClick

## Lancer le jeu

```bash
# 1. Activer l'environnement virtuel
source venv/Scripts/activate  # Sur Windows (Git Bash)
# OU
venv\Scripts\activate  # Sur Windows (CMD)

# 2. Lancer le jeu
python main.py
```

## Premiers pas

### 1. Interface
Au lancement, tu verras 4 onglets en bas de l'écran:
- **COMBAT**: Le combat automatique contre les ennemis
- **RÉCOLTE**: Les nodes à cliquer pour récolter des ressources
- **CRAFT**: Les recettes pour crafter de nouveaux items
- **INVENTAIRE**: Ton équipement et tes items

### 2. Premier combat (T1 - Prairie des Jeunes Pousses)
- Le combat démarre automatiquement
- Tu attaques l'ennemi automatiquement
- Les dégâts et événements s'affichent dans le combat log
- Quand tu tues un ennemi, un nouveau spawn
- Clique sur **SPAWN BOSS** pour affronter le boss de la zone (difficile!)

### 3. Récolter des ressources
- Va dans l'onglet **RÉCOLTE**
- Tu verras 5 nodes (arbres, rochers, etc.)
- **Clique sur un node** pour le récolter
- Quand il est épuisé, il respawn après quelques secondes
- Les ressources récoltées apparaissent dans ton inventaire

### 4. Crafter
- Va dans l'onglet **CRAFT**
- Tu as débloqué le **Workbench** au départ
- Regarde les recettes disponibles
- **Clique sur une recette** si tu as les ressources nécessaires
- L'item crafté va dans ton inventaire

### 5. Gérer l'équipement
- Va dans l'onglet **INVENTAIRE**
- À gauche: ton équipement actuel
- Au centre: tes items dans le sac
- **Clique sur un item** du sac pour l'équiper
- Les stats changent immédiatement

## Raccourcis clavier

- **S**: Sauvegarder manuellement (auto-save toutes les 30s)
- **N**: Aller à la zone suivante
- **P**: Retour à la zone précédente

## Conseils de survie (mode Hardcore!)

### Combat
1. **Ne rush pas les zones!** Les ennemis sont très forts
2. **Améliore ton équipement** avant de changer de zone
3. **Regarde tes stats** en haut: ATK, DEF, HP
4. Si tu meurs: -10% d'or et respawn

### Récolte
1. **Farme les ressources** des zones faciles
2. Les bonus de récolte (gather_power) aident beaucoup
3. Change d'équipement selon ce que tu veux farmer

### Crafting
1. **Priorité**: Améliore ton arme en premier
2. Puis armure (chest, helmet)
3. Les items de meilleure **qualité** ont de meilleures stats
4. Les items **rares** ont plus d'affixes (bonus)

### Progression
1. **Tier 1-2**: Farme pour avoir de l'équipement decent
2. **Tier 3-4**: Débloque de nouvelles stations de craft
3. **Tier 5+**: Cherche des items Epic et Legendary
4. **Boss**: Donnent plus d'XP et de loot, mais sont 5x plus forts!

## Comprendre les stats

### Stats de combat importantes
- **ATK**: Dégâts infligés
- **DEF**: Réduit les dégâts reçus
- **Armure**: Réduit encore plus (focus physique)
- **Crit Chance**: Chance de critique (%)
- **Crit Dégâts**: Multiplicateur des critiques (base: 150%)
- **Esquive**: Chance d'éviter une attaque

### Stats de récolte
- **Gather Power (Wood/Ore/Herb)**: Récolte plus vite ce type
- **Ressources gagnées %**: Bonus sur toutes les ressources
- **Chance double drop**: Chance de doubler le loot

### Raretés (du moins au plus rare)
- **Common** (Gris) - 0 affixe
- **Uncommon** (Vert) - 1-2 affixes
- **Rare** (Bleu) - 2-3 affixes
- **Epic** (Violet) - 3-4 affixes
- **Legendary** (Orange) - 4+ affixes

### Qualités (impact sur les stats)
- **Poor**: 80% des stats
- **Normal**: 100% des stats
- **Superior**: 120% des stats
- **Masterwork**: 140% des stats
- **Perfect**: 160% des stats

## Build suggestions

### Build DPS (Dégâts)
- Focus: ATK, Crit Chance, Crit Dégâts
- Arme de qualité Masterwork ou Perfect
- Affixes: +ATK, +Crit, +Dégâts élémentaires

### Build Tank (Survie)
- Focus: HP Max, DEF, Armure, Blocage
- Armure lourde (chest, helmet, legs)
- Affixes: +HP, +DEF, +Armure, +Blocage

### Build Farmer (Récolte)
- Focus: Gather Power, Double Drop, Ressources gagnées
- Change d'équipement pour farmer
- Affixes: Gather stats, vitesse récolte

### Build Hybrid
- Équilibre ATK et DEF
- Vol de vie pour survivre
- Affixes variés

## Dépannage

### Le jeu ne se lance pas
```bash
# Réinstaller les dépendances
pip install --upgrade arcade pillow
```

### Problème de sauvegarde
```bash
# Supprimer la sauvegarde corrompue
rm saves/savegame.json
```

### FPS bas
- Ferme d'autres applications
- Le jeu utilise arcade.draw_text qui est lent (warning normal)

## Prochaines étapes

1. **Explore les 10 zones** (T1 → T10)
2. **Débloque toutes les stations** de crafting
3. **Collecte un set** d'armure complet
4. **Tue tous les boss** de chaque zone
5. **Atteins le niveau max** dans l'Abyssse Palimpseste

Bon jeu et bon courage! C'est hardcore!
