# Exact JSON string decoding: implementation review

This candidate closes the string-decoding implementation gap beneath K02's
binding-record AST. It does not close the original relation, its inherited
obligations, or the full integration plan.

The existing independent `StringUnitMeaning`, `StringContentMeaning` and
`StringMeaning` define the meaning. This package implements decoders and proves
soundness and completeness against those pre-existing definitions. The
specification is not an equality with the decoder's own result.

| Layer | Implemented behavior | Verified relationship |
|---|---|---|
| Hexadecimal | Decode ASCII 0–9, a–f and A–F | Exact `HexMeaning`; four digits retain the numerical UTF-16 unit |
| Simple escapes | Decode the eight JSON escape codes | Exact `SimpleEscape`; an unknown code fails |
| String unit | Decode one raw Unicode scalar or one escape | Exact consumed word and remaining scalar input; progress and 16-bit unit bounds |
| Content scanner | Read units until the first unescaped quote | Exact independent content meaning and suffix; input-derived fuel is sufficient for all finite meaningful content |
| Quoted prefix | Consume opening/content/closing quotes | Exact `StringMeaning` for the consumed prefix; units and suffix are unique |
| Whole string | Require no remaining scalar input | Exact `StringMeaning` for the complete input |
| UTF-8 composition | Decode the complete bytes, then the whole string | Exact independent UTF-8 stream plus complete string meaning |

`decodeQuoted` returns decoded UTF-16 units and the exact remaining scalar
input. `decodeString` requires complete consumption. `decodeStringBytes`
recognizes a complete quoted string token in UTF-8. Whitespace around a value
belongs to the future document parser; these entry points do not silently trim
it. Original spelling is available in the unchanged input and the exact
consumed-prefix meaning; these APIs do not return a separate lexeme field or
replace the capture envelope's original bytes.

The scanner derives sufficient fuel from input length. Its finite-input
completeness proof excludes a false rejection caused solely by this internal
fuel. This is not a measured execution envelope or an implemented public
resource-limit outcome.

The raw meaning retains unpaired escaped surrogates. For example, `"\uDEAD"`
decodes to `[57005]`. Raw surrogate code points are refused. Literal `𝄞` and
`"\uD834\uDD1E"` decode to `[55348,56606]`; literal `k` and `"\u006b"` decode
to the same key unit. Consequently the future object parser must retain entries
before checking duplicate decoded keys. Replacement, case folding and Unicode
normalization are absent. The distinction between JSON syntax and Unicode
interoperability is described in [RFC 8259, sections 7–8](https://www.rfc-editor.org/rfc/rfc8259).

Implementation review found and resolved these local proof issues: option
composition needed explicit bind forms, exact suffix expressions needed list
associativity normalization, and whole-input consumption needed transport of
both units and the empty suffix. Failed preparation logs are retained and are
not verification evidence. Final sources contain no admitted proof or native
proof shortcut.

Remaining requirements are concrete:

1. Implement literals, numeric prefix recognition, whitespace, arrays, objects
   and whole documents against the already registered independent grammar.
   Preserve original number lexemes and ordered duplicate decoded object keys.
2. Formalize scalar-AST conversion and its unsupported-representation outcome
   before implementing it. Raw unpaired UTF-16 units cannot silently become a
   scalar `String`, and syntactic validity must not be relabeled as invalid JSON.
3. Connect actual captured bytes through the complete parser and conversion to
   binding-record decoders. Realize digest computation, owned profiles, schema
   semantics, authentic review roots and K02's nineteen source policies.
4. Add distinct public outcomes and measure runtime resources; prove complete
   relation/effect/theory closure with mandatory independent checking.
5. Continue the actual K04–K40 owner review and D01–D08 assessments. Candidate
   proofs do not substitute for those assessments or discharge inherited IDs.

All 263 inherited IDs remain pending; all 90 original discharges keep their
original scope. K00–K03 meanings have actual scoped acceptance. K04 and global
policies remain pending. N01 is in progress; N02/N03 are not started and only
N00 is accepted. All seven extensions, 41 kinds, 550 endpoint pairs and the
final new bounded-use assessment remain in the plan.

Fresh verification passes 82 new declarations (27 general results and 55 worked
controls), through 30 compile/replay invocations, 316 dependency-inclusive axiom
inspections and 30 matching-phase import audits. Only allowed standard axioms
occur. Fresh compilation/elaboration took 25.491 seconds total,
with a 2.156-second maximum module. These are not runtime resource limits.
All 36 strict string reference cases match; 19 additional controls cover exact
suffixes, invalid scalar inputs and UTF-8 composition. Same-kernel replay and
Python comparison are not independent proof checking. Full document parsing,
scalar-AST conversion and authenticated source closure remain open.
