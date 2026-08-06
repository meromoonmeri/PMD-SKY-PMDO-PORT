#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_existing_collision.py — Audit des .rsground déjà poussés sur origin/master
=================================================================================
Consigne §8 : identifier les Grounds générés avec l'ANCIENNE méthode
« pixel noir = collision » (dérivation illégale) pour ne régénérer QUE ceux-là.

Méthode : pour chaque ground exporté qui correspond à une MAP_BG de
pret/pmd-sky, on relit le .bma source :
  - si le BMA possède une couche collision  -> le ground est conforme (Cas A)
  - si le BMA n'a PAS de couche collision   -> le ground CONFORME doit être
    TOUT-WALKABLE (Tags=0 partout, Cas B). S'il contient des Tags=1, il a été
    généré avec la dérivation pixels : À RÉGÉNÉRER.

Usage :
  python3 tools/audit_existing_collision.py [--json out.json]
"""
import glob
import json
import os
import subprocess
import sys

BASE = '/tmp/pmd-sky/files/MAP_BG'


def git(args):
    return subprocess.run(['git'] + args, cwd='/home/user/SKY_PORT',
                          capture_output=True, text=True)


def main():
    # liste des grounds sur origin/master
    out = git(['ls-tree', '-r', '--name-only', 'origin/master'])
    grounds = {}
    for line in (out.stdout or '').splitlines():
        line = line.strip()
        if line.startswith('output/Grounds/') and line.endswith('.rsground'):
            name = os.path.basename(line)[:-9]
            grounds[name] = line

    # maps MAP_BG (noms bma)
    maps = {os.path.basename(f)[: -4]
            for f in glob.glob(f'{BASE}/*.bma')}

    from skytemple_files.common.types.file_types import FileType
    to_regenerate = []
    conform = []
    no_ground = []
    for name in sorted(grounds):
        if name not in maps:
            continue  # pas une MAP_BG (ex: aegis_cave_boss = d42p41a ? si)
        # relire le BMA source
        try:
            bma = FileType.BMA.deserialize(open(f'{BASE}/{name}.bma', 'rb').read())
        except Exception:
            # nom français (waterfall_cave_entrance etc.) : chercher la map
            # source dans le Comment du ground distant
            blob = git(['show', f'origin/master:{grounds[name]}'])
            if blob.returncode == 0:
                try:
                    d = json.loads(blob.stdout.lstrip('\ufeff'))['Object']
                    src = str(d.get('Comment', ''))
                    import re
                    m = re.search(r'MAP_BG (\w+)/', src)
                    if m and os.path.isfile(f'{BASE}/{m.group(1)}.bma'):
                        bma = FileType.BMA.deserialize(open(f'{BASE}/{m.group(1)}.bma','rb').read())
                        name = m.group(1)
                    else:
                        no_ground.append(name)
                        continue
                except Exception:
                    no_ground.append(name)
                    continue
            else:
                no_ground.append(name)
                continue
        coll = bma.collision
        if coll is not None:
            conform.append(name)
            continue
        # BMA sans collision : le ground distant doit être tout-walkable
        blob = git(['show', f'origin/master:{grounds[name]}'])
        try:
            d = json.loads(blob.stdout.lstrip('\ufeff'))['Object']
        except Exception:
            no_ground.append(name)
            continue
        ob = d.get('obstacles') or []
        blocked = sum(1 for col in ob for c in col
                      if (c.get('Tags') if isinstance(c, dict) else c) == 1)
        if blocked > 0:
            to_regenerate.append({'map': name, 'blocked_cells': blocked,
                                  'reason': 'ancienne dérivation pixel noir = collision'})
        else:
            conform.append(name)

    print('=== AUDIT DES EXPORTS EXISTANTS (origin/master) ===')
    print(f'Maps MAP_BG avec ground exporté : {len(grounds) & 0 or "?"}')
    print(f'Conformes (collision BMA ou tout-walkable) : {len(conform)}')
    print(f'À RÉGÉNÉRER (dérivation pixels) : {len(to_regenerate)}')
    for t in to_regenerate:
        print(f'  !! {t["map"]}: {t["blocked_cells"]} cellules bloquées ({t["reason"]})')
    print(f'Non analysables : {len(no_ground)}')
    if '--json' in sys.argv:
        out_path = sys.argv[sys.argv.index('--json') + 1]
        json.dump({'to_regenerate': to_regenerate, 'conform': conform,
                   'no_ground': no_ground},
                  open(out_path, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
        print('écrit:', out_path)


if __name__ == '__main__':
    main()
