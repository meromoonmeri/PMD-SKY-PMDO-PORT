# SSB Format Analysis (PMD Sky -> PMDO)

## Présentation du Format SSB (Script Sequence Binary)
Contrairement à PMD Red (macros C), PMD Explorers of Sky compile ses événements narratifs et techniques dans des fichiers binaires `.ssb`. La décompilation du jeu fournit également des sources `.ssa` (Script Sequence Assembly) parfois réversibles, mais les véritables commandes de jeu sont dans les `.ssb`.

Outils de manipulation existants (incorporés dans le pipeline) :
- **skytemple-files / explorerscript** : librairies Python permettant de lire et d'écrire le bytecode `.ssb` de Chunsoft.

## Architecture d'un Script Sky
Chaque script est associé à un fichier de niveau (`.lsd`) et à une table de textes.
Les cinématiques sont déclenchées dans des scripts comme `enter00.ssb`, `m01a0103.ssb` (m01 = Mission 01).

## Mapping des Opcodes NDS -> Lua PMDO

### 1. Caméra (Coroutines)
- `CameraMove(x, y, speed)` -> `GAME:MoveCamera(x, y, speed, true)`
- `CameraMoveToEntity(entity, speed)` -> `GAME:MoveCamera(entity.MapLoc.X, entity.MapLoc.Y, speed, true)`
- `ScreenShake(intensity, frames)` -> `SOUND:PlayBattleSE('EVT_Roar'); GAME:WaitFrames(frames)`

### 2. Audio
- `BGMPlay(track_id)` -> `GAME:PlayBGM('Track Name', true)`
- `BGMFadeOut(frames)` -> `GAME:FadeOutBGM(frames)`
- `SEPlay(sfx_id)` -> `SOUND:PlayBattleSE('SFX_Name')`

### 3. Effets Visuels (Screen FX)
- `ScreenWhiteOut(frames)` -> `GAME:FadeOut(true, frames)`
- `ScreenWhiteIn(frames)` -> `GAME:FadeIn(frames)`
- `ScreenBlackOut(frames)` -> `GAME:FadeOut(false, frames)`
- `ScreenBlackIn(frames)` -> `GAME:FadeIn(frames)`

### 4. Mouvements et Animations des Acteurs
- `EntityMovePosition(entity, x, y, speed)` -> `GROUND:MoveToPosition(entity, x, y, false, speed)`
- `EntityTurn(entity, direction)` -> `GROUND:EntTurn(entity, direction)`
- `EntitySetAnimation(entity, anim_id)` -> `GROUND:CharSetAction(entity, anim)`

## Philosophie de la Conversion
1. Le désassembleur lit le binaire `.ssb` et produit un **JSON d'Abstract Syntax Tree (AST)** ou CIF (Cinematic Intermediate Format).
2. Le convertisseur Lua itère sur l'AST, filtre le texte narratif d'origine (selon notre doctrine de "Remake 30 ans plus tard"), et génère un `.lua` prêt pour RogueEssence.
