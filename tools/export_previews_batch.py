#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
export_previews_batch.py — PNG de prévisualisation de tous les grounds, par lots
=================================================================================
Rendu frame 0 de chaque .rsground depuis ses .tile (tuiles manquantes marquées
en MAGENTA). Sauvegarde continue : commit + push par lot de 50, puis purge
locale (skip-worktree) pour rester sous la limite disque.

Usage : python3 tools/export_previews_batch.py
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
TMP = '/tmp/pv'
BASE_URL = 'https://raw.githubusercontent.com/meromoonmeri/PMD-SKY-PMDO-PORT/master'
MISSING_COLOR = (255, 0, 255)
BATCH = 50

os.makedirs(TMP, exist_ok=True)


def git(*args, check=True):
    return subprocess.run(['git'] + list(args), cwd=REPO, check=check,
                          capture_output=True, text=True)


def fetch(url, dest):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'pv'})
        with urllib.request.urlopen(req, timeout=90) as r:
            data = r.read()
        with open(dest, 'wb') as f:
            f.write(data)
        return True
    except Exception as e:
        print(f'    !! fetch fail: {e}')
        return False


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


def render_one(name):
    rg = os.path.join(TMP, f'{name}.rsground')
    if not fetch(f'{BASE_URL}/output/Grounds/{name}.rsground', rg):
        return {'name': name, 'error': 'rsground fetch fail'}
    try:
        d = json.load(open(rg, encoding='utf-8-sig'))['Object']
    except Exception as e:
        return {'name': name, 'error': f'rsground parse: {e}'}
    try:
        sheet = d['Layers'][0]['Tiles'][0][0]['Layers'][0]['Frames'][0]['Sheet']
    except Exception:
        sheet = None
    if sheet is None:
        return {'name': name, 'error': 'aucune tuile (carte vide)'}
    tp = os.path.join(TMP, f'{sheet}.tile')
    if not fetch(f'{BASE_URL}/output/Tiles/{sheet}.tile', tp):
        return {'name': name, 'error': f'tile {sheet} fetch fail', 'sheet': sheet}
    try:
        cells = load_package(tp)
    except Exception as e:
        return {'name': name, 'error': f'tile parse: {e}', 'sheet': sheet}
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
                for i in range(8):
                    for j in range(8):
                        img.putpixel((x * 8 + i, y * 8 + j), MISSING_COLOR)
    os.makedirs(OUT, exist_ok=True)
    img.convert('RGB').save(os.path.join(OUT, f'{name}.png'))
    return {'name': name, 'missing': missing, 'dims': f'{W}x{H}', 'sheet': sheet}


def main():
    grounds = json.load(open('/tmp/grounds_list.json'))
    names = [g.split('/')[-1][:-9] for g in grounds]
    total = len(names)
    report = {'total': total, 'ok': 0, 'missing_any': [], 'errors': []}
    t0 = time.time()
    for i in range(0, total, BATCH):
        batch = names[i:i + BATCH]
        # purge du tmp avant chaque lot
        for f in os.listdir(TMP):
            os.remove(os.path.join(TMP, f))
        batch_report = []
        for name in batch:
            r = render_one(name)
            if 'error' in r:
                print(f'  ERREUR {name}: {r["error"]}')
                report['errors'].append(r)
                batch_report.append(r)
            else:
                report['ok'] += 1
                if r['missing'] > 0:
                    report['missing_any'].append(r)
                    print(f'  ⚠ {name}: {r["missing"]} tuiles manquantes ({r["dims"]})')
                else:
                    print(f'  OK {name} ({r["dims"]})')
                batch_report.append(r)
        # commit + push du lot
        git('add', 'output/Previews')
        cp = git('commit', '-m', f'feat: previews grounds {batch[0]}..{batch[-1]} ({len(batch)})',
                 check=False)
        if cp.returncode != 0 and 'nothing to commit' not in (cp.stdout + cp.stderr):
            print('  !! commit fail', cp.stderr[-300:])
        p = git('push', 'origin', 'HEAD:master', check=False)
        if p.returncode != 0:
            print('  !! push fail', p.stderr[-300:])
        else:
            print(f'  pushed lot {i//BATCH+1} ({batch[0]}..{batch[-1]})')
        # skip-worktree puis purge locale des PNG
        out = git('ls-files', 'output/Previews')
        for line in (out.stdout or '').splitlines():
            git('update-index', '--skip-worktree', line.strip())
        for f in os.listdir(OUT):
            os.remove(os.path.join(OUT, f))
        # purge tmp
        for f in os.listdir(TMP):
            os.remove(os.path.join(TMP, f))
        print(f'  ... {min(i+BATCH, total)}/{total} en {time.time()-t0:.0f}s')
    json.dump(report, open('/tmp/preview_report.json', 'w', encoding='utf-8'),
              indent=1, ensure_ascii=False)
    print('=' * 60)
    print(f'Terminé : {report["ok"]} OK, {len(report["errors"])} erreurs, '
          f'{len(report["missing_any"])} avec tuiles manquantes')
    if report['missing_any']:
        print('Cartes avec tuiles manquantes :')
        for m in report['missing_any']:
            print(f'  !! {m["name"]}: {m["missing"]} ({m["dims"]}, sheet {m["sheet"]})')
    if report['errors']:
        print('Erreurs :')
        for e in report['errors']:
            print(f'  !! {e}')


if __name__ == '__main__':
    main()
