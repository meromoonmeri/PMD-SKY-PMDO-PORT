import os, struct

def validate_tile_file(tile_path):
    report = {
        "status": "SUCCESS",
        "errors": []
    }
    
    if not os.path.exists(tile_path):
        report["status"] = "FAILED"
        report["errors"].append("Fichier manquant.")
        return report
        
    with open(tile_path, 'rb') as f:
        d = f.read()
        
    if len(d) < 8:
        report["status"] = "FAILED"
        report["errors"].append("En-tête trop court.")
        return report
        
    tile_size, num_entries = struct.unpack('<II', d[:8])
    if tile_size != 8:
        report["errors"].append(f"Taille de tuile incorrecte : {tile_size} (Attendu: 8)")
        
    expected_header_end = 8 + (num_entries * 16)
    if len(d) < expected_header_end:
        report["errors"].append("En-tête de dépendances corrompu.")
        
    if report["errors"]:
        report["status"] = "FAILED"
        
    return report

if __name__ == "__main__":
    print("--- 3. VALIDATEUR D'ASSET (TILE) ---")
    test_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output', 'Tiles', 'b01p01_beach_tileset.tile')
    
    rep = validate_tile_file(test_file)
    print(f"ASSET CONVERSION STATUS: {rep['status']}")
    for e in rep['errors']:
        print(f"  - ERROR: {e}")
