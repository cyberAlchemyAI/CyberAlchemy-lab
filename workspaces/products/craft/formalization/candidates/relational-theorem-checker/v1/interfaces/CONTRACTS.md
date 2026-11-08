# Behavioral contracts

Each contract binds inputs, ordering, outputs, failures and retained trust boundaries. Fields reported by an untrusted submitter are assertions until independently verified.

## C-captureSnapshot

Layer: L0. DAG tasks: B00, C01.
Input: [snapshot-request](schemas/snapshot-request.schema.json). Output: [baseline-snapshot](schemas/baseline-snapshot.schema.json).

**Preconditions**

- Caller is authenticated and authorized to read every referenced artifact.
- Resolve exact SHA-256 and byte size; do not fetch arbitrary URLs or evaluate submitted paths.

**Rules**

- Hash every source and resolve effective state through exact registry evidence.

**Postconditions**

- A selected immutable snapshot with explicit capture evidence; no perpetual currentness claim.

**Failure controls**

- Missing overlays, source drift or ambiguous baseline.

**Trust boundary**

- JSON shape validation is not semantic proof.
- Submitted metadata and outputs remain untrusted until independently verified.

## C-normalizeGraph

Layer: L0. DAG tasks: P01, P02, P03, C03.
Input: [normalization-request](schemas/normalization-request.schema.json). Output: [normalization-report](schemas/normalization-report.schema.json).

**Preconditions**

- Caller is authenticated and authorized to read every referenced artifact.
- Resolve exact SHA-256 and byte size; do not fetch arbitrary URLs or evaluate submitted paths.

**Rules**

- Reject unknown kinds, identity collisions and malformed input; retain exact ordered pairs and original qualifier shapes.

**Postconditions**

- A deterministic projection with preservation mappings and explicit parser trust.

**Failure controls**

- Pair widening, reordered identity bindings, omitted fields or unknown-kind escape.

**Trust boundary**

- JSON shape validation is not semantic proof.
- Submitted metadata and outputs remain untrusted until independently verified.

## C-checkAddition

Layer: L0. DAG tasks: P04, P05, P06, G0.
Input: [check-request](schemas/check-request.schema.json). Output: [check-receipt](schemas/check-receipt.schema.json).

**Preconditions**

- Caller is authenticated and authorized to read every referenced artifact.
- Resolve exact SHA-256 and byte size; do not fetch arbitrary URLs or evaluate submitted paths.

**Rules**

- Fully recheck the resulting graph against independently defined validity; structural scope stays separate.

**Postconditions**

- A scoped result; semantic-valid requires checked general soundness for the selected profile.

**Failure controls**

- Invalid pair/qualifier/reference/invariant or unsupported semantic definition.

**Trust boundary**

- JSON shape validation is not semantic proof.
- Submitted metadata and outputs remain untrusted until independently verified.

## C-deriveObligations

Layer: L2. DAG tasks: E01, E02.
Input: [obligation-request](schemas/obligation-request.schema.json). Output: [obligation-set](schemas/obligation-set.schema.json).

**Preconditions**

- Caller is authenticated and authorized to read every referenced artifact.
- Resolve exact SHA-256 and byte size; do not fetch arbitrary URLs or evaluate submitted paths.

**Rules**

- Compute the exact semantic diff and derive every required hard obligation using server-selected policy.

**Postconditions**

- Complete obligation set with coverage statement, including L3 obligations for rule changes.

**Failure controls**

- Author relabeling, omitted hard obligations or unsupported change profiles.

**Trust boundary**

- JSON shape validation is not semantic proof.
- Submitted metadata and outputs remain untrusted until independently verified.

## C-checkDerivation

Layer: L3. DAG tasks: I01, I02.
Input: [derivation-request](schemas/derivation-request.schema.json). Output: [obligation-result](schemas/obligation-result.schema.json).

**Preconditions**

- Caller is authenticated and authorized to read every referenced artifact.
- Resolve exact SHA-256 and byte size; do not fetch arbitrary URLs or evaluate submitted paths.

**Rules**

- Resolve every base leaf, exact rule and substitution; validate each premise and typed conclusion in a finite DAG.

**Postconditions**

- Sound supported conclusion only with generic derivation soundness evidence.

**Failure controls**

- Cycle, missing premise, forged root, new identity or unbound external fact.

**Trust boundary**

- JSON shape validation is not semantic proof.
- Submitted metadata and outputs remain untrusted until independently verified.

## C-checkClosure

Layer: L3. DAG tasks: I03.
Input: [closure-request](schemas/closure-request.schema.json). Output: [obligation-result](schemas/obligation-result.schema.json).

**Preconditions**

- Caller is authenticated and authorized to read every referenced artifact.
- Resolve exact SHA-256 and byte size; do not fetch arbitrary URLs or evaluate submitted paths.

**Rules**

- Check initial facts, closure under all ground rule instances and justified membership.

**Postconditions**

- Negative non-derivability only with least-fixed-point adequacy or an independent general theorem.

**Failure controls**

- Incomplete saturation, invented member, wrong universe or timeout.

**Trust boundary**

- JSON shape validation is not semantic proof.
- Submitted metadata and outputs remain untrusted until independently verified.

## C-checkModel

Layer: L2. DAG tasks: E04, I05.
Input: [model-request](schemas/model-request.schema.json). Output: [obligation-result](schemas/obligation-result.schema.json).

**Preconditions**

- Caller is authenticated and authorized to read every referenced artifact.
- Resolve exact SHA-256 and byte size; do not fetch arbitrary URLs or evaluate submitted paths.

**Rules**

- Verify a nonempty interpretation against every bound axiom; countermodel also negates the target statement.

**Postconditions**

- Checked witness with exact finite scope; a fully checked countermodel may refute a universal implication.

**Failure controls**

- Empty domain, wrong arity, missing axiom, wrong target or exhausted search.

**Trust boundary**

- JSON shape validation is not semantic proof.
- Submitted metadata and outputs remain untrusted until independently verified.

## C-verifyProof

Layer: L4. DAG tasks: R02.
Input: [proof-request](schemas/proof-request.schema.json). Output: [proof-audit](schemas/proof-audit.schema.json).

**Preconditions**

- Caller is authenticated and authorized to read every referenced artifact.
- Resolve exact SHA-256 and byte size; do not fetch arbitrary URLs or evaluate submitted paths.

**Rules**

- Isolate replay, pin the exact required statement and dependency closure, and audit transitive axioms.

**Postconditions**

- Audit of the actual theorem statement and policy; assumption and kernel boundaries remain explicit.

**Failure controls**

- Weakened theorem, circular assumption, sorry, forbidden axiom or changed dependency.

**Trust boundary**

- JSON shape validation is not semantic proof.
- Submitted metadata and outputs remain untrusted until independently verified.

## C-reviewBundle

Layer: L4. DAG tasks: C02, C04, C05, G1, E03, E05, G2, I04, I06, G3, R01, R03, R04, R06, G4.
Input: [review-request](schemas/review-request.schema.json). Output: [review-report](schemas/review-report.schema.json).

**Preconditions**

- Caller is authenticated and authorized to read every referenced artifact.
- Resolve exact SHA-256 and byte size; do not fetch arbitrary URLs or evaluate submitted paths.

**Rules**

- Recompute all digests and required obligations independently; draft normative profiles cannot become semantically ready.

**Postconditions**

- Readiness only after every hard obligation has allowed, current, completed evidence; human meaning review remains explicit.

**Failure controls**

- Missing hard result, stale dependencies, bounded-search upgrade or incomplete rule evidence.

**Trust boundary**

- JSON shape validation is not semantic proof.
- Submitted metadata and outputs remain untrusted until independently verified.

## C-replayBundle

Layer: L4. DAG tasks: C06.
Input: [replay-request](schemas/replay-request.schema.json). Output: [review-report](schemas/review-report.schema.json).

**Preconditions**

- Caller is authenticated and authorized to read every referenced artifact.
- Resolve exact SHA-256 and byte size; do not fetch arbitrary URLs or evaluate submitted paths.

**Rules**

- Compare the complete bound dependency closure with the observed snapshot and rerun affected obligations.

**Postconditions**

- Currentness and invalidation are verifier-produced, not trusted client flags.

**Failure controls**

- Changed registry, graph, profile, rule, evidence or proof dependency.

**Trust boundary**

- JSON shape validation is not semantic proof.
- Submitted metadata and outputs remain untrusted until independently verified.

## C-recheckApplication

Layer: L4. DAG tasks: R05.
Input: [application-request](schemas/application-request.schema.json). Output: [application-recheck](schemas/application-recheck.schema.json).

**Preconditions**

- Caller is authenticated and authorized to read every referenced artifact.
- Resolve exact SHA-256 and byte size; do not fetch arbitrary URLs or evaluate submitted paths.

**Rules**

- Recapture a trusted observed baseline and recheck at simulated application time.

**Postconditions**

- Candidate recommendation requiring separate human authority; authority effect remains none.

**Failure controls**

- Review/application drift, reused stale receipt or request for actual admission.

**Trust boundary**

- JSON shape validation is not semantic proof.
- Submitted metadata and outputs remain untrusted until independently verified.

## C-artifactTransport

Layer: shared. DAG tasks: cross-cutting.
Input: [common](schemas/common.schema.json). Output: [common](schemas/common.schema.json).

**Preconditions**

- Use the selected versioned profile and exact source identities.

**Rules**

- For named JSON envelopes reject invalid UTF-8, duplicate keys, schema mismatch and unsupported documents. Store raw proof, statement, provider and dependency bytes as untrusted artifacts. Resolve each operation's expected role/schema independently of upload labels; hash original bytes without reserialization.

**Postconditions**

- Artifact identifiers never grant read permission; access remains principal-scoped.

**Failure controls**

- Client-supplied digest, size or currentness is never trusted.

**Trust boundary**

- Implementing this declared rule still requires the corresponding DAG evidence.

## C-jobLifecycle

Layer: shared. DAG tasks: cross-cutting.
Input: [evidence-bundle](schemas/evidence-bundle.schema.json). Output: [review-report](schemas/review-report.schema.json).

**Preconditions**

- Use the selected versioned profile and exact source identities.

**Rules**

- Queued -> running -> completed/timeout/unavailable/failed; queued/running may cancel. Terminal states are immutable.

**Postconditions**

- HTTP 202 and completed job state say execution happened, not that an obligation was satisfied.

**Failure controls**

- Completion is refused if its operation-specific result type or scope is wrong.

**Trust boundary**

- Implementing this declared rule still requires the corresponding DAG evidence.

## C-layerEvidenceGates

Layer: shared. DAG tasks: cross-cutting.
Input: [evidence-bundle](schemas/evidence-bundle.schema.json). Output: [review-report](schemas/review-report.schema.json).

**Preconditions**

- Use the selected versioned profile and exact source identities.

**Rules**

- F0 starts with P01 relational semantics, P03 independent formal predicates, P04 Lean reference checker and P05 general soundness review. B00 baseline refresh and P02 schema/API/decoder alignment follow that accepted evidence. Every later task requires current predecessor evidence; G2 closes supported non-rule scope while I06 closes rule obligations.

**Postconditions**

- Contract authoring does not complete any implementation/proof gate in the DAG.

**Failure controls**

- Plan/fixture receipts cannot substitute for execution acceptance.

**Trust boundary**

- Implementing this declared rule still requires the corresponding DAG evidence.

## C-protectedLineage

Layer: shared. DAG tasks: cross-cutting.
Input: [evidence-bundle](schemas/evidence-bundle.schema.json). Output: [review-report](schemas/review-report.schema.json).

**Preconditions**

- Use the selected versioned profile and exact source identities.

**Rules**

- Match targetVersion, effect, scope and epoch against legitimate roots across all indirect rule paths.

**Postconditions**

- Conformance may coexist with independently justified admission; conformance cannot justify admission.

**Failure controls**

- Qualifier strings, axis names and untrusted adapter attestations cannot create authority roots.

**Trust boundary**

- Implementing this declared rule still requires the corresponding DAG evidence.

## C-compatibilityClaims

Layer: shared. DAG tasks: cross-cutting.
Input: [evidence-bundle](schemas/evidence-bundle.schema.json). Output: [review-report](schemas/review-report.schema.json).

**Preconditions**

- Use the selected versioned profile and exact source identities.

**Rules**

- Check selected data, generic invariant preservation and model conservativity separately.

**Postconditions**

- A conservative-extension claim covers every base model via an expansion with unchanged old reduct.

**Failure controls**

- Pair widening is not unchanged old semantics; finite search exhaustion is not proof.

**Trust boundary**

- Implementing this declared rule still requires the corresponding DAG evidence.

## Review outcome rules

Execution, currentness, evidence method, obligation verdict and aggregate readiness stay independent. Satisfied obligations require completed, current allowed evidence. A bounded-search provider output must become a checked witness before it can discharge a witness-eligible obligation.
The verifier derives the complete hard obligation set from the actual diff/policy and matches exact statements and scope. Schema validation cannot enforce that cross-document completeness or prove a submitted proof term.
Ready-for-review is a candidate review state, not admission. Human normative meaning review is separately recorded. G2 readiness excludes rule changes until I06/L3 discharge them.
