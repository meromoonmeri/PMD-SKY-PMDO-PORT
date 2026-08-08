#!/usr/bin/env python3
from pathlib import Path
import argparse,io,json,struct
from PIL import Image
def pkg(p):
 b=p.read_bytes();_,n=struct.unpack_from('<II',b);o={}
 for i in range(n):
  k,z=struct.unpack_from('<QQ',b,8+i*16);ln=struct.unpack_from('<Q',b,z)[0];o[k&0xffffffff,k>>32]=Image.open(io.BytesIO(b[z+8:z+8+ln])).convert('RGBA')
 return o
def main():
 ap=argparse.ArgumentParser();ap.add_argument('ids',nargs='*');a=ap.parse_args();root=Path(__file__).resolve().parents[1];gd=root/'output/Grounds';td=root/'output/Tiles';out=root/'output/Previews';out.mkdir(parents=True,exist_ok=True);ids=a.ids or [p.stem for p in gd.glob('*.rsground')]
 for n in ids:
  o=json.load(open(gd/(n+'.rsground'),encoding='utf-8-sig'))['Object'];L=o['Layers'][0]['Tiles'];W,H=len(L),len(L[0]);sheets={f['Sheet'] for col in L for c in col for l in c.get('Layers',[]) for f in l.get('Frames',[]) if f.get('Sheet')};ps={s:pkg(td/(s+'.tile')) for s in sheets};im=Image.new('RGBA',(W*8,H*8),(0,0,0,255))
  for x,col in enumerate(L):
   for y,c in enumerate(col):
    for l in c.get('Layers',[]):
     fs=l.get('Frames',[])
     if fs and fs[0].get('Sheet'):
      f=fs[0];q=ps[f['Sheet']][f['TexLoc']['X'],f['TexLoc']['Y']];im.alpha_composite(q,(x*8,y*8))
  im.convert('RGB').save(out/(n+'.png'));print('OK',n,im.size)
if __name__=='__main__':main()
