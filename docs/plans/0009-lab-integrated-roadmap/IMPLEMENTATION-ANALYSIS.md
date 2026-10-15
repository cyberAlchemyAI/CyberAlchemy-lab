# Implementation reuse and change analysis

Inspected 2026-10-07. Exact source hashes are in [SOURCE-BASELINE.json](SOURCE-BASELINE.json). Analysis status: proposed; authority effect: none.

## Source-backed component decisions

| Existing source and selector | Behavior observed | Reuse / change recommendation | DAG tasks |
| --- | --- | --- | --- |
| `implementation/lab-runtime/v2/lab_runtime/sources.py`: `Capture`, `capture`, `freshness`, `resolve`, `validate_histories` | Explicit roots/overlays and schema selectors; exact current lookup binding; epoch and file hashing; exact history join validation. | Reuse resolver/history logic. Extract a compatible profile protocol and trusted reviewed selection; separate immutable baseline verification from currentness hints. | C01, C02, C04, C05 |
| `implementation/lab-runtime/v2/lab_runtime/cli.py`: `read_data`, `main` | Reads and initialization load package-local `profile.json`; exposes inspection/transaction/recovery/session commands. | Add explicit selected-profile/branch parameters in a successor candidate. Keep default selection explainable and fail closed on ambiguity. | C04, C05, R03 |
| `implementation/lab-runtime/v2/lab_runtime/store.py`: `initialize`, `roots`, `replay` | Initialization requires package profile equality; replay compares active profile then walks full chain, validates signatures and regenerates consequences. | Reuse full verifier. Build explicit successor-branch transition and measured verified reuse, without rewriting old transactions or trusting self-digested caches. | C03–C06 |
| `implementation/lab-runtime/v2/lab_runtime/store.py`: `review`, `authorize`, `apply`, `recover`, `lock` | Exact local owner signature, expected HEAD, writer exclusion, atomic commit and recognized interrupted-work recovery. | Preserve local operator trust boundary. Add transport/export separately; signature scope does not authorize repository promotion or general Agent actions. | C07, C09, W02 |
| `implementation/lab-runtime/v2/lab_runtime/operations.py`: `prepare`, `validate_record`, `validate_relation`, `consequences` | Closed target staging, current contract validation, exact endpoint pairs/qualifiers, stable cores and deterministic records. | Reuse pure staging and consequence order. Add domain reference checks and exact generator identity bindings under explicit protocols. New typed connections require declared closure. | C02, C07, C08, W01–W06 |
| `implementation/lab-runtime/v2/lab_runtime/governance.py`: `records` | Independent Decision cores share one bundle/checkpoint with generated boundary/decision/scope records. | Preserve one review envelope and deterministic bookkeeping. General policy/delegation enforcement belongs in a separate evaluator. | C07, W02 |
| `implementation/lab-runtime/v2/lab_runtime/operations.py`: `validate_relation`, `prepare`; D64 Typed Connection Extension Rule | Exact pairs/versions, closed qualifier field objects, axis-ID collision checks and current directional carrier roles are enforced. Full semantic-question preservation, pair-specific qualifier closure and canonical writable relation authority are not established by those checks. | Reuse structural checks and implement complete selected extension admissibility; bind explicit semantic review evidence and propose exact schema successors only if required. | C02, C14, C09 |
| `implementation/lab-runtime/v2/lab_runtime/session.py`: `Session._build`, `context`, `note`, `close` | Bounded derived carriers; HEAD/source/TTL invalidation; process-local notes; closure erases memory. Literal protocol/implementation/assignment reference labels exist. | Preserve ephemeral behavior. Resolve exact governed references where required, label protocol references honestly, and integrate durable lesson selection without persisting notes. This is context preparation, not a general Agent executor. | C08, C12, W02, W06 |
| `implementation/lab-runtime/v2/lab_runtime/graph.py`: `posture`, `build`, `query` | Separate admission/domain/runtime/session facets; closed local signatures; global projections; code links and bounded directional traversal. | Reuse bounded queries. Improve coverage obligations, exact implementation/evidence bridges and challenge joins through selected adapters. | O01–O03, R03 |
| `implementation/lab-runtime/v1/receipts/validation.json`, `v2/receipts/validation.json` | Recorded 33/38 checks and scoped disposable demonstrations, each bound to its own package. | Preserve exact existing files. New successor code receives fresh evidence; suite duration is not operation latency. | B00, C03, C09 |
| `docs/decisions/0075-lab-operational-runtime-v1-admission/apply.py`: `build`, `synchronize`, `check`, `main` | Exact decision-specific construction; immutable complete-bundle rename; reconstructible mirrors/current pointer; conversation authorization recorded honestly. | Adapt publication design into a reusable publisher. Do not modify or generalize the already applied D75 script in place. Handle mirror repair and expected repository baseline. | C07 |
| `authority/governance/candidates/0001-three-lens-module/project.py` and Plan 0007 | Prior overlay/lens research and coverage/query obligations; older source frontiers. | Reuse obligations and compare them with delivered runtime. Candidate-era status or older plan task status is not current authority. | B01, O01, O03 |
| `authority/artifact-types/*/*/schema.json`, current D74 registry and Relation Kind records | 121 current type identities, 143 registered versions and 41 current Relation Kinds in the selected registry anchors. | Generate all-current carrier/endpoint coverage. Validate selected workflows against exact carriers and closed relations; no universal payload/identity-field assumption. | C02, W01, O01, R04 |
| `ontology-lifecycle/runtime/src/lib.rs`, `context_adapter.rs`, `governance_context_adapter.rs` | Separate ontology events, exact joins, challenge contracts, cuts, checkpoint/tail structures and context projections. | Reuse as lifecycle library through an explicit Lab adapter. Map representation events, not a reinterpretation of Project histories. | O02 |
| `ontology-lifecycle/runtime-candidates/cal-ontology-graph-read-model/v1/src/lib.rs` | Bounded traversal, immutable graph generations, joined challenge state and disposable recovery caches for its own event contract. | Reuse only after exact mapping/parity. Rust graph acceleration remains optional if Python meets the selected query requirements. | O02, O03 |
| `implementation/bindings/ontology-product-lifecycle/v1/src/lib.rs`, `generator.py` | Bridge between ontology Product records and lifecycle events/context under named source boundaries. | Inspect existing binding/adoption authority separately from its code package. Adapt its mapping pattern, not assume a Lab-wide binding. | O01, O02, R04 |
| `implementation/bindings/ontology-product-event-runtime/v4/src/storage.rs`, `kernel.rs`, source manifest and receipts | Exact selected source-package adapters, immutable transactions and recovery. Generic source-record envelopes do not prove every source domain schema. | Reuse import allowlist and transaction patterns where fit; add exact Lab carrier validation/disposition. Preserve source-qualified identities and private/runtime state. | O04, O05 |
| `tooling/importers/migration_contract_import.py`, `capability_inventory_import.py` | Existing selected import tooling. | Reuse for declared source formats after fit analysis; no blanket import authority or transitive closure. | O04, O05 |
| Operational foundation Product/Thesis/Capability records | Declared outcome, consumers, contracts and exclusions; no realization bindings or demonstrated value in these bodies. | Use as Product inputs interpreted through D71 authority. Produce exact binding/adoption/conformance and pilot evidence. | R01, R04, R05 |
| `.gitignore`, inventory builders | Runtime/key/environment residue excluded; path/digest and generated structural/search indexes. | Keep permanent stores/keys out of Git; update indexes after planning/implementation material changes. Release review selects exact publishable scope. | B01, R02, R06, R07 |

## Proposed implementation layout

These paths are planned write scopes, not claims that modules already exist:

```text
implementation/lab-runtime/candidates/repeatable-operation/
  lab_runtime/          # successor of v2; profile, transition, replay, promotion integration
  profiles/             # independently reviewed compatible source-profile packages
  schemas/              # explicitly versioned implementation protocols
  receipts/             # exact future validation/measurement evidence
implementation/lab-workflows/candidates/v1/
  workflows/            # engineering/research/domain transitions
  authority/            # bounded action evaluator and tool adapters
  learning/             # failure/challenge/lesson application logic
implementation/lab-ontology/candidates/v1/
  adapters/             # exact Lab-to-ontology representation mapping
  profiles/             # local edge namespace, coverage and query contracts
docs/migration-plans/lab-selected-slice/  # future selected scope, inventory and disposition
product/lab/release-candidates/v1/       # future Product acceptance/release scope
```

The proposed language choice for local orchestration is Python, matching existing runtime and JSON Schema validation. Reuse Rust ontology components behind explicit adapters where justified. No new dependency versions or libraries are selected by this plan. Design tasks finalize module boundaries and package names before construction.

## Ordered implementation rules

1. Resolve carrier identity/discriminator/schema selector from current admitted registry; validate historical inputs under their exact contracts.
2. Capture immutable reviewed sources and exact profile/implementation compatibility before preparing effects.
3. Stage whole proposed contract/record closure; reject duplicate identities, ambiguous references, undeclared endpoint pairs and qualifiers.
4. Compute independent stable cores before deterministic postimages; bind exact scope, owner, base and evidence in authorization.
5. Publish one complete immutable transaction/bundle. The selected atomic pointer or directory commit controls visibility; mirrors are projections.
6. Derive histories, views, context and caches from committed sources. Retain a full independent verification path.
7. Evaluate action authority separately from data admission; enforce period/revocation/gates at dispatch and reconcile uncertain outputs.
8. Persist only eligible selected records through authorized effects. Clear session memory at closure/expiry; reconstruct later context from state and fresh views.

## Analysis ceiling

The selected code and contracts were read; their existing evidence was inspected. No runtime suite, benchmark, migration, publisher or live activation was executed during this planning request. Exact implementation conformance and performance of future modules remain their planned validation obligations.
