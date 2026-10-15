"""Detailed candidate review and type-first continuation."""
from pathlib import Path
import json
root=Path.cwd();p=Path(__file__).resolve().parent;u=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.canonical-representation-invariant'
counts=json.loads((u/'denominator.json').read_bytes());model=json.loads((u/'model-controls.json').read_bytes());source=json.loads((u/'source-checks.json').read_bytes());analysis=json.loads((u/'clause-analysis.json').read_bytes())
assert counts['declarations']==235 and model['control_count']==160 and len(source['checks'])==57
text='''# Canonical Representation Invariant: types and logic review

This is a source-bound, project-owned candidate interpretation of `cal.definition.canonical-representation-invariant@1.0.0-candidate.1`. It has source fidelity pending, semantic readiness false, no accepted whole translation and no whole-definition proof. Its declarations are explicit enough to expose duplicate representations, mismatched origins, dishonest assurance and projected-view confusion on supplied finite models. Actual artifact bytes, owner decisions, origin eligibility, receipt verification, execution, truth and authority remain separate obligations. The admitted Definition, its bound D51 source section, this interpretation and a real canonical artifact are different objects with different evidence requirements.

Canonical Package Manifest's full delivery preserved 7,919 files and passed a separate actual audit before this native interpretation was created. Creation checked every prior sealed file, all 201 source files, the original work unit and the prepared source/model check. There are now 90 working interpretation files against 183 current identities, leaving 93 without native interpretation files. The last full whole inventory still reports 89 partial drafts and 94 missing identities. This types-and-logic stage does not substitute for the next consumer, dependency, whole-inventory and full-delivery work.

## 1. Exact source, admission and identity boundaries

The current source's SHA-256 is `36d484e269e9aeb79e2e4653874062157a07cc6a04d5edacfaa3502b441bbe76`. C53 admits this Definition for use under the full-definition queue. The source checker binds the exact decision, authorization, admission manifest and source-admission overlay, then verifies that the current version and content digest are selected. C53 records zero consumer activations. Admission of a Definition does not mean acceptance of this formal translation, execution of a real producer or a grant of artifact authority.

The embedded source names CAV2-D51, Canonical Artifact. Its exact admitted selection is lines 3522 through 3727 of the current external DEFINITIONS.md: 10,383 bytes with SHA-256 `3e9d50b1154b58b938c164725ac8fabed16914538dda579cf89c671c13c5becc`. The whole file is separately bound with SHA-256 `ecfbd64f334954809e83ffd5d4f9adfb759f39716de96c3ac1227d4ee869c6f8`. Both the coordinates and content match the admission record. This fresh observation does not rewrite the earlier Artifact formalization's observations from a different configured root. Coordinate equality is recorded; acceptance of whole meaning remains pending.

The Definition body still contains candidate-unadmitted metadata and a claim ceiling saying it is not admitted. Its current snapshot supplies the admitted-current decision overlay. The normalization artifact remains a prototype scaffold with authority effect none. These postures are recorded independently. Source reconstruction, a later decision overlay and interpretation acceptance must not be collapsed into one status merely because they refer to related bytes.

## 2. Sorts, symbols and the modeled subject

There are 25 nonempty sorts, 11 constants, 71 total functions and 128 predicate/relation signatures, totaling 235 declarations. ArtifactReference is the carrier of selected subjects. InvariantReference identifies the governing invariant, while RepresentationReference names a machine representation. CanonicalKind and AuthorityKind are distinct sorts linked by an explicit correspondence function. Durability, OwnerReference, ProducerReference, ProcessReference and ProcessVersionReference give the kind and origin fields separate typed denotations. OriginRecordReference and OriginStatementReference distinguish a provenance record from the statement it binds.

AssuranceLevel, SourceReference, ReceiptReference and ArtifactStateReference distinguish support classification, the owner-approved allowed-origin source, receipt evidence and exact state references. ActorReference, IdentityPolicyReference and SignatureReference carry the hypothetical future attestation links. ProjectionReference and DirectoryReference distinguish generated views from physical placement. SemanticIdentity, ScopeReference and TypeReference keep identity, applicability and classification separate. Token provides EMPTY, NONE and opaque nonempty reference markers.

Each sort has a nonempty supplied domain. This is a model representation requirement, not evidence that a real owner, producer, signer or artifact exists. Total functions provide nominated field values. Their existence alone cannot establish cardinality: additional relation tuples must remain observable. The binding relations therefore express exact correspondence for all selected artifact fields and origin fields. A reference handle guards declared, nonempty selections without authenticating their targets. An opaque reference is never silently interpreted as an executed process, verified signature or approved source.

## 3. Applicability, genus and governing invariant

ArtifactApplicable is equivalent to ArtifactInScopeDeclared for the selected candidate scope. Every applicable artifact has eighteen exact nominated field bindings and declared, nonempty reference targets. The effect field equals NONE. These obligations apply to selected subjects; outside references remain available to test that the theory does not accidentally prohibit unrelated declarations everywhere. The outside-directory control demonstrates that a prohibited selected-artifact inference may be present on an outside subject without changing theory satisfaction.

The governing invariant is a separate reference. Every selected artifact points to CURRENT_INVARIANT, whose identity is INVARIANT_TARGET, whose scope is SHARED_SCOPE, whose type is INVARIANT_TYPE and whose source is D51_SOURCE. INVARIANT_TARGET and ARTIFACT_SIBLING are distinct constants. This prevents the shared D51 lineage from merging the normalized invariant into its Artifact sibling. The artifact's own semantic identity and type remain separate fields; they are not forced to equal the invariant's identity and type.

Missing and conflicting field relations fail even when their total selectors retain valid values. Wrong invariant identity, scope, type, source and reference also fail. These are local declaration checks. They do not prove that an actual registry maps the invariant to this source, that every relevant artifact falls inside the scope, or that a shared identity carrier has accepted the same denotation. Those source and identity correspondences remain owner-review findings.

## 4. One declared machine representation and exact state

Every applicable artifact nominates one machine representation. That representation belongs to the same artifact and binds its exact state and type references. MachineCanonicalDeclared is equivalent, over the entire supplied representation domain, to equality with that nominee. This expresses exactly one declared representation for each selected subject. It does not merely say that a selector returns one value; a second relation tuple is visible and fails the theory even when the original nominee is unchanged.

The hostile controls add a hidden second representation, remove the canonical relation and independently change the representation's artifact, state or type. Each fails the corresponding necessary declaration obligation. A valid model can still have many artifacts and representations, including an outside artifact. Uniqueness is scoped to an artifact, not a claim that the entire repository has one canonical file or that two unrelated objects cannot share a format.

The representation reference is an opaque denotation. ArtifactStateReference is also an opaque state identity, with explicit equality where exact binding is required. Neither entails a digest calculation, content integrity, deterministic serialization, filesystem completeness or source fidelity. The actual RepresentationBytes and TypeResolution queries remain outside the theory. A real completeness check must bind the universe of governed representations; the finite model's enumerated domain cannot prove that no omitted file exists.

## 5. Generated human views and convenience labels

A selected projection has a declared, nonempty reference and an applicable artifact subject. Its source equals that subject's nominated machine representation. Its effect is NONE and it is not declared canonical. GeneratedProjectionDeclared is an exact relation over projection, artifact and representation references. The complete relation exposes alternative subjects or sources that would otherwise be hidden behind a total projection selector. Two baseline witnesses distinguish a human view from a convenience label, both generated from the same selected machine representation.

HumanViewDeclared and ConvenienceLabelDeclared provide witness categories rather than a globally exhaustive projection taxonomy. Removing either category leaves the primary theory true while failing the relevant required-population check. This demonstrates the separation between consistency of declarations and coverage of review scenarios. The theory does not require every projection to be both a human view and a label, or collapse the two categories into one identity.

Controls reject a projected view that claims canonical status, a source mismatch, a missing generated relation and an external-effect token. Actual projection correctness, regeneration freshness and byte correspondence remain independent outcomes. The source checker does regenerate this Definition's own human projection using three isolated pure functions; that concrete result is evidence about these selected source bytes. It is not a universal theorem that every generated artifact view is correct or current.

## 6. One origin record and exact origin tuple

An applicable artifact nominates one origin record, whose artifact endpoint equals the subject and whose owner equals the artifact owner. The record supplies producer, process, process-version and statement references. All six origin fields have exact singleton binding relations. OriginRecordForDeclared is equivalent to the record nominee across the supplied origin-record domain. A hidden second origin record therefore fails without relying on a count token or trusting a selector to report all records.

The allowed origin's producer/process/version tuple is deliberately different from the complete origin record. An allowed tuple does not supply the artifact endpoint, statement, owner or receipt; the exact record does. Controls change individual origin fields, omit bindings, substitute an owner or artifact endpoint and insert an additional record. The failures distinguish malformed record structure from a source claim that a process actually ran. The word process-born never becomes evidence of observed process execution.

These references are declarations only. The interpretation creates no real origin record, authentic owner statement, producer output, process run or versioned execution receipt. Authenticity and provenance completeness remain queries. An actual source-to-record map must explain how a producer reference resolves, how the version belongs to the process and how the exact statement is associated with artifact-state bytes. Whole prior Provenance and Artifact theories are not imported to manufacture those correspondences.

## 7. Set-valued eligibility and owner-approved sources

AllowedTupleDeclared has five arguments: kind, producer, process, process version and allowed-origin source. For a selected artifact, AllowedOriginDeclared is equivalent to membership of its exact origin tuple under its kind and source, together with currentness, owner approval, noncandidate source posture, producer admission and noncandidate producer posture. The source nominee also equals the kind's allowed-origin source, with an exact KindOriginSourceBindingDeclared relation. This makes the current source part of eligibility instead of treating an arbitrary textual origin list as sufficient.

The allowed set may contain several producers for the same kind, process, version and source. The baseline includes two alternatives, and the MultipleAllowedOriginTriples population witnesses their distinct producer identities. Removing an alternative preserves the theory but fails that required witness. The source rule is set-valued eligibility with one exact artifact origin, not a global one-producer policy. Two blocked subjects use a candidate producer and remain noncanonical even though other necessary declarations are present.

Negative controls remove allowed tuples, currentness, owner approval or producer admission while retaining the claimed allowed-origin result. Another claims eligibility for the candidate producer. These fail. Real admission, currentness and source authenticity are separate outcomes: declaration predicates do not authenticate an owner decision. The exact resolver, admission carrier and source-to-origin map remain pending; no real producer is activated by this candidate.

## 8. Kind inheritance and authority-kind inclusion

Artifact authority-kind classification, durability and type equal the corresponding fields derived from its nominated canonical kind. They cannot be independently selected by an artifact while keeping the kind fixed. Coherent hostile changes update the artifact field binding before testing inheritance, so a failure is attributable to the kind derivation rather than just a stale relation. This gives a necessary reading of the source's prohibition on freely choosing authority classification or durability.

The source says CanonicalKinds includes AuthorityKinds while not every canonical kind bears authority. Because these are distinct sorts here, inclusion uses an explicit authorityKindCanonical function. Every declared AuthorityKind member maps to a declared CanonicalKind member with an exact binding relation. The baseline supplies one canonical kind beyond that image. Its required population witnesses strictness in the authored example; the primary theory does not assert a universally accepted extensional map or import a global kind registry.

An actual AuthorityKind definition identity is absent from the selected current identity set. The qualified Closed Authority Kind Invariant is selected as related context, while AuthorityKind, CanonicalKind and Durability remain explicit unavailable dependency labels. The candidate does not invent new canonical Definition IDs. Shared-kind denotation, injectivity where intended, enumeration completeness, schema alignment and whether every kind-derived classification has the same owner meaning remain unresolved findings.

## 9. Declared and integrity-bound origin assurance

DECLARED, INTEGRITY and ACTOR are pairwise distinct AssuranceLevel constants. HonestAssuranceDeclared is equivalent to the disjunction of the three specified support forms, and every selected artifact must have honest support. Declared support requires the exact owner and origin-statement pair to appear in OwnerStatementDeclared. This captures the current review mode in which an owner-declared statement is sufficient. It does not silently replace that posture with mechanically verified output, and does not infer that the owner declaration is true.

Integrity support requires a declared valid L1 receipt whose statement and artifact-state references exactly equal the origin statement and selected state. The baseline's integrity artifact demonstrates this support form. Controls remove the L1 validity declaration or change its statement or state link. They fail even though the receipt reference itself remains well sorted and nonempty. The support level is therefore more than an arbitrary label attached to a record.

Actual L1Verification remains outside the declaration theory. The receipt's exact references do not compute a hash, verify a signature, run a verifier or authenticate a verification result. The candidate authors no actual L1 receipt. The source's demand for exact statement and state bytes requires a concrete integrity map before a real receipt can discharge it. Declared support and integrity-bound support remain different forms with different carriers and claim ceilings.

## 10. Conditional future actor attestation and present limits

The actor-attested support form is defined conditionally for future subjects. It requires the selected artifact to be outside CurrentReviewArtifactDeclared, a declared valid L2 receipt, an identified actor, a current identity policy and a declared externally valid signature. The receipt must bind the exact statement, state, actor, policy and signature; the signature must bind the exact statement, state and actor. The baseline future witness is a hypothetical set of references and declaration tuples. It creates no signer, policy, trust store, signature or attestation artifact.

Present review artifacts cannot claim this level merely because its future structure is defined. A hostile control marks the otherwise completely linked future witness as current, and the theory rejects it. Other controls remove L2 validity, actor identification, policy currentness or external-signature validity, or independently alter each receipt and signature link. An unknown assurance-level token also fails. These checks expose incomplete or dishonest claims in the declared support structure.

Actual L2Attestation, SignatureValidity and IdentityPolicy outcomes remain independent queries. External cryptographic verification is not simulated by a true declaration predicate. Future-scope eligibility and correspondence to a real identity-policy receipt require owner decisions and accepted carrier maps. The theory's satisfiable future branch must not be reported as currently available attestation, nor may the currently unavailable level be erased from the source's defined future vocabulary.

## 11. Canonicalness, authority and excluded inferences

For applicable subjects, CanonicalDeclared is equivalent to canonical-kind membership, owner-origin admission, allowed origin and honest assurance. The normalized one-representation and generated-view obligations are conjoined with this D51-origin reading at the normative clause. The composition is explicit, with source precedence unresolved. The biconditional does not say that a selected object is authoritative, that its process ran, or that its statement is correct. It classifies a declared canonical artifact under the supplied interpretation.

Four required witnesses cover canonical true/false crossed with actual authority true/false. The model permits actual authority independently on a canonical artifact and on a noncanonical artifact. Canonical subjects without authority also exist. This shows independence rather than banning authority globally. Controls can independently supply any actual outcome on one canonical subject while other witnesses retain the countermodel population. The source's authority distinction is not implemented as a rule that all artifacts lack authority.

Seventeen selected-artifact inference predicates are excluded. They cover canonicalness granting authority or authoritative-source status, assurance proving execution, truth, correctness, validation, proof, trust or discharge, assurance granting promotion, adoption or publication, directory-based type or authority inference, process-born wording proving execution, confusing a kind enumeration with an artifact instance, and merging the D51 sibling. Each has a hostile true-tuple control. Actual support, classification and decisions are separate from these forbidden inferential shortcuts.

## 12. Source accounting, model evidence and open findings

All 24 selected nonempty source-string units have exact correspondence: five encoded clauses, nine explanatory clauses and ten deferred clauses. The normative statement uses all nine primitive formulas. The formal expression uses genus, origin, kinds, assurance, canonicalness and exclusions. Applicability uses genus, assurance and canonicalness; one scientific boundary uses exclusions and canonicalness; the sibling boundary uses the invariant-target formula. These are five unique selected formula values. Testable conditions remain deferred in the interpretation even though separate concrete source checks evaluate identity, digests, schema and regenerated projection.

The finite verifier evaluates 160 authored controls: 42 satisfy the primary theory, 110 fail it and eight are rejected as malformed models. The prepared check observed at most 30,849 steps under the unchanged 100,000-step limit. Fourteen required populations make selected/outside subjects, support levels, blocked producers, multiple allowed origins, kind inclusion, projections and authority independence visible. The 128 signature populations remain unresolved rather than being silently inhabited by an accepted meaning.

Thirty-four qualified nonentailment queries each have a supplied theory-and-population model in which the universal actual-outcome target is false and the canonical-without-actual-outcomes witness is true. This shows that the declaration theory does not entail those actual outcomes. It does not prove their real-world absence, source fidelity or the full Definition. There are 57 concrete source checks, 27 source-query obligations and two exact 11,637-byte projections. Twenty-three findings remain unresolved. Native author, build, model and source producers all terminated with actual exit code zero; no failed native producer or preparation attempt is concealed.

## 13. Detailed DAG and the continuation boundary

The graph is the work dependency DAG for delivering this candidate. It is separate from the repository's semantic-use graph, which may contain existing cycles. Qualified direct dependencies are selected by exact current version and digest. Sixteen identities provide related Definition, Artifact, Invariant, type, lifetime, authority, kind-invariant, provenance, source, projection, receipt and separation context. No whole prior theory is assembled into the primary theory. Shared denotations, missing identity counterparts and semantic cycles still need their own dependency review.

```mermaid
flowchart TD
 S[Exact C53 source D51 selection and CPM full audit] --> A[Native preflight]
 S --> T[Sorted declaration vocabulary]
 A --> B[Native correspondence and IR]
 T --> B
 B --> I[Required populations and controls]
 I --> C[Independent model and source checks]
 C --> R[Detailed thirteen-aspect review]
 R --> F[Fresh type checks and typed freeze]
 F --> V[Separate typed audit]
 V --> H[Current carrier and consumer inspection]
 H --> P[Qualified authority profiles]
 P --> D[Reachable dependencies]
 D --> J[Current whole inventory]
 J --> E[Six fresh delivery checks]
 E --> Q[Complete delivery review and candidate seal]
 Q --> N[Separate full delivery audit]
 N --> X[Next Derived Refresh definition]
```

The current carrier review must inspect the Definition contract, normalized scaffold, exact D51 selection and semantic.artifact-lifetime consumer without accepting maps from textual similarity. It must distinguish canonical-kind enumeration from an artifact instance, declared source and producer admission from authentic decisions, an origin-support level from actual verification, and generated views from the sole machine representation. C53 overlay versus body metadata, prior Artifact source-root observations and future-L2 availability are explicit cross-definition findings.

The typed freeze binds sixteen inputs and this review after three fresh checks. Its independent audit is evidence for the candidate stage only. Full delivery still requires consumer correspondence findings, qualification profiles, current reachable dependencies, current whole inventory, six fresh checks, complete delivery review, an immutable seal and a separate full audit. Derived Refresh may be created only after that actual full audit, followed by Four Facet Artifact Invariant in the original order. The episode goal remains active across all 183 current identities, 189 versions and 201 sources, with final whole review still required.

### Unresolved source and interpretation findings

'''
text+='\n'.join('- CPRI-FINDING-'+str(i).zfill(3)+': '+x for i,x in enumerate(analysis['known_losses'],1))+'\n'
assert len(text.split())>2500,len(text.split())
with (u/'REVIEW.md').open('x') as f:f.write(text)
with (u/'CONTINUATION.md').open('x') as f:f.write('''# Canonical Representation Invariant continuation

Definitions, types and logic stage: current C53 candidate.1 and exact admitted D51 section; 24 units fully accounted, five encoded, nine explanatory, ten deferred. Source fidelity pending, semantic readiness false, accepted whole translations zero, whole proofs zero. Preserve all 7,919 prior sealed files and the sixteen frozen typed inputs after the actual typed audit.

Next: current Definition/normalization/D51 and semantic.artifact-lifetime consumer inspection; explicit correspondence obligations; authority qualification profiles; static-only reuse checks; reachable dependencies; current whole inventory; six fresh delivery checks; complete delivery review; full candidate seal; separate audit. Actual representation completeness, owner-approved eligibility, kind correspondence, L1 and future-L2 receipt/identity maps remain unresolved. No canonical artifact instance, real receipt, signature, producer activation, migration or publication is requested.

Only after successful separate full delivery audit: F04-T.cal.definition.derived-refresh, then Four Facet Artifact Invariant. Keep the native goal active through the original episode and final complete explanation.
''')
with (u/'DELIVERY-CONTEXT.md').open('x') as f:f.write('''# Typed candidate delivery context

Working native interpretations 90; last complete inventory 89 partial/94 missing; observed 93 current identities without native T. Current whole inventory refresh pending. CPM full 7,919-file seal and actual successful separate audit precede native CPRI. Original scope 183 identities/189 versions/201 source files remains fixed. The review covers thirteen aspects and twenty-three unresolved findings. Candidate source fidelity pending, semantic readiness false, accepted whole translations zero and whole proofs zero. Prepared precheck and all four native producers actual exit zero; preparation/native failures zero. Full consumer/dependency/inventory/delivery work remains required before creating Derived Refresh.
''')
print(json.dumps({'review_words':len(text.split()),'review_aspects':13,'findings':len(analysis['known_losses']),'source_checks':len(source['checks'])},indent=2))
