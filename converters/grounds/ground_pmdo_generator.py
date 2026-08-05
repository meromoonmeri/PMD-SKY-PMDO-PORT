import os, json

def generate_rsground(ground_ast, mapping_db):
    """
    Génère le format final .rsground à partir de l'AST et de la table de compatibilité.
    """
    w = ground_ast['map_size']['width']
    h = ground_ast['map_size']['height']
    
    # 1. Base Structure
    rsground = {
        "Version": "0.8.9.0",
        "Object": {
            "$type": "RogueEssence.Ground.GroundMap, RogueEssence",
            "Name": {"DefaultText": "Converted NDS Map", "LocalTexts": {}},
            "Released": True,
            "obstacles": [[{"Bounds": {"X": x*8, "Y": y*8, "Width": 8, "Height": 8}, "Tags": 0} for y in range(h)] for x in range(w)],
            "Layers": [],
            "Entities": [{"Name": "Entities", "Visible": True, "MapChars": [], "GroundObjects": [], "Spawners": [], "Markers": []}]
        }
    }
    
    # 2. Add Entities
    for ent in ground_ast.get('entities', []):
        if ent['type'] == "player_spawn":
            rsground["Object"]["Entities"][0]["Markers"].append({
                "EntName": mapping_db['mappings']['entities']['player_spawn'],
                "Direction": 4, "EntEnabled": True,
                "Collider": {"X": ent['x']*8, "Y": ent['y']*8, "Width": 16, "Height": 16}
            })
        elif ent['type'] == "npc_spawn":
            rsground["Object"]["Entities"][0]["Spawners"].append({
                "$type": mapping_db['mappings']['entities']['npc_spawn'] + ", RogueEssence",
                "EntName": ent.get('id', 'NPC'), "NPCName": ent.get('npc_id', 'Unknown'),
                "Direction": 4, "EntEnabled": True,
                "Collider": {"X": ent['x']*8, "Y": ent['y']*8, "Width": 16, "Height": 16},
                "CharAnim": "Idle", "CharDir": 4
            })
            
    # 3. Add Events (Triggers)
    for evt in ground_ast.get('events', []):
        if evt['type'] == "event_trigger":
            rsground["Object"]["Entities"][0]["GroundObjects"].append({
                "EntName": "Trigger_" + evt['id'],
                "EntEnabled": True,
                "Collider": {"X": evt['x']*8, "Y": evt['y']*8, "Width": 16, "Height": 16},
                "TriggerType": 1, # Touch
                "TriggerEvent": evt['script']
            })
            
    return rsground

if __name__ == "__main__":
    ast_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'intermediate', 'grounds', 'b01p01_ground_analysis.json')
    map_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'compatibility', 'ground_to_pmdo.json')
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'output', 'Grounds')
    os.makedirs(out_dir, exist_ok=True)
    
    print("--- 5. GÉNÉRATEUR PMDO (.rsground) ---")
    
    with open(ast_path, 'r') as f1, open(map_path, 'r') as f2:
        ast = json.load(f1)
        mapping = json.load(f2)
        
    rsground = generate_rsground(ast, mapping)
    out_file = os.path.join(out_dir, "b01p01_beach.rsground")
    
    with open(out_file, 'w', encoding='utf-8-sig') as f:
        json.dump(rsground, f, indent=2, ensure_ascii=False)
        
    print(f"✅ Rsgound PMDO généré avec succès : {out_file}")
