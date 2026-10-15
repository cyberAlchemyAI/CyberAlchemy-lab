# Generated proposal consumer integration

Status: candidate implementation analysis. Authority effect: none.
Controlling source: frozen `interface/api-v71`; original public contracts retained.
This analysis makes no new admission or owner outcome.

## Current path

`challenge.submit` creates an Evidence Set, open Challenge Event and two declared
Typed Relations. Its completed operation record binds the exact original input,
source cut, generated proposal and evidence objects. `GeneratedCandidateHandlers`
reconstructs that result under the current authenticated grant before selecting
its metadata for the original generic validator. Two carrier-specific semantic
reference obligations remain not-evaluable.

The adapter also authors `change.prepare` consumption, but that path still needs
actual selected runtime qualification. A valid proposal shape is insufficient.

## Verified integration gaps

1. `protocol.CHALLENGE_SUPPORTED` excludes `proposal.review`. `auth.policy_guard`
   requires the exact operation list for each independently selected policy kind.
   Adding a public operation string or reusing the challenge grant cannot create
   review authority.
2. `Service.select_review` requires independent private `candidate:review-routing`.
   `ReviewPreparation` verifies exact source cut, workflow profile, accountable
   Principal, preference, ordered stable cores and all required owner voices.
3. The review member loop reads core and content through the original Vault input
   accessor. Challenge outputs are generated objects, so their consumption must
   be explicitly selected and verified before that loop.
4. The existing positive review fixture includes a proposed User Decision
   Preference as its own independent target. It resolves the accountable owner
   without inferring a legacy user/Principal alias. The challenge's exact
   four-target proposal cannot silently acquire an additional preference target.
5. The current generated selector accepts only the whole exact completed challenge
   proposal. It intentionally rejects arbitrary combinations and changed targets.
   A composition of independent targets therefore needs its own exact private
   selection/provenance contract and original validation.

## Recommended next implementation

First qualify original `change.prepare` using the exact four-target generated
proposal, retaining every gap and testing retry/refusal boundaries.

Then implement an explicitly selected candidate workflow policy with bounded
challenge, generic preparation and review grants. Keep the existing standalone
policies and original operation contracts. Verify each operation's independent
private control and finite scope; no request field supplies a grant or owner voice.

For multi-member review, declare a private exact candidate composition selector.
Select each generated member from a completed producer's original operation
record and each provisioned member from its exact input binding. Verify original
content, metadata, core, producer identity, namespace, source cut and current
permission. Preserve member order and original bytes. Reject changed, missing,
pending, foreign, expired or unselected material before a new claim.

Construct any additional preference as a separate explicit candidate target with
its own core, source-derived carrier and owner routing. Do not append it inside
challenge submission or interpret it as an admitted preference.

Re-execute the original validator and review preparation for the exact composed
proposal. Read generated review members through a locally selected material view
that delegates real guards and preserves the actual Vault manifest, input table,
callbacks and grants. Preserve unresolved semantic references and current owner
authority flags; a candidate review package records no actual decision.

## Required proof

- Actual submit -> prepare -> review path with exact original contracts.
- Four challenge members plus any separately declared preference covered once.
- Exact producer provenance and independently selected member/core order.
- One final checkpoint with every independent required owner voice retained.
- No current owner authority, canonical mutation or activation inferred.
- Refusal for altered bytes/metadata/order, missing/pending producer, expired or
  revoked routing, unsupported operation and absent required owner declaration.
- Exact retry returns the recorded outcome without redispatch or new writes.
- Original source exit and owned fixture cleanup, then current inherited regression.

This work remains within R03 candidate construction. S02 must still close the
complete package before the sole R08 owner interaction; A01-A04 preserve the
separate authorized application and operational acceptance obligations.
