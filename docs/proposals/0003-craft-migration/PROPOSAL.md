<!-- Generated from proposal.json. Do not edit this projection directly. -->

# Craft migration into CyberAlchemy Lab

- Proposal: `CAL-PROP-0003`
- Schema: `cyberalchemy-lab-migration-proposal/v0`
- Status: `draft`
- Decision posture: `not-selected`
- Authority effect: `none`
- Artifact type: `candidate:migration-proposal/v0` (`candidate-unadmitted`)

> This is a non-effectful migration proposal. It does not authorize migration, implementation, Git operations, publication, release, or deployment.

## Objective

Selectively migrate one dependency-closed vertical of the Product lineage formerly named DomainSpec v2 into CyberAlchemy Lab under the active Craft name, preserving stable legacy semantic IDs, exact provenance, owner boundaries, deterministic construction, independent conformance, rollback, and all unselected source material as external legacy evidence.

## Selected naming policy

- Decision: `CAL-DECISION-0002` / `RN-2` — Active Craft naming with stable legacy IDs
- Lineage posture: `same-product-renamed`
- Active name: **Craft**
- Former name: **DomainSpec v2**

## Current evidence posture

- Prior migration-order validation: `PASS`
- Craft Product validation: `BLOCK-source-digest-drift`
- Craft Project validation: `BLOCK-source-digest-drift`
- Prior counts: `source_bindings=9`, `phases=10`, `development_directories_inventoried=53`, `active_backend_meta_types_selected=13`, `backend_relationship_signatures_selected=17`, `source_entries_bound=10956`, `literal_path_consumer_files=1027`, `literal_path_occurrences=9073`

The old migration sequence remains structurally coherent, but its source-bound Craft packages are not current and its cyberAlchemy-v2/craft destination is rejected for the Lab. No prior receipt is reusable as Lab admission or execution authority.

## Migration boundaries

- Source repository: `/home/vrondelli/projects/domainspec-core`
- Destination repository: `/home/vrondelli/projects/CyberAlchemy-lab`
- Source access: `read-only-external-legacy-ledger`
- Selection: `exact-dependency-closed-slices-only`
- Unselected material: `remain-in-place-as-external-legacy-evidence`
- Source deletion: `forbidden`
- Bulk copy: `forbidden`
- Global replacement: `forbidden`

Source roots:

- `projects/domainspec-v2`
- `cyberAlchemy-v2/product/domainspec-v2`
- `cyberAlchemy-v2/architecture/domainspec-v2`
- `cyberAlchemy-v2/authority/domainspec-v2`
- `cyberAlchemy-v2/ontology/domainspec-v2`
- `cyberAlchemy-v2/implementation/domainspec-v2`
- `cyberAlchemy-v2/research/domainspec-v2`
- `cyberAlchemy-v2/development/domainspec-v2`
- `cyberAlchemy-v2/product/craft`
- `cyberAlchemy-v2/goals/projects/craft`

## Migration principles

1. Treat Craft as the current name of the same Product lineage, not a successor Product and not a new semantic universe.
2. Use Craft on active Product, Project, Method, package, tool, CLI, profile, and user-facing surfaces; use specification for the authored/compiled construction layer.
3. Preserve stable DS-* semantic IDs during the first stable migration and require an explicit lineage record for every preserved identifier.
4. Keep machine records canonical and generate human projections deterministically beside them.
5. Bootstrap only the mechanics required to classify and admit later artifacts; mechanics may not own semantic meaning or authority.
6. Migrate definitions before Product Capability, business ontology, specification, system ontology, realization, implementation, or runtime.
7. Treat formal claims, Lean bindings, provider-native source, and theorem receipts as a separate evidence lane over an accepted Definition Snapshot, never as a second definition authority.
8. Use one exact final-path staging worktree per bounded phase; do not create an endless sequence of numbered candidate roots.
9. Run construction and independent conformance through separate implementations and evidence routes.
10. A passing phase makes only its declared candidate evaluable; it never executes its successor automatically.
11. Leave historical source bytes, receipts, paths, and immutable digests unchanged.

## Architecture prerequisites

### AP-01 — CAL-PROP-0001

Add explicit Product carriers and a coordination plane for Project and Goal records.

Candidate paths:

- `product/products/craft/v1/`
- `coordination/projects/craft/`
- `coordination/goals/`

### AP-02 — CAL-PROP-0001

Replace the active capability-instance domainspec/ directory with specification/ while preserving authored and generated subdirectories.

Candidate paths:

- `contexts/<bounded-context-id>/instances/<capability-instance-id>/specification/authored/`
- `contexts/<bounded-context-id>/instances/<capability-instance-id>/specification/generated/`

### AP-03 — CAL-PROP-0002

Replace domainspec-compiler with craft-compiler and remove active DomainSpec naming from platform declarations and profiles.

Candidate paths:

- `platform/tools/craft-compiler/v1/`
- `platform/profiles/languages/craft-specification/v1/`

### AP-04 — CAL-PROP-0001

Select the minimal artifact-mechanics, migration-proposal, source-admission, definition, invariant, lineage-map, formal-claim, native-source-bundle, provider-binding, and receipt artifact types before importing source bytes.

Candidate paths:

- `contracts/artifact-mechanics/v1/`
- `authority/artifact-types/`
- `authority/decisions/source-admission/`

### AP-05 — CAL-PROP-0002

Add Lean as an explicit language and toolchain profile with exact Lean, Lake, dependency, native-process runtime, environment, and lock identities; a checked theorem remains bounded provider evidence.

Candidate paths:

- `platform/languages/lean/v1/`
- `platform/tools/lean/v1/`
- `platform/tools/lake/v1/`
- `platform/profiles/toolchains/lean-meta-types-v1/v1/`
- `platform/profiles/environments/meta-type-formalization-v1/v1/`
- `platform/locks/meta-type-formalization-v1.lock.json`

## Candidate target tree

```text
CyberAlchemy-lab/
├── authority/
│   ├── artifact-types/
│   ├── definitions/
│   ├── invariants/
│   ├── decisions/source-admission/
│   └── lineage/craft/
├── coordination/
│   ├── projects/craft/
│   └── goals/
├── product/
│   ├── products/craft/v1/
│   ├── capabilities/system-construction/v1/
│   └── ontology/craft/
├── contexts/
│   └── <bounded-context-id>/
│       ├── context.json
│       ├── CONTEXT.md
│       ├── language/
│       ├── maps/
│       └── instances/
│           └── <capability-instance-id>/
│               ├── envelope.json
│               ├── specification/
│               │   ├── project.json
│               │   ├── authored/
│               │   └── generated/
│               ├── implementation/
│               ├── construction/
│               ├── evidence/
│               └── handoff/
├── platform/
│   ├── languages/lean/v1/
│   ├── tools/
│   │   ├── craft-compiler/v1/
│   │   ├── lean/v1/
│   │   └── lake/v1/
│   ├── profiles/
│   ├── runtimes/
│   └── locks/
├── evidence/
│   ├── migrations/domainspec-v2-to-craft/
│   │   ├── source-epochs/
│   │   ├── manifests/
│   │   ├── receipts/
│   │   └── rollback/
│   └── conformance/meta-types/active-backend-v1/lean/
└── tests/
    ├── fixtures/
    └── conformance/
```

The tree is a candidate only. CML-00 must revise and select the two architecture proposals before any target path becomes accepted.

## Source classification

### `admit-current`

Exact source bytes selected, transformed if required, independently validated, and accepted through one immutable Lab owner decision.

Destination posture: Active Lab architecture paths.

### `reference-external`

External source or evidence needed for provenance or comparison but not copied into the Lab.

Destination posture: Digest-bound references in migration evidence.

### `retain-legacy`

Unselected, historical, completed, blocked, superseded, or development material retained unchanged in domainspec-core.

Destination posture: No Lab copy.

### `reject`

Generated caches, dependency directories, stale duplicate candidates, unowned bytes, or material outside the selected closure.

Destination posture: No Lab copy; rejection reason recorded.

## Legacy identifier lineage contract

Candidate path: `authority/lineage/craft/legacy-identifiers.json`

Required fields:

- `legacy_id`
- `legacy_display_name`
- `current_display_name`
- `current_artifact_ref`
- `identity_posture`
- `source_repository`
- `source_path`
- `source_selector`
- `source_digest`
- `semantic_equivalence_evidence_refs`
- `consumer_refs`
- `retirement_posture`
- `owner_decision_ref`

Allowed identity postures: `same-id-renamed-display`, `legacy-alias-only`, `superseded-by-explicit-decision`, `rejected`.

Rules:

- Every active DS-* identifier must appear exactly once.
- DS-D1.10 must appear exactly once as a reserved non-active tombstone and may not resolve to an active definition artifact.
- No mapping may infer equivalence from similar names, paths, or schemas.
- No CRAFT-* replacement ID may be introduced without a separate owner decision.
- Historical evidence continues to use its original IDs and names.

## First vertical candidate

**Active backend meta-type semantic snapshot and bounded Lean evidence** — `candidate-not-owner-selected`

Definition scope:

- `active_meta_type_ids`: DS-D1.1, DS-D1.2, DS-D1.3, DS-D1.4, DS-D1.5, DS-D1.6, DS-D1.7, DS-D1.8, DS-D1.9, DS-D1.11, DS-D1.12, DS-D1.13, DS-D1.14
- `definition_records`: 13
- `formation_invariant_records`: 13
- `reserved_legacy_tombstones`: DS-D1.10
- `definition_voices`: formal, plain-language, domain-context
- `edge_participation_posture`: generated-later-from-accepted-DS-D8-not-authored-in-definitions

Deferred definition dependencies:

- `relationship_definition_id`: DS-D8
- `candidate_relationship_signatures`: 17
- `source_relationship_signatures`: 31
- `deferred_relationship_signatures`: 14
- `state_definition_ids`: domainspec-v2-D31, domainspec-v2-D32, domainspec-v2-D33, domainspec-v2-D34, domainspec-v2-D35
- `posture`: excluded-from-first-semantic-snapshot-and-requires-separate-owner-selection

Formalization scope:

- `sequencing_decision_ref`: CAL-DECISION-0003-LEAN-SEQUENCING:LEANS-2
- `sequencing_posture`: parallel-non-blocking-after-accepted-semantic-snapshot
- `formal_claim_source`: accepted-active-backend-definition-snapshot
- `provider`: Lean
- `target_source`: CraftMetaTypes.lean
- `required_claims`: selected vocabulary has exactly 13 members, every selected member has one unique preserved DS-* identifier, the expected 13 identifiers are complete, DS-D1.10 is absent from the active set and reserved in lineage, category assignment is total and disjoint, every selected definition resolves to exactly one formation invariant
- `legacy_current_model`: CurrentDomainSpecMetaTypes.lean is comparison evidence only because it covers 24 meta-types and 31 relationships
- `legacy_extended_model`: DomainSpecEdgeSignature.lean remains noncanonical legacy evidence
- `failure_posture`: A failed, deferred, or unaccepted Lean package leaves its FormalClaims unresolved but neither revokes the accepted semantic snapshot nor blocks the Craft identity branch.
- `claim_ceiling`: The Lean provider may establish only the exact propositions in the exact locked environment; it does not own definitions, prove detailed formation criteria unless separately encoded, or establish runtime, implementation, release, or production conformance.

Serialization:

- `canonical_format`: json
- `yaml_source_ingestion`: migration-tool-only
- `destination_yaml_dependency`: forbidden
- `human_projection`: generated

Excluded:

- UI candidate meta-types
- deferred meta-types
- DS-D1.10 as an active definition while retaining its lineage tombstone
- DS-D8 relationship signatures until a separate relationship decision
- meta-type state vocabulary until a separate definition decision
- the 24-member and 31-relationship Lean model as active Lab authority
- the legacy extended Lean edge-signature model as active Lab authority
- unselected ontologies
- TypeScript, Python, and Rust realizations
- current implementation state as semantic definition authority
- unselected architecture research
- unselected development work packs
- numbered implementation candidates
- dependency caches and node_modules

## Migration phases

### 0. `CML-00-SELECT-LAB-ARCHITECTURE`

- Status: `blocked`
- Depends on: none

**Objective.** Revise proposals 0001 and 0002 for RN-2, select one immutable architecture digest, and constitute the required artifact, platform, source-admission, Product, Project, and migration owners.

**Outputs**

- accepted context/artifact architecture
- accepted platform/environment architecture
- exact owner and path registry
- migration execution boundary

**Exit gate.** One exact architecture decision binds all target paths and owners; no implementation follows automatically.

**Rollback.** Discard unselected draft revisions; existing Lab foundation and RN-2 decision remain unchanged.

### 1. `CML-01-BOOTSTRAP-ARTIFACT-AND-ADMISSION-MECHANICS`

- Status: `not-started`
- Depends on: `CML-00-SELECT-LAB-ARCHITECTURE`

**Objective.** Implement and independently validate only the minimal machine-source, generated-human, schema, definition, invariant, lineage-map, source-admission, formal-claim, native-source-bundle, provider-binding, migration-manifest, receipt, and drift-rejection mechanics required by later phases.

**Outputs**

- artifact mechanics v1
- initial artifact types and schemas
- deterministic projection generator
- source-admission decision schema
- migration manifest and receipt schemas
- positive witness and negative mutants

**Exit gate.** Two-run deterministic projection and all hand-edit, wrong-type, missing-owner, stale-generator, hidden-dependency, and false-admission mutants pass independently.

**Rollback.** Remove only phase-owned unadmitted files from the isolated execution worktree; no source repository bytes are touched.

### 2. `CML-02-REFRESH-AND-FREEZE-SOURCE-EPOCH`

- Status: `not-started`
- Depends on: `CML-01-BOOTSTRAP-ARTIFACT-AND-ADMISSION-MECHANICS`

**Objective.** Recompute the exact legacy source manifest, selected selectors, path consumers, dirty state, owner routes, and content digests against a fresh immutable domainspec-core epoch.

**Outputs**

- source epoch manifest
- selected-source inventory
- consumer inventory
- dirty-state and active-writer record
- source classification ledger

**Exit gate.** Every selected source and consumer has an exact path or selector, digest, owner, classification, and no intersecting active writer.

**Rollback.** The phase is read-only against domainspec-core; discard the Lab candidate epoch if any selected dependency changes.

### 3. `CML-03-MATERIALIZE-DEFINITION-CANDIDATE`

- Status: `not-started`
- Depends on: `CML-02-REFRESH-AND-FREEZE-SOURCE-EPOCH`

**Objective.** Materialize exactly 13 selected active-backend meta-type definitions and their 13 formation invariants as separate canonical JSON artifacts, preserve DS-* IDs through explicit lineage mappings, retain DS-D1.10 as a non-active tombstone, and generate human projections.

**Outputs**

- 13 active backend meta-type definition artifacts
- 13 formation-invariant artifacts
- three generated definition voices per definition artifact
- legacy identifier lineage map with one DS-D1.10 tombstone
- generated meta-type index without authored edge-participation duplication
- schemas, indexes, projections, drift audit, and candidate manifest

**Exit gate.** Exact definition-to-invariant and lineage closure, no destination YAML dependency, no active DS-D1.10 definition, no DS-D8 or implementation-state authority folded into the snapshot, no unmapped selected ID, and no semantic expansion beyond the selected source closure.

**Rollback.** Discard the unadmitted final-path worktree; retain the source epoch and failure receipt.

### 4. `CML-04-FREEZE-DEFINITION-SNAPSHOT`

- Status: `not-started`
- Depends on: `CML-03-MATERIALIZE-DEFINITION-CANDIDATE`

**Objective.** Independently verify source-to-JSON equivalence across the YAML index, definition cards, criterion sources, lifecycle evidence, and owner decisions; verify three definition voices, definition-to-invariant separation, lineage closure, source currentness, generator identity, projection drift, and two-run byte determinism; then route one exact semantic snapshot to its owner.

**Outputs**

- independent validation receipt
- immutable 13-definition and 13-invariant Definition Snapshot candidate
- owner accept, revise, reject, defer, or stop decision surface

**Exit gate.** An exact owner decision accepts one snapshot digest; validator PASS alone is insufficient.

**Rollback.** Reject or defer without changing source or activating successor layers.

### 5. `CML-05-MATERIALIZE-BOUNDED-LEAN-EVIDENCE`

- Status: `not-started`
- Depends on: `CML-04-FREEZE-DEFINITION-SNAPSHOT`

**Objective.** Create a canonical FormalClaim package over the accepted Definition Snapshot, bind it to one exact Lean language, toolchain, native-process runtime, environment, and lock profile, and materialize a new 13-member CraftMetaTypes.lean provider-native source bundle without treating legacy Lean files as Lab authority.

**Outputs**

- canonical formal-claim artifact and generated view
- preservation and Lean provider-binding artifacts
- CraftMetaTypes.lean native-source bundle
- exact Lean, Lake, dependency, runtime, environment, and lock bindings
- legacy Lean comparison manifest

**Exit gate.** Every Lean statement maps to one accepted formal claim and snapshot digest; the source enumerates only the selected 13 active IDs, preserves the DS-D1.10 tombstone boundary, imports no unselected relationship or UI authority, and resolves under one exact locked environment.

**Rollback.** Discard the unadmitted formalization bundle and retain the accepted semantic snapshot unchanged.

### 6. `CML-06-VALIDATE-AND-FREEZE-LEAN-EVIDENCE`

- Status: `not-started`
- Depends on: `CML-05-MATERIALIZE-BOUNDED-LEAN-EVIDENCE`

**Objective.** Independently compare snapshot enumeration and category assignments to Lean, run the exact provider check twice, exercise omission, duplication, DS-D1.10 reuse, category-overlap, invariant-ref, statement-drift, and environment-drift mutants, and route the resulting bounded evidence package to its owner.

**Outputs**

- independent snapshot-to-Lean preservation receipt
- two-run Lean provider receipt
- negative-mutant evidence
- immutable Lean evidence candidate
- owner accept, revise, reject, defer, or stop decision surface

**Exit gate.** The exact theorem statements check in the exact locked environment and an owner accepts one bounded evidence digest; this proves neither detailed formation criteria not represented in the claims nor runtime, implementation, release, or production conformance.

**Rollback.** Reject or defer the Lean evidence candidate without changing the accepted definitions, invariants, lineage, or source repository.

### 7. `CML-07-MATERIALIZE-CRAFT-IDENTITY-AND-COORDINATION`

- Status: `not-started`
- Depends on: `CML-04-FREEZE-DEFINITION-SNAPSHOT`

**Objective.** Create the Craft Product, Project, Method, Goal, and source-map carriers in their selected orthogonal Lab planes, bound to the accepted Definition Snapshot and RN-2 lineage decision.

**Outputs**

- Craft Product record and generated view
- Craft Project and Goal records
- Craft Method binding
- Product-Project-Method non-collapse relations
- source and lineage maps

**Exit gate.** All identities and owner routes close without classifying Craft, Product, or Governance as a bounded context by implication.

**Rollback.** Discard unadmitted identity carriers while preserving CAL-DECISION-0002 and the accepted definition snapshot evidence.

### 8. `CML-08-SELECT-FIRST-CONTEXT-AND-CAPABILITY`

- Status: `not-started`
- Depends on: `CML-07-MATERIALIZE-CRAFT-IDENTITY-AND-COORDINATION`

**Objective.** Select one first Product Capability, one owner-local capability instance, and any real DDD Bounded Context identity with language, scope, exclusions, maps, recursion stop, and recomposition route.

**Outputs**

- first capability decision
- bounded-context decision or explicit no-context posture
- capability-instance envelope
- recursive binding candidate

**Exit gate.** The owner selects exact capability/context identities and one dependency-closed vertical; directory placement cannot supply the decision.

**Rollback.** Reject or revise the candidate envelope without touching accepted definitions or Craft identity carriers.

### 9. `CML-09-MIGRATE-CAPABILITY-AND-BUSINESS-ONTOLOGY`

- Status: `not-started`
- Depends on: `CML-08-SELECT-FIRST-CONTEXT-AND-CAPABILITY`

**Objective.** Migrate only the Product Capability and business-ontology records required by the selected vertical, each bound to the accepted definitions and owner-local context.

**Outputs**

- Product Capability record
- business ontology closure
- typed context-map relations
- capability-instance binding evidence

**Exit gate.** The capability and business ontology close against exact accepted definitions with no unselected ontology imports.

**Rollback.** Discard the unadmitted capability/ontology candidate; accepted predecessors remain unchanged.

### 10. `CML-10-MIGRATE-SPECIFICATION-AND-SYSTEM-ONTOLOGY`

- Status: `not-started`
- Depends on: `CML-09-MIGRATE-CAPABILITY-AND-BUSINESS-ONTOLOGY`

**Objective.** Migrate the selected authored specification, deterministic compiled graph, and system ontology under the capability instance's specification/ boundary using active Craft or neutral names.

**Outputs**

- authored specification source
- exact compiler profile
- compiled graph
- system ontology
- source-to-output determinism receipt

**Exit gate.** The definition-to-capability-to-business-to-specification-to-system-ontology chain is exact, deterministic, and owner-reviewed.

**Rollback.** Discard derived outputs and unadmitted authored candidates; never rewrite the accepted predecessor artifacts.

### 11. `CML-11-MIGRATE-REALIZATIONS-AND-PLATFORM-PROFILES`

- Status: `not-started`
- Depends on: `CML-10-MIGRATE-SPECIFICATION-AND-SYSTEM-ONTOLOGY`

**Objective.** Migrate only required architecture properties, language-neutral realization contracts, TypeScript/Python/Rust bindings, craft-compiler declaration, toolchain profile, runtime profile, and exact environment lock.

**Outputs**

- selected realization contracts
- TypeScript, Python, and Rust bindings
- craft-compiler tool declaration
- toolchain and runtime profiles
- development environment lock

**Exit gate.** Every realization closes against the accepted system ontology and exact language/profile identity with no mutable global dependency or active DomainSpec package/path name.

**Rollback.** Remove only phase-owned local install bindings and unadmitted records; content-addressed shared bytes remain untouched.

### 12. `CML-12-MIGRATE-RUNTIME-AND-SELECTED-CONSUMERS`

- Status: `not-started`
- Depends on: `CML-11-MIGRATE-REALIZATIONS-AND-PLATFORM-PROFILES`

**Objective.** Materialize one standalone implementation and Craft CLI at final Lab paths, then rebind only the consumers named by the selected vertical.

**Outputs**

- dependency-closed implementation
- Craft CLI
- selected generators, schemas, ports, fixtures, and conformance providers
- consumer-rebinding manifest
- installation and activation receipts

**Exit gate.** The implementation installs, typechecks, tests, builds, and resolves only final Craft/neutral paths under the accepted environment profile.

**Rollback.** Discard the isolated worktree or revert the exact phase commit only under separate Git authorization; never modify legacy source consumers globally.

### 13. `CML-13-VALIDATE-AND-FREEZE-FIRST-CRAFT-VERTICAL`

- Status: `not-started`
- Depends on: `CML-12-MIGRATE-RUNTIME-AND-SELECTED-CONSUMERS`

**Objective.** Run final-path generation, three-profile realization, Operation, Workflow, target-project, independent conformance, offline reinstall, and two-run replay checks, then route one immutable baseline candidate to the owner.

**Outputs**

- complete construction binding candidate
- independent conformance evidence
- two-run deterministic replay receipt
- rollback rehearsal receipt
- first Craft baseline owner-decision surface

**Exit gate.** One exact owner decision freezes the first Craft vertical; passing tests do not authorize release or v1.0.0.

**Rollback.** Retain the last accepted phase, reject the baseline candidate, and preserve all failure evidence without switching authority or deleting source.

## Gate model

- Phase order is presentation order; explicit depends_on edges are the authoritative execution prerequisites.
- CML-05 and CML-06 form a parallel bounded-evidence branch after CML-04, while CML-07 begins the Craft identity branch directly from accepted CML-04 semantics.
- Each phase has one exact input graph, write set, validator set, independent reviewer when required, owner route, and terminal receipt.
- A phase begins only after every predecessor is accepted and current; partial predecessor evidence yields blocked or not_evaluable.
- Every owner decision binds one immutable digest. Changed acceptance-bound bytes require a new candidate and decision.
- Validation, materialization, installation, conformance, baseline freeze, release, and publication remain separate transitions.
- No phase may silently refresh a stale source digest or reinterpret old candidate evidence as current.

## Validation obligations

- All canonical Lab records are machine-readable and every human view regenerates byte-identically from its machine source.
- No active Lab path, package ID, CLI command, compiler name, profile ID, or user-facing current-name field uses DomainSpec except an explicit former-name or provenance field.
- Every active preserved DS-* ID resolves through exactly one lineage record; unmapped and multiply mapped IDs fail.
- No historical DomainSpec source, receipt, decision, path, or digest is rewritten.
- Only the selected dependency closure is copied; directory inventory and textual occurrence counts never become copy instructions.
- Every imported byte binds source repository, path or selector, digest, owner, classification, and source-admission decision.
- The first semantic snapshot contains exactly 13 owner-selected active backend definition artifacts, 13 separately typed formation-invariant artifacts, and one non-active DS-D1.10 lineage tombstone; DS-D8, state vocabulary, profiles, and implementation state remain outside it.
- JSON conversion preserves semantic content and meaningful source order across the YAML index, definition cards, criterion sources, lifecycle evidence, and owner decisions; ordinary YAML parsing may not silently discard authoritative comments or boundary notes, and no destination YAML runtime dependency remains.
- Definition meaning, formation invariants, JSON record schemas, DS-D8 relationship authority, implementation state, and formal proof evidence remain separate typed artifacts and owners.
- Authored edge-participation lists are absent from migrated definition authority; a later accepted DS-D8 snapshot may generate them as digest-bound projections.
- CurrentDomainSpecMetaTypes.lean and DomainSpecEdgeSignature.lean remain external comparison or legacy evidence and cannot be copied or renamed into active Lab authority.
- Every Lean statement binds one exact canonical FormalClaim, accepted Definition Snapshot digest, preservation binding, provider-native source digest, and locked Lean environment.
- The first Lean package proves only 13-member enumeration, stable-ID uniqueness and completeness, DS-D1.10 exclusion, total and disjoint category assignment, and one formation-invariant reference per definition; unencoded formation semantics remain unproved.
- Lean omission, duplication, DS-D1.10 reuse, category-overlap, invariant-reference, statement-drift, and environment-drift mutants fail independently, and two identical provider runs return equivalent bounded results.
- Product, Project, Method, Product Capability, capability instance, CAV2 Context, DDD Bounded Context, module, package, and directory remain independent typed identities.
- The specification compiler, materializer, and independent conformance providers are separately identified and cannot share unreported decision logic.
- TypeScript, Python, and Rust realization checks run from exact final paths under pinned profiles and locks.
- Operation and Workflow checks cover declared reads, writes, effects, guards, atomic state/outbox behavior, failure continuation, relationship rules, undeclared-effect rejection, and recovery bindings.
- A mock target project is generated from typed intent and independently checked against exact selected realizations and byte digests.
- Offline warm-store reinstall and clean-store policy-bound install produce the same activation closure.
- Two identical runs produce identical target bytes, manifests, projections, and conformance results.
- Rollback is rehearsed without changing domainspec-core or deleting shared content-addressed runtime bytes.
- A repository-wide scan proves any remaining DomainSpec strings are confined to explicit legacy, former-name, provenance, evidence, or lineage fields.

## Execution model

- `staging`: one isolated CyberAlchemy Lab worktree at final proposed paths per authorized phase
- `source_access`: read-only exact selectors from domainspec-core
- `network`: denied unless the selected environment profile and exact phase authorization permit it
- `writes`: phase-owned Lab paths plus run-local evidence only
- `git`: no commit, merge, tag, push, or history rewrite without a separately selected publication route
- `failure`: stop at the first effectful failure, preserve the receipt, and do not execute successors
- `parallelism`: the selected DAG permits independent Lean-evidence and Craft-identity branches after CML-04; within each branch, effects remain predecessor-gated and bounded

## Rollback strategy

- Before admission, rollback means discard the isolated worktree or remove only the exact unadmitted phase write set.
- After a local accepted commit, rollback requires an explicit inverse commit over the exact phase manifest; no reset or history rewrite.
- Source repositories and legacy roots are never rollback targets because migration is additive and source-deletion is forbidden.
- Content-addressed platform bytes are garbage-collected only when no active environment references them and a separate cleanup decision authorizes removal.
- Every phase receipt records predecessor digests, written paths, installed paths, network effects, consumer changes, validation, rollback command shape, and remaining residue.

## Success criteria

- One accepted 13-definition and 13-invariant Craft semantic snapshot exists with generated human views, exact source admission, preserved stable IDs, and a DS-D1.10 tombstone.
- The Lean evidence branch, when completed and accepted, binds exact formal claims to the semantic snapshot and exact locked provider environment without becoming definition or runtime authority; its unresolved state does not block the first Craft identity or runtime vertical.
- One accepted Craft Product/Project/Method identity graph exists in Lab and cites RN-2 plus an accepted Definition Snapshot.
- One owner-selected Product Capability and owner-local capability instance complete the full definitions-to-runtime construction chain.
- Active Lab surfaces consistently use Craft or neutral specification naming while preserved DS-* IDs remain explicit and traceable.
- One standalone Craft CLI and implementation operate from final Lab paths under an exact environment lock.
- A target project can be generated from typed intent and independently checked across the selected TypeScript, Python, and Rust realization boundary.
- Two-run determinism, consumer closure, negative tests, offline reinstall, and rollback rehearsal all pass.
- Every unselected former-lineage artifact remains external legacy evidence and is neither copied nor implied admitted.

## Decision gates remaining

- Select the revised context/artifact and platform/environment architectures.
- Select owners and exact paths for artifact mechanics, source admission, definitions, invariants, lineage maps, formal claims, provider bindings, Product, Project, platform, migration, and evidence.
- Select whether the 13-definition, 13-invariant, and DS-D1.10-tombstone active-backend slice is the first Lab semantic snapshot after a fresh source epoch.
- Apply selected decision CAL-DECISION-0003-LEAN-SEQUENCING:LEANS-2: Lean is a parallel non-blocking evidence lane after semantic snapshot acceptance.
- Select the exact FormalClaim set and Lean language, Lean tool, Lake tool, dependency, native-process runtime, environment, network, filesystem, and lock profiles.
- Select the first Product Capability, capability instance, and DDD Bounded Context or explicit no-context posture.
- Select exact TypeScript, Python, Rust, Node/container, network, filesystem, and later realization lock profiles.
- Accept, revise, reject, defer, or stop at each immutable phase candidate.
- Make release and v1.0.0 decisions only after the first frozen vertical and separate release-candidate validation.

## Bound evidence

- `selected-lab-rename-scope`: `CyberAlchemy-lab:docs/decisions/0002-craft-rename-scope/decision.json` — `sha256:397f00ce647f7370940ae1726ec2d84d1db88e2733f91ad8bd72684acab719f7`; effect `owner-selected-naming-policy-only`
- `context-and-artifact-architecture-candidate`: `CyberAlchemy-lab:docs/proposals/0001-context-artifact-architecture/proposal.json` — `sha256:c4174297bfa71818012b77848a7cb8560b47d303b30f062144f2dc03c478932f`; effect `rn-2-aligned-draft-awaiting-architecture-selection`
- `platform-environment-architecture-candidate`: `CyberAlchemy-lab:docs/proposals/0002-platform-environment-architecture/proposal.json` — `sha256:cd1b51802aba4dba2c6cbd765f6a5dd000487919530e0fdaaf2b8ba81aa9485b`; effect `rn-2-and-leans-2-aligned-draft-awaiting-architecture-selection`
- `selected-lean-evidence-sequencing`: `CyberAlchemy-lab:docs/decisions/0003-lean-evidence-sequencing/decision.json` — `sha256:91f4a2fb282ddc3649dda673e46dbb3cd52d8bd261944e17f2d87c90765b319d`; effect `owner-selected-architecture-sequencing-only`
- `former-lineage-identity-decision`: `domainspec-core:cyberAlchemy-v2/goals/projects/craft/CRAFT-IDENTITY-DECISION.json` — `sha256:1f2d01026865e031adba063de0dc1dfa081c49a931223aa4bc9f726d3397bceb`; effect `external-lineage-evidence-only`
- `prior-migration-order`: `domainspec-core:cyberAlchemy-v2/development/domainspec-v2/migration/mig-b/map/CRAFT-MIGRATION-ORDER.json` — `sha256:7b690fd8ede305449ec63334d3155c34fcdf5bc7da582eeeb4f0ba84de0b9ac2`; effect `validated-planning-precedent-not-execution-authority`
- `prior-source-epoch-receipt`: `domainspec-core:cyberAlchemy-v2/development/domainspec-v2/migration/mig-b/map/M00-REFRESH-AND-FREEZE-RECEIPT.json` — `sha256:7db9669f62f5db99534ed6b80ce8c6cbfcedbd80717269f9a7540e14717f9823`; effect `historical-freeze-evidence-new-lab-epoch-required`
- `observed-former-lineage-architecture`: `domainspec-core:cyberAlchemy-v2/development/domainspec-v2/migration/mig-b/map/ARCHITECTURE.md` — `sha256:b93a32ae0cf6f9c125431bbaebfb74287483c2be0075b518ea035601dd11194f`; effect `external-observed-architecture-evidence-only`
- `observed-meta-type-machine-index`: `domainspec-core:projects/domainspec-v2/definitions/meta-types/meta-types.yml` — `sha256:bc800afdca36fa701a13ec611e7ee0ef928a4c8d259d48dfac2880a3cc8cbbc4`; effect `planning-input-read-model-refresh-before-migration`
- `observed-meta-type-three-voice-cards`: `domainspec-core:projects/domainspec-v2/definitions/meta-types/meta-types.md` — `sha256:c49f7879f7d27f214f930dc0c643edf411e63bf26d1a057f81be959645f51a51`; effect `planning-input-definition-voices-refresh-before-migration`
- `observed-meta-type-implementation-state`: `domainspec-core:projects/domainspec-v2/definitions/meta-types/current-implementation.json` — `sha256:9709046a5838a365bf25b4a316b05ce0646aeb7bdda81160bf459ac9e9c9eb50`; effect `implementation-and-lifecycle-evidence-not-semantic-definition-authority`
- `observed-current-meta-type-lean-candidate`: `domainspec-core:projects/domainspec-v2/formalization/CurrentDomainSpecMetaTypes.lean` — `sha256:bf77040b2f786f1a6bffa8d84dfa8592937bac462771d91a8fea2aa626239f59`; effect `24-meta-type-31-relationship-comparison-evidence-only`
- `observed-legacy-extended-lean-model`: `domainspec-core:projects/domainspec-v2/formalization/DomainSpecEdgeSignature.lean` — `sha256:383135bb0a1e1f2b12536c2e40846cba275c88106d5c671c86a467bfafe85d58`; effect `noncanonical-legacy-formalization-evidence-only`

## Typed residue

### The RN-2-aligned Lab architecture revisions remain draft candidates and are not yet bound by one immutable architecture-owner decision.

- Owner needed: CyberAlchemy Lab architecture owner
- Effect: CML-00 remains blocked and no migration target path is accepted until the exact revised proposal digests are selected.

### No admitted Lab artifact mechanics, schemas, projection generator, source-admission mechanism, or migration validator exists.

- Owner needed: CyberAlchemy Lab artifact mechanics and governance owners
- Effect: External bytes cannot yet become admitted Lab artifacts.

### The draft artifact architecture names invariant, formal-claim, native-source-bundle, provider-binding, and receipt artifact-type paths but those contracts remain unimplemented and unaccepted.

- Owner needed: CyberAlchemy Lab architecture and artifact-type owners
- Effect: The semantic and Lean evidence packages have candidate paths but no accepted artifact contracts.

### The draft platform architecture has no selected Lean language, Lean or Lake tool, formalization toolchain, native-process runtime, environment, or lock profile.

- Owner needed: CyberAlchemy Lab platform owner
- Effect: CML-05 and CML-06 remain not evaluable even after a semantic Definition Snapshot is accepted.

### CurrentDomainSpecMetaTypes.lean covers 24 meta-types and 31 relationships while the first Lab semantic snapshot proposes 13 active backend meta-types; DomainSpecEdgeSignature.lean is a different legacy extended model.

- Owner needed: Craft formalization and Definition Snapshot owners
- Effect: Neither legacy Lean file can be treated as the active Lab formalization; a new bounded formal-claim and preservation binding is required.

### The prior source epoch is historical and current Craft packages report source-digest drift.

- Owner needed: Craft migration source owner
- Effect: A fresh source freeze is mandatory before selecting migration bytes.

### The first Product Capability, capability instance, and bounded context are unselected.

- Owner needed: Craft Product, Project, capability, and context owners
- Effect: No D65 construction binding or implementation scope is evaluable.

### The Goals and Governance enforcement runtimes cannot admit planning or execution state.

- Owner needed: CyberAlchemy governance runtime owner
- Effect: This proposal remains non-effectful planning evidence.

## Claim ceiling

This draft proposes a Lab-bound migration sequence under RN-2. It does not select the architecture or first vertical, refresh a source epoch, admit an artifact type, source, definition, invariant, lineage tombstone, Definition Snapshot, FormalClaim, Lean binding, provider-native source bundle, theorem result, Product, Project, capability, ontology, specification, realization, implementation, runtime, consumer binding, construction binding, conformance result, or baseline; it does not rename, copy, install, delete, commit, merge, publish, release, deploy, or establish v1.0.0.

