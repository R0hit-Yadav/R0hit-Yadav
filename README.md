<!-- ============================== HERO ============================== -->
<!-- Animated banner: portrait → Bitcoin → Ethereum → Solana particle morph.
     Regenerate with scripts/generate_banner.py. Bump ?v= after regenerating to bust GitHub's image cache. -->

<a href="https://github.com/R0hit-Yadav">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/dark.svg?v=3">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/light.svg?v=3">
  <img width="100%" alt="Rohit Yadav — Rust Blockchain Developer" src="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/dark.svg?v=3">
</picture>
</a>

<!-- ============================== ABOUT ============================== -->

<p align="center"><code>~/about.rs</code></p>

```rust
use chains::{Solana, Aptos, Ethereum, Stellar, Bitcoin};

#[derive(Builder, OnChain)]
pub struct Rohit {
    role:       &'static str,
    based_in:   &'static str,
    writes:     [&'static str; 4],
    ships_on:   [&'static str; 5],
    hackathons: [&'static str; 4],
}

impl Rohit {
    pub fn new() -> Self {
        Self {
            role:       "Rust Blockchain Developer",
            based_in:   "Ahmedabad, India 🇮🇳",
            writes:     ["Rust", "Move", "Solidity", "TypeScript"],
            ships_on:   ["Solana", "Aptos", "EVM", "Soroban", "Bitcoin"],
            hackathons: ["IIT Kanpur '25", "MIT Bitcoin '25", "AMD '25", "Odoo Combat '24"],
        }
    }

    /// what I'm doing right now
    pub fn status(&self) -> Result<&str, Infinite> {
        Ok("building + shipping on-chain 🦀⛓️")
    }
}
```

<!-- ============================== CHAINS ============================== -->

<br/>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/assets/chains-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/assets/chains-light.svg">
  <img width="100%" alt="Chains I build on: Rust, Solana, Aptos, Ethereum, Stellar, Bitcoin" src="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/assets/chains-dark.svg">
</picture>

<!-- ============================== STACK ============================== -->

<br/>
<p align="center"><code>STACK.INSTALLED</code></p>
<p align="center">
  <img src="https://skillicons.dev/icons?i=rust,solidity,ts,js,react,nodejs,py,docker,aws,git,linux,vscode&perline=12" alt="Rust, Solidity, TypeScript, JavaScript, React, Node.js, Python, Docker, AWS, Git, Linux, VS Code" />
</p>

<!-- ============================== PROJECTS ============================== -->
<!-- Live panel: rebuilt every 6h by .github/workflows/projects.yml onto the `projects` branch. Edit projects.json to change it. -->

<br/>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/projects/projects.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/projects/projects-light.svg">
  <img width="100%" alt="Featured projects" src="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/projects/projects.svg">
</picture>

<!-- ============================== STATS ============================== -->

<br/>
<p align="center"><code>NODE.METRICS</code></p>

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://streak-stats.demolab.com/?user=R0hit-Yadav&hide_border=true&background=0A101F&stroke=22D3EE&ring=A78BFA&fire=10B981&currStreakLabel=22D3EE&sideLabels=94A3B8&currStreakNum=F8FAFC&sideNums=F8FAFC&dates=64748B&card_width=1180" />
  <img width="100%" alt="Contribution streak" src="https://streak-stats.demolab.com/?user=R0hit-Yadav&hide_border=true&background=FFFFFF&stroke=0891B2&ring=7C3AED&fire=059669&currStreakLabel=0891B2&sideLabels=475569&currStreakNum=0F172A&sideNums=0F172A&dates=94A3B8&card_width=1180" />
</picture>

<!-- Tip: swap github-readme-stats.vercel.app for your own Vercel deploy if cards rate-limit (see SETUP.md).
     Top-langs excludes DSA / ML / coursework repos so it reflects on-chain work. -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github-readme-stats.vercel.app/api?username=R0hit-Yadav&show_icons=true&count_private=true&include_all_commits=true&hide=issues&hide_rank=true&hide_border=true&custom_title=On-Chain%20Activity&title_color=22D3EE&icon_color=A78BFA&text_color=94A3B8&bg_color=0A101F&card_width=500" />
  <img width="49%" alt="GitHub stats" src="https://github-readme-stats.vercel.app/api?username=R0hit-Yadav&show_icons=true&count_private=true&include_all_commits=true&hide=issues&hide_rank=true&hide_border=true&custom_title=On-Chain%20Activity&title_color=0891B2&icon_color=7C3AED&text_color=0F172A&bg_color=FFFFFF&card_width=500" />
</picture>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github-readme-stats.vercel.app/api/top-langs/?username=R0hit-Yadav&layout=compact&langs_count=8&hide=jupyter%20notebook,html,css&hide_border=true&custom_title=Languages%20I%20Ship&title_color=22D3EE&text_color=94A3B8&bg_color=0A101F&card_width=500&exclude_repo=R0hit-Yadav,LeetCode-Problems,LeetCode,Books,Krishimitra_Chatbot,HackovateLJ_2025,AI_ML-Projects,Python-Projects,Java-Projects,SpaceExpo,Odoo-Hackathon-2024,Rolls-Royce_Project,HTML-AND-CSS,FSD-Projects,PPT-For-Projects,Foundation-Of-Cybersecurity,E-Commerce" />
  <img width="49%" alt="Top languages" src="https://github-readme-stats.vercel.app/api/top-langs/?username=R0hit-Yadav&layout=compact&langs_count=8&hide=jupyter%20notebook,html,css&hide_border=true&custom_title=Languages%20I%20Ship&title_color=0891B2&text_color=0F172A&bg_color=FFFFFF&card_width=500&exclude_repo=R0hit-Yadav,LeetCode-Problems,LeetCode,Books,Krishimitra_Chatbot,HackovateLJ_2025,AI_ML-Projects,Python-Projects,Java-Projects,SpaceExpo,Odoo-Hackathon-2024,Rolls-Royce_Project,HTML-AND-CSS,FSD-Projects,PPT-For-Projects,Foundation-Of-Cybersecurity,E-Commerce" />
</picture>

<!-- Contribution snake — generated by .github/workflows/snake.yml onto the `output` branch -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/output/snake-dark.svg" />
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/output/snake-light.svg" />
  <img width="100%" alt="Snake eating my contributions" src="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/output/snake-dark.svg" />
</picture>

</div>

<!-- ============================== CONNECT ============================== -->

<br/>
<p align="center"><code>OPEN.CHANNELS</code></p>

<div align="center">

<a href="https://www.linkedin.com/in/rohit-yadav-611618260/"><img src="https://img.shields.io/badge/LinkedIn-0A101F?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyByb2xlPSJpbWciIHZpZXdCb3g9IjAgMCAyNCAyNCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBmaWxsPSJ3aGl0ZSI+PHBhdGggZD0iTTIwLjQ0NyAyMC40NTJoLTMuNTU0di01LjU2OWMwLTEuMzI4LS4wMjctMy4wMzctMS44NTItMy4wMzctMS44NTMgMC0yLjEzNiAxLjQ0NS0yLjEzNiAyLjkzOXY1LjY2N0g5LjM1MVY5aDMuNDE0djEuNTYxaC4wNDZjLjQ3Ny0uOSAxLjYzNy0xLjg1IDMuMzctMS44NSAzLjYwMSAwIDQuMjY3IDIuMzcgNC4yNjcgNS40NTV2Ni4yODZ6TTUuMzM3IDcuNDMzYy0xLjE0NCAwLTIuMDYzLS45MjYtMi4wNjMtMi4wNjUgMC0xLjEzOC45Mi0yLjA2MyAyLjA2My0yLjA2MyAxLjE0IDAgMi4wNjQuOTI1IDIuMDY0IDIuMDYzIDAgMS4xMzktLjkyNSAyLjA2NS0yLjA2NCAyLjA2NXptMS43ODIgMTMuMDE5SDMuNTU1VjloMy41NjR2MTEuNDUyek0yMi4yMjUgMEgxLjc3MUMuNzkyIDAgMCAuNzc0IDAgMS43Mjl2MjAuNTQyQzAgMjMuMjI3Ljc5MiAyNCAxLjc3MSAyNGgyMC40NTFDMjMuMiAyNCAyNCAyMy4yMjcgMjQgMjIuMjcxVjEuNzI5QzI0IC43NzQgMjMuMiAwIDIyLjIyNSAweiIvPjwvc3ZnPg==" alt="LinkedIn" /></a>&nbsp;
<a href="https://x.com/RohitYadav2312"><img src="https://img.shields.io/badge/X-0A101F?style=for-the-badge&logo=x&logoColor=22D3EE" alt="X" /></a>&nbsp;
<a href="https://www.instagram.com/rohit_k_yadav._/"><img src="https://img.shields.io/badge/Instagram-0A101F?style=for-the-badge&logo=instagram&logoColor=A78BFA" alt="Instagram" /></a>&nbsp;
<a href="https://discord.gg/gDgGe2Gq"><img src="https://img.shields.io/badge/Discord-0A101F?style=for-the-badge&logo=discord&logoColor=10B981" alt="Discord" /></a>&nbsp;
<a href="mailto:rohitkyadav2312@gmail.com"><img src="https://img.shields.io/badge/Email-0A101F?style=for-the-badge&logo=gmail&logoColor=10B981" alt="Email" /></a>

<br/><br/>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/assets/footer-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/assets/footer-light.svg">
  <img width="100%" alt="tx confirmed — thanks for stopping by" src="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/assets/footer-dark.svg">
</picture>

</div>
