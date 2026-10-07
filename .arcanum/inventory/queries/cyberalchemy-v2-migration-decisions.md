# CyberAlchemy v2 migration decision index

This view traces the decisions governing migration from `cyberAlchemy-v2` to
CyberAlchemy Lab. Decision records, authority registries, and bound receipts
remain authoritative; this page only makes their current relationship visible.

## Decision surface

- Machine decision records under `docs/decisions/`: **76**
- Additional repository-foundation decision: **1** Markdown record
- Migration candidate packages: **26**
- Migration execution evidence packages: **79**
- Migration plans: **6**
- Exact contracts in the current migration registry: **83**

## Governing decisions

| Layer | Recorded choice | Current effect | Source |
| --- | --- | --- | --- |
| Repository foundation | Start CyberAlchemy Lab with clean local history; retain `cyberAlchemy-v2` as external source and evidence | Accepted foundation; no wholesale copy or rename authorized | [Decision 0001](../../../docs/decisions/0001-repository-foundation.md) |
| Product identity | Use active Craft naming while preserving stable legacy DS identifiers through explicit lineage | Owner selected; naming and lineage policy only | [Decision 0002](../../../docs/decisions/0002-craft-rename-scope/DECISION.md) |
| First vertical | Canonical append-only ontology events, per-subject streams, graph commit cursor, typed resulting-state events, Rust reducer over JSON, checked-in calculated projections, separate governance streams, Lab-native witness before legacy migration | Decision gate complete; architecture selection only | [Decision 0003](../../../docs/decisions/0003-event-sourced-ontology-first-vertical/DECISION.md) |
| Lab architecture | Accept the RN-2 aligned context/artifact, platform/environment, and Craft migration graph with LEANS-2 sequencing | Owner selected planning baseline | [Decision 0004](../../../docs/decisions/0004-lab-architecture-selection/decision.json) |
| Definition normalization | Do not infer bounded contexts; use one evaluation envelope with owner-local profiles; make Definition/v1 the first vertical; preserve DS identifiers as lineage aliases | Owner selected planning model | [Decision 0012](../../../docs/decisions/0012-normalize-01-defaults/decision.json) |
| Semantic admission | Admit exact source cohorts, Definition versions, context vocabulary, owners, artifact types, lineage, and Craft identity in bounded overlays | Multiple owner-admitted decisions; each grant is limited to exact bytes and stated meaning | [Decisions 0013-0031](../../../docs/decisions/) |
| Ontology Product | Approve the exact frozen and tested Ontology Product candidate | Product approval only | [Decision 0042](../../../docs/decisions/0042-ontology-product-v1-product-approval/decision.json) |
| Local event runtime | Authorize one local CLI instance and copy the approved navigation graph into per-subject event files | Local instance only; no general legacy import or cutover | [Decision 0049](../../../docs/decisions/0049-ontology-event-runtime-activation/decision.json) |
| Source runtime v4 | Approve an isolated source-qualified migration and event-update prototype covering 21 packages, 815 nodes, 1,210 relations, and 422 supporting documents | Product approval only; runtime adoption, consumer cutover, and source retirement remain false | [Decision 0050](../../../docs/decisions/0050-source-runtime-v4-product-approval/decision.json) |
| Remaining contract review | Approve the exact reviewed set of 83 contracts | Review and adoption selection; no deployment, deletion, publication, or source retirement | [Decision 0051](../../../docs/decisions/0051-remaining-83-review-approval/decision.json) |
| Migration contract registry | Admit the 83 exact contracts into the migration registry | Authoritative selection within this migration; consumer activation is not applied | [Decision 0052](../../../docs/decisions/0052-remaining-83-contract-admission/decision.json) |
| Full Definition queue | Admit all 85 pending Definition versions, including all 70 reconstructed migration versions, plus 58 exact source selections | Definition registry closed for the indexed queue; no carriers or consumers activated | [Decision 0053](../../../docs/decisions/0053-full-definition-queue-admission/decision.json) |
| Definition-complete Lab model | Admit the exact integrated Artifact Type, Relation Kind, endpoint, and model contracts | Bounded contract and model admission; no runtime or migration cutover | [Decision 0070](../../../docs/decisions/0070-definition-complete-lab-model-admission/decision.json) |
| Operational foundation | Admit nine foundation artifact instances and thirteen Typed Relation instances | Durable root admitted; two Project histories declared empty at cursor zero; no runtime activation | [Decision 0071](../../../docs/decisions/0071-cyberalchemy-lab-operational-foundation-admission/decision.json) |
| Project State bootstrap | Admit Project history carriers, one event in each stream, and the first successor Project State | Decision 0071 is recorded at cursor one; the initial state is historical; Decision 0072 awaits a later successor | [Decision 0072](../../../docs/decisions/0072-project-state-bootstrap-admission/decision.json) |

## Current state

| Surface | State | Meaning |
| --- | --- | --- |
| Whole-repository copy candidate | `test-candidate-built` | The 40,673-file additive copy envelope was tested as a candidate but was never approved or executed. Its Repository Migration Manifest Definition is now admitted, while its Artifact Type and execution authorization remain unresolved. |
| Definition registry | `188 versions / 182 current identities` | The live registry includes Decisions 0053, 0064–0066, and 0072. The indexed Definition queue is empty. |
| Artifact Type registry | `129 admitted versions / 115 current identities` | Decision 0072 postimage includes Project semantic and governance history carriers. Type admission does not imply instance admission. |
| Relation Kind registry | `40 admitted kinds` | D70 closed axes and exact endpoint pairs govern later Typed Relation instances. |
| Foundation artifact and relation instances | `12 artifacts / 15 Typed Relations admitted across D71–D72` | Nine artifacts and thirteen relations come from D71; three artifacts and two relations come from D72. Instance effects are exact and bounded. |
| Project State and histories | `D71 successor current; cursors 1 / 1` | D72 made the initial state historical and admitted one semantic plus one governance event. Decision 0072 is not included in the current successor. |
| Migration contract registry | `83 exact contracts admitted` | The registry contains 26 Artifact Types, 25 profiles, 25 relation kinds, and 7 derived surfaces. The grant applies to contract selection within this migration. |
| Contract consumer | `not-applied` | No bounded consumer has been connected, validated against real inputs, or activated. |
| Source runtime v4 | `product-approved prototype` | Historical product tests passed, but Rust tests were not rerun and the local runtime was not reverified at approval time. Operational use still requires environment restoration and fresh acceptance. |
| D65 epoch-002 cutover | `conditional-authorized; not ready` | The authorization covers only an exact 7-to-11 canonical-event migration. Six prerequisites remain missing; runtime activation, migration, and cutover are all recorded as not performed. |
| General CyberAlchemy v2 migration | `not complete` | No decision proves whole migration completion, general consumer cutover, publication, deployment, deletion, or source retirement. |

The current authoritative contract set is
[`authority/decisions/migration-contracts/v1/registry.json`](../../../authority/decisions/migration-contracts/v1/registry.json).
Decision 0052 does not infer Definition or carrier admission. Later decisions
independently admitted bounded Definitions, carrier contracts, and foundation
instances. The migration-registry consumer remains unapplied; general migration
activation and domain actions remain ungranted by those admissions.

## Evidence collections

- [Migration candidates](../../../evidence/migrations/cyberalchemy-v2-to-lab/candidates/)
- [Migration executions](../../../evidence/migrations/cyberalchemy-v2-to-lab/executions/)
- [Migration plans](../../../docs/migration-plans/)
- [All decision records](../../../docs/decisions/)

## Next recorded boundary

For the migration contract registry, the remaining step is to connect one
bounded consumer, validate its actual inputs and exact carrier requirements,
and then seek a separate activation decision. For durable Project State,
Decision 0072 needs a later governed successor. These are separate tracks;
neither is implied by the repository inventory or this navigation view.

This inventory view does not grant admission, activation, cutover, migration
completion, publication, deployment, deletion, or source-retirement authority.
