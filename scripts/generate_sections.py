#!/usr/bin/env python3
"""
Generate the README section SVGs (dark + light), matching the banner palette:

  assets/chains-header-*.svg + assets/chains/<i>-<theme>.svg
                                  — LEDGER.TRACE: the chains I build on, one
                                    image per block so each links to its repo.
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


STEP = 1.1                        # s per block confirmation
CYCLE = STEP * len(BLOCKS) + 1.4
GAP, BW, BH, PAD = 22, 174, 170, 8  # each tile = block + its outgoing link
TW, TH = BW + GAP, BH + 2 * PAD


def chains_header(name: str) -> str:
    t = THEMES[name]
    W, H = 1180, 34
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}" role="img" aria-label="Chains I build on">'
            f'<text x="6" y="22" font-size="11" letter-spacing="3" fill="{t["chrome"]}">LEDGER.TRACE</text>'
            f'<text x="128" y="22" font-size="11" fill="{t["dim"]}">./chains.sh --verify · click a block to open its repo</text>'
            f'<line x1="500" y1="18" x2="{W - 150}" y2="18" stroke="{t["hair"]}"/>'
            f'<text x="{W - 6}" y="22" text-anchor="end" font-size="11" fill="{t["accent"]}">&#9679; {len(BLOCKS)} blocks synced'
            f'<animate attributeName="opacity" values="1;.35;1" dur="2s" repeatCount="indefinite"/></text></svg>\n')


def chain_tile(name: str, i: int) -> str:
    """One block as its own image so the README can wrap each in a repo link."""
    t = THEMES[name]
    chain, stack, repo, cd, cl = BLOCKS[i]
    c = cd if name == "dark" else cl
    prev = h(BLOCKS[i - 1][0] + BLOCKS[i - 1][2]) if i else "0x0000…0000"
    x, by, bw, bh = 2, PAD, BW, BH
    on = i * STEP / CYCLE
    kt = f"0;{on:.3f};{min(on + 0.06, 1):.3f};{min(on + STEP / CYCLE, 1):.3f};1"
    anim = f'keyTimes="{kt}" dur="{CYCLE:.2f}s" repeatCount="indefinite"'
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{TW}" height="{TH}" viewBox="0 0 {TW} {TH}" font-family="{FONT}" role="img" aria-label="{chain} — {repo}">',
         '<defs><filter id="g" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="4"/></filter></defs>']
    if i < len(BLOCKS) - 1:   # link to the next block with a travelling packet
        lx1, lx2, ly = x + bw, TW, by + bh / 2
        pb = (i + 0.75) * STEP
        o.append(f'<line x1="{lx1}" y1="{ly}" x2="{lx2}" y2="{ly}" stroke="{t["chrome"]}" stroke-width="1.5" stroke-dasharray="3 3" opacity=".6">'
                 f'<animate attributeName="stroke-dashoffset" values="6;0" dur="0.6s" repeatCount="indefinite"/></line>')
        o.append(f'<circle r="3" cx="{lx1}" cy="{ly}" fill="{t["chrome"]}" opacity="0">'
                 f'<animate attributeName="cx" values="{lx1};{lx2}" dur="{STEP * 0.35:.2f}s" begin="{pb:.2f}s;{pb:.2f}s+{CYCLE:.2f}s" fill="freeze"/>'
                 f'<animate attributeName="opacity" values="0;1;1;0" dur="{STEP * 0.35:.2f}s" begin="{pb:.2f}s;{pb:.2f}s+{CYCLE:.2f}s"/></circle>')
    o.append(f'<rect x="{x}" y="{by}" width="{bw}" height="{bh}" rx="10" fill="{c}" opacity="0" filter="url(#g)">'
             f'<animate attributeName="opacity" values="0;0;.35;0;0" {anim}/></rect>')
    o.append(f'<rect x="{x}" y="{by}" width="{bw}" height="{bh}" rx="10" fill="{t["card"]}" stroke="{t["stroke"]}"/>')
    o.append(f'<rect x="{x}" y="{by}" width="{bw}" height="{bh}" rx="10" fill="none" stroke="{c}" stroke-width="1.4" opacity="0">'
             f'<animate attributeName="opacity" values="0;0;1;.25;.25" {anim}/></rect>')
    o.append(f'<path d="M{x} {by + 26}h{bw}" stroke="{t["hair"]}"/>')
    o.append(f'<text x="{x + 12}" y="{by + 17}" font-size="10" letter-spacing="1.5" fill="{t["dim"]}">BLOCK #{i:02d}</text>')
    o.append(f'<circle cx="{x + bw - 14}" cy="{by + 13}" r="3.5" fill="{t["dim"]}"><animate attributeName="fill" values="{t["dim"]};{t["dim"]};{t["accent"]};{t["accent"]};{t["accent"]}" {anim}/></circle>')
    o.append(f'<text x="{x + 12}" y="{by + 56}" font-size="17" font-weight="700" fill="{c}">{chain}</text>')
    o.append(f'<text x="{x + 12}" y="{by + 78}" font-size="11" fill="{t["muted"]}">{stack}</text>')
    o.append(f'<text x="{x + 12}" y="{by + 104}" font-size="10" fill="{t["dim"]}">repo <tspan fill="{t["chrome"]}">&#8599;</tspan></text>'
             f'<text x="{x + 12}" y="{by + 118}" font-size="10.5" fill="{t["text"]}" textLength="{min(len(repo) * 6.3, bw - 24):.0f}" lengthAdjust="spacingAndGlyphs">{repo}</text>')
    o.append(f'<text x="{x + 12}" y="{by + 142}" font-size="9.5" fill="{t["dim"]}">prev <tspan fill="{t["muted"]}">{prev}</tspan></text>'
             f'<text x="{x + 12}" y="{by + 157}" font-size="9.5" fill="{t["dim"]}">hash <tspan fill="{c}">{h(chain + repo)}</tspan></text>')
    o.append('</svg>\n')
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
    (OUT / "chains").mkdir(parents=True, exist_ok=True)
    for name in THEMES:
        (OUT / f"chains-header-{name}.svg").write_text(chains_header(name), encoding="utf-8")
        for i in range(len(BLOCKS)):
            (OUT / "chains" / f"{i}-{name}.svg").write_text(chain_tile(name, i), encoding="utf-8")
        (OUT / f"footer-{name}.svg").write_text(footer_svg(name), encoding="utf-8")
    print("wrote chains-header-*.svg, chains/*.svg, footer-*.svg")


if __name__ == "__main__":
    main()
