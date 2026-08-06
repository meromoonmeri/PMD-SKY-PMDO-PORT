#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
convert_nds_map.py — Conversion pixel-perfect MAP_BG PMD Sky (NDS) -> PMDO
=============================================================================
Décode les décors de donjon de Pokémon Donjon Mystère Explorateurs du Ciel
(présents dans pret/pmd-sky/files/MAP_BG/ sous forme .bpl/.bpc/.bma/.bpa)
avec skytemple-files, puis les convertit en assets RogueEssence :

  - .tile : planche 8px contenant TOUTES les tuiles uniques de TOUTES les
            frames d'animation (eau/lave/cascades), format RogueEssence.
  - .rsground : la carte rendue à l'identique (bma.to_pil), avec
            - Layers[0].Tiles[x][y].Layers[0].Frames = les frames d'animation
              de la cellule (FrameLength=10 si animée, 60 sinon)
            - obstacles = collision BMA d'origine (Tags 1 = bloqué)
            - Main_Entrance_Marker au centre de la zone marchable
            - AssetName = nom du fichier (règle New Era)

Le rendu est FAIT PAR LE MOTEUR de skytemple-files (bma.to_pil) : c'est
exactement l'image affichée par le jeu, aucune transformation spatiale.

Usage :
  python3 tools/convert_nds_map.py <bpl> <bpc> <bma> <asset_name> [--bpa <f>] [--fr <Nom FR>]
Exemple :
  python3 tools/convert_nds_map.py d42p41a d42p41a d42p41a aegis_cave_boss --fr "Aegis Cave Boss Arena"
"""
import io
import json
import os
import struct
import sys

from skytemple_files.common.types.file_types import FileType

BASE = '/tmp/pmd-sky/files/MAP_BG'


def write_tile_file(img_frames, out_path, tile_size=8):
    """Pack une planche .tile avec toutes les tuiles uniques de toutes les frames.
    Déduplication par PIXELS (les PNG PIL diffèrent pour des pixels identiques
    selon le mode d'image : on normalise en RGBA et on compare les pixels).
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
    # convertit les index en positions (px,py) de la planche
    per_frame_pos = [[(idx % pwidth, idx // pwidth) for idx in fc]
                     for fc in per_frame]
    return per_frame_pos, n


def make_rsground(name, name_fr, comment, sheet, W, H, collision, per_frame,
                  out_path):
    def tile_cell(frames_pos):
        """frames_pos : liste de (px, py) dans la planche, une par frame.
        Déduplique les frames identiques (cellules statiques -> 1 frame)."""
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

    # Main_Entrance_Marker : walkable le plus proche du centre géométrique
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


def convert(bpl, bpc, bma, asset, name_fr, bpa=None):
    bma_obj = FileType.BMA.deserialize(open(f'{BASE}/{bma}.bma', 'rb').read())
    bpc_obj = FileType.BPC.deserialize(open(f'{BASE}/{bpc}.bpc', 'rb').read())
    bpl_obj = FileType.BPL.deserialize(open(f'{BASE}/{bpl}.bpl', 'rb').read())
    bpas = []
    if bpa:
        bpas.append(FileType.BPA.deserialize(open(f'{BASE}/{bpa}.bpa', 'rb').read()))
    frames = bma_obj.to_pil(bpc_obj, bpl_obj, bpas, include_collision=False)

    W = bma_obj.map_width_camera
    H = bma_obj.map_height_camera
    coll = bma_obj.collision
    derived = coll is None
    if coll is None:
        # Pas de couche collision dans le .bma (motif de base) : dérivation
        # documentée — tuile 8x8 entièrement noire = bloquée, sinon libre.
        img0 = frames[0].convert('RGB')
        px = img0.load()
        coll = []
        for y in range(H):
            for x in range(W):
                black = all(px[x*8+i, y*8+j][:3] == (0, 0, 0)
                            for i in (0, 3, 7) for j in (0, 3, 7))
                coll.append(black)
    collision = list(coll)
    if len(collision) != W * H:
        collision = collision + [True] * (W * H - len(collision))

    sheet = ''.join(p.capitalize() for p in asset.split('_')) + '_Base'
    per_frame, n_uniq = write_tile_file(frames, f'output/Tiles/{sheet}.tile')
    comment = (f'PMD Sky (NDS) MAP_BG {bpl}/{bpc}/{bma} -> {asset}. '
               f'Rendered pixel-perfect via skytemple-files (bma.to_pil), '
               f'{len(frames)} frame(s) d\'animation, collision BMA d\'origine. '
               f'Source: pret/pmd-sky files/MAP_BG.')
    make_rsground(asset, name_fr, comment, sheet, W, H, collision, per_frame,
                  f'output/Grounds/{asset}.rsground')
    # statistiques
    walk = sum(1 for c in collision if not c)
    print(f'{bma} -> {asset:24s} {W}x{H} tuiles, {len(frames)} frame(s), '
          f'tuiles planche={n_uniq}u, libre={walk}/{W*H}')
    return {'src': bma, 'asset': asset, 'W': W, 'H': H, 'frames': len(frames),
            'tiles': n_uniq, 'walk': walk, 'total': W * H}


if __name__ == '__main__':
    args = [a for a in sys.argv[1:]]
    bpl = args[0]
    bpc = args[1] if len(args) > 1 else bpl
    bma = args[2] if len(args) > 2 else bpl
    asset = args[3] if len(args) > 3 else bpl.lower()
    name_fr = asset
    bpa = None
    if '--bpa' in args:
        bpa = args[args.index('--bpa') + 1]
    if '--fr' in args:
        name_fr = args[args.index('--fr') + 1]
    convert(bpl, bpc, bma, asset, name_fr, bpa)
