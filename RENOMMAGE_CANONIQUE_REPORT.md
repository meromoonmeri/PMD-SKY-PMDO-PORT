# Rapport de Renommage Canonique — MAP_BG PMD Sky (NDS) → PMDO

**Dépôt** : `meromoonmeri/PMD-SKY-PMDO-PORT` (branche `master`, commit `3c2d077`)
**Date** : 2026-08-06
**Portée** : identité des cartes UNIQUEMENT (noms de fichiers + `AssetName` +
`Name`). **Aucune modification** des `.tile`, frames d'animation, collisions,
layers ou dimensions.

---

## 1. Le problème identifié

Le pipeline MAP_BG → PMDO avait correctement exporté les assets, mais **deux
attributions de noms étaient fausses** :

| Ancien nom (faux) | Source réelle | Problème constaté |
|---|---|---|
| `waterfall_cave_entrance` | `d00p01` | ❌ `d00` = **TEST DUNGEON** (ID 0) — pas Waterfall Cave |
| `waterfall_cave_boss` | `d00p02` | ❌ idem — d'où les tuiles noires / carte "vide" |
| `aegis_cave_entrance/boss/ice/rock` | `d42p21a/31a/41a/42a` | ❌ `d42` = **TEMPORAL SPIRE** (ID 42) — pas Aegis Cave |

Le VRAI **Waterfall Cave = `d06`** (ID 6) et la vraie **Aegis Cave = `d54`–`d61`**
(ID 54-61).

## 2. Source de validation (autoritative)

- **`pret/pmd-sky/include/enums.h`** — table officielle `DUNGEON_* = ID` :
  `DUNGEON_TEST_DUNGEON = 0`, `DUNGEON_WATERFALL_CAVE = 6`,
  `DUNGEON_TEMPORAL_SPIRE = 42`, `DUNGEON_ICE_AEGIS_CAVE = 54`,
  `DUNGEON_REGICE_CHAMBER = 55`, `DUNGEON_ROCK_AEGIS_CAVE = 56`,
  `DUNGEON_REGIROCK_CHAMBER = 57`, `DUNGEON_STEEL_AEGIS_CAVE = 58`,
  `DUNGEON_REGISTEEL_CHAMBER = 59`, `DUNGEON_AEGIS_CAVE_PIT = 60`,
  `DUNGEON_REGIGIGAS_CHAMBER = 61`.
- **Correspondance 1:1 vérifiée** : le préfixe `d##` de chaque fichier `MAP_BG`
  (`.bma/.bpc/.bpl/.bpa`) == l'ID du donjon dans l'enum, pour les 95 groupes
  (d00 → d95). Aucune exception.
- **Confirmation Bulbapedia** : structure canonique d'Aegis Cave (EoS) =
  Labyrinthe de Glace → Chambre de Regice → Labyrinthe de Roche → Chambre de
  Regirock → Labyrinthe d'Acier → Chambre de Registeel → Fosse d'Aegis →
  Chambre de Regigigas.

## 3. ANCIEN NOM → NOUVEAU NOM → SOURCE DE VALIDATION

### 3.1 Corrections d'identité (mauvais noms précédents)

| Ancien nom | Nouveau nom | Source |
|---|---|---|
| `waterfall_cave_entrance` | `test_dungeon_1` | `DUNGEON_TEST_DUNGEON = 0` (d00p01) |
| `waterfall_cave_boss` | `test_dungeon_2` | `DUNGEON_TEST_DUNGEON = 0` (d00p02) |
| `aegis_cave_entrance` | `temporal_spire_1` | `DUNGEON_TEMPORAL_SPIRE = 42` (d42p21a) |
| `aegis_cave_boss` | `temporal_spire_2` | `DUNGEON_TEMPORAL_SPIRE = 42` (d42p31a) |
| `aegis_cave_ice` | `temporal_spire_3` | `DUNGEON_TEMPORAL_SPIRE = 42` (d42p41a) |
| `aegis_cave_rock` | `temporal_spire_4` | `DUNGEON_TEMPORAL_SPIRE = 42` (d42p42a) |

### 3.2 Le VRAI Waterfall Cave

| Ancien nom | Nouveau nom | Source |
|---|---|---|
| `d06p11a` | `waterfall_cave_1` | `DUNGEON_WATERFALL_CAVE = 6` (avec BPA `d06p11a5`, 7 frames) |

### 3.3 Famille Aegis Cave (renommage canonique)

| Ancien nom | Nouveau nom | Source |
|---|---|---|
| `d54p11a` | `aegis_cave_ice_1` | `DUNGEON_ICE_AEGIS_CAVE = 54` |
| `d54p31a` | `aegis_cave_ice_2` | idem |
| `d54p32a` | `aegis_cave_ice_3` | idem |
| `d55p11a` | `aegis_cave_regice_1` | `DUNGEON_REGICE_CHAMBER = 55` |
| `d55p21a` | `aegis_cave_regice_2` | idem |
| `d55p41a` | `aegis_cave_regice_3` | idem |
| `d56p11a` | `aegis_cave_rock_1` | `DUNGEON_ROCK_AEGIS_CAVE = 56` |
| `d56p12a` | `aegis_cave_rock_2` | idem |
| `d56p21a` | `aegis_cave_rock_3` | idem |
| `d56p41a` | `aegis_cave_rock_4` | idem |
| `d57p21a` | `aegis_cave_regirock_1` | `DUNGEON_REGIROCK_CHAMBER = 57` |
| `d57p41a` | `aegis_cave_regirock_2` | idem |
| `d57p42a` | `aegis_cave_regirock_3` | idem |
| `d57p43a` | `aegis_cave_regirock_4` | idem |
| `d57p44a` | `aegis_cave_regirock_5` | idem |
| `d58p41a` | `aegis_cave_steel_1` | `DUNGEON_STEEL_AEGIS_CAVE = 58` |
| `d59p41a` | `aegis_cave_registeel_1` | `DUNGEON_REGISTEEL_CHAMBER = 59` |
| `d60p41a` | `aegis_cave_pit_1` | `DUNGEON_AEGIS_CAVE_PIT = 60` |
| `d61p41a` | `aegis_cave_regigigas_1` | `DUNGEON_REGIGIGAS_CHAMBER = 61` |

**26 fichiers renommés.** Vérifié sur `origin/master` : 465 grounds préservés,
anciens noms absents, tous les `AssetName` == nom de fichier.

## 4. Manifest complet Source MAP_BG → Nom canonique

(Extrait des groupes clés ; la table complète couvre d00 → d95 = 90 groupes.)

| Groupe MAP_BG | Donjon (enum) | Nom canonique | Fichiers |
|---|---|---|---|
| d00 | TEST_DUNGEON | `test_dungeon` | d00p01, d00p02 |
| d01 | BEACH_CAVE | `beach_cave` | d01p11a, d01p11b, d01p41a |
| d02 | BEACH_CAVE_PIT | `beach_cave_pit` | d02p11a, d02p31a |
| d03 | DRENCHED_BLUFF | `drenched_bluff` | d03p11a, d03p41a |
| d04 | MT_BRISTLE | `mt_bristle` | d04p11a, d04p12a, d04p31a |
| d05 | MT_BRISTLE_PEAK | `mt_bristle_peak` | d05p11a, d05p31a |
| **d06** | **WATERFALL_CAVE** | **`waterfall_cave`** | **d06p11a** |
| d07 | APPLE_WOODS | `apple_woods` | d07p11a |
| d08 | CRAGGY_COAST | `craggy_coast` | d08p11a |
| d09 | SIDE_PATH | `side_path` | d09p11a |
| d10 | MT_HORN | `mt_horn` | d10p21a, d10p41a |
| d11 | ROCK_PATH | `rock_path` | d11p11a |
| d12 | FOGGY_FOREST | `foggy_forest` | d12p21a, d12p41a |
| d13 | FOREST_PATH | `forest_path` | d13p11a |
| d14 | STEAM_CAVE | `steam_cave` | d14p11a, d14p12a |
| d15 | UPPER_STEAM_CAVE | `upper_steam_cave` | d15p21a, d15p41a |
| d16 | STEAM_CAVE_PEAK | `steam_cave_peak` | d16p11a, d16p31a |
| d17 | AMP_PLAINS | `amp_plains` | d17p11a, d17p31a-d34a, d17p45a |
| d18 | FAR_AMP_PLAINS | `far_amp_plains` | d18p11a |
| d19 | AMP_CLEARING | `amp_clearing` | d19p11a |
| d20 | NORTHERN_DESERT | `northern_desert` | d20p11a |
| d21 | QUICKSAND_CAVE | `quicksand_cave` | d21p21a, d21p41a |
| d22 | QUICKSAND_PIT | `quicksand_pit` | d22p11a |
| d23 | UNDERGROUND_LAKE | `underground_lake` | d23p11a |
| d24 | CRYSTAL_CAVE | `crystal_cave` | d24p11a, d24p31a, d24p31b |
| d25 | CRYSTAL_CROSSING | `crystal_crossing` | d25p11a |
| d26 | CRYSTAL_LAKE | `crystal_lake` | d26p21a, d26p31a, d26p43a |
| d27 | CHASM_CAVE | `chasm_cave` | d27p11a |
| d28 | DARK_HILL | `dark_hill` | d28p21a, d28p31a-d34a, d28p44a |
| d29 | SEALED_RUIN | `sealed_ruin` | d29p11a |
| d30 | DEEP_SEALED_RUIN | `deep_sealed_ruin` | d30p21a, d30p32a-d34a, d30p41a, d30p42a |
| d31 | SEALED_RUIN_PIT | `sealed_ruin_pit` | d31p11a, d31p31a, d31p41a |
| d32 | DUSK_FOREST | `dusk_forest` | d32p11a-d14a, d32p31a-d33a, d32p41a-d44a |
| d33 | DEEP_DUSK_FOREST | `deep_dusk_forest` | d33p41a |
| d34 | TREESHROUD_FOREST | `treeshroud_forest` | d34p41a |
| d35 | BRINE_CAVE | `brine_cave` | d35p21a, d35p41a |
| d36 | LOWER_BRINE_CAVE | `lower_brine_cave` | d36p11a, d36p41a |
| d37 | BRINE_CAVE_PIT | `brine_cave_pit` | d37p11a, d37p41a |
| d38 | HIDDEN_LAND | `hidden_land` | d38p11a, d38p12a |
| d39 | HIDDEN_HIGHLAND | `hidden_highland` | d39p21a, d39p32a, d39p41a |
| d40 | OLD_RUINS | `old_ruins` | d40p11a |
| d41 | TEMPORAL_TOWER | `temporal_tower` | d41p21a, d41p41a |
| **d42** | **TEMPORAL_SPIRE** | **`temporal_spire`** | **d42p21a, d42p31a, d42p41a, d42p42a** |
| d43 | TEMPORAL_PINNACLE | `temporal_pinnacle` | d43p31a |
| d44 | MYSTIFYING_FOREST | `mystifying_forest` | d44p31a |
| d45 | MYSTIFYING_FOREST_CLEARING | `mystifying_forest_clearing` | d45p21a, d45p31a, d45p42a |
| d46 | BLIZZARD_ISLAND | `blizzard_island` | d46p11a, d46p21a, d46p31a, d46p41a |
| d47 | CREVICE_CAVE | `crevice_cave` | d47p11a |
| d48 | LOWER_CREVICE_CAVE | `lower_crevice_cave` | d48p11a, d48p21a |
| d49 | CREVICE_CAVE_PIT | `crevice_cave_pit` | d49p41a |
| d50 | SURROUNDED_SEA | `surrounded_sea` | d50p11a |
| d51 | MIRACLE_SEA | `miracle_sea` | d51p11a, d51p21a, d51p41a |
| d52 | DEEP_MIRACLE_SEA | `deep_miracle_sea` | d52p11a, d52p11c, d52p31a, d52p32a |
| d53 | MIRACLE_SEABED | `miracle_seabed` | d53p11a, d53p11b, d53p21a, d53p41a-c |
| **d54** | **ICE_AEGIS_CAVE** | **`aegis_cave_ice`** | **d54p11a, d54p31a, d54p32a** |
| **d55** | **REGICE_CHAMBER** | **`aegis_cave_regice`** | **d55p11a, d55p21a, d55p41a** |
| **d56** | **ROCK_AEGIS_CAVE** | **`aegis_cave_rock`** | **d56p11a, d56p12a, d56p21a, d56p41a** |
| **d57** | **REGIROCK_CHAMBER** | **`aegis_cave_regirock`** | **d57p21a, d57p41a-d44a** |
| **d58** | **STEEL_AEGIS_CAVE** | **`aegis_cave_steel`** | **d58p41a** |
| **d59** | **REGISTEEL_CHAMBER** | **`aegis_cave_registeel`** | **d59p41a** |
| **d60** | **AEGIS_CAVE_PIT** | **`aegis_cave_pit`** | **d60p41a** |
| **d61** | **REGIGIGAS_CHAMBER** | **`aegis_cave_regigigas`** | **d61p41a** |
| d62 | MT_TRAVAIL | `mt_travail` | d62p41a |
| d63 | THE_NIGHTMARE | `the_nightmare` | d63p41a |
| d64 | SPACIAL_RIFT | `spacial_rift` | (d64 absent — pas de MAP_BG) |
| d65 | DEEP_SPACIAL_RIFT | `deep_spacial_rift` | d65p41a |
| d66 | SPACIAL_RIFT_BOTTOM | `spacial_rift_bottom` | d66p41a |
| d67 | DARK_CRATER | `dark_crater` | d67p41a |
| d68 | DEEP_DARK_CRATER | `deep_dark_crater` | d68p41a |
| d69 | DARK_CRATER_PIT | `dark_crater_pit` | d69p41a |
| d70 | CONCEALED_RUINS | `concealed_ruins` | d70p41a |
| d71 | DEEP_CONCEALED_RUINS | `deep_concealed_ruins` | d71p41a |
| d72 | MARINE_RESORT | `marine_resort` | d72p41a |
| d73 | BOTTOMLESS_SEA | `bottomless_sea` | d73p11a, d73p21a-d29a, d73p31a, d73p41a |
| d74 | BOTTOMLESS_SEA_DEPTHS | `bottomless_sea_depths` | (d74 absent) |
| d75 | SHIMMER_DESERT | `shimmer_desert` | (d75 absent) |
| d76 | SHIMMER_DESERT_PIT | `shimmer_desert_pit` | (d76 absent) |
| d77 | MT_AVALANCHE | `mt_avalanche` | (d77 absent) |
| d78 | MT_AVALANCHE_PEAK | `mt_avalanche_peak` | (d78 absent) |
| d79 | GIANT_VOLCANO | `giant_volcano` | d79p11a, d79p21a, d79p41a |
| d80 | GIANT_VOLCANO_PEAK | `giant_volcano_peak` | d80p41a |
| d81 | WORLD_ABYSS | `world_abyss` | d81p41a |
| d82 | WORLD_ABYSS_PIT | `world_abyss_pit` | d82p41a |
| d83 | SKY_STAIRWAY | `sky_stairway` | d83p41a |
| d84 | SKY_STAIRWAY_APEX | `sky_stairway_apex` | d84p41a |
| d85 | MYSTERY_JUNGLE | `mystery_jungle` | d85p41a |
| d86 | DEEP_MYSTERY_JUNGLE | `deep_mystery_jungle` | d86p41a |
| d87 | SERENITY_RIVER | `serenity_river` | d87p41a |
| d88 | LANDSLIDE_CAVE | `landslide_cave` | d88p41a |
| d89 | LUSH_PRAIRIE | `lush_prairie` | d89p41a |
| d90 | TINY_MEADOW | `tiny_meadow` | d90p41a |
| d91 | LABYRINTH_CAVE | `labyrinth_cave` | d91p41a |
| d92 | ORAN_FOREST | `oran_forest` | d92p41a |
| d93 | LAKE_AFAR | `lake_afar` | d93p41a |
| d94 | HAPPY_OUTLOOK | `happy_outlook` | d94p41a |
| d95 | MY_MISTRAL | `my_mistral` | d95p41a |

## 5. Notes importantes

- **Tiles intactes** : les planches `.tile` et les `Sheet` référencés n'ont pas
  été modifiés. Les sheets gardent le nom source (`D54p11a_Base`, etc.) — c'est
  volontaire (règle « ne pas modifier les tiles »). Les fichiers
  `AegisCaveEntrance_Base.tile`/`AegisCaveBoss_Base.tile`/etc. (anciens noms,
  = tiles de d42) restent sur le dépôt : ce sont les tiles de **Temporal Spire**,
  à renommer en `TemporalSpire*_Base.tile` si vous le souhaitez (sans toucher
  au contenu).
- **Fonds noirs** : un MAP_BG sombre (d58-d61, d00) est normal — c'est le
  décor d'arrière-plan ; le générateur d'étage dessine les tuiles jouables
  par-dessus. 0 référence de tuile invalide sur toutes ces cartes (le bug des
  tuiles noires = index > tiles après BPA, absent ici).
- **Reste à renommer** : les autres grounds (d01p11a, d03p41a, etc.) portent
  encore leur identifiant source ; ils peuvent être canonisés à l'identique
  (table §4) sur demande.

## 6. Preuves visuelles

`/home/user/preuves_sky/` :
- `waterfall_cave_1.png` — le VRAI Waterfall Cave (d06p11a), 7 frames
- `aegis_cave_ice_1.png`, `aegis_cave_regice_1.png`, `aegis_cave_rock_1.png`,
  `aegis_cave_regirock_2.png`, `aegis_cave_steel_1.png`,
  `aegis_cave_registeel_1.png`, `aegis_cave_pit_1.png`,
  `aegis_cave_regigigas_1.png`
- Tous : 0 tuile manquante, rendu depuis les fichiers finaux d'origine/master.
