# Authority Boundary: formalization aspect review

Candidate agent self-review, 2026-10-08. Authority effect: none. This delivery advances **F02-T.cal.definition.authority-boundary** under the [definitions/types/logic-first model](../../../foundations-first-v1/FORMALIZATION-MODEL.md) and [detailed DAG](../../../foundations-first-v1/DAG.md). It is partial: whole source translation, owner fidelity, universal obligations and episode completion remain open.

## Source identity, recorded admissions and precedence

[Context](context.json) binds current Authority Boundary/v1 source SHA `e6928339ebf6cbd41966e268da7eeee32d395da382522da086f98c3e2737896c`, the 201-file source snapshot, actual A04/C01/E02 candidate prerequisite receipts, the exact SWU and the sealed Authority Claim predecessor. All 2,747 predecessor candidate files remain byte-preserved. The authored output directory was absent before this unit.

This is a Lab-authored definition rather than the D34 legacy reconstruction used for Authority and Authority Claim. [Source checks](source-checks.json) perform **21 actual read-only checks** of current identity/registry, Definition/v1 shape and bound generator, deterministic two-run projections, decision0053 and its exact admission-queue manifest, preserved historical registry entry and three whole-JSON source selections. The projection is 4,636 bytes, SHA `69341e47e5bc2e319ed0c344fd7196e4dc0366fc0c5c5559ff04ff8adf92ad84`.

The three upstream sources are exact Definition/v1, Governance Language/v2 and the Foundation-01 Owner registry. Their declared SHA values match selected local bytes and exact records in decisions0018,0025,0013 respectively. The Foundation registry records one declared principal and five separate roles; recorded admission does not collapse those scopes. Historical embedded candidate status remains intact under those recorded admission overlays. These checks do not authenticate the actual human/owner/role, prove upstream latest-version currentness or establish interpretation fidelity.

[Comparison selection](comparison-selection.json) binds separate Authority, Claim, Role, Assignment, Principal, Decision, Effect and DecisionScope meanings, plus the sealed Claim draft. None is imported into primary T. In particular, the source's named Governance Decision requires a reviewed map to the selected current Decision definition/carrier; a matching label is insufficient.

## Definition form, roles and signature

[Correspondence](correspondence.json) accounts for every character in **28 source units and 30 spans: two encoded, eleven explanatory, seventeen deferred**. The encoded clauses are axiomatic-implicit specifications with definition role. The Definition artifact's kind is distinct from the logical role of its clauses; no proposition about actual world permission is assumed merely because it is stored in a definition.

[Interpretation](t.json) and [canonical IR](static-ir.json) contain **45 declarations** over nonempty Entity, State and Token, EMPTY Token, six total functions and typed predicates/relations. Boundary, Role, Principal, GovernanceDecision, target and effect kind share Entity. Qualified names prevent identifier collision but neither globally disjoint these meanings nor align them across definitions.

The first encoded clause requires an ExplicitBoundary and OwnerScopedLimit, six explicit binding/set/route markers, a Role-valued selected ownerRole, a Principal-valued selected boundPrincipal, and nonEMPTY selected scope/challenge tokens. The six fields are owner role, accountable-principal binding, authority scope, allowed-effect set, excluded-effect set and challenge route. Named set markers do not imply nonempty extensions; the source itself does not require an allowed effect to exist. Exact tuple equality and value/role/set/route denotation remain unaccepted.

OwnerRole/boundPrincipal are total Entity projections; decisionTarget/decisionEffect are total Entity projections; scopeValue/challengeValue select Token. Their values are candidate interpretations, not authenticated real owners, targets, effects, principals or scopes. The carrier's labels, current fixture identities and actual semantic objects need explicit mappings. The single selected owner role does not imply that its principal holds only that role.

## The two directions of MayDecide

The second encoded clause keeps the source **iff**, under explicit Boundary/Principal/GovernanceDecision conceptual typing:

```text
MayDecide(p,d,b) iff
  HoldsRole(p, ownerRole(b))
  and ScopeContains(b, decisionTarget(d))
  and AllowedEffect(b, decisionEffect(d))
  and not ExcludedEffect(b, decisionEffect(d)).
```

MayDecide tuples also have a selected conceptual type-closure constraint. The necessary direction rejects a tuple with a missing condition. The sufficient direction rejects a model where all four selected conditions hold but MayDecide is absent. Exclusion takes precedence when an effect belongs to both sets. This is an interpretation of local source eligibility, not a grant of actual world permission, execution or admission.

The source formula does **not** require `p = boundPrincipal(b)`. It refers to role holding, while the normative tuple binds an accountable principal. The rich model has a second principal holding the same role and qualifying under the written iff even though its identity differs from the selected bound principal. The notation also describes `p` as the accountable principal acting under an owner role. That may require an implicit binder restriction beyond the printed iff. This exposes ABN-BINDING-002 and a source-precedence question; the wider candidate Principal guard is not accepted whole-source fidelity. I do not silently add equality to the primary formula or claim that the source owner accepts unrestricted alternate actors.

The source formula also has no State, revocation or effective-period premise. A selected revoked marker can coexist with MayDecide under partial T. That does not establish actual current authority; it exposes the difference between the written formula and stronger carrier/time qualification. Those fields require explicit extension semantics, rather than retroactive insertion into the source iff.

## Models, required populations and proof strength

[Model controls](model-controls.json) independently evaluate **45 authored controls** and **17 outside-T targets with checked countermodels**. Ten required hypothetical populations cover Boundary, a MayDecide witness, one principal with two separate owner roles, allowed/excluded overlap, excluded-effect refusal, an empty allowed-effect Boundary, an eligible actor differing from the bound principal, a revoked marker with local MayDecide, MayDecide without actual authorization and distinct Boundaries with shared owner/principal/scope token. **Thirty-four population decisions remain unresolved.** These are selected hypothetical witnesses, not actual existence or exemptions.

Controls reject missing explicit bindings, missing conceptual role/principal types, empty selected scope/challenge, each absent eligibility condition, eligible-but-not-MayDecide, excluded-over-allowed decisions, wrong role/scope, and tuples outside conceptual Principal/Decision/Boundary types. Independent world facts, authenticated markers, authorization or executed-decision markers can coexist without being inferred.

Six structural controls reject a non-total owner function, ill-sorted function result or EMPTY constant, wrong MayDecide arity, duplicate role holding and empty Entity domain. The evaluator checks typed tables before logical truth. T can be vacuously satisfied by an empty Boundary extension with no MayDecide tuples, while required I fails. Removing revocation or the alternate-actor witness, or adding selected permissions to the formerly empty allowed set, can satisfy T while failing a chosen rich population. Rich witness failure is not a universal source prohibition on those alternatives.

Countermodels distinguish Boundary from truth, evidence quality, validation success, actual right, admission, runtime activation, external effect and workflow placement. They distinguish local MayDecide from bound-principal equality, boundary authentication, actual authorization/execution, all-state effectivity or absence of revocation. They also show that allowed/excluded sets need not be globally disjoint, shared owner/principal/scope token need not merge Boundary identity, and a Boundary need not admit any selected decision.

These results are independent evaluations of supplied finite structures. They are not exhaustive model enumeration, accepted source denotation, actual credential/owner/scope/effect validation, meaning-aligned joint theory or universal theorem proof.

## Resource-bound failure and equivalent population rewrite

The preserved [first attempt](attempts/001-equivalent-population-guard-ordering/attempt.json) retains the actual terminal model failure, successful source/profile/dependency checks, original candidate/IR/scripts and read-only per-control diagnostics. Only the empty-Boundary vacuity control exceeded the unchanged 100,000-step cumulative budget across required populations. The baseline itself needed 41,474 steps. Resource exhaustion was not interpreted as falsity or repaired by raising the budget or shrinking the model.

The rewrite commutes existential binders and hoists conjuncts before binders whose variables are not free in those conjuncts. It also substitutes the total boundPrincipal projection for its existential equality witness. Primary theory, source/scope/signature, required-population metadata and domains remain unchanged.

[Rewrite checks](population-reordering-checks.json) independently compare old/new truth for every required population across all **39 well-formed control models: 390 equal results**. Each comparison uses a fresh evaluator per formula to inspect the rewrite, with unchanged limits. Main model controls retain their existing cumulative budget. The comparison is bounded supplied-model evidence plus an explicit logical rewrite explanation; it does not claim a mechanized universal equivalence theorem or owner fidelity.

The [second preserved attempt](attempts/002-rejected-hostile-input-audit-scope/attempt.json) records a failed sealing-audit condition. I initially required the actual-authentication input flag to remain false even in the intentionally hostile input that sets it true and is correctly rejected. The corrected audit requires false on accepted inputs, explicit rejection of the hostile true input, and false actual-authentication observations in every case. No episode/coverage/receipt/manifest output existed after that failed audit; the seven replay checks and source theory were unchanged.

## Stronger qualification and temporal hypotheses

[Profile checks](authority-profile-checks.json) contain **25 Boundary-specific decision profiles, thirteen rejected**. Four selected role/target/effect hypotheses produce a local source-iff observation. Separate actor/role/owner-decision/fidelity support, exact actor-to-binding literal match, selected effectivity and a not-revoked label define a stronger hypothetical qualification. Every map/support marker is explicitly hypothetical; actual permission/authentication stays false.

The source-iff observation can remain true with a different acting principal, a revoked/expired label, selected non-effectivity or unknown effectivity. The stronger hypothetical gate rejects or retains unknown in these cases. Missing role holding, outside-scope target, unallowed effect or excluded-over-allowed effect blocks both selected eligibilities. Other held roles do not widen this selected Boundary. Missing mappings/support, actor/Boundary identity collapse, implicit grants and fabricated actual authentication are rejected.

The same report separately retains **42 related Claim/right context profiles, 23 rejected**, and **19 finite history frames, ten rejected**. Those related profiles use Claim's eight-field tuple and a nine-axis context; they do not replace Boundary's six-field tuple or primary formula. They keep source, role, surface, scope, operation, effect, purpose, mirror and source-space maps explicit, with independent governing support and unknown effectivity. The frames cover copy/move/change/requalification/revocation/successor/separate-grant hypotheses. None executes an actual workflow, proves all reachable-state noninterference or authenticates history.

The source says workflows/preferences cannot create, move, merge or widen authority; one principal holding multiple roles does not merge their Boundaries; checkpoints grant no authority; validation cannot replace an owner decision. Those obligations retain explicit source spans and findings. Finite examples and profiles support interpretation work but do not discharge their universal operational meaning.

## Current carrier, extra fields and joins

**107 bounded actual carrier/catalog checks** bind nine admitted-current related descriptors/schemas/fixtures, both Claim and Boundary exact source bindings, deterministic projections, each declared validator, ten hostile fixtures and all 41 current Kind records. The current Boundary/v1 descriptor binds this exact definition path/SHA. Its embedded candidate status is preserved alongside current catalog admission facts. No canonical validator writer, receipt or source is modified.

The Boundary payload carries owner_role_ref, accountable_principal_ref, authority_scope_ref, allowed_effect_kinds, excluded_effect_kinds, challenge_route_ref, effective_period and revocation_state. It adds the last two fields to the source's six-field tuple. Record owner_ref, payload owner role, record challenge route, payload challenge route, root scope and payload authority scope need reviewed maps; the fixture already uses distinct labels. The current carrier also requires at least one allowed-effect label, whereas the partial source theory admits an empty allowed set. This is a source/carrier conformance question rather than an unannounced source requirement.

**34 side-carrier shape probes accept 22 and reject twelve.** Eight new Boundary probes accept active+revoked, retired+not-revoked, empty excluded effects, whitespace role/principal binding, differing root owner/owner-role and differing record/payload challenge route. They reject empty allowed effects and duplicate allowed labels. Retained probes accept allowed/excluded overlap, arbitrary effective-period text, unresolved owner/scope/basis labels, active labels and self successor; they reject actual grant effects, Authority-kind collapse and undeclared added fields. Shape does not enforce role holding, actor authentication, scope membership, time interpretation, revocation policy or actual permission.

Literal fixture joins preserve gaps. Boundary authority_scope_ref differs from selected DecisionScope identity, while its relation-ref DecisionScope token matches. Claim's EvidenceSet token also matches its selected fixture. Boundary Principal/owner Role and Claim claimant Role/basis Decision labels do not match their selected related fixture identities. Claim/Boundary root scopes differ. Neither these matches nor the Foundation source's one-principal/five-role record authenticates this fixture's actual owner route.

## Relations and canonical alignment gaps

The current catalog has five Claim directions and two Boundary directions. Boundary's governed-by→Policy and scopes-authority-over→DecisionScope directions are separate semantic connections requiring exact relation kinds, qualifiers and Typed Relation identities. Both Boundary endpoint pairs are declared by their current Kinds and absent from current Typed Relation/v3 schema branches.

All **24 side metadata cross-product combinations** pass shape, including **17 undeclared combinations**. Of ten current side direction/peer triplets, seven pass their carrier metadata schema and three added Claim directions fail. Of nine unique side Kind pairs, seven pass Typed Relation/v3 and the two Boundary pairs fail. Authority-scope has three Kind pairs versus two schema pairs.

The full governed-by comparison remains **29 Kind pairs versus 23 schema pairs**, no extras. All 29 are tested: 23 pass, six fail. Omitted sources to Policy are AdmissionTransaction, AuthorityBoundary, DecisionBundle, DecisionCheckpoint, UserDecisionPreference and WorkflowDecisionProfile. Evidence-bears-on, authority-scope and succession retain their forbidden truth/acceptance, permission/authentication/execution and automatic identity/authority-transfer inferences. These are exact preserved observations, not a canonical schema repair, actual new relation, conformance or admission.

## Dependency closure and episode denominator

[Reachable graph](dependency-graph.json) and [joint graph](current-dependency-graph.json) contain **82 nodes, 448 authored edges and 51 missing counterpart packets**, with one unclassified **31-member component containing 280 internal edges**. This unit authors 28 semantic uses. The missing count rises because additional dependencies are exposed; it is not a proof regression. Complete edge review, SCC semantics, common-carrier maps and source meaning alignment remain unresolved.

[Current inventory](current-inventory.json) freshly reevaluates one supplied T/I model for **31 partial drafts**, leaving **152 current identities without per-definition T drafts**. Scope stays 183 current identities and 189 admitted versions. Aggregate coverage: 719 source units, 967 spans, 229 encoded, 260 explanatory, 478 deferred, 250 required and 760 unresolved populations. Whole source-owner-accepted translations and whole-definition proofs remain zero. I04's earlier selected eight-draft report stays intact pending a separately scoped reporting update.

## Disposition and next work

[Fresh replay results](fresh-command-results.json) retain seven actual checks: contract/model/source/profile/dependency/inventory plus the rewrite comparison. [Receipt](receipt.json), [coverage row](coverage-row.json), [episode status](episode-status.json) and [delivery manifest](delivery-manifest.json) bind exact outputs, preservation, the preserved failed attempts and partial ceilings.

Eight ABN findings cover source precedence, actor/binding mismatch, membership denotation, carrier time semantics, workflow noninterference, role/non-grant separation, relation/carrier alignment and complete closure. This self-review supports a partial candidate only. Next is **F02-T.cal.definition.authority-model**, after its actual prerequisite/output checks. Complete translation and owner fidelity, family/common-theory obligations, universal operational proofs, independent replay and the final complete episode review remain required.
