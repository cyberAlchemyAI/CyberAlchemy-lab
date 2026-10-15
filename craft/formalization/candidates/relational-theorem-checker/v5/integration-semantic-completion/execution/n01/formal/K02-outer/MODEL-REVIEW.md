K02 outer Intent Resolution: schema shape and source boundaries

This candidate formalizes all fourteen required outer fields of the existing
Intent Resolution record. K02's intended meaning has been accepted separately.
K04's current owner review and shared-policy assessments are unaffected. No
inherited obligation is discharged and no successor task is accepted here.

The complete typed carrier preserves schema_version, node_id, kind, name,
lifecycle_state, authority_effect, owner_ref, scope_ref, evidence_refs,
challenge_route, successor_refs, relation_refs, payload and claim_ceiling. The
payload preserves all five fields. Each relation reference preserves its four
required fields. This representation requires every field at construction time;
it does not parse raw JSON or represent a missing/extra field.

RecordShape is independently specified from the schema's value constraints. It
requires the exact schema/kind/authority constants, the four allowed lifecycle
labels, nonempty scalar strings, nonempty elements in reference lists, uniqueness
where the source schema requests it, at least one relation reference, exact
relation/direction/counterpart enum membership and all payload shape rules.
recordShapeCheck tests those constraints explicitly. Its equivalence theorem
targets precisely the independent proposition. checkCarrier preserves the whole record
or refuses it; successful admission cannot rewrite, omit or normalize any field.

The source schema differs from full relation semantics in several consequential
ways. Evidence may be empty. An arbitrary nonempty owner label passes shape.
Retired records remain shape-valid. All selected/test/excluded lists may be empty.
A subject may be both selected and excluded. Relation-kind and counterpart-kind
enums are independently checked, so successor-of paired with challenge-event
also passes shape. These are deliberate shape-valid controls, not newly endorsed
semantic outcomes. Distinct raw selected tokens may also be aliases for the same
resolved revision: raw-string uniqueness does not prove resolved-subject uniqueness.
The catalog preserves those aliases and the K02 checker must refuse a duplicate
resolved selection. Later adapters must establish the exact policy joins, current
use posture and evidence sufficiency. The existing K02 checker still refuses
excluded subjects and does not derive satisfaction from empty tests.

Source-fixture generation preserves the original fourteen-field record exactly.
The generator compares 35 typed-shape controls against the existing JSON Schema,
covering all scalar constants/nonempty fields, lifecycle, array elements and
uniqueness, the relation-list minimum and all four relation-reference fields,
payload scalar/list constraints and the permissive cases above. Lean control
modules state the same concrete checks. Fifteen additional JSON Schema probes
remove each outer field or add an extra field; these cannot be represented by
the carrier and remain explicitly unproved raw-adapter obligations.

Verification requires fresh pinned Lean compilation and separate fresh replay,
per-theorem axiom inspection and matching-phase import resolution. Preparation
compilation is not the final evidence. Standard propext, Quot.sound and
Classical.choice are the only allowed axioms. Same-kernel replay does not satisfy
the mandatory independent-checker requirement. Final verification and import
audit reports, when present and valid, establish only this typed-shape component.

Remaining formalization and integration work:

- Define raw JSON-AST/object interpretation, including required/closed keys,
  duplicate keys, exact field types, list order and byte/parser normalization.
  Prove or declare the exact trust premise for source-to-carrier translation.
- Authenticate immutable full source records, exact revisions/digests and the
  owner/profile/scope/snapshot capture. Relate actual bytes to the complete body.
  The generator and role-shaped owner_ref label establish none of this.
- Independently interpret owner, scope, lifecycle, evidence, challenges, successor
  and relation metadata under the exact owned policies. Neither a lifecycle label
  nor authority_effect = none is proof of an authorized operation or live status.
- Join guarded complete-catalog payload resolution with the issued Resolution,
  actual source record identity/body and complete frame. Reject cross-frame or
  conflicting records; retain every outer field for provenance/claim checking.
- Refine intent_resolution_ref/addressing_role and owned Selection companions,
  proving full-source equivalence to Addresses over all six branches.
- Compose qualified recording, full-rule protected-state preservation and the
  independently defined satisfaction/completion/authority/membership outcomes.
  Finish whole-theory countermodels and mandatory independent checking.

The plan's full scope remains all 41 relation kinds, 550 endpoint pairs, seven
extension integrations and 263 inherited pending obligations. Preserve the
90 original discharges and scoped original R06/G4 acceptance. Whole source
refinement and plan completion are not established by this component.

Current validation: the typed-shape component passes fresh pinned Lean
compilation and a separate fresh replay with 46 new declarations (11 general
lemmas and 35 concrete controls), 28 compiler invocations and 232 axiom
inspections including imported dependencies. All 28 matching-phase import
audits pass. The source guard naming failure is retained in repair-attempts/01;
the helper was renamed without relaxing the guard. The final reports bind the
current source versions. The 15 missing/extra-field probes remain Python schema
evidence only. There is no JSON parser, authentic capture, whole-source or
independent-checker proof, and no inherited ID is discharged.
