# -*- coding: utf-8 -*-
"""Hero "do stencil a pele": tira a tinta real de 3 tatuagens do Christian e gera, para cada uma,
uma faixa em tons de cinza com 4 quadros lado a lado (N x N cada):
  0 = tinta (0 pele, 255 preto, com os meios-tons do realismo)
  1 = linhas do stencil   2 = sangrado do stencil (halo roxo)   3 = ordem de chegada do whip shading (0 primeiro)
Saida: assets/hero/<nome>.webp e provas em _ref/estudo.  Uso: python tools/hero.py"""
import cv2, numpy as np
from pathlib import Path
S = Path(__file__).resolve().parent.parent
R = S.parent / '_ref'
N = 1024
PECAS = [  # nome, arquivo, caixa (x0, y0, x1, y1) na foto original, poligonos a apagar (coordenadas finais N x N)
    ('cao', '055_0', (420, 1150, 1700, 2520), []),
    ('escorpiao', '043_0', (300, 860, 1640, 2440), [[(870, 470), (1024, 470), (1024, 1024), (600, 1024)]]),
    ('leao', '046_0', (250, 0, 1180, 1150), [[(0, 540), (215, 540), (215, 1024), (0, 1024)]]),
]
rng = np.random.default_rng(7)


def tinta(im):
    """densidade de tinta com meios-tons: L limpo de poros dividido pelo tom local da pele."""
    lab = cv2.cvtColor(im, cv2.COLOR_BGR2LAB)
    L8 = cv2.fastNlMeansDenoising(lab[..., 0], None, h=7, templateWindowSize=7, searchWindowSize=21)
    L = L8.astype(np.float32)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (101, 101))
    fundo = cv2.GaussianBlur(cv2.morphologyEx(L, cv2.MORPH_CLOSE, k), (0, 0), 45)
    return L / np.maximum(fundo, 1)


def regiao(t):
    forte = (t > .28).astype(np.uint8)
    forte = cv2.morphologyEx(forte, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31)))
    n, l, s, _ = cv2.connectedComponentsWithStats(forte, connectivity=8)
    reg = np.zeros_like(forte)
    big = s[1:, cv2.CC_STAT_AREA].max()
    for i in range(1, n):
        if s[i, cv2.CC_STAT_AREA] > big * .02: reg[l == i] = 1
    reg = cv2.morphologyEx(reg, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (81, 81)))
    reg = cv2.dilate(reg, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41)))
    return cv2.GaussianBlur(reg.astype(np.float32), (0, 0), 14)


def quadrado(a):
    h, w = a.shape[:2]; m = max(h, w)
    o = np.zeros((m, m), np.float32)
    o[(m - h) // 2:(m - h) // 2 + h, (m - w) // 2:(m - w) // 2 + w] = a
    return cv2.resize(o, (N, N), interpolation=cv2.INTER_AREA)


def stencil(t):
    """linhas finas como o stencil termico: Canny sobre a tinta suavizada, sem tracinhos soltos."""
    b = cv2.GaussianBlur((t * 255).astype(np.uint8), (0, 0), 3.4)
    e = cv2.Canny(b, 26, 66, L2gradient=True).astype(np.float32) / 255
    n, l, st, _ = cv2.connectedComponentsWithStats((e > 0).astype(np.uint8), connectivity=8)
    ok = np.zeros(n, bool); ok[1:] = st[1:, cv2.CC_STAT_AREA] > 34
    e *= ok[l]
    e = cv2.GaussianBlur(e, (0, 0), .75) * 1.9
    return np.clip(e, 0, 1)


def lic(t):
    """ruido arrastado ao longo do fluxo do desenho: o rastro do whip shading."""
    b = cv2.GaussianBlur(t, (0, 0), 5)
    gx = cv2.Sobel(b, cv2.CV_32F, 1, 0, ksize=5); gy = cv2.Sobel(b, cv2.CV_32F, 0, 1, ksize=5)
    J11 = cv2.GaussianBlur(gx * gx, (0, 0), 14); J22 = cv2.GaussianBlur(gy * gy, (0, 0), 14); J12 = cv2.GaussianBlur(gx * gy, (0, 0), 14)
    ang = .5 * np.arctan2(2 * J12, J11 - J22) + np.pi / 2
    tx, ty = np.cos(ang), np.sin(ang)
    ruido = cv2.resize(rng.random((N // 2, N // 2)).astype(np.float32), (N, N), interpolation=cv2.INTER_NEAREST)
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
    acc = ruido.copy(); px, py = xx.copy(), yy.copy(); qx, qy = xx.copy(), yy.copy()
    for _ in range(18):
        ix = np.clip(px, 0, N - 1).astype(int); iy = np.clip(py, 0, N - 1).astype(int)
        px += tx[iy, ix] * 1.7; py += ty[iy, ix] * 1.7
        acc += cv2.remap(ruido, px, py, cv2.INTER_LINEAR)
        jx = np.clip(qx, 0, N - 1).astype(int); jy = np.clip(qy, 0, N - 1).astype(int)
        qx -= tx[jy, jx] * 1.7; qy -= ty[jy, jx] * 1.7
        acc += cv2.remap(ruido, qx, qy, cv2.INTER_LINEAR)
    acc /= 37
    return (acc - acc.mean()) / (acc.std() + 1e-6)


def fbm(seed):
    r = np.random.default_rng(seed); o = np.zeros((N, N), np.float32); a = 1.
    for f in (3, 6, 12, 24):
        o += a * cv2.resize(r.random((f, f)).astype(np.float32), (N, N), interpolation=cv2.INTER_CUBIC); a *= .5
    return (o - o.mean()) / o.std()


for i, (nome, arq, (x0, y0, x1, y1), apaga) in enumerate(PECAS):
    im = cv2.imread(str(R / f'ig/posts/{arq}.jpg'))
    r = tinta(im)[y0:y1, x0:x1]
    # escala de tom pela propria peca: o preto mais fundo = 1, a pele = 0
    bruto = np.clip((.97 - r) / .8, 0, 1)
    reg = regiao(bruto)
    dentro = r[reg > .5]
    preto, pele = np.percentile(dentro, .4), np.percentile(r[reg < .05], 50) if (reg < .05).any() else 1.
    t = np.clip((pele * .975 - r) / (pele * .975 - preto), 0, 1)
    t = t ** .92
    t *= reg
    # piso suave: tira so o veu da pele, sem matar os pontilhados claros
    t = np.clip((t - .035) / .965, 0, 1)
    h, w = t.shape
    yy, xx = np.mgrid[0:h, 0:w]
    m = np.minimum.reduce([xx, w - 1 - xx, yy, h - 1 - yy]).astype(np.float32)
    t *= np.clip(m / 50, 0, 1)
    T = quadrado(t)
    ys, xs = np.where(T > .18)
    cx, cy = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
    esc = .88 * N / max(xs.max() - xs.min(), ys.max() - ys.min())
    M = np.float32([[esc, 0, N / 2 - cx * esc], [0, esc, N / 2 - cy * esc]])
    T = np.clip(cv2.warpAffine(T, M, (N, N), flags=cv2.INTER_LANCZOS4, borderValue=0), 0, 1)
    if apaga:
        mk = np.ones((N, N), np.uint8)
        for pg in apaga: cv2.fillPoly(mk, [np.int32(pg)], 0)
        T *= cv2.GaussianBlur(mk.astype(np.float32), (0, 0), 8)
    ST = stencil(T)
    HALO = np.clip(cv2.GaussianBlur(ST, (0, 0), 3.2) * 2.2, 0, 1)
    L = lic(T)
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32) / N
    # chegada: a sombra avanca na diagonal do braco, com borda organica, escuros antes e o rastro do whip
    var = yy * .74 + xx * .26 + fbm(10 + i) * .06
    var = (var - var.min()) / (var.max() - var.min())
    chega = var * .64 + (1 - T) * .24 + L * .04
    chega = (chega - np.percentile(chega, 1)) / (np.percentile(chega, 99.5) - np.percentile(chega, 1))
    chega = np.clip(chega, 0, 1)
    faixa = np.concatenate([T, ST, HALO, chega], axis=1)
    cv2.imwrite(str(S / f'assets/hero/{nome}.webp'), (faixa * 255 + .5).astype(np.uint8), [cv2.IMWRITE_WEBP_QUALITY, 94])
    papel = np.array([227, 233, 236], np.float32); carvao = np.array([18, 17, 18], np.float32); roxo = np.array([199, 56, 77], np.float32)
    a = papel * (1 - T[..., None]) + carvao * T[..., None]
    b = papel * (1 - ST[..., None] * .9) + roxo * ST[..., None] * .9
    o = np.concatenate([a, b], 1)
    orig = cv2.resize(im[y0:y1, x0:x1], (int((x1 - x0) * N / (y1 - y0)), N))
    o = np.concatenate([orig.astype(np.float32), o], 1)
    cv2.imwrite(str(R / f'estudo/{nome}.jpg'), o.astype(np.uint8)[::2, ::2], [cv2.IMWRITE_JPEG_QUALITY, 88])
    print(nome, round((S / f'assets/hero/{nome}.webp').stat().st_size / 1024), 'KB', 'preto', round(float(preto), 3), 'pele', round(float(pele), 3))
