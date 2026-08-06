#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
export_all_sky_maps.py — Export de TOUS les décors MAP_BG de PMD Sky (NDS)
===========================================================================
Convertit les 458 layouts de pret/pmd-sky/files/MAP_BG/ (.bpl/.bpc/.bma,
+ .bpa d'animation) en assets RogueEssence avec le pipeline pixel-perfect
(rendu bma.to_pil, injection BPA pour éliminer les tuiles noires), puis
pousse chaque carte sur GitHub avec sauvegarde continue (commit+push+purge).

Les 6 cartes déjà exportées par export_sky_maps.py (waterfall_cave_*,
aegis_cave_*) sont sautées.

Usage :
  python3 tools/export_all_sky_maps.py                (tout, par lots sûrs)
  python3 tools/export_all_sky_maps.py <bpl> ...      (sous-ensemble)
  python3 tools/export_all_sky_maps.py --list         (liste les maps)
Prérequis : pret/pmd-sky dans /tmp/pmd-sky, skytemple-files, git auth.
"""
import glob
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tools'))
from convert_nds_map import convert  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = '/tmp/pmd-sky/files/MAP_BG'

ALREADY_EXPORTED = {'d00p01', 'd00p02', 'd42p21a', 'd42p31a', 'd42p41a', 'd42p42a'}


def inventory():
    def stems(ext):
        return {os.path.basename(f)[: -len(ext) - 1]
                for f in glob.glob(f'{BASE}/*.{ext}')}
    bma, bpc, bpl = stems('bma'), stems('bpc'), stems('bpl')
    bpa_all = sorted(os.path.basename(f)[: -4] for f in glob.glob(f'{BASE}/*.bpa'))
    bpa_by_map = {}
    for b in bpa_all:
        m = re.match(r'^(.*?)(\d+)$', b)
        key = m.group(1) if m else b
        bpa_by_map.setdefault(key, []).append(b)
    maps = sorted(bma & bpc & bpl)
    return [(m, bpa_by_map.get(m, [])) for m in maps]


def already_on_origin():
    out = subprocess.run(['git', 'ls-tree', '-r', '--name-only', 'origin/master'],
                         cwd=REPO, capture_output=True, text=True)
    grounds = set()
    for line in (out.stdout or '').splitlines():
        line = line.strip()
        if line.startswith('output/Grounds/') and line.endswith('.rsground'):
            grounds.add(os.path.basename(line)[:-9])
    return grounds


def git(*args, check=True):
    return subprocess.run(['git'] + list(args), cwd=REPO, check=check,
                          capture_output=True, text=True)


def save_and_purge(src, info):
    sheet = ''.join(p.capitalize() for p in info['asset'].split('_')) + '_Base'
    files = [f'output/Tiles/{sheet}.tile', f'output/Grounds/{info["asset"]}.rsground']
    git('update-index', '--no-skip-worktree', *files, check=False)
    git('add', '-A')
    cp = git('commit', '-m', f'feat: Export carte NDS {src}', check=False)
    if cp.returncode != 0:
        if 'nothing to commit' in (cp.stdout + cp.stderr):
            print(f'  deja a jour: {src}')
        else:
            print(f'  !! COMMIT ECHOUE pour {src}:\n{(cp.stdout+cp.stderr)[-800:]}')
            sys.exit(2)
    p = git('push', 'origin', 'master', check=False)
    if p.returncode != 0:
        print(f'  !! PUSH ECHOUE pour {src}:\n{p.stderr[-800:]}')
        sys.exit(2)
    print(f'  pushed origin/master: {src}')
    for f in files:
        if os.path.exists(f):
            os.remove(f)
    git('update-index', '--skip-worktree', *files)
    print(f'  purge locale + skip-worktree: {os.path.basename(files[0])}, '
          f'{os.path.basename(files[1])}')


def main():
    args = [a for a in sys.argv[1:] if a != '--force']
    force = '--force' in sys.argv
    if '--list' in args:
        for m, b in inventory():
            print(f'{m:12s} bpa={",".join(b) if b else "-"}')
        return
    on_origin = already_on_origin()
    allmaps = inventory()
    if args:
        wanted = {a.lower() for a in args}
        entries = [(m, b) for m, b in allmaps if m.lower() in wanted]
    else:
        entries = [(m, b) for m, b in allmaps if m not in ALREADY_EXPORTED]
    print(f'EXPORT {len(entries)} MAPS -> {REPO} (déjà sur origin: {len(on_origin)})')
    print('=' * 70)
    results, skipped, black_list = [], [], []
    for m, bpas in entries:
        asset = m.lower()
        if asset in on_origin and not force:
            print(f'--- {m} --- deja exporte, skip')
            skipped.append(m)
            continue
        print(f'--- {m} (bpa={",".join(bpas) if bpas else "-"}) ---')
        info = convert(m, m, m, asset, asset.upper(), bpas)
        if info['black'] > 0:
            black_list.append((m, info['black']))
        save_and_purge(m, info)
        results.append(info)
    print('=' * 70)
    print(f'{len(results)} cartes exportées ce run (+{len(skipped)} déjà faites)')
    if black_list:
        print(f'⚠ {len(black_list)} carte(s) avec tuiles noires restantes:')
        for m, n in black_list:
            print(f'  !! {m}: {n} cellules noires')
    else:
        print('✔ 0 carte avec tuiles noires')


if __name__ == '__main__':
    main()
