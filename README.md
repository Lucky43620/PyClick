# PyClick - Idle RPG Clicker/Crafter

**Un monde où la matière garde mémoire**

Un jeu de rôle idle/clicker/crafting hardcore avec génération procédurale d'items, système de combat automatique, récolte de ressources et crafting complexe.

## Caractéristiques

### Systèmes de jeu
- **Combat automatique** : Combattez des ennemis et des boss avec un système de combat profond (critiques, esquive, blocage, procs, dégâts élémentaires)
- **Récolte de ressources** : Cliquez sur des nodes pour récolter bois, minerais, plantes et autres ressources
- **Crafting complexe** : Craftez des items avec différentes stations, recettes, et améliorez votre équipement
- **Génération procédurale d'items** : Chaque item est unique avec qualité, rareté, stats de base et affixes aléatoires
- **10 zones progressives** : De la Prairie des Jeunes Pousses jusqu'à l'Abyssse Palimpseste (T1-T10)
- **Système de progression** : XP, levels, stats croissantes
- **Sauvegarde automatique** : Votre progression est sauvegardée automatiquement toutes les 30 secondes

### Difficulté Hardcore
- Ennemis puissants dès le début
- Ressources rares
- Drop rates très bas pour les items de qualité
- La mort fait perdre 10% de l'or
- Nécessite de bien gérer son équipement et ses ressources

### Interface
- Style fantasy sombre avec thème médiéval
- 4 vues principales : Combat, Récolte, Craft, Inventaire
- HUD complet avec barres de HP/XP, stats, log de combat
- Système de couleurs par rareté (Common → Legendary)

## Installation

1. Installez Python 3.8 ou supérieur

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

3. Lancez le jeu :
```bash
python main.py
```

## Commandes

### Navigation
- **Cliquez sur les boutons** en bas de l'écran pour changer de vue :
  - COMBAT : Vue de combat automatique
  - RÉCOLTE : Nodes de ressources à cliquer
  - CRAFT : Stations et recettes de crafting
  - INVENTAIRE : Équipement et sac

### Raccourcis clavier
- **S** : Sauvegarder manuellement
- **N** : Aller à la zone suivante (Next)
- **P** : Retourner à la zone précédente (Previous)

### Actions
- **Cliquez sur les nodes** en mode Récolte pour récolter
- **Cliquez sur les recettes** en mode Craft pour crafter
- **Cliquez sur les items** dans l'inventaire pour les équiper
- **Cliquez sur "SPAWN BOSS"** en mode Combat pour invoquer le boss de la zone

## Structure du projet

```
PyClick/
├── main.py                 # Point d'entrée
├── requirements.txt        # Dépendances
├── info/                   # Données JSON (stats, items, zones, etc.)
├── src/
│   ├── core/              # Coeur du jeu
│   │   ├── game.py        # Classe principale
│   │   └── data_manager.py # Chargement des JSON
│   ├── entities/          # Entités du jeu
│   │   └── player.py      # Joueur
│   ├── systems/           # Systèmes de jeu
│   │   ├── stats_system.py    # Calculs de stats et combat
│   │   ├── item_system.py     # Génération d'items
│   │   ├── combat_system.py   # Combat automatique
│   │   ├── gathering_system.py # Récolte
│   │   └── crafting_system.py  # Crafting
│   ├── ui/                # Interface utilisateur
│   │   └── game_view.py   # Vue principale avec UI
│   └── utils/             # Utilitaires
│       └── save_system.py # Sauvegarde/chargement
└── saves/                 # Fichiers de sauvegarde
```

## Progression suggérée

1. **Début (T1)** :
   - Combattez les premiers ennemis
   - Récoltez des ressources de base
   - Craftez de meilleurs équipements

2. **Milieu (T2-T5)** :
   - Explorez de nouvelles zones
   - Déverrouillez des stations de craft avancées
   - Cherchez des items de meilleure rareté

3. **Fin (T6-T10)** :
   - Affrontez des boss puissants
   - Optimisez votre build avec des affixes spécialisés
   - Maîtrisez l'Abyssse Palimpseste

## Systèmes avancés

### Génération d'items
Chaque item est généré avec :
- **Base** : Définit le slot et les stats de base
- **Tier** : T1 à T10, détermine la puissance
- **Qualité** : Poor → Normal → Superior → Masterwork → Perfect (multiplie les stats)
- **Rareté** : Common → Uncommon → Rare → Epic → Legendary (détermine le nombre d'affixes)
- **Affixes** : Bonus aléatoires basés sur les tags de l'item

### Formules de calcul
- **Power** = tier.base_power × quality.mult × rarity.mult
- **Dégâts** = ATK × crit_mult × réductions (DEF, armure, résistances)
- **Affixe** = roll(min,max) × (tier^0.35) × rarity.mult

### Crafting
- Nécessite une station débloquée
- Consomme des ressources et de l'or
- Peut générer des items de qualité variable
- Possibilité de reforger (reroll) les affixes

## Astuces

- Équilibrez vos stats : ATK pour tuer vite, DEF pour survivre
- Les critiques sont puissants : investissez dans crit_chance et crit_degats
- Farmez les ressources avant de changer de zone
- Les boss donnent plus de loot mais sont très dangereux
- Certains affixes sont spécialisés (gather, craft, combat) : adaptez votre équipement

## Développement futur

Le jeu est conçu pour être facilement extensible :
- Ajoutez des JSON dans `info/` pour new content
- Système de sets d'armure
- Familiers et collectibles
- Mode Ascension (prestige)
- Talents et arbres de compétences

## Crédits

Développé avec Python et Arcade
Design data-driven basé sur les JSON fournis
