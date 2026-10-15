# CyberAlchemy Lab website

The complete documentation website and its build process live here. The Lab guide, eight expanded essays, reference library, practical guides, Craft documentation and shared search are built together. The existing company-brain entrance, research page and linked robot-learning article are retained.

The build uses repository-owned templates, prose, illustrations, fonts and the documentation's captured source records. It needs no attachment folder, neighboring repository, live Lab service or external search service. Python dependencies are installed once; rendering then runs locally.

## Build

Use Python 3.11 or newer; the local build and prepared workflow use Python 3.14. From repository root:

```bash
python3 -m venv website/.venv
website/.venv/bin/python -m pip install -r website/requirements.txt
website/.venv/bin/python website/build.py
```

On Windows, use `website\.venv\Scripts\python.exe` for the last two commands.

Outputs:

| Path | Purpose |
| --- | --- |
| `website/dist/` | Complete static site ready for hosting |
| `website/artifacts/cyberalchemy-lab-website.zip` | Portable archive; extract its contents into the hosting root |
| `website/artifacts/build.json` | Archive digest, file count and search coverage |
| `website/dist/release-manifest.json` | Exact deployment file inventory and hashes |
| `website/.build/logs/` | Logs for rendering, the editorial edition and final search generation |

Generated output, logs, archives and the virtual environment are ignored by Git. The source and build files belong in the reviewed commit. A failed rendering stage leaves the previous successful output in place.

## Preview

```bash
python3 -m http.server 8000 --bind 127.0.0.1 --directory website/dist
```

Open `http://127.0.0.1:8000/`. You can also open `website/dist/index.html` directly. Keep the entire output together: navigation, reference records and search use relative URLs. The site supports deployment at a domain root or beneath a project path.

`site.json` selects the root entrance. Its default is the existing Lab homepage at `governance-lab-series/index.html`; the introductory documentation remains at `governance-lab-series/start-here.html`.

The homepage uses the approved Paper & crimson opening, the engraved knot illustration, an interactive incident example and links into the documentation. Its original company-brain content and role map remain in the “More about the company brain” disclosure. Existing fragment links open that content automatically; the event announcement stays visible above the opening. Maintain the approved opening in `source/governance-lab-series/templates/paper-home.html.in`, the shared appearance in `assets/paper-crimson/`, and the integration in `paper_crimson.py`. The original landing template and adopted editorial prose remain maintained inputs.

## Reference records and search

The build preserves all 454 selected record bodies, then places each on a static page under the reference directory. The catalog contains compact reading summaries. Old catalog fragments redirect to the corresponding exact record. The eight expanded essays retain their existing library routes.

Detailed records use the same documentation theme, header and reading grid as the guide, essays and Craft. Each page selects its parent catalog, has category breadcrumbs and an outline, and collapses its navigation on compact screens. Definition reading aids use ruled rows. Relation patterns read horizontally on desktop and vertically on phones. Maintain their generated shell in `reference_pages.py`, shared components in `assets/reference-reading.css`, and record layout/behavior in `assets/reference-record-page.css` and `.js` under the Lab source folder. Presentation changes retain the exact body preservation checks.

Complete-record catalog search loads its text only when needed. Global search loads its index on first use. Both ship complete gzip payloads in local scripts, decoded with the browser’s DecompressionStream API. Browsers without that API load the complete plaintext fallback. Both routes work from a file origin. Search vocabulary and independently selected judgment destinations are maintained separately. Ranking never generates its own expected destination.

The integrated build runs structural checks after the final search index. It verifies all canonical record bodies against the fixed preservation baseline. Use the complete build command above when changing renderers, record routing or search.

## Sharing configuration

`site.json.source_repository` records the selected development repository. The documentation includes a source/status page with that route and a distinction between the captured edition and current development.

Set `site.json.public_url` to the chosen deployed base address, including any project directory, when known. A rebuild then emits absolute canonical and Open Graph URLs. Leaving it unset preserves relative canonical links for local and project-path previews. The build does not choose a domain, publish the site or change repository visibility.

## Edit and rebuild

| Change | Maintained source |
| --- | --- |
| Approved explanatory prose across the site | `editorial-copy.json`, applied by `editorial_style.py` |
| Guide, definition cards, incident flows, home and research pages | `source/governance-lab-series/templates/` and the associated Python renderers |
| Expanded essay structure and captured original prose | `source/governance-lab-series/01-…txt` through `08-…txt` |
| Reference explanations and source selection | `source/governance-lab-series/research/library-reader-copy.json`, `catalog.json` and `context-pack.json` |
| Incident data and record specimens | `research/incident-extraction-case.json` and `documentation_examples.py` in the Lab source folder |
| Craft article | `source/craft-documentation-proposal/craft-model.md` and `tools/build_article.py` |
| Layout, interactions, icons and supplied images | The two source `assets/` directories |
| Shared typography and responsive reading scale | `source/governance-lab-series/assets/site-typography.css`, attached by `build.py` before the editorial pass and final search |
| Shared sidebar order and page links | The `core` groups in `source/governance-lab-series/assets/site-search.js`; the guide and start templates retain the same static order |
| Search extraction and relevance vocabulary | `build_site_search.py`, `search_relevance.py` and `assets/search-engine.js` in the Lab source folder |

The approved writing uses version 3 from [the opening comparison](review/opening-style-comparison.html): natural pauses, varied sentence lengths and a conversational explanation of the reasoning. `editorial-copy.json` holds each original passage and its adopted wording. It covers the guide, essays, reference explanations, Craft, learning and practical pages, company and research pages, and the linked robot series. The comparison preserves the earlier sample for reference.

To edit an adopted passage, update its `editorial` field. Keep exact formal statements, record bodies, code, quotations and example conditions intact. Optional `link_labels` connect revised wording to the original link destinations. If a renderer changes an original passage, update the corresponding entry too. The build fails on an unmatched or conflicting entry rather than silently dropping the adopted prose.

Run the top-level build after changing any surface. It renders examples, Craft, essays, references, the guide and maps, applies the adopted prose, then compiles search from the final pages. The renderers retain their source-binding and construction checks. The editorial stage checks captured record bodies, code blocks, quotations and formal definition cards. Packaging resolves local HTML/CSS dependencies, follows legacy redirects, checks duplicate IDs and matches search fingerprints to the final pages.

The build renders in an isolated temporary directory and leaves maintained source files unchanged. The imported generated HTML supplies the existing navigation anchors during initial construction; all deployable guide, library and Craft pages are rendered again. Build logs are local diagnostics, not files published with the site.

The sidebar follows this order: Getting started, Governance, The Lab model, Practical guides, Software design, Expanded essays, Reference, About CyberAlchemy. Craft chapters and the library's essay and catalog links stay within their subject groups. The desktop tree keeps the selected topic visible; compact screens retain their existing browse disclosure. The latest change is recorded in [NAVIGATION-REVIEW.md](NAVIGATION-REVIEW.md).

The Paper & crimson edition uses the approved monospace reading style, warm paper surfaces, crimson navigation accents and a shared light/dark preference. The original typography sheet remains a foundation; `assets/paper-crimson/appearance.css` supplies the approved reading sizes and responsive shell. Diagram geometry is preserved, and wide figures provide visible horizontal-scroll guidance and full-size links. The earlier type-scale review remains recorded in [TYPOGRAPHY-REVIEW.md](TYPOGRAPHY-REVIEW.md).

The image variants and generated illustrations are supplied assets. `optimize_images.py` is an optional image-maintenance tool requiring Pillow; image generation and image optimization are not part of an ordinary documentation rebuild.

## Captured records and the Markdown edition

The reference selection preserves the documentation's **8 October 2026** capture scope. `IMPORT-MANIFEST.json` records the original imported bytes; portability changes to build tools are described in [MIGRATION.md](MIGRATION.md). Rebuilding does not update admitted definitions or accept documentation specimens into Project State.

The prose edition is dated **12 October 2026**. The release manifest records its voice and source digest. `dist/governance-lab-series/research/editorial-edition.json` records the changed passages, page fingerprints and preserved formal scope. The original capture baseline stays separate from the revised explanatory essays.

Refreshing the source selection is a separate editorial operation. `build_research.py` requires an explicit `--repository` argument; it is never run by the normal build. Review source selection, claims, reading aids, examples and the preservation baseline together before adopting a newer snapshot.

The [repository-readable Markdown edition](../docs/lab/README.md) remains available. To refresh its imported pages from a reviewed successful website build, run:

```bash
python3 tooling/docs/import_site_docs.py --site website/dist/governance-lab-series
```

That command replaces imported Markdown pages; review the resulting changes and import manifest. It is not part of the website build. The website and Markdown edition retain their own directly maintained navigation indexes.

## Deploy

See [DEPLOYMENT.md](DEPLOYMENT.md). The site is ordinary HTML/CSS/JavaScript with no server runtime. Any static host can serve `website/dist`; a manually triggered GitHub Pages workflow is included. Building locally does not publish anything.

The reader response form downloads answers locally. It does not send responses to a service. Reader comprehension, actual screen-reader operation and actual Safari still need their previously planned manual reviews.

## Craft × Lab hackathon

The event page is built at `governance-lab-series/hackathon.html`, with an announcement on the Lab homepage, shared navigation, search coverage, full rules downloads, and calendar reminders. It uses the existing KEP design tokens and site typography. Registration and building open **13 October 2026 at 18:00 Brasília time (UTC−3)**. Registration/submissions close **23 October at 23:59**. Voting opens **24 October at 12:00** and closes **25 October at 18:00**; provisional results are at 18:30, reports close at 20:00, and final results are due by 23:59. Entries are individual, with one new project per person and one final vote per registered participant. Minimum age is 18. Organizer contact is `hello@cyberalchemize.com`.

Edit `hackathon.json` to supply the real `registration_url`, `submission_url`, `gallery_url`, and `voting_url`. Missing links render as “Coming soon”; configured links must use HTTPS. Rebuild the whole site after changing them. The renderer validates the confirmed timestamps against their date fields and the Brasília offset. Rules v1.0 were confirmed on 12 October 2026. The prize is reimbursement of up to US$200 for one month of ChatGPT Pro at the US$200 tier, against a receipt; winners contact the organizer within seven days and reimbursement is due within fourteen days after valid receipt/payment details are received. The funding cap includes taxes and fees. Identifiable operational records are deleted thirty days after prize delivery and dispute resolution.

Maintained sources are `source/governance-lab-series/templates/hackathon.html.in`, `assets/hackathon.css`, the `research_pages.py` renderer, and the two `downloads/hackathon-rules` files. The renderer writes `.ics` reminders in UTC in the isolated build stage. `hackathon.json.calendar_revision_at` supplies their fixed revision timestamp; update it when the event calendar changes, so identical source produces identical release bytes. Private participant identities, submissions, and ballots stay in the organizer’s Google account; this static page does not collect them or enforce voting by itself.

The hackathon page keeps the earlier two-column opening and idea sketch, with one ambitious invitation and a single challenge action. Six expandable project prompts and compact date cards follow; voting closure and the final-result deadline are both explicit. Prize details sit beside the entry information. Its copy follows the requested natural editorial voice, with repeated pitches removed. Supporting event text is at least 18 px on desktop and 17 px on compact screens; detailed prize terms, the checklist, and rule summaries remain available through native disclosures. The full PDF and Word rules retain the confirmed terms. All eight existing section destinations remain searchable and linked.

See [the Google Forms setup guide](GOOGLE-FORMS-SETUP.html) and [copy-ready form text](FORMS-COPY.txt) for the account-side work. Current product frontier: the event page, confirmed rules, and complete local release package. Remaining operational work belongs to the event organizer: configure/link the three forms, check the participant roster, publish the project gallery, test access and ballot controls, and publish the reviewed site on its intended host. Missing form links do not block page construction; a live ballot must not open before its access controls are checked.

## Local review of the complete website

All fifteen findings from the October review have local implementation and verification evidence. See the [fix report](review/2026-10-12-site-fixes/REPORT.md) and [completion audit](review/2026-10-12-site-fixes/COMPLETION-AUDIT.md) for the exact release, preserved records, search scores and remaining reader/device checks. This review does not publish the site or establish full accessibility conformance.


## Runtime documentation input selection

The runtime renderer reads one explicit selector from `site.json`, whose SHA-256 is passed to child build steps. The selector pins the reviewed narrative, public source map and independent peer review; there is no implicit newest edition. Keep the narrative as the prose owner. Register all fourteen article routes in navigation, search and the deployment resource descriptor, then import the resulting final site into Markdown.

The public runtime evidence namespace contains only the exact reviewed files. These are retained documentation snapshots and do not establish current executable eligibility, admission or runtime qualification. Preserve fenced commands, diagram meanings, unsuccessful observations and claim limits through editorial and importer changes.

## Paper & crimson and guided reading paths

The approved design is integrated into the ordinary build, after adopted editorial content and exact record-page generation and before final search. It does not depend on the separate experimental preview or a neighboring repository.

- `paper_crimson.py` applies the maintained appearance, preserves unique content and old fragment destinations through the company-brain consolidation, versions local assets and refreshes final fingerprints.
- `reading_paths.py` renders six guided paths into the current documentation shell, retaining runtime navigation. The short entry hub has one primary chooser; the conceptual primer lives in the existing company-brain article.
- `diagram_presentation.py` maintains the verified graph-label wrapping and visible scroll/full-size controls.
- `source/governance-lab-series/assets/paper-crimson/` holds approved CSS, theme/reading behavior, logos, favicon and knot vectors. Reading progress stays in the browser; all steps and links remain available without JavaScript.
- The final search includes both the current runtime documentation and the new paths. The homepage total is derived from that complete index.

The existing documentation routes, fragments, 454 exact record bodies, 14 runtime articles and selected captured sources are preserved. The release manifest and portable ZIP are generated from the integrated edition; building remains a local operation and does not publish the site.

Local verification evidence for applying the approved edition is in `output/playwright/paper-crimson-current-20261014/` at repository root. The migration check reconciles edited explanatory pages against their recorded canonical owners, while retaining exact formal/runtime bodies and captured source bytes.


## Company-brain consolidation

`company_brain_migration.py` consolidates the generated, adopted prose before final search. It moves the existing five-role map and knowledge/work/decisions cycle into `company-brain.html`, puts that article in Getting started navigation, preserves the single detailed handoff, and reconciles the primer into the same article. Start here becomes one six-path chooser with compact direct lookup links. The first Understand the Lab step opens the conceptual introduction.

Seventeen homepage fragment identities and the retired Start here headings retain meaningful destinations. Same-page equivalents have real alias targets; cross-page moves use ordinary fallback links shown by `:target`, enhanced with a small redirect script that preserves queries and supports file-origin delivery. The homepage announcement/status behavior remains separate.

Exact pre-migration HTML is retained in `migrations/company-brain-20261014/`, outside the shipped reading/search surfaces. The build emits `research/company-brain-migration.json`, including the per-block reconciliation ledger, fragment maps and snapshot fingerprints. Intentional consolidation preserves unique knowledge and destinations rather than duplicate public paragraph/link multiplicity. The normal checks enforce the single chooser, moved figures and working old fragment targets. Evidence is at repository-root `output/playwright/company-brain-migration-20261014/`. Building does not publish anything.
