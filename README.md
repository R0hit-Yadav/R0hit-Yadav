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
<!-- One image per block so each opens its repo. Keep the tiles on one line: whitespace between them breaks the chain. -->

<br/>
<picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/assets/chains-header-dark.svg"><source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/assets/chains-header-light.svg"><img width="100%" alt="LEDGER.TRACE" src="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/assets/chains-header-dark.svg"></picture>

<p align="center"><a href="https://github.com/R0hit-Yadav/Web3_Rust_X_Blockchain"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/assets/chains/0-dark.svg"><source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/assets/chains/0-light.svg"><img width="16.6%" alt="Genesis/Rust — Web3_Rust_X_Blockchain" src="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/assets/chains/0-dark.svg"></picture></a><a href="https://github.com/R0hit-Yadav/Solana_Token"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/assets/chains/1-dark.svg"><source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/assets/chains/1-light.svg"><img width="16.6%" alt="Solana — Solana_Token" src="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/assets/chains/1-dark.svg"></picture></a><a href="https://github.com/R0hit-Yadav/Move_Aptos"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/assets/chains/2-dark.svg"><source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/assets/chains/2-light.svg"><img width="16.6%" alt="Aptos — Move_Aptos" src="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/assets/chains/2-dark.svg"></picture></a><a href="https://github.com/R0hit-Yadav/DAO_Voting_System"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/assets/chains/3-dark.svg"><source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/assets/chains/3-light.svg"><img width="16.6%" alt="Ethereum — DAO_Voting_System" src="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/assets/chains/3-dark.svg"></picture></a><a href="https://github.com/R0hit-Yadav/Soroban_Integration"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/assets/chains/4-dark.svg"><source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/assets/chains/4-light.svg"><img width="16.6%" alt="Stellar — Soroban_Integration" src="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/assets/chains/4-dark.svg"></picture></a><a href="https://github.com/R0hit-Yadav/MIT_BITCOIN-2025"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/assets/chains/5-dark.svg"><source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/assets/chains/5-light.svg"><img width="16.6%" alt="Bitcoin — MIT_BITCOIN-2025" src="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/assets/chains/5-dark.svg"></picture></a></p>

<!-- ============================== STACK ============================== -->

<br/>
<p align="center"><code>STACK.INSTALLED</code></p>
<p align="center">
  <img src="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/assets/stack.svg" alt="Rust, Solidity, TypeScript, JavaScript, React, Node.js, Python, Docker, AWS, Git, Linux, VS Code" />
</p>

<!-- ============================== PROJECTS ============================== -->
<!-- Live cards: rebuilt every 6h by .github/workflows/projects.yml onto the `projects` branch (cards/<repo>.svg).
     To add/reorder: edit projects.json AND the card rows below (one <a> per repo). -->

<br/>
<picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/projects/projects-header.svg"><source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/projects/projects-header-light.svg"><img width="100%" alt="PROJECTS.LIST" src="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/projects/projects-header.svg"></picture>

<p align="center">
<a href="https://github.com/R0hit-Yadav/Web3_Rust_X_Blockchain"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/projects/cards/Web3_Rust_X_Blockchain.svg"><source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/projects/cards/Web3_Rust_X_Blockchain-light.svg"><img width="49%" alt="Web3 Rust X Blockchain" src="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/projects/cards/Web3_Rust_X_Blockchain.svg"></picture></a>
<a href="https://github.com/R0hit-Yadav/Move_Aptos"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/projects/cards/Move_Aptos.svg"><source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/projects/cards/Move_Aptos-light.svg"><img width="49%" alt="Move Aptos" src="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/projects/cards/Move_Aptos.svg"></picture></a>
<br/>
<a href="https://github.com/R0hit-Yadav/Solana_Token"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/projects/cards/Solana_Token.svg"><source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/projects/cards/Solana_Token-light.svg"><img width="49%" alt="Solana Token" src="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/projects/cards/Solana_Token.svg"></picture></a>
<a href="https://github.com/R0hit-Yadav/Soroban_Integration"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/projects/cards/Soroban_Integration.svg"><source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/projects/cards/Soroban_Integration-light.svg"><img width="49%" alt="Soroban Integration" src="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/projects/cards/Soroban_Integration.svg"></picture></a>
<br/>
<a href="https://github.com/R0hit-Yadav/DAO_Voting_System"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/projects/cards/DAO_Voting_System.svg"><source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/projects/cards/DAO_Voting_System-light.svg"><img width="49%" alt="DAO Voting System" src="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/projects/cards/DAO_Voting_System.svg"></picture></a>
<a href="https://github.com/R0hit-Yadav/Hack-IIT-K-2025"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/projects/cards/Hack-IIT-K-2025.svg"><source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/projects/cards/Hack-IIT-K-2025-light.svg"><img width="49%" alt="Hack IIT-K 2025" src="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/projects/cards/Hack-IIT-K-2025.svg"></picture></a>
</p>

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

<a href="https://www.linkedin.com/in/rohit-yadav-611618260/"><img height="28" src="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/assets/badges/linkedin.svg" alt="LinkedIn" /></a>&nbsp;
<a href="https://x.com/RohitYadav2312"><img height="28" src="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/assets/badges/x.svg" alt="X" /></a>&nbsp;
<a href="https://www.instagram.com/rohit_k_yadav._/"><img height="28" src="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/assets/badges/instagram.svg" alt="Instagram" /></a>&nbsp;
<a href="https://discord.gg/gDgGe2Gq"><img height="28" src="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/assets/badges/discord.svg" alt="Discord" /></a>&nbsp;
<a href="mailto:rohitkyadav2312@gmail.com"><img height="28" src="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/assets/badges/email.svg" alt="Email" /></a>

<br/><br/>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/assets/footer-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/assets/footer-light.svg">
  <img width="100%" alt="tx confirmed — thanks for stopping by" src="https://raw.githubusercontent.com/R0hit-Yadav/R0hit-Yadav/main/assets/footer-dark.svg">
</picture>

</div>
