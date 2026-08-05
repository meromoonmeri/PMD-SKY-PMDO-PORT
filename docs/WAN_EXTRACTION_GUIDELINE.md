# Processus d'Extraction des Animations WAN (Nintendo DS -> PMDO)

Le moteur NDS utilise le format `.wan` (Wide Animation Network) pour les sprites de monstres et d'objets.

## Architecture PMDO (RogueEssence)
Dans PMDO, les animations (objets lâchés, attaques spéciales, auras de boss) sont gérées sous forme de dossiers PNG (AnimData) avec des fichiers `AnimData.xml` qui définissent le nombre de frames et la durée.

## Règle de Conversion
1. **Anti-Doublons** : Tous les `.wan` correspondants aux Pokémon ou aux objets communs (Pommes, Baies) sont **ignorés**. PMDO possède déjà ces sprites en HD.
2. **Extraction ciblée** : Seuls les `.wan` d'objets exclusifs à Sky (ex: Rouages du Temps, Blocs de pierre spatiaux, Auras de Primal Dialga) doivent être désassemblés en séquences PNG et exportés.
