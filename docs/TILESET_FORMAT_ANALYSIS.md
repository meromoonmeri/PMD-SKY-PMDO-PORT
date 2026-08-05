# Analyse du Format Tileset NDS (Sir0 / RLCN / RLTS)

## Fonctionnement du Moteur NDS (Explorateurs du Ciel)
Dans le moteur GBA, les graphismes étaient souvent à nu ou compressés en LZ77 classique (`.bpc`).
Dans la NDS, Chunsoft a scindé les assets graphiques en deux fichiers encodés dans des conteneurs Sir0 :
1. **`.rlcn` (Resource List Color / Palette)** : Contient les palettes 15-bits (BGR555).
2. **`.rlts` (Resource List Tiles / Tuiles)** : Contient les pixels bruts des tuiles (souvent 4BPP, soit 16 couleurs).

## Objectif : Le "Pixel-Perfect Baking"
RogueEssence ne lit pas les palettes séparées ou les index de tuiles GBA/NDS. Il demande un fichier `.tile` qui est une grande image RGBA 32-bits pré-découpée.
L'extracteur de Tileset doit donc accomplir le même travail que le PPU (Picture Processing Unit) de la Nintendo DS :
- Lire la palette `.rlcn`.
- Lire la tuile 8x8 pixels dans `.rlts`.
- Appliquer la couleur au pixel.
- Gérer l'Alpha (la 1ère couleur de la palette 0 est toujours transparente).
- Exporter un PNG géant.
- Convertir le PNG en `.tile`.

## Le Format Intermédiaire
Le Désassembleur va extraire les pixels et la palette du binaire NDS et les fusionner dans un objet JSON intermédiaire ("TileModel").
Le Générateur lira ce "TileModel" pour dessiner le PNG.
