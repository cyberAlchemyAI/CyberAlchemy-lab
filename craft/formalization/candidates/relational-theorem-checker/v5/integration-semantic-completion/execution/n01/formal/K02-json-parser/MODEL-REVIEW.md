# Recursive JSON parser: implementation review

The full raw JSON parser is now implemented, including nested arrays/objects,
root whitespace, complete input consumption and UTF-8 composition. The
primitive dispatcher is proved exact against independent meanings. Recursive
container/document grammar soundness, completeness and sufficient fuel remain
unproved; finite passing documents do not discharge those targets.

| Layer | Concrete implementation | Current evidence |
|---|---|---|
| Boundary | Allow end, JSON whitespace, comma, closing bracket/brace | Quantified exactness against independent `FollowsValue` |
| Primitive | Dispatch string, lowercase literal or original number token | Quantified soundness/completeness, unique value/suffix, progress and original grammar bridge |
| Array body | Empty/nonempty bodies; scan whitespace; require comma or closing bracket; disallow empty body after comma | Structural termination and worked controls; full `ArrayBodyMeaning` refinement remains required |
| Object body | Quoted key, colon, value, comma/closing brace; no empty body after comma | Structural termination and worked controls; full `ObjectBodyMeaning` refinement remains required |
| Value | Primitive, array or object; qualify suffix | Implemented for all raw constructors; full `BoundedValuePrefixMeaning` refinement remains required |
| Document | Skip leading whitespace, parse value, skip trailing whitespace, require no remainder | Implemented; full `DocumentMeaning` exactness remains required |
| Bytes | Complete proved UTF-8 decoding followed by document parser | Exact composition with the implemented parser is proved; `ByteDocumentMeaning` exactness still depends on document adequacy |

The independent meanings precede implementation and reuse the already registered
`ValueMeaning`, `ItemsMeaning`, `MembersMeaning`, `StringMeaning` and number grammar.
Body meanings consume the exact closing delimiter. Their bridges back to original
value grammar are proved. They do not define meaning as parser success.

Every mutually recursive call decreases fuel, which Lean checks when accepting
the definitions. The wrapper chooses `2 * input.length + 1`. Structural termination
proves computation ends; it does not prove this budget is sufficient for every
meaningful input. That sufficiency proof is an explicit remaining target. Internal
fuel exhaustion currently shares `none` with syntax refusal; the future public
API must distinguish resource/profile outcomes and grammar failures.

The primitive dispatcher closes a real integration gap: token-prefix decoders
can return `true` from `truex` or `1` from `1abc`. Boundary qualification now refuses
those suffixes as values, while keys use the separate quoted-string/colon path.
A comma or closing delimiter is still only a prefix boundary. The containing
parser must place it correctly, and the root parser requires complete consumption.

Raw object entries remain ordered. `{"k":null,"\u006b":true}` produces two entries
with key units `[107]`; no deduplication or last-write selection occurs. The future
binding-schema layer must refuse duplicate decoded keys where required. Number
lexemes remain exact. Escaped unpaired surrogates remain UTF-16 units, including
`"\uDEAD"` → `[57005]`; scalar-string AST conversion cannot silently replace them.
The syntax/representation basis is [RFC 8259](https://www.rfc-editor.org/rfc/rfc8259),
with standard-to-formal-meaning translation still a separate requirement.

The byte wrapper performs no BOM cleanup. The candidate grammar does not treat
U+FEFF as JSON whitespace, so a leading BOM is refused. RFC 8259 permits parsers
to ignore an incoming BOM; optional tolerance remains a profile decision and
must not be inferred from this candidate. Profile-owner acceptance remains open.

Preparation review resolved exact string-prefix list associativity before
primitive composition. One BOM control needed a larger Lean elaboration recursion
limit to reduce the concrete expression. This setting applies to proof elaboration,
not to runtime/parser fuel or a measured supported envelope. Failed preparation
logs are retained outside passing evidence. Final sources contain no admitted
proof, native proof shortcut or custom axiom.

Remaining requirements, starting with formalization:

1. Prove mutual soundness for value/array-body/object-body modes against existing
   meanings, including nonempty output when the post-comma empty-body flag is false.
   Prove exact whitespace reconstruction, separator placement and source suffixes.
2. Prove grammar completeness with a sufficient consumed-length fuel bound.
   Derive wrapper budget adequacy and deterministic raw meanings. Do not weaken
   the independent grammar to the finite corpus or parser's successful inputs.
3. Prove whole-document exactness, including arbitrary legal root whitespace,
   then derive exact `ByteDocumentMeaning` from the UTF-8 composition theorem.
4. Formalize supported UTF-16-to-scalar AST conversion and explicit unsupported
   representation outcomes; preserve number lexemes, object order and duplicates.
5. Join actual source bytes to binding records and retained catalog stages.
   Realize digest computation, owned profiles, Schema semantics, authentic review
   providers and all nineteen K02 source policies.
6. Implement useful public diagnostics/outcomes, measure runtime limits, complete
   original relation/effect/theory proofs and mandatory independent checking.
   Audit exact inherited IDs and run all seven extensions plus final actual new use
   assessment under the existing full twenty-task plan.

All 263 inherited IDs remain pending; all 90 original discharges retain their
scope. K00–K03 actual meanings retain scope, while K04 and D01–D08 remain pending.
N01 is in progress, N02/N03 unstarted and only N00 accepted. Candidate parser
implementation/proofs do not freeze N03, authenticate a capture or finish the
41-kind/550-pair/seven-extension plan.

Fresh verification passes 101 candidate declarations (18 general/interface/composition
results and 83 worked controls) through 44 compile/replay invocations, 470
dependency-inclusive axiom inspections and 44 matching-phase import audits.
Only allowed standard axioms occur. Compilation/elaboration took
38.164 seconds total and 1.930 seconds for the maximum module;
these are not runtime limits. All 62 full-document reference cases agree, with
21 additional byte/scalar/boundary controls. Same-kernel replay and reference
comparison are not independent proof checking. Complete recursive grammar
soundness/completeness and budget sufficiency remain unproved.
