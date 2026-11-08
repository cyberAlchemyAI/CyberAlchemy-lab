# Repository website build review

The prose adoption is described in [EDITORIAL-REVIEW.md](EDITORIAL-REVIEW.md), followed by the [sidebar revision](NAVIGATION-REVIEW.md) and [typography revision](TYPOGRAPHY-REVIEW.md). The results below record the original repository import build.

Date: **11 October 2026**

## Build result

The integrated build completed with the local Python installation and again in a fresh virtual environment using the declared dependencies. Both runs produced this archive digest:

```text
9dc7331fde3916e38a2816005dcccdcaa40735dd2adedcadca449049cb7b6c4e
```

The archive contains **630 files**, including its release manifest, and is **20,052,694 bytes**. ZIP integrity inspection reported no damaged member. The generated index contains **690 entries**:

| Search group | Entries |
| --- | ---: |
| Reference records | 460 |
| Guide | 53 |
| Expanded essays | 47 |
| Craft | 42 |
| Practical guides | 26 |
| Reference examples | 17 |
| Learning paths | 16 |
| The Lab | 13 |
| Start here | 8 |
| Research lab | 7 |
| Sources | 1 |

The generated index fingerprint and every indexed HTML source fingerprint matched. Package selection resolved local HTML/CSS dependencies and retained the explicit assets used by dynamic search. The selected deployment inventory contains no build tools, virtual environment, browser traces or historical versions.

The integrated build renders in its own temporary directory. Comparing maintained source against the import inventory found changes only in the four documented portability adapters: repository capture, Craft search sequencing, preservation-check baseline and package entry point. The reference records and authored article content were preserved.

## Browser observations

Playwright drove Chromium against the repository's generated output:

- The root entrance opened the existing company-brain homepage.
- Searching for Calculation from the guide and selecting Craft opened the capacity Calculation explanation.
- Searching for Delegation from Craft opened the reference definition and expanded its record body.
- Searching for agent in the expanded-essay scope opened **An agent’s working session**; one essay was visible.
- The retired authority page redirected to the guide's governance section.
- The homepage at a 390-pixel viewport had no horizontal overflow.
- At a `/CyberAlchemy-lab/` hosting path, search from the homepage opened Craft while preserving that path.
- From a local `file:` origin, search opened the reference definition in the repository's generated site.

No page errors or failed requests were observed during the HTTP navigation sequence. No page errors were observed during the project-path and file-origin sequence. A local homepage screenshot is retained under ignored `website/output/playwright/repository-website/`.

## Scope

These observations establish the local build, packaging and selected browser integrations. The manually triggered GitHub Pages workflow is prepared but has not been dispatched. No commit, push or live deployment was performed.

The previous plan's reader study, actual screen-reader checks and actual Safari checks remain separate manual work. This review does not establish new evidence for those checks or change the documentation's captured authority selection.
