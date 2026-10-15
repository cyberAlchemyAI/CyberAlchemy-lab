# Byte binding-record meaning before implementation

`RecordBytesMeaning(version, kind, target, bytes, record)` means that the exact
original byte sequence has an independently meaningful scalar AST and that AST
has the existing complete, field-preserving binding-record meaning. The meaning
contains no call to the parser or record decoder. Scalar interpretation includes
the independent raw UTF-8/JSON grammar and recursive representation conversion.

`PreparedBytesMeaning(version, kind, target, frame, envelope, prepared)` additionally
requires the existing independent EnvelopeMeaning, exact record fields and frame,
and retention of this exact envelope in the prepared output. The AST is derived
from the envelope bytes; callers cannot supply an unrelated AST to this entrypoint.
Nonempty submitted digest/profile labels do not establish their correctness,
computation, issuer legitimacy or authentication.

Record outcomes distinguish invalid raw syntax, valid raw JSON without a supported
scalar AST, supported scalar AST without binding-record meaning, and decoded record.
Capture outcomes first check the submitted envelope fields, then those record
outcomes, then exact frame alignment. Success retains full envelope/record data.
Each result must be equivalent to its independent meaning, with no silent repair.

A parser-policy adapter may implement only the existing `parses` predicate using
this exact independent scalar byte-document meaning. Digest, owned digest-profile,
Schema and authentic review requirements remain separate and unrealized. A
conditional bridge must require their actual evidence; no permissive provider is
introduced. Any complete-source or inherited discharge requires those gaps closed.

Worked controls must evaluate the actual original resolution/role fixture bytes,
not a Python-produced AST paired with arbitrary bytes. Mutations must distinguish
byte syntax, scalar support, record fields, envelope count and stale frame. Fixtures
retain their declared synthetic reference/review roots; parsing is not authenticity.

All 263 inherited IDs, K04 and global D01–D08 remain pending. N01 stays in progress;
N02/N03 admission and the full seven-extension plan keep their original scope.
