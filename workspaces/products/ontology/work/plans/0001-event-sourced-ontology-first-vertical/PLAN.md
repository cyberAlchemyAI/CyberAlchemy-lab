# Event-Sourced Ontology First Vertical

Status: planning candidate; implementation entry is blocked  
Route: `CA2-ROUTE-PLAN`  
Construction invariant: `CAV2-D65`  
Target decision: `CAL-ESOV-0003` at SHA-256 `7468a1d70cf01049abc6f2cd29f06f7c824efc96c4755a4c2f8a6ef83ef2b931`

## Outcome

Build the smallest Lab-native runtime that can reconstruct one ontology state at
an exact graph commit cursor from append-only typed events. Keep the semantic
event streams and governance event streams separate. Join them only with exact
event identity, digest, and cursor references.

This plan prepares that implementation. It does not authorize it.

## Core architecture

Two deterministic transformations are required. They have different inputs and
must not be collapsed:

```text
DomainSpec design compiler
  admitted DomainSpec source
    -> compiled design graph
    -> system-ontology projection

Ontology state reducer
  canonical semantic events + exact governance references
    -> ontology_at(cursor)
    -> machine projection + human projection
```

DomainSpec describes the runtime contract: event types, operations, reducer,
query, policies, interfaces, and their allowed relations. It does not replace
the event log. Canonical JSON event files remain runtime data. Machine state,
human views, indexes, and latest snapshots remain calculated projections.

## D65 readiness

| D65 stage | Current state | Required next evidence |
| --- | --- | --- |
| Canonical definitions | `absent` for this capability | Owner-resolved meanings for ontology event, subject stream, graph commit cursor, ontology projection, and governance event reference. Reuse existing definitions where they are sufficient. |
| Product Capability | `absent` | One CyberAlchemy Lab Product Capability: reconstruct governed ontology state at an exact cursor. |
| Capability-local business ontology | `absent` | Concepts, invariants, inputs, outputs, failure states, and exact relations for the Ontology Lifecycle context. |
| DomainSpec v2 authored source | `not_evaluable` | Use the registered Project and Goal, then bind an admitted profile, language digests, feature, nodes, and connections after the three semantic predecessors are current. |
| Deterministic compiled graph | `blocked` | Repair the supported-profile registry digest and pass the compiler corpus, or select an owner-admitted replacement profile. |
| System ontology | `absent` | A generic or capability-owned deterministic projection and receipt derived from the exact graph. |
| Implementation binding | `absent` | An owner-accepted exact Rust target binding to the admitted system ontology. |
| Static conformance | `not_evaluable` | Graph-derived obligations, exact code bindings, observations, and an independently consumed receipt. |
| Runtime evidence | `not_evaluable` | Replay, cursor-cut, failure, and projection-rebuild evidence against the exact implementation target. |

The Goals v9 ConstructionBinding registry cannot receive a concrete record. Its
schema fixes `bindings` to an empty array, and its validator rejects non-empty
bindings. A later governed schema and validator epoch must open the registry.

## What DomainSpec can do now

The current minted-project tool can:

- resolve declared JSON project, feature, and node sources;
- bind an exact profile, kind registry, and relationship registry;
- validate node formation and allowed endpoint types;
- reject missing, duplicate, out-of-scope, and unsupported graph material;
- sort nodes, edges, and provenance deterministically;
- emit a graph, source manifest, readable specification, machine view, and
  build receipt;
- verify source currentness and artifact digests.

The Registry Context package proves that the current tool can produce the same
check result twice with a development-only profile. That result is local
evidence. It is not release admission or D65 completion.

## What is missing from deterministic compilation

1. **The default supported profile is not current.** It binds the meta-type
   registry to `439496...`, while the current registry digest is `bc800a...`.
   The focused compiler suite therefore stops at `REGISTRY_DIGEST_MISMATCH`:
   1 test passes and 12 fail.
2. **No release-admitted minted-project profile exists.** Both listed profiles
   retain `release_admission: not-granted` or deferred status. A development
   profile can support a witness but cannot satisfy the D65 admitted-profile
   requirement.
3. **The compiled graph does not generically emit a system ontology.** Registry
   Context uses a capability-owned wrapper to create `NODES.json`,
   `RELATIONS.json`, and `PROFILE.json`. The reusable compiler emits only the
   graph and read views.
4. **The graph cannot state the full reducer dataflow.** The active backend
   relationship language has no admitted connection for a `Calculation` that
   consumes `Event` data and supplies a `Query` or calculated projection. The
   model can name those nodes, but it cannot express the load-bearing dataflow
   as checked edges without a DomainSpec language decision.
5. **Graph-to-obligation derivation is unfinished.** The current architecture
   says the JSON compiler and the Markdown obligation engine are separate. A
   successful graph build does not produce implementation obligations.
6. **No exact Rust realization binding is produced.** The compiler does not map
   graph node IDs to Rust modules, symbols, schemas, or tests. That binding must
   be a separate exact artifact and owner decision.
7. **No generic D65 transition evaluator exists.** Determinism evidence does
   not validate the predecessor chain or grant implementation authority.
8. **The architecture source epoch drifted.** The decision binds the proposal
   digest `7ee728...`; the current proposal digest is `a8ffc2...`. The plan can
   rely on the closed decision record, but implementation cannot claim a current
   architecture bridge until an owner reconciles this drift.

## Proposed DomainSpec model

The capability-local ontology must settle the exact names and meanings first.
After that gate, the smallest truthful DomainSpec feature should contain these
roles:

| Proposed node | DomainSpec kind | Purpose |
| --- | --- | --- |
| `OntologySubject` | Entity | Identity-bearing node or relation subject with its own semantic stream. |
| `GraphCommitCursor` | Value Object | One immutable global cut coordinate. |
| `OntologyEvent` | Event | Typed semantic event with the complete resulting subject state. |
| `GovernanceEvent` | Event | Separate decision or lifecycle event linked by exact refs. |
| `AppendOntologyEvent` | Operation | Validate and append one canonical semantic event. |
| `ReduceSubjectStream` | Calculation | Pure fold from ordered subject events to subject state. |
| `OntologyAtCursor` | Query | Assemble the consistent graph cut at one cursor. |
| `ProjectionIntegrityRule` | Rule | Reject cursor gaps, duplicate identity, invalid endpoints, and mismatched resulting state. |
| `ReductionPolicy` | Policy | Select fail-closed handling for absent or invalid subject state. |
| `OntologyRuntimeInterface` | Interface | Expose append and query contracts without owning semantic authority. |

Existing relationships can express `emits`, `produces`, `enforces`, `applies`,
`reads`, `contains`, and `exposes`. The reducer input/output relationship remains
an explicit DomainSpec language blocker; do not hide it in an invented edge.

## Implementation layers

### L0 — Deterministic single-cut witness

Included:

- two owner-selected ontology nodes and one owner-selected relation;
- one stream per node or relation;
- canonical JSON events with a global monotonic cursor;
- complete resulting subject state in each semantic event;
- a Rust library reducer;
- `ontology_at(cursor)`;
- checked-in machine and human projections;
- one separate governance event joined by exact identity, digest, and cursor;
- replay, invalid-event, cursor-gap, relation-endpoint, and projection-rebuild
  tests.

Deferred: legacy import, compaction, distributed writers, network services,
publication, deployment, and runtime enforcement outside the witness.

Risk: a convenient static-state file could become a second source of truth.

Cost: one feature, one library crate, one fixture corpus, and deterministic
projection tooling.

Exit evidence:

- the DomainSpec build is byte-equal across two runs;
- the Rust projection is byte-equal across two clean replays;
- deleting projections and rebuilding produces the same bytes;
- `ontology_at(c)` contains no event after `c` and rejects an incomplete cut;
- every relation endpoint resolves at the same cut;
- governance joins fail on a wrong ID, digest, or cursor;
- the implementation target is bound to exact system-ontology bytes.

After this layer, we know whether canonical events can calculate one consistent,
reproducible ontology cut without a second authority source.

### L1 — Complete selected topology

Add arbitrary per-node and per-relation streams, the full semantic/governance
join, snapshot acceleration that is always rebuildable, and collect-all
validation reports.

Exit evidence: a larger fixture graph gives the same result with and without
snapshots, and every invalid stream or join produces a stable machine code.

After this layer, we know whether the selected `STR-2`, `ASM-1`, `PAY-1`,
`PRJ-1`, and `GOV-2` model scales beyond the small witness.

### L2 — D65 construction and conformance closure

Open the governed ConstructionBinding registry, bind the exact Lab Project,
definitions, product ontology, business ontology, DomainSpec source, compiler,
graph, system ontology, Rust target, static observations, and runtime evidence.

Exit evidence: a non-empty binding passes the governed evaluator, drift in any
predecessor makes downstream evidence non-current, and no validator grants
authority.

After this layer, we know whether the implementation conforms to one exact D65
construction epoch.

### L3 — Legacy migration

Inventory legacy ontology records, translate each through explicit admission
decisions, preserve provenance, compare replayed projections, and cut over only
after an owner accepts the exact migration candidate.

Exit evidence: migration is complete or every excluded record remains visible
as residue; rollback restores the pre-cutover state.

After this layer, we know whether `MIG-1` can move selected legacy meaning
without silently importing authority or history.

## First Task Session dry-run

Task ID: `CAL-ESOV-W0-SEMANTIC-PREDECESSORS`

Objective: make the first three D65 stages evaluable before authoring DomainSpec
source or Rust code.

Read scope:

- the exact `CAL-ESOV-0003` decision and receipt;
- the current proposal only after its digest drift is resolved;
- `CAV2-D65` and its machine schema;
- the exact DomainSpec kind, relationship, profile, compiler, and formation
  contracts needed by the proposed model.

Proposed write scope:

- capability definition proposals only where existing definitions are
  insufficient;
- one Product Capability candidate;
- one capability-local business ontology candidate;
- bridge and residue records that keep unresolved meanings visible.

Forbidden scope:

- DomainSpec authored source;
- Rust implementation or fixtures;
- generated graphs or projections;
- a concrete ConstructionBinding;
- legacy migration, publication, deployment, or external effects.

Done criteria:

- the proposal drift is owner-resolved;
- the registered Lab Project and Goal remain current and close bidirectionally;
- each required term is reused or proposed through its proper definition owner;
- the Product Capability and business ontology have exact digests;
- every proposed DomainSpec node and edge maps to business meaning;
- the reducer dataflow relationship gap has an explicit DomainSpec owner route;
- the next DomainSpec-authoring task has exact read/write scope and validation.

Registration result: `CA2-PROJECT-CYBERALCHEMY-LAB-ONTOLOGY-LIFECYCLE` and
`CA2-GOAL-CYBERALCHEMY-LAB-EVENT-SOURCED-ONTOLOGY` now provide the proposed
Project and draft Goal carrier. Registration does not supply the missing Product
Capability, business ontology, or ConstructionBinding.

Dry-run result: `BLOCK`. The context is sufficient to plan W0, but the stale
proposal binding, absent semantic predecessors, non-current default compiler
profile, and missing reducer relationship prevent an implementation handoff.

## Promotion rule

Promote one layer only when its exact exit evidence is current and its owner
gate is recorded. A passing local build does not promote the profile, admit the
system ontology, accept the Rust binding, prove conformance, authorize migration,
or create release authority.

## Claim ceiling

This document is a planning and readiness candidate linked to one proposed
Project and one draft Goal. It does not establish canonical definitions,
Product Capability adoption, business ontology
admission, DomainSpec source admission, compiler-profile admission, system
ontology validation, implementation acceptance, conformance, runtime behavior,
migration, publication, deployment, or external effect.
