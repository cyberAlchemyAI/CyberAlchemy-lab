# Independent graph review

Read-only review of the isolated Paper & crimson preview. No source files edited.

## Coverage

32 page-family states: governance guide, incident walkthrough, research, company-brain, hackathon, Craft, library, and robot essays at 1440 and 390px in light/dark. All 30 figure instances were captured in each applicable state (120 figure observations). Library and robot essays contain no actual figure/SVG diagrams; their prose still included in overflow/runtime checks.

40 map states: all ten layouts across the two widths/themes. All relationship lists matched declared edges, every Fit measurement matched stage width, and Zoom increased diagram size. No page overflow or runtime errors.

27 standalone SVG files inspected in light and dark browser color schemes (54 states): 16 explanatory/Craft diagrams and 11 map exports (the governance alias duplicates its overview). All returned HTTP 200, had title/description, and all text stayed inside SVG viewBox. Craft retains deliberate light figure surfaces inside dark reading pages. The three guide PNG concept illustrations loaded and remained clear in light/dark; captures include full alt context via review.json.

## Findings for parent correction batch

1. Medium: five guide inline diagrams intentionally exceed reading column width but lack visible scroll/open affordance. Sources are #figure-evidence-chain, #figure-admission-and-histories, #figure-meaning-shape-record, #figure-records-and-ontology, #figure-agent-session; child .diagram-shell. Evidence governance-lab-reference-light-1440-figure3.png and -light-390-figure3.png: Assessment node offscreen. Keyboard scroll aria-label exists, but sighted users have no instruction. Match Craft with visible scroll guidance and optional full-size SVG links. Preserve graph geometry. Exact standalone asset stems match figure IDs after removing figure-.

2. Low: Agent session map title extends slightly past its node border. .smap-node[data-map-node="assignment"] > text in agent view: rect x590,width220 ends810; title x645.99994,width165.25124 ends811.25118. At desktop fit, Agent Assignment touches/passes right border, unlike sibling wrapped titles. Screenshot map-agent-default-light-1440.png and dark equivalent. Wrap title on two lines without changing node/edge geometry.

No further concrete graph defect found in bounded review. This is local Chromium verification, not a claim of whole-site WCAG conformance or physical-device testing.

## Final confirmation

Both original visual findings are resolved. All five scroll regions have visible guidance, full-size links, aria-describedby associations, and keyboard horizontal scrolling in 20 theme/width observations. Agent Assignment now wraps in the embedded map and standalone export. All forty map state title bounds fit. An introduced oversized link icon was caught in confirmation, corrected by the parent, and rechecked in twenty tool states: every icon is 16×16px, tool rows stay compact, zero page overflow. Final screenshots use final-fixed-*; earlier final-* tool captures are diagnostic and superseded. Tiny semantic follow-up requested to retain a space between Agent and Assignment tspans for accessible text.
