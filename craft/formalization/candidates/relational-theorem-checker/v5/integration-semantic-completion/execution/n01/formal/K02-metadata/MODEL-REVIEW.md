K02 captured metadata binding — model and limits

This package closes a structural projection gap: previous payload decoding took
Resolution.ref and Resolution.scope as parameters. Here they are derived from
the exact captured source receipt and its scope binding. The public relation
checker and complete source refinement remain unfinished.

A source artifact retains its full fourteen-field typed body, original bytes,
revision reference, source-kind label and owner-review reference. A receipt joins
that artifact to separately captured identity, owner and scope statements. Every
selected statement names the same source revision and complete frame. The scope
statement identifies the exact owner statement. The owner holder is a revision
reference: this model does not establish that it denotes a Principal, controls
the namespace or has authority over the source. Field names do not prove those
facts.

ReceiptMeaning is an independent nineteen-field predicate. ContextMeaning adds
non-equivocation for artifact revisions, receipts and each binding-role catalog,
plus well-formedness of every selected record and root. These meanings do not
call the decoder. The boolean checks and resolver are proved equivalent to the
meanings; missing or contradictory captured entries cannot establish resolution.

The complete projection is:

    captured context + exact frame/source revision
      -> resolved receipt
      -> original-byte equality + JSON-AST/full-body agreement
      -> guarded five-field payload decoding
      -> Resolution(ref = captured source, scope = captured scope, payload)

SourceMeaning requires both byte equality and AST/body agreement. These are two
checks. Their conjunction does not establish that the bytes parse to that AST.
A provider or verified parser must establish that correspondence. This package
also does not prove signatures, capture authenticity or digest computation.
The fixture retains all 1,208 bytes of the repository's actual Intent Resolution
example, but its frame, reference mapping and metadata roots are synthetic. Real
fixture bytes are not evidence of real authorization or a real reviewed source.

ContextMeaning currently requires one canonical complete receipt for each source
revision key in a fixed-frame capture. Identical repetitions are allowed. Different
owner statements or review receipts for the same source in that capture conflict,
even if both could be legitimate under a richer policy. Different frames belong
in different captures. Supporting multiple legitimate receipts requires a revised
key/selection policy and new uniqueness and resolution proofs. This is a candidate
profile choice to assess within N01; it is not a universal source-catalog law.

The refusal controls isolate missing roots and identity/owner/scope statements;
wrong receipt/schema/kind and statement source, token, scope or frame; broken
owner-to-scope joins; all eight expected-frame fields; changed digest; empty
capture; changed source bytes; a schema-valid substituted owner label; malformed
AST; missing metadata through the composed decoder; and conflicting captured
owner receipts or byte content. Positive proofs derive reference and scope from
the original fixture. Controls test captured consistency, not authentic issuance.

Still missing for complete K02 source meaning:

- Verified byte-to-AST correspondence and an assessed parser/capture profile.
- Authentic provider roots, entity-kind interpretation, holder/namespace ownership
  policy, scope authorization, schema revision correspondence and review validity.
- Lifecycle and freshness interpretation, evidence policy, challenge route,
  successor references, companion relation joins and claim-ceiling interpretation.
- Closed qualifier interpretation, owned addressing role, exact Intent Resolution,
  selected subject, exclusion and owned Selection/frame joins. Guarded payload
  decoding alone does not require payload.intent = frame.target.
- Whole-rule protected-state closure, countermodels under the complete pinned
  theory and mandatory independent proof checking.

The seven K02 inherited IDs remain pending. This package grants no authority,
records no global policy acceptance and does not finish N01. Four meaning
assessments remain recorded; K04 is still the current human review.

Verification must rebuild every dependency in separate compile and replay
directories using pinned Lean 4.33.1, inspect every declaration's axioms, reject
warnings and forbidden proof mechanisms, and audit exact import resolution.
Same-kernel replay is not independent checking. The authoritative results are
verification.json and import-resolution-audit.json, once both runs succeed;
preparation logs alone do not qualify this package for the proof index.

Verification result: 67 new declarations pass 48 fresh compile/replay invocations,
440 axiom inspections including imported dependencies and all 48 matching-phase
import audits. The declarations include 35 isolated refusal controls, seven
positive fixture proofs, independent equivalence/preservation lemmas and control
helpers. Nine separate executable probes produce the expected results. The byte
literal comparator confirms the original 1,208 bytes. The compiler runs took
460.537 seconds in total; the slowest module took 40.662 seconds. These timings
include compilation and proof elaboration, not a supported production resource
envelope. No independent checker has run. Earlier preparation failures remain in
repair-attempts and contribute no registered declarations.
