import os, json

def disassemble_tileset(rlcn_path, rlts_path):
    """
    Simule la désassemblage de la donnée binaire décompressée d'un Sir0 (RLCN/RLTS)
    vers un Abstract Syntax Tree de Tileset (TileModel).
    Dans le vrai environnement, ce script utilise struct.unpack pour décoder les 15-bits BGR.
    """
    # Simulation du décodage de la Plage (Beach)
    ast = {
        "asset_name": "b01p01_beach_tileset",
        "format": "4BPP",
        "tiles_count": 256,
        "palettes": [
            # Array de RGBA (Simulation)
            [0,0,0,0], [255,255,255,255], [128,128,128,255], [200,150,100,255]
        ],
        "pixels": [
            # Index de palette pour chaque pixel (8x8 = 64 pixels par tuile)
            [0, 1, 2, 3] * 16 # Remplissage factice
        ] * 256
    }
    return ast

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'intermediate', 'assets')
    os.makedirs(out_dir, exist_ok=True)
    
    print("--- 1. DÉSASSEMBLEUR TILESET NDS (RLCN/RLTS) ---")
    ast = disassemble_tileset('dummy.rlcn', 'dummy.rlts')
    
    out_file = os.path.join(out_dir, "b01p01_tileset_analysis.json")
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(ast, f, indent=2)
        
    print(f"✅ Analyse du Tileset générée : {out_file}")
