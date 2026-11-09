# Engineer Assessment software and question meanings

Status: **superseded exact source cut, 2026-10-26**. The [76-meaning access successor](../access-meaning-v2/README.md) is the selected current candidate cut. The editable source remains the separate [Engineer Assessment workspace](../../../../../../engineer-assessment/README.md). This Lab snapshot copies seven source files: canonical definitions, ontology, software definition coverage, question lifecycle, data model, API contract and experiment operations. It is not a new canonical Lab registry version.

The 72 task-local meanings are split into three [Define v2 requests](define-v2/request-01.json), [part 2](define-v2/request-02.json) and [part 3](define-v2/request-03.json), each containing 24 closed `propose` dispositions. Each request binds the exact same seven source files plus the Lab registry observed during capture. The historical [Packs](define-v2/package-01/manifest.json), [part 2](define-v2/package-02/manifest.json) and [part 3](define-v2/package-03/manifest.json) were produced by `capture-snapshot` and `prepare`; `inspect-package` verified 13 required members per Pack, and `reconstruct-local` succeeded for all three. The Pack digests are:

| Part | Pack SHA-256 | Root SHA-256 |
| --- | --- | --- |
| 01 | `bb9a804263a8ccdb1f6c87074d5166c7bd5dfab3c047c5888bcee6fdd60cff98` | `d5b0e5000e18b40e674d60bdb672a36300716e474f24d1f953c07f1165bb1609` |
| 02 | `dec5c715cc0fff15d5dcff4925d512824168240351a6f8c13b6dabb92e32120d` | `b531ab73be30baee8f1be7ae634e4466acc12457be4ae8fc02b887624fa2cacf` |
| 03 | `edb6a9a8e9e2a8c0889b9fe1f036d6082584698f2ee03068b0e3ae6a4111e3f0` | `56dda01fd34f17b9ac4e584114a7f44993189ff85a5a9d9b666fe4f88fdd154c` |

`prepare` reported `prepared-with-gaps`: `inspect-preparation=ready`, `prepare-owner-review=blocked` (`historical-capture`, `current-host`) and `governing-application=blocked` (`actual-governing-route`). `inspect-package` says `current_use_readiness=not-established`. The default v1 `./define/define doctor` separately fails due to a source-digest mismatch in `authority/project-state-transitions/current.json`; the explicit v2 `doctor` verified its 29 selected runtime files and reported preparation available, with live host qualification and release adoption pending. No owner semantic decision, Lab definition admission, participant-collection approval or employment use follows from these Packs.

The question-specific [rule, use-case, operation and workflow design](software/QUESTION-LIFECYCLE.md) is a source snapshot, not a completed run. Release counts, reviewer principals, similarity thresholds, trial precision and case monitoring triggers remain open selections. The earlier [60-meaning cut](../software-meaning-v1/README.md) is superseded.
