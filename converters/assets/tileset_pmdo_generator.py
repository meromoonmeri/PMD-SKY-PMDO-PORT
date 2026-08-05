import os, json, struct, io
from PIL import Image

def generate_tile_file(img, out_path, tile_size=8):
    """
    Fonction officielle (issue du tutoriel) pour créer le binaire .tile de RogueEssence.
    Déchire le PNG en tuiles indexées en 64-bits.
    """
    W, H = img.size
    cols, rows = W // tile_size, H // tile_size
    entries = []
    
    # 1. Découpage du PNG et compression en mémoire
    for y in range(rows):
        for x in range(cols):
            t = img.crop((x*tile_size, y*tile_size, (x+1)*tile_size, (y+1)*tile_size))
            buf = io.BytesIO()
            t.save(buf, 'PNG', optimize=True)
            entries.append(((x | (y << 32)), buf.getvalue()))
            
    # 2. Dédoublonnage
    uniq, order = {}, []
    for key, png in entries:
        if png not in uniq:
            uniq[png] = None
            order.append(png)
            
    # 3. Ecriture de l'en-tête (Header)
    header_size = 8 + len(entries) * 16
    offsets, pos = {}, header_size
    for h in order:
        offsets[h] = pos
        pos += 8 + len(h)
        
    out = bytearray()
    out += struct.pack('<II', tile_size, len(entries))
    
    for key, png in entries:
        out += struct.pack('<QQ', key, offsets[png])
    for h in order:
        out += struct.pack('<Q', len(h)) + h
        
    with open(out_path, 'wb') as f:
        f.write(bytes(out))
        
    return len(entries), len(order)

def bake_tilemodel_to_png(tile_ast):
    """
    Reconstruit l'image 2D depuis les données brutes (Pixel-Perfect Baking)
    """
    tiles_count = tile_ast['tiles_count']
    palettes = tile_ast['palettes']
    
    # Calcul des dimensions (Carré approximatif)
    cols = 16
    rows = (tiles_count // cols) + (1 if tiles_count % cols != 0 else 0)
    
    img = Image.new('RGBA', (cols * 8, rows * 8), (0, 0, 0, 0))
    
    for ti, pixels in enumerate(tile_ast['pixels']):
        tx = ti % cols
        ty = ti // cols
        
        for py in range(8):
            for px in range(8):
                idx = pixels[py * 8 + px]
                color = tuple(palettes[idx])
                img.putpixel((tx * 8 + px, ty * 8 + py), color)
                
    return img

if __name__ == "__main__":
    ast_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'intermediate', 'assets', 'b01p01_tileset_analysis.json')
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'output', 'Tiles')
    os.makedirs(out_dir, exist_ok=True)
    
    print("--- 2. GÉNÉRATEUR DE TILESET PMDO (.tile) ---")
    
    with open(ast_path, 'r', encoding='utf-8') as f:
        ast = json.load(f)
        
    img = bake_tilemodel_to_png(ast)
    png_path = os.path.join(out_dir, f"{ast['asset_name']}.png")
    img.save(png_path)
    print(f"✅ Baking de la matrice NDS vers PNG réussi : {png_path}")
    
    tile_path = os.path.join(out_dir, f"{ast['asset_name']}.tile")
    total, uniq = generate_tile_file(img, tile_path)
    print(f"✅ Format .tile natif PMDO généré : {tile_path} ({total} tuiles dont {uniq} uniques)")
