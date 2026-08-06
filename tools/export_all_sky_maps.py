#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
export_all_sky_maps.py — Export de TOUS les MAP_BG PMD Sky (NDS) -> PMDO
==========================================================================
CONFORME AU CAHIER DES CHARGES (robustesse industrielle) :
  - chaque map est indépendante : PROCESS <map> -> SUCCESS ou FAILED
  - try/except par carte + timeout par carte (600s, cartes 384 frames incluses)
  - logs séparés : output/export_log.txt
  - skip des cartes déjà sur origin/master ; --force pour ré-export
  - rapport final : output/export_progress.json
    (Total / Exportées / Skip / Failed / Animations / BPA / sans collision /
     liste erreurs détaillée avec stack)
  - une erreur ne stoppe jamais le batch.

Usage :
  python3 tools/export_all_sky_maps.py                (tout)
  python3 tools/export_all_sky_maps.py <bpl> ...      (sous-ensemble)
  python3 tools/export_all_sky_maps.py --force <bpl>  (ré-export forcé)
  python3 tools/export_all_sky_maps.py --list         (liste)
Prérequis : pret/pmd-sky dans /tmp/pmd-sky, skytemple-files, git auth.
"""
import glob
import json
import os
import signal
import subprocess
import sys
import time
import traceback

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tools'))
from convert_nds_map import convert  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = '/tmp/pmd-sky/files/MAP_BG'
PROGRESS = os.path.join(REPO, 'output', 'export_progress.json')
LOG_FILE = os.path.join(REPO, 'output', 'export_log.txt')
TIMEOUT_PER_MAP = 600  # secondes

# Les 6 cartes exportées sous noms français (export_sky_maps.py)
ALREADY_EXPORTED = {'d00p01', 'd00p02', 'd42p21a', 'd42p31a', 'd42p41a', 'd42p42a'}


class Timeout(Exception):
    pass


def _alarm(sig, frame):
    raise Timeout()


def log(msg):
    print(msg, flush=True)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')


def inventory():
    def stems(ext):
        return {os.path.basename(f)[: -len(ext) - 1]
                for f in glob.glob(f'{BASE}/*.{ext}')}
    bma, bpc, bpl = stems('bma'), stems('bpc'), stems('bpl')
    bpa_all = sorted(os.path.basename(f)[: -4] for f in glob.glob(f'{BASE}/*.bpa'))
    maps = sorted(bma & bpc & bpl)
    entries = []
    for m in maps:
        bpas = sorted(b for b in bpa_all if b.startswith(m))
        entries.append((m, bpas))
    return entries


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
            log(f'  deja a jour: {src}')
        else:
            raise RuntimeError('commit failed: ' + (cp.stdout + cp.stderr)[-400:])
    p = git('push', 'origin', 'master', check=False)
    if p.returncode != 0:
        raise RuntimeError('push failed: ' + p.stderr[-400:])
    log(f'  pushed origin/master: {src}')
    for f in files:
        if os.path.exists(f):
            os.remove(f)
    git('update-index', '--skip-worktree', *files)
    log(f'  purge locale + skip-worktree: {os.path.basename(files[0])}, '
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

    # log fichier : nouvelle session
    os.makedirs(os.path.join(REPO, 'output'), exist_ok=True)
    open(LOG_FILE, 'a', encoding='utf-8').write(
        f'\n===== SESSION {time.strftime("%Y-%m-%d %H:%M:%S")} =====\n')

    log(f'EXPORT {len(entries)} MAPS -> {REPO} (déjà sur origin: {len(on_origin)})')
    log('=' * 70)

    results = {'total': len(entries), 'exported': 0, 'already': 0, 'failed': [],
               'invalid_refs': [], 'collision_absent': [], 'animated': [],
               'with_bpa': [], 'dims_reports': []}

    for m, bpas in entries:
        asset = m.lower()
        if asset in on_origin and not force:
            log(f'--- {m} --- deja exporte, skip')
            results['already'] += 1
            continue
        log(f'PROCESS {m} (bpa={",".join(bpas) if bpas else "-"})')
        t0 = time.time()
        try:
            signal.signal(signal.SIGALRM, _alarm)
            signal.alarm(TIMEOUT_PER_MAP)
            try:
                info = convert(m, m, m, asset, asset.upper(), bpas)
            finally:
                signal.alarm(0)
            if info['invalid'] > 0:
                results['invalid_refs'].append({'map': m, 'invalid': info['invalid'],
                                                'detail': info['invalid_detail']})
            if info['collision_source'] == 'NONE':
                results['collision_absent'].append(m)
            if info['frames'] > 1:
                results['animated'].append(m)
            if bpas:
                results['with_bpa'].append(m)
            if info['dims'].get('DECISION', '').startswith('rendu'):
                results['dims_reports'].append(info['dims'])
            save_and_purge(m, info)
            results['exported'] += 1
            log(f'  SUCCESS {m} ({time.time()-t0:.0f}s)')
        except Timeout:
            log(f'  FAILED {m}: TIMEOUT ({TIMEOUT_PER_MAP}s)')
            results['failed'].append({'map': m, 'reason': f'timeout {TIMEOUT_PER_MAP}s',
                                      'stack': 'timeout'})
        except Exception as e:
            tb = traceback.format_exc().splitlines()[-3:]
            log(f'  FAILED {m}: {type(e).__name__}: {str(e)[:200]}')
            results['failed'].append({'map': m, 'reason': f'{type(e).__name__}: {str(e)[:200]}',
                                      'stack': tb})
        # checkpoint de reprise : sauvegarde partielle
        json.dump(results, open(PROGRESS, 'w', encoding='utf-8'), indent=1,
                  ensure_ascii=False)

    # --- rapport final ---
    log('=' * 70)
    report = {
        'MAP_BG Conversion Report': True,
        'Total MAP_BG': results['total'],
        'Exportés': results['exported'],
        'Skip (déjà présents)': results['already'],
        'Failed': len(results['failed']),
        'Animations': {
            'Maps avec BPA': len(results['with_bpa']),
            'Maps animées (>1 frame)': len(results['animated']),
            'Maps sans collision BMA (Tags=0 documenté)': len(results['collision_absent']),
        },
        'Références invalides (bug tuiles noires)': results['invalid_refs'],
        'Rapports dimensions': results['dims_reports'],
        'Liste erreurs détaillée': results['failed'],
    }
    json.dump(report, open(PROGRESS, 'w', encoding='utf-8'), indent=1,
              ensure_ascii=False)
    log(f'RAPPORT FINAL -> {PROGRESS}')
    log(json.dumps(report, indent=1, ensure_ascii=False)[:2500])


if __name__ == '__main__':
    main()
