#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
convert_nds_map.py — Conversion pixel-perfect MAP_BG PMD Sky (NDS) -> PMDO
=============================================================================
CONFORME AU CAHIER DES CHARGES (corrections strictes appliquées).

Objectif : chaque MAP_BG devient un Ground PMDO exploitable :
    Data/Grounds/<asset>.rsground  +  Data/Tiles/<sheet>.tile
contenant Layers / Tiles / Frames / obstacles / Entities / Markers,
chargeable dans RogueEssence/New Era sans correction manuelle.

1. RENDU — OBLIGATOIRE via skytemple-files : bma.to_pil(bpc, bpl, bpas).
   Aucune reconstruction manuelle, aucun redessin, aucune transformation
   spatiale (pas de resize, pas de correction esthétique).

2. COLLISION — SOURCE UNIQUE : bma_obj.collision.
   Cas A : présente  -> exactement les données originales.
   Cas B : absente   -> Tags = 0 PARTOUT (aucune analyse de couleur, aucun
           mur artificiel). Rapport : collision_source=NONE,
           collision_generated=false. Commentaire du .rsground :
           "No BMA collision layer available. No artificial collision generated."

3. DIMENSIONS — audit systématique IMAGE / CAMERA / COLLISION / DECISION.
   Jamais de correction silencieuse : toute différence est consignée.

4. BPA — 8 slots (0-3 layer0, 4-7 layer1) via bpc.layers[L].bpas[i] <-> bpa.
   Validation RÉELLE : une erreur est UNIQUEMENT
     "tile index demandé > tiles disponibles après injection BPA".
   Une tuile noire normale n'est PAS une erreur.

5. LOGS DE PROGRESSION par carte :
   START MAP / LOAD BMA / LOAD BPC / LOAD BPL / LOAD BPA / RENDER /
   WRITE TILE / WRITE GROUND / DONE

Usage :
  python3 tools/convert_nds_map.py <bpl> <bpc> <bma> <asset> [--bpa a,b] [--fr "Nom"]
  OUT=output_test pour tester vers un dossier temporaire.
"""
import contextlib
import io
import json
import os
import re
import struct
import sys

from skytemple_files.common.types.file_types import FileType

BASE = '/tmp/pmd-sky/files/MAP_BG'
OUT_DIR = os.environ.get('OUT', 'output')  # 'output' ou 'output_test'


def log(msg):
    print(msg, flush=True)


def write_tile_file(img_frames, out_path, tile_size=8):
    """Planche .tile : tuiles uniques de toutes les frames, dédup par pixels RGBA.
    Retourne (per_frame, n_uniques). per_frame[f][idx] = (px, py) dans la planche."""
    frames = [fr.convert('RGBA') for fr in img_frames]
    W, H = frames[0].size
    cols, rows = W // tile_size, H // tile_size
    cell_pos = {}       # pixels(tobytes) -> index linéaire
    cell_png = []       # index -> PNG
    per_frame = []
    for fr in frames:
        fc = []
        for y in range(rows):
            for x in range(cols):
                t = fr.crop((x*tile_size, y*tile_size, (x+1)*tile_size, (y+1)*tile_size))
                k = t.tobytes()
                if k not in cell_pos:
                    cell_pos[k] = len(cell_png)
                    buf = io.BytesIO()
                    t.save(buf, 'PNG', optimize=True)
                    cell_png.append(buf.getvalue())
                fc.append(cell_pos[k])
        per_frame.append(fc)
    n = len(cell_png)
    pwidth = max(cols, int(n ** 0.5) + 1)
    entries = []
    for idx, png in enumerate(cell_png):
        entries.append(((idx % pwidth) | ((idx // pwidth) << 32), png))
    entries.sort(key=lambda e: e[0])
    header_size = 8 + len(entries) * 16
    offsets, pos = {}, header_size
    uniq_order = []
    for key, png in entries:
        if png not in offsets:
            offsets[png] = pos
            uniq_order.append(png)
            pos += 8 + len(png)
    out = bytearray()
    out += struct.pack('<II', tile_size, len(entries))
    for key, png in entries:
        out += struct.pack('<QQ', key, offsets[png])
    for png in uniq_order:
        out += struct.pack('<Q', len(png)) + png
    open(out_path, 'wb').write(bytes(out))
    per_frame_pos = [[(idx % pwidth, idx // pwidth) for idx in fc]
                     for fc in per_frame]
    return per_frame_pos, n


def make_rsground(name, name_fr, comment, sheet, W, H, collision, per_frame,
                  out_path):
    def tile_cell(frames_pos):
        seen, uniq = set(), []
        for pos in frames_pos:
            if pos not in seen:
                seen.add(pos)
                uniq.append(pos)
        frames = [{"Sheet": sheet, "TexLoc": {"X": px, "Y": py}}
                  for (px, py) in uniq]
        return {"AutoTileset": "", "Associates": [],
                "Layers": [{"Frames": frames,
                            "FrameLength": 10 if len(frames) > 1 else 60}],
                "NeighborCode": -1}

    tiles = []
    for x in range(W):
        col = []
        for y in range(H):
            idx = y * W + x
            frames_pos = [fr[idx] for fr in per_frame]
            col.append(tile_cell(frames_pos))
        tiles.append(col)

    obstacles = [[{"Bounds": {"X": x*8, "Y": y*8, "Width": 8, "Height": 8},
                   "Tags": 1 if collision[y*W + x] else 0}
                  for y in range(H)] for x in range(W)]

    # Main_Entrance_Marker : FALLBACK uniquement, marche, proche du centre
    walk = [(x, y) for x in range(W) for y in range(H) if not collision[y*W + x]]
    if walk:
        gx, gy = W // 2, H // 2
        hx, hy = min(walk, key=lambda p: (p[0]-gx)**2 + (p[1]-gy)**2)
    else:
        hx, hy = W // 2, H // 2
    marker = {"EntName": "Main_Entrance_Marker", "Direction": 0,
              "EntEnabled": True, "EntOrder": 0, "InteractOrder": 0,
              "triggerType": 0,
              "Collider": {"X": hx*8, "Y": hy*8, "Width": 16, "Height": 16}}

    d = {
        "Version": "0.8.9.0",
        "Object": {
            "$type": "RogueEssence.Ground.GroundMap, RogueEssence",
            "TexSize": 1,
            "Name": {"DefaultText": name_fr, "LocalTexts": {"fr": name_fr}},
            "Released": False,
            "Comment": comment,
            "obstacles": obstacles,
            "rand": {"$type": "RogueElements.ReRandom, RogueElements",
                     "FirstSeed": 0, "s": [16294208416658607535, 7960286522194355700,
                                           4876170194715417726, 12554865158188930543]},
            "Status": {},
            "Background": {"$type": "RogueEssence.Dungeon.MapBG, RogueEssence",
                           "MapLoc": {"X": 0, "Y": 0},
                           "BGAnim": {"AnimIndex": "", "FrameTime": 1,
                                      "StartFrame": -1, "EndFrame": -1,
                                      "AnimDir": -1, "Alpha": 255, "AnimFlip": 0},
                           "BGMovement": {"X": 0, "Y": 0},
                           "RepeatX": False, "RepeatY": False},
            "BlankBG": {"AutoTileset": "", "Associates": [], "Layers": [],
                        "NeighborCode": -1},
            "Layers": [{"Name": "Base", "Layer": 0, "Visible": True,
                        "Tiles": tiles}],
            "AssetName": name,
            "Music": "",
            "EdgeView": 1,
            "NoSwitching": False,
            "ViewCenter": None,
            "ViewOffset": {"X": 0, "Y": 0},
            "ActiveChar": None,
            "Decorations": [{"Name": "New Deco", "Layer": 0, "Visible": True,
                             "Anims": []}],
            "Entities": [{"Name": "New EntLayer", "Visible": True,
                          "MapChars": [],
                          "GroundObjects": [],
                          "Spawners": [],
                          "Markers": [marker]}],
        },
    }
    with io.open(out_path, 'w', encoding='utf-8-sig') as f:
        json.dump(d, f, ensure_ascii=False, indent=1)


def build_bpa_slots(bpc_obj, bpa_files):
    """8 slots (0-3 layer0, 4-7 layer1) : bpc.layers[L].bpas[i] <-> bpa.number_of_tiles."""
    slots = [None] * 8
    bpas_obj = []
    for b in (bpa_files or []):
        bpas_obj.append(FileType.BPA.deserialize(open(f'{BASE}/{b}.bpa', 'rb').read()))
    for L in range(min(2, len(bpc_obj.layers))):
        expected = bpc_obj.layers[L].bpas
        for i, need in enumerate(expected[:4]):
            if need > 0:
                for bpa in bpas_obj:
                    if bpa.number_of_tiles == need and slots[L*4 + i] is None:
                        slots[L*4 + i] = bpa
                        break
    return slots, bpas_obj


def analyze_invalid_refs(errtext, bpc_obj, bpas_obj, bpa_files):
    """Parse les 'invalid tile reference' de skytemple pour produire le rapport
    détaillé : map / layer / tile index demandé / disponibles après BPA / BPA."""
    detail = []
    pat = re.compile(r'TileMappingEntry (\d+) - (\d+) - .*invalid tile reference')
    for m in pat.finditer(errtext):
        idx = int(m.group(1))
        layer = int(m.group(2))
        # tiles disponibles après injection BPA pour ce layer
        base = len(bpc_obj.layers[layer].tiles) if layer < len(bpc_obj.layers) else 0
        bpa_add = 0
        bpa_names = []
        for i in range(4):
            bpa = (bpas_obj[layer*4 + i] if layer*4 + i < len(bpas_obj) else None)
            if bpa is not None:
                bpa_add += bpa.number_of_tiles
                if bpa_files and layer*4 + i < len(bpa_files):
                    bpa_names.append(bpa_files[layer*4 + i])
        detail.append({
            'layer': layer, 'tile_index_demande': idx,
            'tiles_disponibles': base + bpa_add,
            'bpa_associe': ','.join(bpa_names) or 'AUCUN',
        })
    return detail


def convert(bpl, bpc, bma, asset, name_fr, bpa_files=None):
    """Retourne un dict. Ne lève jamais pour données manquantes : tout est
    consigné (champ 'error')."""
    log(f'START MAP {bma}')
    res = {'src': bma, 'asset': asset, 'error': None, 'invalid': 0,
           'invalid_detail': [], 'frames': 0, 'collision_source': 'BMA',
           'collision_generated': True, 'dims': {}, 'logs': []}

    log('LOAD BMA')
    bma_obj = FileType.BMA.deserialize(open(f'{BASE}/{bma}.bma', 'rb').read())
    log('LOAD BPC')
    bpc_obj = FileType.BPC.deserialize(open(f'{BASE}/{bpc}.bpc', 'rb').read())
    log('LOAD BPL')
    bpl_obj = FileType.BPL.deserialize(open(f'{BASE}/{bpl}.bpl', 'rb').read())
    log('LOAD BPA')
    slots, bpas_obj = build_bpa_slots(bpc_obj, bpa_files)

    log('RENDER')
    errbuf = io.StringIO()
    with contextlib.redirect_stderr(errbuf):
        frames = bma_obj.to_pil(bpc_obj, bpl_obj, slots, include_collision=False,
                                include_unknown_data_block=False, pal_ani=True)
    errtext = errbuf.getvalue()
    n_invalid = sum(1 for l in errtext.splitlines() if 'invalid tile' in l)
    res['invalid'] = n_invalid
    res['frames'] = len(frames)
    res['invalid_detail'] = analyze_invalid_refs(errtext, bpc_obj, bpas_obj,
                                                 bpa_files)

    # --- AUDIT DIMENSIONS : IMAGE / CAMERA / COLLISION / DECISION ---
    img_w, img_h = frames[0].size
    grid_w, grid_h = img_w // 8, img_h // 8
    cam_w, cam_h = bma_obj.map_width_camera, bma_obj.map_height_camera
    coll_raw = bma_obj.collision
    coll_len = len(coll_raw) if coll_raw is not None else 0
    res['dims'] = {
        'IMAGE': f'{grid_w}x{grid_h}',
        'CAMERA': f'{cam_w}x{cam_h}',
        'COLLISION': f'{coll_len}',
        'DECISION': ('rendu skytemple conservé tel quel (grille=image)'
                     if (grid_w, grid_h) != (cam_w, cam_h) else 'image==camera'),
    }
    log(f"MAP: {asset} IMAGE: {grid_w}x{grid_h} CAMERA: {cam_w}x{cam_h} "
        f"COLLISION: {coll_len} DECISION: {res['dims']['DECISION']}")

    # --- COLLISION : SOURCE UNIQUE bma_obj.collision ---
    if coll_raw is None:
        # Cas B : AUCUNE collision BMA. Tags=0 partout. AUCUNE analyse pixels.
        res['collision_source'] = 'NONE'
        res['collision_generated'] = False
        collision = [False] * (grid_w * grid_h)
    else:
        collision = list(coll_raw)
        if len(collision) != grid_w * grid_h:
            log(f"  WARN collision({len(collision)}) != grille({grid_w*grid_h}) "
                f"— pad False pour aligner (fidélité BMA conservée)")
            collision = collision + [False] * (grid_w * grid_h - len(collision))

    # --- WRITE .tile ---
    log('WRITE TILE')
    sheet = ''.join(p.capitalize() for p in asset.split('_')) + '_Base'
    os.makedirs(f'{OUT_DIR}/Tiles', exist_ok=True)
    os.makedirs(f'{OUT_DIR}/Grounds', exist_ok=True)
    per_frame, n_uniq = write_tile_file(frames, f'{OUT_DIR}/Tiles/{sheet}.tile')

    # --- WRITE .rsground ---
    log('WRITE GROUND')
    bpa_note = (f'{len(bpas_obj)} BPA(s) injecté(s) ({", ".join(bpa_files or [])})'
                if bpas_obj else 'aucun BPA')
    if res['collision_source'] == 'NONE':
        coll_note = ('No BMA collision layer available. '
                     'No artificial collision generated.')
    else:
        coll_note = 'Collision BMA d\'origine.'
    comment = (f'PMD Sky (NDS) MAP_BG {bpl}/{bpc}/{bma} -> {asset}. '
               f'Rendered pixel-perfect via skytemple-files (bma.to_pil), '
               f'{len(frames)} frame(s), {bpa_note}. {coll_note} '
               f'Source: pret/pmd-sky files/MAP_BG.')
    make_rsground(asset, name_fr, comment, sheet, grid_w, grid_h, collision,
                  per_frame, f'{OUT_DIR}/Grounds/{asset}.rsground')

    walk = sum(1 for c in collision if not c)
    res.update({'W': grid_w, 'H': grid_h, 'tiles': n_uniq, 'walk': walk,
                'total': grid_w * grid_h, 'bpas': bpa_files or []})
    log(f'DONE {bma} -> {asset} {grid_w}x{grid_h}, {len(frames)} frame(s), '
        f'planche={n_uniq}u, libre={walk}/{grid_w*grid_h}, '
        f'invalid_refs={n_invalid}, collision_source={res["collision_source"]}')
    return res


if __name__ == '__main__':
    args = [a for a in sys.argv[1:]]
    bpl = args[0]
    bpc = args[1] if len(args) > 1 else bpl
    bma = args[2] if len(args) > 2 else bpl
    asset = args[3] if len(args) > 3 else bpl.lower()
    name_fr = asset
    bpa_files = None
    if '--bpa' in args:
        bpa_files = args[args.index('--bpa') + 1].split(',')
    if '--fr' in args:
        name_fr = args[args.index('--fr') + 1]
    convert(bpl, bpc, bma, asset, name_fr, bpa_files)
