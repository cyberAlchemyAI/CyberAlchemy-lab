# R0 — source and effective-state baseline

Status: research complete with explicit unresolved version references, 2026-10-06. Authority effect: none. This is a read-only source audit, not a new admission or runtime observation.

The [selected-source manifest](r0-source-manifest.json) binds 50 exact local files by SHA-256. Its scope is the first three governance queries, not the whole repository. The [version-reference audit](r0-version-ref-audit.json) records one important D73 traceability gap separately.

## Inventory currentness at inspection

| Derived surface | Observation | Use in this baseline |
| --- | --- | --- |
| [Path inventory](../../../.arcanum/inventory/inventory.json) | Read-only freshness check passed at **10,812 files** in the inspected working tree. | Path and digest navigation only. The count is a snapshot, not a continuously true total. |
| [Governance repository map](../../../authority/governance/candidates/0001-three-lens-module/repository-map.json) | Read-only check passed: **44 zones**, **487 exact governed-match paths**, and **10 source-linked zone connections** over the same 10,812 paths. | Zone navigation only. Its exact governed status lookup covers D71–D72 and does not resolve D73. |
| [Content map metadata](../../../.arcanum/inventory/content-map-info.json) | Index reports **10,797** source files; its source-manifest digest differs from the current path inventory digest. | Stale for current code-declaration claims. S2 must refresh or inspect source files directly. |

The inventory covers tracked and present non-ignored untracked files. It excludes ignored files, Git internals, empty directories, and its self-referential generated outputs. A complete path list is not a complete ontology or evidence of a file's admission state.

## Decision and overlay matrix

Effective state below comes from the cited owner decision, admission bundle, and overlays. Embedded `candidate` text in copied records remains source provenance.

| Epoch | Admitted effect | Project State and history result | Runtime boundary |
| --- | --- | --- | --- |
| [D70](../../../docs/decisions/0070-definition-complete-lab-model-admission/decision.json) / [bundle](../../../authority/admissions/definition-complete-lab-model/v1/bundle.json) | 93 Artifact Type contracts, 40 Relation Kinds, one integrated Governed Model instance; no Typed Relation instances. | Establishes the contract base. The D70 registry postimage has 127 admitted Artifact Type contract versions: 113 current and 14 historical. The Relation Kind registry has 40 current entries. | Zero activations. |
| [D71](../../../docs/decisions/0071-cyberalchemy-lab-operational-foundation-admission/decision.json) / [bundle](../../../authority/admissions/cyberalchemy-lab-operational-foundation/v1/bundle.json) | Nine artifact instances and 13 Typed Relation instances. | Initial `project-state:...:decision-0070` admitted-current at its epoch. [History declaration](../../../authority/admissions/cyberalchemy-lab-operational-foundation/v1/history-declarations.json) names empty logical semantic and governance streams at cursor 0; these are not event instances. | Zero activations. |
| [D72](../../../docs/decisions/0072-project-state-bootstrap-admission/decision.json) / [bundle](../../../authority/admissions/project-state-bootstrap/v1/bundle.json) | Two Project history Definitions and Artifact Types, three artifact instances, two Typed Relations. | Admits successor `project-state:...:decision-0071`, makes the D71 state historical, and records one semantic event and one governance event at cursor 1. The state includes D71, not D72 itself. The D72 registry postimage has 129 admitted Artifact Type contract versions: 115 current and 14 historical. | Zero activations. |
| [D73](../../../docs/decisions/0073-first-governed-agent-work-episode-admission/decision.json) / [bundle](../../../authority/admissions/first-governed-agent-work-episode/v1/bundle.json) | 22 artifact instances and 23 Typed Relations; the Agent Instance and Session are closed. | Admits successor `project-state:...:decision-0072`, makes the D72 state and cursor-1 histories historical, and advances separate semantic and governance histories to cursor 2. The state includes D72, not D73 itself. A bounded operational Ontology has two Nodes, one projected `member-of` Edge, a Cut, and a View. | Zero activations; no ongoing Agent memory or service is established. |

The effective [Definition registry](../../../authority/definitions/registry.json) currently records 188 version entries and 182 current identities. Those counts are registry scope, not the number of ontology nodes to create. All four bundles and decisions are in the 50-file manifest.

## Exact Lifecycle path for the first graph slice

```text
D71 initial Project State (decision:0070; now historical)
  ← D72 admitted relation.successor-of
D72 Project State (decision:0071; now historical)
  ← D73 admitted relation.successor-of
D73 Project State (decision:0072; current in this inspected admission chain)

Project semantic history: cursor 0 declared empty → event 1 → events 1, 2
Project governance history: cursor 0 declared empty → event 1 → events 1, 2
```

The [D72](../../../authority/admissions/project-state-bootstrap/v1/artifact-instance-admission.json) and [D73](../../../authority/admissions/first-governed-agent-work-episode/v1/artifact-instance-admission.json) overlays explicitly mark predecessor transitions without mutating predecessor bytes. The two admitted successor Typed Relations have exact source and target identities. Their version labels need the resolution described below before the graph claims exact-version traversal.

## Unresolved version-reference finding

The D73 copied Typed Relation records contain **10 endpoint `version_ref` values, out of 46 endpoints, that differ from every version for the same subject identity in the D71–D73 artifact admission overlays**. They all point to D71/D72 external subjects using `@candidate.1` where the admitted overlays name `@foundation.1` or `@bootstrap.1`. The D73 `state-successor` target is one example: `project-state:...:decision-0071@candidate.1` versus the admitted `@bootstrap.1`.

The D73 Project Ontology Node also represents the exact D71 Project bytes by matching digest, but labels its represented subject `@decision-0071` while the D71 admission overlay names `@foundation.1`. The inspected [candidate validator](../../../authority/agent-work-episodes/candidates/0001-first-governed-agent-context/validate.py) checks relation endpoint identity and kind in this path; it does not compare endpoint `version_ref` with the admitted overlay there. The byte-digest audit found no mismatches in the checked D71–D73 source and admitted copies. These observations do not reverse D73 admission. They require an explicit version-alias interpretation or a governed successor/correction before exact-version graph claims.

## Initial coverage obligations

| Query planned for C1 | Required source classes | Current gap to expose |
| --- | --- | --- |
| `show Lifecycle` | State and event-history Definitions/Artifact Types; D71–D73 states, decisions, overlays, successor relations, histories; [governance projector](../../../authority/governance/candidates/0001-three-lens-module/project.py); D72/D73 apply scripts. | Version-label mismatch; candidate projector stops at D72; no reusable Project history writer or current runtime observer established by these decisions. |
| `why may Decision 0073 count?` | Authority/Policy/Decision Definitions; D73 owner decision and authorization, bundle, instance and relation overlays, exact effects and exclusions. | No general permission evaluator; decision admission is not action authorization. |
| `where did the Product Capability come from?` | Provenance Definition; D71 Product Thesis and Capability; admitted `relation.derives-from`; candidate/source copy and overlay digests. | Derivation does not establish realization binding, fulfillment, or effectiveness. |

## Exclusions and next step

This baseline does not inspect every code declaration, adopt the Rust graph read model, refresh the stale content index, or claim a live ontology service. It does not rewrite the D73 admitted copies or infer a version alias. **C1 is next:** specify the three query responses and their claim ceilings. **S1 must resolve or fail closed on the version-reference finding before L0 can claim exact-version paths.**
