#!/usr/bin/env python3
from pathlib import Path
import sys,re,json
from skytemple_files.common.types.file_types import FileType
ROOT=Path(__file__).resolve().parents[1];BASE=Path('/tmp/pmd-sky/files/MAP_BG');sys.path.insert(0,str(ROOT/'tools'))
import convert_nds_map as c
c.BASE=str(BASE)
errors=[];checked=0;with_bpa=0
for bpcp in sorted(BASE.glob('*.bpc')):
 stem=bpcp.stem
 if not (BASE/(stem+'.bma')).exists() or not (BASE/(stem+'.bpl')).exists():continue
 bpc=FileType.BPC.deserialize(bpcp.read_bytes());names=sorted(p.stem for p in BASE.glob(stem+'*.bpa'))
 try:
  slots,loaded=c.build_bpa_slots(bpc,names);checked+=1
  if loaded:with_bpa+=1
 except Exception as e:errors.append({'map':stem,'error':str(e),'bpa':names})
print(json.dumps({'checked':checked,'with_bpa':with_bpa,'errors':len(errors)}))
for e in errors[:30]:print('ERROR',e)
(ROOT/'BPA_SLOT_AUDIT.json').write_text(json.dumps({'checked':checked,'with_bpa':with_bpa,'errors':errors},indent=2)+'\n')
raise SystemExit(bool(errors))
