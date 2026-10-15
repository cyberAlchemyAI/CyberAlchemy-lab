# Adopted editorial edition

Date: **12 October 2026**

This review records the prose-adoption build. The later sidebar revision and its build are recorded in [NAVIGATION-REVIEW.md](NAVIGATION-REVIEW.md).

## Writing selection

The user selected version 3 from the opening comparison for the site's explanatory text: natural pauses, varied sentence lengths, clear reasoning and a voice suited to reading on a phone. The earlier comparison stays available as an archive of that choice.

The maintained edition contains **639 authored passage entries** in `editorial-copy.json`. The renderer applies them in **16 HTML surfaces**, including the guide alias. The latest build replaced **950 passage occurrences**. Repeated explanations in the reference library account for the difference between authored entries and occurrences. The four revised opening subtitles were adopted in the templates with their anchor identities preserved.

The prose covers the guide, all eight essays, reference introductions and explanations, Craft, learning and practical pages, company and research pages, and the linked robot series. Exact statements, formulas, numeric specimens, control labels and short technical summaries retain the wording needed for their purpose.

## Build and preservation

The complete static build succeeded. Search was compiled after the editorial stage and retains **690 entries**. The build matched each indexed source fingerprint to the final rendered page and resolved the deployment's local resources.

The editorial stage compared all **454 reference record bodies** against the captured baseline, excluding explanatory reading aids. They are unchanged. It also compared code blocks, quotations and formal definition cards before and after the prose pass. All comparisons matched. The original 8 October source selection and authority standing were preserved.

The incident still uses Northstar, `status = active`, fixed snapshot S1, output E12 and method 2. Its comparison establishes 200 missing identifiers among 10,000 required identifiers. Cause, wider impact and recovery remain unresolved. The capacity example retains strict inequality, unchanged supplied capacity during Calculation, and a separate state-changing reservation Operation.

The package contains **631 files**, including the release manifest and editorial receipt. ZIP integrity inspection found no damaged member.

Archive SHA-256 at prose adoption:

```text
b8f170c45625e67524223726ad751538b18b67a62f58dfd967175f5a12c0495d
```

The current build receipt is `artifacts/build.json`. The editorial receipt is `dist/governance-lab-series/research/editorial-edition.json`; the release manifest identifies the adopted copy by digest.

## Repository-readable edition

The Markdown importer refreshed **37 pages**, including all eight essays, from this final build. It reported **0 unresolved links** and **0 changed digest-bearing captured sources**. It records the editorial edition and import date, and preserves paragraph pauses from the HTML.

The importer now reads each essay's stable source name from its rendered article. A deployment build does not need to ship the original draft TXT files for its Markdown import to include the essays.

## Changed passages by surface

| Surface | Replacements |
| --- | ---: |
| governance-lab-series/governance-lab-reference.html | 142 |
| governance-lab-series/governance-lab-series.html | 142 |
| governance-lab-series/lab-reference-library.html | 324 |
| craft-documentation-proposal/craft-model.html | 141 |
| governance-lab-series/index.html | 15 |
| governance-lab-series/company-brain.html | 23 |
| governance-lab-series/research.html | 14 |
| governance-lab-series/start-here.html | 19 |
| governance-lab-series/incident-walkthrough.html | 16 |
| governance-lab-series/concept-comparisons.html | 11 |
| governance-lab-series/read-record.html | 9 |
| governance-lab-series/prepare-incident-assessment.html | 9 |
| governance-lab-series/prepare-definition.html | 10 |
| governance-lab-series/resume-agent-work.html | 11 |
| governance-lab-series/record-examples.html | 9 |
| robot-learning-series/robot-learning-series.html | 55 |

## Review scope

This is a prose adoption and local build review. The integrity comparisons establish preservation of the selected formal content. They do not establish new runtime behavior or reader-comprehension results. No implementation suite, commit, push or external deployment was performed.
