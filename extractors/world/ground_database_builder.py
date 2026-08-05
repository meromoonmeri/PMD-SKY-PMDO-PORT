import os, json, re

def build_ground_db(pmd_sky_path):
    print("--- ÉTAPE 1 : INVENTAIRE COMPLET DES GROUNDS ---")
    
    script_dir = os.path.join(pmd_sky_path, 'files', 'language-specific', 'US', 'SCRIPT')
    if not os.path.exists(script_dir):
        print(f"Erreur: {script_dir} introuvable.")
        return {}

    grounds = {}
    
    # Analyse de tous les dossiers de scripts (qui correspondent aux Grounds)
    for folder in os.listdir(script_dir):
        if folder.startswith('.') or not os.path.isdir(os.path.join(script_dir, folder)):
            continue
            
        ground_id = folder.lower()
        
        # Classification heuristique basée sur les conventions de nommage Chunsoft
        g_type = "unknown"
        if ground_id.startswith('t'): g_type = "town"
        elif ground_id.startswith('d') and 'p' in ground_id: 
            # DxxPxx: Dungeon parts (entrances, midpoints, summits)
            if '11' in ground_id or '01' in ground_id: g_type = "dungeon_entrance"
            elif '21' in ground_id: g_type = "dungeon_midpoint"
            elif '31' in ground_id or '41' in ground_id: g_type = "boss_arena"
            else: g_type = "cinematic_zone"
        elif ground_id.startswith('m') or ground_id.startswith('s'): g_type = "event"
        
        grounds[ground_id] = {
            "id": ground_id,
            "name": ground_id.upper(), # Sera enrichi par les strings du jeu
            "type": g_type,
            "source": f"files/GROUND/{ground_id}.sir0",
            "script_folder": f"files/language-specific/US/SCRIPT/{folder}",
            "connections": []
        }

    return grounds

if __name__ == "__main__":
    db = build_ground_db('/tmp/pmd-sky')
    out_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'database', 'grounds.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2)
    print(f"✅ Généré : {out_path} ({len(db)} grounds identifiés)")
