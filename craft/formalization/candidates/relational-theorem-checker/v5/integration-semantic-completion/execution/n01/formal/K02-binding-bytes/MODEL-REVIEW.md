# Original byte-to-binding-record and capture review

The new entrypoints derive the complete binding record from the original bytes.
They also prepare retained envelopes and structurally checked catalog stages from
those bytes. Callers cannot pair unrelated bytes with a supplied AST at these new
entrypoints. This closes the byte/AST correspondence gap in the binding preparation
layer; authentication and complete source semantics remain separate requirements.

## The theorem and its implementation

`record_bytes_exact` states:

```text
decodeRecordBytes(version, kind, target, bytes) = some(record)
    iff exists ast,
      ScalarByteDocumentMeaning(bytes, ast)
      and RecordMeaning(version, kind, target, ast, record)
```

Both meanings are independent of the parser/decoder. The first combines the
independent raw UTF-8/JSON grammar and scalar interpretation; the second is the
existing complete field-preserving record meaning. No parser-success premise
stands in for independent membership. The fixed resolution/role byte entrypoints
bind their exact schema-version, kind and target decoder.

`prepare_bytes_exact` additionally checks the submitted envelope, exact frame and
retention of the original envelope. `prepared_bytes_entry_fields` connects all
prepared entry fields to the decoded record and exact original byte content.
`prepared_bytes_retains_capture` connects the submitted byte count to retained
content length. `prepare_bytes_catalog_exact` requires every ordered record/root
capture to have this meaning, aligns the requested digest profile and reuses the
existing structural catalog checks. It retains the full record/envelope stage.

## What each refusal says

Record classification distinguishes malformed raw syntax, a valid raw document
without scalar interpretation, a scalar AST without the complete record meaning,
and a decoded record. Capture classification first checks submitted envelope
fields, then reports the corresponding record refusal, stale exact frame or a
prepared result. The classifier never reports a decoded record as a record refusal.
Three direct capture-refusal theorems state grammar, scalar-support and record
meaning causes without referring to the intermediate record classifier.
All these results have proved independent meanings and agree with the byte
entrypoints on success. Catalog refusal still needs fuller diagnostic integration.

These checks validate submitted digest/profile strings structurally. They do not
compute the digest, authenticate the selected profile or prove issuer ownership.
Digest, owned-profile, Schema and authentic review requirements remain unchanged
when the parse-policy adapter supplies the exact byte interpretation. Conditional
capture construction requires all four of those separate evidence premises.

## Worked original fixtures and the repaired gap

The exact original resolution fixture contains 2621 bytes; the role fixture
contains 1848. The controls prove that these byte sequences parse to explicit raw
ASTs, convert to scalar ASTs and decode into the expected complete typed records.
The fresh verifier compares the UInt8 literals used by the kernel byte-for-byte
with the actual source files and their captured SHA-256 bindings. It does not
substitute a Python-produced AST as the parser input.

For each original record, capture preparation and catalog staging accept the exact
submitted bytes, retain them in the entry and distinguish a stale requested epoch
from an incorrect byte count. The fixtures' identity, digest-profile and review
roots remain explicitly synthetic; the capture digest labels remain uncomputed.
Ground parsing success is not authentic production source evidence.

A concrete regression exposes the old gap: the AST-input preparation interface
accepts a full valid fixture AST paired with unrelated bytes `[1,2]` and a matching
count. The new byte-input interface refuses those bytes. Its parser must interpret
the actual submitted content before record meaning can hold. Additional controls
separate malformed UTF-8, an escaped unpaired surrogate and meaningful JSON `null`
that is not a binding record.

## Verification scope

There are 44 general results and 28 kernel-checked controls, including the two
original fixture byte proofs. General statements cover every finite original byte
input, ordered preparation lists and structurally valid catalog stages; controls
exercise the actual fixtures and refusal/regression examples. Fresh compilation,
replay, axiom and import-resolution results are recorded separately.

Proof-elaboration recursion settings are raised only in large closed fixture
control modules. They do not change the parser, its accepted input domain, runtime
limits or supported deployment profile. Same-kernel replay does not satisfy
mandatory independent closure checking. Typed expectation generation is not
claimed as a general verified JSON-to-Lean translator; the concrete correspondence
is established by the actual closed byte-result theorems.

## Remaining gaps and immediate next work

Computed digests and an authentically selected profile must replace arbitrary
nonempty labels. Full Schema correspondence, authentic issuer/review/evidence
providers and all nineteen complete K02 source-policy obligations remain open.
The parser component now exists, but this does not automatically discharge the
broader `parses` policy under the full owned source contract. Original source/world,
Selection, payload and qualifier joins still need that complete refinement.

External-standard translation, owned parser-profile acceptance, measured resources,
full checker/certificate/diagnostic integration, original relation/effect and
whole-theory closure, and mandatory independent checking remain open. The next
step is formalizing the pinned digest-profile meaning and byte/digest computation
bridge, then implementing it and connecting it to retained capture verification.
Ownership of the selected profile remains an independently evidenced condition.

All 263 inherited IDs remain pending; all 90 original discharges retain scope.
K00–K03 meanings remain accepted in their own scopes; K04 and D01–D08 remain pending.
N01 remains in progress, N02/N03 unstarted and only N00 accepted (1/20). All 41 kinds,
550 endpoint pairs, seven extensions and the new final bounded-use assessment keep
 their required scope. This package does not freeze N03 or complete the full plan.

Fresh verification passes all 72 new declarations through 118 compile/replay
invocations, 1120 dependency-inclusive axiom inspections and 118 matching-phase
import audits. Only permitted standard axioms occur. Proof compilation/elaboration
took 167.414 seconds total, with a 15.768-second maximum module.
These are proof-checking timings, not a measured parser runtime/resource envelope.
