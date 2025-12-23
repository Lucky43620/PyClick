Idle RPG Clicker / Crafter – Asset Pack (starter ultra complet)
Date: 2025-12-23

Contenu:
- stats.json: définition des stats (combat + récolte + craft + procs)
- tiers.json: courbes de scaling (T1..T10)
- rarities.json / qualities.json: raretés et qualités
- resources.json: ressources (matières premières)
- nodes.json: noeuds cliquables (récolte) par zone
- items_base.json: bases d'items (slot + matériau + tier) avec stats de base
- affixes.json: pool d'affixes (offense/defense/utility/gather/craft/elemental/proc/legendary)
- sets.json: sets + bonus de pièces
- stations.json / recipes.json: crafting stations et recettes de base
- enemies.json: ennemis + bosses + tables de loot
- zones.json: progression de zones
- collectibles.json: pages de lore + reliques permanentes + familiers
- lore.json: prémisse + factions + hooks
- schemas.json: schémas des fichiers

Idée d'utilisation:
- Charge ces JSON au démarrage (data-driven).
- Pour générer un item final: item_base + rareté + qualité + N affixes (selon tags et tier).

Formules conseillées:
- power ≈ tier.base_power * quality.mult * rarity.mult
- base_stats_roll = roll(min,max) * quality.mult * rarity.mult
- affix_roll = roll(min,max) * (tier_num**0.35) * rarity.mult
