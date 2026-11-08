# Critique of the runtime integration design

These findings distinguish observed code behavior from proposed repairs. They do not claim that a counterexample was executed. References are relative to this repository and bind the exact files recorded in `run.json`.

## D01 — Component anatomy is ahead of demonstrated need

**Category:** overbuilding / abstraction mismatch. **Disposition:** revise.

[DESIGN §3–4](../0006-runtime-integration-design/DESIGN.md) prescribes a dozen Python modules and a full preparation-kernel rewrite. Exact-byte ownership is justified: the existing [JavaScript context adapter](../../../implementation/define-cli/v1/src/context-adapter.mjs) parses and reserializes host JSON. That does not establish that every pure transformation needs replacement or a separate component interface.

The existing [session runtime](../../../implementation/define-cli/v1/src/session-runtime.mjs) contains disposition/readiness mechanics; the [Python bridge](../../../implementation/define-cli/v1/lab_bridge.py) and [no-replace publisher](../../../implementation/define-cli/v1/publish_directory.py) are useful reuse candidates. Their legacy contracts are not automatically adequate for the revised Pack.

**Repair:** specify three responsibilities and their observable behavior; choose module layout after the first complete path. Compare reuse versus replacement for compatible pure transformations. Preserve [C06](../0005-amended-integration-plan/DESIGN.md): Python owns new authority-record encoding/digests and exact bytes to be signed. This grants Define no signing role; real authentication, owner signatures and verification remain host-owned. Reuse of helper semantics must account for entrypoint side effects and source pins.

## D02 — The adapter can be smaller and more concrete

**Category:** unnecessary generality / boundary fit. **Disposition:** revise.

The [Host Port and runtime profile](../0006-runtime-integration-design/CONTRACTS.md) describe a broad configurable integration surface for one currently selected host family. The pure preparation semantics do not depend on API17 directory names, operator revision labels or transport selection.

**Repair:** start with one pinned concrete adapter mapping actual operations to capture, currentness and later handoff. Keep exact source/schema/dependency/credential-locator bindings. Missing operations remain explicit gaps. Preserve a normalized input boundary; defer a multi-backend framework until a second actual integration demonstrates a need.

## D03 — Fresh candidate bytes cannot simply enter the existing review Vault

**Category:** coherence gap / external blocker. **Disposition:** revise and route.

The [review flow](../0006-runtime-integration-design/FLOWS.md) assumes local material can enter host custody. [workspace.py:34–53](../../../product/lab/release-candidates/v1/interface/api-integration-v17/workspace.py) checks an immutable, policy-bound manifest and exact flat input set; `material()` at lines 97–102 rejects unselected inputs except under specific package policies. [candidate.py:38–40,61–68](../../../product/lab/release-candidates/v1/interface/api-integration-v17/candidate.py) additionally requires selected target metadata and an already supplied exact decision core. `change.prepare` independently reconstructs and compares that core; it does not create a missing initial core input.

**Failure:** a new Definition body exists locally, but its metadata/core/body refs cannot resolve in the selected workspace. Copying old generated proposal objects into a new workspace also fails: object refs include workspace identity ([workspace.py:103–109](../../../product/lab/release-candidates/v1/interface/api-integration-v17/workspace.py)).

**Repair:** specify the [staged handoff](DISTILLED-DESIGN.md#staged-review-handoff). Precompute proposed cores using exact selected host mechanics, then independently provision a new immutable workspace and regenerate workspace-bound proposal/review evidence. Review routing is lazily selected at the call, but it is still a frozen Vault input ([service.py:138–147](../../../product/lab/release-candidates/v1/interface/api-integration-v17/service.py)).

**Still open:** the supported nonfixture provisioning and applicable review-policy route. [review_preparation.py:31–34](../../../product/lab/release-candidates/v1/interface/api-integration-v17/review_preparation.py) binds a historical one-shot authorization and bounded permission; this is not new Define authority. The [fixture sequence](../../../product/lab/release-candidates/v1/interface/api-integration-v17/review_fixture.py) demonstrates ordering, not transferable credentials or permission. Never patch an active Vault or weaken its policy to bypass this gap.

## D04 — Byte integrity does not establish source-epoch membership

**Category:** underbuilding / provenance confusion. **Disposition:** revise.

The original capture rules bind exact bytes but do not fully specify the join between a host cut and locally read source files. A genuine E1 context and a genuine E2 local body are individually intact; that does not make the body an admitted E1 member.

**Repair:** classify each captured input as host-selected member, local candidate supplement or external evidence. A local copy claiming membership must match the host's exact member binding. A supplement retains its own attribution, standing and applicability; it does not inherit the host cut. A conflicting claimed member blocks or triggers recapture.

## D05 — Frozen readiness and later-use readiness need different records

**Category:** lifecycle coherence. **Disposition:** revise.

The [contracts](../0006-runtime-integration-design/CONTRACTS.md) include readiness in an immutable Pack and also require currentness checks on later use. Without an explicit distinction, a recheck either rewrites the Pack or becomes an unbound Boolean.

The reviewed [Pack meaning](../../development/m1-preparation-preview/v1/reviews/consolidated-model/v2/definitions/definition-pack/definition.json) already permits separate current-use assessments that preserve frozen history.

**Repair:** embedded readiness records preparation-time evidence. A later observation binds exact Pack digest, intended use, current source/profile/owner obligations and evidence. It may refuse the use without rewriting history. Changed selected input, intended use, payload, concept set or meaning produces the applicable new frozen revision and any required fresh review; the observation does not authorize it.

## D06 — Retaining a package requires an actual reconstruction contract

**Category:** hidden glue / evidence ceiling. **Disposition:** revise and route.

[DESIGN §8](../0006-runtime-integration-design/DESIGN.md) distinguishes a directory package, a member manifest and retained “package bytes.” [Source/v1](../../../authority/artifact-types/source/v1/schema.json) supplies a locator and content digest, but does not itself define directory traversal or a resolver for every member. Work output refs likewise do not imply successful resolution.

**Failure:** the manifest is available and its digest matches, but `pack.json` or a required evidence member is absent. A subsequent Session cannot reconstruct the claimed result.

**Repair:** propose one identity convention: exact manifest-root bytes plus the complete required content-addressed member closure. Bind Source's digest to those exact root bytes and select a resolver that retrieves and checks every member. Keep optional versus required members explicit. A missing required member blocks full reconstruction. Exact root/member resolution through existing custody remains to be qualified; the proposal does not claim that a new storage route already exists.

The original already assigns governing publication to the host and makes durable retention conditional. Preserve those boundaries; this finding concerns the unclosed transfer/resolution mechanism, not a supposed second governing publisher.

## D07 — Authoring and parameter interpretation are real inputs

**Category:** responsibility closure / knowledge status. **Disposition:** revise.

The deterministic kernel receives handling that somebody has already supplied. The existing chat path does not by itself prove an adapter for every revised handling payload. Separately, Definition/v2 has no generic top-level parameter field; an extraction by an LLM cannot create authoritative declarations.

**Repair:** name the interaction adapter's output: attributable explicit handling or a recorded candidate supplement, with source/input lineage. Model suggestions remain suggestions; submission is not semantic admission. Missing authoring support is an explicit limitation. Bind parameters to exact meaning clauses and types, or report `parameter-contract-unresolved`.

The original already rejects a new independent parameter registry. Keep the mapping subordinate to the Pack and selected meaning; do not invent another registry to solve this.

## D08 — Preserve the objective while naming partial delivery accurately

**Category:** objective drift / delivery scope. **Disposition:** reconcile.

[L0](../0006-runtime-integration-design/IMPLEMENTATION-LAYERING.md) is already honestly labelled snapshot-only, so the design does not claim it proves live integration. Nevertheless, accepting a local serializer as the integration outcome would leave the central host boundary unexercised.

**Repair:** retain the snapshot core as an implementation step. Name the first runtime-integration acceptance as an actual permitted host cut/context → Pack episode, including stale/expired refusal and Session cleanup. If the host prerequisite is missing, core progress can continue, while live acceptance remains pending. Materialization/review and authorized publication/reconstruction remain later distinct acceptance boundaries.
