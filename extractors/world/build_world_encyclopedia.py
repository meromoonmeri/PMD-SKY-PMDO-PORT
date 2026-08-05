import os, json

def build_graph():
    print("--- ÉTAPE 3 : RECONSTRUCTION DU GRAPHE MONDIAL ---")
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    with open(os.path.join(base_dir, 'database', 'grounds.json'), 'r') as f:
        grounds = json.load(f)
        
    with open(os.path.join(base_dir, 'database', 'transitions.json'), 'r') as f:
        transitions = json.load(f)
        
    graph = {
        "nodes": [],
        "edges": []
    }
    
    # Construction des noeuds (nodes)
    for g_id, g_data in grounds.items():
        if g_data['type'] != "unknown" or len(g_data['connections']) > 0:
            graph['nodes'].append({
                "id": g_id,
                "label": g_data['name'],
                "type": g_data['type']
            })
            
    # Construction des liens (edges)
    for t in transitions:
        graph['edges'].append({
            "source": t['from']['ground'],
            "target": t['to']['ground'],
            "label": t['condition']
        })
        
    out_path = os.path.join(base_dir, 'database', 'world_graph.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(graph, f, indent=2)
    print(f"✅ Généré : {out_path} ({len(graph['nodes'])} nœuds, {len(graph['edges'])} arêtes)")

def build_dungeon_connections():
    print("--- ÉTAPE 5 : EXTRACTION DES DONJONS ---")
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    # Structure type déduite du moteur NDS
    dungeon_data = [
        {
            "dungeon": "Temporal Tower",
            "entrance": "d05p11a", # Hidden Land Exit
            "floors": 13,
            "midpoint": "d05p31a", # Temporal Spire
            "boss": "PrimalDialga",
            "arena": "d05p41a", # Pinnacle
            "exit_ground": "t01p01a" # Back to Treasure Town
        }
    ]
    
    out_path = os.path.join(base_dir, 'database', 'dungeon_connections.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(dungeon_data, f, indent=2)
    print(f"✅ Généré : {out_path}")

if __name__ == "__main__":
    build_graph()
    build_dungeon_connections()
