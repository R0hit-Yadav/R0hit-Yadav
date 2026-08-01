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

## 5. Self-host GitHub stats (recommended)

The public `github-readme-stats.vercel.app` instance often rate-limits. Self-host:

1. Create a **classic PAT**: GitHub → Settings → Developer settings → Personal access tokens (classic) → `repo` scope → **copy once**
2. Fork [anuraghazra/github-readme-stats](https://github.com/anuraghazra/github-readme-stats)
3. Import the fork on [Vercel](https://vercel.com) (Hobby / free)
4. Add env var `PAT_1` = your token → Deploy
5. In `README.md`, replace every `https://github-readme-stats.vercel.app` with your instance URL (e.g. `https://github-readme-stats-xxxx.vercel.app`)

## 6. Regenerate the banner (optional)

Needs Python 3 + `pillow`, `numpy`, `scipy`, `rembg`:

```bash
python3 scripts/generate_banner.py
```

Source photo: `/home/rohit/Rohit/Work/GithubReadme/Rohit.jpg` (also copied to `assets/rohit.jpg`).

Edit identity rows in `scripts/generate_banner.py` → `PROFILE` dict, then re-run.

## Theme palette

| Role | Dark | Light |
|------|------|-------|
| Background | `#0A101F` | `#FFFFFF` |
| Portrait | `#A78BFA` | `#7C3AED` |
| Chrome | `#22D3EE` | `#0891B2` |
| Accent | `#10B981` | `#059669` |

## Cache tip

If GitHub shows an old banner after push, open:

`https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/dark.svg?v=2`

and hard-refresh. Camo CDN can lag a few minutes.
