Exact interpretation of the two pinned source pattern forms

The seven complete schemas contain only two distinct pattern expressions: \S
and the fixed twenty-character UTC timestamp shape. The installed Python regex
backend accepts Unicode decimal digits for \d and permits a final LF under $.
Its whitespace class also differs from ECMAScript. These are observed behavior
differences, not evidence that the original schema owners intended a new policy.

JSON Schema's pattern guidance names ECMA-262:
[validation 6.3.3](https://json-schema.org/draft/2020-12/json-schema-validation#name-pattern).
The exact digit, whitespace and anchor behavior is specified by
[ECMAScript regex semantics](https://tc39.es/ecma262/multipage/text-processing.html#sec-runtime-semantics-compileassertion)
and [character-class escapes](https://tc39.es/ecma262/multipage/text-processing.html#sec-compiletocharset).

For the supported scalar strings, NonWhitespace(s) means that some character's
code point is outside {9,10,11,12,13,32,160,5760,8192..8202,8232,8233,8239,
8287,12288,65279}. The pattern is unanchored: one non-whitespace character is
sufficient. Do not replace this with Python str.isspace or ASCII-only whitespace.

TimestampShape(s) means length exactly twenty; positions 4 and 7 are '-', 10 is
'T', 13 and 16 are ':', 19 is 'Z'; every other character is one of ASCII 0..9.
No final newline is accepted. This is the original regex shape, not calendar
validity, a trusted clock, freshness, or proof that the claimed instant occurred.

Implement these two meanings explicitly and retain the original schema text and
all other assertions. Refuse unrecognized pattern forms rather than silently
using a different dialect. Compare the scalar whitespace set exhaustively against
the local ECMAScript engine, and compare timestamp boundary/mutation examples.
These checks do not independently verify Lean proof closure or establish a general
JSON Schema theorem. The later proved Decoder still requires exact correspondence
to the retained raw AST and full source semantics.
