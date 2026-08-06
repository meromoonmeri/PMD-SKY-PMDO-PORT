# Extraction d'Urgence — Décors PMD Sky (NDS) vers PMDO

**Dépôt** : `meromoonmeri/PMD-SKY-PMDO-PORT` (branche `master`)
**Date** : 2026-08-06
**Source** : `pret/pmd-sky` → `files/MAP_BG/` (fichiers NDS `.bpl`/`.bpc`/`.bma`),
décodés et rendus avec **skytemple-files** (`bma.to_pil` = rendu exact du jeu).

---

## 1. Ce qui a été extrait (VRAIE géométrie, pas des stubs)

| Source NDS | Type (index) | Asset | Dim. | Frames anim. | Tuiles planche | Collision libre |
|---|---|---|---|---|---|---|
| d00p01 | dungeon_entrance | `waterfall_cave_entrance` | 57×57 | 1 | 1 | 3249/3249 |
| d00p02 | cinematic_zone | `waterfall_cave_boss` | 57×57 | 1 | 33 | 873/3249 |
| d42p21a | dungeon_midpoint | `aegis_cave_entrance` | 57×57 | 1 | 33 | 873/3249 |
| d42p31a | boss_arena | `aegis_cave_boss` | 126×63 | **27** | 2736 | 7937/7938 |
| d42p41a | boss_arena | `aegis_cave_ice` | 63×63 | **27** | 2584 | 3962/3969 |
| d42p42a | cinematic_zone | `aegis_cave_rock` | 63×57 | **27** | 2672 | 3591/3591 |

- **Rendu pixel-perfect** : `bma.to_pil(bpc, bpl, bpas)` — l'image exacte affichée par le jeu, aucune transformation spatiale.
- **Animations environnementales** : les arènes Aegis ont **27 frames** (eau/lave animée) ; chaque cellule animée porte ses frames dans le `.rsground` (`FrameLength=10`), les cellules statiques 1 frame (`FrameLength=60`).
- **Collision** : couche BMA d'origine (`Tags` 1 = bloqué) ; dérivation « tuile noire » documentée pour `d00p01` (le `.bma` n'a pas de couche).
- **Markers** : `Main_Entrance_Marker` au centre de la zone marchable (les MAP_BG n'embarquent pas les entités des grounds `.sir0`, absents de pret/pmd-sky).
- **AssetName** = nom du fichier (règle New Era).

## 2. Point d'honnêteté méthodologique

- `pret/pmd-sky` (décompilation) **ne contient pas** les grounds fixes `.sir0`
  (villes, entrées cinématiques) — ils vivent dans la ROM non versionnée.
  Ce qu'il contient, ce sont les **décors de donjon** `files/MAP_BG/` : les
  layouts/tilesets réels utilisés par les étages d'Aegis Cave et Waterfall Cave.
- Les **mazes Ice/Rock/Steel d'Aegis Cave sont procéduraux** (générés à la
  volée) : il n'existe pas de layout fixe unique par maze. Les 4 layouts `d42`
  disponibles sont exportés ; le mapping `ice`/`rock` (et l'absence de
  `steel`) est **indicatif** — à confirmer en jeu par les couleurs.
- `d00p01` (entrée Waterfall) est un **motif de base uni** (1 tuile unique) :
  c'est le fond de sol du 1er étage, exporté tel quel, pas un stub.

## 3. Sauvegarde continue (appliquée)

Pour chaque décor : `git add -A` → `git commit "feat: Export carte NDS {id}"`
→ `git push origin master` → `os.remove()` local → `git update-index
--skip-worktree`. 6 commits poussés, working tree local propre.

## 4. Outils livrés

- `tools/convert_nds_map.py` — pipeline : décodage skytemple-files, rendu
  multi-frame, pack `.tile` (dédup par pixels), génération `.rsground`
  (frames animées, collision, marker).
- `tools/export_sky_maps.py` — manifeste des 6 cibles + sauvegarde continue.

## 5. Vérifications

- 6 `.rsground` + 6 `.tile` sur `origin/master` (7 grounds au total avec le
  stub préexistant `b01p01_beach`).
- Rendu reconstruit depuis `.tile`+`.rsground` : 0 tuile manquante (testé sur
  `aegis_cave_boss`).
- Les 105 tilesets `.tile` préexistants du dépôt restent intacts.
