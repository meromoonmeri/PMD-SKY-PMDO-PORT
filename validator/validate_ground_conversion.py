import os, json

def validate_ground(rsground_path):
    report = {
        "status": "SUCCESS",
        "errors": [],
        "warnings": []
    }
    
    with open(rsground_path, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
        
    obj = data.get('Object', {})
    
    # Validation 1: Obstacles (Collisions)
    obs = obj.get('obstacles', [])
    if not obs:
        report['errors'].append("Aucune collision (obstacles) détectée.")
        
    # Validation 2: Entities
    ents = obj.get('Entities', [{}])[0]
    spawners = ents.get('Spawners', [])
    markers = ents.get('Markers', [])
    events = ents.get('GroundObjects', [])
    
    if not any(m.get('EntName') == 'Main_Entrance_Marker' for m in markers):
        report['errors'].append("Aucun point de spawn Joueur (Main_Entrance_Marker) trouvé.")
        
    # Validation 3: Out of bounds
    w = len(obs)
    h = len(obs[0]) if w > 0 else 0
    for s in spawners:
        sx = s['Collider']['X'] / 8
        if sx > w:
            report['errors'].append(f"Le Spawner {s['EntName']} est hors map (X={sx} > {w})")
            
    if len(report['errors']) > 0:
        report['status'] = "FAILED"
        
    return report

if __name__ == "__main__":
    test_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output', 'Grounds', 'b01p01_beach.rsground')
    print("--- 7. AUDIT QUALITÉ GROUND ---")
    
    if os.path.exists(test_file):
        rep = validate_ground(test_file)
        print(f"GROUND CONVERSION STATUS: {rep['status']}")
        if rep['errors']:
            for e in rep['errors']: print(f"  - ERROR: {e}")
