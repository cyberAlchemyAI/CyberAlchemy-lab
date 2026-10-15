# Scalar conversion definition before implementation

The raw JSON grammar retains UTF-16 units; the binding AST stores Lean scalar
strings. The conversion is a separate partial interpretation. Raw grammar success
must not be mistaken for successful scalar interpretation.

An independent `UnitCharsMeaning(units, chars)` has three constructors: empty;
one BMP scalar unit followed by a meaningful tail; and a valid high/low surrogate
pair followed by a meaningful tail. BMP scalar units exclude the surrogate range.
A pair denotes the scalar `65536 + (high - 55296) * 1024 + (low - 56320)`.
`StringMeaning(units, text)` means these independent characters equal `text.toList`.
No normalization, replacement characters, case folding or duplicate-key erasure
is part of this meaning. NUL and other escaped control scalars remain representable.

The implementation target is `decodeString(units) = some(text)` iff
`StringMeaning(units, text)`. None means no scalar-string interpretation exists;
it is not a claim that the original raw JSON document is malformed. Unpaired
surrogates, wrongly ordered surrogate units and units beyond 16 bits have no
interpretation in this converter. The raw grammar continues to admit escaped
unpaired units. The supported interpretation is not yet an accepted owner profile.

A subsequent independent recursive `ValueMeaning(raw, scalar)` must preserve all
six AST constructors, exact number lexemes, array order, ordered object entries
and every decoded key/value; it must fail if any nested string/key lacks meaning.
Duplicate decoded keys remain visible and are refused separately by the existing
closed binding-object checker. Conversion does not itself qualify any relation,
Schema, source digest, authentic owner review or semantic policy.

Quantified soundness/completeness, unique interpretations, explicit refusal and
source-to-AST composition precede any source-policy or inherited closure claim.
This definition neither accepts K04/D01–D08 nor discharges any inherited ID.
