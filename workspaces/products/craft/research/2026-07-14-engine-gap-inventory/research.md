# DomainSpec v2 Engine Gap Inventory — Explorer Transcript

Dispatch: `2026-07-14-domainspec-v2-engine-gap-inventory`

This file preserves the explorer returns verbatim. Synthesis and reviewer material do not belong here.

## Agent 1 — Shannon, Claude

# Shannon, Claude — DomainSpec v2 executable-engine audit

## Executive answer

Filling the semantic engine is the first major implementation priority, but it is not the next overall roadmap action. The roadmap requires `FPR-01` through `FPR-03` to establish the authority, profile, and business-to-spec denominator before `FPR-04` can compile an authoritative specification graph. See `projects/domainspec-v2/development/first-production-release/ROADMAP.md:58-67,94-104`.

The existing package is a useful deterministic obligation prototype:

```text
feature Markdown
  → local parser IR G
  → hard-coded obligation derivation
  → TEST-SPEC / generated tests
```

It is not yet the graph engine required by the intended implementer-agent loop:

```text
authoritative Spec
  → Sg
  → bounded traversal / compiler IR G
  → implementation
  → I_struct
  → directional conformance
```

The highest-priority engine work is therefore `FPR-04`: construct and verify `Spec → Sg`, then explicitly encode `Sg → G`. Extending obligation rules inside the current local `G` before that would deepen the wrong substrate.

## Evidence boundary

Read-only inspection covered:

- `projects/domainspec-v2/development/first-production-release/ROADMAP.md`
- `projects/domainspec-v2/development/first-production-release/craft/expected-node-edge-manifest.yml`
- `projects/domainspec-v2/development/first-production-release/research/2026-07-12-expanded-capability-frontiers/findings.md`
- `projects/domainspec-v2/definitions/meta-types/meta-types.yml`
- `projects/domainspec-v2/definitions/relationships/relationships.yml`
- `projects/domainspec-v2/impl/spec/TAXONOMY.md`
- `projects/domainspec-v2/impl/test-derivation-engine/README.md`
- `projects/domainspec-v2/impl/test-derivation-engine/package.json`
- Every executable source and focused test under `projects/domainspec-v2/impl/test-derivation-engine/src/`
- The Financial Settlement fixture and binding only through parser/deriver calls

No files were edited. The final scoped status showed only pre-existing untracked first-production-release artifacts.

## Commands and checks

| Check | Result |
|---|---|
| Local `vitest run` | `97/97` passed |
| Local `tsc --noEmit` | Passed |
| `tsx src/cli.ts derive __definitely_missing_engine_gap_witness__` | Exit `0`; emitted an empty obligation table |
| `tsx src/cli.ts lint __definitely_missing_engine_gap_witness__` | Exit `0`; reported `CLEAN (0)` |
| Parse Financial Settlement | 62 nodes, 2 edges, 79 obligations |
| Financial hybrid generation | 79 obligations; 12 assertions, 1 property, 67 coverage gaps |
| FPR target artifact existence check | Core `Sg`, compiler IR, obligation registry, `I_struct`, and conformance artifacts absent |
| Package-manager route | `pnpm` failed before engine execution with Corepack `ERR_VM_DYNAMIC_IMPORT_CALLBACK_MISSING`; direct installed binaries worked |

The package tests are genuinely green, but they validate the current prototype contract—not FPR-04/07/08 conformance.

## Current executable pipeline

1. `parse(featureDir)` reads nine known Markdown aspect filenames and constructs a local `ConceptGraph`. Every file is optional; a missing file is explicitly not a violation.  
   Evidence: `src/grammar/index.ts:910-959`.

2. `derive(graph, rules)` applies hard-coded derivation functions and emits deterministic obligations. Although it accepts a `RuleSet`, the `_rules` parameter is unused.  
   Evidence: `src/rules/index.ts:51-56,631-664`.

3. `deriveFeature()` returns only obligations, rendered spec text, and optional tests. It does not return or persist `Sg`, a source manifest, a compiler-IR manifest, or a retraction receipt.  
   Evidence: `src/index.ts:11-33`.

4. Legacy test generation emits one `it.todo` per obligation. Hybrid generation emits assertions for the supported pure subset and `it.skip` for unresolved coverage.  
   Evidence: `src/emit/tests.ts:71-91,330-433`.

5. The CLI can report coverage gaps but returns `0` after hybrid generation. It also prints parser violations and continues on the `emit-tests` path.  
   Evidence: `src/cli.ts:353-394`.

6. Round-trip validation compares derived obligation identities with a committed test catalogue. A pass can retain classified “irreducible” missing rows.  
   Evidence: `src/roundtrip/index.ts:789-865`; accepted explicitly by `src/index.test.ts:266-299`.

## Witnessed gaps

### `ENG-GAP-01` — Authoritative `Spec → Sg` projection is absent

- Class: absent path.
- Witness: the proposed `spec-graph.json`, `compiler-ir.json`, `semantic-manifest.json`, schemas, source manifest, and `verify-spec-projection.cjs` do not exist.
- Current engine instead parses Markdown directly into its local `G`; `deriveFeature()` exposes no `Sg`.
- Owner: already owned by `FPR-04`, semantic, validation, and engine owners.
- Evidence: `expected-node-edge-manifest.yml:121-146`; `src/index.ts:22-33`.
- Dependency/priority: `P0-engine`, after `FPR-01..03`.
- Implementer-agent impact: there is no authoritative graph for the agent to traverse. Traversing current `G` would traverse parser internals rather than DomainSpec intent.

### `ENG-GAP-02` — Missing and empty sources are accepted as successful input

- Class: false-green validation path.
- Smallest live witness:

```text
derive nonexistent-target → exit 0 + empty table
lint nonexistent-target   → exit 0 + CLEAN (0)
```

- The behavior is also unit-tested as expected: `deriveFeature("nonexistent-feature")` must return an empty obligation set.
- Owner: `FPR-04` owns missing/empty source and graph rejection; `FPR-07` owns zero-obligation rejection.
- Evidence: `src/grammar/index.ts:934-940`; `src/index.test.ts:28-38`; `src/cli.ts:179-206,403-427`; `expected-node-edge-manifest.yml:140-144,217-221`.
- Dependency/priority: first negative control in the `FPR-04` walking skeleton.
- Implementer-agent impact: an absent or misresolved feature can look like successful completion with no work frontier.

### `ENG-GAP-03` — Local `G` edge semantics are underbuilt and collide with current authority

- Class: semantic graph mismatch.
- The local IR declares 7 edge labels, but the parser contains only one `edges.push`: `Consumer --consumes--> Event`.
- Financial Settlement produced 62 nodes but only 2 edges, both `consumes`.
- Current DomainSpec authority defines 30 active signatures and defines `consumes` as `Component --consumes--> Hook`.
- The local IR also defines `enforces` as `Operation → Invariant`, while authority defines it as `Rule → Operation`.
- Owner: `FPR-04` quotient/projection work; definitions and relationship authority remain upstream.
- Evidence:
  - `src/ir/types.ts:5-35`
  - `src/grammar/index.ts:486-545`
  - `definitions/relationships/relationships.yml:1-18,83-97,323-337`
  - `expected-node-edge-manifest.yml:129-144`
- Dependency/priority: `P0-engine`; resolve as explicit `Sg → G` mappings, not by silently renaming either graph.
- Implementer-agent impact: current edges cannot drive authoritative composition traversal. The same label can mean incompatible source/target signatures.

### `ENG-GAP-04` — Independent `Sg → G → Sg_canonical` retraction is absent

- Class: absent verification path.
- Current round-trip compares generated obligation identities against a human test catalogue; it does not independently reconstruct and compare the semantic graph.
- Its accepted pass may retain irreducible missing rows.
- Owner: `FPR-04`, semantic and validation owners.
- Evidence: `src/roundtrip/index.ts:789-865`; `src/index.test.ts:286-299`; `expected-node-edge-manifest.yml:129-145`.
- Dependency/priority: immediately after the smallest `Sg` compiler.
- Implementer-agent impact: semantic loss during graph compilation can remain invisible while downstream obligation tests stay green.

### `ENG-GAP-05` — Obligation derivation owns its own denominator

- Class: validation authority collapse.
- The derivation rules say they were reverse-engineered from documentation/test categories.
- `RuleSet` contains only a version string, and `_rules` is ignored; all obligation classes are selected directly in generator code.
- Independent `O_spec(P)`, expected outcomes, and evidence requirements do not exist.
- Owner: already owned by `FPR-07`, semantic, validation, and generation owners.
- Evidence: `src/rules/index.ts:1-39,51-56,631-655`; `expected-node-edge-manifest.yml:198-223`.
- Dependency/priority: may begin only after `FPR-04`; cannot close before `FPR-05/06`.
- Implementer-agent impact: the same mechanism generates and implicitly judges the work frontier, so missing obligation classes cannot be detected reliably.

### `ENG-GAP-06` — Generated verification reports holes but succeeds

- Class: executable false-green.
- Legacy mode emits `it.todo`.
- Hybrid mode emits `it.skip` for unresolved obligations.
- Current Financial Settlement witness: 67 coverage gaps among 79 obligations.
- `emit-tests` returns `0` after writing/printing the result, regardless of nonzero coverage gaps, and does not fail on parser violations.
- Owner: `FPR-07`.
- Evidence: `src/emit/tests.ts:71-91,330-433`; `src/cli.ts:353-394`; `src/emit/tests.test.ts:61-107`; `expected-node-edge-manifest.yml:217-221`.
- Dependency/priority: `P1`, after independent obligation ownership.
- Implementer-agent impact: the agent may classify a generated suite as completed even when most obligations remain unexecuted.

### `ENG-GAP-07` — Implementation-graph extraction is absent

- Class: absent path.
- No frozen-root AST/symbol/import/call extractor was found in the engine.
- `implementation-graph.json`, its schema, root manifests, and tag reconciliation evidence are absent.
- Owner: already owned by `FPR-08`, implementation/platform owner.
- Evidence: `expected-node-edge-manifest.yml:225-247`.
- Dependency/priority: parallel lane after `FPR-04/05`; it should not be folded into the semantic parser.
- Implementer-agent impact: the agent can generate code but cannot observe what was actually built or construct `I_struct`.

### `ENG-GAP-08` — Cross-graph conformance join is absent

- Class: absent integration path.
- No conformance vector or validator connects `Sg`, obligations/tests, architecture, and `I_struct`.
- Owner: `FPR-09`; downstream of `FPR-03..08`.
- Evidence: `ROADMAP.md:65-67`; `expected-node-edge-manifest.yml:249-269`.
- Dependency/priority: later technical join, not the first engine work unit.
- Implementer-agent impact: traversal has no evidence-backed completion predicate. It can visit nodes but cannot prove realization.

### `ENG-GAP-09` — Runtime documentation and invocation surfaces are stale

- Class: stale projection/toolchain residue.
- `README.md` says the parser and derivation rules are typed stubs, despite the observed `97/97` implementation suite.
- The normal `pnpm` route failed in the current environment while direct local binaries passed.
- Owner: test-derivation-engine package/read-model maintenance; broader hermetic execution belongs downstream to release substrate.
- Evidence: `README.md:23-25`; `package.json:8-19`.
- Dependency/priority: low relative to `FPR-04`, but repair before presenting package-level readiness.
- Implementer-agent impact: an agent relying on package docs or the documented command route receives an incorrect capability picture or cannot run the engine reproducibly.

## Smallest safe work sequence

1. Complete `FPR-01` authority reconciliation; do not choose an engine vocabulary before the active denominator is ratified.
2. Create the `FPR-04` source/profile gate that rejects missing required documents and an empty graph.
3. Emit the smallest schema-valid `Sg` using current meta-type and relationship authorities.
4. Encode `Sg → G` through an explicit quotient/mapping registry, preserving the local obligation IR only where justified.
5. Build the independent `Sg → G → Sg_canonical` comparator and kill missing-node, mutated-field, mutated-edge, and unapproved-quotient controls.
6. Reattach the existing deterministic derivation code as an `O_gen` producer.
7. Add independently owned `O_spec`, expected outcomes, evidence requirements, and a zero-gap nonzero-exit gate.
8. Build `I_struct` extraction as a separate `FPR-08` subsystem, then join it through `FPR-09`.

The first concrete engine witness should be deliberately tiny: one required source, two authoritative nodes, one admitted DomainSpec relationship, one derived obligation, and mutations for missing source, empty graph, changed node type, reversed edge, and missing obligation. That establishes the traversal spine before broadening the engine.

## Agent 2 — Senge, Peter

## Structural-governance explorer — `Senge, Peter`

### One-line priority answer

Filling the engine is the first major implementation capability, but it is not the first safe work unit: the live continuation authority requires `FPR-01 → FPR-02 → FPR-03` before `FPR-04`, because the engine currently has no ratified source set, supported profile, or non-contradictory graph vocabulary to compile ([ROADMAP.md:54-104](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/first-production-release/ROADMAP.md:54), [ledger.yml:77-82](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/.craft/ledger.yml:77)).

### Authority sources

| Source | Authority role |
|---|---|
| [`.craft/ledger.yml:1-14`](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/.craft/ledger.yml:1) | Continuation authority; FPR context is `stage: plan`, `gate: block`, next move `FPR-01` ([lines 284-312](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/.craft/ledger.yml:284)). |
| [`ROADMAP.md:31-75`](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/first-production-release/ROADMAP.md:31) | Canonical operational projection; separates `B`, `Sg`, `G`, `I_struct`, and evidence planes. |
| [`expected-node-edge-manifest.yml:49-66`](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/first-production-release/craft/expected-node-edge-manifest.yml:49) | Machine proposal for `FPR-01`; names exact missing baseline artifacts and negative controls. |
| [`AUTHORITY-MODEL.md:40-64`](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/authority/AUTHORITY-MODEL.md:40) | DomainSpec may type, derive, validate, and rule; it cannot infer runtime satisfaction or implementation acceptance. |
| [`source-spine.md:11-20`](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/authority/source-spine.md:11) | Local source posture; v1 is harvested precedent, not a resolution path. |
| [`meta-types.yml:1-23`](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/definitions/meta-types/meta-types.yml:1) | Current DS-D1 machine read model: 24 staged candidates, 13 registered backend members, 11 formation-deferred UI types. |
| [`relationships.yml:1-18`](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/definitions/relationships/relationships.yml:1) | Current DS-D8 machine authority: 30 active signatures. |
| [`IMPORT-MANIFEST.md:22-46`](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/IMPORT-MANIFEST.md:22) | Engine was imported verbatim; TAXONOMY, TEST-PIPELINE, DRIFT, CONSTITUTION and Batch-2 tooling still carry reformulation work. |
| [`spec-ontology-unification/toy/verdict.md:13-65`](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/research/spec-ontology-unification/toy/verdict.md:13) | Narrow substrate evidence only; Lane Z versus Lane A and agent-cost benefit remain unproved. |

### Dependency graph

```text
FPR-00 accepted decision
  → FPR-01 authority baseline
      → FPR-02 exact supported profile
          → FPR-03 governed B → Spec direction and total mapping
              → FPR-04 Spec → Sg compiler and bounded retraction
                  ├─→ FPR-05 node patterns and edge composition
                  ├─→ FPR-06 bounded formal profile
                  ├─→ FPR-08 code → I_struct
                  └─→ FPR-07 obligations and generated verification
                              ↓
                        FPR-09 cross-graph conformance
```

Before `FPR-01`, safe parallel work is limited to evidence census, stale-reference detection, mutation-test harnesses, and finishing already-owned closeouts. It must not mint a graph schema, denominator, or supported vocabulary ([ROADMAP.md:77-104](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/first-production-release/ROADMAP.md:77)).

### Reconciled live contradictions

These counts describe different repository states or maturity planes. They must be disposed by an owner baseline, not resolved by selecting the most convenient number.

| Dimension | Current machine surface | Conflicting current/historical surfaces | Reconciliation |
|---|---|---|---|
| Backend node types | 13 registered members; `DS-D1.10` intentionally absent ([meta-types.yml:9-23](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/definitions/meta-types/meta-types.yml:9)) | Ledger descriptions still say 14 ([ledger.yml:414-423](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/.craft/ledger.yml:414), [1173-1179](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/.craft/ledger.yml:1173)); `DEFINITIONS.md` still says `DS-D1.1..14` ([1053-1065](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/definitions/DEFINITIONS.md:1053)). | Saga collapse was explicitly selected and repository-local migration completed: 13 schemas and 30 signatures pass ([decision:32-58](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/ds-d1-improvement-plan/decisions/DEC-DSD1-SAGA-FORK.md:32), [validation:5-21](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/saga-removal/runs/SWU-SGRM-008/VALIDATION-SUMMARY.md:5)). Current evidence favors 13, but only `FPR-01` may ratify the release baseline. |
| Total staged labels | 24 = 13 backend + 11 UI ([TAXONOMY.md:1-25](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/impl/spec/TAXONOMY.md:1)) | `DEFINITIONS.md` and index still say 25 ([DEFINITIONS.md:1058-1065](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/definitions/DEFINITIONS.md:1058), [DEFINITIONS-INDEX.md:43-58](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/definitions/DEFINITIONS-INDEX.md:43)). | 25 is the pre-Saga-collapse vocabulary; 24 is the current registry. Stale references remain live. |
| Relationship signatures | Machine and human root authority agree on 30 ([relationships.yml:17-18](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/definitions/relationships/relationships.yml:17), [relationships.md:17-27](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/definitions/relationships/relationships.md:17)). | `DEFINITIONS.md` says both 31 and 30 ([358-359](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/definitions/DEFINITIONS.md:358), [1030-1032](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/definitions/DEFINITIONS.md:1030), [1137-1139](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/definitions/DEFINITIONS.md:1137)); `DEFINITION-DRIFT-AUDIT.md` claims pass while citing 31 ([38-57](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/definitions/DEFINITION-DRIFT-AUDIT.md:38)); `LEARNING-ORDER.md` still says 31 ([lines 8-13](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/impl/spec/meta-types/LEARNING-ORDER.md:8)). | The removed 31st signature was the standalone Saga `orchestrates` row. Current machine evidence favors 30; the stale “pass” is itself an FPR-01 witness. |
| Maturity status | DS-D1 registry and all 13 cards remain `candidate`, owner-confirmation gated ([meta-types.md:8-22](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/definitions/meta-types/meta-types.md:8)). | `TAXONOMY.md` calls the same 13 backend types “active” ([lines 1-7](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/impl/spec/TAXONOMY.md:1)). | Likely distinct dimensions—implementation-admitted versus definition-promoted—but no machine baseline currently names those dimensions. The engine must not collapse them into one `status`. |

## Authority gap candidates

### `AUTH-GAP-01` — FPR authority baseline does not exist

- Witness: `authority-baseline.yml` and its ratification receipt are declared targets but absent; the manifest marks `FPR-01` `blocked-open` ([expected manifest:49-66](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/first-production-release/craft/expected-node-edge-manifest.yml:49)).
- Owner/state: already owned by `FPR-01`; definitions, validation, and layering owners; blocked-open.
- Priority: **P0 prerequisite**.
- Smallest safe work unit: author a baseline schema and source census, derive counts/statuses from exact files, record every stale projection disposition, require owner ratification, and reject one mutated count and one stale path.
- Dogfood effect: gives the implementer one snapshot ID and prevents traversal from silently switching between 13/14, 24/25, or 30/31 graphs.

### `AUTH-GAP-02` — Active edges reference formation-deferred node types

- Witness: all 11 UI DS-D1 types are formation-deferred and explicitly not promoted by endpoint use ([meta-types.yml:18-23](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/definitions/meta-types/meta-types.yml:18)); nevertheless DS-D8 actively admits eight UI and six UI/backend signatures ([relationships.md:65-87](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/definitions/relationships/relationships.md:65)).
- Owner/state: already owned by `GAP-SH-UI11-MIGRATE`, batch-1 R2 / MT5 ([ledger.yml:803-813](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/.craft/ledger.yml:803)), plus `FPR-01/FPR-02` profile ownership.
- Priority: **P0 for a full graph; nonblocking for an explicitly backend-only first profile**.
- Smallest safe work unit: model separate `formation_status`, `signature_status`, and `profile_admission`; either exclude UI from the first supported profile or complete the existing UI formation route.
- Dogfood effect: the walker must emit `formation-deferred-endpoint` rather than traverse an active edge into a node type it cannot instantiate.

### `AUTH-GAP-03` — The authoritative Spec source set is split across three homes

- Witness:
  - Authority model names `docs/features/<f>/` as spec primary source ([AUTHORITY-MODEL.md:23-31](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/authority/AUTHORITY-MODEL.md:23)).
  - Local ontology documentation calls `impl/spec/` primary source ([ontology/README.md:17-25](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/ontology/README.md:17)).
  - Local validators walk `impl/spec/features` through the package-relative `spec/features` default ([validate-content.ts:56-71](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/impl/tools/validate-content.ts:56)).
  - The engine CLI still resolves features from the v1 `validation/poker-team/docs/features` tree ([cli.ts:68-82](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/impl/test-derivation-engine/src/cli.ts:68)).
- Owner/state: build-from-owned by `DEC-DSV2-SPEC-HOMING`, reformulate-batch1, `FPR-01`, and the `FPR-04` source manifest.
- Priority: **P0**.
- Smallest safe work unit: add exact source dispositions to `authority-baseline.yml`: `authoritative`, `generated-projection`, `fixture/evidence`, `harvested-v1`, `deferred`, or `retired`; reject missing or legacy resolution paths.
- Dogfood effect: without this, two implementer runs can compile different `Sg` graphs from the same checkout.

### `AUTH-GAP-04` — Ontology direction remains unresolved

- Witness: `FR-FPR-ONTOLOGY-DIRECTION` is active and blocks `FPR-03` promotion ([ledger.yml:894-904](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/.craft/ledger.yml:894)); Lane Z versus Lane A remains an open, nonblocking research decision ([ledger.yml:606-619](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/.craft/ledger.yml:606)).
- Existing safe boundary: contract → authoring only; ontology is a read lens, not reverse authority ([spec-as-ontology findings:54-73](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/research/2026-07-01-spec-as-ontology/findings.md:54)).
- Owner/state: semantic owner + definitions-governance; active block for FPR-03.
- Priority: **P1 after baseline, before promoted B→Spec**.
- Smallest safe work unit: decide direction, supersession, provenance, and contradiction handling in the already-proposed `ontology-spec-direction.md`.
- Dogfood effect: learner/mental-map overlays may be built as generated views now, but they must not write semantic authority back into `Sg`.

### `AUTH-GAP-05` — Definition drift audit is a false-green manual projection

- Witness: the audit declares `pass` while citing `signature_count=31` ([DEFINITION-DRIFT-AUDIT.md:38-57](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/definitions/DEFINITION-DRIFT-AUDIT.md:38)); the machine authority is 30. Its status explicitly says a deterministic scan remains follow-up ([lines 5-12](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/definitions/DEFINITION-DRIFT-AUDIT.md:5)).
- Owner/state: definitions-governance; new witnessed residue inside existing `FPR-01`.
- Priority: **P0 evidence control**.
- Smallest safe work unit: deterministic reference/count/status scan over the selected authority sources, with seeded stale-count and retired-ID fixtures.
- Dogfood effect: becomes the compiler’s preflight guard against using a stale graph.

## Engine implementation gaps already owned

### `ENG-GAP-01` — The imported engine precedes the v2 derivation contract

- Witness: the executor was imported verbatim ([IMPORT-MANIFEST.md:22-32](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/IMPORT-MANIFEST.md:22)); `TEST-PIPELINE.md` remains reformulation-pending, and the import triage labels the executor “wired, not finished” ([findings.md:29-37](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/research/2026-06-29-v1-import-triage/findings.md:29)).
- Owner/state: reformulate-batch1 `R4`, validation governance, then `FPR-04/FPR-07`.
- Priority: **P1 immediately after or contractually alongside the authority/profile work; δ-rule mutation must wait**.
- Smallest safe work unit: reformulate `TEST-PIPELINE` into a v2, profile-scoped public obligation contract without changing private rules.
- Dogfood effect: lets a traversal distinguish an obligation required by Spec from behavior merely inherited from v1.

### `ENG-GAP-02` — No authoritative `Spec → Sg` compiler product exists

- Witness: `spec-graph.json`, compiler IR, schemas, source manifest, and independent comparator are declared but absent ([expected manifest:121-146](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/first-production-release/craft/expected-node-edge-manifest.yml:121)).
- Owner/state: already owned by blocked `FPR-04`.
- Priority: **first engine walking skeleton after FPR-01/02/03**.
- Smallest safe work unit: compile one frozen backend profile into `Sg` with stable IDs and source anchors; reject missing sources, formation-deferred types, mutated edges, and unapproved quotients.
- Dogfood effect: creates the graph the implementer can actually traverse.

### `ENG-GAP-03` — Node patterns are evidence staging, not executable authority

- Witness: backend cards are explicitly non-authoritative; only 5 are evidence-ready, 8 staged-review, and one rejected/superseded ([backend cards:10-16](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/architecture-pattern-enforcement/cards/backend/README.md:10), [25-43](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/architecture-pattern-enforcement/cards/backend/README.md:25)).
- Owner/state: APE / `FPR-05`; definitions-governance owns promotion.
- Priority: **P1 after profile freeze**.
- Smallest safe work unit: admit only the node patterns exercised by the first witness; every unadmitted node returns a typed `pattern-unavailable` gap.
- Dogfood effect: prevents the implementer from laundering legacy examples into canonical code-generation instructions.

### `ENG-GAP-04` — Edge signatures are much broader than executable composition semantics

- Witness: root DS-D8 has 30 active signatures, but the current composability implementation reports nine derived code-call rules and 26 explicit unsupported-active call-semantic signatures ([SWU-R3C-001 result:19-27](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/r3-closeout-plan/task-sessions/2026-07-12-swu-r3c-001/TASK-SESSION-RESULT.md:19), [49-58](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/r3-closeout-plan/task-sessions/2026-07-12-swu-r3c-001/TASK-SESSION-RESULT.md:49)).
- Owner/state: existing bounded R3/APE implementation is complete; breadth residue belongs to APE / `FPR-05`, not reopened R3 authority.
- Priority: **P1 for the implementer’s selected edge subset**.
- Smallest safe work unit: an implementer-facing composition registry carrying `supported`, `unsupported`, evidence source, pattern inputs, and failure code; start with only edges present in the first witness.
- Dogfood effect: an admitted semantic edge without code composition becomes a typed gap rather than an invented implementation.

### `ENG-GAP-05` — The loop cannot close because `I_struct` and cross-graph comparison are absent

- Witness: implementation graph artifacts are `FPR-08` targets ([expected manifest:225-247](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/first-production-release/craft/expected-node-edge-manifest.yml:225)); cross-graph predicates are absent under `FPR-09` ([249-270](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/first-production-release/craft/expected-node-edge-manifest.yml:249)).
- Owner/state: `FPR-08` partial/false-green; `FPR-09` absent.
- Priority: **P2 after the first Sg-driven implementation attempt**.
- Smallest safe work unit: extract AST/symbol/import/call observations for the exact generated witness roots and compare one named directional predicate.
- Dogfood effect: upgrades the loop from “agent wrote code” to “implementation evidence realizes or fails the traversed graph.”

## Language gaps suitable for immediate dogfood discovery

These are already governed deferred candidates, not permission for the project to invent edges:

- `Operation → Value Object` return remains deferred because a return-type property currently appears sufficient.
- `depends-on` lacks typed endpoints and a distinct consequence.
- Event payload/publisher composite lacks a non-collapse witness.

The owner packet requires finite endpoints, positive and negative witnesses, and a changed reject/derive/project/compose/owner/generated-artifact consequence before promotion ([deferred packet:22-40](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/definitions/reviews/2026-07-12-deferred-relationship-candidates.md:22)). These are excellent typed gap-emitter fixtures: the implementer should record the attempted relation and halt or use the explicitly admitted non-edge representation.

## Optional or parallel research

- **Lane Z versus Lane A / agent-cost experiment:** valuable but nonblocking for a Lane-A-style generated `Sg`; the toy proves mapping viability, not agent cost or fusion superiority ([toy verdict:29-40](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/research/spec-ontology-unification/toy/verdict.md:29)).
- **Full category law:** optional for the first bounded walker. Current authority claims only a typed composable graph fragment; general identity, closure, and associativity are not established ([category route:13-23](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/definitions/reviews/2026-07-12-category-law-formalization-route.md:13)). The implementer may traverse explicitly supported local compositions, but must not claim general path algebra.
- **L2 actor-signature attestation:** an active authority-assurance blocker, but separate from local semantic compilation; the L1 integrity receipt already exists and the external identity/key capability remains missing ([ledger.yml:751-765](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/.craft/ledger.yml:751)).
- **Drift `Stream<CheckResult>` engine realization:** already `BLK-DSV2-DRIFT-ENGINE`; required for convergence claims, not for the first static `Spec → Sg` walking skeleton ([ledger.yml:739-749](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/.craft/ledger.yml:739)).

## Recommended first safe work units

1. **Close `FPR-01`:** authority baseline, source dispositions, explicit maturity dimensions, deterministic drift checker, owner receipt, and red mutations.
2. **Freeze a deliberately narrow `FPR-02` backend profile:** use current 13/24/30 baseline but admit only the node and edge subset required by the first witness.
3. **Resolve `FPR-03` direction and Spec source manifest:** contract authority flows into generated ontology/learning views, never reverse.
4. **Build the `FPR-04` walking skeleton:** exact `Spec → Sg`, source anchors, bounded subgraph extraction, and typed gap emission.
5. **Attach minimal `FPR-05` pattern/composition support:** fail closed on every unpromoted node pattern or unsupported edge composition; then implement one witness and proceed to minimal `I_struct`.

This sequence still makes the engine the central implementation priority, while ensuring the project discovers DomainSpec gaps instead of encoding today’s contradictions as permanent engine behavior.

## Agent 3 — Turing, Alan

# Turing, Alan — DomainSpec v2 adversarial traversal

## Attack method

I traced claims in this order:

1. Canonical prose and machine authority.
2. Manifests and generated projections.
3. Package-script composition.
4. Validator control flow and negative fixtures.
5. Live command results.
6. Gap/Craft ownership to distinguish new defects from already-declared blockers.

No files were edited.

## Evidence boundary

- Live worktree on 2026-07-14, including pre-existing modified/untracked FPR and Craft artifacts.
- Primary scope: `projects/domainspec-v2/{README.md,IMPORT-MANIFEST.md,definitions/,authority/,impl/,development/*GAP*,development/*PROOF*,development/*RECEIPT*,development/first-production-release/}`.
- Executed read-only validation commands under `projects/domainspec-v2/impl`.
- Current worktree was already dirty: `.craft/ledger.yml` and `impl/package.json` modified; FPR roadmap/research/craft/visibility artifacts untracked. The `package.json` diff changes formatting and `packageManager`, not validation-script composition.

## Contradiction table

| ID | Claim under attack | Live adversarial evidence | Existing owner | Classification / priority |
|---|---|---|---|---|
| C1 | Saga-removal closeout remains a zero-violation, full-package proof. | `development/saga-removal/runs/SWU-SGRM-008/TASK-SESSION-RESULT.md:14-17,55-63` claims complete synchronization, full `validate` PASS, and zero reference violations. Today `npm run audit:retired-orchestration` exits 1: 210 matching files, 1,765 matches, 2 violations—one unclassified FPR research file and one frozen-manifest count drift. `npm run validate` consequently ends with 67 tool tests passing and 2 failing. This does not prove the historical run lied; it proves the receipt has expired under live drift. | Saga-removal SGRM-006/007 and validation-governance; the current FPR research already records the failure at `research.md:268`. | Reopened completed-proof regression. **P0 for release; P1 repository-wide.** |
| C2 | The canonical meta-type vocabulary is stable. | Canonical `definitions/DEFINITIONS.md:231-240,248-260,281-295` still asserts 25 fixed types and backend IDs 1–14. Current machine view says 24 candidates, 13 backend members, IDs `1..9,11..14` (`meta-types.yml:9-23`); `impl/spec/TAXONOMY.md:3-39` agrees with 24/13. The stale prose also contradicts its own linked evidence. | Already declared as **FPR-01 AUTHORITY-BASELINE**, owned by definitions, validation, and layering owners (`expected-node-edge-manifest.yml:49-66`). | Confirmed declared authority conflict; do not mint a duplicate gap. **P0.** |
| C3 | The sample makes validation “non-vacuously green.” | `impl/spec/features/sample/SPEC.md:3-10` makes that exact claim. Live `validate:content -- --file .../sample/SPEC.md` returns PASS with **0 concepts and 0 edges**. Live `engine:lint` over the same sample returns CLEAN with **0 noncanonical tables and 0 formal cells**. Validator control flow silently accepts absent registries, missing columns, and unknown/unformalized types (`validate-content.ts:99-119`). There is no unknown-meta-type rejection test in `validate-content.test.ts`; “unknown” tests concern attribute values or rule kinds. | Already bounded by FPR-02 supported-profile negatives and FPR-04 authoritative projection (`expected-node-edge-manifest.yml:68-93,121-146`). | Confirmed false-green / missing negative control. **P0 for release; P1 validator contract.** |
| C4 | “13 schemas and 30 signatures” means the current real corpus exercises that vocabulary. | Live parsing of the three feature `SPEC.md` files finds 20 concepts using **11/13** backend types; Mapping and State Machine are absent from positive real packs. Fourteen edges use only **9/30** active verbs. The 21 absent positive verbs are `performs`, `triggers-cross`, `transitions`, `maps`, `emits`, `owns`, `belongs-to`, and all fourteen active UI/cross-layer verbs. Fixtures do exercise every schema shape and selected invalid edges, but `canonicalSignatures=30` means the authority was loaded, not that 30 signatures were positively traversed. This contradicts FPR research wording at `research.md:60`; the R3C receipt itself is narrower and honest at `TASK-SESSION-RESULT.md:14-17,50-66`. | FPR-02/FPR-04; R3C correctly closed only the bounded “second corpus adds breadth” gap, not exhaustive signature exercise. | Denominator/wording defect plus bounded coverage gap. **P0 if used for completeness; P1 otherwise.** |
| C5 | `npm run validate` is an aggregate implementation gate. | `impl/package.json:17-32` includes docs, relationships, content, tool tests, and sample engine lint. It omits `engine:test`, `tags:test`, `instances:validate`, and `typecheck`. Those independent commands currently pass: engine 97/97, tags 15/15, generated instances 13/13, typecheck 0. A future failure in any of them can therefore coexist with aggregate `validate` success. The retired-reference audit is currently included indirectly through `tools:test`, so it is not omitted. | Validation-governance; release integration belongs across FPR-04/FPR-07/FPR-08. | Aggregate-boundary ambiguity, not proof the omitted suites are presently red. **P1.** |
| C6 | The import manifest supplies an auditable, navigable completed migration surface. | `IMPORT-MANIFEST.md:22` says “build-proof: see RESULT below,” but the file ends at line 97 with no RESULT section. Line 93 says `impl/spec/DEFINITIONS.md` was built by R7 and is distinct from root governance definitions; that file is absent, while root `definitions/DEFINITIONS.md` now owns the live DomainSpec vocabulary. An implementer following the manifest reaches a nonexistent authority path. | Import-migration owner and definitions-governance/R7; FPR-01 covers stale projections but not this exact broken destination claim. | New stale-manifest/path gap. **P1.** |
| C7 | Engine status documentation describes current implementation maturity. | `impl/test-derivation-engine/README.md:23-25` says parser and δ rules are typed stubs and names them as future units. Current `rules/index.ts:631-663` derives fifteen obligation families, and `engine:test` passes 97 tests. `rules/index.ts:2-4` also says `TEST-PIPELINE.md` does not exist, while `impl/spec/TEST-PIPELINE.md` exists. | Test-derivation engine owner; import manifest already marks TEST-PIPELINE reformulation pending. | Documentation drift, not missing implementation. **P2.** |
| C8 | Authority direction can be inferred during implementation. | Active `definitions/DEFINITIONS.md:183-216` says authority flows **contract → authoring, never reverse**. The FPR chain requires governed business meaning to precede typed specification. Current Craft explicitly records `FR-FPR-ONTOLOGY-DIRECTION` and blocks FPR-03 until an owner resolves direction. This is a deliberate unresolved gate, not permission to choose whichever direction helps an implementation. | Existing `FR-FPR-ONTOLOGY-DIRECTION`; semantic owner plus definitions-governance. | Confirmed declared blocker; no duplicate. **P0.** |

## Smallest reproducible witness or bounded unavailable witness

```bash
cd projects/domainspec-v2/impl

npm run audit:retired-orchestration
# exit 1
# Result: FAIL; violations: 2

npm run validate:content -- --file spec/features/sample/SPEC.md
# exit 0
# PASS (0 concepts, 0 edges, 1 file, schemas=13)

npm run engine:lint
# exit 0
# CLEAN: 0 noncanonical tables, 0 unparseable Formal cells

npm run engine:test
# exit 0; 97/97

npm run tags:test
# exit 0; 15/15

npm run instances:validate
# exit 0; 13/13

npm run typecheck
# exit 0
```

A persistent unknown-type fixture was intentionally not created under the read-only constraint. The bounded witness is nevertheless executable from existing files: the sample yields a successful zero-check verdict, while `validate-content.ts:116-119` unconditionally skips any registry type lacking a schema.

The real-pack coverage census is:

- Node types: 11/13 positively exercised; Mapping and State Machine absent.
- Active relationship verbs: 9/30 positively exercised.
- Edge instances: 14 across two substantive packs; the third pack is the zero-content sample.

## Existing owner if any

- **FPR-01:** count, status, stale projection, composability, and authority-direction reconciliation.
- **FPR-02:** supported-profile denominator and explicit unknown-type/absent-root/empty-profile negatives.
- **FPR-04:** total authoritative Spec projection and fail-closed type/relation/document coverage.
- **SGRM-006/007:** refresh the classified retired-orchestration manifest/allowlist and restore the guard.
- **Definitions-governance/R7:** remove or repair the nonexistent `impl/spec/DEFINITIONS.md` destination claim.
- **Engine owner:** synchronize README and stale `TEST-PIPELINE.md` source comment.

## Gap classification and priority

- **P0 — keep first-release execution blocked:** C2, C3, C4 when used as completeness evidence, and C8.
- **P0 release / P1 repository:** C1, because current validation is red and the closeout proof no longer describes the worktree.
- **P1 — implementation traversal correctness:** C5 and C6.
- **P2 — misleading but non-blocking documentation:** C7.

Only C6 appears to require a distinct new gap. C1 is a reopened proof obligation. C2–C4 and C8 already have live FPR owners and should be attached to those nodes rather than duplicated.

## Implementer-traversal consequence

An implementer cannot safely traverse DomainSpec v2 by following a single prose entry point:

1. `definitions/DEFINITIONS.md` gives stale counts.
2. `IMPORT-MANIFEST.md` points to an absent definitions authority.
3. `npm run validate` is both currently red and structurally narrower than the complete command set.
4. A PASS with `schemas=13` or `canonicalSignatures=30` does not prove those denominators were exercised.
5. Empty or unsupported specification content can currently disappear behind a green verdict.
6. Authority direction is explicitly owner-gated.

The safe continuation order is therefore: restore the live audit guard, execute FPR-01 authority reconciliation, freeze FPR-02’s supported profile and fail-closed negatives, then implement FPR-04’s total projection. Any implementation begun before those gates risks selecting stale vocabulary, silently omitting concepts, and generating internally consistent evidence over the wrong denominator.
