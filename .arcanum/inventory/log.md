# Inventory log

## 2026-10-05 — Initial repository inventory

- Installed a repository-local inventory package at `.arcanum/inventory/`.
- Added a deterministic builder that inventories tracked and non-ignored
  untracked working-tree files, with path, classification, size, and SHA-256.
- Indexed 8,213 files: 8,204 tracked and 9 non-ignored untracked files.
- Added generated repository and file-type index plus a `--check` validation
  mode. The manifest excludes itself to avoid a recursive digest.
- Source: the current repository working tree; paths and digests are recorded
  in `inventory.json`.

## 2026-10-05 — Internal content map

- Added a structural map and FTS5 full-text search index for repository files.
- Mapped Markdown sections and links, JSON/JSONL/YAML/TOML field paths,
  source declarations and imports, prose spans, PDF pages, binary metadata,
  and members nested in TAR and ar archives.
- Content is linked to its source by path and SHA-256. The validator checks
  physical file coverage, archive member sets and digests, SQLite row counts,
  and a full-text search probe.

## 2026-10-05 — Definition and migration status views

- Added a governed Definition status view over the live registry: 33 admitted
  versions, 31 identities, and 31 current lookup entries.
- Added a CyberAlchemy v2 migration decision index spanning the repository
  foundation, identity and event architecture choices, bounded admissions,
  Product/runtime approvals, and the 83-contract registry.
- Kept candidate, approval, admission, activation, execution, and completion
  states separate and linked every status summary to repository evidence.

## 2026-10-05 — Full Definition queue admission refresh

- Refreshed the Definition status view after Decision 0053 admitted all 85
  pending versions, including all 70 reconstructed migration Definitions.
- The live registry now contains 118 admitted versions and 112 current
  identities; the indexed pending Definition queue is empty.
- Recorded four candidate.2 current selections, 58 source admissions, the
  historical D53 Axiom source snapshot, and the remaining carrier and consumer
  boundaries.

## 2026-10-06 — Definition-complete model admission refresh

- Refreshed the repository manifest after owner-authorized Decision 0070
  atomically admitted the Definition-complete Artifact Type, Relation Kind,
  endpoint, and ontology/runtime integration model bundle.
- The admitted effect contains 93 Artifact Types, 40 Relation Kinds, 101
  resolved endpoint kinds, and one Governed Model instance; nine Artifact Type
  predecessors became historical.
- Rebuilt the structural content map and FTS5 search index. Exact current file
  and record counts are recorded in `inventory.json` and
  `content-map-info.json`.
- Decision 0070 activates no consumer or runtime, creates no Typed Relation
  instance, and performs no migration or cutover.

## 2026-10-06 — Reference instance slice candidate

- Added the first coherent candidate instance pack over the admitted model:
  CyberAlchemy Lab Product, CyberAlchemy v2 migration Project, Product
  Capability, research and experiment chain, implementation and work,
  ephemeral Agent session, durable Project State, Context View, and ontology
  projection.
- Materialized 91 candidate artifact instances across 32 semantic kinds and 44
  candidate Typed Relations. The ontology projection contains 12 nodes, nine
  edges, and separate semantic and governance histories per projected subject.
- All 12 deterministic schema, endpoint, qualifier, closure, projection,
  memory-boundary, non-collapse, and zero-effect checks pass.
- The pack remains candidate-only. It admits no instance or relation and
  activates no Agent, consumer, implementation, service, or runtime.

## 2026-10-06 — Operational foundation admission

- Added and owner-admitted Decision 0071, the smallest real operational root
  for CyberAlchemy Lab.
- Admitted nine exact artifact instances and thirteen exact Typed Relation
  instances for Intent, Product, Product Thesis, Product Capability, Project,
  Policy, Challenge Contract, initial Project State, and reusable Context.
- Declared separate semantic and governance Project history streams empty at
  cursor zero. Decision 0071 enters the first immutable successor Project
  State through governed events, avoiding a self-referential bootstrap digest.
- Activated no Agent, session, consumer, implementation, service, or runtime;
  generated no synthetic evidence or ontology projection.
- Rebuilt the path inventory, structural content map, and FTS5 search index.
  Exact current counts are recorded in `inventory.json` and
  `content-map-info.json`.

## 2026-10-06 — Project State bootstrap admission

- Added and owner-admitted Decision 0072, closing the first transition from
  the initial Decision 0070 Project State to the Decision 0071 successor.
- Admitted two Project-scoped event-history Definitions, two matching Artifact
  Types, three artifact instances, two Typed Relation instances, one semantic
  event, and one governance event.
- Kept Project histories distinct from ontology histories and preserved the
  semantic-versus-governance event boundary.
- Marked the Decision 0070 Project State historical and made the Decision 0071
  Project State current. Decision 0072 enters a later successor to avoid a
  self-referential state digest.

## 2026-10-06 — Repository-wide governance map

- Connected the existing path and content inventory to governance module
  candidate 0001 rather than installing a competing repository catalog.
- Added source-linked governance zones and exact status lookup routes for every
  path in the inventory selection, with a path lookup and coverage command.
- Added a repository integration view and linked it from the inventory index.
- Reconciled stale current-state claims in the migration decision query: the
  live Definition registry now has 188 versions and 182 current identities;
  Decisions 0070–0072 added bounded carrier, instance, relation, and Project
  State effects after the older D53 snapshot.
- The map and query remain non-authority navigation projections. Exact
  decisions, registries, overlays, and receipts retain their own effects.
- Activated no Agent, session, consumer, implementation, service, or runtime.
- Refreshed Definition drift evidence and the Definition status navigation view
  to 188 admitted versions and 182 current identities.

## 2026-10-06 — First governed Agent work episode candidate

- Materialized a candidate Decision 0072 Project State successor and first
  bounded Agent work episode from admitted-current contracts.
- Added 22 candidate artifact instances and 23 candidate Typed Relations for
  state histories, Context resolution, Work, assignment, principal, Agent
  profile and capability, classification, implementation, ephemeral Agent and
  Session, and a minimal ontology projection.
- Bound machine Agent lifetime to the Session and required session memory to
  expire. Durable continuity remains Project State, the immutable Context
  View, and the purpose-bounded Ontology View.
- Projected only the exact Decision 0072 Project State, migration Project, and
  their global `member-of` relation into the ontology surface.
- Excluded Context Lineage Record because its admitted v2 contract represents
  Context succession rather than Context View selection lineage.
- Candidate validation passes 9 checks. No artifact or relation is admitted
  and no runtime is activated.

## 2026-10-06 — Decision 0073 first governed Agent work episode admission

- Owner admitted the corrected reviewed candidate through Decision 0073.
- Admitted 22 exact artifact instances and 23 exact Typed Relations.
- Advanced the current Project State to Decision 0072 and advanced both
  Project event histories to cursor 2; prior state and history bytes remain
  preserved as historical versions.
- Closed the ephemeral machine Agent and Agent Session at the owner review
  boundary. Session memory was not retained; durable continuity remains the
  Project State, Context View, and Ontology View.
- Bound one editorial consistency repair that replaced a stale empty-ontology
  sentence with the already reviewed minimal exact ontology projection. The
  semantic scope did not change.
- Decision validation passes 10 checks. Runtime activations remain zero.
- Decision 0073 and its bundle must enter the next immutable Project State
  through the next semantic and governance events.

## 2026-10-06 — Decision 0073 Project State successor candidate

- Materialized `project-state:cyberalchemy-v2-to-lab-migration:decision-0073`
  as the immutable candidate successor of the admitted Decision 0072 state.
- Appended semantic event 3 for the first governed Agent work episode
  admission and governance event 3 for its exact owner authorization.
- Preserved the first two semantic and governance events byte for byte.
- Added the exact `successor-of` and `member-of` Typed Relations for the new
  state.
- Candidate validation passes 8 checks. Decision 0074 is excluded, no
  admission is applied, and runtime activations remain zero.

## 2026-10-06 — Approval and admission boundary audit

- Reviewed Decisions 0070 through 0073 against the admitted Decision
  Checkpoint, Decision Bundle, Authority Boundary, Decision, Decision Scope,
  User Decision Preference, Workflow Decision Profile, and Derived Refresh
  definitions.
- Found that separate decision identities generally preserved valid authority
  boundaries, while repeated human approvals introduced avoidable checkpoint
  churn.
- Confirmed that the single-checkpoint semantic definitions are admitted but
  six executable carriers are missing: Authority Boundary, Decision Bundle,
  Decision Checkpoint, User Decision Preference, Workflow Decision Profile,
  and Admission Transaction.
- Rejected the pending Decision 0074 approval pattern. A deterministic Project
  State successor declared by an authorized transaction should materialize in
  the same transaction without a second approval.
- Preserved Decisions 0070 through 0073 as immutable admitted history.
- Audit validation passes 10 checks and has no authority effect.

## 2026-10-06 — Governance transaction surface candidate

- Added the candidate Admission Transaction Definition with synchronized
  registry and index postimages plus downstream non-collapse drift checks.
- Materialized the six missing governance carriers: Authority Boundary,
  Decision Bundle, Decision Checkpoint, User Decision Preference, Workflow
  Decision Profile, and Admission Transaction.
- Added seven explicit v2 endpoint carrier successors required by the closed
  relation roles: Decision, Decision Scope, Policy, Generated Output, Project
  State, Project Semantic Event History, and Project Governance Event History.
- Extended three admitted Relation Kinds through candidate successors and
  added the orthogonal `relation.materializes-consequence` axis. The 41-axis
  candidate relation model passes exact endpoint, extension-rule, and
  no-collapse checks.
- Bound a realistic one-checkpoint example containing three independent
  Decisions, one owner response boundary, and one planned atomic Admission
  Transaction. Unresolved selected outcomes, authorization evidence, and the
  application receipt remain null rather than fabricated.
- Replaced sentinel hashes with exact Definition, Relation Kind set,
  thirteen-carrier target set, predecessor state, and already-materialized
  Decision 0073 successor digests. Not-yet-generated outputs remain null.
- Candidate validations pass 6 Definition checks, 9 relation checks, and 14
  integrated carrier and transaction checks. Nothing is admitted or applied,
  and runtime activations remain zero.

## 2026-10-06 — Decision 0074 governance transaction surface admission

- Recorded one final-review checkpoint with three independent Decision
  identities and one explicit owner authorization.
- Added the required Typed Relation/v3 representation closure repair for the
  already reviewed `materializes-consequence` axis. The correction added no
  relation kind, runtime effect, external effect, or semantic scope.
- Atomically admitted one Definition, fourteen Artifact Type contracts, three
  Relation Kind successors, and one new Relation Kind.
- Preserved the Decision 0073 Project State and both event histories as exact
  historical bytes, then appended semantic and governance events 4 and made
  Decision 0074 the current Project State in the same transaction.
- Materialized four exact `relation.materializes-consequence` Typed Relations
  for Project State, semantic history, governance history, and the generated
  registry and index projection output.
- Effective registries now contain 189 Definition versions with 183 current
  identities, 143 Artifact Type contracts with 121 current identities, 41
  Relation Kinds, 109 endpoint kinds, and 550 exact endpoint pairs.
- Decision validation passes 14 checks. Runtime activations and external
  effects remain zero, and no Decision 0075 bookkeeping approval is required.
