from pathlib import Path
import json
root=Path.cwd();unit=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.artifact-surface-classification';p=Path(__file__).resolve().parent
review='''# Artifact Surface Classification: candidate types and logic review

This review explains the exact candidate interpretation of cal.definition.artifact-surface-classification@1.0.0-candidate.2. Native author, build, model and source producers returned zero with empty stderr. The current result is partial candidate verification. Meaning acceptance, consumer correspondence, reachable dependency closure, full delivery and a whole Definition proof remain open. Definitions, types and logic precede carrier implementation. The episode retains 183 current identities, 189 versions and 201 source files; adding this interpretation does not reduce that denominator.

## 1. Definition identity, source version and authority

The selected meaning is the current C53 source at authority/definitions/candidates/0010-artifact-surface-foundation-revision/definitions/artifact-surface-classification/v1/definition.json. Its SHA256 is 552b583d5bc7efb4567fde4483064fbd63275963e4b79cf0da3cc6c16f3cdc83. Selection binds an exact version, path and content digest. A similarly named predecessor is a separate source; a matching identity alone cannot substitute its bytes or admit this translation. C53 meaning admission is observed independently of the candidate formalization's pending fidelity review.

The source describes each governed file's job within a package. A canonical artifact instance has different obligations from a component, generated projection, evidence file, fixture or transient state. The interpretation makes these obligations explicit while leaving actual role correctness and actual admission independently observable. Necessary declarations do not issue an authority grant. Current registry selection, embedded lifecycle posture, historical admission overlay and candidate interpretation status have separate evidence fields.

The native context preserves Lifetime's 7,270-file full candidate seal and its separately successful audit. Preparation scripts and command captures are durable external context inputs. No canonical Definition, admitted registry, private runtime or live consumer is changed by this work. The review discusses intended denotations; it does not record source-owner acceptance. The formalization goal stays active after this typed stage.

## 2. Types, constants and versioned keys

Eight nonempty sorts distinguish PackageReference, GovernedFileReference, SurfaceRole, RegistryReference, ArtifactTypeReference, ArtifactTypeKey, PackageHomeReference and Token. The distinction prevents a package role from being passed as a type, or a type result from being used as a role. Every declaration is qualified by exact source version and interpretation scope before evaluation. There are eight constants, thirteen total functions and thirty-eight predicate or relation signatures, making sixty-seven declarations overall.

Six distinct constants name INSTANCE, COMPONENT, GENERATED, EVIDENCE, FIXTURE and TRANSIENT. EMPTY is a Token used by reference guards. CANONICAL_MANIFEST_TYPE is an ArtifactTypeKey containing the exact versioned manifest descriptor. ArtifactTypeKey deliberately describes the versioned key rather than asserting that an identity and its version are interchangeable. The earlier source-only proposal's ArtifactTypeIdentity terminology is refined here without changing that frozen proposal.

The package functions select a home, registry and manifest file. selectedRole takes a package and file; selectedResolvedType takes the same pair and returns a type reference. typeKey returns a versioned descriptive key. Seven handle functions support local nonempty guards. These functions are mathematical total selectors over the supplied domains. Their presence does not discover files, authenticate references or establish global key injectivity. A positive control explicitly permits distinct type references with one descriptive key when the selected declarations remain exact.

## 3. Genus, applicability and manifest self-entry

GENUS identifies the selected package scope through equivalence between PackageApplicable and PackageInScopeDeclared. For an applicable package it requires a nonempty package handle and declared, nonempty home, registry and manifest-file references. CanonicalPackageHomeDeclared binds that exact selected home. ManifestSelfEntryDeclared and GovernedDeclared include the selected manifest itself. Its selected role is INSTANCE, and its selected type's key is exactly CANONICAL_MANIFEST_TYPE.

These obligations prevent a superficially complete file list from omitting the manifest that claims to govern it. They also reject a manifest mislabeled as a fixture or component, a missing self-entry marker, an undeclared home or an incorrect manifest type key. The self-entry rule refers to the supplied manifest reference. It does not infer that a file named package.json is the correct manifest, establish uniqueness of every package home or prove that the inventory exhausts all governed files.

Scope remains visible rather than silently universal. An outside package is required in the finite witness, and empty handles outside selected scope can be permitted. Such controls distinguish failure of a selected necessary obligation from an unrestricted claim about the entire repository. The independent-authority package in the witness has its own manifest and home, so authority independence is illustrated without accidentally relying on an implausible shared manifest. Its authority is independently supplied, not derived from the package's classification.

## 4. Role vocabulary and exact explicit assignments

VOCABULARY makes the six role constants pairwise distinct and equates SurfaceRoleDeclared with membership in that exact vocabulary. A fabricated seventh declared role fails. Collapsing COMPONENT into INSTANCE also fails. The logic does not require that every possible value in a mathematical domain be selected by a package. Recognized vocabulary, selected assignment and correctness of that assignment remain different questions.

CLASSIFICATION applies to each applicable package and governed file pair. It requires a declared nonempty file reference and recognized selected role. Crucially, RoleAssignmentDeclared is a ternary relation over package, file and role. For every role value, its tuple holds exactly when that value equals selectedRole for the same package and file. Consequently there is one explicit declared assignment, rather than uniqueness merely being hidden inside a total selection function.

Removing any of the seven primary governed-file assignment tuples fails a negative control. Adding a second distinct role tuple fails another. Changing the selector without changing the explicit declaration also fails. These controls test the relationship between declarations and selectors; they do not validate the real job of the selected file. A file handle or extension can change without automatically changing its role. There is no path-to-role function, and directory membership alone supplies no canonical-subject qualification.

## 5. Canonical subject scope and component participation

For a selected governed pair, CanonicalSubjectDeclared is equivalent to the selected role being INSTANCE. COMPONENT, GENERATED, EVIDENCE, FIXTURE and TRANSIENT therefore cannot gain canonical-subject qualification merely by participating in a package. A schema or validator may be a declared component without being independently represented as an Artifact instance. The theory requires a second canonical instance beyond the manifest, avoiding an interpretation in which self-entry exhausts every possible instance.

The source writes canonical_subject(f) alongside package-relative role_P(f). This candidate uses CanonicalSubjectDeclared(P,f), an explicit package-relative reading. A multiply referenced file may expose a tension between local package participation and a global canonical home or global subject identity. The candidate does not resolve that tension by asserting global role uniqueness, globally unique homes, or universal file subject status. SURF-FINDING-008 routes this scope choice for source-owner and package-owner review.

The boundary is consequential for reuse. A file referenced as evidence in one package could have an independent canonical representation elsewhere, but the current local predicate cannot establish that external status. Conversely, the source might intend canonical subject status to be global, requiring a different relation or mapping. Neither reading is silently accepted here. The separate outside-file controls demonstrate the selected theory's scope and make clear that they are not evidence that a real external file has no obligations.

## 6. Unique declared type resolution and admission

Each selected canonical instance requires a declared nonempty ArtifactTypeReference and ArtifactTypeKey. ArtifactTypeAdmittedDeclared binds the nominated reference to the package's selected registry. For every candidate type reference, ResolvedTypeDeclared(registry,file,type) holds exactly when it equals the nominated selectedResolvedType. This relation therefore has one exact result for that selected registry and file. It is stronger than recording only a total result function while leaving contradictory resolution tuples possible.

Negative controls remove a resolution tuple, add a second result, change a registry without matching declarations, use an undeclared type, or substitute a wrong manifest nominee. These fail the necessary theory. A positive registry-change control supplies the corresponding declared resolution and admission tuples and passes. Extra resolution tuples in an unselected registry remain outside the selected requirement. The manifest's exact type key is additionally guarded by GENUS, while other canonical instances may nominate a different type.

Declared admission and declared resolution are representation assertions. SurfaceActualTypeAdmission and SurfaceActualTypeResolution remain separate predicates. Successful finite evaluation does not execute a resolver, query an authenticated registry or accept an Artifact Type. Shared registry/file references across packages could impose compatibility through the relation; a future accepted correspondence must examine that scope rather than importing a global policy by accident. The following Artifact Type Registry and Artifact Type Resolution units must receive their own exact definitions and logic.

## 7. Transient state and dependency exclusion

TRANSIENT excludes CanonicalDependencyDeclared for an applicable, governed file whose selected role is TRANSIENT. A selected transient state cannot satisfy the candidate declaration of a canonical dependency. The rule follows the exact scientific boundary condition. It does not expand into a ban on every component, generated representation, evidence file or fixture participating in validation. It also does not declare all nontransient dependencies actually satisfied.

A negative control marks the selected transient file as a canonical dependency and fails T. A positive control declares a dependency on a nontransient file while leaving actual dependency satisfaction false. Another control places a transient dependency outside selected package scope and passes the selected theory. The latter is an observation about scope, not a permission to use transient state in a real canonical dependency path. An accepted consumer map must define how applicability and membership are established before these results can guide implementation.

The unit's temporal boundary is deliberately modest. TRANSIENT is a surface job here, not the complete Artifact Lifetime theory. No effective instance durability, retention schedule, retirement chronology or source history ordering is inferred from the role tag. Lifetime and Artifact remain separately frozen interpretations. Their pending default/effective durability mapping is preserved instead of being resolved through an accidental cross-unit equivalence.

## 8. Populations, T and I, and outcome independence

There are eleven required populations and thirty-eight unresolved populations. Required populations witness a selected package with all twenty-two actual outcomes false, an outside package, an outside governed file, a canonical nonmanifest instance, an independently authoritative selected package and each of the six selected roles. Each required population has carrier PackageReference. Unresolved populations preserve pending denotations and inhabitation questions for the signatures; they are not silently changed to accepted requirements.

T contains the encoded necessary formulas. I contains the required population statements. The checker evaluates them separately and reports both results. A mutation can violate T while leaving I inhabited, or change a required role witness as well as a theory guard. Treating their two truth values as one would obscure why the candidate fails. The controls retain complete qualified models and model digests so these differences can be inspected again.

The selected package without actual outcomes supplies a counterexample to each universal actual-outcome target. A second package has separately supplied authority and a distinct manifest/home, establishing that the interpretation neither grants authority nor rules out supported authority. Further positive controls turn individual actual predicates true without changing the necessary classification theory. These examples support bounded independence claims for the authored model; they do not prove independence for every accepted real-world interpretation or discharge owner fidelity.

## 9. Source accounting and unresolved translation choices

The source denominator is twenty-seven nonempty string-leaf units. All twenty-seven are mapped to exact selectors and excerpts: eight encoded clauses, nine explanatory clauses and ten deferred clauses. Repeated formulas across distinct source spans remain distinct accounting entries. Five unique encoded source formula values use four primitive theory formulas. Coverage of a string-leaf inventory is not the same as having a complete accepted translation of every sentence.

The interpretation records no assumptions and no assumption links. Twenty named owner findings keep the losses explicit. The source precedence review remains pending, as do population reviews. Thirty-three source-query obligations bind exact excerpts and digests to actual-outcome targets. They distinguish an encoded necessary declaration guard from the actual target, which is never inserted into T. Exact character accounting prevents a scientific boundary or explanatory qualifier from disappearing during simplification.

Local upstream Definition, Artifact Type, Canonical Package Home and historical Surface predecessor bytes are checked. The old predecessor's embedded candidate-unadmitted posture is kept distinct from its admitted-historical snapshot overlay. These observations prevent stale source selection and lifecycle conflation, but cannot settle the intended canonical_subject scope, actual inventory completeness, registry authority or owner meaning acceptance. Explanatory paths and labels stay explanatory even when the notation resembles a practical repository layout.

## 10. Finite controls, malformed structures and replay

The native suite contains ninety-five controls: thirty-one satisfy T, fifty-six fail T and eight are rejected before logical satisfaction can be claimed. Malformed structures cover an artifact-type result used as a role, missing signature symbols, a nontotal role function, an ill-sorted manifest constant, wrong relation arity, duplicate predicate tuples, an empty role domain and duplicate function tuples. Structural rejection has its own result code rather than being represented as an ordinary semantic false result.

The model verifier qualifies each declaration with source and scope, checks the model denominator and evaluates every encoded clause and required population. Twenty-two actual-outcome countermodels satisfy T and I with the selected target false and the required witness condition true. Each retains the complete supplied model, its digest and the evaluated target. Their mechanism is finite evaluation of authored structures. It is not automated theorem proving, exhaustive model search or a verified translation of all source meanings.

Fresh typed replay will run the interpretation contract, native model checker and native source checker against current bytes. Successful original producers are retained separately from replay captures. A freeze then binds sixteen exact typed-stage inputs, followed by a separate read-only audit. Changing a bound input would invalidate the receipt. The full delivery needs additional carrier, consumer, dependency and whole-inventory evidence after this stage; replay success alone must not stand in for those unfinished steps.

## 11. Source observations, projections and consumer work

The source checker completed fifty-five checks, including current exact source selection, C53 admission and authorization bindings, four local upstream source observations, six roles, manifest self-entry, type and subject boundaries, transient exclusion and thirty-three query obligations. Two pure Definition projections match the committed 4,853-byte source projection. Their SHA256 is 156aab592db1b6f5e0a4dcf4490351818e9887ba4e981abad0e3ec115c06ecdb. Pure rendering checks determinism and input preservation; it does not run a live package validator.

The source names cal.artifact-type.canonical-package-manifest/v1 and tooling/validators/artifact_surface.py as primary consumers. This typed stage checks those labels but does not claim either consumer was executed or aligned. The next stage must inspect exact current bytes, establish what each reads and emits, and identify the accepted semantic correspondence it would need. A schema field named role or artifact_type is insufficient to prove equivalence with these quantified relations.

Consumer evidence should distinguish representation-level manifest shape from complete governed inventory, role correctness, registry type resolution and conformance. Historical semantic bindings need exact version inspection before any drift finding is asserted. No accepted consumer map exists in this typed stage. The generic Definition carrier may test representation shape while its retention and consistency profiles remain separate. Neither its PASS result nor a generated Markdown file can substitute for actual package classification fidelity.

## 12. Dependency DAG, gates and remaining episode scope

Twenty-six direct semantic uses bind exact current Definition references. Their names include Artifact, Artifact Type, Artifact Type Registry, Artifact Type Resolution, Canonical Package Home, invariants, authority, evidence, validation and typed relations. Field labels without a current Definition identity are recorded as unavailable labels, rather than manufacturing registry entries. No whole prior package or type theory is assembled into this primary T. Reachable closure and the joint current inventory still require fresh evaluation.

The following plan is acyclic and has fifteen nodes and eighteen dependency edges. Source selection and scope decisions precede type and population work. T and I jointly precede finite controls. Source accounting and countermodels feed the typed freeze. Only that audited stage permits carrier and consumer correspondence work, followed by dependency and inventory refresh. Six fresh delivery checks, a full review, a candidate seal and its separate audit precede the next native unit.

```mermaid
flowchart TD
 S[Exact source and prior seal] --> A[Scope and owner findings]
 A --> T[Types and signatures]
 A --> P[Populations]
 T --> I[Primary T and required I]
 P --> I
 I --> C[Controls and malformed models]
 S --> B[Source accounting and projections]
 C --> H[Actual outcome countermodels]
 B --> R[Fresh typed replay]
 H --> R
 R --> E[Freeze and separate typed audit]
 E --> Q[Carrier and consumer maps]
 Q --> D[Reachable dependency closure]
 D --> F[Joint current inventory]
 F --> J[Six fresh delivery checks]
 Q --> J
 J --> V[Full review seal and separate audit]
 B --> V
```

Lifetime's last sealed whole inventory contains eighty-three partial drafts and one hundred missing current identities. This unit creates the eighty-fourth working interpretation; that count is a file observation until the new whole inventory passes. Artifact Type Registry is the next native priority after this full delivery audit. These local gates preserve the larger 183-identity episode and its final comprehensive review rather than presenting an eighty-four-unit subset as completed formalization.

## 13. Owner findings, evidence ceiling and completion criteria

The twenty findings below are unresolved owner routes, not automatic authorization to rewrite canonical sources. Each has exact source selectors in the correspondence packet. Package, file, registry, resolver and consumer owners must resolve denotations and scope with the Definition owner. Any accepted change must be translated into explicit typed obligations, population evidence, accepted correspondence and new validation without overwriting earlier frozen history.

'''
losses=json.loads((unit/'clause-analysis.json').read_text())['known_losses']
for i,loss in enumerate(losses,1):review+=f'- **SURF-FINDING-{i:03}:** {loss}\n'
review+='''
The typed-stage evidence supports exact authored declaration checks, supplied finite models, source byte selection and complete local string-span accounting. It does not support actual governed enumeration, earned canonical legitimacy, authenticated registry admission, resolver execution, semantic conformance, global consistency or promotion. Source fidelity is pending, semantic readiness is false, owner-accepted whole translations are zero and whole Definition proofs are zero.

Completion of this local candidate delivery requires current carrier and consumer evidence, explicit unresolved findings, reachable dependency and joint-inventory reports, six fresh checks, a full review, a seal and an independent audit. Completion of the whole episode additionally requires the remaining Definitions and its final complete explanatory review under the original denominator. Candidate delivery can pass with visible owner obligations; it must retain a partial status rather than mislabeling those obligations as proven meanings. Earlier independently sealed units and unrelated working-tree changes remain preserved.
'''
assert len(review.split())>2500,len(review.split())
with (unit/'REVIEW.md').open('x') as f:f.write(review)
texts={'CONTINUATION.md':'''# Artifact Surface Classification continuation

Definitions, types and logic remain first. The native candidate has 8 sorts, 67 declarations, 11 required populations, 95 controls, 22 countermodels, 55 source checks and 33 source-query bindings. C53 current candidate.2 meaning admission is distinct from this pending translation and candidate.1 historical overlay.

Keep explicit RoleAssignmentDeclared(package,file,role), exact unique declared registry/file type results, manifest self-entry and versioned ArtifactTypeKey. CanonicalSubjectDeclared(package,file) is an unaccepted scope reading for multiply referenced files. No path determines a role; no transient state satisfies a selected canonical dependency. Actual enumeration, admission, resolution, Conformance and authority remain independent.

Fresh contract/model/source replay, sixteen-input freeze and separate typed audit precede carrier and consumer maps, reachable dependencies, current whole inventory, six fresh delivery checks, full review, seal and separate audit. Continue Artifact Type Registry only after that full audit. Preserve 183 identities, 189 versions, 201 sources and the prior 7,270-file Lifetime seal. Goal active; fidelity pending; semantic readiness false; no whole proof.
''','DELIVERY-CONTEXT.md':'''# Artifact Surface Classification delivery context

Lifetime's full 7,270-file candidate seal and separate successful audit precede this native unit. Its last sealed inventory has 83 partial drafts and 100 missing current identities. This unit creates the 84th working interpretation; fresh joint inventory remains required for full delivery.

Current C53 source SHA256 552b583d5bc7efb4567fde4483064fbd63275963e4b79cf0da3cc6c16f3cdc83 is cal.definition.artifact-surface-classification@1.0.0-candidate.2. Two pure projections match the exact 4,853-byte source. Twenty findings keep source acceptance, canonical-subject scope, registry denotations and consumer correspondence pending. The review explains thirteen aspects and a fifteen-node, eighteen-edge DAG. Sixteen typed inputs will be frozen and separately audited.

Durable preparation inputs and Lifetime audit captures are source-bound. Native author, build, model and source producers passed without a retained failed Surface native attempt. Earlier units and their retained histories remain immutable. No accepted semantic consumer map, actual package inventory, live resolver execution or authority effect is asserted by this stage.
'''}
for name,txt in texts.items():
 with (unit/name).open('x') as f:f.write(txt)
state={'unit_id':'F04-T.cal.definition.artifact-surface-classification','goal_status':'active','source_fidelity':'pending','semantic_ready':False,'owner_accepted_whole_translations':0,'whole_definition_proofs':0,'last_sealed_partial_drafts':83,'working_drafts_observed':84,'remaining_without_working_draft_observed':99,'full_delivery_sealed':False,'native_producers':{stem:json.loads((unit/(stem+'-command-result.json')).read_text())['exit_code'] for stem in ['author','build','model','source']},'next_gate':'fresh typed replay, freeze and separate audit','original_scope':{'identities':183,'versions':189,'sources':201}}
with (p/'current-state.json').open('x') as f:json.dump(state,f,indent=2);f.write('\n')
print(json.dumps({'review_words':len(review.split()),'aspects':13,'findings':20,'working_drafts_observed':len(list((unit.parent).glob('*/t.json')))}))
