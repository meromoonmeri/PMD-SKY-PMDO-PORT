#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_previews.py — Génère les PNG de prévisualisation de TOUS les grounds
================================================================================
Rendu frame 0 de chaque .rsground depuis ses .tile, pour inspection visuelle
des tuiles manquantes. Les tuiles manquantes sont marquées en MAGENTA vif
(255,0,255) afin d'être immédiatement repérables.

Sortie : output/Previews/<ground>.png  (+ rapport output/preview_report.json)

Usage : python3 tools/generate_previews.py [--limit N]
"""
import io
import json
import os
import struct
import subprocess
import sys
import time
import urllib.request

from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, 'output', 'Previews')
TILECACHE = '/tmp/preview_tiles'
BASE_URL = 'https://raw.githubusercontent.com/meromoonmeri/PMD-SKY-PMDO-PORT/master'
MISSING_COLOR = (255, 0, 255)  # magenta vif

os.makedirs(OUT, exist_ok=True)
os.makedirs(TILECACHE, exist_ok=True)


def git(args, check=True):
    return subprocess.run(['git'] + list(args), cwd=REPO, check=check,
                          capture_output=True, text=True)


def fetch(url, dest):
    if os.path.isfile(dest) and os.path.getsize(dest) > 0:
        return True
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'preview-gen'})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
        with open(dest, 'wb') as f:
            f.write(data)
        return True
    except Exception as e:
        print(f'    !! fetch fail {url}: {e}')
        return False


def get_rsground(name):
    dest = os.path.join(TILECACHE, f'{name}.rsground')
    if fetch(f'{BASE_URL}/output/Grounds/{name}.rsground', dest):
        return dest
    return None


def get_tile(sheet):
    dest = os.path.join(TILECACHE, f'{sheet}.tile')
    if fetch(f'{BASE_URL}/output/Tiles/{sheet}.tile', dest):
        return dest
    return None


def load_package(path):
    raw = open(path, 'rb').read()
    ts, count = struct.unpack_from('<II', raw, 0)
    cells = {}
    for i in range(count):
        key, off = struct.unpack_from('<QQ', raw, 8 + i * 16)
        x, y = key & 0xFFFFFFFF, key >> 32
        ln = struct.unpack_from('<Q', raw, off)[0]
        cells[(x, y)] = Image.open(io.BytesIO(raw[off + 8:off + 8 + ln])).convert('RGBA')
    return cells


def render(name):
    """Retourne (png_path, nb_missing, dims, sheet) ou None."""
    gp = get_rsground(name)
    if gp is None:
        return {'name': name, 'error': 'rsground introuvable'}
    try:
        d = json.load(open(gp, encoding='utf-8-sig'))['Object']
    except Exception as e:
        return {'name': name, 'error': f'rsground illisible: {e}'}
    try:
        sheet = d['Layers'][0]['Tiles'][0][0]['Layers'][0]['Frames'][0]['Sheet']
    except Exception:
        sheet = None
    if sheet is None:
        return {'name': name, 'error': 'aucune tuile (carte vide ?)'}
    tp = get_tile(sheet)
    if tp is None:
        return {'name': name, 'error': f'tile {sheet} introuvable', 'sheet': sheet}
    try:
        cells = load_package(tp)
    except Exception as e:
        return {'name': name, 'error': f'tile illisible: {e}', 'sheet': sheet}

    W = len(d['Layers'][0]['Tiles'])
    H = len(d['Layers'][0]['Tiles'][0])
    img = Image.new('RGBA', (W * 8, H * 8), (0, 0, 0, 255))
    missing = 0
    for x in range(W):
        for y in range(H):
            frames = d['Layers'][0]['Tiles'][x][y]['Layers'][0]['Frames']
            tl = frames[0]['TexLoc']
            pos = (tl['X'], tl['Y'])
            if pos in cells:
                img.paste(cells[pos], (x * 8, y * 8))
            else:
                missing += 1
                # marquage magenta
                for i in range(8):
                    for j in range(8):
                        img.putpixel((x * 8 + i, y * 8 + j), MISSING_COLOR)
    out_png = os.path.join(OUT, f'{name}.png')
    img.convert('RGB').save(out_png)
    return {'name': name, 'missing': missing, 'dims': f'{W}x{H}',
            'sheet': sheet, 'png': out_png}


def main():
    limit = None
    if '--limit' in sys.argv:
        limit = int(sys.argv[sys.argv.index('--limit') + 1])
    grounds = json.load(open('/tmp/grounds_list.json'))
    if limit:
        grounds = grounds[:limit]
    print(f'Génération de {len(grounds)} previews -> {OUT}')
    report = {'total': len(grounds), 'ok': 0, 'missing_any': [], 'errors': []}
    t0 = time.time()
    for i, g in enumerate(grounds, 1):
        name = g.split('/')[-1][:-9]
        r = render(name)
        if 'error' in r:
            print(f'[{i}/{len(grounds)}] {name}: ERREUR {r["error"]}')
            report['errors'].append(r)
        else:
            report['ok'] += 1
            if r['missing'] > 0:
                report['missing_any'].append({'name': name, 'missing': r['missing'],
                                              'dims': r['dims'], 'sheet': r['sheet']})
                print(f'[{i}/{len(grounds)}] {name}: ⚠ {r["missing"]} tuiles manquantes')
            else:
                print(f'[{i}/{len(grounds)}] {name}: OK ({r["dims"]})')
        if i % 25 == 0:
            print(f'  ... {i}/{len(grounds)} en {time.time()-t0:.0f}s')
    json.dump(report, open(os.path.join(REPO, 'output', 'preview_report.json'),
                           'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print('=' * 60)
    print(f'Terminé : {report["ok"]} OK, {len(report["errors"])} erreurs, '
          f'{len(report["missing_any"])} avec tuiles manquantes')
    if report['missing_any']:
        print('Cartes avec tuiles manquantes :')
        for m in report['missing_any']:
            print(f'  !! {m["name"]}: {m["missing"]} manquantes ({m["dims"]}, sheet {m["sheet"]})')
    print('Rapport : output/preview_report.json')


if __name__ == '__main__':
    main()
