# Analyse du Format Ground (NDS -> PMDO)

## Changement de paradigme (GBA vs NDS)
Contrairement à *Red Rescue Team* (GBA) où les données étaient brutes (`BPL`, `BPC`, `BMA`), *Explorers of Sky* (NDS) utilise un conteneur propriétaire : le **Sir0**.

Le format Sir0 est une archive structurée contenant des données hiérarchiques. 
Dans les dossiers `ROM/GROUND/` ou `ROM/MAP_BG/`, les fichiers sont souvent sous les extensions `.bgs`, `.bma`, `.bpc`, mais encapsulés dans un Sir0.

### 1. Structure du Conteneur Sir0
- **Header** : 16 octets. Commence par la signature magique `SIR0` (0x53 0x49 0x52 0x30).
- **Pointeur principal** : Pointe vers le début des blocs de données (Data offset).
- **Pointeur d'offsets (Pointer offset)** : Pointe vers la section contenant une liste d'entiers compressés. Ces entiers indiquent où se trouvent les sous-pointeurs dans la mémoire pour que le jeu puisse les reloger dynamiquement (Relocation Table).
- **Data** : Les données réelles (Palettes, Tuiles, Collisions).

### 2. Contenu d'une Carte (Ground) NDS
- **`.rlcn` (Palettes)** : Remplace le `.bpl`. Ce sont des palettes compressées ou non, 15-bits BGR.
- **`.rlts` (Tuiles / Tilesets)** : Remplace le `.bpc`. Ce sont les graphismes (pixels).
- **`.rlsn` (Tilemap / Chunks)** : Remplace le `.bma`. Détermine l'agencement des tuiles, l'ordre des couches (Z-index), et inclut les **flags de collision**.

### 3. Mapping NDS -> PMDO (RogueEssence)
La philosophie stricte "PMDO reste maître" s'applique à la géométrie :
| Donnée NDS (Sir0) | Format Intermédiaire (JSON) | Sortie Native PMDO (RogueEssence) |
| :--- | :--- | :--- |
| `.rlts` / `.rlcn` | `tiles`, `palettes` brutes | Fichier `Data/Tile/*.tile` (Tuiles PNG concaténées, identité visuelle parfaite). |
| `.rlsn` (Agencement) | `layers`, `grid_size` | Balise `Layers` dans le `.rsground` (RogueEssence.Ground.GroundMap). |
| `.rlsn` (Collision) | `collision_matrix` (Tags 0/1) | Balise `obstacles` dans le `.rsground`. 0=Libre, 1=Bloquant. |
| Scripts Station / SSB | `entities`, `markers` | Balise `Spawners` (GroundSpawner) et `Markers` du `.rsground`. |

## Processus du Pipeline de Conversion
1. **Extraction** : Le parseur `sir0_parser.py` ouvre l'archive, lit la table de relocation, et extrait la donnée brute en mémoire.
2. **Désassemblage** : Le script `ground_disassembler.py` décode le binaire NDS extrait en JSON (dimensions, collisions, layers, entités).
3. **Conversion** : Le générateur `ground_pmdo_generator.py` prend ce JSON et écrit un `.rsground` strict, vérifiable et utilisable par l'éditeur PMDO natif.
