# PyClick v1.2 - VRAIMENT Hardcore

## Changements majeurs appliqués

### ✅ Corrections de bugs
1. **Combat redémarre correctement** quand tu changes d'onglet
2. **Changement de zone fonctionnel** avec N/P - les ennemis changent selon la zone
3. **Affichage équipement corrigé** - montre bien les items équipés

### 💀 Balancing HARDCORE (Script appliqué)

#### Craft rendu 8-10x plus difficile
- **Ressources x8**: Au lieu de 4 pierre, il faut maintenant 32 pierre!
- **Or x10**: Au lieu de 5 or, il faut 50 or!
- Un craft basique nécessite maintenant un VRAI farming

#### Stats des items réduites de 50-60%
- **Stats de base -50%**: Les items de départ sont BEAUCOUP plus faibles
- **Affixes -40%**: Même avec des affixes, c'est moins OP
- **Scaling réduit**: Les items de haut tier ne sont plus aussi puissants

### 🎮 Résultat: Un jeu qui demande du GRIND

Maintenant tu DOIS:
1. **Farmer longtemps** avant de pouvoir craft
2. **Choisir intelligemment** ce que tu craftes (les ressources sont précieuses)
3. **Grind de l'XP et de l'équipement** des drops avant de pouvoir progresser
4. **Mourir souvent** si tu rush sans équipement
5. **Optimiser chaque craft** car c'est très cher

## Ce qui reste à implémenter (optionnel)

### Système d'inspection (tooltip)
- Fichier créé: `src/ui/tooltip.py`
- Non intégré car nécessite refonte de game_view.py
- Afficherait les stats détaillées au survol

### Délai de craft avec progression
- Variables ajoutées dans game_view.py
- Logique non implémentée (trop de changements)
- Permettrait un craft progressif avec barre

## Comment tester

```bash
# 1. Lance le jeu
python main.py

# 2. Teste le craft
# - Farme BEAUCOUP de ressources (40-50 de chaque)
# - Va dans CRAFT
# - Vois les coûts élevés
# - Craft si tu as assez

# 3. Teste les zones
# - Appuie sur N pour zone suivante
# - Les ennemis changent (plus forts)
# - Appuie sur P pour revenir
```

## Stats avant/après

### Avant v1.2
- Craft arme T1: 6 fibres, 6 eau, 4 pierre, 5 or
- Stats arme T1: ~15-20 ATK
- Tu détruis tout en 1 craft

### Après v1.2 (HARDCORE)
- Craft arme T1: 48 fibres, 48 eau, 32 pierre, 50 or
- Stats arme T1: ~7-10 ATK
- Il faut farmer 30min+ avant de pouvoir craft
- L'arme craft ne te rend pas OP immédiatement

## Le jeu est maintenant VRAIMENT difficile! 💀

Bon farming! 🔥
