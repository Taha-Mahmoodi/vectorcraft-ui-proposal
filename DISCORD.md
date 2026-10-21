**VectorCraft: a quieter interface (proposal, code ready)** 🎨

Hi @bflatastic! Thanks for merging my PRs (#3200, #3206, #3207, #3208). You invited me to talk about what's next, so here's what I'd like to work on.

Since 0.12 the toolbar, the rail and the dock are rounded cards inside square columns. Corners have no system (10 hand-picked radii in 44 files). And the coral accent tints the chrome around the artwork. For a tool where people judge shape and colour all day, I think the chrome should recede.

I made two alternatives, each in **Dark and Light**:
• **A · Flat**: today's look without the cards. Panels flush to the edges, 1 px dividers, underlined tabs, a neutral active tool, and blue only for selection, focus and the main action
• **B · Quiet**: one calm continuous surface with no lines, soft raised buttons, segmented tabs

Both are **already built** as extra Color Scheme choices. Modern and Classic are untouched, the corner scale is its own commit, and "make it the default" is its own one-line commit. `cargo xtask ci` passes end to end on both.

📄 Proposal (one-page argument, paper with sources and measurements, FigCraft prototype): https://github.com/Taha-Mahmoodi/vectorcraft-ui-proposal
💬 Issue: https://github.com/storytold/vectorcraft/issues/3439

What I'm asking:
1️⃣ take the corner-scale commit either way
2️⃣ pick a default: A, B, or keep Modern
3️⃣ keep the other one as an option, or drop it

I can open the PRs the same day. Happy to tweak colours and corners, or combine it with #3175.

*(attach: compare-mediumDark.png, compare-light.png, compare-mediumDark-dock.png)*
