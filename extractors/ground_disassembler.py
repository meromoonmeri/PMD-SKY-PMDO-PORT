import os, json

def disassemble_ground_data(sir0_json_path):
    """
    Simule la désassemblage de la donnée binaire décompressée d'un Sir0 (RLSN/RLTS)
    vers un Abstract Syntax Tree de Ground.
    """
    if not os.path.exists(sir0_json_path): return None
    
    # Simulation du décodage de la plage "Plage du début" (Beach) - Chapitre 1
    ast = {
        "map_size": {"width": 80, "height": 60},
        "tiles": ["tile_sand", "tile_water", "tile_cliff"],
        "layers": 2,
        "collision": [0, 0, 1, 1, 0], # Matrix flattened
        "entities": [
            {"id": "hero_spawn", "type": "player_spawn", "x": 40, "y": 30},
            {"id": "partner", "type": "npc_spawn", "x": 42, "y": 30, "npc_id": "bulbasaur"}
        ],
        "events": [
            {"id": "cutscene_trigger", "type": "event_trigger", "x": 45, "y": 30, "script": "m01a0103.lua"}
        ]
    }
    
    return ast

if __name__ == "__main__":
    in_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'intermediate', 'sir0_unpacked', 'b01p01_unpacked.json')
    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'intermediate', 'grounds')
    os.makedirs(out_dir, exist_ok=True)
    
    print("--- 3. DÉSASSEMBLEUR GROUND NDS ---")
    ast = disassemble_ground_data(in_path)
    
    out_file = os.path.join(out_dir, "b01p01_ground_analysis.json")
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(ast, f, indent=2)
        
    print(f"Analyse du terrain générée : {out_file}")
