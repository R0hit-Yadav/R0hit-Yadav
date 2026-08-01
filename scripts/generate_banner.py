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
ASSETS = Path("/home/rohit/Rohit/Work/GithubReadme")
PHOTO = ASSETS / "Rohit_professional.png"
OUT_DIR = ROOT

# Morph logos (dithered) — Bitcoin → ETH → NFT particle cycle
LOGO_IMAGES = [
    ASSETS / "Bitoin-new.png",  # clean Bitcoin logo
    ASSETS / "ETH.png",
    ASSETS / "NFT.png",
]
# Portrait grid — match arifhaxn frame math exactly
# Frame: x=36,y=84 w=400 h=492 · portrait translate(50,86) scale(1.24,1.4471)
# → 300*1.24=372 wide (14px side inset) · 340*1.4471≈492 tall (flush)
GRID_W, GRID_H = 300, 340
PANEL_W, PANEL_H = 400, 492
SCALE_X = 1.2400
SCALE_Y = 1.4471
PORTRAIT_TX, PORTRAIT_TY = 50, 86
FRAME_X, FRAME_Y = 36, 84

# Timing
INTRO_END = 3.2
LOOP_DUR = 14.2

N_INTRO_GROUPS = 60
N_DRIFT_BANDS = 94
N_TRAVELLERS = 1100
N_MORPH_GROUPS = 140  # particle clusters that fly between shapes

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


def dither_logo_image(path: Path, canvas_w: int = GRID_W, canvas_h: int = GRID_H) -> np.ndarray:
    """
    Convert a logo into a centered dithered point cloud on the portrait grid.
    Fits with margin so tall logos (ETH diamond) are never clipped.
    """
    from scipy import ndimage

    im = Image.open(path)
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        rgba = im.convert("RGBA")
        bg = Image.new("RGBA", rgba.size, (0, 0, 0, 255))
        im = Image.alpha_composite(bg, rgba).convert("RGB")
    else:
        im = im.convert("RGB")

    arr = np.asarray(im).astype(np.float32)
    lum = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    # Keep bright ink + vivid orange (Bitcoin) + teal accents
    orange = (r > 140) & (g > 60) & (g < 180) & (b < 100)
    teal = (b > 80) & (g > 60) & (b + g > r + 40)
    content = (lum > 22) | orange | teal

    content = ndimage.binary_closing(content, iterations=2)
    content = ndimage.binary_fill_holes(content)
    labeled, n = ndimage.label(content)
    if n:
        sizes = ndimage.sum(content, labeled, range(1, n + 1))
        content = labeled == (int(np.argmax(sizes)) + 1)

    ys, xs = np.where(content)
    if len(xs) < 50:
        x0, x1, y0, y1 = 0, arr.shape[1], 0, arr.shape[0]
    else:
        pad = 12
        x0 = max(0, int(xs.min()) - pad)
        x1 = min(arr.shape[1], int(xs.max()) + pad + 1)
        y0 = max(0, int(ys.min()) - pad)
        y1 = min(arr.shape[0], int(ys.max()) + pad + 1)

    crop = im.crop((x0, y0, x1, y1))
    # Leave ~18% margin so logos never clip the VISUAL.MAP frame
    max_w, max_h = int(canvas_w * 0.70), int(canvas_h * 0.70)
    tw, th = crop.size
    scale = min(max_w / tw, max_h / th)
    nw, nh = max(1, int(tw * scale)), max(1, int(th * scale))
    crop = crop.resize((nw, nh), Image.Resampling.LANCZOS)

    g = ImageOps.grayscale(crop)
    g = ImageOps.autocontrast(g, cutoff=2)
    g = ImageEnhance.Contrast(g).enhance(1.6)
    g = g.filter(ImageFilter.UnsharpMask(radius=2, percent=130, threshold=2))
    gray = np.asarray(g).astype(np.float32)

    target = np.clip((255.0 - gray) * 1.2, 0, 255)
    dots = floyd_steinberg(target)

    canvas = np.zeros((canvas_h, canvas_w), dtype=bool)
    ox = (canvas_w - nw) // 2
    oy = (canvas_h - nh) // 2
    canvas[oy : oy + nh, ox : ox + nw] = dots
    return dots_to_coords(canvas)


def logo_shapes() -> list[np.ndarray]:
    """Dithered morph targets: Bitcoin → ETH → NFT."""
    logos = []
    for path in LOGO_IMAGES:
        if not path.exists():
            print(f"[warn] missing logo image: {path}")
            continue
        pts = dither_logo_image(path)
        print(f"  logo {path.name}: {len(pts)} dots")
        debug = OUT_DIR / "scripts" / "debug"
        debug.mkdir(parents=True, exist_ok=True)
        prev = np.zeros((GRID_H, GRID_W, 3), dtype=np.uint8)
        prev[:, :] = (10, 16, 31)
        for x, y in pts.astype(int):
            if 0 <= x < GRID_W and 0 <= y < GRID_H:
                prev[y, x] = (34, 211, 238)
        Image.fromarray(prev).save(debug / f"logo_{path.stem}.png")
        logos.append(pts)
    if not logos:
        raise RuntimeError("No logo images found to dither")
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

    indices = list(range(len(coords)))
    RNG.shuffle(indices)
    intro_groups = [[] for _ in range(N_INTRO_GROUPS)]
    for i, idx in enumerate(indices):
        intro_groups[i % N_INTRO_GROUPS].append(coords[idx])

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
        port_pts = coords[t_idx].copy()
    else:
        port_pts = sample_points(coords, N_TRAVELLERS)

    stages = [port_pts]
    cur = port_pts
    for lg in logos:
        matched = optimal_transport_match(cur, sample_points(lg, N_TRAVELLERS))
        stages.append(matched)
        cur = matched
    stages.append(optimal_transport_match(cur, port_pts))

    order_m = np.argsort(port_pts[:, 0] + port_pts[:, 1] * 0.7 + NP_RNG.normal(0, 8, len(port_pts)))
    morph_groups: list[list[int]] = [[] for _ in range(N_MORPH_GROUPS)]
    for i, idx in enumerate(order_m):
        morph_groups[i % N_MORPH_GROUPS].append(int(idx))

    pt = portrait_transform()
    parts: list[str] = []

    svg_head = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="610" viewBox="0 0 1180 610" '
        'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,\'Liberation Mono\',monospace" '
        'role="img" aria-label="Rohit Yadav — profile.sh --live">',
        '<defs>',
        f'<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">',
        f'  <stop offset="0" stop-color="{theme["violet2"]}"><animate attributeName="stop-color" values="{theme["violet2"]};{theme["chrome"]};{theme["accent"]};{theme["violet2"]}" dur="10s" repeatCount="indefinite"/></stop>',
        f'  <stop offset="0.5" stop-color="{theme["chrome"]}"><animate attributeName="stop-color" values="{theme["chrome"]};{theme["accent"]};{theme["violet2"]};{theme["chrome"]}" dur="10s" repeatCount="indefinite"/></stop>',
        f'  <stop offset="1" stop-color="{theme["accent"]}"><animate attributeName="stop-color" values="{theme["accent"]};{theme["violet2"]};{theme["chrome"]};{theme["accent"]}" dur="10s" repeatCount="indefinite"/></stop>',
        '</linearGradient>',
        f'<linearGradient id="panelGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{theme["panel"]}"/><stop offset="1" stop-color="{theme["panel2"]}"/></linearGradient>',
        '<filter id="glow8" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="8"/></filter>',
        '<filter id="glow3" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="3"/></filter>',
        '<filter id="txtGlow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="0.9" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
        '<clipPath id="winClip"><rect x="2" y="2" width="1176" height="606" rx="18"/></clipPath>',
        f'<clipPath id="mapClip"><rect x="{FRAME_X}" y="{FRAME_Y}" width="{PANEL_W}" height="{PANEL_H}" rx="10"/></clipPath>',
        '</defs>',
        f'<rect x="2" y="2" width="1176" height="606" rx="18" fill="{theme["bg"]}"/>',
        '<g clip-path="url(#winClip)">',
        '<rect x="2" y="2" width="1176" height="606" fill="url(#panelGrad)"/>',
        f'<rect x="2" y="2" width="1176" height="46" fill="{theme["bar"]}"/>',
        f'<line x1="2" y1="48" x2="1178" y2="48" stroke="{theme["hairline"]}"/>',
        '<circle cx="30" cy="25.0" r="5.5" fill="#ff5f56"/>',
        '<circle cx="50" cy="25.0" r="5.5" fill="#ffbd2e"/>',
        '<circle cx="70" cy="25.0" r="5.5" fill="#27c93f"/>',
        f'<text x="590.0" y="29.0" text-anchor="middle" font-size="12" fill="{theme["muted"]}">{_xml_escape(PROFILE["email_title"])}</text>',
        f'<text x="38" y="74" font-size="10" letter-spacing="3" fill="{theme["dim"]}">VISUAL.MAP</text>',
        f'<rect x="{FRAME_X}" y="{FRAME_Y}" width="{PANEL_W}" height="{PANEL_H}" rx="10" fill="none" stroke="{theme["chrome"]}" stroke-width="2" opacity="0.45" filter="url(#glow3)"/>',
        f'<rect x="{FRAME_X}" y="{FRAME_Y}" width="{PANEL_W}" height="{PANEL_H}" rx="10" fill="{theme["panel"]}" stroke="{theme["frame_stroke"]}"/>',
    ]
    parts.append("\n".join(svg_head) + "\n")
    parts.append('<g clip-path="url(#mapClip)">\n')

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

    kt = "0;0.183;0.275;0.394;0.486;0.606;0.697;0.817;0.908;1"
    port_op = "1;1;0;0;0;0;0;0;0;1"
    splines9 = ";".join([".4 0 .2 1"] * 9)

    parts.append(
        f'<g transform="{pt}" fill="{theme["portrait"]}" shape-rendering="crispEdges" opacity="0">\n'
        f'<set attributeName="opacity" to="1" begin="{INTRO_END}s"/>\n'
    )
    for bi, band in enumerate(bands):
        if not band:
            continue
        arr = np.array(band)
        dx = (first_centroid[0] - arr[:, 0].mean()) * 0.55
        dy = (first_centroid[1] - arr[:, 1].mean()) * 0.55
        dx += (bi % 7 - 3) * 3.0
        dy += (bi % 5 - 2) * 3.0
        gdots = np.zeros((GRID_H, GRID_W), dtype=bool)
        for x, y in band:
            xi, yi = int(x), int(y)
            if 0 <= xi < GRID_W and 0 <= yi < GRID_H:
                gdots[yi, xi] = True
        d = "".join(pack_runs(gdots))
        if not d:
            continue
        tv = (
            f"0 0;0 0;{dx:.1f} {dy:.1f};{dx*1.25:.1f} {dy*1.25:.1f};"
            f"{dx*1.25:.1f} {dy*1.25:.1f};{dx*1.25:.1f} {dy*1.25:.1f};"
            f"{dx*1.25:.1f} {dy*1.25:.1f};{dx*1.25:.1f} {dy*1.25:.1f};0 0;0 0"
        )
        parts.append(
            f'<g>\n'
            f'  <animate attributeName="opacity" values="{port_op}" keyTimes="{kt}" dur="{LOOP_DUR}s" begin="{INTRO_END}s" repeatCount="indefinite" calcMode="linear"/>\n'
            f'  <animateTransform attributeName="transform" type="translate" values="{tv}" keyTimes="{kt}" dur="{LOOP_DUR}s" begin="{INTRO_END}s" repeatCount="indefinite" calcMode="spline" keySplines="{splines9}"/>\n'
            f'  <path d="{d}"/>\n'
            f'</g>\n'
        )
    parts.append("</g>\n")

    logo_hold_op = [
        "0;0;0.25;1;0.25;0;0;0;0;0",
        "0;0;0;0;0.25;1;0.25;0;0;0",
        "0;0;0;0;0;0;0.25;1;0.25;0",
    ]
    parts.append(f'<g transform="{pt}" fill="{theme["chrome"]}" shape-rendering="crispEdges">\n')
    for li, lg in enumerate(logos):
        d = path_from_points(lg, size=1)
        if not d:
            continue
        parts.append(
            f'<g opacity="0">\n'
            f'  <animate attributeName="opacity" values="{logo_hold_op[li]}" keyTimes="{kt}" dur="{LOOP_DUR}s" begin="{INTRO_END}s" repeatCount="indefinite"/>\n'
            f'  <path d="{d}"/>\n'
            f'</g>\n'
        )
    parts.append("</g>\n")

    swarm_op = "0;0;1;1;1;1;1;1;0.35;0"
    morph_splines = ";".join([".42 0 .58 1", ".35 0 .25 1"] * 4 + [".42 0 .58 1"])
    parts.append(f'<g transform="{pt}" fill="{theme["chrome"]}" shape-rendering="crispEdges">\n')
    for gi, members in enumerate(morph_groups):
        if len(members) < 2:
            continue
        base = stages[0][members].mean(axis=0)
        rel = stages[0][members] - base
        gdots = np.zeros((28, 28), dtype=bool)
        for x, y in rel:
            xi, yi = int(round(x + 14)), int(round(y + 14))
            if 0 <= xi < 27 and 0 <= yi < 27:
                gdots[yi:yi + 2, xi:xi + 2] = True
        local_path = "".join(pack_runs(gdots)) or "M13 13h2v2h-2z"

        cents = [st[members].mean(axis=0) for st in stages]
        seq = [cents[0], cents[0], cents[1], cents[1], cents[2], cents[2], cents[3], cents[3], cents[4], cents[4]]
        scatter = (gi % 11 - 5) * 3.2
        scatter_y = ((gi * 5) % 9 - 4) * 2.6
        tv_parts = []
        for ki, c in enumerate(seq):
            x, y = float(c[0] - 14), float(c[1] - 14)
            if ki == 1:
                x += scatter * 0.55
                y += scatter_y * 0.55
            elif ki in (2, 4, 6, 8):
                x += scatter * 0.15
                y += scatter_y * 0.15
            tv_parts.append(f"{x:.1f} {y:.1f}")
        tv = ";".join(tv_parts)
        delay = (gi % 14) * 0.025
        x0, y0 = float(seq[0][0] - 14), float(seq[0][1] - 14)
        parts.append(
            f'<g opacity="0" transform="translate({x0:.1f} {y0:.1f})">\n'
            f'  <animate attributeName="opacity" values="{swarm_op}" keyTimes="{kt}" dur="{LOOP_DUR}s" begin="{INTRO_END + delay:.2f}s" repeatCount="indefinite"/>\n'
            f'  <animateTransform attributeName="transform" type="translate" values="{tv}" keyTimes="{kt}" dur="{LOOP_DUR}s" begin="{INTRO_END + delay:.2f}s" repeatCount="indefinite" calcMode="spline" keySplines="{morph_splines}"/>\n'
            f'  <path d="{local_path}"/>\n'
            f'</g>\n'
        )
    parts.append("</g>\n</g>\n")

    c = theme["chrome"]
    parts.append(
        f'<path d="M 50 84 L 36 84 L 36 98" fill="none" stroke="{c}" stroke-width="2" opacity="0.8"/>\n'
        f'<path d="M 422 84 L 436 84 L 436 98" fill="none" stroke="{c}" stroke-width="2" opacity="0.8"/>\n'
        f'<path d="M 50 576 L 36 576 L 36 562" fill="none" stroke="{c}" stroke-width="2" opacity="0.8"/>\n'
        f'<path d="M 422 576 L 436 576 L 436 562" fill="none" stroke="{c}" stroke-width="2" opacity="0.8"/>\n'
    )
    parts.append(info_rows_svg(theme))
    parts.append(
        '<rect x="3" y="3" width="1174" height="604" rx="17" fill="none" stroke="url(#accent)" stroke-width="3" opacity="0.55" filter="url(#glow8)"/>\n'
        '<rect x="3" y="3" width="1174" height="604" rx="17" fill="none" stroke="url(#accent)" stroke-width="1.6"/>\n'
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
