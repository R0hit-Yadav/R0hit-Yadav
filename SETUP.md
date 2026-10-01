# GitHub Profile Setup — Rohit Yadav

Your profile README is ready in this repo (`R0hit-Yadav/R0hit-Yadav`). Follow these steps after you push.

## 1. Push this repo

```bash
cd R0hit-Yadav
git add -A
git commit -m "feat: animated terminal profile with dithered banner"
git push -u origin main
```

Visit: https://github.com/R0hit-Yadav

## 2. Enable Actions write permission

1. Repo **Settings → Actions → General**
2. **Workflow permissions → Read and write permissions**
3. Save

## 3. Run the snake workflow

1. **Actions → Generate Snake Animation → Run workflow**
2. Wait for green ✓
3. Confirm an `output` branch exists with `snake-dark.svg` / `snake-light.svg`
4. Refresh your profile — the snake section appears

## 4. Run the projects workflow (optional live stars)

1. **Actions → Generate Projects Panel → Run workflow**
2. Creates/updates the `projects` branch

Edit featured projects anytime in `projects.json` (order = display order). Logos live in `logos/`.

The Action also writes one image per project to `cards/<repo>.svg` on the `projects` branch, so each card in the README is its own clickable link. **When you add or remove a project in `projects.json`, add or remove its `<a href=…><picture>…</picture></a>` row in the PROJECTS section of `README.md` too.**

Note: GitHub strips `target="_blank"` from README links, so links open in the same tab. Ctrl/⌘-click or middle-click opens a new tab.

## 5. Self-host GitHub stats (recommended)

The public `github-readme-stats.vercel.app` instance often rate-limits. Self-host:

1. Create a **classic PAT**: GitHub → Settings → Developer settings → Personal access tokens (classic) → `repo` scope → **copy once**
2. Fork [anuraghazra/github-readme-stats](https://github.com/anuraghazra/github-readme-stats)
3. Import the fork on [Vercel](https://vercel.com) (Hobby / free)
4. Add env var `PAT_1` = your token → Deploy
5. In `README.md`, replace every `https://github-readme-stats.vercel.app` with your instance URL (e.g. `https://github-readme-stats-xxxx.vercel.app`)

## 6. Regenerate the banner & sections (optional)

Banner (needs Python 3 + `pillow numpy scipy`, optional `rembg` for background removal):

```bash
python3 scripts/generate_banner.py     # -> dark.svg / light.svg
python3 scripts/generate_sections.py   # -> assets/chains-*.svg, assets/footer-*.svg (stdlib only)
```

- Portrait source: `assets/rohit_professional.png`; morph logos: `assets/morph/` (Solana is drawn from geometry).
- Edit SYSTEM.INFO rows in `PROFILE` and the morph timing (`HOLDS`, `TRAVEL`) at the top of `generate_banner.py`.
- Edit the chain blocks in `BLOCKS` at the top of `generate_sections.py`.
- After regenerating, bump `?v=` on the banner URLs in `README.md` so GitHub's image cache refreshes.
- Debug previews of every dithered shape land in `scripts/debug/` (git-ignored).

## Theme palette

| Role | Dark | Light |
|------|------|-------|
| Background | `#0A101F` | `#FFFFFF` |
| Portrait | `#A78BFA` | `#6D28D9` |
| Bitcoin / Ethereum / Solana | `#F7931A` / `#8EA2FF` / `#9945FF→#14F195` | `#D97706` / `#4F46E5` / `#7C3AED→#059669` |
| Chrome | `#22D3EE` | `#0891B2` |
| Accent | `#10B981` | `#059669` |

## Cache tip

If GitHub shows an old banner after push, open:

`https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/dark.svg?v=3`

and hard-refresh. Camo CDN can lag a few minutes.
