# Spécifications Pixel Art - PyClick

## Taille recommandée: **32x32 pixels**

La taille 32x32 est optimale pour:
- Assez grande pour des détails visibles
- Assez petite pour charger rapidement
- Standard dans les jeux indie/rétro

## Types d'icônes nécessaires

### 1. Ressources (environ 30 icônes)
- Bois (3 types: tendre, chêne, spongieux)
- Pierre/Minerai (fer, cuivre, etc.)
- Fibres/Tissus
- Herbes médicinales
- Cristaux élémentaires (feu, glace, arcane) ⭐ **rare**
- Fragments (combat, artisan, collecte) ⭐ **rare**
- Essences (forge, alchimie) ⭐ **épique**
- Parchemins anciens ⭐ **légendaire**

### 2. Items craftés (environ 25 icônes)
- Planches, lingots, cuir traité

### 3. Équipement (environ 40 icônes)
- Armes: épées, haches, arcs
- Armures: casques, plastrons, jambières, bottes
- Accessoires: anneaux, amulettes
- Outils: pioches (T1-T5), haches (T1-T5), faucilles (T1-T5)

### 4. Consommables (environ 10 icônes)
- Potions de soin (petite, moyenne, grande)
- Potions de buff (force, défense, vitesse)

### 5. UI Elements (environ 15 icônes)
- Icône combat
- Icône récolte
- Icône craft
- Icône inventaire
- Icône skills/upgrades
- Bouton pause/reprendre
- Bouton fuir
- Stats (ATK, DEF, HP, etc.)

## Style recommandé

**Fantasy Dark** - Palette sombre avec accents lumineux:
- Fond transparent (PNG avec alpha channel)
- Contours noirs/gris foncé (1-2px)
- Couleurs légèrement désaturées
- Highlights pour les items rares

## Codes couleur par rareté

```
Commun:      #B4B4B4 (gris clair)
Peu commun:  #64C864 (vert)
Rare:        #6496FF (bleu)
Épique:      #C864FF (violet)
Légendaire:  #FFB432 (or)
```

## Organisation des fichiers

```
assets/
├── icons/
│   ├── resources/
│   │   ├── bois_tendre.png
│   │   ├── cristal_feu.png
│   │   └── ...
│   ├── items/
│   │   ├── tool_pioche_t1.png
│   │   ├── potion_soin_petite.png
│   │   └── ...
│   ├── equipment/
│   │   ├── weapon_sword_t1.png
│   │   ├── armor_helmet_t1.png
│   │   └── ...
│   └── ui/
│       ├── icon_combat.png
│       ├── icon_skills.png
│       └── ...
```

## Priorité de création

### Phase 1 - Urgent (30 icons)
1. Ressources de base (bois, pierre, fibres) - 10 icons
2. Ressources rares pour upgrades (cristaux, fragments) - 8 icons
3. Outils T1 (pioche, hache, faucille) - 3 icons
4. Potions de base - 3 icons
5. UI icons (5 onglets + combat) - 6 icons

### Phase 2 - Important (40 icons)
1. Équipement T1-T2 (armes, armures) - 20 icons
2. Outils T2-T5 - 12 icons
3. Matériaux craftés - 8 icons

### Phase 3 - Complet (40+ icons)
1. Équipement T3-T5 - 25 icons
2. Stats & effects icons - 15 icons

## Notes techniques

- Format: PNG avec transparence
- Pas d'anti-aliasing (pixel art pur)
- Export 2x pour HD (64x64) optionnel
- Nommer les fichiers selon les IDs du jeu

## Exemples de style

**Cristal de Feu** (cristal_feu.png):
- Base: rouge/orange (#FF4422)
- Lueur: jaune (#FFAA22)
- Contour: noir #000000
- Style: cristallin, facettes, brillance

**Pioche T1** (tool__pioche__t1):
- Manche: brun (#8B4513)
- Tête: gris pierre (#A0A0A0)
- Style: simple, rustique

**Fragment de Combat** (fragment_combat):
- Base: rouge sang (#CC0000)
- Éclats: nuance plus claire
- Effet: énergie/aura
- Rareté: bleu (#6496FF) pour bordure
