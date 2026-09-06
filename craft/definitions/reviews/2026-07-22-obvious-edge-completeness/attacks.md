# DomainSpec v2 Obvious-Edge Completeness — Attack and Verification Returns

Dispatch: `2026-07-22-dsv2-obvious-edge-completeness-review`

This is the verbatim collected-return surface for the three attacker lanes and
two verifier lanes. It is review evidence, not relationship authority.

## A1 — Spivak, David — Formal fidelity/governance

### Verdict

One obvious missing first-class edge exists: a same-feature `Operation → Entity` creation/mutation edge. The live graph currently launders that relation through cross-feature-only `produces-for`.

A second, well-shaped `Action → Binding` edge is semantically non-collapsing, but its endpoint meta-types remain candidate-only, so it must stay deferred rather than enter active DS-D8 now.

### Findings

#### 1. `creates`: same-feature Operation-to-Entity creation is absent

- **Severity:** CRITICAL
- **Disposition:** ACTIVE-GAP
- **Candidate:** `Operation --[creates]--> Entity`
- **Exact evidence:**
  - Canonical `produces-for` is cross-feature-only: `definitions/relationships/relationships.yml:52-65`, especially `"feature_scope": ["cross-feature"]` at line 57 and “owned by another feature” at line 60.
  - Its human companion likewise says “foreign entity”: `definitions/relationships/relationships.md:50`.
  - The current source graph nevertheless declares `CreatePlayer --[produces-for]--> Player` while both nodes belong to `ui-profile-create-player`: `impl/spec/features/ui-profile-create-player/nodes/create-player-operation.json:3-10`.
  - The Operation intent is explicitly creation plus persistence of a new identity: same file, lines 6-7.
  - Operation’s formal card says it “transitions entities”: `definitions/meta-types/meta-types.md:418-424`.
- **Nearest existing edge/non-edge:** `produces-for`; otherwise Operation’s prose/body property `state_change=yes`.
- **Why it does not collapse:** `produces-for` names a foreign-feature projection/write seam. Same-feature identity creation has a different ownership path and implementation consequence. Merely widening `produces-for` to same-feature would erase the feature-boundary distinction that D3 explicitly includes among admissibility axes (`DEFINITIONS.md:109-117`) and contradict its current semantics.
- **Changed D20-D25 property:**
  - **D20 reject/allow:** the current same-feature fixture should be rejected under `produces-for`; `creates` would admit the intended pairing.
  - **D23 composition path:** local aggregate creation/persistence differs from writing or projecting foreign-owned state.
  - **D24 owner route:** lifecycle authority remains with the target’s same-feature owner rather than crossing a feature ownership boundary.
- **Fix:** Add an owner-reviewed `creates` signature with exact endpoints `Operation → Entity`, `feature_scope: ["same-feature"]`, creation-specific semantics, and positive/negative fixtures. Replace the Create Player graph’s `produces-for` edge only after admission. Do not broaden `produces-for`.

#### 2. `invokes`: Action has no admitted source edge

- **Severity:** MAJOR
- **Disposition:** DEFER
- **Candidate:** `Action --[invokes]--> Binding`
- **Exact evidence:**
  - The Action card explicitly says “an Action-source relationship is still a separate unresolved request”: `definitions/meta-types/meta-types.md:227-234`.
  - The source Action declares `target_kind: "Binding"` but has no connections: `impl/spec/features/ui-profile-create-player/nodes/create-player-action.json:7-15`.
  - Residue records the omission: `impl/spec/features/ui-profile-create-player/residue.json:8`.
  - The authority packet supplies finite semantics, positive witness, non-examples, and endpoint validation obligations: `development/ui-profile-implementation/authority-packet/packet.json:114-118`.
  - The human packet confirms no edge was admitted: `development/ui-profile-implementation/authority-packet/PACKET.md:66-77`.
- **Nearest existing edge/non-edge:** `Form --[submits]--> Action`, followed by `Binding --[mutates]--> Operation`; otherwise Action’s `target_kind` attribute.
- **Why it does not collapse:** removing `Action → Binding` breaks the typed path from user intent to durable endpoint interaction. `submits` ends at Action; `mutates` begins at Binding. An attribute naming `Binding` does not validate target identity or generate graph traversal.
- **Changed D20-D25 property:**
  - **D20 reject/allow:** exact `Action → Binding` accepted; reversed or `Action → Hook` rejected.
  - **D23 composition path:** `Form → Action → Binding → Operation`.
  - **D25 generated artifact:** generated graph/traversal gains the currently absent connection.
- **Why deferred:** Action and Binding are explicitly “candidate; not active or promotion-ready”: `definitions/meta-types/meta-types.md:220-223` and `259-264`. DS-D8 admission before DS-D1 formation would invert authority.
- **Fix:** After DS-D1 owner admission of both endpoints, promote narrowly as `invokes: Action → Binding`. Reject a target union such as `Binding|Hook|Page`: that would be D3 target-type overload, not source widening.

### Ownership and overload attack results

- `produces-for` is being used outside its declared cross-feature ownership scope. Same endpoint types do not make same-feature creation and foreign-feature projection the same relation.
- `invokes` must remain finite at `Binding`; Action’s prose-level “target kind” must not become a polymorphic `Binding|Hook|Page` edge.
- `Hook → Binding` remains a justified non-edge: the packet retains `consumes` plus `fetches`/`mutates` (`PACKET.md:71-72`; `packet.json:120`).
- `Component → Form` has no demonstrated D20-D25 consequence and should not overload `composes` merely because Form is renderable (`packet.json:121-128`).
- The three existing deferred candidates remain correctly deferred: their review packet finds no changed property (`definitions/reviews/2026-07-12-deferred-relationship-candidates.md:24-40`).

### Attack coverage

Attacked all 30 active signatures for endpoint and scope holes; D3/D18/D20-D25/DS-D8; same-feature versus cross-feature ownership; Operation creation; Action-source closure; target unions; UI candidate maturity; deferred candidates; current Create Player source/generated graph; relationship-card triage and residue. No other obvious first-class edge survived the non-collapse test.

## A2 — Shannon, Claude — Mechanics/correctness

### Coverage and commands

- Live catalogue: 30 active signatures; current UI graph: 17 nodes, 20 edges, 19 distinct signatures (63.3% signature coverage).
- Every authored UI edge is endpoint-admitted by the development profile; 11 catalogue signatures are currently unwitnessed: `applies`, `belongs-to`, `calculates`, `composes`, `contains`, `emits`, `orchestrates`, `owns`, `reflects`, `shapes`, `triggers-cross`.
- Commands passed:
  - `npm run validate:rels` → `5 specs checked, edgesChecked=34, canonicalSignatures=30`
  - `npm run tools:test` → `147/147` pass.
  - Static graph/catalog comparison → exactly one catalogue-scope mismatch, below.

### Findings

#### F1 — same-feature creation is represented as a cross-feature write

- Severity: **MAJOR**
- Classification: **ACTIVE-GAP** — catalog semantics plus validator/tooling lag.
- Evidence: `relationships.yml:52-65` defines `produces-for` as a cross-feature operation write/projection and allows only `feature_scope: ["cross-feature"]`; the current one-feature graph authors `CreatePlayer --produces-for--> Player` at `create-player-operation.json:10`, projected at `graph.json:320-324`.
- Positive witness: `Operation -> Entity` is type-admitted and compiled into the generated graph.
- Negative witness: the source and target have the same `feature_id`; the compiler has only a blanket rejection of actual cross-feature edges at `compiler.ts:434-439`, and no `feature_scope` enforcement. Thus the stated cross-feature signature is used for same-feature creation and still passes all gates.
- Proposed fix/check: first make the semantic decision: either widen `produces-for` to include same-feature writes/creation (and revise its name/semantics), or add a distinct operation→entity creation/mutation signature. Then enforce `feature_scope` against source/target feature IDs in the minted compiler and add positive/negative same-/cross-feature controls. Markdown-only validation cannot establish this property without feature identity.

#### F2 — Action-to-Binding control flow is intentionally unrepresentable

- Severity: **MAJOR**
- Classification: **DEFER** — missing catalog semantics, not an unrecognized validator failure.
- Evidence: `Action` is a UI candidate node type at `meta-types.yml:24-27`; the active catalogue gives it an incoming `Form --submits--> Action` signature at `relationships.yml:340-353`, but no Action-source signature. The Action declares `target_kind: Binding` in `create-player-action.json:8-14`, while the generated residue records `Action -> Binding` as omitted because no active DS-D8 signature exists at `residue.json:24-30`.
- Positive witness: `Form --submits--> Action` is correctly represented and endpoint-validated at `SPEC.md:53`.
- Negative witness: no graph edge connects Action to its declared Binding target; the generated Action projection has zero outgoing edges at `create-player-action.json:19-27`.
- Proposed fix/check: keep this deferred until the DS-D8 owner chooses whether Action→Binding is a real typed control-flow relationship, a body reference only, or an Action normalization to another type. If promoted, add a signature, profile admission, source and target endpoint mutants, and a traceability invariant tying `Action.body.target_kind` to the emitted edge.

#### F3 — endpoint validation is present; the older “no machine signatures” claim is stale

- Severity: **INFO**
- Classification: **REJECT** as a current gap.
- Evidence: the relationship validator resolves source/target concept types and rejects nonmatching signatures at `relationship-signatures.ts:474-499`; six negative endpoint controls are asserted at `validate-relationships.test.ts:29-42`. The compiler independently rejects endpoint-kind mismatches at `compiler.ts:441-455`.
- Positive witness: all 20 current graph edges pass endpoint admission; the suite has explicit success coverage.
- Negative witness: reversed `enforces`, `Operation --emits--> Event`, `Saga --orchestrates--> Operation`, and UI endpoint mutants reject.
- Proposed check: retain both validator paths, but add scope assertions from F1; endpoint-kind validation alone is insufficient for scope semantics.

#### F4 — the remaining UI endpoint pressures are correctly preserved as deferred residue

- Severity: **LOW**
- Classification: **DEFER**, not evidence of endpoint misuse.
- Evidence: `Adapter --shapes--> View Model`, `State Indicator --reflects--> State Machine`, `Hook -> Binding`, and `Component -> Form` are all recorded as owner-decision-required residue at `residue.json:7-46`. The test asserts their absence from authored edges and their deferred status at `ui-profile-graph-source.test.ts:139-155`.
- Positive witness: Adapter is normalized into active Mapping rather than coerced into an unrecognized node; State Indicator is split into projection/role.
- Negative witness: neither `shapes` nor `reflects` is silently authored under an altered endpoint; the named mutants reject at `ui-profile-graph-source.test.ts:164-169`.
- Proposed check: require each future residue closure to specify whether it changes DS-D8, profile-only representation, or remains a body-level reference.

### Inventory-claim calibration

- The older R3 inventory assertion that the live path lacked machine-enforceable endpoint signatures is now superseded by the validator/compiler evidence above.
- The EVF assertion of **30** current signatures is verified.
- “Four of thirteen kinds admitted” remains true only for the default experimental supported profile (`supported-profiles.yml:20-50`); the explicit UI development profile admits 17 kinds (`minted-project-profile.json:27-45`). It must not be generalized to all live development tooling.

## A3 — van Lamsweerde, Axel — Operability/ownership

**Verdict:** one active representability gap, resolved by widening an existing signature rather than minting a verb. Return/result and dependency remain correctly deferred; Action-source remains route-open with no admissible edge. Creation, deletion, and update do not justify separate lifecycle verbs.

### Findings

| ID | Evidence and attack | Overlap / collapse pressure | D20–D25 consequence | Severity | Disposition | Proposed fix |
|---|---|---|---|---|---|---|
| OOA-01 | The active `produces-for` signature is exclusively cross-feature and means writing/projecting into “an entity owned by another feature” (`relationships.yml:52-65`). Yet the current financial-settlement feature says it owns settlement generation and creation of ledger transactions (`financial-settlement/SPEC.md:12-15`), then authors `GenerateSettlement --[produces-for]--> SettlementTransaction` inside that same feature (`:29-37`). Its operation postconditions explicitly create those entities (`operations.md:70-77`). **Same-feature Operation→Entity create/write is therefore not representable honestly by active DS-D8; the corpus currently borrows a cross-feature edge.** | `creates`, `writes`, and `updates` all collapse into one Operation→Entity mutation/write path. Separate verbs would change no typed path; lifecycle kind belongs in operation postconditions. | **D20:** feature-scope allow/reject should differ. **D23:** widening permits the missing same-feature typed path without changing target semantics. **D21:** existing create/update postconditions remain the derived obligations. | High | **ACTIVE-GAP** | Widen `produces-for.feature_scope` to `same-feature` + `cross-feature` and neutralize semantics to “writes or projects data into an Entity”; preserve local/foreign ownership as scope metadata. Add positive same-feature and cross-feature fixtures plus wrong-endpoint negatives. Do **not** add `creates` or `updates`. |
| OOA-02 | Update is already expressed as an operation postcondition: “Updates player makeup…” (`operations.md:74-76`); the active graph supplies Operation reads through `queries` (`relationships.yml:212-225`) and cross-feature writes through `produces-for` (`:52-65`). | `updates` collapses into the widened write edge plus a field-level postcondition. A new verb would duplicate endpoint/path behavior. | No distinct **D20**, **D23**, or **D25** beyond `produces-for`; the field mutation remains a **D21** postcondition obligation. | Low | **NO-GAP** conditional on OOA-01 | Keep update kind, predicate, and changed fields in operation postconditions; use widened `produces-for` only for graph-level write coupling. |
| OOA-03 | The only deletion-like corpus evidence located is “safe to soft-delete duplicate” in observability narrative (`observability.md:154`); no current feature graph requires a deletion-specific typed path. `owns` already carries lifecycle/custody responsibility (`relationships.yml:244-257`). | Hard/soft delete is operation mode/postcondition; lifecycle authority is `owns`. No evidence that `deletes` changes endpoint admissibility or composition. | No witnessed **D20–D25** consequence. | Low | **NO-GAP** | If deletion becomes a feature guarantee, encode it as an Operation postcondition and use ownership/write edges already present; reopen DS-D8 only with a red/green non-collapse witness. |
| OOA-04 | Return/result behavior is explicit as an operation postcondition—“Returns one SettlementResult” (`operations.md:70-75`)—and as `formal_return_type` attributes (`financial-settlement/SPEC.md:88-95`). Authority explicitly defers `operation-returns-value-object` because it is representable as a signature property (`relationships.yml:516-519`); the review requires proof that the edge changes an observable obligation beyond return typing (`deferred-relationship-candidates.md:27`). | Full collapse into operation return type/postcondition. “Result” is a value role, not presently a graph coupling. | No independent **D20–D25** consequence; especially no new **D21** obligation or **D25** artifact. | Low | **DEFER** | Keep return/result in the operation signature. Reject promotion unless paired fixtures prove an edge-specific validator, composition, or generated-output delta. |
| OOA-05 | `depends-on` is deferred because no witness separates it from references or field-level dependency (`relationships.yml:511-515`). The review packet requires finite endpoints and a dependency-presence, cycle, build-order, or generated-projection obligation (`deferred-relationship-candidates.md:24-26`). Existing cards likewise record “No distinct validation witness” (`cards/relationships/README.md:66`). | Generic reference/dependency collapses into typed fields, scope metadata, explicit feature dependency tables, or more specific existing edges. | No current **D20–D25** consequence. | Low | **DEFER** | Preserve deferred state. Reopen only for typed endpoints plus a cycle/build-order validator or generated dependency artifact that existing edges/reference fields cannot produce. |
| OOA-06 | The owner decision keeps Action-source “route-open” but has `authority_effect: none`, demands exact verb/target, positive and negative witnesses, finite endpoints, and a changed D20–D25 consequence; it admits no signatures (`decision.json:35-53`). Current evidence already represents Form→Action via `submits` (`ui-profile-create-player/SPEC.md:53`); Action’s target/effect/outcomes remain attributes (`:170-179`), while Binding→Operation is `mutates` (`:57-58`). | A proposed Action→Binding/Operation edge currently collapses into `target_kind`, effect/outcome attributes, Form→Action `submits`, and Binding→Operation `mutates`. Handler-shaped narrative is insufficient. | No demonstrated **D20–D25** consequence; the owner packet correctly demands one. | Medium | **DEFER** | Keep route open but unadmitted. Require an exact Action-source signature and fixtures showing a composition/validation/generation delta not obtainable from `submits` + `mutates` + attributes. Otherwise reject at owner gate. |

### What I attacked

I tested entity creation, update, deletion, operation return/result, generic reference/dependency, and Action as a relationship source across current feature graphs, operation postconditions, architecture-card triage, DS-D8 authority, and explicit deferred/route-open packets. I also challenged narrative verbs against the non-collapse standard: DS-D8 itself requires new relationships to pass the D18 test and leaves returns/dependency deferred (`DEFINITIONS.md:1140-1147`). The only present failure is not a missing verb but a missing **same-feature scope** on the existing Operation→Entity write relationship.

## V1 — Sattler, Christian — Counterexample verifier

VERDICT: MAJOR ACTIVE-GAP, with one correction: UIP-02 proves unlabeled Action→Binding pressure, not specifically `invokes`.

Surviving findings:

- REL-01: `produces-for` is cross-feature-only and foreign-owned in authority, yet both feature graphs use it within one feature.
- REL-02: scope enforcement is absent from both validators. The minted compiler actually imposes the opposite coarse rule: it rejects every cross-feature endpoint while admitting same-feature endpoints based on profile/type.
- REL-03: correctly rejected; endpoint validation exists.
- UIP-01 / FIN-01: survive as invalid same-feature uses with positive creation semantics.
- Scope mutants, a real cross-feature projection witness, and D20–D25 comparison are required.
- Severity MAJOR is supported; CRITICAL is not.

Objections:

- UIP-02 must say “Action→Binding relationship pressure DEFER.” `target_kind: Binding` is metadata, and residue leaves the edge unlabeled. `invokes` is unproven.
- Green validation demonstrates validator lag, not conformance.
- Current evidence cannot select distinct `creates` versus widening `produces-for`; DS-D8/D18 comparison remains necessary.
- Broad verdicts for `instantiates`, `updates`, `deletes`, and `returns` were not independently established from this lane’s bounded corpus.

Exact evidence:

- Authority: `definitions/relationships/relationships.yml:52-65`.
- UI invalid use: `ui-profile-create-player/SPEC.md:18-20,40-43`; machine same-feature witness in `feature.json:2-22` and `nodes/create-player-operation.json:3-10`.
- Financial invalid use: `financial-settlement/SPEC.md:12-15,19-25,31-42,72-78`.
- Same-feature non-creation comparator: `GenerateSettlement --queries--> SettlementTransaction`, financial SPEC line 36.
- Endpoint-only validator: `relationship-signatures.ts:402-499`.
- Compiler scope inversion: `minted-project/compiler.ts:430-455`.
- Action→Binding pressure: action node lines 5-15; generated node lines 9-20; residue lines 24-29.
- No exercised cross-feature `produces-for` instance was found; authority line 61 is only an example.

Checks:

- `npm run validate:rels`: PASS, 5 specs / 34 edges / 30 signatures.
- `npm run tools:test`: PASS, 147/147.

## V2 — Popper, Karl — Vacuity/definitional verifier

VERDICT: **MAJOR ACTIVE-GAP confirmed**, narrowly: `produces-for` asserts cross-feature/foreign-entity semantics but accepts and generates same-feature uses. Do not yet promote `creates` or `instantiates`; neither has a named changed D20–D25 consequence.

Objections by synthesis ID:

- **REL-01 — survives.** `produces-for` is explicitly cross-feature and foreign-owned, yet both examples are same-feature. The UI machine source puts both nodes in `ui-profile-create-player`; Financial Settlement has only a single local feature pack. This is a semantic-authority mismatch, not merely a test gap.
- **REL-02 — survives, strengthened.** Markdown validation checks only label and endpoint types; it never reads `feature_scope`. The compiler also does not enforce signature scope: it instead rejects every cross-feature edge wholesale. Thus there is neither scope-aware acceptance nor scope-aware rejection.
- **REL-03 — reject.** Endpoint validation exists and has named negative controls. The stale “endpoint validation absent” claim is false.
- **UIP-01 / FIN-01 — survive as invalid-under-current-semantics uses**, not proof that a new `creates` relation is warranted. Each currently validates because only endpoint types are checked.
- **UIP-02 — DEFER survives.** `Action.target_kind: Binding` is a required scalar attribute, not an authored graph edge. The generated graph retains the attribute but no edge; residue explicitly routes `Action -> Binding` to DS-D8. “invokes” has no D20–D25 delta yet.
- **Instantiates NO-GAP — objection.** No current `instantiates` authority, authored use, or named residue was found in this bounded evidence. “No gap” is only “no observed pressure,” not evidence that `creates` collapses into `instantiates`.
- **Updates/deletes NO-GAP — same objection.** Not established by this audit’s authority/compiler/two-feature surface; retain only as “no witnessed pressure.”
- **returns / depends-on — DEFER survives.** Current authority itself says return values remain operation properties and `depends-on` lacks distinct validation behavior.
- **Hook→Binding — DEFER survives.** It is explicitly omitted residue, with no changed consequence.
- **Component→Form — REJECT survives.** Current pressure has no non-collapse witness; it would otherwise be an implementation/navigation convenience.

Required non-vacuous proof before any new creation relation:

| D18 property | Required named delta |
|---|---|
| D20 | Scope-aware validator rejects current same-feature `produces-for`, while a proposed `creates` (or revised relation) accepts the intended case. |
| D21 | A creation-specific obligation/fixture changes; `state_change: yes` alone does not qualify. |
| D22 | A governed projection distinguishes creation from cross-feature projection, not merely a different display label. |
| D23 | A typed composition path differs from `Operation → Entity` cross-feature write/projection. |
| D24 | A distinct owner/gate route changes; the same DS-D8 owner is insufficient. |
| D25 | Deterministic generated graph/fixture deltas with provenance are produced from the distinction. |

Exact evidence:

- `produces-for` is `Operation → Entity`, `feature_scope: ["cross-feature"]`, and means writing/projecting into an entity owned by another feature: `relationships.yml:52-65`.
- Same-feature UI use is authored in `ui-profile-create-player/SPEC.md:42`, with both source and target IDs under `ui-profile-create-player` in `create-player-operation.json:3`.
- Same-feature Financial Settlement use is `financial-settlement/SPEC.md:35`.
- Relationship validation matches only label/source type/target type: `relationship-signatures.ts:474`.
- The compiler rejects all cross-feature edges independently of signature scope: `compiler.ts:434`; its test states that boundary expressly: `minted-project-compiler.test.ts:233`.
- `Action → Binding` is explicit omitted residue: `residue.json:8`; `target_kind` is only a nonempty schema attribute: `action.schema.yml:17`.
- D20–D25 require an actual changed allow/reject, derivation, projection, composition, owner route, or generated artifact: `DEFINITIONS.md:774`.

Dropped claims: that endpoint validation is absent; that current evidence selects `creates` over a scope-corrected/renamed `produces-for`; that `instantiates`, updates, or deletes have positively established no-gap status.

Observed live checks: `validate:rels` passed (5 specs, 34 edges, 30 signatures); `tools:test` passed (147/147).
