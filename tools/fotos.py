# -*- coding: utf-8 -*-
"""Fotos do site a partir do Instagram (../_ref/ig): miniaturas 4:5 (assets/img/p), fotos grandes (assets/img/g),
blocos dos destaques e assets/js/dados.js.  Uso: python tools/fotos.py"""
import json
from pathlib import Path
from PIL import Image, ImageOps
S = Path(__file__).resolve().parent.parent
R = S.parent / '_ref/ig'

# id, post, fotos do carrossel, categoria, legenda PT, legenda EN, foco vertical da miniatura (0 topo .. 1 base)
PORT = [
    ('woody', '055', [0], 'pet', 'Woody', 'Woody', .5),
    ('poseidon', '001', [0], 'real', 'Poseidon', 'Poseidon', .45),
    ('escorpiao', '043', [0], 'real', 'Escorpião', 'Scorpion', .45),
    ('lobo-neo', '004', [0], 'neo', 'Lobo neotradicional', 'Neo-traditional wolf', .5),
    ('freya', '079', [0], 'pet', 'Freya', 'Freya', .5),
    ('leao', '046', [0, 1, 3], 'real', 'Leão · Yeshua', 'Lion · Yeshua', .5),
    ('caveira', '062', [0, 1, 3], 'neo', 'Caveira e rosas, 2.º lugar', 'Skull and roses, 2nd place', .5),
    ('torre', '041', [0, 1, 2], 'real', 'Torre Eiffel', 'Eiffel Tower', .5),
    ('husky', '181', [0, 1], 'pet', 'Husky', 'Husky', .5),
    ('magpie', '067', [0, 2, 3, 1], 'neo', 'Pega, cobertura', 'Magpie, cover-up', .4),
    ('templario', '054', [0, 1, 2], 'real', 'Cavaleiro templário', 'Templar knight', .5),
    ('arya', '024', [0], 'pet', 'Arya', 'Arya', .5),
    ('viagem', '027', [0], 'manga', 'Manga das viagens', 'Travel sleeve', .5),
    ('lilith', '073', [0], 'neo', 'Lilith, 3.º lugar', 'Lilith, 3rd place', .5),
    ('boston', '087', [1, 2, 3, 4, 5], 'pet', 'Retratos de animais', 'Pet portraits', .5),
    ('dali', '085', [0], 'real', 'A persistência da memória', 'The Persistence of Memory', .5),
    ('manga-neo', '003', [0], 'manga', 'Manga neotradicional cicatrizada', 'Healed neo-traditional sleeve', .3),
    ('lucas', '044', [0], 'pet', 'Lucas', 'Lucas', .5),
    ('lobo-magnolias', '086', [0], 'real', 'Lobo e magnólias', 'Wolf and magnolias', .5),
    ('onca', '072', [0, 1], 'cob', 'Onça, cobertura de cicatriz', 'Jaguar, scar cover-up', .5),
    ('cavalo', '034', [0, 1], 'real', 'Cavalo', 'Horse', .5),
    ('farrusca', '021', [0], 'pet', 'Farrusca', 'Farrusca', .5),
    ('corvo', '094', [0], 'real', 'Três mentes, um destino', 'Three minds, one fate', .5),
    ('manga-nalu', '025', [0, 1, 2, 3], 'manga', 'Manga freehand', 'Freehand sleeve', .4),
    ('tartaruga', '009', [0, 1, 4], 'cob', 'Tartaruga, cobertura', 'Turtle, cover-up', .5),
    ('peanut', '058', [0], 'pet', 'Peanut', 'Peanut', .5),
    ('pai', '052', [0], 'real', 'Homenagem ao pai', 'A tribute to his father', .5),
    ('raposa', '207', [0], 'neo', 'Raposa', 'Fox', .5),
    ('lucho', '051', [0], 'pet', 'Lucho', 'Lucho', .5),
    ('icaro', '065', [0], 'real', 'Ícaro', 'Icarus', .3),
    ('relogio', '029', [0], 'manga', 'Manga relógio e rosas', 'Clock and roses sleeve', .5),
    ('lobo-cob', '059', [0, 1], 'cob', 'Lobo, sobre tatuagem antiga', 'Wolf over an old tattoo', .5),
    ('leopardo', '206', [0], 'neo', 'Leopardo', 'Leopard', .5),
    ('tubarao', '110', [0], 'real', 'Tubarão', 'Shark', .5),
    ('ziggy', '060', [0], 'pet', 'Ziggy', 'Ziggy', .5),
    ('belmont', '063', [0], 'real', 'Belmont, costas', 'Belmont, back piece', .5),
    ('veado', '121', [0], 'neo', 'Veado', 'Deer', .5),
    ('cleopatra', '095', [0], 'manga', 'Manga egípcia', 'Egyptian sleeve', .4),
    ('pai-filha', '077', [0], 'real', 'Pai e filha', 'Father and daughter', .5),
    ('thor', '040', [0], 'pet', 'Thor, com a foto', 'Thor, with the photo', .5),
]

# blocos extra (miniatura 4:5 + grande)
EXTRA = [
    ('ref-zeus', 'posts/112_0'), ('ref-thor', 'posts/040_0'), ('ref-conceicao', 'posts/178_0'), ('ref-husky', 'posts/181_0'),
    ('stencil-pele', 'posts/062_3'), ('stencil-tablet', 'hl/feedback/04'), ('result-pele', 'posts/062_0'),
    ('cic-boston', 'hl/healed/00'), ('cic-crocodilo', 'hl/healed/05'), ('cic-manga', 'hl/healed/08'), ('cic-moeda', 'hl/healed/09'),
    ('cic-anubis', 'posts/088_0'), ('cic-skull', 'posts/093_0'), ('cic-neo', 'posts/003_0'), ('cic-pele', 'posts/089_0'),
    ('premio-lisboa', 'posts/064_0'), ('premio-porto', 'posts/074_0'), ('premio-lisboa-peca', 'posts/062_0'), ('premio-porto-peca', 'posts/073_0'),
    ('sobre', 'posts/087_0'), ('sobre-2', 'hl/process/06'),
    ('viagem-1', 'posts/027_0'), ('viagem-2', 'posts/031_0'), ('viagem-3', 'posts/039_0'), ('viagem-4', 'posts/041_0'), ('viagem-5', 'posts/012_1'),
    ('cob-tartaruga-antes', 'posts/009_1'), ('cob-tartaruga', 'posts/009_0'), ('cob-onca-antes', 'posts/072_1'), ('cob-onca', 'posts/072_0'),
    ('cob-lobo-antes', 'posts/059_1'), ('cob-lobo', 'posts/059_0'), ('cob-magpie-antes', 'posts/067_1'), ('cob-magpie', 'posts/067_0'),
    ('dep-coelho', 'hl/feedback/01'), ('dep-pai', 'hl/feedback/02'), ('dep-cao', 'hl/feedback/03'),
]
FOCO = {'sobre': .35, 'premio-lisboa': .35, 'premio-porto': .4, 'cic-manga': .5, 'stencil-tablet': .55, 'sobre-2': .45}

for d in ('p', 'g'): (S / f'assets/img/{d}').mkdir(parents=True, exist_ok=True)


def abre(f):
    return ImageOps.exif_transpose(Image.open(f)).convert('RGB')


def mini(im, fy=.5, W=720, H=900):
    w, h = im.size
    if w / h > W / H:
        nw = int(h * W / H); x = (w - nw) // 2; im = im.crop((x, 0, x + nw, h))
    else:
        nh = int(w * H / W); y = int((h - nh) * fy); im = im.crop((0, y, w, y + nh))
    return im.resize((W, H), Image.LANCZOS)


def grande(im, M=1400):
    im = im.copy(); im.thumbnail((M, M), Image.LANCZOS); return im


dados = []
for pid, post, idx, cat, pt, en, fy in PORT:
    fs = [R / f'posts/{post}_{k}.jpg' for k in idx]
    mini(abre(fs[0]), fy).save(S / f'assets/img/p/{pid}.webp', quality=82, method=6)
    gr = []
    for k, f in enumerate(fs):
        im = grande(abre(f)); n = f'{pid}-{k}'
        im.save(S / f'assets/img/g/{n}.webp', quality=84, method=6)
        gr.append([n, im.width, im.height])
    dados.append(dict(id=pid, cat=cat, pt=pt, en=en, g=gr))

for n, f in EXTRA:
    im = abre(R / f'{f}.jpg')
    mini(im, FOCO.get(n, .5)).save(S / f'assets/img/p/{n}.webp', quality=82, method=6)
    grande(im).save(S / f'assets/img/g/{n}.webp', quality=84, method=6)

(S / 'assets/js/dados.js').write_text('window.PORT=' + json.dumps(dados, ensure_ascii=False, separators=(',', ':')) + ';\n', encoding='utf8')
tot = sum(f.stat().st_size for f in (S / 'assets/img').rglob('*.webp'))
print(len(dados), 'pecas', len(EXTRA), 'extra', round(tot / 1e6, 1), 'MB')
