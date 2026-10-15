# Reusing verified preflight results

The reusable entrypoint now has a kernel-checked equality theorem:

```text
CandidatePreflightReuse.run(all original inputs)
  = CandidateEvidenceResources.classifyBoundedEvidence(all original inputs)
```

This equality covers every supported input and configuration, including successful
prepared stages, all refusal categories, exact source positions and numeric tokens.
It does not replace the original source/evidence meaning with a weaker cache check.

Previously, preflight parsed and hashed each capture and typed preparation repeated
those operations. The new entrypoint keeps the original Envelope and scalar AST.
Typed preparation uses that AST with the existing complete binding-record decoder,
profile selection, authority header/coherence and evidence joins. It performs no
second byte parse or digest evaluation on this path.

A raw cached Input is not enough. The typed adapter takes CertifiedInput, a subtype
carrying independently specified proof of the envelope, verified digest, original
bytes-to-AST correspondence and numeric work bounds under the exact profile and
budget. The checked constructor produces those proofs from actual preflight. The
AST uniqueness theorem rejects substituting a different AST for the same capture.
Lean erases proof fields at runtime; it retains the original data and AST.

The combined original-byte/count guard runs first. Ordered collection visits the
authority, every declaration and every selection before typed decoding. Duplicate
input occurrences retain their positions. Collection proves exact original-input
retention and equality of the first-refusal result. Only after successful collection
does typed preparation run. Existing ownership/authenticity requirements remain
unchanged because the final BoundedOutcome and its independent meaning are equal.

## Verification

All 23 new general declarations passed 12 fresh new-module compile/replay invocations
and 46 per-theorem axiom inspections. All 22 runtime controls passed in each phase,
including the original captured success, authority-inclusive budgets, corrupt
lengths, missing reviews, source positions and huge exponents in nested/unused/
duplicate entries. All 12 corresponding import audits passed.

The unchanged 88 dependency modules were NOT rebuilt. Their exact source and output
bindings were checked against the registered predecessor's fresh compile/replay and
import reports, then the corresponding phase outputs were copied and verified.
Every new import resolves to the current fresh local output or that exact verified
prior phase output. This is incremental pinned Lean checking, not a fresh dependency
rebuild and not independent proof checking. Only propext, Quot.sound and
Classical.choice are permitted; there are no new sorry/admit/native_decide/custom
axioms. Preparation failures were repaired before these final checks.

## Remaining gaps

- There is no observed live application consumer to switch. Candidate APIs, proofs
  and controls use the new path; legacy unguarded functions remain callable.
- Retaining all ASTs until typed preparation may change peak memory. The current
  resource bounds do not prove whole-process memory/time. N14 must measure the
  complete composed checker before qualifying limits or claiming performance gains.
- This change does not supply a real authentic-root provider or complete the
  remaining original source policies, Schema/review interpretations or full-theory
  countermodels. Exact result equality preserves those requirements rather than
  bypassing them.
- The scalar, combined-budget and typed-data diagnostics keep their documented
  coarse causes. Independent checking and N03 public API/schema freezing remain open.
- No original obligation is discharged. All 263 remain open and all 90 original
  discharges retain scope. K04 and global policies remain pending; only N00 is
  accepted. The full 41-kind/550-pair/seven-extension plan is active and incomplete.

## Formalization-first continuation

1. Formalize the actual evidence-provider/owned-root and complete source-policy
   contracts; implement only evidence that can establish their real premises.
2. Compose raw original relation sources and all typed catalogs with the guarded
   entrypoint. Require every consumed raw capture to be counted/preflighted and
   preserve full source refinement, not only data preparation.
3. Complete mandatory consumer boundary enforcement when the actual application
   consumer is available; do not invent a production cutover.
4. Measure composed time/memory/depth/adversarial behavior and independently check
   selected proofs, then finish all seven extension integrations and exact audits.
5. Complete the remaining actual meaning/global-policy reviews and final bounded-use
   assessment. K04's existing scoped question remains pending.
