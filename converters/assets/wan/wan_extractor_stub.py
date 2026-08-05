import os

def document_wan_extraction(out_dir):
    md = "# Processus d'Extraction des Animations WAN (Nintendo DS -> PMDO)\n\n"
    md += "Le moteur NDS utilise le format `.wan` (Wide Animation Network) pour les sprites de monstres et d'objets.\n\n"
    md += "## Architecture PMDO (RogueEssence)\n"
    md += "Dans PMDO, les animations (objets lâchés, attaques spéciales, auras de boss) sont gérées sous forme de dossiers PNG (AnimData) avec des fichiers `AnimData.xml` qui définissent le nombre de frames et la durée.\n\n"
    md += "## Règle de Conversion\n"
    md += "1. **Anti-Doublons** : Tous les `.wan` correspondants aux Pokémon ou aux objets communs (Pommes, Baies) sont **ignorés**. PMDO possède déjà ces sprites en HD.\n"
    md += "2. **Extraction ciblée** : Seuls les `.wan` d'objets exclusifs à Sky (ex: Rouages du Temps, Blocs de pierre spatiaux, Auras de Primal Dialga) doivent être désassemblés en séquences PNG et exportés.\n"
    
    with open(os.path.join(out_dir, "WAN_EXTRACTION_GUIDELINE.md"), 'w', encoding='utf-8') as f:
        f.write(md)

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'docs')
    document_wan_extraction(out_dir)
    print("✅ Documentation du pipeline d'animation WAN générée.")
