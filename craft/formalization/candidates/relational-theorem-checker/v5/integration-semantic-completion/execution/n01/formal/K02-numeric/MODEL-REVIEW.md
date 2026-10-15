This package formalizes exact epoch-number meanings before implementing the full
binding-frame parser. It proves structured evaluation and a full-token witness
check. A total raw-number-token parser is still required; this package does not
close the frame, binding-record, byte-parser, authentic-source or inherited obligations.

JSON permits different spellings of the same integer value: 42, 42.0, 4.2e1 and
420e-1 all denote epoch 42. Negative zero denotes epoch zero. Conversely, 0.5 and
42e-1 are numbers but cannot be natural epochs. Restricting epoch tokens to bare
decimal digits would reject valid schema values. Rounding decimals to a machine
float can accept a fraction or substitute a different epoch. Both changes would
alter the intended meaning.

The independent representation has a negative-sign flag, an integer digit list,
an optional fraction digit list and an optional exponent. The exponent retains
uppercase/lowercase marker, unsigned/plus/minus sign and its digit list. Each digit
is a mathematical natural less than ten. The integer list must be nonempty and
cannot start with zero unless it is exactly [0]. Present fractions and exponents
must have at least one digit. Exponents may contain leading zeros. Top-level plus,
Unicode digit substitutes, whitespace inside a token and missing digits are not
part of the number grammar.

The grammar itself is a proposition over ASCII character lists: an optional minus,
an integer word, an optional period plus nonempty digit word, and an optional e/E
plus optional exponent sign and nonempty digit word. It does not call a parser.
Valid structured representations spell words in that grammar. A successful AST
witness check therefore implies valid JSON-number grammar, and any token outside
that grammar refuses every representation witness. The converse representation
existence/uniqueness and a complete executable token parser remain to be proved.

Let m be the integer digits followed by the fraction digits, f the fraction length,
p the positive exponent magnitude and q the negative exponent magnitude. Define:

    N = m × 10^p
    D = 10^(f + q)

The signed decimal value is N/D with the retained negative sign. The independent
epoch meaning requires valid grammar components, a nonnegative sign (or N = 0),
and N = epoch × D. This proposition calls neither division, remainder nor decoder
success. D is strictly positive. The multiplication equation gives a unique epoch
for each fixed representation. All arithmetic uses unbounded natural numbers;
there is no floating-point approximation or fixed-width overflow.

The proved evaluator equivalence is:

    decodeParts(parts) = Some(epoch) iff EpochMeaning(parts, epoch)

The evaluator validates grammar components first. A zero mantissa returns zero
before constructing exponent powers. Otherwise, a negative sign refuses, and a
nonnegative number returns its quotient only if the remainder is zero. The
zero-mantissa shortcut is proved equivalent to the independent exact meaning.
It does not skip validation: a malformed zero representation still refuses.
Computing a mantissa with a very long fraction or a nonzero value with an enormous
exponent can still be expensive; no supported resource envelope is established.

The AST entry point also requires the number token to equal the exact spelling of
the supplied representation. It proves:

    decodeWitness(ast, parts) = Some(epoch) iff
      ast = Number(spelling(parts)) AND EpochMeaning(parts, epoch)

This is a checked representation witness, not a token-to-representation parser.
It grants no authority or source authenticity. It can refuse a valid number when
given a different representation witness. For example, token 43 with the witness
for 42 refuses, while a parser should produce the witness for 43. The full parser
must supply that witness itself and prove exact lexical refinement; a caller's
unverified representation or success flag is not a substitute.

Forty-six worked proof controls cover ordinary integers, integral decimals,
positive/negative/unsigned exponents, uppercase markers, exponent leading zeros,
negative zero, nonintegral or negative values, exact values beyond binary-float
integer precision, malformed component shapes, exact token substitutions and
non-number AST types. Two controls use zero mantissas with trillion-sized exponent
magnitudes and pass without constructing those exponent powers. The concrete
controls do not establish a general resource bound or complete token-parser coverage.

The separate 39-case Python reference audit uses exact Decimal values and confirms
the explicit epoch subschema is integer with minimum zero. Its generator and
reference parser are not proved. Wrong-witness cases are explicitly separated
from malformed tokens. The audit initially conflated surrounding JSON document
whitespace with number-token syntax; that comparison was corrected and recorded.
The Lean number grammar and proof sources were unaffected by that correction.

A concrete translation hazard was reproduced: default Python JSON decoding rounds
42.0000000000000001 to 42.0, after which the integer schema validator accepts it.
The exact reference and Lean witness checker refuse the original fractional token.
A future byte parser must preserve the original number lexeme and prove its exact
value bridge. This observation concerns this Python decoding path, not every JSON
library and not the already accepted original checker's complete behavior.

Next required work: prove token representation completeness and uniqueness and a
complete executable numeric-token parser; compose its result with all eight Frame
fields and the closed binding body/record; prove the full schema/AST and original
byte/capture/digest bridge; realize authentic providers and all nineteen source
semantic policies; integrate the parsed bindings into K02; complete public outcome
classification and measured limits; prove whole-source/effect/theory closure and
run mandatory independent checking. All 263 inherited IDs remain pending, and the
90 original discharges retain scope. K04/global assessments remain pending.

All 68 new declarations passed 10 fresh pinned compile/replay invocations and
152 dependency-inclusive axiom inspections. All 10 matching-phase import audits
passed, with only the allowed standard axioms and no placeholder/native proof
shortcut. Compile/elaboration took 25.992 seconds in total; the maximum module
was 3.81 seconds. These compiler timings are not runtime resource limits.
The 39-case exact Decimal comparison and float-translation counterexample passed
separately. Same pinned-kernel replay is not mandatory independent checking.
