# Changelog - PyClick

## Version 1.1 - Hardcore Balance (2025-12-23)

### Balancing HARDCORE
- **Stats de départ réduites de 40%**:
  - HP: 50 → 30
  - ATK: 5 → 3
  - DEF: 2 → 0
  - Vitesse attaque: 1.0 → 0.8
  - Crit chance: 5% → 2%

- **Progression ultra-lente**:
  - Stats par niveau divisées par 2
  - XP requise multipliée par 1.5x avec courbe plus agressive (1.35 au lieu de 1.15)
  - XP des ennemis réduite de 75%

- **Drop rates réduits**:
  - Common: 70% → 85%
  - Rare: 7% → 3%
  - Epic: 2.5% → 0.8%
  - Legendary: 0.5% → 0.2%

- **Qualité des items réduite**:
  - Poor: 50% → 60%
  - Perfect: 1% → 0.5%

- **Boss BEAUCOUP plus forts**:
  - HP multiplié par 8 (au lieu de 5)
  - ATK multiplié par 2 (au lieu de 1.5)
  - DEF multiplié par 3 (au lieu de 2)

- **Ressources de départ réduites**:
  - Or: 50 → 10
  - Bois/Pierre: 10 → 3
  - Fibres: 5 → 2

### Corrections de bugs
- Fix: Les clics sur les boutons de navigation fonctionnent maintenant correctement
- Fix: Conversion correcte des coordonnées float en int pour les index

## Version 1.0 - Release initiale (2025-12-23)

### Systèmes implémentés
- Combat automatique avec stats avancées
- Récolte de ressources cliquable
- Crafting avec stations et recettes
- Génération procédurale d'items
- 10 zones de T1 à T10
- Système de sauvegarde automatique
- Interface fantasy sombre complète

### Caractéristiques
- Data-driven (tout en JSON)
- Difficulté hardcore
- 4 vues: Combat, Récolte, Craft, Inventaire
- Progression XP et levels
- Raretés et qualités d'items
- Affixes procéduraux
