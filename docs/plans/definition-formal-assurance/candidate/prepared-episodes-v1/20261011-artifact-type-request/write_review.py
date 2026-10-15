from pathlib import Path
import json,sys
root=Path.cwd();u=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.artifact-type-request';sys.path.insert(0,str(u));import build_candidate as b
core=json.loads((u/'t.json').read_bytes())['payload'];counts=json.loads((u/'denominator.json').read_bytes());model=json.loads((u/'model-controls.json').read_bytes());src=json.loads((u/'source-checks.json').read_bytes())
text='''# Artifact Type Request: definitions, types and logic review

## 1. Exact target and verification boundary

The selected meaning is cal.definition.artifact-type-request@1.0.0-candidate.2, admitted-current by the captured C53 overlay. Its exact source digest is ba76127c0cc5c883c53ea2dc91a3618f2aa17bba921b04098c45b1ca2a11c912. This review explains an authored, partial, typed interpretation of that meaning. It creates no real Artifact Type Request, requested subject, usable Artifact Type, admission, registration or owner decision. Definition admission and acceptance of this translation remain separate claims.

Registry's actual separate full-delivery audit exited zero before Request's native author was run. The Request author preserved 7,509 prior candidate files and reverified all 201 captured source files. Native author, build, model and source producers each exited zero. The model checker evaluated all ten encoded source clauses, not just a simplified conjunction used for a convenient example. Owner source fidelity remains pending, semantic readiness false and mechanized whole-definition proof absent. The episode scope remains 183 current identities, 189 admitted versions and 201 source files.

## 2. Source authority and predecessor lineage

The scientific formal voice supplies normative meaning. The plain-language and domain voices explain it. Their Runtime Binding, Source Closure and Ontology Package examples cannot create a particular request or extend operational permissions. Every nonempty source string selected by the established source inventory policy has an exact character account. There are 27 source units and 27 mapped clauses: ten encoded, nine explanatory and eight deferred. Deferred source content remains visible rather than disappearing from the denominator.

C53's exact decision, authorization and manifest bindings are checked independently of the source's embedded candidate metadata. Three embedded upstream meanings have admitted-current bindings: Definition, Artifact Type and Validation. Request candidate.1 is different: its captured overlay is admitted-historical, while candidate.2 preserves candidate.1's embedded candidate-unadmitted posture and null source admission reference. Those are observations of different roles and times. Neither an embedded label nor a current registry lookup authenticates every historical execution.

The source checker verified all four local upstream byte bindings, the Definition schema and generator bindings, and two pure, deterministic projections without input mutation or a writer entrypoint. Both projections contain 4,642 bytes and have SHA256 d6199aa2c817c23234362113f080ff8d9bf0f25f7a3f0cde6ad0e5c31e748ef8. These checks establish representation fidelity for the selected local files; they do not establish accepted semantic correspondence or a live producer's current state.

## 3. Sorted signature and identity interpretation

RequestReference identifies the candidate intake record. SubjectIntentReference identifies the intended, not-yet-authored subject. ArtifactTypeReference identifies a proposed type reference or separate output candidate. These sorts cannot be equated directly in the typed logic. The source's Q != a and Q != T are therefore represented through three separately typed functions into IdentityKey: requestIdentity, subjectIdentity and typeIdentity. This makes the inequality well sorted and exposes its concrete correspondence for review.

The proposed type selector is a candidate modeling choice for the source's T notation. Its nonempty declared reference is an intent handle; it is not a claim that an exact contract already exists. The output candidate has an explicit relation and may differ from that proposal. No global identity-key injectivity, unique request identity, unique output candidate, filesystem identity rule or globally canonical namespace is asserted. A positive control permits two request references to share an identity key, preserving the unresolved alias policy.

All 139 declarations carry the exact source qualification and candidate scope. The 18 sorts have nonempty mathematical domains. Their inhabitation is a modeling requirement rather than a declaration that each corresponding real artifact exists. The two Token constants EMPTY and NONE are distinct: an absent reference and a declared lack of authority effect are different conditions. Total selectors provide nominated values, while explicit binding relations expose missing or conflicting values instead of concealing them in functions.

## 4. Candidate intake genus and declared content

RequestApplicable(q) is equivalent to RequestInScopeDeclared(q). Applicable requests require a nonempty request handle, a CandidateIntakeDeclared marker and nonempty mapped identity keys. The request identity differs from its intended subject and proposed type identities. Outside requests remain explicitly represented and are not forced through selected-request guards. Applicability is not inferred from a directory name, arbitrary metadata or a successful schema check.

Thirteen selectors nominate the subject intent, proposed type intent, bound registry, resolution observation, compatibility analysis, intended semantics, owner, package home, representation direction, validation purpose, discriminator path, discriminator value and dependency set. Each selected value must be declared with a nonempty handle. Each field has an explicit exact binding relation: for every value of its sorted domain, the binding holds if and only if that value is the selector's value. Adding a conflicting second binding fails even when the selector remains unchanged.

A declared owner field does not authenticate owner authority. A package-home field does not produce a canonical package. A validation-purpose field does not show that validation ran or passed. A representation direction does not prove projection fidelity. These descriptive sorts are proposed denotations and not new admitted Definition identities. Their concrete field maps remain owner review work.

## 5. Unresolved resolution and rejected exact reuse

Every selected request has an IntakeCreationDeclared marker, a resolution observation bound to its exact registry and subject intent, an UnresolvedResultDeclared marker, and a compatibility analysis bound to the same subject that declares rejection of exact reuse. The bound proposed discriminator must have no admitted-current match tuple for any ArtifactTypeReference. This is explicit absence in a relation, not merely an unresolved nomination function that could hide a conflicting match.

A negative control inserts one eligible current match while retaining all ordinary request fields and the unresolved observation; the theory rejects it. Other negative controls remove the resolution binding, remove the unresolved result, remove the compatibility subject binding, or remove rejected exact reuse. Changing only the nominated registry and its field binding also fails when the observation remains bound to the original registry. Matches in a different registry or under a different discriminator remain permissible.

This necessary declaration theory does not execute a resolver or compatibility analyzer. It does not prove that the search was complete, that every existing type was considered, that patterns were evaluated correctly, that observations are fresh, or that no admitted usable fit actually exists. Those actual outcome targets are separately typed predicates and remain outside the encoded theory. Concrete pattern matching and Registry v2's entry-versus-descriptor scope still need accepted maps.

## 6. Request effect and subject dependency separation

The selected request's declared authority effect is exactly NONE. ConsumedAsSubjectDeclared, AdmissionRequestDeclared, SelfRegistrationDeclared, SelfAdmissionDeclared and ConvenienceWideningDeclared must all be false for selected requests. For each dependency reference, SatisfiesSubjectDependencyDeclared(q,requestSubject(q),d) must be false. The request cannot stand in for its intended subject or satisfy a dependency that requires that subject.

This exclusion is deliberately scoped. A positive control permits a declaration involving an unrelated subject intent; the theory has no source-backed global ban on every possible dependency role of the intake record. The intake can still participate as evidence or a component of its own workflow. That permission is not a grant of subject authority or an accepted cross-definition composition. Carrier owners must map such roles explicitly.

The model contains an independent actual-authority observation in a separately identified context while every selected request retains NONE as its declared effect. RequestActualAuthority names an uninterpreted actual-outcome observation used to test nonderivation; it must not be mapped to an effect created by the request itself. The denotation of that predicate is pending. No countermodel or model population authorizes real authority, and no proof of a general impossibility of independently supported authority is claimed.

## 7. Subject authorship and exact type existence

The source says the intended subject remains unauthored until its exact type exists. The candidate represents the necessary guard SubjectAuthoredDeclared(requestSubject(q)) implies ExactTypeExistsDeclared(requestSubject(q)). A selected request with declared subject authorship and no exact-type-exists marker fails. Required populations include an unauthored subject and another subject with both declarations so the guard is exercised rather than checked only vacuously.

ExactTypeExistsDeclared is intentionally uninterpreted with respect to lifecycle state. The source sentence does not by itself decide whether existence means a candidate contract, an admitted usable type, a particular resolution state or another owner-approved contract boundary. Silently equating it with CandidateTypePostureDeclared or TypeAdmittedDeclared would hide that ambiguity. The candidate therefore retains it as an explicit owner mapping obligation.

Neither the guard nor the authored subject population creates an actual subject record. Actual subject authorship remains a separate target. The populations are mathematical witnesses designed to exercise the logical boundaries, not production fixtures or execution history. Resolving the exact-type-exists policy is required before any claim of whole source fidelity or operational subject creation can be accepted.

## 8. Draft components and exact dependency membership

A DraftComponentDeclared tuple for a selected request requires a declared nonempty ComponentReference, an AttachmentDeclared tuple, and absence of an AdmittedContractComponentDeclared marker for that component. This preserves draft schemas as attachments or declared request components. ComponentReference remains distinct from ArtifactTypeReference; the draft cannot silently become the requested subject or an admitted contract because it happens to be packaged with the intake.

The candidate uses AttachmentDeclared as its umbrella interpretation of attached or declared components. Owners must decide its precise correspondence to both source alternatives. Removing the attachment declaration or declaring the draft an admitted contract fails. An unrelated component's admission marker remains permitted, and removing all draft markers creates a required-population failure rather than a source-theory failure. Generic attachments without draft classification are not globally prohibited.

RequestDependencyMemberDeclared is equivalent to membership in the selected DependencySetReference. Every declared member has a nonempty declared dependency reference. Empty and populated dependency sets are both required authored witnesses. The source does not demand a nonempty dependency set, and exact declared membership is not proof of complete dependency discovery, availability or satisfaction. Adding an unbound member or omitting an exact member fails the declaration account.

## 9. Acceptance and a separately identified candidate output

For an applicable request, RequestAcceptedDeclared implies existence of at least one CandidateOutputDeclared tuple. Each declared output has a declared nonempty ArtifactTypeReference and identity key, differs in identity from the request and intended subject, has CandidateTypePostureDeclared, and lacks a TypeAdmittedDeclared marker. Acceptance does not turn the output into a usable admitted type.

A missing output, missing candidate posture, declared output admission, or output identity collapsed with the request or subject fails. A positive control permits two separately identified candidate outputs, because the source's existence obligation supplies no uniqueness theorem. The theory also does not require every accepted output to equal the nominated proposed type intent. Such equality would require a concrete accepted output mapping.

The accepted-request and candidate-output records in the model are declarations. Actual request acceptance, actual candidate generation, authenticated owner selection and actual type admission remain different propositions. The actual-candidate-creation query has a finite countermodel in which the declared acceptance and separate candidate output guards hold while actual creation is false. That establishes a limit of this authored theory, not a factual allegation about a real request.

## 10. Terminal alternatives and owner-treatment residue

A selected request declaring resolution, rejection or replacement must declare expiry or supersession. The disjunction is inclusive: either branch suffices, and both may coexist. Required populations exercise expiry without supersession and supersession without expiry. Negative controls reject terminal requests with neither branch. An additional expiry marker on an unterminated request remains permissible because the source does not supply a reverse characterization.

No clock, chronological ordering, authenticated replacement relation or actual expiration operation is invented. Source chronology and the mechanism of supersession remain review obligations. A terminal marker does not discharge subject admission or create output authority. Importing the whole Artifact Lifetime theory would require separate shared-denotation and dependency review, so this candidate uses only its scoped necessary declarations.

The retained residue requires owner selection before a real unresolved carrier receives Request treatment. OwnerTreatmentSelectedDeclared is present in the signature but is not assumed as an authenticated selection in T. Creating this Definition formalization is not creating a real intake or choosing that treatment for a carrier. This residue must be inspected with the operational carrier and consumers after the typed stage; actual owner selection remains one of the nonderivation targets.

## 11. Controls, populations and actual-outcome countermodels

The native checker independently evaluated 136 supplied controls against the compiled source-qualified interpretation. Thirty-eight satisfy T, ninety fail T as expected, and eight fail model structure before semantic evaluation. Structural cases cover wrong result sort, missing signature symbol, nontotal function, ill-sorted constant, wrong relation arity, duplicate predicate tuple, empty domain and duplicate function tuple. These are different evidence classes from a well-typed model in which a necessary guard is false.

Eleven required populations cover selected requests without actual outcomes, an outside request, independent actual authority, draft components, accepted separate candidate output, expiry and supersession alternatives, empty and populated dependency sets, unauthored subjects and the exact-type-exists guard. Eighty-five additional population obligations remain unresolved. These witnesses prevent central conditions from passing only because no relevant object was selected; they do not classify every real request population.

Twenty-four actual-outcome queries each retain a source-qualified target outside T and a true selected witness condition. The checker verifies T and all required populations while each target is false in its supplied countermodel. Targets include resolver execution, completeness, compatibility correctness, owner selection, subject authorship, candidate creation, expiry, chronology, dependency satisfaction, type admission, registration, conformance, validation, fidelity, authority and consumer alignment. Finite countermodels establish those particular nonentailment limits; they are not universal accepted proofs of the whole Definition.

## 12. Source account, review findings and continuation DAG

The source account preserves exact selectors, excerpts, digests, character spans and disposition for all 27 units. Actual-outcome obligations link their targets back to exact source clauses and never introduce targets as assumptions. There are no interpretation assumptions or hidden whole-prior-theory imports. Source precedence, dependency closure, owner review and semantic acceptance all remain pending.

Twenty named findings retain every candidate denotation and known loss. The finding table below is an owner-review queue, not evidence that the owner has accepted the proposed interpretation. Unavailable requested dependency labels remain descriptive sorts rather than fabricated canonical Definition identities. Current Registry's three unresolved consumer findings, including the seven operational-schema errors, retain their prior sealed evidence. Request does not erase or resolve them by adopting a convenient entry scope.

The following DAG separates source selection, typed declarations, logic, populations, controls, source correspondence, typed freeze, consumer maps, dependency closure, joint inventory, fresh delivery replay and final review. It is acyclic and contains fifteen nodes and eighteen edges. A candidate must pass a separate typed audit before consumer work. Full candidate delivery still requires current carrier/consumer observations, reachable dependency graph, joint inventory, six fresh terminal checks, complete delivery review, seal and separate delivery audit.

```mermaid
flowchart TD
 S[Exact source and prior seal] --> A[Scoped author and context]
 A --> T[Types and signatures]
 T --> P[Primary theory]
 P --> I[Required populations]
 I --> C[Controls and countermodels]
 A --> B[Byte and source checks]
 P --> H[Source correspondence]
 B --> H
 C --> R[Typed freeze and separate audit]
 H --> R
 R --> E[Carrier and consumer maps]
 E --> Q[Qualified comparison checks]
 Q --> D[Reachable dependency closure]
 D --> F[Joint inventory]
 F --> J[Six fresh delivery checks]
 J --> V[Full review seal and audit]
 H --> V
 E --> V
```

## 13. Remaining work and original completion criteria

This typed candidate is one unit in the original formalization episode. There are now 86 native T draft files, with the last full-delivery inventory still reporting 85 sealed partial drafts and 98 missing current identities. A fresh whole inventory has not yet evaluated the new Request draft, so those two observations must not be collapsed into an updated accepted denominator. Whole accepted translations and whole-definition proofs remain zero.

The next immediate work is to finish the typed review, perform the three fresh typed checks, freeze sixteen exact typed inputs and run a separate audit. After that, inspect the Artifact Type Request/v1 carrier and authority/artifact-type-requests intake path without executing a writer or creating a real request. Compare the carrier fields, owner selection treatment, accepted candidate output and lifecycle behavior with the source. Keep the current Registry v2 and current Resolution meaning separate from historical labels.

Then verify reachable dependencies and freshly evaluate every selected interpretation in the whole candidate inventory. Preserve every prior seal and every captured source byte, retain failed attempts visibly, and run the six actual delivery checks. Produce the full delivery explanation, seal its exact files and separately audit preservation and claim boundaries. Artifact Type Resolution follows Request in manifest order. The broader episode cannot be called complete while any required Definition, accepted source correspondence, dependency review, proof obligation or final aspect-by-aspect review remains missing.
'''
text+='\nCandidate review findings:\n\n| Finding | Pending correspondence or limitation |\n|---|---|\n'+''.join('| REQ-FINDING-'+str(i).zfill(3)+' | '+x+' |\n' for i,x in enumerate(b.LOSSES,1))
text+='\nExact sorted signature:\n\n| Symbol | Arguments | Result or role |\n|---|---|---|\n'
for n,s in b.CONSTANTS.items():text+='| '+n+' | constant | '+s+' |\n'
for n,(args,result) in b.FUNCTIONS.items():text+='| '+n+' | '+', '.join(args)+' | '+result+' |\n'
for n,args in b.SIGNATURE.items():text+='| '+n+' | '+', '.join(args)+' | declared predicate or relation; actual targets remain independent |\n'
text+='\nComplete source clause account:\n\n| Clause | Selector | Disposition | Exact source excerpt |\n|---|---|---|---|\n'
texts=dict(b.co.string_leaves(b.co.source_document(b.snapshot(),core['source'])))
for c in core['clauses']:text+='| '+c['clause_id']+' | '+c['source_selector']+' | '+c['disposition']+' | '+texts[c['source_selector']].replace('|','\\|').replace('\n',' ')+' |\n'
with (u/'REVIEW.md').open('x') as f:f.write(text)
with (u/'CONTINUATION.md').open('x') as f:f.write('# Artifact Type Request continuation\n\nTyped native author,build,model and source producers exited0. Next:three fresh typed checks,freeze16 inputs,separate typed audit. Then current carrier/consumer comparison,reachable dependencies,joint inventory,six fresh delivery checks,full delivery review,seal and separate audit. Last full Registry seal7509files/85partial98missing. Working native T files86; whole inventory refresh pending. Next Definition:Artifact Type Resolution. Owner fidelity,whole translations and proofs pending;goal active. No real Request,subject,type or authority effect created. Retained prepared syntax attempt1 before native creation; native author/build/model/source have no failed attempts.\n')
with (u/'DELIVERY-CONTEXT.md').open('x') as f:f.write('# Local-native Request SWU context pack\n\nTask:F04-T.cal.definition.artifact-type-request. Mode:lean selector evidence;no runtime delegation or handoff.\n\n| Obligation | Controlling evidence and selector | Disposition |\n|---|---|---|\n| Exact meaning | Source Definition /voices/scientific_formal and /scope | verified bytes;meaning map pending |\n| Prior gate | Registry receipt +manifest +successful separate full audit | PASS7509files preserved |\n| Scope | foundations-first-v1/swu-manifest.json Request row | output T.json;native candidate write scope |\n| Dependency gates | prerequisite A04,C01,E02 receipts in context.json | actual PASS current bytes |\n| Typed denotations | Request normative fields,identity inequality,boundaries | explicit candidate denotations;owner mappings deferred |\n| Source precedence | scientific formal voice versus explanation/notation | preserved;20findings pending |\n| Validation | prepared4scripts +native contracts,IR,verifier,correspondence | available;actual native4producers0 |\n| Claims and continuation | source claim_ceiling,residue +original183/189/201scope | candidate only;whole episode active |\n\nEight context items cover the selected task obligations; broad background and live consumers are excluded from this typed stage. No blocker-level user decision is required for reversible authored candidate theory. Exact-type-exists lifecycle policy,owner selection and consumer mappings are deferred and cannot become accepted semantic claims. Experiment harness not applicable;adapter none;handoff none. Evidence synchronization uses local candidate artifacts and outside-seal prepared current-state,with no canonical Definition,index or admission changes.\n')
print(json.dumps({'review_words':len(text.split()),'sections':13,'findings':20,'source_units':counts['source_units'],'goal_status':'active'},indent=2))
