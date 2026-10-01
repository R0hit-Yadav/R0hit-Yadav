#!/usr/bin/env python3
"""
Generate the theme-aware animated profile banner (dark.svg / light.svg).

Left  : VISUAL.MAP — a particle field that morphs
        portrait -> Bitcoin -> Ethereum -> Solana -> portrait.
        Each hold shows a crisp dithered frame; transitions are a single
        <path> per particle group whose `d` is SMIL-interpolated, so ~2k
        particles cost a few hundred KB and animate smoothly everywhere
        GitHub renders SVG (camo serves it as <img>; SMIL still runs).
Right : SYSTEM.INFO terminal panel.

Run:  python3 scripts/generate_banner.py
Deps: pillow numpy scipy (rembg optional, for portrait background removal)
"""
from __future__ import annotations

import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps
from scipy import ndimage
from scipy.optimize import linear_sum_assignment

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT
ASSETS = ROOT / "assets"
PHOTO = ASSETS / "rohit_professional.png"
BTC_IMG = ASSETS / "morph" / "Bitoin-new.png"
ETH_IMG = ASSETS / "morph" / "ETH.png"
DEBUG = ROOT / "scripts" / "debug"

# ---------------------------------------------------------------- geometry
# Frame (VISUAL.MAP) in banner px
FRAME_X, FRAME_Y, PANEL_W, PANEL_H = 36, 84, 400, 492
# Dither grid — uniform scale (no more squashed portrait / oval Bitcoin)
GRID_W, GRID_H = 250, 307
CELL = 1.6  # px per grid cell -> 400 x 491
MAP_TX = FRAME_X
MAP_TY = FRAME_Y + (PANEL_H - GRID_H * CELL) / 2

# Particles live on a half-grid (unit = 0.8px) so the dot "h3v3h-3z" is
# 2.4px while every coordinate stays an integer (small SVG).
PSUB = 2
PSIZE = 3
N_PARTICLES = 2200
N_GROUPS = 8          # stagger groups (one <path> each)
MAX_STAGGER = 0.38    # s, spread of group departures

# ---------------------------------------------------------------- timing
INTRO = 2.6           # particles stream in and settle on the portrait
TRAVEL = 1.9          # one morph (incl. stagger)
HOLDS = [3.8, 2.8, 2.8, 2.8]   # portrait, btc, eth, sol
FADE = 0.35

RNG = random.Random(7)
NP_RNG = np.random.default_rng(7)

PROFILE = {
    "title": "rohit@mainnet: ~ % ./profile.sh --live",
    "pill": "R0hit-Yadav @ mainnet",
    "email": "rohitkyadav2312@gmail.com",
    "identity": [
        ("Subject", "Rohit Yadav"),
        ("Role", "Rust Blockchain Developer"),
        ("Origin", "Ahmedabad, India"),
        ("Education", "B.E. Computer Engineering"),
        ("Status", "Building + Shipping On-Chain"),
        ("ToolChain", "VS Code, Cargo, Git, Anchor"),
    ],
    "stack": [
        ("Core.Lang", "Rust, Move, Solidity, TS"),
        ("Core.Frontend", "React, TypeScript"),
        ("Core.Backend", "Rust, Anchor, Node.js"),
        ("Core.Chains", "Solana, Aptos, EVM, Soroban"),
        ("Core.Infra", "Docker, AWS, Foundry, Git"),
    ],
    "contact": [
        ("Grid.Mail", "rohitkyadav2312@gmail.com"),
        ("Grid.LinkedIn", "rohit-yadav-611618260"),
        ("Grid.GitHub", "@R0hit-Yadav"),
        ("Grid.X", "@RohitYadav2312"),
        ("Grid.Instagram", "@rohit_k_yadav._"),
    ],
}

THEMES = {
    "dark": {
        "bg": "#070B16", "panel": "#0A101F", "panel2": "#0C1426", "bar": "#0B1222",
        "chrome": "#22D3EE", "accent": "#10B981", "violet2": "#7C3AED",
        "pill": "#4C1D95", "pill_text": "#E9D5FF", "live": "#F87171",
        "text": "#F8FAFC", "muted": "#94A3B8", "dim": "#475569",
        "dots": "rgba(148,163,184,0.35)", "hairline": "rgba(255,255,255,0.10)",
        "frame_stroke": "rgba(34,211,238,0.35)", "gridline": "rgba(148,163,184,0.10)",
        "scan": "#22D3EE",
        # per-shape ink: portrait, bitcoin, ethereum, solana (particle tint)
        "shape": ["#A78BFA", "#F7931A", "#8EA2FF", "#5EEAD4"],
        "sol_grad": ("#9945FF", "#14F195"),
        "invert_portrait": False,
    },
    "light": {
        "bg": "#E2E8F0", "panel": "#FFFFFF", "panel2": "#F8FAFC", "bar": "#F1F5F9",
        "chrome": "#0891B2", "accent": "#059669", "violet2": "#7C3AED",
        "pill": "#5B21B6", "pill_text": "#EDE9FE", "live": "#DC2626",
        "text": "#0F172A", "muted": "#475569", "dim": "#94A3B8",
        "dots": "rgba(100,116,139,0.40)", "hairline": "rgba(0,0,0,0.08)",
        "frame_stroke": "rgba(8,145,178,0.40)", "gridline": "rgba(100,116,139,0.12)",
        "scan": "#0891B2",
        "shape": ["#6D28D9", "#D97706", "#4F46E5", "#0D9488"],
        "sol_grad": ("#7C3AED", "#059669"),
        "invert_portrait": True,
    },
}

SHAPE_LABELS = ["subject.rohit", "chain.bitcoin", "chain.ethereum", "chain.solana"]


# ================================================================ portrait
def remove_background(img: Image.Image) -> tuple[Image.Image, np.ndarray]:
    """Return RGB image + boolean subject mask."""
    try:
        from rembg import remove

        arr = np.array(remove(img.convert("RGBA")))
        return Image.fromarray(arr[:, :, :3], "RGB"), arr[:, :, 3] > 128
    except Exception as e:  # noqa: BLE001
        print(f"[warn] rembg failed ({e}); using heuristic mask")
        return heuristic_mask(img)


def heuristic_mask(img: Image.Image) -> tuple[Image.Image, np.ndarray]:
    """Fallback: keep the central subject, drop dark studio background."""
    rgb = img.convert("RGB")
    arr = np.asarray(rgb).astype(np.float32)
    h, w, _ = arr.shape
    yy, xx = np.mgrid[0:h, 0:w]
    lum = arr.mean(axis=2)
    dist = np.sqrt(((xx - w * 0.5) / (w * 0.42)) ** 2 + ((yy - h * 0.5) / (h * 0.55)) ** 2)
    mask = (lum > 28) & (dist < 1.1)
    mask = ndimage.binary_closing(mask, iterations=4)
    mask = ndimage.binary_fill_holes(mask)
    labeled, n = ndimage.label(mask)
    if n:
        sizes = ndimage.sum(mask, labeled, range(1, n + 1))
        mask = labeled == (np.argmax(sizes) + 1)
    return rgb, mask


def fit_subject(img: Image.Image, mask: np.ndarray) -> tuple[Image.Image, np.ndarray]:
    """Scale the subject onto the grid: centred, shoulders flush with the bottom."""
    ys, xs = np.where(mask)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    sub = img.crop((x0, y0, x1, y1))
    smask = Image.fromarray(mask[y0:y1, x0:x1].astype(np.uint8) * 255)
    sw, sh = sub.size
    scale = min(GRID_W * 0.94 / sw, GRID_H * 0.93 / sh)
    nw, nh = int(sw * scale), int(sh * scale)
    sub = sub.resize((nw, nh), Image.Resampling.LANCZOS)
    smask = smask.resize((nw, nh), Image.Resampling.BILINEAR)
    canvas = Image.new("RGB", (GRID_W, GRID_H))
    m = np.zeros((GRID_H, GRID_W), dtype=bool)
    ox, oy = (GRID_W - nw) // 2, GRID_H - nh
    canvas.paste(sub, (ox, oy))
    m[oy:oy + nh, ox:ox + nw] = np.asarray(smask) > 128
    return canvas, m


def portrait_dots(img: Image.Image, mask: np.ndarray, invert: bool) -> np.ndarray:
    img, m = fit_subject(img, mask)
    m = ndimage.binary_fill_holes(ndimage.binary_closing(m, iterations=2))
    g = ImageOps.autocontrast(ImageOps.grayscale(img), cutoff=1)
    g = ImageEnhance.Contrast(g).enhance(1.3)
    g = g.filter(ImageFilter.UnsharpMask(radius=3, percent=140, threshold=2))
    arr = np.asarray(g).astype(np.float32)
    if invert:   # light theme: ink = shadows, lifted so the suit isn't solid
        target = np.where(m, arr * 0.62 + 85.0, 255.0)
    else:        # dark theme: ink = highlights
        target = np.where(m, 255.0 - arr, 255.0)
    return floyd_steinberg(target) & ndimage.binary_erosion(m, iterations=1)


# ================================================================ logos
def _ink_from_lum(lum: np.ndarray, content: np.ndarray, floor: float, gamma: float) -> np.ndarray:
    lo, hi = np.percentile(lum[content], [2, 98]) if content.any() else (0, 255)
    t = np.clip((lum - lo) / max(hi - lo, 1), 0, 1) ** gamma
    ink = np.where(content, floor + (1 - floor) * t, 0.0)
    rim = content & ~ndimage.binary_erosion(content, iterations=2)
    return np.where(rim, 1.0, ink)


def _place(ink: np.ndarray, dy: int = 0) -> np.ndarray:
    canvas = np.zeros((GRID_H, GRID_W))
    h, w = ink.shape
    ox, oy = (GRID_W - w) // 2, (GRID_H - h) // 2 + dy
    canvas[oy:oy + h, ox:ox + w] = ink
    return canvas


def _load_logo(path: Path, max_w: float, max_h: float) -> tuple[np.ndarray, np.ndarray]:
    """Return (lum, content) at grid resolution, cropped to ALL logo parts."""
    im = Image.open(path).convert("RGBA")
    bg = Image.new("RGBA", im.size, (0, 0, 0, 255))
    rgb = np.asarray(Image.alpha_composite(bg, im).convert("RGB")).astype(np.float32)
    lum = rgb @ np.array([0.299, 0.587, 0.114])
    content = lum > 22
    content = ndimage.binary_opening(content, iterations=2)
    labeled, n = ndimage.label(content)
    if n:  # keep every sizeable component (the old code kept only the largest -> half ETH)
        sizes = ndimage.sum(content, labeled, range(1, n + 1))
        keep = [i + 1 for i, s in enumerate(sizes) if s > sizes.max() * 0.02]
        content = np.isin(labeled, keep)
    ys, xs = np.where(content)
    box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    bw, bh = box[2] - box[0], box[3] - box[1]
    s = min(GRID_W * max_w / bw, GRID_H * max_h / bh)
    size = (int(bw * s), int(bh * s))
    lum_im = Image.fromarray(lum.astype(np.uint8)).crop(box).resize(size, Image.Resampling.LANCZOS)
    con_im = Image.fromarray(content.astype(np.uint8) * 255).crop(box).resize(size, Image.Resampling.BILINEAR)
    return np.asarray(lum_im).astype(np.float32), np.asarray(con_im) > 127


def bitcoin_dots() -> np.ndarray:
    lum, content = _load_logo(BTC_IMG, 0.80, 0.70)
    # orange disc -> ~38% ink, white ₿ -> solid
    ink = np.where(content, np.where(lum > 225, 1.0, 0.36), 0.0)
    rim = content & ~ndimage.binary_erosion(content, iterations=2)
    ink = np.where(rim, 1.0, ink)
    return floyd_steinberg(255 * (1 - _place(ink)))


def ethereum_dots() -> np.ndarray:
    lum, content = _load_logo(ETH_IMG, 0.62, 0.84)
    ink = _ink_from_lum(lum, content, floor=0.22, gamma=1.15)
    return floyd_steinberg(255 * (1 - _place(ink)))


def solana_dots() -> np.ndarray:
    """Solana mark drawn from its geometry (three slanted bars)."""
    W0, H0 = 398, 312
    bars = [
        [(70, 0), (392, 0), (330, 78), (6, 78)],
        [(6, 117), (330, 117), (392, 195), (70, 195)],
        [(70, 234), (392, 234), (330, 312), (6, 312)],
    ]
    k = 4
    hi = Image.new("L", (W0 * k, H0 * k), 0)
    d = ImageDraw.Draw(hi)
    for poly in bars:
        d.polygon([(x * k, y * k) for x, y in poly], fill=255)
    s = min(GRID_W * 0.82 / W0, GRID_H * 0.62 / H0)
    size = (int(W0 * s), int(H0 * s))
    cov = np.asarray(hi.resize(size, Image.Resampling.LANCZOS)).astype(np.float32) / 255
    content = cov > 0.5
    u = np.linspace(0, 1, size[0])[None, :]
    ink = np.where(content, 0.42 + 0.5 * u, 0.0)
    rim = content & ~ndimage.binary_erosion(content, iterations=2)
    ink = np.where(rim, 1.0, ink)
    return floyd_steinberg(255 * (1 - _place(ink)))


# ================================================================ helpers
def floyd_steinberg(gray: np.ndarray) -> np.ndarray:
    """1-bit serpentine Floyd–Steinberg; True = ink."""
    h, w = gray.shape
    img = gray.astype(np.float64) / 255.0
    out = np.zeros((h, w), dtype=bool)
    for y in range(h):
        fwd = y % 2 == 0
        xs = range(w) if fwd else range(w - 1, -1, -1)
        s = 1 if fwd else -1
        row, nxt = img[y], img[y + 1] if y + 1 < h else None
        for x in xs:
            old = row[x]
            new = 0.0 if old < 0.5 else 1.0
            out[y, x] = new == 0.0
            err = old - new
            if 0 <= x + s < w:
                row[x + s] += err * 7 / 16
            if nxt is not None:
                if 0 <= x - s < w:
                    nxt[x - s] += err * 3 / 16
                nxt[x] += err * 5 / 16
                if 0 <= x + s < w:
                    nxt[x + s] += err * 1 / 16
    return out


def pack_runs(dots: np.ndarray) -> str:
    """Horizontal runs -> compact path data."""
    parts = []
    for y in range(dots.shape[0]):
        row = np.concatenate([[0], dots[y].astype(np.int8), [0]])
        diff = np.diff(row)
        for x0, x1 in zip(np.where(diff == 1)[0], np.where(diff == -1)[0]):
            parts.append(f"M{x0} {y}h{x1 - x0}v1h-{x1 - x0}z")
    return "".join(parts)


def sample(dots: np.ndarray, n: int) -> np.ndarray:
    ys, xs = np.where(dots)
    idx = NP_RNG.choice(len(xs), size=n, replace=len(xs) < n)
    return np.stack([xs[idx], ys[idx]], axis=1).astype(np.float64) * PSUB


def assign(src: np.ndarray, cand: np.ndarray, also: np.ndarray | None = None) -> np.ndarray:
    """Optimal 1:1 assignment of candidate points to src particles (min squared travel)."""
    cost = ((src[:, None, :] - cand[None, :, :]) ** 2).sum(-1)
    if also is not None:
        cost += ((also[:, None, :] - cand[None, :, :]) ** 2).sum(-1)
    r, c = linear_sum_assignment(cost)
    out = np.empty_like(src)
    out[r] = cand[c]
    return out


def swirl(a: np.ndarray, b: np.ndarray, angle: float) -> np.ndarray:
    """Mid-flight positions: midpoint rotated about the centre + pushed out + jitter."""
    c = np.array([GRID_W, GRID_H]) * PSUB / 2
    m = (a + b) / 2 - c
    ca, sa = np.cos(angle), np.sin(angle)
    rot = np.stack([m[:, 0] * ca - m[:, 1] * sa, m[:, 0] * sa + m[:, 1] * ca], axis=1)
    return c + rot * 1.12 + NP_RNG.normal(0, 7, size=a.shape)


def particle_d(pts: np.ndarray) -> str:
    return "".join(f"M{int(x)} {int(y)}h{PSIZE}v{PSIZE}h-{PSIZE}z" for x, y in np.rint(pts))


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def kt(times: list[float], total: float) -> str:
    return ";".join(f"{min(max(t / total, 0), 1):.4f}" for t in times)


# ================================================================ timeline
def timeline():
    """Loop-relative arrive/depart times. The portrait hold is split across the
    loop seam (60% at the start, 40% at the end) so the loop restarts in a
    steady state: dense portrait shown, particles hidden."""
    t = HOLDS[0] * 0.6
    arrive, depart = [None], [t]
    for h in HOLDS[1:]:
        t += TRAVEL
        arrive.append(t)
        t += h
        depart.append(t)
    t += TRAVEL
    arrive[0] = t
    return arrive, depart, t + HOLDS[0] * 0.4


# ================================================================ info panel
def leader(label: str, value: str, total: int = 72) -> str:
    return "." * max(8, total - (len(label) + len(value) + 2))


def info_row(label: str, value: str, y: float, begin: float, th: dict) -> str:
    return (
        f'<g opacity="0">'
        f'<animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{begin:.2f}s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="{begin:.2f}s" fill="freeze"/>'
        f'<text x="470" y="{y:.0f}" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve">'
        f'<tspan fill="{th["chrome"]}">{esc(label)} </tspan>'
        f'<tspan fill="{th["dots"]}">{leader(label, value)}</tspan>'
        f'<tspan fill="{th["text"]}" font-weight="600"> {esc(value)}</tspan>'
        f"</text></g>"
    )


def info_panel(th: dict) -> str:
    p = [
        f'<text x="470" y="106" font-size="13" letter-spacing="2" fill="{th["chrome"]}" filter="url(#txtGlow)">SYSTEM.INFO</text>',
        f'<line x1="566" y1="102" x2="1061" y2="102" stroke="{th["hairline"]}"/>',
        f'<text x="1125" y="106" text-anchor="end" font-size="12" fill="{th["live"]}" font-weight="700">'
        f'<tspan>&#9679;</tspan> LIVE<animate attributeName="opacity" values="1;0.25;1" dur="1.6s" repeatCount="indefinite"/></text>',
    ]
    pill = PROFILE["pill"]
    pw = len(pill) * 8.6 + 22
    p.append(
        f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="0.6s" fill="freeze"/>'
        f'<rect x="470" y="122" width="{pw:.0f}" height="20" rx="4" fill="{th["pill"]}"/>'
        f'<text x="481" y="136" font-size="13" font-weight="700" fill="{th["pill_text"]}">{esc(pill)}</text>'
        f'<line x1="{470 + pw + 10:.0f}" y1="132" x2="1125" y2="132" stroke="{th["hairline"]}"/></g>'
    )
    y, t = 162.0, 0.9
    for block in ("identity", "stack"):
        for lab, val in PROFILE[block]:
            p.append(info_row(lab, val, y, t, th))
            y += 23
            t += 0.12
        y += 8
        t += 0.1
    p.append(
        f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{t:.2f}s" fill="freeze"/>'
        f'<text x="470" y="{y:.0f}" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve">'
        f'<tspan fill="{th["muted"]}">- Contact </tspan><tspan fill="{th["dots"]}">{"-" * 70}</tspan></text></g>'
    )
    y += 23
    t += 0.12
    for lab, val in PROFILE["contact"]:
        p.append(info_row(lab, val, y, t, th))
        y += 23
        t += 0.12
    y += 8
    p.append(
        f'<text x="470" y="{y:.0f}" font-size="14" fill="{th["muted"]}">'
        f'&#9656; More about me &amp; projects below in README &#8595; '
        f'<tspan fill="{th["chrome"]}">&#9608;<animate attributeName="fill-opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></tspan></text>'
    )
    return "\n".join(p)


# ================================================================ banner
def build_svg(theme_name: str, shapes: list[np.ndarray]) -> str:
    th = THEMES[theme_name]
    arrive, depart, L = timeline()
    n_shapes = len(shapes)
    loop = f'dur="{L:.2f}s" begin="{INTRO}s" repeatCount="indefinite"'

    # ---- particle stations: OT-chained so every morph is near-minimal travel
    pts = [sample(s, N_PARTICLES) for s in shapes]
    P = [pts[0]]
    P.append(assign(P[0], pts[1]))
    P3 = assign(P[0], pts[3])                    # solve last leg backwards
    P.append(assign(P[1], pts[2], also=P3))      # eth fits both neighbours
    P.append(assign(P[2], pts[3], also=P[0]))
    stations = P  # 0 portrait, 1 btc, 2 eth, 3 sol
    mids = [swirl(stations[i], stations[(i + 1) % n_shapes], (0.85 if i % 2 == 0 else -0.85))
            for i in range(n_shapes)]
    scatter = NP_RNG.uniform([0, 0], [GRID_W * PSUB, GRID_H * PSUB], size=(N_PARTICLES, 2))
    scatter[:, 1] = scatter[:, 1] * 0.35 - GRID_H * PSUB * 0.15    # pour in from the top

    groups = np.array_split(NP_RNG.permutation(N_PARTICLES), N_GROUPS)
    travel = TRAVEL - MAX_STAGGER

    ease_in = "0.55 0 0.9 0.55"
    ease_out = "0.1 0.45 0.45 1"
    hold = "0 0 1 1"

    def group_anim(g: int, idx: np.ndarray) -> str:
        off = MAX_STAGGER * g / max(N_GROUPS - 1, 1)
        times, vals, splines = [0.0], [particle_d(stations[0][idx])], []
        for i in range(n_shapes):
            j = (i + 1) % n_shapes
            dep = depart[i] + off
            times += [dep, dep + travel / 2, dep + travel]
            vals += [particle_d(stations[i][idx]), particle_d(mids[i][idx]), particle_d(stations[j][idx])]
            splines += [hold, ease_in, ease_out]
        times.append(L)
        vals.append(vals[-1])
        splines.append(hold)
        ib = 0.1 + 0.6 * g / max(N_GROUPS - 1, 1)
        return (
            f'<path d="{particle_d(scatter[idx])}">'
            f'<animate attributeName="d" values="{particle_d(scatter[idx])};{vals[0]}" dur="{INTRO - 0.4 - ib:.2f}s" '
            f'begin="{ib:.2f}s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.2 0.6 0.3 1"/>'
            f'<animate attributeName="d" values="{";".join(vals)}" keyTimes="{kt(times, L)}" '
            f'calcMode="spline" keySplines="{";".join(splines)}" {loop}/>'
            f"</path>"
        )

    # particle colour follows the shape it is flying to
    fill_t, fill_v = [0.0], [th["shape"][0]]
    for i in range(n_shapes):
        j = (i + 1) % n_shapes
        fill_t += [depart[i] + 0.2, depart[i] + TRAVEL]
        fill_v += [th["shape"][i], th["shape"][j]]
    fill_t.append(L)
    fill_v.append(th["shape"][0])

    # particles visible only while moving; crisp frames take over on holds
    nxt = lambda i: arrive[(i + 1) % n_shapes]  # noqa: E731  (last group lands)
    pop_t, pop_v = [0.0], [0]
    for i in range(n_shapes):
        pop_t += [depart[i] - FADE, depart[i], nxt(i), nxt(i) + FADE]
        pop_v += [0, 1, 1, 0]
    pop_t.append(L)
    pop_v.append(0)

    def dense_anim(i: int) -> str:
        if i == 0:   # visible across the loop seam
            t = [0, depart[0] - FADE, depart[0], arrive[0], arrive[0] + FADE, L]
            v = [1, 1, 0, 0, 1, 1]
        else:
            t = [0, arrive[i], arrive[i] + FADE, depart[i] - FADE, depart[i], L]
            v = [0, 0, 1, 1, 0, 0]
        return (f'<animate attributeName="opacity" values="{";".join(map(str, v))}" '
                f'keyTimes="{kt(t, L)}" {loop}/>')

    def label_anim(i: int) -> str:
        # label switches to the destination as soon as the morph starts
        if i == 0:
            t, v = [0, depart[0], depart[-1], L], [1, 0, 1, 1]
        else:
            t, v = [0, depart[i - 1], depart[i], L], [0, 1, 0, 0]
        return (f'<animate attributeName="opacity" values="{";".join(map(str, v))}" '
                f'keyTimes="{kt(t, L)}" calcMode="discrete" {loop}/>')

    # ---------------------------------------------------------------- svg
    g1, g2 = th["sol_grad"]
    o = []
    o.append(
        '<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="610" viewBox="0 0 1180 610" '
        "font-family=\"ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace\" "
        'role="img" aria-label="Rohit Yadav — Rust Blockchain Developer — profile.sh --live">'
    )
    o.append(f"""<defs>
<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{th['violet2']}"><animate attributeName="stop-color" values="{th['violet2']};{th['chrome']};{th['accent']};{th['violet2']}" dur="10s" repeatCount="indefinite"/></stop>
  <stop offset="0.5" stop-color="{th['chrome']}"><animate attributeName="stop-color" values="{th['chrome']};{th['accent']};{th['violet2']};{th['chrome']}" dur="10s" repeatCount="indefinite"/></stop>
  <stop offset="1" stop-color="{th['accent']}"><animate attributeName="stop-color" values="{th['accent']};{th['violet2']};{th['chrome']};{th['accent']}" dur="10s" repeatCount="indefinite"/></stop>
</linearGradient>
<linearGradient id="panelGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{th['panel']}"/><stop offset="1" stop-color="{th['panel2']}"/></linearGradient>
<linearGradient id="solGrad" gradientUnits="userSpaceOnUse" x1="20" y1="{GRID_H * 0.8:.0f}" x2="{GRID_W - 20}" y2="{GRID_H * 0.2:.0f}"><stop offset="0" stop-color="{g1}"/><stop offset="1" stop-color="{g2}"/></linearGradient>
<linearGradient id="scanGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{th['scan']}" stop-opacity="0"/><stop offset="0.85" stop-color="{th['scan']}" stop-opacity="0.10"/><stop offset="1" stop-color="{th['scan']}" stop-opacity="0.35"/></linearGradient>
<pattern id="mapGrid" width="20" height="20" patternUnits="userSpaceOnUse" x="{FRAME_X}" y="{FRAME_Y}"><path d="M20 0H0V20" fill="none" stroke="{th['gridline']}" stroke-width="1"/></pattern>
<filter id="glow8" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="8"/></filter>
<filter id="glow3" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="3"/></filter>
<filter id="txtGlow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="0.9" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<clipPath id="winClip"><rect x="2" y="2" width="1176" height="606" rx="18"/></clipPath>
<clipPath id="mapClip"><rect x="{FRAME_X}" y="{FRAME_Y}" width="{PANEL_W}" height="{PANEL_H}" rx="10"/></clipPath>
</defs>""")
    o.append(f'<rect x="2" y="2" width="1176" height="606" rx="18" fill="{th["bg"]}"/>')
    o.append('<g clip-path="url(#winClip)">')
    o.append('<rect x="2" y="2" width="1176" height="606" fill="url(#panelGrad)"/>')
    o.append(f'<rect x="2" y="2" width="1176" height="46" fill="{th["bar"]}"/>')
    o.append(f'<line x1="2" y1="48" x2="1178" y2="48" stroke="{th["hairline"]}"/>')
    o.append('<circle cx="30" cy="25" r="5.5" fill="#ff5f56"/><circle cx="50" cy="25" r="5.5" fill="#ffbd2e"/><circle cx="70" cy="25" r="5.5" fill="#27c93f"/>')
    o.append(f'<text x="590" y="29" text-anchor="middle" font-size="12" fill="{th["muted"]}">{esc(PROFILE["title"])}</text>')

    # frame + live shape label
    o.append(f'<text x="38" y="74" font-size="10" letter-spacing="3" fill="{th["dim"]}">VISUAL.MAP</text>')
    for i, lab in enumerate(SHAPE_LABELS):
        o.append(
            f'<text x="436" y="74" text-anchor="end" font-size="10" letter-spacing="1.5" fill="{th["shape"][i]}" opacity="{1 if i == 0 else 0}">'
            f'&#9673; {lab}{label_anim(i)}</text>'
        )
    o.append(f'<rect x="{FRAME_X}" y="{FRAME_Y}" width="{PANEL_W}" height="{PANEL_H}" rx="10" fill="none" stroke="{th["chrome"]}" stroke-width="2" opacity="0.45" filter="url(#glow3)"/>')
    o.append(f'<rect x="{FRAME_X}" y="{FRAME_Y}" width="{PANEL_W}" height="{PANEL_H}" rx="10" fill="{th["panel"]}" stroke="{th["frame_stroke"]}"/>')

    o.append('<g clip-path="url(#mapClip)">')
    o.append(f'<rect x="{FRAME_X}" y="{FRAME_Y}" width="{PANEL_W}" height="{PANEL_H}" fill="url(#mapGrid)"/>')

    # crisp frames
    o.append(f'<g transform="translate({MAP_TX},{MAP_TY:.1f}) scale({CELL})" shape-rendering="crispEdges">')
    for i, dots in enumerate(shapes):
        fill = "url(#solGrad)" if i == 3 else th["shape"][i]
        if i == 0:   # intro: portrait resolves once particles settle
            o.append(f'<g opacity="0">'
                     f'<animate attributeName="opacity" values="0;1" dur="0.5s" begin="{INTRO - 0.45:.2f}s" fill="freeze"/>'
                     f'<g opacity="1">{dense_anim(0)}<path fill="{fill}" d="{pack_runs(dots)}"/></g></g>')
        else:
            o.append(f'<g opacity="0">{dense_anim(i)}<path fill="{fill}" d="{pack_runs(dots)}"/></g>')
    o.append("</g>")

    # particles
    o.append(
        f'<g transform="translate({MAP_TX},{MAP_TY:.1f}) scale({CELL / PSUB})" fill="{th["shape"][0]}">'
        f'<animate attributeName="opacity" values="1;1;0" keyTimes="0;0.8;1" dur="{INTRO:.2f}s" fill="freeze"/>'
        f'<animate attributeName="opacity" values="{";".join(map(str, pop_v))}" keyTimes="{kt(pop_t, L)}" {loop}/>'
        f'<animate attributeName="fill" values="{";".join(fill_v)}" keyTimes="{kt(fill_t, L)}" {loop}/>'
    )
    for g, idx in enumerate(groups):
        o.append(group_anim(g, idx))
    o.append("</g>")

    # scan beam
    o.append(
        f'<rect x="{FRAME_X}" y="{FRAME_Y - 70}" width="{PANEL_W}" height="70" fill="url(#scanGrad)">'
        f'<animateTransform attributeName="transform" type="translate" values="0 0;0 {PANEL_H + 70}" dur="4.2s" repeatCount="indefinite"/></rect>'
    )
    o.append("</g>")  # mapClip

    c = th["chrome"]
    for d in ("M50 84H36V98", "M422 84H436V98", "M50 576H36V562", "M422 576H436V562"):
        o.append(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="2" opacity="0.85"/>')

    o.append(info_panel(th))
    o.append(
        '<rect x="3" y="3" width="1174" height="604" rx="17" fill="none" stroke="url(#accent)" stroke-width="3" opacity="0.55" filter="url(#glow8)"/>'
        '<rect x="3" y="3" width="1174" height="604" rx="17" fill="none" stroke="url(#accent)" stroke-width="1.6"/>'
    )
    o.append("</g>\n</svg>\n")
    return "\n".join(o)


def preview(dots: np.ndarray, color: tuple[int, int, int], name: str) -> None:
    img = np.zeros((GRID_H, GRID_W, 3), dtype=np.uint8)
    img[:] = (10, 16, 31)
    img[dots] = color
    Image.fromarray(img).save(DEBUG / f"{name}.png")


def main() -> None:
    DEBUG.mkdir(parents=True, exist_ok=True)
    print("Portrait:", PHOTO)
    rgb, mask = remove_background(Image.open(PHOTO).convert("RGB"))
    print("Logos…")
    logos = [bitcoin_dots(), ethereum_dots(), solana_dots()]
    for name, d in zip(("btc", "eth", "sol"), logos):
        preview(d, (34, 211, 238), f"logo_{name}")
        print(f"  {name}: {int(d.sum())} dots")
    for theme_name in ("dark", "light"):
        th = THEMES[theme_name]
        pdots = portrait_dots(rgb, mask, invert=th["invert_portrait"])
        preview(pdots, (167, 139, 250), f"portrait_{theme_name}")
        svg = build_svg(theme_name, [pdots] + logos)
        out = OUT_DIR / f"{theme_name}.svg"
        out.write_text(svg, encoding="utf-8")
        print(f"Wrote {out.name} ({out.stat().st_size / 1024:.0f} KB, portrait {int(pdots.sum())} dots)")


if __name__ == "__main__":
    main()
