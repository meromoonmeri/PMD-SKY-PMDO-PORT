# PMD Explorers of Sky Engine Analysis (NDS -> PMDO)

## Changement de Paradigme Technique (GBA vs NDS)

La décompilation de *Pokémon Mystery Dungeon: Explorers of Sky* (`pret/pmd-sky`) marque une rupture technologique majeure avec *Red Rescue Team*. Le Framework doit intégrer de nouveaux extracteurs adaptés à l'architecture Nintendo DS (ARM9).

### 1. Gestion des Scripts (SSB vs Station)
- **PMD Red (GBA)** : Les événements étaient codés en dur dans des tableaux C structurés (`ground_data_*_station.h`).
- **PMD Sky (NDS)** : Le jeu introduit un vrai langage de script sérialisé : le format **SSB** (Script Sequence Binary). Les scripts se trouvent dans `ROM/SCRIPT/` et définissent les cinématiques, les dialogues et le séquençage des donjons.
- **Stratégie Framework** : Créer un décompilateur SSB (ou s'interfacer avec `skytemple-files` / `explorerscript`) pour traduire le bytecode NDS en notre Cinematic Intermediate Format (CIF), puis en Lua RogueEssence.

### 2. Gestion des Cartes et des Décors (BGS / Sir0)
- **PMD Red (GBA)** : Les cartes utilisaient des BPL/BPC/BMA bruts.
- **PMD Sky (NDS)** : Les assets (Backgrounds, UI, etc.) sont encapsulés dans un conteneur propriétaire Chunsoft appelé **Sir0**. À l'intérieur du Sir0, la géométrie est souvent divisée en formats tels que `.bgs`, `.rlcn` (palettes), `.rlsn` et `.rlts`.
- **Stratégie Framework** : Utiliser un parseur Sir0 pour désencapsuler la géométrie. Le processus de *baking* restera identique (génération Pixel-Perfect vers PNG puis `.tile`).

### 3. Animations des Modèles (.WAN)
- La NDS utilise le format `.wan` (Wide Animation Network) pour les sprites de monstres et d'objets.
- Bien que PMDO possède déjà les monstres, les objets exclusifs au jeu (ex: Masques, items scénarisés) devront voir leurs `.wan` extraits et convertis en sprite-sheets PMDO.

## Philosophie du Framework (Inchangée)
Malgré le bond technologique, **la règle absolue reste la même** :
1. `PMDO` reste le moteur maître.
2. Aucun Pokémon natif, capacité ou météo n'est dupliqué.
3. Toutes les cinématiques sont converties dynamiquement en Lua (sans le texte narratif d'origine, en préparation pour New Era).
