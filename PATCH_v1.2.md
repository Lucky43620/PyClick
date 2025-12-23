# Patch v1.2 - Améliorations majeures

## Changements à appliquer

### 1. Multiplier les coûts de craft par 5-10x
- Modifier toutes les recettes pour demander beaucoup plus de ressources
- Augmenter les coûts en or

### 2. Ajouter des délais de craft
- Chaque craft doit prendre du temps (time_sec dans les recettes)
- Barre de progression pendant le craft
- Impossible de crafter plusieurs items en même temps

### 3. Réduire MASSIVEMENT les stats des items craftés
- Les items de départ doivent être très faibles
- Progression plus lente

### 4. Système d'inspection d'items
- Hover sur un item = tooltip avec toutes les stats
- Clic droit pour inspecter en détail

### 5. Affichage correct de l'équipement
- Montrer toutes les stats de chaque pièce équipée
- Comparaison avant/après équipement

## Code à modifier

Trop de changements à faire manuellement. Je recommande:
1. Modifier directement les JSON pour augmenter les coûts
2. Réduire les multiplicateurs de stats dans le code
3. Implémenter le système de craft progressif
