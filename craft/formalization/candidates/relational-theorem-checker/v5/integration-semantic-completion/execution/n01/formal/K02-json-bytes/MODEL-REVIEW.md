K02: exact UTF-8 decoding and independent complete JSON document meaning

The source bridge needs a proved connection from original bytes to the retained
binding-record AST. This component implements and proves the complete UTF-8 layer
and defines the independent complete JSON document meaning needed for the next
parser. It does not yet implement or prove the full JSON string/value/document
parser, convert its raw values to the existing checker AST, authenticate captures
or discharge any inherited obligation.

What changed

Previously, a capture supplied both bytes and an AST, while the relationship
between them remained an unrealized policy predicate. The new encoding decoder
reads actual UInt8 byte sequences and returns exact natural Unicode scalar values.
It checks shortest-form one-, two-, three- and four-byte encodings, continuation
ranges, surrogate exclusion and the maximum scalar boundary.

Its independent WordMeaning specifies a valid encoded word and its numerical
value; StreamMeaning joins those words until all original bytes are consumed.
Neither meaning calls the implementation. The principal theorem is:

    decodeUtf8(bytes) = Some(scalars)
        if and only if
    IndependentUtf8StreamMeaning(bytes, scalars).

A successful prefix decode consumes one to four bytes, returns a valid scalar and
retains the exact remaining suffix. Prefix meanings are unique. The full-stream
proof establishes soundness, completeness and uniqueness; None is equivalent to
absence of any stream meaning. It cannot successfully ignore an invalid suffix.
There is no replacement-character recovery or permissive decoding of overlong
forms, directly encoded surrogates or values above the scalar maximum.

The implementation uses structural fuel, but the public pure function derives it
from byteLength + 1. The proof shows that every valid finite stream completes with
that fuel. This is a termination argument, not a selected input limit or a measured
runtime envelope. Compilation's maxRecDepth setting is also an elaboration setting,
not a parser language/resource restriction.

The document meaning comes before its parser

JsonDocumentMeaning defines all JSON value forms, root values with surrounding
whitespace, arrays, objects, complete number spellings, string units and escapes.
Numbers reuse the already proved complete number grammar and retain their original
String token. Arrays retain order; objects retain the ordered member list, including
all repeated decoded keys. Whitespace is restricted to the four JSON whitespace
codes. The byte-document meaning combines complete UTF-8 stream meaning with the
independent document meaning; its encoding bridge is proved.

The mutual value/member/item grammar defines the syntax rather than evaluating a
parser. Singleton and recursive sequence constructors require an actual next value
or member after each comma, so the grammar does not permit a trailing comma. Empty
containers use separate constructors. Strings begin and end with a quotation mark;
unescaped controls, quotations and reverse solidus are excluded from raw string
units. Simple escapes and exactly four hexadecimal digits have explicit meanings.

An important representation gap

The standards distinguish Unicode scalar encoding from JSON escape syntax. UTF-8
excludes directly encoded surrogate code points. JSON's escape grammar can still
contain an unpaired UTF-16 surrogate, whose interoperability behavior is problematic.
The raw document representation therefore retains UTF-16 units instead of silently
replacing or rejecting that syntax. [RFC 3629 sections 3-4](https://www.rfc-editor.org/rfc/rfc3629#section-3),
[RFC 8259 sections 7-8.3](https://www.rfc-editor.org/rfc/rfc8259#section-7).

For example, an escaped unpaired surrogate has a valid raw ByteDocumentMeaning,
although its decoded unit is not a Unicode scalar. A raw supplementary scalar and
its escaped surrogate pair produce the same retained unit pair. Every resulting
unit is proved less than 65536; raw supplementary scalars are converted to the
correct high/low unit representation. This is a syntax representation choice for
the candidate meaning, not acceptance of a new application profile.

The existing checker AST uses Lean scalar strings. Converting the new raw values
to that AST must therefore be explicit: paired units can become scalar strings;
unpaired units need a specified profile outcome or a representation extension.
They must not be mislabeled as malformed UTF-8, replaced by another character, or
silently excluded while claiming coverage of the full JSON grammar. This conversion
and its owner-approved supported profile remain open. String normalization and
identity equivalence are not added here.

Duplicate decoded keys remain visible

The worked raw grammar includes an object with a literal key and the same key
written with a hexadecimal escape. Both decode to the same unit sequence, and the
object meaning retains both member/value pairs. The parser must preserve them.
The later closed binding-record decoder can then refuse duplicate fields rather
than accepting whichever value a dictionary conversion kept. The full raw-value
to-existing-AST duplicate-preservation bridge is not yet proved.

Worked verification

There are 39 explicit UTF-8 controls, including ASCII bounds, each multibyte width,
both sides of the surrogate range, the scalar maximum, overlong forms, invalid
continuations, truncated words, an invalid suffix, mixed scripts, distinct composed/
decomposed sequences and original large-number ASCII bytes. Their exact outputs
match strict Python UTF-8 decoding in a separate corpus audit. The Python comparison
is engineering evidence, not an independent kernel or proof of standard translation.

Eight additional kernel controls show literal/escaped key meanings, retention of
an unpaired escaped surrogate, its distinction from a scalar, equivalent raw/
escaped supplementary representation, preservation of duplicate decoded keys and
raw byte-document syntax for an unpaired escape. These accompany quantified prefix,
stream, scalar-range, unit-range and encoding-bridge results.

Limits and integration still required

- The complete UTF-8 codec is implemented and exact against its independently
  defined local meaning. JSON string/number-prefix/value/container/document parsing
  still needs implementation and soundness/completeness against DocumentMeaning.
- The document meaning follows inspected primary standards, but no machine proof
  translates RFC prose or Schema documents into these definitions. The meaning and
  Unicode/profile decisions remain candidates, with no new owner acceptance.
- A UTF-8 BOM is a scalar at the encoding layer. Whether a document profile permits
  or ignores it is separate; the decoder does not strip or normalize captured bytes.
- JSON syntax validation, binding schema qualification, semantic ownership and
  authentic source policy are separate checks. A recognized raw document cannot
  grant authority or prove that its digest/review/profile is authentic.
- Original byte-to-existing-AST correspondence, digest computation, authentic
  profile/root/review providers, all nineteen K02 policies, integrated source/
  Selection checks, public outcome classifications and measured resources remain
  pending, along with whole-source/effect/theory and mandatory independent closure.

All 263 inherited obligations remain pending and all 90 original discharges retain
their scope. K00-K03 meanings retain actual acceptance; K04 and D01-D08 remain
pending. Only N00 is accepted (1/20 tasks); N01 is in progress, N02/N03 remain
unstarted. All 41 relations, 550 endpoint pairs, seven extensions and the final
actual new bounded-use assessment remain part of the active full plan.

Fresh verification passes all 67 new declarations (20 general/meaning/encoding
results and 47 worked controls), through 24 compile/replay invocations, 246
dependency-inclusive axiom inspections and 24 matching-phase import audits.
Only allowed standard axioms occur. Fresh compilation/elaboration took
21.354 seconds total, with a 1.666-second maximum module. These timings are
not measured runtime limits. All 39 strict UTF-8 reference cases match.
Same pinned-kernel replay and Python corpus comparison are not independent
proof checking. Full JSON parsing and scalar-AST/source/authentic closure remain open.
