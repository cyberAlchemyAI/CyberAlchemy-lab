# Documentation sidebar revision

Date: **12 October 2026**

## Reading order

1. Getting started: start, overview, definitions, incident, comparisons and map.
2. Governance: authority, provenance and lifecycle.
3. The Lab model: purpose, records, agents, learning and operational scope.
4. Practical guides: read a record, prepare a definition, prepare an assessment and resume work.
5. Software design: Craft and its chapters on the Craft page.
6. Expanded essays: the series entrance and individual essays in the library.
7. Reference: catalogs, examples, sources and questions.
8. About CyberAlchemy: company purpose and research.

The shared navigation moves existing links into these groups, preserving the nodes used by the chapter controllers. It removes repeated destinations and keeps the active topic visible in the desktop tree. The guide and start templates also carry this ordering without JavaScript. The guide and essay pagers follow the revised local topic order.

## Browser observations

Playwright drove Chromium at a 1440 × 1000 viewport. Start here, the authority chapter, essay 6, Craft's definition chapter and the definition preparation guide all displayed the same eight groups in order. Each had the appropriate active link visible, with no repeated sidebar destination.

| Page | Sidebar links |
| --- | ---: |
| Start here | 26 |
| Authority chapter | 27 |
| Expanded essay 6 | 40 |
| Craft definition chapter | 38 |
| Prepare a definition | 26 |

At 390 × 844, Start here's browse disclosure was closed initially, opened on activation, and displayed all eight groups. The page had no horizontal overflow. Desktop and mobile screenshots are retained in ignored `output/playwright/sidebar-desktop.png` and `sidebar-mobile.png`.

These observations cover the selected Chromium pages and viewport states.

## Build

The complete static build succeeded with 631 packaged files and 690 search entries. Its preservation comparison retained all 454 captured reference record bodies. The adopted explanatory prose remains unchanged.

Archive SHA-256:

```text
5ac5cf86ec43e5c610639f9f48b39183c23ea1a3a519c5968bd629bbf860e87e
```

The Markdown import refreshed 37 pages, including eight essays, and reported no unresolved links or changed digest-bearing captured sources. No implementation suite, commit, push or deployment was performed.
