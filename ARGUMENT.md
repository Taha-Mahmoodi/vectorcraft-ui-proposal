# The case for quiet chrome, in one page

**The ask:** make VectorCraft's chrome flat and neutral again — no cards inside columns, one corner scale, colour only where it means something. Two designs, both in Dark and Light, are built and ready: pick one, and the pull requests open the same day.

## Why it matters

1. **The artwork is the job.** People use VectorCraft to judge shape and colour. Colour pulls attention (Wolfe & Horowitz 2004); an irrelevant coloured item captures it anyway (Theeuwes 1992). A coral active tool, coral-tinted layer rows and coral buttons put colour signals in the corners of the eye all day.
2. **Colour next to the art changes the art.** Perceived colour depends on its surround (Shevell & Kingdom 2008). Colour-critical work keeps the surround neutral — the soft-proofing standard ISO 12646 asks for no strongly coloured surfaces around the display. Neutral chrome is the on-screen version of that rule.
3. **A box in a box says the same thing twice.** A docked panel is already a region (Palmer 1992, common region). The rounded card inside it, set off by a band of frame colour, adds edges and corners but no meaning. Edges are what clutter measures count (Rosenholtz et al. 2007; Mack & Oliva 2004).
4. **Corners have no system.** 10 different hard-coded radii across 44 files; the theme's radius helper `cr()` is called once. Design systems use a small corner scale (Material Design 3) so that the same kind of thing always looks the same.
5. **Users noticed.** #3134: VectorCraft and PhotoCraft "no longer feel like they belong to the same suite". #3175 tries to bring the old flat look back.

## What's ready

| | A · Flat | B · Quiet |
|---|---|---|
| In one line | Today's look without the cards | Calm, monochrome, soft depth |
| Separation | Tone + 1 px lines | Tone + space, no lines |
| Corners | 0 / 4 / 8 | 0 / 8 / pill / 14 |
| Modes | Dark + Light | Dark + Light |
| Code | `ui/flat-scheme` | `ui/quiet-scheme` |

- FigCraft prototype with design-system sheets (tokens as variables), every screen in both modes, clickable.
- Both designs implemented as opt-in Color Schemes; Modern and Classic untouched; "make it the default" is a separate commit; full `cargo xtask ci` green.
- Measured on live screenshots of the running app: lower the edge density of the chrome by 19–20 % at the default Medium Dark brightness (5–10 % in Light) and cut its coloured pixels by 27–42 % at Medium Dark, with Modern and Classic unchanged

## The decision

1. Take the corner-scale commit regardless.
2. Choose the default: **A**, **B**, or keep Modern.
3. Keep the other one as an option, or drop it.

Full paper: `paper.pdf`. Prototype: `VectorCraft UI proposal.figcraft`.
