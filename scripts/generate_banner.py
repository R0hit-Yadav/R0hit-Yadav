#!/usr/bin/env python3
"""
Generate theme-aware animated profile banners (dark.svg / light.svg)
for Rohit Yadav — dithered portrait + terminal SYSTEM.INFO panel.
"""
from __future__ import annotations

import math
import os
import random
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[1]
PHOTO = Path("/home/rohit/Rohit/Work/GithubReadme/Rohit.jpg")
OUT_DIR = ROOT

# Portrait grid — match arifhaxn frame math exactly
# Frame: x=36,y=84 w=400 h=492 · portrait translate(50,86) scale(1.24,1.4471)
# → 300*1.24=372 wide (14px side inset) · 340*1.4471≈492 tall (flush)
GRID_W, GRID_H = 300, 340
PANEL_W, PANEL_H = 400, 492
SCALE_X = 1.2400
SCALE_Y = 1.4471
PORTRAIT_TX, PORTRAIT_TY = 50, 86
FRAME_X, FRAME_Y = 36, 84

# Timing (Master Prompt)
INTRO_END = 3.2
LOOP_DUR = 14.2
PORTRAIT_HOLD = 3.0
LOGO_HOLD = 2.0
TRANS = 1.3

N_INTRO_GROUPS = 60
N_DRIFT_BANDS = 94
N_TRAVELLERS = 900

RNG = random.Random(42)
NP_RNG = np.random.default_rng(42)


PROFILE = {
    "name": "Rohit Yadav",
    "handle": "@R0hit-Yadav",
    "email": "rohitkyadav2312@gmail.com",
    "email_title": "rohitkyadav2312@gmail.com - % ./profile.sh --live",
    # identity block
    "identity": [
        ("Subject", "Rohit Yadav"),
        ("Role", "Rust Blockchain Developer"),
        ("Origin", "Ahmedabad, India"),
        ("Education", "B.E. Computer Engineering"),
        ("Status", "Building + Shipping On-Chain"),
        ("ToolChain", "VS Code, Cargo, Git, Anchor"),
    ],
    # stack block
    "stack": [
        ("Core.Lang", "Rust, Move, Solidity, TS"),
        ("Core.Frontend", "React, TypeScript"),
        ("Core.Backend", "Rust, Anchor, Node.js"),
        ("Core.Chains", "Solana, Aptos, EVM, Soroban"),
        ("Core.Infra", "Docker, AWS, Foundry, Git"),
    ],
    # contact block
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
        "bg": "#070B16",
        "panel": "#0A101F",
        "panel2": "#0C1426",
        "bar": "#0B1222",
        "portrait": "#A78BFA",
        "chrome": "#22D3EE",
        "accent": "#10B981",
        "violet2": "#7C3AED",
        "pill": "#4C1D95",
        "pill_text": "#E9D5FF",
        "live": "#F87171",
        "text": "#F8FAFC",
        "muted": "#94A3B8",
        "dim": "#475569",
        "dots": "rgba(148,163,184,0.35)",
        "hairline": "rgba(255,255,255,0.10)",
        "frame_stroke": "rgba(34,211,238,0.35)",
        "invert_dither": False,
        "segment_bg": True,
    },
    "light": {
        "bg": "#E2E8F0",
        "panel": "#FFFFFF",
        "panel2": "#F8FAFC",
        "bar": "#F1F5F9",
        "portrait": "#7C3AED",
        "chrome": "#0891B2",
        "accent": "#059669",
        "violet2": "#7C3AED",
        "pill": "#5B21B6",
        "pill_text": "#EDE9FE",
        "live": "#DC2626",
        "text": "#0F172A",
        "muted": "#475569",
        "dim": "#94A3B8",
        "dots": "rgba(100,116,139,0.40)",
        "hairline": "rgba(0,0,0,0.08)",
        "frame_stroke": "rgba(8,145,178,0.40)",
        "invert_dither": True,
        "segment_bg": False,
    },
}


def remove_background(img: Image.Image) -> tuple[Image.Image, np.ndarray]:
    """Return RGB image + boolean subject mask."""
    try:
        from rembg import remove

        rgba = remove(img.convert("RGBA"))
        arr = np.array(rgba)
        mask = arr[:, :, 3] > 128
        rgb = Image.fromarray(arr[:, :, :3], "RGB")
        return rgb, mask
    except Exception as e:
        print(f"[warn] rembg failed ({e}); using heuristic mask")
        return heuristic_mask(img)


def heuristic_mask(img: Image.Image) -> tuple[Image.Image, np.ndarray]:
    """Fallback: keep center subject, drop sky-ish / edge blues & grays."""
    rgb = img.convert("RGB")
    arr = np.asarray(rgb).astype(np.float32)
    h, w, _ = arr.shape
    yy, xx = np.mgrid[0:h, 0:w]
    # Distance from vertical center-lower (person leaning on ledge)
    cx, cy = w * 0.50, h * 0.42
    dist = np.sqrt(((xx - cx) / (w * 0.38)) ** 2 + ((yy - cy) / (h * 0.48)) ** 2)
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    sky = (b > 140) & (b > r + 15) & (b > g)
    concrete = (np.abs(r - g) < 18) & (np.abs(g - b) < 18) & (r > 90) & (r < 200) & (yy > h * 0.55)
    edge = (xx < w * 0.08) | (xx > w * 0.92) | (yy < h * 0.05)
    mask = (dist < 1.05) & ~sky & ~(concrete & (dist > 0.7)) & ~edge
    # Fill holes roughly
    from scipy import ndimage

    mask = ndimage.binary_closing(mask, iterations=4)
    mask = ndimage.binary_fill_holes(mask)
    labeled, n = ndimage.label(mask)
    if n:
        sizes = ndimage.sum(mask, labeled, range(1, n + 1))
        mask = labeled == (np.argmax(sizes) + 1)
    return rgb, mask


def crop_head_shoulders(img: Image.Image, mask: np.ndarray) -> tuple[Image.Image, np.ndarray]:
    """Crop head + shoulders, centered like arifhaxn (subject fills frame, not tight face)."""
    ys, xs = np.where(mask)
    if len(xs) == 0:
        w, h = img.size
        side = min(w, h)
        left = (w - side) // 2
        top = int(h * 0.05)
        box = (left, top, left + side, top + int(side * 1.15))
        cropped = img.crop(box)
        m = np.ones((cropped.size[1], cropped.size[0]), dtype=bool)
        return cropped, m

    x0, x1 = int(xs.min()), int(xs.max())
    y0, y1 = int(ys.min()), int(ys.max())
    bw, bh = x1 - x0, y1 - y0

    # Generous side pad so subject sits centered with breathing room
    pad_x = int(bw * 0.22)
    pad_top = int(bh * 0.16)   # more headroom
    pad_bot = int(bh * 0.02)   # less empty bottom
    x0 = max(0, x0 - pad_x)
    x1 = min(img.size[0], x1 + pad_x)
    y0 = max(0, y0 - pad_top)
    y1 = min(img.size[1], y1 + pad_bot)

    # Force exact portrait aspect 300:340, centered on subject
    cw, ch = x1 - x0, y1 - y0
    target = GRID_W / GRID_H
    cur = cw / max(ch, 1)
    cx = (x0 + x1) / 2
    cy = (y0 + y1) / 2 - bh * 0.04  # bias slightly upward toward face
    if cur > target:
        nh = ch
        nw = int(nh * target)
    else:
        nw = cw
        nh = int(nw / target)
    x0 = int(max(0, cx - nw / 2))
    y0 = int(max(0, cy - nh / 2))
    x1 = int(min(img.size[0], x0 + nw))
    y1 = int(min(img.size[1], y0 + nh))
    # If clamped, shift back
    if x1 - x0 < nw:
        x0 = max(0, x1 - nw)
    if y1 - y0 < nh:
        y0 = max(0, y1 - nh)
        y1 = min(img.size[1], y0 + nh)

    box = (x0, y0, x1, y1)
    cropped = img.crop(box)
    m = mask[y0:y1, x0:x1]
    return cropped, m


def recenter_on_canvas(
    img: Image.Image, mask: np.ndarray, out_w: int = GRID_W, out_h: int = GRID_H
) -> tuple[Image.Image, np.ndarray]:
    """
    Place subject centered on a fixed canvas (matches arifhaxn framing).
    Horizontal center + modest headroom so the face sits in the upper half.
    """
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return img.resize((out_w, out_h), Image.Resampling.LANCZOS), np.ones((out_h, out_w), dtype=bool)

    x0, x1 = int(xs.min()), int(xs.max())
    y0, y1 = int(ys.min()), int(ys.max())
    # Trim tiny mask bleed
    sub = img.crop((x0, y0, x1 + 1, y1 + 1))
    smask = mask[y0 : y1 + 1, x0 : x1 + 1]
    sw, sh = sub.size

    # Fit subject inside canvas with ~10% margin
    margin = 0.08
    max_w = int(out_w * (1 - 2 * margin))
    max_h = int(out_h * (1 - 2 * margin))
    scale = min(max_w / sw, max_h / sh)
    nw, nh = max(1, int(sw * scale)), max(1, int(sh * scale))
    sub_r = sub.resize((nw, nh), Image.Resampling.LANCZOS)
    mask_r = Image.fromarray((smask.astype(np.uint8) * 255)).resize((nw, nh), Image.Resampling.BILINEAR)

    canvas = Image.new("RGB", (out_w, out_h), (0, 0, 0))
    mcanvas = np.zeros((out_h, out_w), dtype=bool)

    # Center X; bias Y upward (headroom ~12% of leftover)
    ox = (out_w - nw) // 2
    leftover_y = out_h - nh
    oy = max(0, int(leftover_y * 0.28))  # more space below than above → head higher
    canvas.paste(sub_r, (ox, oy))
    marr = np.asarray(mask_r) > 128
    mcanvas[oy : oy + nh, ox : ox + nw] = marr
    return canvas, mcanvas


def prepare_dither(
    img: Image.Image, mask: np.ndarray, dark_mode: bool
) -> tuple[np.ndarray, np.ndarray]:
    """
    Returns (binary_dots HxW bool, mask_resized HxW bool).
    dark_mode: segment bg, dots = lit subject
    light_mode: subject on white, dots = dark parts (shadow-lifted so shirts aren't solid)
    """
    from scipy import ndimage

    # Center subject on the exact dither grid before processing
    img, mask_r = recenter_on_canvas(img, mask, GRID_W, GRID_H)
    mask_r = ndimage.binary_closing(mask_r, iterations=2)
    mask_r = ndimage.binary_fill_holes(mask_r)

    # Contrast pipeline
    g = ImageOps.grayscale(img)
    g = ImageOps.autocontrast(g, cutoff=1)
    g = ImageEnhance.Contrast(g).enhance(1.3)
    g = g.filter(ImageFilter.UnsharpMask(radius=3, percent=140, threshold=2))
    arr = np.asarray(g).astype(np.float32)

    if dark_mode:
        arr = np.where(mask_r, arr, 0.0)
        target = 255.0 - arr
        target = np.where(mask_r, target, 255.0)
    else:
        arr = np.where(mask_r, arr, 255.0)
        arr = np.where(mask_r, arr * 0.62 + 85.0, 255.0)
        target = np.clip(arr, 0, 255)

    dots = floyd_steinberg(target)
    eroded = ndimage.binary_erosion(mask_r, iterations=1)
    dots = dots & eroded
    return dots, mask_r


def floyd_steinberg(gray: np.ndarray) -> np.ndarray:
    """1-bit FS dither; True = draw ink (dark)."""
    h, w = gray.shape
    img = gray.copy() / 255.0
    out = np.zeros((h, w), dtype=bool)
    for y in range(h):
        if y % 2 == 0:
            xs = range(w)
            step = 1
        else:
            xs = range(w - 1, -1, -1)
            step = -1
        for x in xs:
            old = img[y, x]
            new = 0.0 if old < 0.5 else 1.0
            out[y, x] = new < 0.5
            err = old - new
            if step == 1:
                if x + 1 < w:
                    img[y, x + 1] += err * 7 / 16
                if y + 1 < h:
                    if x > 0:
                        img[y + 1, x - 1] += err * 3 / 16
                    img[y + 1, x] += err * 5 / 16
                    if x + 1 < w:
                        img[y + 1, x + 1] += err * 1 / 16
            else:
                if x - 1 >= 0:
                    img[y, x - 1] += err * 7 / 16
                if y + 1 < h:
                    if x + 1 < w:
                        img[y + 1, x + 1] += err * 3 / 16
                    img[y + 1, x] += err * 5 / 16
                    if x - 1 >= 0:
                        img[y + 1, x - 1] += err * 1 / 16
    return out


def pack_runs(dots: np.ndarray) -> list[str]:
    """Pack horizontal runs into SVG path commands."""
    h, w = dots.shape
    parts = []
    for y in range(h):
        x = 0
        while x < w:
            if not dots[y, x]:
                x += 1
                continue
            x0 = x
            while x < w and dots[y, x]:
                x += 1
            run = x - x0
            if run == 1:
                parts.append(f"M{x0} {y}h1v1h-1z")
            else:
                parts.append(f"M{x0} {y}h{run}v1h-{run}z")
    return parts


def dots_to_coords(dots: np.ndarray) -> np.ndarray:
    ys, xs = np.where(dots)
    return np.stack([xs, ys], axis=1).astype(np.float64)


def logo_shapes() -> list[np.ndarray]:
    """Three logo point clouds in grid space (300x340)."""
    logos = []

    # 1) Rust-inspired gear ring + inner R stem
    pts = []
    cx, cy, r = 150, 170, 78
    for a in np.linspace(0, 2 * math.pi, 120, endpoint=False):
        for rr in (r - 4, r, r + 4):
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        # teeth
        if int(a / (math.pi / 6)) % 2 == 0:
            for rr in np.linspace(r + 6, r + 18, 6):
                pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    for y in range(130, 220):
        for x in range(138, 162):
            if abs(x - 150) < 8 or (y > 200 and abs(x - 150) < 22):
                pts.append((x, y))
    logos.append(np.array(pts, dtype=np.float64))

    # 2) Blockchain hexagon chain
    pts = []
    def hexagon(hx, hy, rad):
        out = []
        for i in range(6):
            a = math.pi / 6 + i * math.pi / 3
            out.append((hx + rad * math.cos(a), hy + rad * math.sin(a)))
        # edges sampled
        edge = []
        for i in range(6):
            x0, y0 = out[i]
            x1, y1 = out[(i + 1) % 6]
            for t in np.linspace(0, 1, 14):
                edge.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
        return edge

    for hx, hy in ((110, 150), (190, 150), (150, 210)):
        pts.extend(hexagon(hx, hy, 42))
        pts.extend(hexagon(hx, hy, 28))
    # links
    for x in range(130, 170):
        pts.append((x, 165))
        pts.append((x, 195))
    logos.append(np.array(pts, dtype=np.float64))

    # 3) </> code glyph
    pts = []
    # <
    for t in np.linspace(0, 1, 50):
        pts.append((150 - 55 * t, 120 + 50 * t))
        pts.append((150 - 55 * t, 220 - 50 * t))
    for t in np.linspace(0, 1, 40):
        pts.append((95 + 10 * t, 170))
    # /
    for t in np.linspace(0, 1, 60):
        pts.append((130 + 40 * t, 230 - 110 * t))
    # >
    for t in np.linspace(0, 1, 50):
        pts.append((150 + 55 * t, 120 + 50 * t))
        pts.append((150 + 55 * t, 220 - 50 * t))
    logos.append(np.array(pts, dtype=np.float64))

    return logos


def sample_points(cloud: np.ndarray, n: int) -> np.ndarray:
    if len(cloud) == 0:
        return NP_RNG.uniform([50, 50], [250, 290], size=(n, 2))
    idx = NP_RNG.choice(len(cloud), size=n, replace=len(cloud) < n)
    pts = cloud[idx].copy()
    pts += NP_RNG.normal(0, 1.2, size=pts.shape)
    return pts


def optimal_transport_match(src: np.ndarray, dst: np.ndarray) -> np.ndarray:
    """Greedy nearest matching (approx OT) — permute dst to match src order."""
    from scipy.spatial import cKDTree

    tree = cKDTree(dst)
    used = set()
    matched = np.zeros_like(src)
    # Sort src by x+y for stability
    order = np.argsort(src[:, 0] + src[:, 1] * 0.3)
    for i in order:
        dists, idxs = tree.query(src[i], k=min(12, len(dst)))
        if np.isscalar(idxs):
            idxs = [idxs]
        for j in np.atleast_1d(idxs):
            j = int(j)
            if j not in used:
                matched[i] = dst[j]
                used.add(j)
                break
        else:
            matched[i] = dst[int(idxs[0])]
    return matched


def path_from_points(pts: np.ndarray, size: float = 1.0) -> str:
    """Render traveller dots as path runs (rounded to int grid)."""
    if len(pts) == 0:
        return ""
    cells = defaultdict(list)
    for x, y in pts:
        xi, yi = int(round(x)), int(round(y))
        if 0 <= xi < GRID_W and 0 <= yi < GRID_H:
            cells[yi].append(xi)
    parts = []
    s = max(1, int(round(size)))
    for y in sorted(cells):
        xs = sorted(set(cells[y]))
        i = 0
        while i < len(xs):
            x0 = xs[i]
            x1 = x0
            while i + 1 < len(xs) and xs[i + 1] == x1 + 1:
                i += 1
                x1 = xs[i]
            run = x1 - x0 + 1
            parts.append(f"M{x0} {y}h{run}v{s}h-{run}z")
            i += 1
    return "".join(parts)


def leader_dots(label: str, value: str, total: int = 72) -> str:
    """Dot leaders filling the gap between label and value (arifhaxn style)."""
    used = len(label) + 1 + 1 + len(value)
    n = max(8, total - used)
    return "." * n


def info_row(label: str, value: str, y: float, begin: float, theme: dict, label_color: str | None = None) -> str:
    lc = label_color or theme["chrome"]
    dots = leader_dots(label, value)
    return (
        f'<g opacity="0">'
        f'<animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{begin:.2f}s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="{begin:.2f}s" fill="freeze"/>'
        f'<text x="470" y="{y:.0f}" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve">'
        f'<tspan fill="{lc}">{_xml_escape(label)} </tspan>'
        f'<tspan fill="{theme["dots"]}">{dots}</tspan>'
        f'<tspan fill="{theme["text"]}" font-weight="600"> {_xml_escape(value)}</tspan>'
        f'</text></g>'
    )


def info_rows_svg(theme: dict) -> str:
    """SYSTEM.INFO panel matching arifhaxn typography: cyan labels, white values, pill, LIVE."""
    parts = []
    # Header row
    parts.append(
        f'<text x="470" y="106" font-size="13" letter-spacing="2" fill="{theme["chrome"]}" filter="url(#txtGlow)">SYSTEM.INFO</text>'
    )
    parts.append(
        f'<line x1="566" y1="102" x2="1061" y2="102" stroke="{theme["hairline"]}"/>'
    )
    parts.append(
        f'<text x="1125" y="106" text-anchor="end" font-size="12" fill="{theme["live"]}" font-weight="700">'
        f'<tspan>&#9679;</tspan> LIVE'
        f'<animate attributeName="opacity" values="1;0.25;1" dur="1.6s" repeatCount="indefinite"/>'
        f'</text>'
    )

    # Email pill
    email = PROFILE["email"]
    pill_w = max(245, len(email) * 9 + 24)
    parts.append(
        f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="0.6s" fill="freeze"/>'
        f'<rect x="470" y="122" width="{pill_w}" height="20" rx="4" fill="{theme["pill"]}"/>'
        f'<text x="479" y="136" font-size="14" font-weight="700" fill="{theme["pill_text"]}">{_xml_escape(email)}</text>'
        f'<line x1="{470 + pill_w + 10}" y1="130" x2="1125" y2="130" stroke="{theme["hairline"]}"/>'
        f'</g>'
    )

    y = 162.0
    t = 0.90
    # Identity
    for lab, val in PROFILE["identity"]:
        parts.append(info_row(lab, val, y, t, theme))
        y += 23
        t += 0.12

    # Stack (small gap)
    y += 8
    t += 0.10
    for lab, val in PROFILE["stack"]:
        parts.append(info_row(lab, val, y, t, theme))
        y += 23
        t += 0.12

    # Contact separator
    y += 8
    t += 0.08
    contact_dots = "-" * 70
    parts.append(
        f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{t:.2f}s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="{t:.2f}s" fill="freeze"/>'
        f'<text x="470" y="{y:.0f}" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve">'
        f'<tspan fill="{theme["muted"]}">- Contact </tspan>'
        f'<tspan fill="{theme["dots"]}">{contact_dots}</tspan>'
        f'</text></g>'
    )
    y += 23
    t += 0.12

    for lab, val in PROFILE["contact"]:
        parts.append(info_row(lab, val, y, t, theme))
        y += 23
        t += 0.12

    # Footer CTA with blinking block cursor (arifhaxn style)
    y += 8
    parts.append(
        f'<text x="470" y="{y:.0f}" font-size="14" fill="{theme["muted"]}">'
        f'&#9656; More about me &amp; projects below in README &#8595; '
        f'<tspan fill="{theme["chrome"]}">&#9608;'
        f'<animate attributeName="fill-opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/>'
        f'</tspan></text>'
    )
    return "\n".join(parts)


def _xml_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def portrait_transform() -> str:
    return f'translate({PORTRAIT_TX},{PORTRAIT_TY}) scale({SCALE_X:.4f},{SCALE_Y:.4f})'


def build_svg(theme_name: str, dots: np.ndarray) -> str:
    theme = THEMES[theme_name]
    coords = dots_to_coords(dots)
    print(f"[{theme_name}] portrait dots: {len(coords)}")

    # Intro groups — interleaved random across whole portrait
    indices = list(range(len(coords)))
    RNG.shuffle(indices)
    intro_groups = [[] for _ in range(N_INTRO_GROUPS)]
    for i, idx in enumerate(indices):
        intro_groups[i % N_INTRO_GROUPS].append(coords[idx])

    # Drift bands with position noise (avoid grid trap)
    noisy = coords + NP_RNG.normal(0, 4.0, size=coords.shape)
    cx, cy = coords.mean(axis=0)
    ang = np.arctan2(noisy[:, 1] - cy, noisy[:, 0] - cx)
    order = np.argsort(ang + NP_RNG.normal(0, 0.15, size=len(ang)))
    bands = [[] for _ in range(N_DRIFT_BANDS)]
    for i, idx in enumerate(order):
        bands[i % N_DRIFT_BANDS].append(coords[idx])

    logos = logo_shapes()
    first_centroid = logos[0].mean(axis=0)

    if len(coords) >= N_TRAVELLERS:
        t_idx = NP_RNG.choice(len(coords), size=N_TRAVELLERS, replace=False)
        travellers_src = coords[t_idx]
    else:
        travellers_src = sample_points(coords, N_TRAVELLERS)

    logo_targets = [
        optimal_transport_match(travellers_src, sample_points(lg, N_TRAVELLERS))
        for lg in logos
    ]

    pt = portrait_transform()
    parts: list[str] = []
    parts.append(
        f'''<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="610" viewBox="0 0 1180 610" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace" role="img" aria-label="Rohit Yadav — profile.sh --live">
<defs>
<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{theme["violet2"]}"><animate attributeName="stop-color" values="{theme["violet2"]};{theme["chrome"]};{theme["accent"]};{theme["violet2"]}" dur="10s" repeatCount="indefinite"/></stop>
  <stop offset="0.5" stop-color="{theme["chrome"]}"><animate attributeName="stop-color" values="{theme["chrome"]};{theme["accent"]};{theme["violet2"]};{theme["chrome"]}" dur="10s" repeatCount="indefinite"/></stop>
  <stop offset="1" stop-color="{theme["accent"]}"><animate attributeName="stop-color" values="{theme["accent"]};{theme["violet2"]};{theme["chrome"]};{theme["accent"]}" dur="10s" repeatCount="indefinite"/></stop>
</linearGradient>
<linearGradient id="panelGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{theme["panel"]}"/><stop offset="1" stop-color="{theme["panel2"]}"/></linearGradient>
<filter id="glow8" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="8"/></filter>
<filter id="glow3" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="3"/></filter>
<filter id="txtGlow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="0.9" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<clipPath id="winClip"><rect x="2" y="2" width="1176" height="606" rx="18"/></clipPath>
<clipPath id="mapClip"><rect x="{FRAME_X}" y="{FRAME_Y}" width="{PANEL_W}" height="{PANEL_H}" rx="10"/></clipPath>
</defs>
<rect x="2" y="2" width="1176" height="606" rx="18" fill="{theme["bg"]}"/>
<g clip-path="url(#winClip)">
<rect x="2" y="2" width="1176" height="606" fill="url(#panelGrad)"/>
<rect x="2" y="2" width="1176" height="46" fill="{theme["bar"]}"/>
<line x1="2" y1="48" x2="1178" y2="48" stroke="{theme["hairline"]}"/>
<circle cx="30" cy="25.0" r="5.5" fill="#ff5f56"/>
<circle cx="50" cy="25.0" r="5.5" fill="#ffbd2e"/>
<circle cx="70" cy="25.0" r="5.5" fill="#27c93f"/>
<text x="590.0" y="29.0" text-anchor="middle" font-size="12" fill="{theme["muted"]}">{_xml_escape(PROFILE["email_title"])}</text>
<text x="38" y="74" font-size="10" letter-spacing="3" fill="{theme["dim"]}">VISUAL.MAP</text>
<rect x="{FRAME_X}" y="{FRAME_Y}" width="{PANEL_W}" height="{PANEL_H}" rx="10" fill="none" stroke="{theme["chrome"]}" stroke-width="2" opacity="0.45" filter="url(#glow3)"/>
<rect x="{FRAME_X}" y="{FRAME_Y}" width="{PANEL_W}" height="{PANEL_H}" rx="10" fill="{theme["panel"]}" stroke="{theme["frame_stroke"]}"/>
'''
    )

    # Portrait layers — clipped to frame, centered like arifhaxn
    parts.append(f'<g clip-path="url(#mapClip)">\n')

    # Intro assemble
    parts.append(
        f'<g transform="{pt}" fill="{theme["portrait"]}" shape-rendering="crispEdges">\n'
        f'<set attributeName="opacity" to="0" begin="{INTRO_END}s"/>\n'
    )
    for gi, group in enumerate(intro_groups):
        if not group:
            continue
        begin = 0.20 + (gi / N_INTRO_GROUPS) * 2.0
        gdots = np.zeros((GRID_H, GRID_W), dtype=bool)
        for x, y in group:
            xi, yi = int(x), int(y)
            if 0 <= xi < GRID_W and 0 <= yi < GRID_H:
                gdots[yi, xi] = True
        d = "".join(pack_runs(gdots))
        if not d:
            continue
        parts.append(
            f'<g opacity="0"><animate attributeName="opacity" values="0;1" dur="0.9s" begin="{begin:.2f}s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".4 0 .2 1"/><path d="{d}"/></g>\n'
        )
    parts.append("</g>\n")

    kt = "0;0.211;0.303;0.444;0.535;0.676;0.768;0.908;1"
    op_vals = "1;1;0;0;0;0;0;0;1"

    # Drift loop
    parts.append(
        f'<g transform="{pt}" fill="{theme["portrait"]}" shape-rendering="crispEdges" opacity="0">\n'
        f'<set attributeName="opacity" to="1" begin="{INTRO_END}s"/>\n'
    )
    for bi, band in enumerate(bands):
        if not band:
            continue
        arr = np.array(band)
        dx = (first_centroid[0] - arr[:, 0].mean()) * 0.42
        dy = (first_centroid[1] - arr[:, 1].mean()) * 0.42
        dx += (bi % 7 - 3) * 2.5
        dy += (bi % 5 - 2) * 2.5
        gdots = np.zeros((GRID_H, GRID_W), dtype=bool)
        for x, y in band:
            xi, yi = int(x), int(y)
            if 0 <= xi < GRID_W and 0 <= yi < GRID_H:
                gdots[yi, xi] = True
        d = "".join(pack_runs(gdots))
        if not d:
            continue
        tv = f"0 0;0 0;{dx:.1f} {dy:.1f};{dx:.1f} {dy:.1f};{dx * 0.3:.1f} {dy * 0.3:.1f};{dx * 0.3:.1f} {dy * 0.3:.1f};{-dx * 0.2:.1f} {-dy * 0.2:.1f};0 0;0 0"
        parts.append(
            f'''<g>
  <animate attributeName="opacity" values="{op_vals}" keyTimes="{kt}" dur="{LOOP_DUR}s" begin="{INTRO_END}s" repeatCount="indefinite" calcMode="linear"/>
  <animateTransform attributeName="transform" type="translate" values="{tv}" keyTimes="{kt}" dur="{LOOP_DUR}s" begin="{INTRO_END}s" repeatCount="indefinite" calcMode="linear"/>
  <path d="{d}"/>
</g>\n'''
        )
    parts.append("</g>\n")

    logo_op = [
        "0;0;0;1;1;0;0;0;0",
        "0;0;0;0;0;1;1;0;0",
        "0;0;0;0;0;0;0;1;0",
    ]
    parts.append(
        f'<g transform="{pt}" fill="{theme["chrome"]}" shape-rendering="crispEdges">\n'
    )
    for li, target in enumerate(logo_targets):
        d = path_from_points(target, size=2)
        if not d:
            continue
        parts.append(
            f'''<g opacity="0">
  <animate attributeName="opacity" values="{logo_op[li]}" keyTimes="{kt}" dur="{LOOP_DUR}s" begin="{INTRO_END}s" repeatCount="indefinite"/>
  <path d="{d}"/>
</g>\n'''
        )
    parts.append("</g>\n")
    parts.append("</g>\n")  # end mapClip

    # Corner brackets (arifhaxn style)
    c = theme["chrome"]
    parts.append(
        f'''<path d="M 50 84 L 36 84 L 36 98" fill="none" stroke="{c}" stroke-width="2" opacity="0.8"/>
<path d="M 422 84 L 436 84 L 436 98" fill="none" stroke="{c}" stroke-width="2" opacity="0.8"/>
<path d="M 50 576 L 36 576 L 36 562" fill="none" stroke="{c}" stroke-width="2" opacity="0.8"/>
<path d="M 422 576 L 436 576 L 436 562" fill="none" stroke="{c}" stroke-width="2" opacity="0.8"/>
'''
    )

    parts.append(info_rows_svg(theme))

    # Outer accent window border (glow + crisp)
    parts.append(
        f'''<rect x="3" y="3" width="1174" height="604" rx="17" fill="none" stroke="url(#accent)" stroke-width="3" opacity="0.55" filter="url(#glow8)"/>
<rect x="3" y="3" width="1174" height="604" rx="17" fill="none" stroke="url(#accent)" stroke-width="1.6"/>
'''
    )
    parts.append("</g>\n</svg>\n")
    return "".join(parts)


def main():
    print("Loading photo…", PHOTO)
    raw = Image.open(PHOTO).convert("RGB")
    print("Size:", raw.size)

    print("Removing background…")
    rgb, mask = remove_background(raw)
    print("Subject coverage:", float(mask.mean()))

    cropped, cmask = crop_head_shoulders(rgb, mask)
    print("Cropped:", cropped.size)

    debug = OUT_DIR / "scripts" / "debug"
    debug.mkdir(parents=True, exist_ok=True)
    cropped.save(debug / "crop.jpg")
    Image.fromarray((cmask.astype(np.uint8) * 255)).save(debug / "mask.png")

    for theme_name in ("dark", "light"):
        dark_mode = theme_name == "dark"
        dots, _ = prepare_dither(cropped, cmask, dark_mode=dark_mode)
        print(f"{theme_name} ink coverage:", float(dots.mean()))
        prev = np.zeros((GRID_H, GRID_W, 3), dtype=np.uint8)
        if dark_mode:
            prev[:, :] = (10, 16, 31)
            prev[dots] = (167, 139, 250)
        else:
            prev[:, :] = (255, 255, 255)
            prev[dots] = (124, 58, 237)
        Image.fromarray(prev).save(debug / f"dither_{theme_name}.png")

        svg = build_svg(theme_name, dots)
        out = OUT_DIR / f"{theme_name}.svg"
        out.write_text(svg, encoding="utf-8")
        print(f"Wrote {out} ({out.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
