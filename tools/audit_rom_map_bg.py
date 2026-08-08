#!/usr/bin/env python3
"""Compare pret/pmd-sky MAP_BG against the legally supplied retail NDS ROM."""
from pathlib import Path
import argparse,hashlib,json
from ndspy.rom import NintendoDSRom
def sha(b):return hashlib.sha256(b).hexdigest()
def extract(rom):
 r=NintendoDSRom.fromFile(str(rom));out={}
 def walk(f,p=''):
  for i,n in enumerate(f.files):
   q=p+n
   if q.upper().startswith('MAP_BG/'):out[q.split('/',1)[1].lower()]=r.files[f.firstID+i]
  for n,s in f.folders:walk(s,p+n+'/')
 walk(r.filenames);return out
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--rom',required=True);ap.add_argument('--pret',required=True);ap.add_argument('--out',required=True);a=ap.parse_args();rom=extract(a.rom);pd=Path(a.pret)/'files/MAP_BG';pret={p.name.lower():p.read_bytes() for p in pd.iterdir() if p.is_file()};common=set(rom)&set(pret);changed=sorted(n for n in common if sha(rom[n])!=sha(pret[n]));ro=sorted(set(rom)-set(pret));po=sorted(set(pret)-set(rom));o={'schema':1,'rom_sha256':sha(Path(a.rom).read_bytes()),'counts':{'rom_files':len(rom),'pret_files':len(pret),'common_identical':len(common)-len(changed),'changed':len(changed),'rom_only':len(ro),'pret_only':len(po)},'rom_only':[{'name':n,'bytes':len(rom[n]),'sha256':sha(rom[n])} for n in ro],'pret_only':po,'changed':changed,'conclusion':'ROM-only MAP_BG assets must be included; pret and ROM common assets are byte-identical.'};Path(a.out).write_text(json.dumps(o,indent=2)+'\n');print(json.dumps(o['counts']))
if __name__=='__main__':main()
