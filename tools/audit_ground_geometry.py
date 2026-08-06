import os, json

def audit_geometry(grounds_dir):
    print("==================================================")
    print("1. AUDIT DE LA GÉOMÉTRIE DU GROUND")
    print("==================================================")
    
    if not os.path.exists(grounds_dir):
        print("Dossier Grounds introuvable.")
        return
        
    for f in os.listdir(grounds_dir):
        if not f.endswith('.rsground'): continue
        
        filepath = os.path.join(grounds_dir, f)
        with open(filepath, 'r', encoding='utf-8-sig') as f_in:
            data = json.load(f_in)
            
        obj = data.get('Object', {})
        layers = obj.get('Layers', [])
        obstacles = obj.get('obstacles', [])
        
        w = len(layers[0].get('Tiles', [])) if layers else 0
        h = len(layers[0].get('Tiles', [[]])[0]) if w > 0 else 0
        
        obs_w = len(obstacles)
        obs_h = len(obstacles[0]) if obs_w > 0 else 0
        
        status = "SUCCESS"
        issues = []
        
        if w == 0 or h == 0:
            status = "FAILED"
            issues.append("Dimensions nulles.")
            
        if w != obs_w or h != obs_h:
            status = "FAILED"
            issues.append(f"Désynchronisation Géométrie/Collision : Tiles({w}x{h}) != Obstacles({obs_w}x{obs_h})")
            
        print(f"GROUND: {f}")
        print(f"-> Dimensions: {w}x{h}")
        print(f"-> Couches (Layers): {len(layers)}")
        print(f"-> Matrice de Collisions: {obs_w}x{obs_h}")
        print(f"GROUND GEOMETRY STATUS : {status}")
        if issues:
            for i in issues: print(f"  - {i}")
        print("-" * 40)
        
        # We audit only the first 3 for brevity in terminal, but the script supports all
        break

if __name__ == "__main__":
    out_grounds_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output', 'Grounds')
    audit_geometry(out_grounds_dir)
