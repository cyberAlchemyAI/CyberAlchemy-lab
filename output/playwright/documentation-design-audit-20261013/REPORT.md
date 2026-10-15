# Documentation design consistency audit

13 October 2026. Current locally built website at http://127.0.0.1:33733/.

## Scope

Compared ten rendered routes at 1440 × 1000 and 390 × 1000: Start here, two guide chapters, definition and relation catalogs, an expanded essay, the Craft overview, a definition record, a relation record and an artifact-type record. Screenshots and DOM measurements describe this edition and these viewports. They do not measure reader comprehension or establish accessibility conformance. The audit does not edit maintained website sources or formal records.

## Findings

| Priority | Finding | Browser evidence | Recommended change |
| --- | --- | --- | --- |
| High | Detailed records lose the documentation header and theme. | The desktop header grows from 86.5 px in the guide/catalog to 183 px on records. Navigation and search stack. White/blue documentation styling changes to the cream/red base theme. | Give records the shared documentation shell and body theme marker. Use one header implementation. |
| High | Record navigation occupies the opening on phones. | The record sidebar is 1,697 px high and its disclosure stays open. The record title begins around y=1,918 px. The guide/catalog disclosure collapses and their topic titles begin around y=312 px. | Use the shared responsive disclosure behavior on records, with navigation initially collapsed at compact widths. |
| High | Reference reading aids lose their component layout. | On the Definition record, introductory fields form unequal columns with excessive wrapping. On member-of, source, relation label, both direction arrows, qualifier and target run together. | Scope component styles to the component itself, including standalone record pages. Keep introductory aids separate from formal metadata grids. |
| Medium | Detailed records break the reading alignment. | At desktop width, guide/essay/catalog content starts at x=360 px. Record content starts at x=480 px. | Use the same desktop grid and content origin across documentation pages. |
| Medium | Records lose location cues. | No selected left-navigation link on the three sampled record routes. No local heading index. Breadcrumb says “Reference catalog / Exact record” without the category. | Keep Definitions, Connection rules or Record formats selected as the parent. Use a breadcrumb such as “Reference / Connection rules / member-of”. Provide an outline for long records. |
| Medium | Reference explanatory text uses a smaller reading scale. | Guide/essay prose is 20 px on desktop and about 18.9 px on phone. Record introductory prose is 17 px and about 16.1 px. | Give explanatory prose the shared reading scale. Use explicit compact roles for metadata, code and technical tables. |

## Why this happens

The guide, essays, library and Craft already share many of the same navigation groups, heading styles and desktop content origin. Most of the visible divergence occurs when a catalog record becomes a standalone page.

1. `website/reference_pages.py` emits `<body data-docs-enhanced="record">`, without the `data-edition="reference"` marker used by the documentation theme. The header is copied, but the theme and header selectors in `lab-docs.css` no longer match.
2. `reference-reading.css` requires `.resource-shelf` around its definition aids and relation patterns. Standalone records do not have that ancestor. The relation grid and its mutually exclusive horizontal/vertical arrow styles therefore do not apply.
3. `reference-record-page.css` applies a two-column grid to every record `dl`. A definition's reading aid contains wrapper elements, while formal metadata uses direct term/value children. Applying the same grid to both produces the malformed introduction.
4. The record generator hardcodes an open navigation disclosure. It removes the library chapter controller, which normally adjusts disclosure state. The shared navigation script fills the menu, but does not provide the missing compact record behavior or select the record's parent catalog.
5. Records have their own two-column 1,160 px layout and no local outline. The other documentation families use a shared grid and page outline.

All 454 generated record pages share the same missing edition marker and absent resource-shelf wrapper: 183 definitions, 121 record formats, 41 relation rules and 109 endpoint kinds. The browser inspected representative pages from three of these families. The generator inventory establishes the broader shared source condition.

## What should remain distinct

The centered product homepage is an appropriate entrance. Documentation pages should share header, palette, reading grid, navigation, breadcrumbs and typography roles. Content components should express their subjects:

- A definition: meaning, scope, boundaries and exact record details.
- A relation: one declared source-kind → relation → target-kind pattern, permitted ordered pairs and qualifiers.
- A record format: purpose, required fields and schema.
- An essay or guide: continuous explanation with a local heading index.

Start here and the Craft overview have larger introductory titles (55.8 and 58.5 px at the desktop sample). Chapter and record titles use 33.75 px. This hierarchy is a reasonable page-role distinction. The broken record header, lost component styling and mobile navigation behavior need repair first.

## Suggested order

1. Make standalone records participate in the shared documentation shell.
2. Repair compact navigation, parent-catalog selection and breadcrumbs.
3. Restore definition reading-aid rows and relation diagrams through reusable component styles.
4. Align reading columns and explanatory typography across families.
5. Add local outlines for long records and inspect the resulting desktop/phone reading flow.

Apply the changes through the renderer and shared source styles, then rebuild. Keep exact record wording, source identities, version and standing intact.

## Evidence

- `observations.json`: twenty route/viewport observations.
- `diagnosis.json`: live body marker, header display and member-of component markup.
- `screenshots/`: captured renderings of each sample.
