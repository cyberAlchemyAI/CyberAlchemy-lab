---
title: SFOL L8-L10 Ontology Construction Plan
status: implemented-development-candidate
updatedAt: 2026-09-01
owner: DomainSpec v2 owner and Test Derivation Engine owner
scope: product-capability, business-system-bridge, domainspec-source, generated-system-ontology
authorityEffect: none
---

# SFOL L8-L10 Ontology Construction Plan

## Outcome

Generalize the existing Auth-backed SFOL test closure into one bounded,
capability-neutral DomainSpec product capability:

> Compile an admitted, typed, bounded SFOL clause into deterministic neutral
> cases, deterministic negative-control evidence, replayable target
> observations, and a closed proof receipt without allowing a target adapter
> to author semantics.

L8, L9, and L10 are three implementation layers of that one capability. They
must not become three disconnected products or three independent ontologies.

Proposed stable candidate identities:

- Product Capability: `DSV2-CAP-SFOL-TEST-CLOSURE`
- capability-local business ontology:
  `DSV2-ONTOLOGY-SFOL-TEST-CLOSURE`
- DomainSpec feature: `sfol-test-closure`
- generated system ontology:
  `domainspec.system.sfol-test-closure`
- implementation profile: `domainspec-sfol-test-closure/v1`

These IDs identify a locally implemented v2 capability whose profile, source,
and generated system-ontology selections are bound to exact owner decisions.
The canonical Product Ontology projection remains a separate candidate until
its existing package passes source-currentness validation.

## Construction invariant

The work follows `CAV2-D65` in this exact order:

```text
canonical definitions
  -> Product Capability
  -> capability-local business ontology
  -> DomainSpec v2 authored source
  -> deterministic compiled graph and generated system ontology
  -> exact TypeScript/CLI/target binding
  -> conformance and replay evidence
  -> DomainSpec Product Ontology business/system/bridge projection
```

The final Product Ontology projection navigates the accepted evidence. It does
not replace any predecessor or manufacture an admission.

## Ontology placement

The repository already owns the canonical private product ontology package at
`projects/domainspec-v2/ontology/`. Therefore this capability should not create
a second product ontology package.

The planned ownership split is:

| Surface | Planned owner and location | Meaning |
| --- | --- | --- |
| Canonical definitions | `projects/domainspec-v2/definitions/DEFINITIONS.md` | Meaning of bounded partition calculus, witness domain, negative control, fault model, detection evidence, proof replay, and migration boundary. |
| Product Capability and local business ontology | `projects/domainspec-v2/capabilities/sfol-test-closure/` | Capability promise, consumer outcome, business concepts, operations, rules, exact property denominator, and residue. |
| Authored DomainSpec source | `projects/domainspec-v2/capabilities/sfol-test-closure/domainspec/` | Typed feature and node sources that express the capability without TypeScript, Rust, Auth, or CLI vocabulary. |
| Generated graph and system ontology | `projects/domainspec-v2/capabilities/sfol-test-closure/generated/` | Deterministic compiler output; never hand-authored as evidence of compilation. |
| Runtime realization | `projects/domainspec-v2/impl/test-derivation-engine/src/sfol/` and `src/cli.ts` | TypeScript implementation, stable API, and CLI composition. |
| Canonical product navigation | `projects/domainspec-v2/ontology/` | Business nodes, system nodes, and evidence-bearing bridge relations over admitted/current sources. |

The capability package is durable and private. Its proposed owner route is the
`DomainSpec v2 owner`; the TDE owner owns implementation correspondence, not
product meaning.

## Product capability boundary

The Product Capability should promise only this bounded outcome:

1. accept one exact admitted typed SFOL clause and its immutable proof context;
2. derive finite neutral cases using an explicit versioned partition strategy;
3. apply versioned negative controls at the semantic, derivation, binding,
   observation, lineage, scope, and provider seams;
4. bind cases to one exact implementation target and collect real
   observations;
5. prove exact stage-set closure and replay against allowlisted digests.

Explicit exclusions:

- translating or changing the existing Lean claim;
- claiming global logical equivalence from finite evaluation;
- requiring AST mutation when another negative control directly tests the
  selected seam;
- inventing witnesses absent from a declared domain;
- unbounded theorem proving or solver ownership;
- permitting a renderer or target adapter to choose cases or expected values;
- effectful target execution without a separately authorized runner;
- publication, deployment, release, or production-security claims.

## Capability-local business ontology

The business ontology is independent of TypeScript, Rust, Auth, files, and CLI
syntax. It owns these planned concepts:

| Candidate node | Role | Required meaning |
| --- | --- | --- |
| `SFOL-TEST-CLOSURE` | capability outcome | Exact bounded continuity from admitted clause to replayable implementation evidence. |
| `ADMITTED-CLAUSE-REF` | semantic input | Immutable identity and digest of the selected admitted SFOL clause and proof context. |
| `PARTITION-DOMAIN` | value object | Explicit finite typed witnesses and universes; absence is residue, never permission to guess. |
| `PARTITION-STRATEGY` | policy | Versioned exhaustive or reduction rule with canonical ordering and tie-breaking. |
| `PARTITION-BUDGET` | constraint | Maximum derivation work included in identity; overflow fails closed unless an explicit reduction strategy applies. |
| `NEUTRAL-CASE` | value object | Capability-neutral typed inputs and evaluator-owned expected result. |
| `FAULT-MODEL` | policy | Versioned declaration of one known-bad change, its seam, applicability, expected detector, and claim ceiling. |
| `NEGATIVE-CONTROL` | value object | Content-addressed application of one fault model to exact source, case, binding, observation, lineage, scope, or provider bytes. |
| `DETECTION-CLASSIFICATION` | evidence classification | `detected`, `survived`, `invalid-control`, `unsupported`, or `indeterminate`; absence of detection is never silently called equivalence. |
| `DETECTION-RELATION` | evidence relation | One declared check rejects one exact negative control for the expected reason. |
| `DETECTION-MATRIX` | evidence aggregate | Exact rows of negative-control IDs and columns of detector/check IDs with no inferred cells. |
| `AST-MUTATION-PROFILE` | optional policy specialization | Optional typed SFOL fault model used to assess reduced-case discrimination; it is not required by the base EVF chain. |
| `BOUNDED-EQUIVALENCE-EVIDENCE` | optional evidence specialization | Equality of original and mutated results over one exact declared finite domain; never global logical equivalence. |
| `TARGET-BINDING` | bridge input | Exact binding from one neutral case shape to one observed implementation operation. |
| `PROOF-RECEIPT` | evidence aggregate | Exact equality across denominator, projected, validated, typed, generated, bound, observed, and evaluated case sets. |
| `REPLAY-ALLOWLIST` | policy | Exact artifact and tool digests that may be replayed together. |
| `MIGRATION-BOUNDARY` | lifecycle rule | Explicit predecessor/successor compatibility without rewriting historical evidence. |
| `DERIVATION-RESIDUE` | typed gap | Unsupported form, missing witness, exceeded bound, indeterminate evaluation, or incompatible version. |

Planned domain operations:

- `DSV2-SFOL-OP-DERIVE-PARTITIONS`
- `DSV2-SFOL-OP-APPLY-NEGATIVE-CONTROLS`
- `DSV2-SFOL-OP-BUILD-TEST-CLOSURE`
- `DSV2-SFOL-OP-REPLAY-TEST-CLOSURE`

Planned invariants:

1. Expected results come only from the typed SFOL evaluator.
2. Every generated case belongs to the exact admitted clause denominator.
3. Every witness belongs to the declared typed finite domain.
4. Canonical order and tie-breaking are versioned inputs to identity.
5. Every required negative control names one fault model, one affected seam,
   one expected detector, and one exact original/control identity pair.
6. `applicable_controls = detected union survived union indeterminate` with
   disjoint sets; invalid and unsupported controls remain outside that
   denominator.
7. A passing negative-control result requires every required applicable control
   to be `detected`; optional profiles cannot become gates unless the selected
   capability profile explicitly requires them.
8. AST-specific `equivalent-bounded` evidence is permitted only when the
   selected finite domain is declared and digest-bound. A non-exhaustive case
   set may report `survived`, not equivalence.
9. Replay requires exact input, profile, tool, target, binding, and receipt
   digests; similar or current-by-name is insufficient.

## DomainSpec authored source

The first authored source should model only the portable operations and their
rules. Proposed inventory:

```text
projects/domainspec-v2/capabilities/sfol-test-closure/
  product-capability.json
  business-ontology.json
  property-denominator.json
  domainspec/
    project.json
    feature.json
    nodes/
      partition-domain.json
      partition-strategy.json
      neutral-case.json
      fault-model.json
      negative-control.json
      detection-matrix.json
      ast-mutation-profile.json
      proof-receipt.json
      replay-allowlist.json
      migration-boundary.json
      derive-partitions.json
      apply-negative-controls.json
      build-test-closure.json
      replay-test-closure.json
      partition-closure-rule.json
      negative-control-closure-rule.json
      replay-closure-rule.json
  generated/
    source-manifest.json
    compiled-graph.json
    system-ontology.json
    build-receipt.json
  construction-binding.json
  conformance/
    implementation-binding.json
    evidence.json
```

The exact node split should be reduced if the DomainSpec compiler can express a
coherent operation with fewer nodes. File count is not evidence of semantic
coverage; the property denominator is.

## Generated system ontology

The compiler-generated system ontology should identify these system roles and
their exact bindings:

- SFOL language decoder and typechecker;
- typed evaluator;
- finite partition engine;
- partition-strategy registry;
- negative-control registry and seam adapters;
- detection classifier;
- detection-matrix builder;
- optional SFOL AST-mutation profile adapter;
- case/binding/observation/evaluation join;
- proof-receipt builder and replay verifier;
- target profile registry and runner boundary;
- stable TDE API;
- stable TDE CLI;
- artifact schemas and validators;
- migration adapter for historical Auth v1/v2 consumers.

System status must be per node: `designed`, `implemented`, or
`evidence-bound`. The current finite exhaustive partitioner may support an
`implemented` candidate claim only after it is bound to the new authored source
and generated ontology. The current AST-mutation prototype remains an optional
experimental adapter: it cannot support an adequacy gate while it lacks honest
`survived` and `unsupported` outcomes and treats every undetected valid mutant
as bounded-equivalent. Existing code by itself cannot backfill the construction
chain.

## Canonical DomainSpec Product Ontology projection

After predecessor admission and compiler/conformance evidence exist, amend the
existing `projects/domainspec-v2/ontology/` package rather than creating a new
ontology.

Planned business nodes:

- `dsv2.product.sfol-test-closure`
- `dsv2.product.bounded-partition-calculus`
- `dsv2.product.negative-control-discrimination`
- `dsv2.product.test-closure-replay`

Planned system nodes:

- `dsv2.system.sfol-partition-engine`
- `dsv2.system.evf-negative-control-engine`
- `dsv2.system.evf-detection-matrix-builder`
- `dsv2.system.sfol-ast-mutation-profile`
- `dsv2.system.sfol-proof-replay`
- `dsv2.system.tde-sfol-api`
- `dsv2.system.tde-sfol-cli`
- `dsv2.system.tde-sfol-migration-adapter`

Planned bridge relations:

- product closure `realized_by` partition, negative-control, proof, API, and CLI
  components;
- bounded partition calculus `tested_by` non-Auth vertical and determinism
  tests;
- negative-control discrimination `tested_by` semantic, derivation, binding,
  observation, lineage, scope, and provider controls;
- optional AST-mutation profile `constrained_by` an explicit fault-model and
  exhaustive-domain or survivor-reporting contract;
- replay promise `observed_by` two-run byte identity and exact allowlist
  verification;
- capability `constrained_by` partition budget, finite-domain requirement,
  target runner authority, and migration boundary;
- every system node `traced_to` one admitted business rule or operation.

Each bridge edge requires separate business and system source refs. Missing
evidence becomes an explicit residue row; it is not smoothed into a relation.

Prospective ontology package mutations, only after admission/currentness gates:

- `ontology/sources.json`: add exact capability, generated graph/system
  ontology, implementation, tests, CLI, schemas, and evidence sources;
- `ontology/nodes.json`: add the business and system nodes above;
- `ontology/relations.json`: add system topology and evidence-bearing bridge
  edges;
- `ontology/residue.json`: add unsupported operators, non-exhaustive domains,
  effectful runners, unsupported negative-control seams, global-equivalence
  proof, optional AST-profile limitations, and migration gaps;
- `ontology/views/business.md`, `views/system.md`, `views/bridge.md`: refresh
  human projections;
- `ontology/schema/<dated-sfol-test-closure-amendment>.json`: add only if the
  existing closed schema cannot represent a required record;
- `ontology/validation-receipts/<next-epoch>.json`: append; never overwrite.

## L8 - bounded capability-neutral partition calculus

Decision question:

> After L8, we know whether supported finite SFOL forms produce deterministic,
> capability-neutral cases under explicit witness and budget bounds.

Minimum working unit:

- retain `exhaustive-finite/v1`;
- add `mcdc/v1` for Boolean terms over budget with fixed atom order and
  lexicographic tie-breaking;
- add explicit comparison-boundary witness synthesis from declared typed
  domains;
- add set/list membership, equality, multiplicity, and cardinality strategies;
- add empty, satisfying, and violating finite-universe quantifier strategies;
- emit typed residue for unsupported/unbounded/missing-domain forms;
- prove one non-Auth vertical through cases, bindings, observations,
  evaluations, and replay.

Exit evidence:

- two clean derivations are byte-identical;
- generic source and fixtures contain no Auth identifiers;
- each supported operator has positive, boundary, residue, and budget tests;
- property-denominator coverage is exact;
- unsupported semantics make dependent completeness `not_evaluable`.

## L9 - deterministic negative-control and discrimination evidence

Decision question:

> After L9, we know whether each required EVF seam rejects its declared
> known-bad variants, and whether every non-detection remains visible without
> overstating equivalence or adequacy.

Minimum working unit:

- a versioned fault-model registry covering semantic, derivation, binding,
  observation, lineage/currentness, scope/claim-ceiling, and provider-
  translation seams;
- stable negative-control identity using the fault-model version, affected
  seam, exact original digest, exact changed digest, and expected detector;
- controls for omitted/duplicated cases, wrong or stale bindings, corrupted
  observations, altered evaluator results, mismatched stage sets, stale tool
  digests, widened claims, and meaning-changing provider translations;
- explicit `detected`, `survived`, `invalid-control`, `unsupported`, and
  `indeterminate` classifications;
- an exact detection matrix with control, detector, expected-reason, observed-
  reason, and set digests;
- an optional `sfol-ast-mutation/v1` profile only for a selected semantic fault
  model. It may emit a subordinate kill matrix when the consumer explicitly
  requests mutation-adequacy evidence.

Exit evidence:

- every required applicable negative control is detected for the declared
  reason;
- survived, invalid, unsupported, and indeterminate controls remain explicit
  and block only the claims that depend on them;
- each seam has at least one positive baseline and one known-bad control;
- two runs produce the same ordered control IDs and detection-matrix bytes;
- when the optional AST profile is selected, it reports honest survivors and
  may classify bounded equivalence only over an exact exhaustive finite domain;
- exhaustive L8 partitions do not require AST mutation to close the base EVF
  receipt, while reduced strategies may select it as additional adequacy
  evidence.

## L10 - stable API, CLI, replay, and migration boundary

Decision question:

> After L10, we know whether consumers can invoke, validate, replay, and migrate
> the capability without Auth orchestration or implicit local state owning its
> semantics.

Minimum working unit:

- stable library entry points for `derive`, `challenge`, `close`, `verify`, and
  `replay`;
- CLI namespace with equivalent commands, structured JSON diagnostics, and
  documented exit codes;
- exact request/result schemas and a target-profile registry;
- `--check` mode that performs no writes;
- explicit output directory for materialization and atomic publication;
- no cwd inference, filesystem enumeration, timestamps, hostnames, or random
  values in semantic identity;
- replay allowlist binding all semantic, tool, target, binding, and artifact
  digests;
- additive migration adapter preserving Auth historical v1 evidence and the
  existing v2 successor evidence byte for byte.

Proposed CLI grammar:

```text
tde sfol derive  --request <request.json> [--out <directory> | --check]
tde sfol challenge --request <request.json> [--out <directory> | --check]
tde sfol close   --request <request.json> [--out <directory> | --check]
tde sfol verify  --receipt <receipt.json>
tde sfol replay  --receipt <receipt.json> --allowlist <allowlist.json>
```

Exit evidence:

- API and CLI produce byte-identical semantic artifacts for the same request;
- check mode leaves the worktree unchanged;
- schema-invalid, stale, partial, duplicate, extra, or incompatible inputs fail
  closed with stable diagnostics;
- replay succeeds from an isolated directory using only allowlisted handles;
- historical Auth v1 and current v2 digests remain unchanged;
- the Auth adapter maps neutral inputs to the Rust target but owns no case
  selection, oracle, negative-control selection, classification, or proof
  logic.

## Implementation waves

| Wave | Layer | Planned effect | Promotion evidence |
| --- | --- | --- | --- |
| W8.0 | ontology predecessors | Propose definitions, Product Capability, business ontology, property denominator, and owner decision packet. | Exact immutable candidate digest and separate owner decision; no status-field admission. |
| W8.1 | authored source | Author the portable DomainSpec feature and compile it twice. | Byte-identical graph, source manifest, system ontology, and build receipt. |
| W8.2 | L8 runtime | Implement MC/DC, comparison, set/list, and quantifier strategies plus residue. | Non-Auth vertical closes; budget and unsupported controls fail closed. |
| W9.0 | L9 runtime | Implement the fault-model registry, seam controls, honest classifications, and detection matrix. | Every required applicable control is detected; survivors and residue are explicit; exact matrix closure and two-run identity. |
| W9.1 | optional L9 profile | Repair and bind `sfol-ast-mutation/v1` only if a selected consumer requires mutation adequacy or an L8 reduction strategy needs fault-model evidence. | Honest survivor reporting, exhaustive-domain-bound equivalence, and no effect on the base EVF gate when unselected. |
| W10.0 | L10 contracts | Freeze request/result schemas, API, CLI commands, profile registry, diagnostics, and validator. | API/CLI parity, check-only purity, hostile fixtures, package validation. |
| W10.1 | migration/replay | Replace Auth orchestration with a thin adapter and add isolated replay. | v1/v2 byte preservation, isolated replay PASS, stale allowlist FAIL. |
| W10.2 | D65 and ontology bridge | Bind exact implementation/evidence, then amend the canonical Product Ontology. | Complete current D65 candidate, source-current ontology validation, append-only receipt, independent conformance review. |

## Non-regression and migration rules

- The existing Lean claim and historical v1 evidence remain unchanged.
- The admitted SFOL claim is an input, not generated or revised by TDE.
- L7 exhaustive Boolean behavior remains a supported profile.
- Current Auth v2 artifacts remain historical successor evidence; migration
  adds a compatibility manifest rather than rewriting them.
- A fault-model, optional AST catalog, or partition-strategy version change
  creates a new identity and receipt.
- Bounded equivalence never becomes theorem-level or global equivalence by
  wording, count, or package status.
- A generated system ontology cannot be replaced by a hand-authored lookalike.
- Product Ontology validation cannot admit a capability, accept an
  implementation, or prove conformance.
- Publication and branch integration remain separate from this plan.

## Recommended next action

The exact v2 profile-eligibility, source-acceptance, and system-ontology
decisions are now selected, and the capability-local D65 chain has a local
technical pass. The next bounded action is W10.2 canonical Product Ontology
enrichment using `product-ontology-amendment-candidate.json`:

1. reconcile the pre-existing canonical package source-currentness drift;
2. apply the candidate's business nodes, system nodes, bridge relations, and
   explicit residue to `projects/domainspec-v2/ontology/`;
3. append a fresh validation receipt and rerun `node validate-ontology.mjs
   --require-receipt`;
4. perform publication only through a separately authorized Git envelope.

The canonical Product Ontology was deliberately not mutated in this epoch:
its validator is currently blocked by stale/missing pre-existing source
bindings, independent of the SFOL v2 candidate.

## Implementation result

- W8.0: definition, Product Capability, business-ontology, and property-
  denominator candidates exist with exact owner selections recorded.
- W8.1: the capability-local DomainSpec source compiles twice to an identical
  13-node, 8-edge graph and generated system-ontology candidate.
- W8.2: exhaustive finite and deterministic MC/DC strategies, primitive
  boundaries, collection witnesses, universe variants, typed residue, and a
  non-Auth partition-to-proof vertical are implemented.
- W9.0: all seven seam types, exact observations, honest classifications, and
  content-addressed detection matrices are implemented.
- W9.1: optional AST mutation reports real survivors and permits bounded
  equivalence only for a declared exhaustive finite domain.
- W10.0: versioned API, CLI, request schemas, target profiles, close/verify/
  replay operations, atomic output, check-only operation, and stable
  diagnostics are implemented.
- W10.1: an additive Auth adapter and migration manifest preserve the v1
  carriers; validation hashes the Lean and Auth v1 preimages before PASS.
- W10.2: exact implementation, local conformance, profile-eligibility,
  source-acceptance, and system-ontology selections exist. Canonical ontology
  enrichment is prepared as a v2 candidate and remains blocked on existing
  source-currentness drift.

## Ontology Vault planning result

- Mode: implemented capability-local development candidate
- Ontology type: `business-system-bridge`
- Type selection: inferred with high confidence
- Materialization: capability package complete; canonical package enrichment deferred
- Package root: `projects/domainspec-v2/ontology/`
- Package owner: `DomainSpec v2 owner`
- Visibility: private
- Ontology mutations performed: generated capability-local system-ontology candidate only; canonical package unchanged
- Validation: local technical conformance PASS with two test and compile runs
- Blocker before ontology enrichment: pre-existing canonical ontology
  source-currentness drift; the v2 capability, source, profile, generated
  system ontology, and conformance evidence are exact-bound and locally valid
