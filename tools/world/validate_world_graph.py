import os, json

def validate_world(graph_path):
    print("--- ÉTAPE 7 : VALIDATION DU GRAPHE ---")
    
    with open(graph_path, 'r', encoding='utf-8') as f:
        graph = json.load(f)
        
    errors = []
    node_ids = {n['id'] for n in graph['nodes']}
    
    for edge in graph['edges']:
        if edge['source'] not in node_ids:
            errors.append(f"Warp sans origine valide: {edge['source']}")
        if edge['target'] not in node_ids:
            errors.append(f"Destination inexistante: {edge['target']}")
            
    if errors:
        print("WORLD GRAPH STATUS : FAILED")
        for e in errors: print(f" - {e}")
    else:
        print("WORLD GRAPH STATUS : SUCCESS")
        print("Tous les warps et transitions canoniques analysés pointent vers des lieux existants en mémoire.")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    validate_world(os.path.join(base_dir, 'database', 'world_graph.json'))
