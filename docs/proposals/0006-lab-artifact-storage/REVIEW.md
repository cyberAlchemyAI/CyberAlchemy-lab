# Storage design review

Mode: Concept Layer Optimizer Validate. One proposal track, one independent read-only Balancer (`/root/artifact_storage_balance`) and one root repair/reconciliation. No recursive expansion beyond the finite review. Verdict: **flag: recommended design fit; implementation and performance unverified**.

## Role trace

Proposer claim: reuse event-sourced immutable commits, add SQLite as a disposable artifact query projection and generate selected files. Evidence: current Lab transactions, ontology storage and disposable graph read model. Assumptions: exact byte closure and generic package/projector/materializer interfaces can be implemented under existing authority contracts or reviewed successors.

| Named Balancer objection | Evidence | Reconciliation |
| --- | --- | --- |
| Ontology representation becomes artifact authority | v4 README limits conformance/source authority | Accepted: dedicated artifact command/authority path; explicit representation adapter. |
| SQL index solves file proliferation | Index leaves canonical files in place | Accepted: package new operational content and selectively materialize files; preserve old sources. |
| Rows and editable files become two writers | Independent commits diverge | Accepted: one canonical path; file edits become exact-base drafts. |
| Parsed JSON preserves original bytes | Lab source capture stores parsed material/hashes | Accepted: exact byte envelopes, distinct semantic hashes and complete dependencies. |
| DB commit/export form one atomic action | Separate storage visibility points | Accepted: canonical commit followed by recoverable immutable generations and distinct receipts. |
| Histories always share current state | Ontology can lag artifact commit | Accepted: separate stream watermarks/cuts and explicit freshness. |
| Foreign keys/hashes establish authority | Structural integrity is not owner authorization | Accepted: canonical source/trust verification and independent replay obligations. |
| One file per transaction bounds growth | Transaction count and cumulative history still grow | Accepted: no storage bound; delta/segment/retention designs require selected contract fit. |

Root repair: the SQL body cache is optional; projected artifact/schema/evidence byte hashes resolve through canonical source locators even without cached payload rows. This prevents compulsory duplicate storage merely to provide indexes.

The Balancer independently recommends option C for the present repository. A canonical SQLite event/content store remains valid if database-first custody, migrations, backup/restore, logical exports and measured workload benefit are explicitly selected. No performance contest has run.

## Concept layers and recomposition

Purpose: trustworthy artifact continuity. Capability: governed artifact management. Workflow: prepare/validate/commit/project/materialize. Artifact protocols: exact content, package, generation and file manifest. Operations: current commit implementation or future reviewed storage adapter, SQL generation and export publication.

Inputs: current exact sources/contracts, candidate body bytes, authority scope, expected head and selected dependencies. Outputs: canonical committed revision content plus attributable, rebuildable query and file generations. Semantic/governance ownership stays with its scoped contracts/history. The ontology adapter adds representation rather than absorbing that ownership.

Every roadmap domain can remain an ordinary exact artifact carrier; SQL provides indexes over heterogeneous content. This recomposes with profile selection, whole-candidate closure, publisher, workflows, context, ontology and Product packaging. Missing glue is named: package writer/decoder, generic publisher, projector, ontology adapter and file materializer. Their implementation is not claimed.

## Technique trace

| Technique | Hook / reason | Inspected state and output | Decision / readiness |
| --- | --- | --- | --- |
| abstraction_level_guard | before_accept_split / always | Event model, storage engine, ownership and views separated | pass / unchanged |
| recomposition_proof | before_verdict / always | Current artifacts/history versus command, package, SQL and export interfaces | flag / implementation glue named |
| evolution_profile | before_verdict / source growth and new scopes | Packaging and exact profile boundaries; canonical SQLite retained as measured alternative | pass / unchanged |
| frame_expiry_note | before_verdict / always | Database-first custody/concurrency/workload triggers below | pass / unchanged |
| cognitive_load_check | after_balancer_pass / three competing choices | One write path and two derived consumption surfaces; catalog navigation retained | pass / unchanged |
| requisite_variety_check | before_verdict / heterogeneous contracts and bytes | Generic envelope plus exact carriers; no per-type SQL authority or universal payload | pass / unchanged |
| boundary_object_check | after_balancer_pass / source, artifact, ontology owners | Source-qualified identity, distinct scope and representation join | pass / unchanged |
| concept_vs_knowledge_status | before_accept_split / missing workload proof | Source-inspected architecture fit versus unmeasured storage/performance | flag / no performance claim |
| premortem_pass | before_verdict / medium-high custody risk | Lossy content, false authority, stale views and dual writes below | flag / guards explicit |
| set_based_tournament | before_pitch_off / skipped | Validate comparison with one independent critique; no empirical tournament | skipped-with-reason / unchanged |
| navigable_result_check | before_verdict / always | Proposal, comparison, architecture, schema catalog and evidence | pass / next route explicit |

## Premortem and expiry

Likely failure: exact content is lost because a convenient index/import envelope is assumed complete. Guard: retain original byte content and all replay/schema/evidence dependencies, or expose missing closure and block use requiring it.

Other concrete failures: writable generated files diverge from SQL; package commits precede failed exports; an ontology projection is treated as source authority; cumulative snapshots consume excessive space. Guards: exact-base draft ingestion, distinct commit/projection/export receipts, scoped adapter provenance, and measured packaging/retention design with preserved history.

Expiry triggers: Product chooses database-first custody, measurements establish severe transaction/inode pressure, multi-host/concurrent write scope is selected, canonical format or source ownership changes, or a carrier requires an incompatible retention/delta rule. Re-run the affected design before migration.

Next route: fit protocol fields to C01/C02/S01/S02, then implement an isolated package/projector/materializer vertical slice under its selected authorization and validation scope. Detailed workflow protocols follow storage and authority fit. No database activation or storage migration is requested by this review artifact.
