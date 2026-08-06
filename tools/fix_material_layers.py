#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_material_layers.py — Remplissage du fond des MAP_BG "material layer"
==========================================================================
Diagnostic : certaines MAP_BG (ex: d32 = Aegis Cave) sont des material
layers — le layout BMA ne place que la silhouette du sol (zone jouable), le
reste (hors-zone) est un fond transparent que le jeu DS remplissait via ses
couches BG matérielles (absentes des fichiers). Le .rsground converti est
donc majoritairement noir (76-79%), fidèle mais inutilisable visuellement.

Correction (sans modifier les données NDS) :
  - la zone JOUEABLE (collision libre) garde EXACTEMENT ses tuiles originales
  - la zone BLOQUÉE (fond) est remplie avec un motif de grotte construit à
    partir des tuiles OFFICIELLES du tileset de la carte (rendues via
    skytemple-files, dédupliquées par pixels)
  - la collision BMA est préservée à l'identique
  - le Comment documente le remplissage

Usage : python3 tools/fix_material_layers.py <asset> <bma> [<asset> <bma> ...]
Exemple : python3 tools/fix_material_layers.py aegis_cave_entrance d32p11a
"""
import io
import json
import os
import struct
import sys

from skytemple_files.common.types.file_types import FileType
from PIL import Image

BASE = '/tmp/pmd-sky/files/MAP_BG'
REPO = '/home/user/SKY_PORT'
OUT_TILES = os.path.join(REPO, 'output', 'Tiles')
OUT_GROUNDS = os.path.join(REPO, 'output', 'Grounds')

# couleurs "roche/grotte" à utiliser pour le fond (hors sol beige clair et noir)
ROCHE_HUES = [
    (175, 151, 74), (232, 160, 56), (240, 176, 72),
    (232, 246, 185), (212, 138, 42), (195, 172, 92),
]


def to_rgb555(v):
    return ((v & 0x1F) << 3, ((v >> 5) & 0x1F) << 3, ((v >> 10) & 0x1F) << 3)


def load_tileset_tiles(bpc, bpl):
    """Rend toutes les tuiles 8px du tileset via skytemple (chunks_to_pil),
    retourne la liste des images 8x8 RGBA."""
    img = bpc.chunks_to_pil(0, bpl.palettes, 20)
    img = img.convert('RGBA')
    W, H = img.size
    ts = 8
    tiles = []
    for ty in range(H // ts):
        for tx in range(W // ts):
            t = img.crop((tx * ts, ty * ts, (tx + 1) * ts, (ty + 1) * ts))
            tiles.append(t)
    return tiles


def dominant(tile_img):
    px = tile_img.convert('RGB').load()
    from collections import Counter
    c = Counter(px[x, y] for y in range(8) for x in range(8))
    return c.most_common(1)[0][0]


def pick_rocks(tiles, sol_color):
    """Sélectionne les tuiles 'roche' (couleur dominante dans ROCHE_HUES,
    proche d'une teinte de grotte, différente du sol)."""
    rocks = []
    for t in tiles:
        dom = dominant(t)
        if dom == (0, 0, 0):
            continue
        # proche d'une teinte roche (distance)
        if any(sum((dom[i] - h[i]) ** 2 for i in range(3)) < 2500 for h in ROCHE_HUES):
            rocks.append(t)
    # déduplique par pixels
    uniq, seen = [], set()
    for t in rocks:
        k = t.tobytes()
        if k not in seen:
            seen.add(k)
            uniq.append(t)
    return uniq


def write_tile_file(cell_images, out_path, ts=8):
    """cell_images : liste d'images 8x8 -> planche .tile (dédup pixels)."""
    cell_pos, cell_png = {}, []
    for img in cell_images:
        img = img.convert('RGBA')
        k = img.tobytes()
        if k not in cell_pos:
            cell_pos[k] = len(cell_png)
            buf = io.BytesIO()
            img.save(buf, 'PNG', optimize=True)
            cell_png.append(buf.getvalue())
    n = len(cell_png)
    pwidth = max(20, int(n ** 0.5) + 1)
    entries = []
    for idx, png in enumerate(cell_png):
        entries.append(((idx % pwidth) | ((idx // pwidth) << 32), png))
    entries.sort(key=lambda e: e[0])
    header = 8 + len(entries) * 16
    offsets, pos = {}, header
    order = []
    for key, png in entries:
        if png not in offsets:
            offsets[png] = pos
            order.append(png)
            pos += 8 + len(png)
    out = bytearray()
    out += struct.pack('<II', ts, len(entries))
    for key, png in entries:
        out += struct.pack('<QQ', key, offsets[png])
    for png in order:
        out += struct.pack('<Q', len(png)) + png
    open(out_path, 'wb').write(bytes(out))
    # positions des cellules dans la planche
    return [(cell_pos[img.convert('RGBA').tobytes()] % pwidth,
             cell_pos[img.convert('RGBA').tobytes()] // pwidth)
            for img in cell_images]


def make_rsground(asset, name_en, name_fr, sheet, W, H, collision, cell_pos,
                  out_path):
    def tile_cell(pos):
        return {"AutoTileset": "", "Associates": [],
                "Layers": [{"Frames": [{"Sheet": sheet, "TexLoc": {"X": pos[0], "Y": pos[1]}}],
                            "FrameLength": 60}],
                "NeighborCode": -1}

    tiles = [[tile_cell(cell_pos[y * W + x]) for y in range(H)] for x in range(W)]
    obstacles = [[{"Bounds": {"X": x * 8, "Y": y * 8, "Width": 8, "Height": 8},
                   "Tags": 1 if collision[y * W + x] else 0}
                  for y in range(H)] for x in range(W)]
    walk = [(x, y) for x in range(W) for y in range(H) if not collision[y * W + x]]
    gx, gy = W // 2, H // 2
    hx, hy = min(walk, key=lambda p: (p[0] - gx) ** 2 + (p[1] - gy) ** 2)
    marker = {"EntName": "Main_Entrance_Marker", "Direction": 0, "EntEnabled": True,
              "EntOrder": 0, "InteractOrder": 0, "triggerType": 0,
              "Collider": {"X": hx * 8, "Y": hy * 8, "Width": 16, "Height": 16}}
    comment = (f'{name_fr}. MAP_BG material layer {sheet}: zone jouable = tuiles '
               f'originales exactes, fond hors-zone rempli avec un motif des tuiles '
               f'officielles du tileset source (aucun redessin, collision BMA '
               f'préservée). Source: pret/pmd-sky files/MAP_BG.')
    d = {
        "Version": "0.8.9.0",
        "Object": {
            "$type": "RogueEssence.Ground.GroundMap, RogueEssence",
            "TexSize": 1,
            "Name": {"DefaultText": name_en, "LocalTexts": {"fr": name_fr}},
            "Released": False, "Comment": comment, "obstacles": obstacles,
            "rand": {"$type": "RogueElements.ReRandom, RogueElements", "FirstSeed": 0,
                     "s": [16294208416658607535, 7960286522194355700, 4876170194715417726, 12554865158188930543]},
            "Status": {},
            "Background": {"$type": "RogueEssence.Dungeon.MapBG, RogueEssence",
                           "MapLoc": {"X": 0, "Y": 0},
                           "BGAnim": {"AnimIndex": "", "FrameTime": 1, "StartFrame": -1,
                                      "EndFrame": -1, "AnimDir": -1, "Alpha": 255, "AnimFlip": 0},
                           "BGMovement": {"X": 0, "Y": 0}, "RepeatX": False, "RepeatY": False},
            "BlankBG": {"AutoTileset": "", "Associates": [], "Layers": [], "NeighborCode": -1},
            "Layers": [{"Name": "Base", "Layer": 0, "Visible": True, "Tiles": tiles}],
            "AssetName": asset, "Music": "", "EdgeView": 1, "NoSwitching": False,
            "ViewCenter": None, "ViewOffset": {"X": 0, "Y": 0}, "ActiveChar": None,
            "Decorations": [{"Name": "New Deco", "Layer": 0, "Visible": True, "Anims": []}],
            "Entities": [{"Name": "New EntLayer", "Visible": True, "MapChars": [],
                          "GroundObjects": [], "Spawners": [], "Markers": [marker]}],
        },
    }
    with io.open(out_path, 'w', encoding='utf-8-sig') as f:
        json.dump(d, f, ensure_ascii=False, indent=1)


def fix(asset, bma_name, name_en, name_fr):
    print(f'=== {asset} ({bma_name}) ===')
    bma = FileType.BMA.deserialize(open(f'{BASE}/{bma_name}.bma', 'rb').read())
    bpc = FileType.BPC.deserialize(open(f'{BASE}/{bma_name}.bpc', 'rb').read())
    bpl = FileType.BPL.deserialize(open(f'{BASE}/{bma_name}.bpl', 'rb').read())

    # rendu frame 0 natif (le sol)
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        frames = bma.to_pil(bpc, bpl, [], include_collision=False,
                            include_unknown_data_block=False, pal_ani=False)
    sol_img = frames[0].convert('RGBA')

    W = bma.map_width_camera
    H = bma.map_height_camera
    coll = list(bma.collision)
    if len(coll) != W * H:
        coll = coll + [False] * (W * H - len(coll))

    # tuiles de roche du tileset
    tiles = load_tileset_tiles(bpc, bpl)
    # couleur du sol (dominante des cellules libres)
    px = sol_img.load()
    from collections import Counter
    solc = Counter()
    for y in range(H):
        for x in range(W):
            if not coll[y * W + x]:
                solc[px[x * 8, y * 8]] += 1
    sol_color = solc.most_common(1)[0][0] if solc else (225, 224, 152)
    print(f'  sol dominant: {sol_color}, libres={sum(1 for c in coll if not c)}')
    rocks = pick_rocks(tiles, sol_color)
    print(f'  tuiles roche sélectionnées: {len(rocks)}')
    if not rocks:
        print('  !! AUCUNE tuile roche trouvée, abandon')
        return None

    # motif : pour chaque cellule, image finale
    cell_images = []
    for y in range(H):
        for x in range(W):
            if coll[y * W + x]:
                # fond bloqué : motif de roche déterministe
                r = rocks[(x * 3 + y * 5) % len(rocks)]
                cell_images.append(r)
            else:
                # sol : tuile originale exacte (8x8)
                cell_images.append(sol_img.crop((x * 8, y * 8, x * 8 + 8, y * 8 + 8)))

    os.makedirs(OUT_TILES, exist_ok=True)
    os.makedirs(OUT_GROUNDS, exist_ok=True)
    sheet = ''.join(p.capitalize() for p in asset.split('_')) + '_Base'
    cell_pos = write_tile_file(cell_images, f'{OUT_TILES}/{sheet}.tile')
    make_rsground(asset, name_en, name_fr, sheet, W, H, coll, cell_pos,
                  f'{OUT_GROUNDS}/{asset}.rsground')
    print(f'  OK -> {OUT_GROUNDS}/{asset}.rsground ({W}x{H}, planche {len(set(cell_pos))} tuiles)')
    return asset


if __name__ == '__main__':
    pairs = sys.argv[1:]
    if len(pairs) % 2 != 0:
        print('usage: fix_material_layers.py <asset> <bma> ...')
        sys.exit(1)
    for i in range(0, len(pairs), 2):
        a, b = pairs[i], pairs[i + 1]
        fix(a, b, a.replace('_', ' ').title(), a.replace('_', ' ').title())
