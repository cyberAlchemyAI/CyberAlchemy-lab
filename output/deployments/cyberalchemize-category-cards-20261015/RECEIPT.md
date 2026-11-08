# Hackathon category cards — deployed and verified

Live page: https://cyberalchemize.com/governance-lab-series/hackathon.html?review=category-cards#challenge

Studio front-end and Open projects now have individual padded cards with
original wild imagery made with the built-in image_gen tool. The approved
Paper & crimson palette, all category copy, existing links, dates and rules
remain intact. [Artwork files and exact prompts](../../imagegen/hackathon-category-cards-20261015/README.md).

Release: `lab-20261015T053101Z-5eae124ed3be`.
ZIP SHA-256: `890fdc4e822991a7d3871501f8c6ef0dc1a5777f880b2f1342c49598ad84946b`.
Manifest SHA-256: `5eae124ed3be2f73b01837f070632771999f241a0431e42c9c87b083fad85a23`.

## Verified

- Normal build: 41,830 checks pass. 498 pages preserve every original paragraph,
  heading, list item, link and fragment; 23,911 local references resolve.
- Local and live Chromium: 16 states each across 320, 390, 768 and 1440 px,
  both themes. No overflow, image failures, clipped card bodies, incorrect
  padding, footer misalignment, runtime errors or stale event text.
- Two axe audits per environment: zero violations. Five event/search/no-JS
  checks per environment pass.
- All 1,237 public release files match reviewed bytes over verified HTTPS;
  image WebP MIME types pass. Ten prior public/protected route checks pass.
- 64 earlier image/font/download/calendar files remain byte-identical; event
  configuration, rules sources and rules PDF/DOCX retain their exact hashes.
- Staging validated a 1,248-file combined tree, preserved eight secondary files
  and old hashed asset URLs, and verified private-route authentication.
- Nginx, Compose, credentials, static image and unrelated containers unchanged.
  A complete private rollback is retained outside the web root at
  `/srv/co-op-engine/deployments/lab-20261015T053101Z-5eae124ed3be/rollback`.

The exact reviewed envelope and machine-readable evidence are beside this
receipt. No Git commit or push was performed. The local server remains available.
