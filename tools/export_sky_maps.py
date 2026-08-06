#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
export_sky_maps.py — Export des décors canoniques PMD Sky vers PMD-SKY-PMDO-PORT
=================================================================================
Convertit les MAP_BG de pret/pmd-sky (fichiers NDS .bpl/.bpc/.bma) en
assets RogueEssence (.tile + .rsground) et les pousse sur GitHub avec la
sauvegarde continue (commit + push + purge + skip-worktree) par carte.

Cibles : Aegis Cave (D42) et Waterfall Cave (D00), la VRAIE géométrie NDS.

Mapping source -> nom (documenté ; les biomes ice/rock/steel sont indicatifs,
à confirmer en jeu — les 3 layouts restants sont tous des arènes/eaux) :
  d00p01 (dungeon_entrance)  -> waterfall_cave_entrance
  d00p02 (cinematic_zone)    -> waterfall_cave_boss
  d42p21a (dungeon_midpoint) -> aegis_cave_entrance
  d42p31a (boss_arena)       -> aegis_cave_boss
  d42p41a (boss_arena)       -> aegis_cave_ice
  d42p42a (cinematic_zone)   -> aegis_cave_rock
Note : les mazes Ice/Rock/Steel sont procéduraux (pas de layout fixe) ; seuls
les 4 layouts d42 de pret/pmd-sky existent. aegis_cave_steel n'a pas de
layout dédié dans les données versionnées.

Usage : python3 tools/export_sky_maps.py
Prérequis : pret/pmd-sky cloné dans /tmp/pmd-sky ; skytemple-files ; git auth.
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tools'))
from convert_nds_map import convert  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MANIFEST = [
    # (bpl, bpc, bma, asset, nom FR, [bpa])
    ('d00p01', 'd00p01', 'd00p01', 'waterfall_cave_entrance',
     'Waterfall Cave — Entrée', None),
    ('d00p02', 'd00p02', 'd00p02', 'waterfall_cave_boss',
     'Waterfall Cave — Zone du Boss', None),
    ('d42p21a', 'd42p21a', 'd42p21a', 'aegis_cave_entrance',
     'Aegis Cave — Entrée', None),
    ('d42p31a', 'd42p31a', 'd42p31a', 'aegis_cave_boss',
     'Aegis Cave — Arène du Boss', None),
    ('d42p41a', 'd42p41a', 'd42p41a', 'aegis_cave_ice',
     'Aegis Cave — Arène de Glace', None),
    ('d42p42a', 'd42p42a', 'd42p42a', 'aegis_cave_rock',
     'Aegis Cave — Arène de Roche', None),
]


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
    print(f'EXPORT {len(MANIFEST)} DECORS PMD SKY -> {REPO}')
    print('=' * 70)
    results = []
    for bpl, bpc, bma, asset, fr, bpa in MANIFEST:
        print(f'--- {bpl} -> {asset} ---')
        info = convert(bpl, bpc, bma, asset, fr, bpa)
        save_and_purge(bpl, info)
        results.append(info)
    print('=' * 70)
    print(f'{len(results)} decors exportes et pousses.')


if __name__ == '__main__':
    main()
