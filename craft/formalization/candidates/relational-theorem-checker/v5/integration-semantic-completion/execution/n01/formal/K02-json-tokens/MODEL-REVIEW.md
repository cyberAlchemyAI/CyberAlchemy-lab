# Exact JSON tokens: implementation review

This candidate closes the whitespace/literal/numeric token-scanning gap below
the pending complete JSON document parser. It reuses the independent document
and number grammar instead of treating scanner output as its own specification.

`RunMeaning` specifies the exact consumed word, its predicate and the first
nonmatching suffix. The generic scanner is proved sound and complete, has a
unique result, and preserves total input length. `scanWhitespace` instantiates
that result for exactly space, tab, line feed and carriage return. Nonbreaking
space and vertical tab are not silently trimmed.

`LiteralMeaning` independently names lowercase `null`, `false` and `true`.
`takeWord` proves exact word consumption. The literal decoder is proved exact
against this meaning, with unique value/suffix, progress and a bridge to the
pre-existing `ValueMeaning`.

`NumberPrefixMeaning` uses the existing independent `NumberGrammar`, exact
original token characters and a suffix that stops the maximal numeric-character
run. The implementation first consumes the entire run of ASCII digits, minus,
plus, decimal point and exponent marker. It then requires the entire run to
satisfy the existing number grammar. Thus `01,`, `1e]`, `1.,` and `1-2,` fail;
none can be qualified by accepting only an earlier `0` or `1`.

The conversion between scalar codes and number characters has proved round-trip
identities. Valid numbers contain only the stated ASCII codes. The number
scanner is proved sound and complete, retains exact lexemes/suffixes, has a
unique result, consumes at least one code and maps into the existing raw number
value meaning. `decodeWholeNumber` additionally requires complete input
consumption and is proved exact against the whole-number meaning. `42`, `42.0`
and `4.2e1` remain different returned spellings. No floating-point conversion or
number normalization occurs here.

A token prefix is not a complete document. `truex` intentionally returns literal
`true` and suffix `x`; `1abc` returns number token `1` and suffix `abc`. The whole
number API refuses the latter. The pending value/document parser must qualify
the suffix. `FollowsValue` now specifies that interface: end of input, the four
JSON whitespace codes, comma, closing bracket or closing brace. Its boundary
is proved to stop a number run, giving completeness for meaningful number
prefixes at every such boundary. Quoted object keys use their separate colon
interface. The forthcoming container parser must check where each separator
is permitted; comma alone does not make a whole document admissible.

The grammar basis is [RFC 8259, sections 2, 3 and 6](https://www.rfc-editor.org/rfc/rfc8259).
The proof is against the registered independent formal meanings; translation
of the standard's prose to those meanings remains a separate requirement.

Implementation review resolved local proof issues around projection of a
conditional pair, transporting only the original input without rewriting its
scanner calls, and proving positive consumed lengths. Literal controls use
kernel reduction directly because the recursive raw JSON type intentionally
has no global equality decider. Failed preparation logs remain outside the
passing verification evidence; no admitted proof or native proof shortcut is
present in final sources.

Remaining work, in dependency order:

1. Formalize the mutually recursive container scanner interfaces and their
   recursion measure against `ValueMeaning`, `ItemsMeaning` and `MembersMeaning`.
   Include exact whitespace, punctuation, empty containers, no trailing comma,
   ordered duplicate decoded keys and complete document consumption.
2. Implement and prove the complete value/array/object/document parser, then
   compose it with the proved UTF-8 decoder against `ByteDocumentMeaning`.
3. Formalize and implement supported scalar-AST conversion with explicit
   surrogate pairing or unsupported-representation outcomes. Raw unpaired
   escaped units must not be replaced or reclassified as invalid JSON syntax.
4. Join actual captured bytes to the binding-record AST and retained catalog.
   Realize digest computation, owned profiles, Schema semantics, authentic
   review roots and all nineteen K02 source policies.
5. Implement distinct public outcomes, measure runtime resource limits and
   prove original relation/effect/theory closure with mandatory independent
   checking. Continue the exact inherited obligation audit and all seven
   integration extensions in the existing twenty-task DAG.

These are N01 candidate results. All 263 inherited IDs remain pending; all 90
original discharges keep their scope. K00–K03 meanings have actual acceptance;
K04 and D01–D08 remain pending. N01 is in progress; N02/N03 are not started,
only N00 is accepted, and the full 41-kind/550-pair plan remains active.

Fresh verification passes 94 new declarations (31 general results and 63 worked
controls), with 32 compile/replay invocations, 340 dependency-inclusive axiom
inspections and 32 matching-phase import audits. Only allowed standard axioms
occur. Compilation/elaboration took 25.055 seconds total and
1.546 seconds for the maximum module; these are not measured runtime limits.
All 38 exact whole-number reference cases agree; 25 further controls bind literal,
number-prefix and whitespace behavior. Same-kernel replay and reference comparison
are not independent proof checking. No inherited ID is discharged.
