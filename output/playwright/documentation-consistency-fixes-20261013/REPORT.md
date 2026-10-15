# Documentation consistency fixes

13 October 2026. Implemented in maintained website source and rebuilt into the local website.

## Changes

- All 454 detailed record pages use the shared documentation theme, header, reading grid and explanatory type scale.
- Parent catalog navigation remains selected. Breadcrumbs identify the record category and name.
- Long records have a local outline with stable fragment links. Links into closed formal disclosures reveal the requested section.
- Compact navigation starts collapsed. Native keyboard disclosure controls remain available.
- Definition reading aids use ruled term/value rows and stack on phones.
- Relation patterns use a horizontal layout on desktop and a vertical layout on phones. Only the appropriate direction arrow is visible.
- Catalog introductions use the same explanatory text size as the guide.
- Documentation header labels and link styling are consistent. The centered homepage remains the product entrance.

## Verification

| Scope | Result |
| --- | --- |
| Formal content | All 454 body identities/fingerprints match the previous release. All record body text and verbatim code fingerprints are unchanged. |
| Complete reference corpus | 454 pages at desktop 1440 px and phone 390 px, totaling 908 rendered states. No page overflow, duplicate IDs, theme, selected-catalog, compact-navigation, relation-direction or script failures. |
| Representative site families | 15 routes at 1440, 1024, 390 and 320 px, totaling 60 states. Guide, catalogs, essays, Craft, practical pages and detailed records share the expected header and content alignment. |
| Interactions | 12 checks pass: keyboard navigation, parent catalog route, local outline, direct fragment reload, responsive disclosure state, search from records/guide/Craft, Escape dismissal and formal-code focus. |
| Build | Full build completes, including its documentation checks and generated search with 708 entries. |

The final desktop reference header is 86.5 px high, matching the guide. Content begins at x=360 px, with 20 px explanatory text. At 390 px, reference titles begin around y=312 px and reading text is about 18.9 px. The prior mobile record opening was around y=1,918 px.

The initial focus check attempted to focus code inside a closed native disclosure. The corrected user flow opens that disclosure using the keyboard before focusing its code. The initial result is retained in `interaction-checks.initial.json`.

An overlapping hackathon update briefly prevented the full build because its new illustrations were not yet packaged. Those assets are now present and were preserved. No placeholder images or relaxed missing-resource checks were used.

## Release

- Reviewed archive: `website/artifacts/docs-consistency-20261013-2597e05eea90.zip`
- SHA-256: `2597e05eea90c19de09b0c187c93923f30acea9f7364b50e12052f7223b071ed`
- Local website: http://127.0.0.1:33733/
- Definition: http://127.0.0.1:33733/governance-lab-series/reference/def-cal-definition-definition.html
- Relation: http://127.0.0.1:33733/governance-lab-series/reference/rel-relation-member-of.html

The named archive preserves this reviewed edition separately from the mutable working preview. Browser checks use Playwright Chromium with viewport emulation. They establish the checked behavior and geometry, not reader comprehension or complete accessibility conformance.

## Evidence

- `preservation-and-structure.json`
- `browser-checks.json` and `screenshots/`
- `record-corpus-checks.json`
- `interaction-checks.json`
- `release.json`
- Source snapshots in `before/`

## Maintained implementation

`website/reference_pages.py` generates the record shell and outline. Shared header and navigation styles live in `lab-docs.css` and `site-search.js`. `reference-reading.css` owns definition aids and relation patterns. `reference-record-page.css` and `.js` handle record layout and behavior. `site-typography.css` and `lab-library-docs.css` own reading roles. The article and governance templates retain consistent header labels.
