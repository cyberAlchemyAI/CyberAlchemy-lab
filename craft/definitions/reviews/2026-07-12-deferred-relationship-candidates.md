---
artifact_role: pre-canonical-relationship-review
status: review-ready
current_disposition: defer
owner: definitions-governance
source_task: SWU-R3C-007
created: 2026-07-12
---

# Deferred Relationship Candidate Review Packet

This packet gives three DS-D8 deferred candidates a falsifiable owner route. It
is not relationship authority and does not change their current `deferred`
state in [relationships.yml](../relationships/relationships.yml).

The promotion filter is the
[relationship non-collapse test](../DEFINITIONS.md#domainspec-v2-d18-relationship-non-collapse-test):
removing a candidate must change at least one named property—reject/allow,
derivation, projection, composition path, owner route, or generated artifact.
Clearer wording or a convenient graph arrow is insufficient.

## Decision matrix

| Candidate | Current overlap / collapse pressure | Positive witness required | Negative witness required | Changed obligation if promoted | Promote criteria | Defer criteria | Reject criteria | Owner route |
|---|---|---|---|---|---|---|---|---|
| `depends-on` | Overlaps ordinary field/reference dependency and may overlap existing typed edges once endpoints are declared. Current candidate has no bounded source/target types, so active-signature overlap cannot yet be adjudicated precisely. | Declare finite endpoint types and one concrete spec pair where adding/removing only `depends-on` changes a named D18 property—for example a validator decision, derived build obligation, or typed composition path that no existing edge or field reference expresses. | Show the same implementation and validation outcome using an existing DS-D8 signature or a typed field/reference, with no changed obligation or generated artifact. | A named endpoint rule plus a specific validation/authoring duty such as required dependency presence, cycle rule, build-order obligation, or generated dependency projection. | Typed endpoints + cited active-overlap analysis + positive/negative fixtures + at least one changed D20-D25 property + owner-approved semantics and validator/authoring surface. | The use is intelligible but endpoints, distinct consequence, fixtures, or implementation owner are missing. | Every bounded example collapses into existing edges or ordinary field/reference dependency and removing the label changes no D18 property. | definitions-governance owner gate; validator owner joins only after a concrete changed obligation is named. |
| `operation-returns-value-object` | Currently represented as an Operation signature/return-type property. Candidate edge pressure is `Operation -> Value Object`, but no distinct graph behavior beyond the property is witnessed. | Provide otherwise identical Operation specs where the relationship—not merely the declared return type—changes validation, a public derived obligation, composition, or a generated artifact. The witness must explain why a return-type property cannot carry the distinction. | Model the return as the existing typed Operation signature and show identical validator, generation, and implementation results without a relationship edge. | A relationship-specific endpoint rule and at least one new observable obligation, path, or generated output that cannot be derived from the return type alone. | Non-collapse from the signature property + exact endpoint semantics + red/green fixture pair + named public obligation/artifact + definitions and validator owner approval. | A plausible graph use exists, but the only current semantics are return typing or no executable witness exists. | All uses are fully and more simply modeled by the Operation return-type property, with zero changed D18 property. | definitions-governance owner gate with content-validator/engine contract review; private derivation rules are not evidence. |
| `event-payload-publisher-composite` | Pressures a composite of Event payload typing, Operation `produces`, Entity `emits`, and publisher metadata. Current endpoint enforcement for `produces`/`emits` is already unblocked. | Give a concrete event spec where the composite changes an allow/reject decision, public obligation, typed composition path, or generated artifact beyond the conjunction of payload fields plus existing `produces` and `emits`. The witness must keep publisher, producer, entity source, and payload roles unambiguous. | Decompose the same case into payload typing + `produces` and/or `emits` and show equivalent validation, generation, and implementation obligations. | A composite-specific well-formedness rule and named output/obligation whose failure cannot be detected by the decomposed model. | Non-collapse from the decomposed model + typed role semantics + positive/negative fixtures + changed D20-D25 property + owner-approved validator/authoring contract. | Role boundaries or distinct behavior remain uncertain, or only endpoint-enforcement pressure is known. | Every case decomposes without loss into payload/signature metadata plus active relationships, so the composite adds no distinct D18 property. | definitions-governance owner gate; DS-D8/validator owner reviews any proposed composite rule. |

## Current rulings

| Candidate | Current ruling | Reason |
|---|---|---|
| `depends-on` | `defer` | No typed endpoints or non-collapse witness. |
| `operation-returns-value-object` | `defer` | Current return-type property is sufficient until a distinct observable consequence is shown. |
| `event-payload-publisher-composite` | `defer` | Existing payload/signature metadata plus `produces`/`emits` have not been shown insufficient. |

These are evidence-state rulings, not permanent rejection. A later proposal must
open a definitions-governance owner review and cite the exact row above that it
satisfies. No candidate may enter active DS-D8 through this packet alone.

## Review checklist

For any reopening:

1. Declare candidate semantics and finite endpoint types.
2. Name the closest active signature or non-edge representation.
3. Cite at least one D18 property that changes.
4. Supply a positive witness and a collapse/negative witness.
5. Name the validator, public obligation, projection, composition path, owner
   route, or generated artifact that changes.
6. Route the decision to definitions-governance; route implementation only
   after the semantic owner accepts a non-collapse claim.
