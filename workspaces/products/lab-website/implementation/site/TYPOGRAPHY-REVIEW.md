# Shared typography revision

Date: **12 October 2026**

## Presentation

The shared `site-typography.css` is loaded last on the rendered documentation pages, the company and research pages, the reader form and the linked robot series. The build attaches it before the editorial pass and search compilation, so recorded page fingerprints refer to the final delivered HTML.

| Role | Desktop | Compact screens |
| --- | ---: | ---: |
| Main reading text | 20 px | About 19 px |
| Navigation | 16 px | About 15 px |
| Metadata and captions | 15 px | About 14 px |
| Reference record text | 17 px | About 16 px |
| Code blocks | 16 px | About 15 px |

Lead text and headings retain their hierarchy. The standalone robot series has a slightly larger essay scale. The desktop sidebar is 250 px wide. On compact screens the logo and search share the first header row, with navigation below. Header height is measured so sticky navigation and fragment destinations stay clear of it.

Diagrams grow through their display dimensions, preserving the relationship between text, label backgrounds and arrows. Their existing horizontal scrolling and full-size controls remain available.

## Browser observations

Playwright inspected Chromium at widths of 1440, 1024, 390 and 320 px. The homepage, Start here, essay 6 and Craft's typed-model chapter showed the expected reading and navigation sizes, with no page-level horizontal overflow at those widths.

Additional 390 px inspections covered the company article, research page, robot series, system map, an expanded reference definition and Craft's definition chapter. Those pages also had no page-level horizontal overflow. Narrow navigation rows and diagrams use their own scrolling where needed.

The initial larger header occupied about 195–223 px on a phone. Its revised layout occupies about 120–130 px. The desktop sidebar gives the larger topic labels more room. Screenshots are retained under ignored `output/playwright/typography-*.png`.

These observations cover the selected Chromium pages and viewport states.

## Build and content

The complete static build succeeded with 632 packaged files and 690 search entries. The preservation comparison retained all 454 captured reference record bodies. Formal statements, code, example data and the adopted editorial prose are unchanged.

Archive SHA-256:

```text
96b0f08ee90b9026523d748a71c025a2c9041fa232de546c9dd396aa67b25b29
```

The Markdown import refreshed 37 pages and reported no unresolved links or changed digest-bearing captured sources. No implementation suite, commit, push or deployment was performed.
