K02: complete resolution and role binding-record AST formalization

This component closes the missing Frame, Body and enclosing Record AST decoding
layers for addresses-intent. It begins with independently specified meanings,
implements pure decoders and proves exact equivalences. It does not close the
original source-authenticity or relation obligations. All seven K02 inherited IDs
and all 263 successor IDs remain pending.

The practical problem was that the owned binding checker accepted typed bodies,
while the earlier AST decoder covered revision references and typed targets only.
There was no proved route from a complete retained binding-record AST to the
exact body that the checker consumes. This component provides that route through
syntax and field preservation. The captured bytes and authentication bridge still
need implementation and proof before those typed entries can be admitted.

What each layer means

| Layer | Input fields and meaning | Result |
|---|---|---|
| Revision key/reference, reused | Nonempty owner/artifact/revision and digest; closed objects with distinct keys | Exact RevisionKey or RevisionRef |
| Target, reused | Resolution: four revision references and three ordered reference arrays. Role: reference, nonempty code and one of seven subject spellings | Exact typed Resolution or Role |
| Frame, new | Six exact references: profile, subject, target, context, scope, snapshot; exact natural epoch; nonempty timeDomain | All eight fields of the existing Frame |
| Body, new | Nonempty token, target of the fixed target decoder and complete Frame | The existing owned-catalog Body type, with no parallel body representation |
| Record, new | Exact schema_version, binding_revision_key, exact kind, complete Body and owner_review_ref | Typed record retaining all five fields |

The two public record decoders fix their version, kind and target decoder internally:

- resolutionRecord accepts the candidate intent-resolution-qualifier-binding
  version/kind and a Resolution target.
- roleRecord accepts the candidate intent-addressing-role-binding version/kind
  and a Role target.

Generic helpers compose these decoders. A caller cannot select another target
schema or relabel a record through either of these two fixed public functions.
The schemas remain candidates; this component admits neither a schema nor an API.

The main theorem, in readable notation

    decodeResolutionRecord(ast) = Some(record)
        if and only if
    IndependentResolutionRecordMeaning(ast, record).

The role theorem has the same form. RecordMeaning contains a closed, duplicate-free
object with the five required fields and their independent component meanings.
It does not define validity as decoder success. Object membership, nonempty strings,
exact constant equality, ordered array meanings and decimal-value equations are
specified separately. The established combinators supply the equivalence between
those meanings and decoding.

The quantified field theorems expose the actual correspondence: the five record
fields come from five exact input values; its body comes from exactly token, target
and frame; its frame comes from all eight exact values. The six reference meanings
retain owner, artifact, revision and digest. Epoch uses the already proved exact
JSON-number parser and natural-value equation, rather than converting through a
floating-point number. Record success also proves that its returned schemaVersion
and kind equal the fixed constants. These results apply to arbitrary retained ASTs,
not only the worked fixtures.

For example, a frame epoch written as 42, 42.0 or 4.2e1 decodes to the same natural
42. An epoch written as 42.0000000000000001 refuses; rounding it would change its
meaning. The original number lexeme remains in the input AST. Negative nonzero,
fractional, string and malformed epoch inputs refuse. Negative zero denotes zero
under the prior numeric meaning, and large exact integers remain arbitrary precision.

The input AST stores an ordered list of object entries. That matters because a
normal dictionary would erase duplicate keys before the proof could inspect them.
Even identical duplicate kind or epoch fields refuse. Object order can change
without changing a successfully decoded record. Required arrays retain their order
and contents; the decoder does not silently remove repeated references or exclusions.

Worked cases and what they establish

BindingRecordControls contains 84 kernel-checked declarations: 44 for the resolution
record and 40 for the role record. They include both original fixtures, removal of
every required root/body/frame/target field, extra fields at each of those levels,
wrong version/kind, empty selected required strings, invalid epochs, exact decimal
and exponent epochs, identical duplicate fields, reordered root fields and an
independent meaning consequence for each original fixture. They are concrete
regression examples beside the general equivalence and field theorems.

The full-schema source audit compares both pinned draft schemas against explicit
expected revision-key, revision-reference, frame, target, body and root structures:
12 comparisons. It also compares the key, enum and constant spellings in the actual
compiled source, then validates an ordinary syntax corpus. This is a useful drift
check, not a theorem implementing all JSON Schema semantics. Its Python numeric
examples cannot validate retained numeric precision or duplicate keys; those are
handled by the separate exact Lean controls.

Limits that still matter

1. The proved input is the retained AST. The Python fixture-to-AST generator is
   not proved to parse the original UTF-8 bytes. Original-byte consumption,
   escapes, Unicode, duplicate-key retention and digest/capture correspondence
   still need a separate formal byte bridge.
2. The local AST meanings and the draft schemas have been compared structurally.
   There is no proved general JSON Schema interpreter or verified translation
   from these schema documents to the Lean meanings. N03 schema/API freezing
   therefore remains open.
3. A nonempty digest or owner-review reference is syntax. This decoder does not
   verify digest computation, signer/issuer authority, review authenticity or
   owner scope. The catalog's rooted-entry membership is a separate invariant,
   and a synthetic root cannot establish a real authentication claim.
4. A typed Body can now be obtained from a complete AST. Constructing authenticated
   catalog entries requires the captured bytes, computed identity, source kind and
   actual owner review. No unconditional parsed-record-to-authenticated-catalog
   bridge is supplied here.
5. Syntax is weaker than relation qualification. A role target with subjectKind
   other, or a resolution with no selected subjects, can be syntactically valid.
   The relation checker must still require an allowed source, selected/non-excluded
   exact subject, owned role and exact selection/resolution/frame joins. The
   nineteen source-policy predicates remain to receive authentic realizations.
6. Option.none identifies failure of this local AST meaning; it does not yet
   classify public errors into syntax, semantic, freshness, authentication or
   resource outcomes. No supported runtime resource envelope has been measured.
7. Same pinned Lean compilation and replay are not independent proof checking.
   Full source/effect/protected-state/theory closure, all inherited discharges,
   remaining owner/global reviews and the final bounded-use assessment remain open.

Implementation review

Reuse of the existing Body avoids a second representation that could diverge from
the owned checker. Fixing public versions/kinds prevents permissive caller-selected
schema dispatch. Field preservation avoids losing binding identity or owner-review
references while projecting the body. The independent meanings make decoder
correctness inspectable, and the exact numeric adapter prevents a precision gap
at the frame boundary. The remaining integration should keep the envelope outside
the body, so bytes, source identity and authentication cannot be replaced by a
syntactic pointer. NEXT-IMPLEMENTATION.md makes those dependencies explicit.

K02 meaning acceptance remains the actual scoped user assessment already recorded.
This component creates no new owner assessment. K04 and shared policies D01-D08
remain pending. No inherited obligation has been discharged, and N01 remains open.

Fresh verification passed all 94 declarations (10 general/field theorems and 84
worked controls), through 44 compile/replay invocations, 536 dependency-inclusive
axiom inspections and 44 matching-phase import audits. Only the allowed standard
axioms occur. Fresh compilation/elaboration took 125.641
seconds total; the largest module took 38.018 seconds. These timings
are not runtime resource measurements. The full-schema source audit passed all
12 comparisons and 68 syntax cases. No independent checker was run here.
