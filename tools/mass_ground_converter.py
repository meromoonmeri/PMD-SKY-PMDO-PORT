import os, sys, json, struct, io, time, glob
from PIL import Image

base_dir = os.path.dirname(os.path.dirname(__file__))
pmd_map_bg_dirs = ['/tmp/pmd-sky/files/MAP_BG', '/tmp/pmd-sky/files/language-specific/US/MAP_BG']
out_tiles_dir = os.path.join(base_dir, 'output', 'Tiles')
out_grounds_dir = os.path.join(base_dir, 'output', 'Grounds')

os.makedirs(out_tiles_dir, exist_ok=True)
os.makedirs(out_grounds_dir, exist_ok=True)

def parse_bpl(p):
    with open(p, 'rb') as f: d = f.read()
    n = d[0]; pals = []; off = 4
    for _ in range(n):
        cols = [(0,0,0,0)]
        for c in range(15):
            cols.append((d[off], d[off+1], d[off+2], 255))
            off += 4
        pals.append(cols)
    return pals

def parse_bpc(p):
    with open(p, 'rb') as f: d = f.read()
    cw, chh, nt = struct.unpack_from('<HHH', d, 0)
    nc, = struct.unpack_from('<H', d, 14)
    tiles = [bytes(32)] + [d[16+i*32:16+(i+1)*32] for i in range(nt-1)]
    off = 16 + (nt-1)*32; n = cw * chh
    chunks = [[0]*n]
    for i in range(nc-1):
        chunks.append(list(struct.unpack_from(f'<{n}H', d, off)))
        off += n*2
    return cw, chh, tiles, chunks

def parse_bpa(p):
    if not os.path.exists(p): return 0, 0, []
    with open(p, 'rb') as f: d = f.read()
    tiles_per_frame, num_frames = struct.unpack_from('<HH', d, 0)
    if tiles_per_frame == 0 or num_frames == 0: return 0, 0, []
    expected_tile_data_size = tiles_per_frame * num_frames * 32
    header_size = len(d) - expected_tile_data_size
    if header_size < 0: return 0, 0, []
    off = header_size
    frames = []
    for f in range(num_frames):
        frame_tiles = []
        for t in range(tiles_per_frame):
            frame_tiles.append(d[off:off+32])
            off += 32
        frames.append(frame_tiles)
    return tiles_per_frame, num_frames, frames

def decode_bma(p):
    with open(p, 'rb') as f: d = f.read()
    Wt, Ht, tw, th, Wc, Hc = d[:6]
    nL, hD, hC = struct.unpack_from('<HhH', d, 6)
    src = 12; STRIDE = 64; layers = []
    for li in range(nL):
        dst = []
        for j in range(Hc):
            row = []
            prev = dst[(j-1)*STRIDE:j*STRIDE] if j > 0 else [0]*STRIDE
            k = 0
            while k < Wc:
                cmd = d[src]; src += 1
                if cmd >= 0xC0:
                    for l in range(cmd - 0xC0 + 1):
                        v = d[src] | (d[src+1]<<8) | (d[src+2]<<16); src += 3
                        a, b = v & 0xFFF, (v >> 12) & 0xFFF
                        if j > 0: a ^= prev[len(row)]; b ^= prev[len(row)+1]
                        row += [a, b]
                    k += (cmd - 0xBF) * 2
                elif cmd >= 0x80:
                    v = d[src] | (d[src+1]<<8) | (d[src+2]<<16); src += 3
                    for l in range(cmd - 0x80 + 1):
                        a, b = v & 0xFFF, (v >> 12) & 0xFFF
                        if j > 0: a ^= prev[len(row)]; b ^= prev[len(row)+1]
                        row += [a, b]
                    k += (cmd - 0x7F) * 2
                else:
                    for l in range(cmd + 1):
                        if j > 0: row += [prev[len(row)], prev[len(row)+1]]
                        else: row += [0, 0]
                    k += (cmd + 1) * 2
            row = row[:STRIDE] + [0]*(STRIDE - len(row))
            dst += row
        layers.append(dst)
    return Wt, Ht, Wc, Hc, nL, hC, layers

def generate_tile_file(img, out_path, tile_size=8):
    W, H = img.size
    cols, rows = W // tile_size, H // tile_size
    entries = []
    for y in range(rows):
        for x in range(cols):
            t = img.crop((x*tile_size, y*tile_size, (x+1)*tile_size, (y+1)*tile_size))
            buf = io.BytesIO()
            t.save(buf, 'PNG', optimize=True)
            entries.append(((x | (y << 32)), buf.getvalue()))
    uniq, order = {}, []
    for key, png in entries:
        if png not in uniq:
            uniq[png] = None
            order.append(png)
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

def generate_rsground(base_name, W, H, collisions, sheet, anim_frames=1):
    def tile(x, y):
        layers = []
        for i in range(anim_frames):
            layers.append({"Sheet": f"{sheet}_Frame_{i}" if anim_frames > 1 else sheet, "TexLoc": {"X": x, "Y": y}})
        return {"AutoTileset": "", "Associates": [], "Layers": [{"Frames": layers, "FrameLength": 15 if anim_frames > 1 else 60}], "NeighborCode": -1}
        
    tiles = [[tile(x, y) for y in range(H)] for x in range(W)]
    obstacles = [[{"Bounds": {"X": x*8, "Y": y*8, "Width": 8, "Height": 8}, "Tags": 1 if collisions[y*W + x] else 0} for y in range(H)] for x in range(W)]
    
    rsground = {
        "Version": "0.8.9.0",
        "Object": {
            "$type": "RogueEssence.Ground.GroundMap, RogueEssence",
            "Name": {"DefaultText": base_name.upper(), "LocalTexts": {}},
            "Released": True,
            "Comment": f"Auto-converted PMD Sky Map: {base_name}",
            "obstacles": obstacles,
            "Layers": [{"Name": "Base", "Layer": 0, "Visible": True, "Tiles": tiles}],
            "Entities": [{"Name": "Entities", "Visible": True, "MapChars": [], "GroundObjects": [], "Spawners": [], "Markers": [
                {"EntName": "Main_Entrance_Marker", "Direction": 4, "EntEnabled": True, "Collider": {"X": 0, "Y": 0, "Width": 16, "Height": 16}}
            ]}],
            "rand": {"$type": "RogueElements.ReRandom, RogueElements", "s": [0,0,0,0]},
            "Background": {"$type": "RogueEssence.Dungeon.MapBG, RogueEssence", "MapLoc": {"X": 0, "Y": 0}, "BGMovement": {"X": 0, "Y": 0}},
            "BlankBG": {"AutoTileset": "", "Associates": [], "Layers": [], "NeighborCode": -1},
            "Decorations": [{"Name": "New Deco", "Layer": 0, "Visible": True, "Anims": []}],
        }
    }
    with open(os.path.join(out_grounds_dir, f"{base_name}.rsground"), 'w', encoding='utf-8-sig') as f:
        json.dump(rsground, f, indent=2, ensure_ascii=False)

def run_mass_conversion():
    bpl_files = []
    for d in pmd_map_bg_dirs:
        bpl_files.extend(glob.glob(os.path.join(d, '*.bpl')))
        
    print(f"Démarrage de la conversion massive pour {len(bpl_files)} maps Sky (Mode Pixel-Perfect avec Animations)...")
    start_time = time.time()
    success_count = 0; fail_count = 0
    
    for bpl_path in bpl_files:
        base_name = os.path.basename(bpl_path).replace('.bpl', '')
        b_dir = os.path.dirname(bpl_path)
        
        bpc_name = base_name
        if not os.path.exists(os.path.join(b_dir, f'{bpc_name}.bpc')):
            bpc_name = base_name[:-1]
            if not os.path.exists(os.path.join(b_dir, f'{bpc_name}.bpc')):
                bpc_name = base_name[:-2] # some edge cases
        
        bpc_path = os.path.join(b_dir, f'{bpc_name}.bpc')
        bma_path = os.path.join(b_dir, f'{base_name}.bma')
        
        # Look for .bpa
        bpas = glob.glob(os.path.join(b_dir, f'{bpc_name}*.bpa'))
        bpa_path = bpas[0] if bpas else None
        
        if not os.path.exists(bpc_path) or not os.path.exists(bma_path):
            fail_count += 1
            continue
            
        try:
            base_pals = parse_bpl(bpl_path)
            cw, chh, base_tiles, chunks = parse_bpc(bpc_path)
            Wt, Ht, Wc, Hc, nL, hC, layers = decode_bma(bma_path)
            
            tpf, n_frames, anim_frames = parse_bpa(bpa_path) if bpa_path else (0, 1, [[]])
            if n_frames == 0: n_frames = 1; anim_frames = [[]]
            
            collisions = [0] * (Wt * Ht)
            sheet_name = f"{base_name}_tileset"
            
            for frame_idx in range(n_frames):
                current_tiles = list(base_tiles)
                current_tiles.extend(anim_frames[frame_idx] if len(anim_frames)>frame_idx else [])
                
                img = Image.new('RGBA', (Wt * 8, Ht * 8), (0, 0, 0, 255))
                for lay in reversed(layers):
                    for cy in range(Hc):
                        for cx in range(Wc):
                            cid = lay[cy * 64 + cx]
                            if cid <= 0 or cid >= len(chunks): continue
                            for i, ent in enumerate(chunks[cid]):
                                ti = ent & 0x3FF; hf = (ent >> 10) & 1; vf = (ent >> 11) & 1; pi = (ent >> 12) & 0xF
                                if ti == 0 or ti >= len(current_tiles): continue
                                tx, ty = cx * 3 + i % 3, cy * 3 + i // 3
                                if tx * 8 + 8 > Wt * 8 or ty * 8 + 8 > Ht * 8: continue
                                
                                td = current_tiles[ti]
                                pal = base_pals[pi % len(base_pals)]
                                
                                for y in range(8):
                                    for x in range(4):
                                        b = td[y * 4 + x]
                                        for k2, ci in enumerate((b & 0xF, b >> 4)):
                                            if ci == 0: continue
                                            xx = x * 2 + k2; yy = y
                                            if hf: xx = 7 - xx
                                            if vf: yy = 7 - yy
                                            img.putpixel((tx * 8 + xx, ty * 8 + yy), pal[ci])
                                            
                frame_sheet_name = f"{sheet_name}_Frame_{frame_idx}" if n_frames > 1 else sheet_name
                generate_tile_file(img, os.path.join(out_tiles_dir, f"{frame_sheet_name}.tile"))
                
            generate_rsground(base_name, Wt, Ht, collisions, sheet_name, n_frames)
            success_count += 1
            
            if success_count % 50 == 0:
                print(f"Progression : {success_count} maps pixel-perfect traitées...")
                
        except Exception as e:
            fail_count += 1
            
    print(f"\n====================================")
    print(f" BATCH CONVERSION TERMINÉE")
    print(f" Succès: {success_count}")
    print(f" Échecs: {fail_count}")
    print(f" Temps : {time.time() - start_time:.2f} secondes")
    print(f"====================================")

if __name__ == "__main__":
    run_mass_conversion()
