# Reference resolution for generated challenge members

Status: bounded implementation analysis. Authority effect: none.
Current source: `interface/api-v71/candidate.py`, `generated_candidate.py`,
`challenge_submission.py`, and `challenge_fixture.py`.

The original generic validator reports two not-evaluable checks, one for Evidence
Set/v1 and one for Challenge Event/v1. Producer verification does not remove these
checks or prove every consumer obligation. A successor must produce separately
bound carrier-specific checks before replacing a gap.

## Evidence Set

The actual generated payload has `source_refs` and `item_refs`. In this fixture,
the source is an exact Work version and an item is an independently completed
validation receipt. Both are declared original bindings in private challenge
routing. The receipt is operational evidence, not an artifact node or a Source
artifact inferred from its locator.

The consumer must resolve each reference through the selected typed original
binding registry. Verify original bytes and the declared posture, exact artifact
header when present, captured original schema where applicable, and actual receipt
scope. Require complete coverage and reject duplicate/ambiguous binding matches.
Validate the selected Project membership and keep the separate Typed Relation.
Preserve the coverage statement and every limitation; byte availability does not
prove factual coverage or truth.

The generated output copies use workspace-object locators. Payload references
retain original source/receipt locators. Do not rewrite the payload to match the
copied locators. Derive and verify their correspondence from the exact completed
producer record and its current independent routing.

## Challenge Event

Resolve `challenge_contract_ref` and `challenger_ref` to the exact independently
selected current Challenge Contract and active authenticated Principal. Resolve
`subject_ref` together with `subject_version_ref` and the original byte binding;
historical subject use requires explicit permission and its exact historical
carrier, with no promotion to current membership.

Require the ground to be declared by that exact contract, all required evidence
kinds to be present, and every `evidence_ref` to resolve through the verified typed
original binding registry. Verify declared challenge relations against their
independent relation target, signature, axis, endpoint kinds and exact revisions.

For this producer's open output, `response_state` is `open`, the explicitly
reconstructed `resolution_decision_ref` is `none`, and `residue_refs` is empty.
That producer-specific state records no resolution Decision. Do not turn this
bounded token handling into a generic lifecycle rule for every Challenge Event.
Other states and actual resolution require their own contract, exact Decision and
current authority evidence.

## Implementation boundary

Keep unrecognized carriers not-evaluable. Add a selected carrier resolver contract
with exact producer provenance and original-byte access; avoid a generic string
lookup that collapses artifact references, receipt bindings and protocol locators.
Retain original native schema/core preparation and typed connection checks.

A resolved check proves reference closure within the selected cut and provenance.
It grants no factual adjudication, owner response, admission or operational effect.
Add real negative cases for missing original receipt, changed source/subject bytes,
wrong evidence kind, foreign Principal, ambiguous selector and undeclared ground.
Qualify original validation/preparation plus current inherited regression before
claiming this reference-resolution increment complete.
