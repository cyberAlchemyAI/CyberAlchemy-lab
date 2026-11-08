# Validation Receipt: proposed typed logical fragment

This is a proposed design for the next native unit. It is not an executed interpretation, accepted denotation, mechanized proof or admitted receipt format. Its positive source is the current C29 Validation Receipt Definition at SHA256 `7df65f1254c26f05ad7f030f0616085d7842cbd746751d52bddb8fe72da9fd5e`. The existing source inspection and design remain unchanged. All formulas below need native declaration, correspondence, controls and source-owner review.

Use separate sorts for Receipt, ValidationEventReference, ReceiptIdentity, SubjectReference, CriteriaProfile, ValidatorReference, InputOccurrence, InputReference, EnvironmentReference, DeclaredCheck, OutcomeReference, EvidenceReference, CausalBlockerReference, EmissionTime, ClaimCeiling, AuthorityEffect, Observation, Digest, Context and Token. These are descriptive mathematical sorts. They do not create canonical Definition identities. InputOccurrence keeps repeated inputs distinguishable without assuming path names or digest strings identify occurrences globally.

A receipt has total projections to its identity, one event, subject, profile, validator, environment, emission time, claim ceiling, context and authority effect. Subject, profile and validator each have a digest projection; the receipt has corresponding recorded digest projections. Each input occurrence projects to an input reference and its digest. A receipt/occurrence pair has a recorded input digest. Exact reference presence and nonempty handles must be separately declared. Digest equality is a necessary recorded binding; no digest algorithm, authenticity, collision freedom, source currentness or successful execution follows from equality alone.

Let `Selected(r)` guard the receipt fragment. Let `E(r)` denote its one event reference. The proposed exact scalar binding guards are:

```text
Selected(r) => RecordedSubjectDigest(r) = SubjectDigest(Subject(r))
Selected(r) => RecordedProfileDigest(r) = ProfileDigest(Profile(r))
Selected(r) => RecordedValidatorDigest(r) = ValidatorDigest(Validator(r))
Selected(r) => AuthorityEffect(r) = NONE
```

Each projection requires its appropriate declared, nonempty reference. The event's exact subject, profile, validator, environment and input denotations need an independently accepted bridge; merely pointing to an EventReference does not import the complete Evaluation or Validation theory. Shared subject or receipt-identity labels cannot collapse distinct events. Global identity uniqueness and one receipt per event are additional policies, not consequences of a record being about one event.

For input collection completeness, declare event membership and receipt membership over InputOccurrence. Within selected scope the candidate guard is exact membership, rather than one aggregate digest substituted for the collection:

```text
Selected(r) => (ReceiptInput(r,i) <=> EventInput(E(r),i))
Selected(r) & ReceiptInput(r,i) =>
  InputOccurrenceDeclared(i) & InputReferenceDeclared(Input(i))
  & RecordedInputDigest(r,i) = InputDigest(i)
```

This retains multiplicity through occurrence identity while leaving order and collection representation open. Real exact evaluated bytes and reference resolution remain actual-outcome targets. An owner must accept how occurrences and receipt membership map to concrete formats. Empty input collections need an explicit policy; do not silently forbid or bless them through a vacuous formula.

For outcome completeness, separately declare event outcome membership, receipt outcome membership and each outcome's check reference. A receipt cannot omit an event outcome or add an unrelated one under the exact membership proposal. Every event-declared check requires at least one recorded matching outcome:

```text
Selected(r) => (ReceiptOutcome(r,o) <=> EventOutcome(E(r),o))
Selected(r) & EventCheck(E(r),c) =>
  exists o: ReceiptOutcome(r,o) & OutcomeCheck(o) = c
```

Outcome tags, repeated attempts, aggregation and one-final-result policy remain independently reviewed maps. Validation's owner-pending partial reported PASS cannot silently define this receipt's overall status. An exact recorded outcome need not be truthful, authentic or complete with respect to undiscovered checks. Retaining all declared outcomes and discovering all relevant criteria are separate claims.

Declare dependencies between checks within an event. A necessary direct dependency guard requires both endpoints to be event-declared checks:

```text
Selected(r) & DependsOn(E(r),c,d) =>
  EventCheck(E(r),c) & EventCheck(E(r),d)
```

Together with outcome existence for every event-declared check, this covers every endpoint of every declared finite dependency path. It does not discover missing dependencies, prove that recorded paths are causally adequate, assert acyclicity, or compute a general transitive closure. Native controls should include a chain of at least two dependency edges, a missing dependent check, a missing outcome for the intermediate check and a cycle. A cycle is not automatically malformed unless an accepted profile requires acyclicity.

Causal blocker preservation should similarly use explicit event/receipt membership, with retained check or outcome references and evidence references. The proposed necessary guards are:

```text
Selected(r) => (ReceiptBlocker(r,b) <=> EventBlocker(E(r),b))
Selected(r) => (ReceiptEvidence(r,e) <=> EventEvidence(E(r),e))
```

Blocker causality, applicability and adequacy are independent actual-outcome targets. A referenced blocker cannot by itself prove why a check did not run. Zero blockers may be appropriate for an unblocked event; preserve a nonempty-blocker witness so completeness does not pass only vacuously. Evidence membership does not entail Evidence adequacy or the entire previously formalized Evidence theory.

Immutability needs a comparison or observation surface. Give each Observation a receipt reference and recorded canonical-content digest. A proposed necessary comparison guard is:

```text
ObservationSelected(a) & ObservationSelected(z)
& ObservedReceipt(a) = ObservedReceipt(z)
=> ObservedContentDigest(a) = ObservedContentDigest(z)
```

This expresses invariance within the selected declared observations. It is not a proof that every possible future storage mutation is impossible. Observation coverage, canonical serialization, digest authenticity and append-only storage remain open. Emission-time labels do not imply actual chronology. The owner may select a stronger temporal model, which must then be declared and validated explicitly.

For changed evaluated inputs, compare a receipt's binding with a proposed event/input observation. A new input digest must change the applicable evaluated-input binding or make the original receipt inapplicable to that new input. Do not rewrite the immutable original record to make it appear current. A native candidate should exhibit both changed-binding and invalidated-binding controls; it must avoid claiming the owner accepted either operational strategy merely because a finite model supports it.

Required populations should expose a selected receipt without actual authority, an outside receipt, a nonempty input occurrence, a complete dependency chain, a nonempty blocker record, repeated same-receipt observations with equal content binding, and a changed-input comparison. Query targets should separately cover actual immutability, event authenticity, byte resolution, receipt production/storage, completeness discovery, causal adequacy, timestamp accuracy, traceability, Conformance, Admission, Acceptance, authority, Publication, Deployment, owner fidelity and consumer alignment. Positive supported outcomes remain permitted with independent evidence; non-entailment is not a universal ban.

Native implementation follows the separately audited Validation delivery. All source characters must receive encoded, explanatory or deferred correspondence. These proposed formulas cannot replace the full Definition's scientific-formal boundary and test conditions. Exact finite controls and countermodels precede a frozen typed receipt, carrier/consumer observations, dependency and inventory refresh, six fresh delivery checks, detailed review, seal and separate audit.
