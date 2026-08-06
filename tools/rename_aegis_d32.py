#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rename_aegis_d32.py — Mapping canonique AEGIS CAVE = groupe MAP_BG d32
=======================================================================
Instruction utilisateur (explicite, répétée) : le groupe MAP_BG **d32**
est la série Aegis Cave. Mapping demandé :
    d32p11a -> aegis_cave_entrance
    d32pXX  -> aegis_cave_floor_XX

Corrections associées (révocation des renommages spéculatifs) :
  - d54-d61 (aegis_cave_ice/regice/rock/regirock/steel/registeel/pit/
    regigigas) -> retour aux IDs source neutres (d54p11a, ...)
  - doublons d42 (temporal_spire_1..4) et d00 (test_dungeon_1/2) supprimés
    (les versions batch d42p21a.. / d00p01.. sont conservées)
  - d06 -> waterfall_cave_1 conservé (DUNGEON_WATERFALL_CAVE=6)

Ne modifie PAS : .tile, frames, collisions, layers, dimensions.
Uniquement : nom de fichier + AssetName + Name + note source dans Comment.

Usage : python3 tools/rename_aegis_d32.py
"""
import json
import os
import subprocess
import sys

REPO = '/home/user/SKY_PORT'
G = 'output/Grounds'

# (old, new, EN, FR)
RENAMES = [
    # --- d32 -> Aegis Cave (mapping utilisateur) ---
    ('d32p11a', 'aegis_cave_entrance',  'Aegis Cave Entrance',  "Grotte d'Aegis — Entrée"),
    ('d32p12a', 'aegis_cave_floor_01',  'Aegis Cave Floor 01',  "Grotte d'Aegis — Étage 01"),
    ('d32p13a', 'aegis_cave_floor_02',  'Aegis Cave Floor 02',  "Grotte d'Aegis — Étage 02"),
    ('d32p14a', 'aegis_cave_floor_03',  'Aegis Cave Floor 03',  "Grotte d'Aegis — Étage 03"),
    ('d32p31a', 'aegis_cave_floor_04',  'Aegis Cave Floor 04',  "Grotte d'Aegis — Étage 04"),
    ('d32p32a', 'aegis_cave_floor_05',  'Aegis Cave Floor 05',  "Grotte d'Aegis — Étage 05"),
    ('d32p33a', 'aegis_cave_floor_06',  'Aegis Cave Floor 06',  "Grotte d'Aegis — Étage 06"),
    ('d32p41a', 'aegis_cave_floor_07',  'Aegis Cave Floor 07',  "Grotte d'Aegis — Étage 07"),
    ('d32p42a', 'aegis_cave_floor_08',  'Aegis Cave Floor 08',  "Grotte d'Aegis — Étage 08"),
    ('d32p43a', 'aegis_cave_floor_09',  'Aegis Cave Floor 09',  "Grotte d'Aegis — Étage 09"),
    ('d32p44a', 'aegis_cave_floor_10',  'Aegis Cave Floor 10',  "Grotte d'Aegis — Étage 10"),
    # --- Réversion d54-d61 (renommages spéculatifs aegis_cave_*) ---
    ('aegis_cave_ice_1',     'd54p11a', 'D54P11A', 'D54P11A'),
    ('aegis_cave_ice_2',     'd54p31a', 'D54P31A', 'D54P31A'),
    ('aegis_cave_ice_3',     'd54p32a', 'D54P32A', 'D54P32A'),
    ('aegis_cave_regice_1',  'd55p11a', 'D55P11A', 'D55P11A'),
    ('aegis_cave_regice_2',  'd55p21a', 'D55P21A', 'D55P21A'),
    ('aegis_cave_regice_3',  'd55p41a', 'D55P41A', 'D55P41A'),
    ('aegis_cave_rock_1',    'd56p11a', 'D56P11A', 'D56P11A'),
    ('aegis_cave_rock_2',    'd56p12a', 'D56P12A', 'D56P12A'),
    ('aegis_cave_rock_3',    'd56p21a', 'D56P21A', 'D56P21A'),
    ('aegis_cave_rock_4',    'd56p41a', 'D56P41A', 'D56P41A'),
    ('aegis_cave_regirock_1','d57p21a', 'D57P21A', 'D57P21A'),
    ('aegis_cave_regirock_2','d57p41a', 'D57P41A', 'D57P41A'),
    ('aegis_cave_regirock_3','d57p42a', 'D57P42A', 'D57P42A'),
    ('aegis_cave_regirock_4','d57p43a', 'D57P43A', 'D57P43A'),
    ('aegis_cave_regirock_5','d57p44a', 'D57P44A', 'D57P44A'),
    ('aegis_cave_steel_1',   'd58p41a', 'D58P41A', 'D58P41A'),
    ('aegis_cave_registeel_1','d59p41a','D59P41A', 'D59P41A'),
    ('aegis_cave_pit_1',     'd60p41a', 'D60P41A', 'D60P41A'),
    ('aegis_cave_regigigas_1','d61p41a','D61P41A', 'D61P41A'),
]

# doublons à supprimer (renommages spéculatifs, versions batch conservées)
DELETES = ['temporal_spire_1', 'temporal_spire_2', 'temporal_spire_3', 'temporal_spire_4',
           'test_dungeon_1', 'test_dungeon_2']


def git(*args, check=True):
    return subprocess.run(['git'] + list(args), cwd=REPO, check=check,
                          capture_output=True, text=True)


def main():
    print(f'{len(RENAMES)} renommages + {len(DELETES)} suppressions')
    print('=' * 70)
    for old, new, en, fr in RENAMES:
        oldp = f'{G}/{old}.rsground'
        newp = f'{G}/{new}.rsground'
        if not os.path.isfile(oldp):
            print(f'  !! {old}: absent localement')
            continue
        # 1. git mv
        git('mv', oldp, newp)
        # 2. MAJ identité (AssetName + Name + note source) — PAS les tiles
        d = json.load(open(newp, encoding='utf-8-sig'))
        d['Object']['AssetName'] = new
        d['Object']['Name'] = {'DefaultText': en, 'LocalTexts': {'fr': fr}}
        note = (' Canonical New Era name (Aegis Cave series, MAP_BG group d32 '
                'per project instruction).' if new.startswith('aegis_cave')
                else ' Neutral source ID (speculative rename reverted).')
        d['Object']['Comment'] = (d['Object'].get('Comment', '') + note)
        with open(newp, 'w', encoding='utf-8-sig') as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
        git('add', newp)
        print(f'  {old:22s} -> {new:24s} [{en}]')
    for name in DELETES:
        p = f'{G}/{name}.rsground'
        if os.path.isfile(p):
            git('rm', p)
            print(f'  DEL {name} (doublon spéculatif supprimé)')
    print('=' * 70)
    print('Terminé. Vérifiez avec git status puis commit+push.')


if __name__ == '__main__':
    main()
