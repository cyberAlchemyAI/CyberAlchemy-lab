Formalization contract for the proposed successor

This is a theorem specification, not compiled Lean code. Every formula below is a proposed target. All new models and policies require owner interpretation and exact statement/definition review. Existing v1–v4 artifacts are immutable inputs.

1. Define shared semantic objects first.

`RevisionRef = (artifact_id, revision, content_binding)`. References retain type/role. `Frame = (profile_revision, subject_revision, target_revision, context_revision, scope_revision, snapshot_revision, epoch, time_domain)`. A snapshot binds its owner-selected sources, provenance, as-of boundary and completeness statement. Exact epoch equality alone is not real-world currentness.

An `OwnedCatalog` has a trusted ownership basis, immutable revision, closed unique keys and exact content. Do not treat `owner=true`, `review.accepted=true` or a matching SHA as authentication. Local actual review capture or a verified source adapter supplies the ownership premise. `WellFormedCatalog` is explicit, not an unexamined axiom. Resolving an absent entry returns unresolved/unsupported, never a default approval.

Define persistent revision keys `(owner_namespace, artifact_id, revision)` and legal catalog evolution. Uniqueness inside one snapshot is insufficient: two catalogs could otherwise approve different content under the same stable revision. Legal extension preserves all existing bindings, and content changes require a fresh revision. If a required selected revision changes, the old qualification is stale for that new target; a historical proof about its original revision remains valid in its original scope.

`Truth` keeps yes/no/unknown. Define the positive and negative meanings per operation. Distinguish rejected input, violated meaning, absent completed bounded support, unknown evidence, unsupported profile, incomplete/resource refusal, stale evidence, conflict and independent-checker disagreement. These are not all semantic false. Contradictory active norms require a declared owner policy; there is no default winner.

2. Define obligations and coverage independently of submitted results.

An `Obligation` binds its original ID, kind/source revision, owned meaning revision, exact statement and definition closure, universe/frame, required method, dependencies and trust premises. Derive all applicable obligations from the actual diff and owned profile policy. The source set contains the exact 263 inherited pending IDs; new integration obligations have separate IDs. Preserve the 90 earlier discharges and their scopes. Missing, duplicated or substituted obligations refuse readiness.

`Discharged(o,e,S)` means current exact challenge/definition matching, allowed completed evidence and owner-reviewed source refinement under the named premises. It does not mean an input label says passed. Retirement, unsupported status and a narrower unrelated theorem cannot count as discharge.

Proposed coverage theorem:

    Ready(P,S,E) → ∀ o ∈ Required(P,S), ∃ e ∈ E, Discharged(o,e,S)

Proposed full-inherited-coverage theorem:

    FullInheritedReady(S,E) →
      {o.id | o ∈ DischargedInherited(S,E)} = Original263Ids

This full criterion concerns all inherited IDs. A first narrow pilot may be ready for its owned supported subset while full inherited completion remains false. The policy, rather than the caller, chooses that subset.

3. Resolve definitions and criteria before evaluation.

Proposed catalog theorem:

    WellFormedCatalog(C) ∧ resolve(C,owner,revision)=Some d₁ ∧
      resolve(C,owner,revision)=Some d₂ → d₁=d₂

Proposed revision/content theorem:

    acceptedDefinition(C,r,h₁) ∧ acceptedDefinition(C,r,h₂) → h₁=h₂

Proposed cross-catalog preservation theorem:

    LegalCatalogExtension(C,C′) ∧ resolve(C,owner,r)=Some d
      → resolve(C′,owner,r)=Some d

Content commitments rely on the stated hash/byte-binding assumptions. They do not prove collision resistance or human authenticity. Changed content needs a new owner-approved revision, and every dependent result is invalidated or explicitly requalified.

E00 activation must use the resolved expression, exact frame and retained norm origin. E03 fulfillment must use `Criteria(resolve(requirement_revision))`, not a caller-shortened list:

    FulfilledOwned(S,r) →
      ∀ c ∈ Criteria(resolve(r)), ∃ e, ExactAcceptedSupport(S,r,c,e)

Add a well-formedness predicate for action/output/evaluation ownership and prove all three verdict rails. Current E03 normalization checks request/requirement/frame correspondence. Its generic negative criterion branch uses the criterion reference without those checks; lift normalizer obligations into a typed theorem rather than claiming stale negative evidence is accepted by the public API. Also make the admissibility of negative evidence from unaccepted actions/outputs an explicit policy.

4. Formalize every relation's actual meaning.

For each of the 41 kinds define independent `Meaning_k(S,a)` from the source question, endpoint revisions, typed qualifiers and owned evidence policy. Its definition must not call the checker it is meant to validate. Provide a satisfiable positive example so a false antecedent cannot make the proof vacuous.

    decode_k(C,S,raw)=Some a ∧ WellFormed(C,S)
      → SourceMeaning_k(C,S,raw) ↔ Meaning_k(S,a)

    relationChecker_k(S,a)=true ↔ Meaning_k(S,a)

The 74 qualifier obligations instantiate exact source-token decoding and owner resolution. The 41 effect obligations additionally identify the claim tier: recorded intent, checked supplied snapshot, executed local effect or authenticated external observation. A recorded receipt does not establish that an atomic authorized action actually ran. Execution claims require a verified state transition and an appropriate provenance adapter; external truth remains conditional on the named external evidence model.

The 148 forbidden-inference obligations require exact conclusion meanings. There are 83 distinct label spellings, but the same spelling need not denote the same predicate for every relation. For each intended non-entailment prove a nonvacuous countermodel:

    ∃ M,a, ModelOf(T_k,M) ∧ Meaning_k(M,a) ∧ ¬ Conclusion_k,label(M,a)

This establishes `T_k + Meaning_k` does not entail the conclusion. It does not establish the conclusion is always false. Non-entailment for a single relation is distinct from a global inference prohibition. Global no-authority/no-root-manufacture and identity/ownership preservation claims need transition or least-closure invariants over the full applicable rule theory. Pin that theory; adding a rule can invalidate the result.

5. Compose qualification before lifecycle commitment.

`Qualified` binds the exact source/candidate pair, definition/evidence policies, snapshot/frame, independently derived complete obligations, checked meanings, required preservation/conservativity evidence, fresh process-local event and actual exact owner review. Each component is required only when the owned profile says it applies; an unrelated yes result cannot satisfy a requirement. Projection bridges retain subject, target, scope, context and epoch across the separately defined E00–E04 types. No existential unary projection can establish conformance to an arbitrary target.

    ComposedCheck(P,S,proposal)=Accepted cert → Qualified(P,S,proposal,cert)

    transition(S,proposal,cert)=Some S′ →
      Qualified(P,S,proposal,cert) ∧ WF(S′) ∧ SemanticInvariant(S′) ∧
      PreservedHistory(S,S′) ∧ PreservedEvidence(S,S′)

Avoid a circular premise: candidate eligibility cannot require the receipt that its own future commit will create. Define pre-commit qualification and post-commit materialization separately. A future output is not already a materialized consequence. Previously recorded consequences use their own exact earlier receipts. Recovery checks recorded state and creates no fresh event.

6. Improve traversal without changing absence semantics.

Prove the adjacency/visited-set implementation enumerates exactly the effective joined simple paths represented by the old edge-word universe within the declared depth. If the result includes every support, prove complete support retention and specify ordering/canonicalization; an early existential witness is insufficient for that result contract. A cutoff gives incomplete/resource refusal, never a completed no. No result claims unbounded-chain absence.

7. Reduce transport and checker boundaries explicitly.

Specify a restricted UTF-8 JSON grammar: scalar Unicode, exact escape decoding, unique keys, full byte consumption and explicit natural-number lexemes. Choose and review handling of `-0`, exponents, fractions and escapes rather than inheriting Python coercion. JSON standard validity and this profile's narrower validity are different.

    verifyParse(bytes,certificate)=Some ir → ByteDenotes(bytes,Denote(ir))

    verifyParse(bytes,certificate)=Some ir ∧ domainImport(ir)=Some a
      → DomainByteMeaning(bytes,a)

`ByteDenotes` is an independent inductively specified grammar/denotation relation, including full consumption. `DomainByteMeaning` uses the owned domain predicates, rather than defining itself as the importer returned true. Prove uniqueness of the supported byte denotation and the exact mapping assumptions needed for domain composition.

The certificate must bind and check all raw bytes/spans, not merely repeat an emitter's expected value. An untrusted generator may propose the certificate. Hashes and host execution remain stated premises unless separately formalized. Universal refinement is distinct from finite differential tests.

For independent checking, require both valid proof and the independently anchored intended statement/semantic definitions. Inventory all mandatory closures, universes, inductives/recursors, quotients, primitive extensions and allowed axioms. Implement accept/reject/unsupported/resource/disagreement distinctly. Retain the original mandatory Lean check. The first two substantial independently checked theorems are a milestone; they do not complete whole-profile assurance. Full completion requires every mandatory selected closure to pass or a reviewed versioned narrowing that does not misreport the wider goal complete.

Lean's official guidance separates proof validity from intended statement meaning and explains challenge comparison and independent kernels: https://lean-lang.org/doc/reference/latest/ValidatingProofs/. The JSON grammar baseline is RFC 8259: https://www.rfc-editor.org/rfc/rfc8259.
