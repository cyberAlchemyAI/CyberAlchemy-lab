K02 complete nested JSON-AST source projection

This candidate closes the representation gap left by the complete typed carrier:
raw objects can now contain missing fields, extra fields, duplicate keys or wrong
value types. K02's intended relation meaning was accepted separately. K04 and
global shared-policy assessments remain pending; no inherited obligation or
successor task is accepted by this component.

The JSON value model includes null, boolean, number tokens, strings, ordered
arrays and objects represented as ordered lists of key/value entries. Object
entries retain duplicate keys. Numbers retain a lexical token because number
syntax is part of the unproved byte-parser premise; this schema has no numeric
fields. There is no coercion between number, boolean, null and string values.

The independent object denotation requires unique declared schema keys, unique
input keys, no undeclared input key and an exact value for every required key.
It states membership directly and does not call lookup or a decoder. The
fixed adapters use the exact fourteen record keys, five payload keys and four
relation-reference keys. Lookup is performed only after duplicate/extra-key
checks. Missing required fields cause complete refusal. Identical and conflicting
duplicate keys both refuse. This is an explicit candidate parser-profile choice;
its owner assessment under N01's existing choice/policy review and actual byte
implementation are still required.

The array denotation specifies every input position and every corresponding
output. A failed head or tail refuses the whole array. Array order and duplicates
are preserved; schema uniqueness is checked later where the original schema
requires it. Objects with unique fields may reorder those fields without changing
the decoded result. No source field or array item is silently dropped, sorted,
trimmed or deduplicated.

The complete record theorem is:

    decodeRecord(j) = Some(r) iff SchemaAstMeaning(j, r).

SchemaAstMeaning combines the independently specified nested object/field/array
denotation with the previously proved RecordShape constraints. It covers all
fourteen outer fields, all five payload fields and every four-field relation
reference. Its meaning definition does not call decodeRecord. Separate proofs
cover key lookup, required-field presence, unknown and duplicate refusal, object
reordering, array-length preservation, primitive type interpretation, each nested
adapter and the full record composition. Canonical encoding followed by decoding
recovers every typed record field; schema-valid records also pass the final gate.
That theorem preserves typed contents. It does not assert that re-encoding an
arbitrary input preserves original JSON byte formatting or object-field order.

The exact source fixture is read with an object-pairs hook that retains object
entries and lexical number tokens. The generated fixtures keep its original
object order. Eighty-two concrete controls cover missing and wrong-type fields
at every object tier, extra keys, identical/conflicting duplicate keys, invalid
array heads/tails, wrong top-level types, full object reordering, selected-array
order, repeated relation items and permissive schema cases. JSON Schema controls
use Draft202012Validator; duplicate-object cases use the explicit candidate
retained-key rejection policy because an ordinary dictionary would erase them.
The generator and Python byte parser are not formally verified.

Shape-valid controls deliberately include empty evidence, an unverified owner
label, retired lifecycle, empty satisfaction tests, selected/excluded overlap and
a relation-kind/counterpart-kind combination permitted by independent enums.
Their acceptance proves faithful shape projection, not authentic ownership, live
permission, satisfied Intent, valid companion relations or completed work.

Validation requires fresh pinned Lean compilation and separate fresh replay,
per-theorem axiom inspection and matching-phase import-resolution audits.
Preparation compilation is not final verification. Only the standard propext,
Quot.sound and Classical.choice axioms are permitted. Same-kernel replay is not
the mandatory independent checker.

Still required for the full original plan:

- Implement and prove, or explicitly bound in the trust profile, byte-to-AST
  parsing: syntax, UTF-8/escapes, decoded-key identity, retained duplicates, number
  token syntax, trailing input, parser normalization and original byte capture.
- Obtain the parser-profile assessment; preserve exact schema/source identity.
- Define and prove authenticated metadata denotation: node identity, actual owner,
  scope, lifecycle use posture, evidence, challenge route, successors, relation
  companions and claim ceiling in the complete profile/context/snapshot/frame.
- Join the AST/body/bytes with complete non-equivocating owned catalogs and the
  existing guarded payload projection. The same artifact revision must denote
  the exact immutable record across every alias and approval root.
- Refine the exact intent_resolution_ref/addressing_role qualifiers and owned
  Selection companion over all six source/Intent branches. Complete recording
  and protected-state preservation, full-theory outcome countermodels and
  mandatory independent checks.
- Enforce input/resource limits. The finite model and compiler wall-clock timeout
  do not establish production parser/checker resource gates.

All 263 inherited obligations remain pending. Preserve all 90 original discharges,
original scoped R06/G4 acceptance, all 41 kinds/550 pairs, all seven integrations
and the separate successor human use assessment. Whole source refinement,
authenticity, independent proof closure and plan completion remain unproved.

Current validation: complete JSON-AST projection component verified. Fresh pinned
compilation and separate fresh replay pass all 117 new declarations: 35 general
lemmas and 82 concrete controls. All 58 compiler invocations succeed, with
396 axiom inspections including dependencies. All 58 matching-phase import
audits pass. The preparation match-splitting failure is retained under
repair-attempts/01; the final reports bind the repaired sources. Byte parsing,
parser-profile assessment, authenticated metadata, whole K02 source/theory
refinement and mandatory independent checking remain open. No inherited
obligation is discharged and N01 is not accepted.
