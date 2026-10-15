# Bounded confirmation after the final build

All three findings in REVIEW.md pass confirmation on the rebuilt site served at `http://127.0.0.1:8767/`. The real theme control was used; the browser session was `review-design-confirm` and was closed afterward. No source edits or builds were performed by this reviewer.

- **Search containment: PASS.** At 390×844, the panel is x=16..374 and y=128..828, below the header ending at y=120. At 900×1000, it is x=16..884 and y=131..984, below the header ending at y=123. Text is visible across its full width. Evidence: `confirmed-search-390-dark.png`, `confirmed-search-900-dark.png`.
- **Dark search colors: PASS.** Toolbar background is rgb(40,30,33), count text rgb(198,177,171). Matches use rgb(250,240,232) on a muted dark crimson fill; labels and matching words remain readable. Evidence: the same two search screenshots.
- **Expanded original-home map: PASS.** At 1440px, the core again has absolute placement and a 185px box; its caption ends at y=531 while the instruction begins at y=879. At 390px, the core correctly joins the responsive static grid; caption ends at y=231 while the instruction begins at y=690. Caption, instruction, and following content no longer overlap. Retained role labels use the approved monospace stack. Evidence: `confirmed-role-map-1440-dark.png`, `confirmed-role-map-390-dark.png`.

This confirmation is limited to the three reported fixes and does not expand the initial review scope.
