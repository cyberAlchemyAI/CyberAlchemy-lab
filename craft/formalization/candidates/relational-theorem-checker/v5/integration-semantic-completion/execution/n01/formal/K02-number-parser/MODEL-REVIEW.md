This package closes the raw-number-token parser gap identified by K02-numeric.
The epoch decoder constructs its own exact lexical representation; it no longer
requires a caller-supplied representation witness. This is a verified N01 candidate
component, not a full binding-record parser, source authentication or inherited
obligation discharge.

The parser separates two questions. First: is this complete token a JSON number?
Second: does its exact value represent a nonnegative integer epoch? Thus 0.5 has
valid number syntax but no natural epoch, while 42garbage has invalid number syntax.
Both currently produce None at the pure epoch interface; the final public diagnostic
classification remains to be implemented. Neither refusal establishes anything
about ownership or the intent relation itself.

The executable scanner consumes ASCII digits and retains the first remaining
character. The candidate parser then records an optional minus, integer digits,
an optional fraction, and an optional e/E exponent with optional plus/minus sign.
It preserves those spellings instead of normalizing them through a host float.
A mandatory final check validates all component grammar rules and reconstructs
the exact complete retained character list. A partially scanned prefix cannot
qualify a token with ignored suffixes or extra punctuation.

The independent Representation meaning says that the structured parts satisfy
integer/fraction/exponent digit rules and spell exactly the original characters.
It does not call the scanner, parser or an executable success flag. Integer digits
are nonempty and have no leading zero except the single zero. Fractions/exponents,
when present, contain at least one digit. Exponent leading zeros, e/E, plus/minus
exponent signs, decimals, and negative zero are preserved.

The principal lexical results are:

    parseChars(chars) = Some(parts) iff Representation(chars, parts)
    NumberGrammar(chars) iff there exists parts with parseChars(chars) = Some(parts)
    Representation(chars, a) AND Representation(chars, b) implies a = b

The proofs cover all finite character lists, not just the concrete corpus.
Completeness constructs digit, integer, fraction and exponent representations
from the independently stated ASCII grammar. Reconstruction of every valid
representation proves that parsing does not narrow the grammar. Determinism plus
that reconstruction proves uniqueness of the complete lexical representation.
No claim relies on accepting only canonical decimal-digit spellings.

The parsed parts feed the earlier exact rational-value equation N = epoch × D,
with positive denominator and unbounded natural arithmetic. The independent token
meaning existentially states exact representation and that value equation. The
new arithmetic/AST equivalences are:

    decodeTokenEpoch(token) = Some(epoch) iff TokenEpochMeaning(token, epoch)
    decodeEpochAst(ast) = Some(epoch) iff AstEpochMeaning(ast, epoch)

The AST meaning requires a number AST containing that exact token. String, boolean,
null, array and object ASTs cannot become epochs. The epoch is unique for a fixed
token. The new epochAdapter carries this decoder, its independent meaning and
its exactness proof for reuse by the Frame object decoder.

The previously exposed numeric cases now use only the raw token. Tokens 42, 42.0,
4.2e1 and 420e-1 produce 42; negative zero produces zero; a fractional residue such
as 42.0000000000000001 refuses. Token 43 produces 43, fixing the prior witness-only
interface's inability to qualify it when supplied with the representation for 42.
The large exact decimal 9007199254740993.0 retains that exact integer instead of
rounding it to 9007199254740992. The zero-mantissa shortcut remains in the evaluator,
so the demonstrated zero values with trillion-sized exponent magnitudes do not
construct those exponent powers.

Fifty-three worked proof controls include 46 raw numeric cases, non-number AST
refusals, equivalent spelling results, syntax-valid fractional parsing, independent
meaning and adapter composition. They cover ignored suffixes, second exponent or
period, missing digits, leading zeros, leading plus, Unicode digit substitutions,
line-break/space tokens, negative values, decimal/exponent integers and precision
boundaries. The separate exact Decimal audit is executable source/corpus evidence,
not a proved generator, schema interpreter or independent proof checker.

This parser consumes a number token already represented as a Lean String. It does
not tokenize UTF-8 bytes or parse a complete JSON document. Leading document
whitespace may be legitimate for a whole JSON parser; it is not part of a number
lexeme. The future byte parser must extract and preserve the exact number token
and prove the byte/token/AST bridge. Full draft-schema interpretation is also
separate: the local mathematical epoch domain and exact source-shape comparison
do not constitute a proved interpreter for every JSON Schema feature.

Formal totality over finite input does not establish a supported runtime envelope.
Very long digit lists/fractions or large nonzero exponents may be expensive, and
native stack/memory limits still require measurement and explicit public limit
outcomes. Compiler timings are not those resource measurements. No profile-owner
acceptance or N03 API/schema freeze is inferred here.

Next: compose the proved epoch adapter with all eight Frame fields, then the
closed binding body and enclosing resolution/role records. Preserve every exact
version/kind/revision/token/target/frame/owner-review field and duplicate-key refusal.
Then establish full schema and byte/digest/capture correspondence; realize authentic
providers and all nineteen source policies; integrate parsed bindings with the
K02 source/Selection pipeline; implement public diagnostics/resources and complete
whole-source/effect/theory plus mandatory independent closure checking. All 263
inherited IDs remain pending, the 90 original discharges retain scope, K04/global
review remains pending, and the complete 41-kind/seven-extension plan remains active.

Fresh verification passed all 84 new declarations, including 53 worked controls,
through 22 pinned compile/replay invocations and 254 dependency-inclusive axiom
inspections. All 22 matching-phase import audits passed. Only the allowed standard
axioms occur; no placeholder or native proof shortcut is used. Compile/elaboration
took 54.459 seconds total, with a 13.236-second maximum module. These are not
runtime limit measurements. The 46-case exact Decimal audit passed separately.
Same pinned-kernel replay is not mandatory independent proof checking.
