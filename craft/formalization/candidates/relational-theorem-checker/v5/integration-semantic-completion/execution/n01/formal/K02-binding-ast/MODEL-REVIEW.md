This package closes the AST decoding gap for the revision references and the two
binding target structures. It is a candidate component of N01; it does not
complete N01, freeze an N03 schema, or discharge an inherited obligation.

The resolution binding selects an exact seven-field Resolution: its own revision,
scope, intent, owner decision, selected subjects, excluded subjects and satisfaction
tests. The role binding selects an exact three-field Role: revision, code and
subject kind. Losing any field would change what the later source/Selection join
checks. These decoders retain each field and preserve reference array order and
repetitions. They do not substitute a caller's abbreviated target or a reference
key without its digest.

The independent mathematical meanings describe retained JSON AST entries and
ordinary typed values. A nonempty string means the AST is that exact string and
that string differs from the empty string. A closed object means unique raw entry
keys, no additional entries, and every required field represented in schema order.
A field product conjoins its component meanings. Mapping the product to a typed
record states equality of every mapped field. An array states the ordered element
meaning recursively, including the empty array. None of these propositions calls
the corresponding decoder, lookup or success flag. The Decoder/Fields structures
carry both the meaning and the proof relating an executable decoder to it.

The principal results are:

    key.decode(ast) = Some(k) iff KeyMeaning(ast, k)
    reference.decode(ast) = Some(r) iff ReferenceMeaning(ast, r)
    role.decode(ast) = Some(role) iff RoleMeaning(ast, role)
    resolution.decode(ast) = Some(resolution) iff ResolutionMeaning(ast, resolution)

Additional field-characterization theorems expose the three Role fields and all
seven Resolution fields as exact constituent meanings. Revision owner/artifact/
revision and digest strings must be nonempty. Role codes must be nonempty. The
subject-kind decoder covers the exact seven draft enum strings, including other.
Array decoding preserves the original AST element count. Generic object theorems
refuse duplicate keys and extra fields before field lookup.

Twenty worked proof controls use the target and revision-key content of the two
existing draft binding fixtures. They cover successful original decoding, permitted
object-key permutation, empty reference components, an extra approval field,
identical repeated digest keys, a missing digest or owner decision, empty role
code, an unlisted subject kind, a malformed array element, and array order and
repetition preservation. The Python generator translating fixture content to
Lean literals is not proved; its exact input and output files are evidence-bound.
The proofs concern those explicit AST literals and typed outputs, not an asserted
byte-parser translation or authentic owner record.

The syntax/semantic boundary matters. A Role with kind other is allowed by the
draft syntax but cannot qualify an addresses-intent source. An empty selected
list, or a repeated selected subject, can satisfy the target syntax while failing
selection or distinctness in the relation meaning. The draft JSON schemas have
neither minItems nor uniqueItems on these arrays. Adding those constraints in
this decoder would silently change the schema. Ownership, selection, exact full
frame and root authenticity remain the responsibility of subsequent joins and
provider policy proofs.

The source-shape audit compares all revisionKey, revisionRef and target schema
objects exactly against the implemented profile and checks key/enum spellings
in the actual candidate sources. Six comparisons and seven numeric boundary
cases pass. This Python comparison is useful drift evidence; it is not a formal
interpretation of the JSON Schema language or a proof of schema-to-Lean translation.
The compiled equivalence is between the independent local AST denotations and
these decoders. Whole binding schema/AST correspondence remains open.

The frame and enclosing binding record are the next required formalization.
In particular, JSON Schema's integer/minimum-zero epoch accepts integral decimal
or exponent spellings and negative zero. A digits-only spelling decoder would
miss valid values such as 42.0 or 4.2e1. The next number model must formalize JSON
number grammar and its exact decimal value, then require a nonnegative integral
value. Resource bounds must be handled explicitly; floating-point rounding and
silent overflow must not become epoch semantics.

After frame and record AST decoding, the remaining requirements are original-byte
parsing, external digest/capture correspondence, authentic root and World/Selection
providers, all nineteen source semantic policies, full pipeline integration,
public invalid/unknown/unsupported diagnostics and a measured resource envelope,
complete-rule effect preservation and complete-theory countermodels, and mandatory
independent checking. Same pinned-kernel replay is not independent checking.
All seven K02 IDs and the complete set of 263 inherited IDs remain pending.
The 90 original discharges retain their earlier scope. K04 and global policy
assessments remain pending; no acceptance is inferred from this implementation.

Fresh verification passed all 39 new declarations through 20 pinned compiler/replay
invocations and 214 axiom inspections, including dependency declarations. All 20
matching-phase import audits passed. Total compile/elaboration time was 63.595
seconds, with a 6.264-second maximum module; these are not runtime resource limits.
Only the standard allowed axioms occur, with no proof placeholder or native
proof shortcut. Twenty worked controls are included in the 39 declarations.
The source-shape/numeric audit is separate executable evidence, not a proof.
