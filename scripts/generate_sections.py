#!/usr/bin/env python3
"""
Generate the README section SVGs (dark + light), matching the banner palette:

  assets/chains-{dark,light}.svg  — LEDGER.TRACE: the chains I build on, drawn
                                    as linked blocks with a packet confirming
                                    each block in turn.
  assets/footer-{dark,light}.svg  — closing terminal line.

Run: python3 scripts/generate_sections.py   (stdlib only)
"""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

# (chain, stack, repo, dark colour, light colour)
BLOCKS = [
    ("Genesis/Rust", "Rust · Cargo · CLI", "Web3_Rust_X_Blockchain", "#F4A261", "#C2410C"),
    ("Solana", "Rust · Anchor · SPL", "Solana_Token", "#14F195", "#059669"),
    ("Aptos", "Move · Aptos CLI", "Move_Aptos", "#5EEAD4", "#0D9488"),
    ("Ethereum", "Solidity · Foundry", "DAO_Voting_System", "#8EA2FF", "#4F46E5"),
    ("Stellar", "Soroban · Rust · TS", "Soroban_Integration", "#7DD3FC", "#0284C7"),
    ("Bitcoin", "MIT Bitcoin '25", "MIT_BITCOIN-2025", "#F7931A", "#D97706"),
]

THEMES = {
    "dark": dict(panel="#0A101F", card="#0C1426", bar="#0B1222", chrome="#22D3EE", violet="#A78BFA",
                 accent="#10B981", text="#F8FAFC", muted="#94A3B8", dim="#475569",
                 stroke="rgba(34,211,238,0.28)", hair="rgba(255,255,255,0.08)"),
    "light": dict(panel="#FFFFFF", card="#F8FAFC", bar="#F1F5F9", chrome="#0891B2", violet="#7C3AED",
                  accent="#059669", text="#0F172A", muted="#475569", dim="#94A3B8",
                  stroke="rgba(8,145,178,0.30)", hair="rgba(0,0,0,0.08)"),
}


def h(s: str) -> str:
    d = hashlib.sha256(s.encode()).hexdigest()
    return f"0x{d[:4]}…{d[-4:]}"


def chains_svg(name: str) -> str:
    t = THEMES[name]
    W, H = 1180, 232
    n = len(BLOCKS)
    gap = 22
    bw = (W - 10 - gap * (n - 1)) / n
    by, bh = 44, 170
    step = 1.1                     # s per block confirmation
    cycle = step * n + 1.4
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}" role="img" aria-label="Chains I build on">',
         '<defs><filter id="g" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="4"/></filter></defs>']
    o.append(f'<text x="6" y="24" font-size="11" letter-spacing="3" fill="{t["chrome"]}">LEDGER.TRACE</text>'
             f'<text x="128" y="24" font-size="11" fill="{t["dim"]}">./chains.sh --verify</text>'
             f'<line x1="300" y1="20" x2="{W - 150}" y2="20" stroke="{t["hair"]}"/>'
             f'<text x="{W - 6}" y="24" text-anchor="end" font-size="11" fill="{t["accent"]}">&#9679; {n} blocks synced'
             f'<animate attributeName="opacity" values="1;.35;1" dur="2s" repeatCount="indefinite"/></text>')
    prev = "0x0000…0000"
    for i, (chain, stack, repo, cd, cl) in enumerate(BLOCKS):
        c = cd if name == "dark" else cl
        x = 5 + i * (bw + gap)
        on = i * step / cycle
        kt = f"0;{on:.3f};{min(on + 0.06, 1):.3f};{min(on + step / cycle, 1):.3f};1"
        # link to next block with travelling packet
        if i < n - 1:
            lx1, lx2, ly = x + bw, x + bw + gap, by + bh / 2
            o.append(f'<line x1="{lx1:.1f}" y1="{ly}" x2="{lx2:.1f}" y2="{ly}" stroke="{t["chrome"]}" stroke-width="1.5" stroke-dasharray="3 3" opacity=".6">'
                     f'<animate attributeName="stroke-dashoffset" values="6;0" dur="0.6s" repeatCount="indefinite"/></line>')
            pb = (i + 0.75) * step
            o.append(f'<circle r="3" cy="{ly}" fill="{t["chrome"]}" opacity="0">'
                     f'<animate attributeName="cx" values="{lx1:.1f};{lx2:.1f}" dur="{step * 0.35:.2f}s" begin="{pb:.2f}s;{pb:.2f}s+{cycle:.2f}s" fill="freeze"/>'
                     f'<animate attributeName="opacity" values="0;1;1;0" dur="{step * 0.35:.2f}s" begin="{pb:.2f}s;{pb:.2f}s+{cycle:.2f}s"/></circle>')
        # card
        o.append(f'<g>')
        o.append(f'<rect x="{x:.1f}" y="{by}" width="{bw:.1f}" height="{bh}" rx="10" fill="{c}" opacity="0" filter="url(#g)">'
                 f'<animate attributeName="opacity" values="0;0;.35;0;0" keyTimes="{kt}" dur="{cycle:.2f}s" repeatCount="indefinite"/></rect>')
        o.append(f'<rect x="{x:.1f}" y="{by}" width="{bw:.1f}" height="{bh}" rx="10" fill="{t["card"]}" stroke="{t["stroke"]}"/>')
        o.append(f'<rect x="{x:.1f}" y="{by}" width="{bw:.1f}" height="{bh}" rx="10" fill="none" stroke="{c}" stroke-width="1.4" opacity="0">'
                 f'<animate attributeName="opacity" values="0;0;1;.25;.25" keyTimes="{kt}" dur="{cycle:.2f}s" repeatCount="indefinite"/></rect>')
        o.append(f'<path d="M{x:.1f} {by + 26}h{bw:.1f}" stroke="{t["hair"]}"/>')
        o.append(f'<text x="{x + 12:.1f}" y="{by + 17}" font-size="10" letter-spacing="1.5" fill="{t["dim"]}">BLOCK #{i:02d}</text>')
        o.append(f'<circle cx="{x + bw - 14:.1f}" cy="{by + 13}" r="3.5" fill="{t["dim"]}"><animate attributeName="fill" values="{t["dim"]};{t["dim"]};{t["accent"]};{t["accent"]};{t["accent"]}" keyTimes="{kt}" dur="{cycle:.2f}s" repeatCount="indefinite"/></circle>')
        o.append(f'<text x="{x + 12:.1f}" y="{by + 56}" font-size="17" font-weight="700" fill="{c}">{chain}</text>')
        o.append(f'<text x="{x + 12:.1f}" y="{by + 78}" font-size="11" fill="{t["muted"]}">{stack}</text>')
        o.append(f'<text x="{x + 12:.1f}" y="{by + 104}" font-size="10" fill="{t["dim"]}">repo</text>'
                 f'<text x="{x + 12:.1f}" y="{by + 118}" font-size="10.5" fill="{t["text"]}" textLength="{min(len(repo) * 6.3, bw - 24):.0f}" lengthAdjust="spacingAndGlyphs">{repo}</text>')
        cur = h(chain + repo)
        o.append(f'<text x="{x + 12:.1f}" y="{by + 142}" font-size="9.5" fill="{t["dim"]}">prev <tspan fill="{t["muted"]}">{prev}</tspan></text>'
                 f'<text x="{x + 12:.1f}" y="{by + 157}" font-size="9.5" fill="{t["dim"]}">hash <tspan fill="{c}">{cur}</tspan></text>')
        prev = cur
        o.append('</g>')
    o.append('</svg>')
    return "\n".join(o)


def footer_svg(name: str) -> str:
    t = THEMES[name]
    W, H = 1180, 70
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}" role="img" aria-label="Thanks for visiting">
<defs><linearGradient id="l" x1="0" x2="1"><stop offset="0" stop-color="{t["violet"]}" stop-opacity="0"/><stop offset=".5" stop-color="{t["chrome"]}"/><stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/>
<animate attributeName="x1" values="-1;1" dur="5s" repeatCount="indefinite"/><animate attributeName="x2" values="0;2" dur="5s" repeatCount="indefinite"/></linearGradient></defs>
<line x1="0" y1="12" x2="{W}" y2="12" stroke="url(#l)" stroke-width="1.5"/>
<text x="{W / 2}" y="46" text-anchor="middle" font-size="14" fill="{t["muted"]}"><tspan fill="{t["accent"]}">&#10003;</tspan> tx confirmed <tspan fill="{t["dim"]}">·</tspan> thanks for stopping by <tspan fill="{t["dim"]}">·</tspan> <tspan fill="{t["chrome"]}">gm</tspan> <tspan fill="{t["chrome"]}">&#9608;<animate attributeName="fill-opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></tspan></text>
</svg>
'''


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for name in THEMES:
        (OUT / f"chains-{name}.svg").write_text(chains_svg(name), encoding="utf-8")
        (OUT / f"footer-{name}.svg").write_text(footer_svg(name), encoding="utf-8")
    print("wrote chains-*.svg, footer-*.svg")


if __name__ == "__main__":
    main()
