# -*- coding: utf-8 -*-
"""Hero "do stencil a pele": tira a tinta real de 3 tatuagens do Christian e gera, para cada uma,
uma faixa em tons de cinza com 3 quadros lado a lado (N x N cada):
  0 = tinta (0 pele, 255 preto)  1 = linhas do stencil  2 = ordem de chegada do whip shading (0 primeiro).
Saida: assets/hero/<nome>.webp e provas em _ref/estudo.  Uso: python tools/hero.py"""
import cv2, numpy as np
from pathlib import Path
S = Path(__file__).resolve().parent.parent
R = S.parent / '_ref'
N = 1024
PECAS = [  # nome, arquivo, caixa (x0, y0, x1, y1) na foto original, angulo
    ('cao', '055_0', (420, 1150, 1700, 2520), []),
    ('escorpiao', '043_0', (300, 860, 1640, 2440), [[(880, 500), (1024, 500), (1024, 1024), (620, 1024)]]),
    ('leao', '046_0', (250, 0, 1180, 1150), [[(0, 560), (212, 560), (212, 1024), (0, 1024)]]),
]
rng = np.random.default_rng(7)


def tinta(im):
    lab = cv2.cvtColor(im, cv2.COLOR_BGR2LAB).astype(np.float32)
    L = cv2.bilateralFilter(lab[..., 0], 9, 10, 6)
    L = cv2.GaussianBlur(L, (0, 0), 1.1)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (91, 91))
    fundo = cv2.GaussianBlur(cv2.morphologyEx(L, cv2.MORPH_CLOSE, k), (0, 0), 40)
    r = L / np.maximum(fundo, 1)
    t = np.clip((.965 - r) / .80, 0, 1)
    return t


def regiao(t):
    forte = (t > .30).astype(np.uint8)
    forte = cv2.morphologyEx(forte, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25)))
    n, l, s, _ = cv2.connectedComponentsWithStats(forte, connectivity=8)
    reg = np.zeros_like(forte)
    big = s[1:, cv2.CC_STAT_AREA].max()
    for i in range(1, n):
        if s[i, cv2.CC_STAT_AREA] > big * .015: reg[l == i] = 1
    reg = cv2.morphologyEx(reg, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (61, 61)))
    reg = cv2.dilate(reg, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31)))
    return cv2.GaussianBlur(reg.astype(np.float32), (0, 0), 9)


def quadrado(a, fill=0.):
    h, w = a.shape[:2]; m = max(h, w)
    o = np.full((m, m), fill, np.float32)
    o[(m - h) // 2:(m - h) // 2 + h, (m - w) // 2:(m - w) // 2 + w] = a
    return cv2.resize(o, (N, N), interpolation=cv2.INTER_AREA)


def stencil_velho(t):
    """linhas de contorno como um stencil termico: XDoG sobre a tinta suavizada, so as bordas fortes."""
    b = cv2.GaussianBlur(t, (0, 0), 2.2)
    g1 = cv2.GaussianBlur(b, (0, 0), 1.2); g2 = cv2.GaussianBlur(b, (0, 0), 1.2 * 1.7)
    d = g1 - .985 * g2
    e = np.clip(d * 26, 0, 1)
    gx = cv2.Sobel(b, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(b, cv2.CV_32F, 0, 1, ksize=3)
    mag = np.sqrt(gx * gx + gy * gy)
    e = np.maximum(e, np.clip((mag - .10) * 5, 0, 1) * .9)
    e = cv2.GaussianBlur(e, (0, 0), .7)
    e = np.where(e < .22, 0, e)
    return np.clip(e * 1.25, 0, 1)


def stencil(t):
    """linhas finas de contorno, como o stencil termico: Canny sobre a tinta bem suavizada."""
    b = cv2.GaussianBlur((t * 255).astype(np.uint8), (0, 0), 3.2)
    e = cv2.Canny(b, 28, 70, L2gradient=True).astype(np.float32) / 255
    # tira tracinhos soltos
    n, l, st, _ = cv2.connectedComponentsWithStats((e > 0).astype(np.uint8), connectivity=8)
    ok = np.zeros(n, bool); ok[1:] = st[1:, cv2.CC_STAT_AREA] > 26
    e *= ok[l]
    e = cv2.dilate(e, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
    return np.clip(cv2.GaussianBlur(e, (0, 0), .9) * 1.15, 0, 1)


def lic(t):
    """ruido arrastado ao longo do fluxo do desenho (tensor de estrutura): o rastro do whip shading."""
    b = cv2.GaussianBlur(t, (0, 0), 5)
    gx = cv2.Sobel(b, cv2.CV_32F, 1, 0, ksize=5); gy = cv2.Sobel(b, cv2.CV_32F, 0, 1, ksize=5)
    J11 = cv2.GaussianBlur(gx * gx, (0, 0), 14); J22 = cv2.GaussianBlur(gy * gy, (0, 0), 14); J12 = cv2.GaussianBlur(gx * gy, (0, 0), 14)
    ang = .5 * np.arctan2(2 * J12, J11 - J22) + np.pi / 2   # tangente
    tx, ty = np.cos(ang), np.sin(ang)
    small = N // 2
    ruido = rng.random((small, small)).astype(np.float32)
    ruido = cv2.resize(ruido, (N, N), interpolation=cv2.INTER_NEAREST)
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
    acc = ruido.copy(); px, py = xx.copy(), yy.copy(); qx, qy = xx.copy(), yy.copy()
    for _ in range(16):
        ix = np.clip(px, 0, N - 1).astype(int); iy = np.clip(py, 0, N - 1).astype(int)
        px += tx[iy, ix] * 1.6; py += ty[iy, ix] * 1.6
        acc += cv2.remap(ruido, px, py, cv2.INTER_LINEAR)
        jx = np.clip(qx, 0, N - 1).astype(int); jy = np.clip(qy, 0, N - 1).astype(int)
        qx -= tx[jy, jx] * 1.6; qy -= ty[jy, jx] * 1.6
        acc += cv2.remap(ruido, qx, qy, cv2.INTER_LINEAR)
    acc /= 33
    acc = (acc - acc.mean()) / (acc.std() + 1e-6)
    return acc


def fbm(seed):
    r = np.random.default_rng(seed); o = np.zeros((N, N), np.float32); a = 1.
    for f in (4, 8, 16, 32):
        n = cv2.resize(r.random((f, f)).astype(np.float32), (N, N), interpolation=cv2.INTER_CUBIC)
        o += a * n; a *= .5
    return (o - o.mean()) / o.std()


for i, (nome, arq, (x0, y0, x1, y1), apaga) in enumerate(PECAS):
    im = cv2.imread(str(R / f'ig/posts/{arq}.jpg'))
    t = tinta(im)
    t = t[y0:y1, x0:x1]
    reg = regiao(t)
    t = t * reg
    # limpa poros e pele: ponto fraco solto some
    t = np.where(t < .07, 0, (t - .07) / .93)
    p = (t > .03).astype(np.uint8)
    n, l, s, _ = cv2.connectedComponentsWithStats(p, connectivity=8)
    ok = np.zeros(n, bool); ok[1:] = s[1:, cv2.CC_STAT_AREA] > 160
    t *= cv2.GaussianBlur(ok[l].astype(np.float32), (0, 0), .8)
    t = np.clip(t ** 1.12, 0, 1)
    # bordas da caixa: some suave
    h, w = t.shape
    yy, xx = np.mgrid[0:h, 0:w]
    m = np.minimum.reduce([xx, w - 1 - xx, yy, h - 1 - yy]).astype(np.float32)
    t *= np.clip(m / 40, 0, 1)
    T = quadrado(t)
    ys, xs = np.where(T > .2)
    # recentra pelo centro de massa da caixa
    cx, cy = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
    esc = .86 * N / max(xs.max() - xs.min(), ys.max() - ys.min())
    M = np.float32([[esc, 0, N / 2 - cx * esc], [0, esc, N / 2 - cy * esc]])
    T = cv2.warpAffine(T, M, (N, N), flags=cv2.INTER_CUBIC, borderValue=0)
    T = np.clip(T, 0, 1)
    if apaga:
        mk = np.ones((N, N), np.uint8)
        for pg in apaga: cv2.fillPoly(mk, [np.int32(pg)], 0)
        T *= cv2.GaussianBlur(mk.astype(np.float32), (0, 0), 6)
    T = cv2.GaussianBlur(T, (0, 0), .6)
    ST = stencil(T)
    L = lic(T)
    # chegada: varredura de cima para baixo com borda organica + escuros primeiro + rastro do whip
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32) / N
    var = yy * .55 + fbm(10 + i) * .07 + xx * .08
    var = (var - var.min()) / (var.max() - var.min())
    chega = var * .62 + (1 - T) * .22 + L * .045
    chega = (chega - np.percentile(chega, 1)) / (np.percentile(chega, 99.5) - np.percentile(chega, 1))
    chega = np.clip(chega, 0, 1)
    faixa = np.concatenate([T, ST, chega], axis=1)
    cv2.imwrite(str(S / f'assets/hero/{nome}.webp'), (faixa * 255).astype(np.uint8), [cv2.IMWRITE_WEBP_QUALITY, 90])
    # prova
    papel = np.array([228, 233, 236], np.float32); carvao = np.array([20, 19, 18], np.float32); roxo = np.array([196, 70, 86], np.float32)
    a = papel * (1 - T[..., None]) + carvao * T[..., None]
    b = papel * (1 - ST[..., None] * .85) + roxo * ST[..., None] * .85
    c = np.repeat((chega * 255)[..., None], 3, 2)
    cv2.imwrite(str(R / f'estudo/{nome}.jpg'), np.concatenate([a, b, c], 1).astype(np.uint8)[::2, ::2], [cv2.IMWRITE_JPEG_QUALITY, 85])
    print(nome, 'ok', round((S / f'assets/hero/{nome}.webp').stat().st_size / 1024), 'KB')
