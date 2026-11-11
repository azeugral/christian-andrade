# -*- coding: utf-8 -*-
"""Grava o hero em MP4 (celular / modo economia) e o poster, ambos sobre BRANCO (o site aplica multiply).
Saidas: assets/video/hero.mp4 (1080x1080, 3 pecas x 9 s, 30 fps, loop), assets/img/hero-poster.webp e assets/img/capa.jpg.
Uso: python tools/gerar_video.py"""
import base64, io, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image, ImageChops
S = Path(__file__).resolve().parent.parent
NOMES = ['cao', 'escorpiao', 'leao']
LADO, FPS, PECA = 1080, 30, 9.0
b64 = lambda f: 'data:image/webp;base64,' + base64.b64encode((S / f).read_bytes()).decode()
(S / 'assets/video').mkdir(exist_ok=True)

with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge', args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
    g = b.new_page(viewport={'width': 400, 'height': 400})
    g.set_content('<body style="margin:0"><canvas id=c></canvas></body>')
    g.add_script_tag(content=(S / 'assets/js/stencil.js').read_text(encoding='utf8'))
    g.evaluate("""async(a)=>{window.H=stencilHero(document.getElementById('c'),{guardar:true});
      for(let i=0;i<a.length;i++){const m=new Image();m.src=a[i];await m.decode();H.textura(i,m)}}""", [b64(f'assets/hero/{n}.webp') for n in NOMES])
    quadro = lambda t, q: Image.open(io.BytesIO(base64.b64decode(g.evaluate(
        f"(H.desenha({t},{LADO},1),document.getElementById('c').toDataURL('image/jpeg',{q}))").split(',', 1)[1]))).convert('RGB')

    pst = quadro(6.6, .97)
    pst.save(S / 'assets/img/hero-poster.webp', quality=90, method=6)
    # capa 1200x630: poster multiplicado pelo papel, centrado
    capa = Image.new('RGB', (1200, 630), (236, 233, 227))
    m = pst.resize((600, 600), Image.LANCZOS)
    capa.paste(ImageChops.multiply(m, Image.new('RGB', m.size, (236, 233, 227))), (300, 15))
    capa.save(S / 'assets/img/capa.jpg', quality=88)

    n = int(PECA * len(NOMES) * FPS)
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', str(FPS), '-c:v', 'mjpeg', '-i', '-',
                           '-c:v', 'libx264', '-preset', 'slow', '-crf', '27', '-pix_fmt', 'yuv420p', '-color_range', 'tv',
                           '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-g', str(FPS * 3),
                           '-movflags', '+faststart', '-an', str(S / 'assets/video/hero.mp4')], stdin=subprocess.PIPE)
    for k in range(n):
        d = g.evaluate(f"(H.desenha({k / FPS},{LADO},1),document.getElementById('c').toDataURL('image/jpeg',.95))")
        ff.stdin.write(base64.b64decode(d.split(',', 1)[1]))
        if k % 90 == 0: print(k, '/', n, flush=True)
    ff.stdin.close(); ff.wait()
    b.close()
print('mp4', round((S / 'assets/video/hero.mp4').stat().st_size / 1e6, 2), 'MB')
