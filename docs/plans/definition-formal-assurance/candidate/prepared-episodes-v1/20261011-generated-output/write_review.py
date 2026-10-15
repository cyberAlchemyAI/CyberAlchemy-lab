"""Thirteen-aspect explanation and detailed DAG for Generated Output types and logic."""
from pathlib import Path
import json
root=Path.cwd();u=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.generated-output';load=lambda n:json.loads((u/n).read_bytes());assert load('model-controls.json')['control_count']==279 and len(load('source-checks.json')['checks'])==46
s='''# Generated Output: types and logic review

This candidate interpretation selects `cal.definition.generated-output@1.0.0-candidate.1`, admitted-current by C65. It describes exact canonical input records, an exact governed generator version, reproducibility records, lineage and parity bindings, and the explicit Artifact Type contract exception for canonical status. The primary theory concerns necessary declarations. It does not run a generator, compute hashes, authenticate lineage, adopt a contract or grant authority. Source fidelity remains pending, semantic readiness false, source-owner accepted whole translations zero and whole-definition proofs zero.

The previous Four-Facet full delivery passed a separate actual audit before this native unit was created. Preflight verifies all 8,253 previously sealed candidate file hashes and all 201 source files. There are now 93 native candidate interpretations against 183 current identities, leaving 90 without native T files. The latest completed full inventory still records 92 partial drafts until the current consumer/dependency/inventory delivery is completed. Neither creating this candidate nor passing its finite controls closes the whole episode.

## 1. Exact source, admission and explanatory evidence

The selected Definition digest is `f54b29e0b52ffdc4c57eb5df8525f3c065c1545f664ffd479188657b10d0c9cf`. C65 is `CAL-DECISION-0065-INTEGRATED-LAB-DEFINITION-MODEL-ADMISSION`. Source checking binds its decision, exact authorization and exact selected Definition row. That decision admitted sixty Definition versions and activated no carrier or consumer. Its historical registry postimage is not treated as the current complete registry; the current snapshot independently selects 183 identities and 189 versions.

The body remains candidate-authored and says the term supplies meaning for review only. Its embedded review source retains candidate-unadmitted posture and a null source-admission reference. The current whole review file has digest `1c92c720e176027597db09579276f9ea6e1d13b3d52bda233f9b0c4543dcb5eb`, equal to the embedded whole-file selection. The later Definition admission overlay is retained without rewriting that earlier metadata or treating it as acceptance of this interpretation.

The domain example concerns regeneration of DEFINITIONS-INDEX.md from registry.json with exact byte parity. Here that example is explanatory and not executed. The only projection executed is the isolated pure Definition renderer. Current Artifact Type contracts, generator adoption, relation availability, ontology use and runtime behavior require their own evidence and owners.

## 2. Sorted vocabulary and qualification

The theory has 17 nonempty sorts, six constants, 75 total functions and 130 predicate/relation signatures, totaling 228 declarations. OutputReference identifies the subject record. InputSetReference separates plural input selection from individual InputReference records. GeneratorReference names the producer version, while RunReference names a declaration of one result. LineageReference and ParityReference separate ancestry/check records from run records. ArtifactTypeContractReference carries the conditional canonical-status contract.

ByteStateReference and DigestReference are different sorts. SemanticIdentity, VersionReference, OwnerReference, SourceReference, ScopeReference and TypeReference keep identity, version, responsible owner, source, bounded scope and classification independent. Token contains explicit EMPTY, NONE, MATCH and nonempty descriptions. Nonempty model domains and total functions are representation requirements; they do not prove that a real output, generator or contract exists.

All symbols are qualified by exact source version and the candidate scope. Each field has a typed selector and an exact binding relation so missing or conflicting declarations can be detected. Handles make empty references observable. Seventy-five selectors do not establish shared denotations with another theory. The declaration of a function is not a call to a real tool, and qualification is not a proof of source-owner correspondence.

## 3. Genus, scope and declaration classification

OutputApplicable is equivalent to OutputInScopeDeclared. Each selected output has exact identity, Definition version, owner, source, scope, type, effect, input-set, generator, generator identity/version/digest, state/digest, first/second run, lineage and parity bindings. The candidate record uses CURRENT_DEFINITION_VERSION, CURRENT_SCOPE, CURRENT_SOURCE and NONE effect. Its source is declared current and owner-approved. These are record declarations, with actual source currentness and owner fidelity kept as query targets.

GeneratedOutputDeclared holds for each selected output. Its classification formula ties it to in-scope posture, nominated input membership, governed generator, run, lineage and parity declarations. The full normative conjunction supplies the detailed necessary guards. The shorter formal/applicability clauses point to classification and inference boundaries without repeatedly expanding every field formula.

An outside output remains in the model to test scope. Prohibited inference attached to that outside subject does not fail the selected theory. This makes the boundary explicit without asserting that every object elsewhere in the repository obeys the same record shape. Actual output selection, identity uniqueness, scope completeness and source precedence still require reviewed correspondence.

## 4. Plural exact canonical inputs

Each selected output binds an InputSetReference. The set has exact nominee and source bindings, and InputMemberDeclared includes the nominee. Every declared member of that set has complete identity, type, version, owner, source, byte-state and digest records, is declared canonical, and names a declared current owner-approved source. The digest selector agrees with the declared digest of its byte-state selector.

The baseline includes two distinct canonical input references. Removing the additional member leaves the theory true but makes the required multiple-input demonstration false. Removing the nominee fails theory coverage. Adding an outside input with incomplete canonical/current posture fails. A total input selector cannot conceal missing membership or an invalid extra record.

The source says exact canonical inputs but does not prescribe ordering, duplicate-reference policy or a particular aggregate encoding. The candidate uses set membership with a nominated member as an explicit representation choice. It does not impose a universal two-input requirement or claim that the declared set captures every real generator dependency. Actual input canonicalness, ordering, completeness, aliases, byte fidelity and digest computation remain unassumed obligations.

## 5. Exact governed generator and version

The selected generator has complete identity, version, owner, source, code-state, code-digest and output-type bindings. GeneratorGovernedDeclared is required. Output generator identity, version and digest equal the corresponding generator fields, and output type equals the generator's declared output type. Code digest agrees with the declared digest selector for code-state. The generator source is declared current and owner-approved.

Hostile controls change output generator identity/version/digest, remove governed posture, change code digest or output type, remove exact field relations and add conflicting relations. These fail even when their references remain well-sorted. Type correctness is necessary but does not establish that two separately named versions mean the same thing, or that source code really matches the declared digest.

GeneratorGovernance, GeneratorVersionFidelity, GeneratorCodeFidelity and GeneratorExecution are separate actual queries. No canonical Generator Definition is invented: that label is unavailable in the current identity inventory. Related Artifact Type, Source, Provenance and Derived Refresh definitions provide qualified context only. The model neither installs a producer nor adopts a changed generator, and a shared name cannot silently merge versions.

## 6. Declared result state and digest coherence

GeneratedState is a total function of GeneratorReference and InputSetReference returning ByteStateReference. Each selected output's state equals that declared result, and its digest equals the declared digest of that state. These equations record necessary coherence for a reproducible product from the exact selected producer and inputs. They do not execute the producer, serialize inputs or calculate the digest.

Byte-state and digest references remain distinct. A changed output state with an unchanged digest label can fail the result equation; a correctly typed digest label still has no demonstrated computation behind it. The candidate assumes neither collision resistance nor injectivity of the digest selector. Equal labels cannot stand in for actual byte equality, and unequal references need not establish different real content without an accepted reference/content map.

This distinction is central to interpretation. A deterministic mathematical selector supplies one declared state for a pair of arguments, but actual reproducibility is a property of governed execution and its environment. OutputBytesFidelity, OutputDigestComputed, GeneratorExecution and Reproducibility remain actual targets. No renderer, build process, filesystem writer or real byte comparison is invoked by these formula evaluations.

## 7. Repeated runs and additional records

Each selected output nominates first and second RunReference values and declares RunForOutputDeclared for them. Every declared run for that output has complete generator, input-set, state, digest and source fields matching the selected output and producer. The baseline includes an additional run for the ordinary noncanonical output. An incompatible hidden run fails rather than escaping through the nominated selector.

Distinct first and second references are a required demonstration population, not a universal source axiom. A control sets both nominated runs to the same reference and adjusts the parity link coherently. The primary theory remains true while the distinct-run witness is false. This exposes why record repetition, two independent execution events and actual reproducibility require different evidence.

Additional complete run records are allowed. Removing the extra record preserves the theory but makes its demonstration witness false. Actual run-universe completeness, execution environment, nondeterminism and omitted results remain source-owner issues. The candidate does not fabricate two real runs to pass a checker. Run membership is a declaration, and all declared records are checked under the selected output scope.

## 8. Lineage records and checking responsibility

Every selected output nominates a LineageReference and declares its lineage link. Every additional lineage record for that output has exact output, input-set, generator, generator-digest and source fields. The baseline has a second complete lineage record for one output, demonstrating that nomination does not enforce unsupported uniqueness. Removing it preserves the theory while failing the additional-lineage population.

Changing an extra lineage record's output, inputs, generator, digest or source fails. Adding an outside incompatible lineage record fails. These controls expose endpoint coherence and source bindings rather than treating a lineage reference as self-authenticating evidence. Complete declared fields can still refer to fabricated or stale sources.

The source binds output to lineage and parity checks but does not specify a canonical lineage carrier shape or check algorithm. This candidate records a minimal explicit correspondence proposal. LineageAuthenticity and LineageCheckExecution remain independent actual queries, and accepted relations, endpoint identities, qualifier schemas, evidence authenticity and consumer interpretation remain pending. No current canonical Lineage Definition is fabricated and no check is run merely because a record names its source.

## 9. Parity records and MATCH posture

Each output nominates and declares a ParityReference. Every declared parity record binds its output, exact first/second run references, first/second digest references, MATCH result description and source. The digest fields agree with the corresponding run digests and with each other. The source field agrees with the selected output source. These are declared parity conditions on the supplied model.

Hostile controls change the output endpoint, nominate a run from the other output, alter either digest, replace MATCH or add an incompatible parity record. They fail despite well-sorted field values. The candidate therefore checks more than the presence of a nonempty parity handle. It also keeps the selected run records and their declared content equations coherent.

MATCH is a Token, not an authentic comparison receipt. ParityComputation and ParityCheckExecution remain actual outcomes. The record neither computes a hash nor establishes a real byte-for-byte comparison. The source's index-regeneration example may require stronger byte evidence in an accepted consumer map, but that example does not silently import an index algorithm or a validation-contract theory into this primary interpretation.

## 10. Conditional canonical-status contract

The source says Generated Output is not a second semantic authority and is canonical only when an explicit Artifact Type contract says so. The theory preserves both parts. It forbids the second-authority inference and, for canonical-declared outputs, requires an exact contract binding and contract link. Every declared linked contract on such an output has complete type, version, owner, source and nonempty explicit canonical-clause fields, declared admitted posture, declared canonical permission and a declared current owner-approved source.

Canonical status is not universally forbidden. The baseline includes one output declared canonical under its permitted contract. Conversely, permission does not force an output canonical: the ordinary output also links that permitted contract while remaining noncanonical. Controls make all selected outputs noncanonical or both canonical. Both satisfy the theory but lose the particular mixed demonstration populations.

Missing links, missing admission, missing permission, wrong contract type and incompatible additional contracts fail. Actual ArtifactTypeContractAuthenticity and CanonicalStatus remain unassumed. An opaque canonical clause or admitted marker does not perform admission, bind a real carrier or resolve the true meaning of canonicalness. This condition is necessary rather than an unsupported equivalence between contract permission and actual status.

## 11. Authority, actual outcomes and forbidden inference

Twenty-nine actual-outcome predicates remain outside the primary theory's assumptions. The baseline ordinary output has all actual outcomes false. The other output has independently supplied actual authority. Each nonentailment query receives a freshly evaluated theory-and-population model with false actual target and a true all-outcomes-false witness. This shows that necessary declaration records do not entail the queried actual properties.

Positive controls independently add each actual outcome to the ordinary output, including authority and canonical status. They preserve the primary theory while losing the all-outcomes-false demonstration. Nonentailment does not deny independent evidence or impose a ban on real outcomes. The candidate NONE effect is a record posture, with no actual effect predicate assumed from it.

Fourteen forbidden inference declarations prevent term/admission/schema success, reproducibility labels, lineage refs, MATCH, digest labels, projection labels or canonical status from proving execution, semantic preservation, general proof or approval. They also prevent universal noncanonicalness, forced canonicalness from permission and shared-generator-name version collapse. These boundaries preserve the source's separation of meaning from separately admitted carrier, relation, runtime and authority contracts.

## 12. Source correspondence and finite verification

All 21 selected source-string units have exact correspondence: ten encoded clauses, six explanatory clauses and five deferred clauses. The normative clause includes all ten primitive formulas. Shorter expression, applicability and boundary clauses use classification, exclusions and conditional canonical guards. Five distinct formula values avoid unnecessary repeated expansion while retaining the normative constraints. Three source tests, authority scope and claim ceiling remain deferred semantic clauses rather than actual execution assertions.

Eleven required populations exercise selected/outside outputs, plural inputs, distinct/additional runs, additional lineage, noncanonical output, explicit-contract canonical output, permitted-but-noncanonical status and independent authority. The 130 signature populations remain unresolved. The model verifier evaluates 279 supplied controls: forty satisfy the primary theory, 231 fail it and eight reject malformed model structures. Maximum prepared evaluation uses 11,657 steps under the unchanged 100,000-step limit.

Native input size is 214,840 bytes and qualified IR has 25,507 nodes, within unchanged byte/tree limits. Forty-six concrete source checks bind C65, the embedded review source, two identical 4,410-byte pure projections and 28 source/query obligations. No preparation or native producer failure occurred. Actual author, build, model and source commands terminate zero. Passing these checks remains bounded evidence and cannot establish source fidelity, accepted shared meaning or a whole-definition proof.

## 13. Detailed delivery DAG and remaining episode work

Eighteen exact current Definition identities provide Artifact, Artifact Type, Source, Provenance, Derived Refresh, representation, validation, authority, schema, facet and separation context. Generator, Generation, Reproducibility, Lineage, Parity and CanonicalInput are unavailable requested labels and are not silently introduced as canonical identities. Thirteen separately qualified comparison sources remain outside the primary theory. Source-owner precedence and shared denotations remain pending.

```mermaid
flowchart TD
 S[Exact C65 source and F4 full audit] --> A[Native preflight]
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
 N --> X[Next Projection Specification definition]
```

This is the unit's work dependency DAG, not a proof that the semantic-use graph is acyclic or closed. Three fresh type checks precede a sixteen-input freeze and a separate actual audit. Full delivery then requires current carrier/consumer correspondence, qualified mapping obligations, profiles, static-reuse checks, dependency selection, current whole inventory, six fresh checks, the full review, a candidate seal and a separate full audit. Projection Specification native creation waits for that audit.

The current GeneratedOutput/v2 carrier is admitted-current by C74A and binds the exact Generated Output Definition. Its existing payload names generator, input, output-digest and reproducibility-receipt references. Exact correspondence to this interpretation's input-set, run, lineage, parity and canonical-contract fields remains a later consumer obligation. Carrier shape alone cannot establish authentic references, computed digests, check execution or canonical status.

The original episode remains 183 identities, 189 versions, 201 source files, 121 tasks, 511 planning edges, 797 work units and 36 frontiers. Accepted whole translations and whole-definition proofs remain zero. Its eventual complete review must explain every definition, type, formula, population, source correspondence, consumer map, authority boundary, dependency and proof obligation across that scope. This typed stage is concrete progress toward that episode, with its completion and claim boundaries recorded precisely.

### Unresolved source and interpretation findings

'''
for i,description in enumerate(load('clause-analysis.json')['known_losses'],1):s+='- GO-FINDING-'+str(i).zfill(3)+': '+description+'\n'
assert len(s.split())>2500
with (u/'REVIEW.md').open('x') as f:f.write(s)
with (u/'CONTINUATION.md').open('x') as f:f.write('''# Continuation after Generated Output types and logic

Keep the original183identity episode active. After the separate typed audit, inspect exact current GeneratedOutput/v2,Definition,ArtifactType and relevant Source/Provenance/representation meanings. Test carrier shape separately from authentic input/generator/run/lineage/parity and canonical-contract maps. Preserve canonical permission as necessary rather than automatic or universally prohibited.

Then prepare qualified profiles,static-only reuse,reachable dependencies and the current93draft inventory. Run six fresh checks,write the complete delivery review,seal all candidate files and execute a separate exact full audit. Only then begin Projection Specification native types/logic,followed by Representation Revision and Schema Evolution Invariant in the existing queue. Source-owner acceptance,shared consistency,cycle classification andwhole proof remain downstream.
''')
with (u/'DELIVERY-CONTEXT.md').open('x') as f:f.write('''# Generated Output typed-stage context

Local candidate SWU F04-T.cal.definition.generated-output. Exact C65 current candidate.1 source;source review,body and admission overlay remain separate. All8253priorsealed files preserved before native creation. Typed precheck and actual native producers pass with unchanged checker budgets and no retained failures.

Native packet has21source units,10encoded,6explanatory,5deferred clauses;17sorts,6constants,75functions,130signatures,228declarations;11required and130unresolved populations;18direct semantic uses and29nonentailment queries. 279controls and46source checks pass;28source/query obligations remain bounded. Sixteen typed-stage inputs are frozen only after three fresh checks and receive a separate audit.

There are93native drafts and90missing;the last full inventory remains92partial/91missing until refreshed. Original183identities189versions201sources/121tasks511edges797SWUs36frontiers remain unchanged. Whole translation acceptance andproof zero,source fidelity pending,semantic readiness false. Current carrier/consumer alignment,full inventory/fullseal/fullaudit are still required.
''')
print(json.dumps({'review_words':len(s.split()),'aspects':13,'findings':22,'DAG_nodes':17,'DAG_edges':17,'source_fidelity':'pending'}))
