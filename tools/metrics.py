"""Measure the window chrome (everything outside the canvas) in VectorCraft screenshots.

chromatic share: % of chrome pixels whose CIELAB chroma C*ab > 15 (visibly coloured, not grey).
edge density:    % of chrome pixels on an edge (Sobel magnitude on L* > 8 per pixel), the
                 Edge Density clutter proxy (Mack & Oliva 2004) as used by later clutter studies.
Usage: metrics.py SHOT.png x0 y0 x1 y1 (canvas rect x y w h in window points; the PNG may be 2x).
"""
import json, sys
import numpy as np
from PIL import Image


def srgb_to_lab(rgb):
    c = rgb / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    m = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = np.stack([(c[..., 0] * m[i, 0] + c[..., 1] * m[i, 1] + c[..., 2] * m[i, 2]) / wp for i, wp in enumerate([0.95047, 1.0, 1.08883])], -1)
    f = np.where(xyz > 216 / 24389, np.cbrt(xyz), (24389 / 27 * xyz + 16) / 116)
    L = 116 * f[..., 1] - 16
    a = 500 * (f[..., 0] - f[..., 1])
    b = 200 * (f[..., 1] - f[..., 2])
    return L, a, b


def measure(path, rect):
    img = np.asarray(Image.open(path).convert("RGB")).astype(np.float64)
    h, w, _ = img.shape
    scale = w / 1440.0
    x0, y0, x1, y1 = [int(round(v * scale)) for v in (rect[0], rect[1], rect[0] + rect[2], rect[1] + rect[3])]
    chrome = np.ones((h, w), bool)
    chrome[y0:y1, x0:x1] = False
    L, a, b = srgb_to_lab(img)
    chroma = np.hypot(a, b)
    coloured = (chroma > 15) & chrome
    gx = np.zeros_like(L); gy = np.zeros_like(L)
    gx[1:-1, 1:-1] = (L[:-2, 2:] + 2 * L[1:-1, 2:] + L[2:, 2:]) - (L[:-2, :-2] + 2 * L[1:-1, :-2] + L[2:, :-2])
    gy[1:-1, 1:-1] = (L[2:, :-2] + 2 * L[2:, 1:-1] + L[2:, 2:]) - (L[:-2, :-2] + 2 * L[:-2, 1:-1] + L[:-2, 2:])
    edges = (np.hypot(gx, gy) / 8 > 8) & chrome
    n = chrome.sum()
    return {"chromatic_pct": round(100 * coloured.sum() / n, 2), "edge_density_pct": round(100 * edges.sum() / n, 2),
            "chrome_pixels": int(n)}


if __name__ == "__main__":
    print(json.dumps(measure(sys.argv[1], [float(v) for v in sys.argv[2:6]])))
