# PyClick - Idle RPG Clicker/Crafter

## 🎮 Description

Un jeu RPG idle/clicker hardcore avec crafting, combat automatique, récolte de ressources et système de progression profond. Développé en Python avec Arcade.

## 🚀 Fonctionnalités

### Combat Automatique
- Combats en temps réel contre des ennemis par zone (T1-T10)
- Boss avec drops améliorés
- Stats de combat détaillées en temps réel
- **Pause/Reprendre** le combat sans pénalité
- **Fuir** avec pénalité de 20% d'or
- Système de buffs temporaires

### Récolte de Ressources
- Nodes clickables avec respawn
- **Outils de récolte** améliorables (T1-T5)
- 3 types: Pioche (ore), Hache (wood), Faucille (herb)
- Ressources communes ET rares (cristaux, fragments, essences)

### Crafting Avancé
- **50+ recettes** disponibles
- Système de scroll pour voir toutes les recettes (UP/DOWN)
- Multiple stations: Atelier, Forge, Alchimie, Tannerie
- Items procéduraux avec affixes aléatoires
- **5 niveaux de rareté**: Commun, Peu commun, Rare, Épique, Légendaire
- **5 niveaux de qualité**: Pauvre, Normal, Supérieur, Chef-d'œuvre, Parfait

### Système de Potions
- Potions craftables: Soin (petite/moyenne), Force, Défense, Vitesse
- Inventaire de potions séparé
- Utilisation par clic
- Buffs temporaires visibles

### Skills Permanents (NOUVEAU!)
- **6 compétences** débloquables avec ressources rares:
  - **Berserk**: +15% ATK
  - **Forteresse**: +20% HP Max, +10 Armure
  - **Précision Mortelle**: +5% Crit Chance, +25% Crit Dégâts
  - **Artisan Expert**: -15% coûts de craft
  - **Collecteur Efficace**: x2 quantité récoltée
  - **Fortune**: +25% gain d'or
- Coût: Fragments + Cristaux + Or

### Améliorations de Stations (NOUVEAU!)
- Stations améliorables jusqu'à LVL 2-3
- Bonus permanents:
  - Atelier: +vitesse craft, +qualité
  - Forge: +vitesse craft, +stats items
  - Alchimie: +effet potions, +durée buffs
- Coût: Ressources rares (Essences, Cristaux arcanes)

### Progression
- Système d'XP avec courbe **TRÈS exponentielle** (hardcore)
- 10 tiers de zones avec ennemis progressifs
- Équipement dans 9 slots + 3 outils
- Système de sauvegarde automatique (30s)
- Navigation entre zones (N/P)

## 📦 Installation

```bash
# Installer les dépendances
pip install arcade

# Lancer le jeu
python main.py
```

## 🎯 Contrôles

### Souris
- Clic gauche: Interagir avec UI, nodes, boutons
- Zones cliquables: Tout en UI

### Clavier
- **S**: Sauvegarder manuellement
- **N**: Zone suivante
- **P**: Zone précédente
- **UP/DOWN**: Scroller les recettes (en mode Craft)

### Onglets
1. **COMBAT**: Combats automatiques + stats
2. **RÉCOLTE**: Cliquer les nodes pour farmer
3. **CRAFT**: 50+ recettes avec scroll
4. **INVENTAIRE**: Équipement + Potions utilisables
5. **UPGRADES**: Skills permanents + Amélioration de stations

## 🎨 Style Visuel

- **Thème**: Fantasy Dark
- **Palette**: Tons sombres avec accents dorés
- **UI**: Inspirée des RPG classiques
- **Icons**: Pixel art 32x32 (en cours - voir PIXEL_ART_SPECS.md)

## 📁 Structure du Projet

```
PyClick/
├── main.py                 # Point d'entrée
├── save.json               # Sauvegarde (auto-généré)
├── src/
│   ├── core/
│   │   ├── data_manager.py   # Charge les JSON
│   │   └── game.py            # Boucle principale
│   ├── entities/
│   │   └── player.py          # Joueur + inventaire
│   ├── systems/
│   │   ├── combat_system.py   # Combat auto
│   │   ├── crafting_system.py # Craft
│   │   ├── gathering_system.py# Récolte
│   │   ├── item_system.py     # Génération items
│   │   ├── skill_system.py    # Skills + Station upgrades
│   │   └── stats_system.py    # Stats & calculs
│   ├── ui/
│   │   ├── game_view.py       # Interface 5 onglets
│   │   └── tooltip.py         # Tooltips items
│   └── utils/
│       └── save_system.py     # Sauvegarde JSON
├── info/                   # Données du jeu (JSON)
│   ├── tiers.json
│   ├── zones.json
│   ├── enemies.json
│   ├── resources.json
│   ├── recipes.json
│   ├── items_base.json
│   ├── affixes.json
│   ├── skills.json         # Skills permanents
│   ├── station_upgrades.json
│   └── ... (16 fichiers)
└── assets/                 # Assets (pixel art)
    └── icons/
        ├── resources/
        ├── items/
        ├── equipment/
        └── ui/
```

## 🔥 Difficulté HARDCORE

Le jeu est volontairement **TRÈS difficile**:

- **Coûts de craft ×8-10**: Farming intensif nécessaire
- **Stats d'items -50%**: Progression lente
- **XP exponentielle**: Formule 150 × 1.35^level
- **Drops rares**: Boss = meilleur loot
- **Skills coûteux**: Ressources rares requises
- **Upgrades de stations**: Gros investissement

**C'est voulu!** Le jeu récompense l'optimisation et la patience.

## 🛠️ Technologies

- **Python 3.11+**
- **Arcade 3.3.3**: Moteur de jeu 2D
- **JSON**: Toutes les données du jeu
- **Architecture data-driven**: Facile à modder

## 📈 Roadmap

- [x] Combat automatique
- [x] Récolte clickable
- [x] Crafting avancé
- [x] Système de potions
- [x] Skills permanents
- [x] Upgrade de stations
- [x] 50+ recettes
- [ ] Pixel art 32x32 (Phase 1: 30 icons prioritaires)
- [ ] Sons & musique
- [ ] Plus de zones (T6-T10)
- [ ] Système de set d'équipement
- [ ] Achievements

## 📝 License

Projet perso - Libre d'utilisation pour apprentissage

## 🎨 Assets

Le jeu utilise actuellement des placeholders pour les graphismes. Pour créer les assets pixel art, voir [PIXEL_ART_SPECS.md](PIXEL_ART_SPECS.md).

**Priorité**: 30 icons 32x32 (ressources + UI)

---

**Bon farming!** 🔥
