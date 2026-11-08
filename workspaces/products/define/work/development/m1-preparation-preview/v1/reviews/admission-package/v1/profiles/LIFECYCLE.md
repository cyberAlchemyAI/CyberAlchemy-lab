<!-- GENERATED FILE: edit the bound canonical profile JSON. -->

# Definition/v2 lifecycle profile

> Generated from `lifecycle.json`; this view is not canonical.

- Record: `CAL-LIFECYCLE-DEFINITION-V2`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Owner: `role:definition-owner`
- Subject: `cal.artifact-type.definition/v2`
- Profile schema SHA256: `533d6487edd40a3006e9deb73c205ad9ae0f87562f665d9d995ca8cdc5d72d16`
- Check/phase contract: `define/development/m1-preparation-preview/v1/steps/04-definition-v2-profiles/check-contracts.json`
- Check/phase contract SHA256: `bedd3309bd4c1c6c079cddcc05a113159f5868c60f432003543062b986c998c7`

## States

- `candidate-authored`
- `validated-candidate`
- `owner-reviewed`
- `admitted`
- `superseded`
- `withdrawn`

## Transitions

| From | To | Gate | Effect |
| --- | --- | --- | --- |
| candidate-authored | validated-candidate | Exact validation phase in the bound check contract is PASS under adopted applicable profile/carrier bindings; checks 13-14 are excluded. Record a separate attributable transition for this exact candidate epoch. | Record scoped validation posture; create no semantic authority. |
| validated-candidate | owner-reviewed | Checks 01-12 PASS; applicable owner review/fidelity record binds the exact candidate and evidence; a separate transition record confirms review completion. | Record review completion; select no admission effect. |
| owner-reviewed | admitted | Pre-decision eligibility is established without a prior admission; exact owner Decision passes check 13 and its authorized application passes check 14. | Only confirmed applicable admission makes the selected exact version authoritative within its scope. |
| admitted | superseded | Exact owner successor Decision and confirmed coherent application select the admitted replacement and preserve predecessor bytes/history. | Retire current lookup for this predecessor only after the exact successor becomes effective. |
| candidate-authored | withdrawn | Exact applicable owner withdrawal Decision and confirmed application; if the subject is current, bind a replacement or terminal lookup route. | Record withdrawal and preserve evidence/history; remove current authority only when applicable. No deletion is inferred. |
| validated-candidate | withdrawn | Exact applicable owner withdrawal Decision and confirmed application; if the subject is current, bind a replacement or terminal lookup route. | Record withdrawal and preserve evidence/history; remove current authority only when applicable. No deletion is inferred. |
| owner-reviewed | withdrawn | Exact applicable owner withdrawal Decision and confirmed application; if the subject is current, bind a replacement or terminal lookup route. | Record withdrawal and preserve evidence/history; remove current authority only when applicable. No deletion is inferred. |
| admitted | withdrawn | Exact applicable owner withdrawal Decision and confirmed application; if the subject is current, bind a replacement or terminal lookup route. | Record withdrawal and preserve evidence/history; remove current authority only when applicable. No deletion is inferred. |
| superseded | withdrawn | Exact applicable owner withdrawal Decision and confirmed application; if the subject is current, bind a replacement or terminal lookup route. | Record withdrawal and preserve evidence/history; remove current authority only when applicable. No deletion is inferred. |

## Separation invariants

- Semantic identity, lifecycle state, source currentness, validation result, authority state, and publication state are independent axes.
- A digest change creates a new candidate epoch; it cannot refresh an old admission decision.
- PASS does not imply owner review, admission, publication, implementation, or correctness.
- Directory placement and generated projections never change lifecycle state.
- Representation PASS, full validation, owner review, pre-decision eligibility, selected admission and confirmed application are separately recorded.
- No profile or walkthrough executes a transition. No gate requires its own future Decision to already exist.
- Changed subject/evidence/profile/source/effect bytes invalidate affected evidence and require a new epoch and applicable review. Historical state/evidence remains preserved; no automatic backward lifecycle rewrite.
- Revise, defer and reject are review outcomes, not extra Definition lifecycle states. Defer can preserve the current state; withdrawal requires its explicit selected effect and applicable transition.
- Candidate profile use in a preparation preview cannot promote the example to validated-candidate or admitted under an unadopted contract.

## Claim ceiling

Proposed lifecycle successor. Defines gates and effect boundaries; performs no owner review, transition, admission, supersession, withdrawal, lookup update or runtime activation.
