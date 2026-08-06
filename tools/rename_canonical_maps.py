#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rename_canonical_maps.py — Renommage canonique des MAP_BG exports
==================================================================
Corrige l'IDENTITÉ des cartes (uniquement les noms de fichiers + AssetName +
Name). NE TOUCHE PAS aux .tile, frames, collisions, layers, dimensions.

Table officielle : pret/pmd-sky/include/enums.h (DUNGEON_* = ID) — le préfixe
d## des MAP_BG == DUNGEON_ID (vérifié 1:1 sur les 95 groupes).

Anciennes erreurs corrigées :
  - d00 (TEST_DUNGEON=0) était nommé waterfall_cave_*  -> test_dungeon_*
  - d42 (TEMPORAL_SPIRE=42) était nommé aegis_cave_*   -> temporal_spire_*
Nouvelles identités canoniques :
  - d06 (WATERFALL_CAVE=6)  -> waterfall_cave_1        (le VRAI Waterfall Cave)
  - d54-d61 (AEGIS CAVE)    -> aegis_cave_ice/regice/rock/regirock/steel/
                               registeel/pit/regigigas

Usage : python3 tools/rename_canonical_maps.py
Prérequis : clone partiel SKY_PORT (--filter=blob:none --no-checkout),
fichiers source présents sur origin/master, git auth configurée.
"""
import json
import os
import subprocess
import sys

REPO = '/home/user/SKY_PORT'

# old -> (new, nom_EN_officiel, nom_FR)
RENAMES = {
    # --- CORRECTIONS d'identité (mauvais noms précédents) ---
    'waterfall_cave_entrance': ('test_dungeon_1', 'Test Dungeon 1', 'Donjon de Test 1'),
    'waterfall_cave_boss':     ('test_dungeon_2', 'Test Dungeon 2', 'Donjon de Test 2'),
    'aegis_cave_entrance':     ('temporal_spire_1', 'Temporal Spire 1', 'Flèche du Temps 1'),
    'aegis_cave_boss':         ('temporal_spire_2', 'Temporal Spire 2', 'Flèche du Temps 2'),
    'aegis_cave_ice':          ('temporal_spire_3', 'Temporal Spire 3', 'Flèche du Temps 3'),
    'aegis_cave_rock':         ('temporal_spire_4', 'Temporal Spire 4', 'Flèche du Temps 4'),
    # --- VRAI Waterfall Cave (d06) ---
    'd06p11a':                 ('waterfall_cave_1', 'Waterfall Cave 1', 'Grotte Cascade 1'),
    # --- Aegis Cave : Ice Maze (d54) ---
    'd54p11a': ('aegis_cave_ice_1', 'Ice Aegis Cave 1', 'Grotte d\'Aegis — Glace 1'),
    'd54p31a': ('aegis_cave_ice_2', 'Ice Aegis Cave 2', 'Grotte d\'Aegis — Glace 2'),
    'd54p32a': ('aegis_cave_ice_3', 'Ice Aegis Cave 3', 'Grotte d\'Aegis — Glace 3'),
    # --- Aegis Cave : Regice Chamber (d55) ---
    'd55p11a': ('aegis_cave_regice_1', 'Regice Chamber 1', 'Chambre de Regice 1'),
    'd55p21a': ('aegis_cave_regice_2', 'Regice Chamber 2', 'Chambre de Regice 2'),
    'd55p41a': ('aegis_cave_regice_3', 'Regice Chamber 3', 'Chambre de Regice 3'),
    # --- Aegis Cave : Rock Maze (d56) ---
    'd56p11a': ('aegis_cave_rock_1', 'Rock Aegis Cave 1', 'Grotte d\'Aegis — Roche 1'),
    'd56p12a': ('aegis_cave_rock_2', 'Rock Aegis Cave 2', 'Grotte d\'Aegis — Roche 2'),
    'd56p21a': ('aegis_cave_rock_3', 'Rock Aegis Cave 3', 'Grotte d\'Aegis — Roche 3'),
    'd56p41a': ('aegis_cave_rock_4', 'Rock Aegis Cave 4', 'Grotte d\'Aegis — Roche 4'),
    # --- Aegis Cave : Regirock Chamber (d57) ---
    'd57p21a': ('aegis_cave_regirock_1', 'Regirock Chamber 1', 'Chambre de Regirock 1'),
    'd57p41a': ('aegis_cave_regirock_2', 'Regirock Chamber 2', 'Chambre de Regirock 2'),
    'd57p42a': ('aegis_cave_regirock_3', 'Regirock Chamber 3', 'Chambre de Regirock 3'),
    'd57p43a': ('aegis_cave_regirock_4', 'Regirock Chamber 4', 'Chambre de Regirock 4'),
    'd57p44a': ('aegis_cave_regirock_5', 'Regirock Chamber 5', 'Chambre de Regirock 5'),
    # --- Aegis Cave : Steel Maze / Registeel / Pit / Regigigas ---
    'd58p41a': ('aegis_cave_steel_1', 'Steel Aegis Cave 1', 'Grotte d\'Aegis — Acier 1'),
    'd59p41a': ('aegis_cave_registeel_1', 'Registeel Chamber 1', 'Chambre de Registeel 1'),
    'd60p41a': ('aegis_cave_pit_1', 'Aegis Cave Pit 1', 'Fosse d\'Aegis 1'),
    'd61p41a': ('aegis_cave_regigigas_1', 'Regigigas Chamber 1', 'Chambre de Regigigas 1'),
}


def git(*args, check=True):
    return subprocess.run(['git'] + list(args), cwd=REPO, check=check,
                          capture_output=True, text=True)


def main():
    print(f'{len(RENAMES)} renommages canoniques -> {REPO}')
    print('=' * 70)
    ok, fail = [], []
    for old, (new, en, fr) in sorted(RENAMES.items()):
        oldp = f'output/Grounds/{old}.rsground'
        newp = f'output/Grounds/{new}.rsground'
        if not os.path.isfile(oldp):
            print(f'  !! {old}: fichier absent localement (sparse?)')
            fail.append(old)
            continue
        # 1. git mv
        git('mv', oldp, newp)
        # 2. MAJ AssetName + Name (metadata uniquement, pas les tiles)
        d = json.load(open(newp, encoding='utf-8-sig'))
        d['Object']['AssetName'] = new
        d['Object']['Name'] = {'DefaultText': en, 'LocalTexts': {'fr': fr}}
        # enrichir le Comment avec la source canonique
        c = d['Object'].get('Comment', '')
        d['Object']['Comment'] = c + f' Canonical name: {en} (source pret/pmd-sky/include/enums.h).'
        with open(newp, 'w', encoding='utf-8-sig') as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
        git('add', newp)
        print(f'  {old:24s} -> {new:24s}  [{en}]')
        ok.append((old, new))
    print('=' * 70)
    print(f'{len(ok)} renommés, {len(fail)} échecs')
    json.dump(ok, open('/tmp/renamed.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
