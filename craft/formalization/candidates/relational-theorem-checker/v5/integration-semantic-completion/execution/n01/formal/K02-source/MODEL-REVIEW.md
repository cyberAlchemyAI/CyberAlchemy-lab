K02 Intent Resolution source-payload refinement candidate

This package connects the five exact required fields in the existing Intent
Resolution payload to K02's typed Resolution. It is candidate preparation within
N01, using the already accepted K02 meaning. It does not complete N01 or discharge
an inherited obligation, and it does not accept K03 or shared policies.

The source payload contains intent_ref, owner_decision_ref, selected_subject_refs,
satisfaction_test_refs and excluded_subject_refs. Those fields are opaque strings
or ordered string lists. The typed K02 model expects exact RevisionRef values,
including their owner/artifact/revision key and digest. Treating a nonempty source
string as an approved reference would skip the main semantic duty.

TokenResolution.lean defines the independent token meaning: the token is nonempty,
its role-specific catalog has that value, every candidate value for that exact
role/token agrees, and the value appears in the independent roots for that role.
The executable resolver checks those conditions. Missing, conflicting or unapproved
values refuse. Repeated identical values are permitted in this provisional model;
the implementation does not silently accept the first of conflicting values.

This role domain distinguishes Intent, Decision, subject and satisfaction-test
references. A mapping present only under another role cannot establish this field.
These reference roles are separate from the relation's addressing_role qualifier;
this module does not yet decode that owned addressing-role code.
These catalogs are verification-context inputs, not an eventual caller-provided
approval flag. Their ownership, authentic capture, version/frame binding and global
consistency are still obligations, so this is a conditional typed projection proof.

ListMeaning independently relates each source item to the corresponding exact
reference in the same position. The list decoder is proved equivalent to that
meaning. It preserves list lengths, every item and order; a missing tail item fails
the whole list. It does not omit unresolved exclusions, omit tests, sort, trim,
rewrite or deduplicate. Two distinct tokens can resolve to the same exact revision;
the resulting duplicate remains visible to K02's semantic checks.

RawIntentPayload.lean states the five-field denotation independently of the decoder.
Its central theorem is:

    decodePayload(catalog, roots, raw) = some payload
        if and only if PayloadMeaning(catalog, roots, raw, payload).

The implication covers all five fields together, not an existentially chosen subset
of tests or exclusions. Separate theorems establish exact selected/test/excluded
counts and preserve the entire payload when attaching the independently supplied
resolution identity and scope. Further bridges to the actual K02 meaning show:

- If the subject is in the attached exclusion list, K02 addressing is impossible,
  even if it also occurs in the selected list.
- An attached empty satisfaction-test list cannot establish Satisfied.
- Duplicate exact selected references make the attached K02 addressing invalid.

A schema-permitted empty list is preserved by decoding. Payload decoding does not
itself assert that a subject addresses an Intent, that all needed witnesses exist,
or that any test passed. K02 qualification and its separate outcomes remain distinct.

SourceFixture.lean captures the existing source fixture's complete five-field
payload as Lean data. Its revision bindings and roots are explicitly synthetic
controls, not authenticated live owner records. generate_fixture.py checks the
original JSON Schema, exact payload keys and the fixture's list counts before
emitting that data; source-capture.json binds the generator, schema, raw fixture
and generated module. The generator is an unproved translation step, not proof of
Python parsing or JSON-byte correspondence.

The controls exercise exact fixture decoding, unknown/wrong-role/conflicting/
unapproved references, identical repeated bindings, unresolved exclusions and a
missing second test. They also preserve empty tests, selected/excluded overlap and
aliases that produce duplicate exact references. Dropping the sole exclusion or
second test violates the independent payload meaning. Verification requires fresh
pinned compilation, separate fresh replay, per-theorem axiom inspection and exact
import resolution. Preparation failures are kept separately; only the final strict
verification output counts as evidence. The final run passes 31 new candidate
declarations in 14 compiler invocations with 168 axiom inspections including
imports. All 14 source/phase import-resolution checks pass. This is same-kernel
replay, not mandatory independent checking.

refinement-matrix.json maps the prepared components and remaining requirements to
all seven exact inherited K02 IDs; every one remains pending.

Remaining work before complete K02 source refinement:

- Prove or explicitly account for the raw-byte parser, JSON-AST projection, schema
  closure, wrong types, duplicate object keys, invalid strings and serialization.
- Bind the outer resolution identity, owner_ref, scope_ref, lifecycle, evidence,
  challenge route, claim ceiling and complete context to authentic issued records.
- Bind the raw relation qualifiers intent_resolution_ref/addressing_role and the
  independently owned Selection companion to exact resolution, subject, role,
  owner decision, kind/pair and full frame. Payload projection does not supply them.
- Establish snapshot/version capture and global non-equivocation. This resolver
  checks agreement for one role/token; different tokens referring to the same
  revision key with different digests/content need a global catalog invariant.
- Prove the complete decoded-source meaning equivalent to K02 Addresses, compose
  qualification with issued relation identity/content and pure recording, and
  independently check every selected mandatory closure proof.
- Complete actual owner assessments for the remaining kinds and global policies,
  the whole-source/full-theory obligations and all downstream successor plan gates.

The full plan and all 263 inherited pending obligations remain open. The original
90 discharges and original R06/G4 acceptance keep their original scope.
