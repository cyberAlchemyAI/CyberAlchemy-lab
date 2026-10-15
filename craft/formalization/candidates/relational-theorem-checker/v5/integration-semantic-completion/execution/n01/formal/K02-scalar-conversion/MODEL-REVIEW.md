# Scalar conversion and byte-document review

The raw parser's output can now be converted into the existing scalar-string AST
with an exact, independent meaning. The composed byte parser succeeds precisely
when an original byte document has a raw grammar meaning and that raw result has
a scalar AST interpretation. This closes the representation-conversion gap; it
does not authenticate a source or qualify a relation.

The central theorem is `scalar_byte_document_exact`:

```text
parseScalarDocumentBytes(bytes) = some(value)
    iff exists raw,
      ByteDocumentMeaning(bytes, raw) and ValueMeaning(raw, value)
```

`ByteDocumentMeaning` is the existing independent UTF-8/raw JSON grammar.
`ValueMeaning` is newly defined independently of the converter. Its six value
constructors preserve null, booleans, exact numeric tokens, interpreted strings,
ordered arrays and ordered object entries. The list/member meanings recurse on
all entries rather than filtering out unsupported values.

## Three layers and their guarantees

1. **String interpretation.** An ordinary BMP scalar unit denotes its character;
   a high/low surrogate pair denotes the corresponding supplementary scalar.
   Exactness holds for all finite Nat-unit lists. The converter checks 16-bit and
   surrogate bounds before creating a character. Unpaired or wrongly ordered
   surrogates have no interpretation; no replacement-character recovery occurs.
2. **Structural AST interpretation.** Soundness/completeness and unique converted
   values hold for every raw AST. All number spellings remain exact. Arrays and
   object entries retain order and length. An unsupported nested value or key
   refuses conversion of the whole document.
3. **Original byte-document composition.** Raw parser exactness composes with
   structural conversion exactness. `classifyBytes` has three proved outcomes:
   invalid syntax iff no raw grammar meaning; unsupported scalar representation
   iff the exact raw meaning exists but has no scalar AST interpretation; and
   converted iff the independent composed meaning exists.

## Worked distinctions

An escaped unpaired high surrogate is accepted by the raw grammar and produces
an unsupported scalar representation. A malformed UTF-8 byte inside a quoted
string produces invalid syntax. A valid surrogate pair produces one scalar;
escaped NUL and controls remain representable. No normalization is performed.

The document `{"a":null,"\u0061":true}` converts to two ordered entries with the
same decoded key `a`. Conversion retains both. The existing closed binding-object
checker refuses the duplicate key separately; raw grammar success does not imply
binding-record acceptance. This example checks an actual original byte document.

The implementation uses structural termination measures for nested values and
lists. No new arbitrary depth cutoff is inserted in the converter. This is a
termination proof for the formal implementation, not a measured stack, latency
or memory bound for a deployed service.

## Scope of the evidence

There are 52 general declarations and 43 finite controls. Of the controls, 34 use
Python strict UTF-16 decoding as an independent finite reference, covering BMP
boundaries, paired supplementary scalars, lone/reversed surrogates, out-of-range
units, controls and mixed valid/invalid tails. The quantified Lean proofs provide
the general conversion and byte-composition guarantee; the reference corpus does
not substitute for them or certify an external standard profile.

Fresh verification results and exact import audits are recorded alongside this
review. Same-kernel replay does not satisfy mandatory independent closure checking.

## Remaining gaps and the next dependency

The public representation classifier is implemented and proved in this candidate;
the full checker API, source-policy diagnostics and resource outcomes are still
open. No original captured binding fixture is parsed/authenticated by this package.
Source envelopes still need computed digests, owned profiles, complete Schema
correspondence and authentic review/evidence providers. Nineteen K02 source policies
remain unrealized. External-standard translation and measured runtime qualification
remain separate work. Original semantic/effect/whole-theory obligations and their
mandatory independent checking remain open.

Next, formalize and compose this exact byte-to-scalar parser with the existing
complete field-preserving binding-record decoder and retained source envelope.
Keep syntax, unsupported representation, schema refusal and missing/authenticity
policy evidence as distinct outcomes. Then realize the exact source policies.

All 263 inherited IDs remain pending; all 90 original discharges retain scope.
K00–K03 meanings remain accepted separately; K04 and global D01–D08 are pending.
N01 remains in progress, N02/N03 unstarted and only N00 accepted (1/20). This package
freezes no successor API and does not complete the full seven-extension plan.

Fresh verification passed 68 compilation/replay invocations, 620 dependency-inclusive
axiom inspections and 68 matching-phase import audits, for all 95 new declarations.
Only permitted standard axioms occur. Proof compilation/elaboration took
48.099 seconds total with a 1.978-second maximum
module. These timings are not a measured parser runtime envelope.
