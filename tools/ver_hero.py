# -*- coding: utf-8 -*-
"""Prova do hero: quadros em tempos fixos lado a lado (_ref/estudo/quadros.jpg). Uso: python tools/ver_hero.py [peca]"""
import base64, io, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
S = Path(__file__).resolve().parent.parent
NOMES = ['cao', 'escorpiao', 'leao']
P = int(sys.argv[1]) if len(sys.argv) > 1 else 0
TS = [0.35, 0.7, 1.1, 2.2, 3.4, 4.6, 5.2, 6.0, 8.2, 8.6]
b64 = lambda f: 'data:image/webp;base64,' + base64.b64encode((S / f).read_bytes()).decode()

with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge', args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
    g = b.new_page(viewport={'width': 400, 'height': 400})
    g.set_content('<body style="margin:0"><canvas id=c></canvas></body>')
    g.add_script_tag(content=(S / 'assets/js/stencil.js').read_text(encoding='utf8'))
    g.evaluate("""async(a)=>{window.H=stencilHero(document.getElementById('c'),{guardar:true});
      for(let i=0;i<a.length;i++){const m=new Image();m.src=a[i];await m.decode();H.textura(i,m)}}""", [b64(f'assets/hero/{n}.webp') for n in NOMES])
    out = []
    for t in TS:
        d = g.evaluate(f"(H.desenha({P * 9.0 + t},520,1),document.getElementById('c').toDataURL('image/jpeg',.9))")
        out.append(Image.open(io.BytesIO(base64.b64decode(d.split(',', 1)[1]))))
    W = sum(i.width for i in out)
    o = Image.new('RGB', (out[0].width * 5, out[0].height * 2))
    for k, i in enumerate(out): o.paste(i, ((k % 5) * i.width, (k // 5) * i.height))
    o.save(S.parent / '_ref/estudo/quadros.jpg', quality=85)
    b.close()
print('ok')
