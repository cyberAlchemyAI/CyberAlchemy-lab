K02 captured source pipeline and draft binding schemas

This package composes closed qualifier decoding, owned Resolution lookup, complete
source-body/byte/metadata projection and owned role/Selection/full-frame checking.
Its independent Meaning predicate is the conjunction of the component denotations;
it does not call run. A bidirectional theorem proves that run returns an Output
exactly when that captured composition meaning holds.

The pipeline accepts source bytes and source/qualifier ASTs, captured metadata and
binding contexts, the captured typed World/frame and a typed claim. It first decodes
the exact two-field qualifier object, resolves its Resolution token and uses that
resolved revision to decode the source. There is no independent source-reference
argument a caller can override. The owned join then pins the complete resolved
Resolution to both the source projection and claim, pins the role to the selected
owned role and checks the complete Selection frame, including epoch. Separate
preservation theorems show these equalities for every successful result.

The original byte fixture and all six synthetic typed source branches pass the
composition meaning/proof checks. Missing owned Resolution records cannot start
the pipeline. Malformed qualifiers or source AST, changed original bytes, missing
role roots and a stale Selection epoch refuse the composition. The positive
proofs use independent component meanings and their established equivalences,
not an unverified native decision tactic.

This is a captured composition result. It does not prove bytes-to-AST parsing,
root authenticity or the nineteen SourceInterpretation policy obligations. None
means unqualified in this fragment; the final public invalid/unknown/unsupported
classification is not implemented. A malicious caller supplying fabricated
contexts can satisfy structural checks; actual trusted provider capture is an
independent requirement. The pure function has no authority-granting or recording
side effect and no implication of satisfaction, completion or membership.

Two draft JSON Schema 2020-12 files specify resolution and role binding records.
Each has a fixed candidate schema version/kind, a binding revision key, a closed
body containing token/full typed target/full frame, and an owner-review reference.
The typed Resolution target preserves all seven fields; Role preserves reference,
code and subject kind. Frame preserves all eight dimensions, with a natural epoch.
Revision references preserve owner/artifact/revision keys and opaque digest strings.
Role syntax includes other, whose relation use is refused by the typed branch
checker; empty selected-subject lists remain syntax-valid but cannot select a claim.

Original binding bytes are captured outside the JSON record. Its own digest is
also external: the provider computes or verifies it from the exact source bytes
and combines it with binding_revision_key. Putting original bytes or a digest of
the complete file into that same file would create a self-referential serialization.
No hashing or digest/authenticity algorithm is proved here. The owner-review pointer
is an external record reference, not a proof that review took place.

The forty-case schema corpus checks missing/extra/wrong fields, token types and
emptiness, frame epochs/domains, revision keys, forbidden self-bytes/digest fields
and the two syntax/semantic boundary cases. This validates proposed syntax only.
Python dictionary validation does not preserve duplicate keys; a future byte
parser must retain entries and reject duplicates using the explicit parser profile.
Lean AST/schema correspondence for these new binding schemas is unproved. Their
nonempty-reference/domain restrictions are draft profile choices stricter than the
unconstrained typed carriers in some cases. They are not an admitted artifact type
or a frozen N03 API/schema, and no new owner/profile acceptance is inferred.

Remaining work: prove binding-record AST/schema and byte/capture correspondence;
realize authentic root, typed World/Selection and all nineteen source policies;
implement final diagnostics and supported resource limits; prove whole-source
semantics under those actual policies, complete-rule record preservation and
complete-theory non-entailment countermodels; run mandatory independent checking.
All 263 inherited IDs remain pending, all 90 original discharges retain scope,
K04/global policy review remains pending, and N01/the full plan is incomplete.

Verification result: all 21 new declarations pass 72 fresh pinned compiler/replay
invocations, 504 declaration axiom inspections including imported dependencies and
all 72 matching-phase import audits. The forty-case draft-schema corpus also passes
separately. Total compiler time was 239.950 seconds; the slowest module took 16.318
seconds. These timings include compilation/elaboration and are not a supported
runtime envelope. Same-kernel replay and JSON Schema syntax validation are not
independent proof checking or byte/schema correspondence. No inherited obligation
or authentic full-source policy is discharged.
