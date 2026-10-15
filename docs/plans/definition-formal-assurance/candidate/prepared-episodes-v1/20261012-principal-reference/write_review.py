"""Thirteen-aspect Principal Reference explanation and exact staged delivery DAG."""
from pathlib import Path
import json,re
p=Path(__file__).resolve().parent;u=Path('docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.principal-reference');load=lambda n:json.loads((u/n).read_bytes());context=load('context.json');counts=load('denominator.json');analysis=load('clause-analysis.json');model=load('model-controls.json');source=load('source-checks.json');fresh=load('fresh-types-logic-results.json');assert all(x['exit_code']==0 and not (u/x['stderr']).read_bytes() for x in fresh)
s='''# Principal Reference: definitions,types and logic review

Principal Reference is formalized as a minimal governed reference to one Principal for accountability or authorization linkage. It preserves minimum stable identifier,kind,issuer or registry,resolution route and integrity data needed by a consumer. A reference resolves by declaration to one governed Principal or is explicitly unresolved. The Principal retains identity authority;the reference does not copy,mutate,authenticate or replace it. Authority decisions require separate current grant evidence. No real identity resolution,credential access,authorization or grant is performed.

Native creation followed Principal's full9,364-file seal and separate actual audit0. All prior sealed files and201sourcebytes remain hash verified. Working native drafts now number102among183currentidentities,leaving81withoutT. Last completed whole inventory remains101partialdrafts82missing until this packet's full delivery. Original183identities189versions201sources and121tasks511planningedges797SWUs36frontiers stay fixed. Accepted whole translations and whole-definition proofs remain zero. Source fidelity,shared denotations and semantic readiness remain pending;the full episode and final review stay active.

## 1. Exact source and C65 admission

The selected source is cal.definition.principal-reference@1.0.0-candidate.1,SHA7ca6bd645843a17ac21936da623f7ccff6b011f4d7051ad6e4ffd19121b1a16e. Its current admission is CAL-DECISION-0065-INTEGRATED-LAB-DEFINITION-MODEL-ADMISSION. Exact selection fixes the positive meaning under interpretation. A nearby Principal,Person Reference,carrier schema,issuer protocol or actual credential is not substituted for this source.

Source checking binds C65 decision,authorization,candidate,selected Definition digest and validation receipt. Current183identity189versionsnapshot validation is separate from historical counts in an admission decision. Definition admission does not resolve a Principal,instantiate a reference,access a credential,execute authorization or accept this formal translation. Type and instance effects remain separate.

The retained source body stays review-only under its positive admission overlay. Its actor-model-review remains candidate-unadmitted with exact local bytes,and the integrated consumer remains an observed source path. No operational map or runtime activation follows. Private routing read-first references stay path/hash metadata only;their content and meaning are not imported into primary theory. Canonical meaning remains the exact selected Definition,while source precedence and correspondence need owner review.

## 2. Sorted signature and qualified vocabulary

Sixteen nonempty sorts are proposed:ReferenceRecord,PrincipalReference,StableIdentifierReference,PrincipalKindReference,IssuerReference,RegistryReference,ResolutionRouteReference,IntegrityReference,ScopeReference,ConsumerReference,ReferenceUseReference,DataFieldReference,AuthorityDecisionReference,GrantEvidenceReference,TimeReference and Token. ReferenceRecord is the reference under this Definition;PrincipalReference denotes its independently governed referent nomination. This distinction prevents a reference record from silently becoming the Principal.

Seven constants include EMPTY Token and six minimal data-field class markers. Eighteen selectors and fifteen reference-handle functions give33totalfunctions. There are150predicate/relation signatures and206declarations. Descriptive types and field classes do not create new canonical identities or authenticate real values merely from their names.

Every required selected field has a declared target,nonempty handle and exact BindingDeclared relation matching its selector. Totality supplies a well-sorted finite value without proving the referent exists or is authentic. Symbols are qualified by exact source version and candidate scope. Similar names across other packets do not establish common denotation or import their whole theories. Missing,conflicting,undeclared and empty selected nominations fail independently of real lookup and authority.

## 3. Minimal governed reference genus

ReferenceApplicable is equivalent to ReferenceInScopeDeclared. A selected record is governed,bounded and minimal by declaration. Identity-backed or record-backed criterion is inclusive. Accountability linkage or authorization linkage is also inclusive. A reference may support either purpose or both without becoming a permission or authentication operation.

The source's minimal governed reference genus is represented by necessary declaration structure. A minimal flag alone is insufficient to prove actual purpose,consumer need or data minimization. Those have independently queried outcomes. The formal governed_identity_or_record implication and positive reference genus require source-owner precedence correspondence. No unaccepted physical carrier or global identity registry is inferred.

A selected reference may have no modeled consumer use. Required populations preserve that case without pretending that the finite model enumerates every real consumer. References may share a Principal and may be used by several independently identified consumers. No universal reference uniqueness or one-reference-per-Principal rule is invented. This keeps the source's one nominated referent distinct from a global cardinality assumption or a claim that every reference is already resolved.

## 4. Exact minimum metadata and optional origins

Selected references nominate exact stable identifier,Principal kind,resolution route,integrity data and governance scope. Identifier and kind are separate from the reference record's identity. Route is separate from a running resolver. IntegrityReference is a typed nomination rather than a computed cryptographic digest or authenticated byte binding. Actual fidelity and availability remain independent outcomes.

Issuer or registry presence is inclusive:issuer only,registry only or both may hold. At least one alternative is declared. Exact optional issuer/registry fields are guarded only when present. A reference cannot replace a required origin with an empty token,but an unused total optional selector does not fabricate an issuer or registry.

Positive controls omit an unused issuer binding on a registry-only record and an unused registry binding on an issuer-only record. Empty outside handles are allowed where no selected guard applies. These controls preserve the source's alternative rather than demanding both origins universally. Actual issuer/registry authenticity and their relationship to Principal authority require accepted maps. Governance scope remains separately nominated and is not automatically copied identity data or permission scope.

## 5. Resolved versus explicitly unresolved

Every selected reference has exactly one of two declared states:resolved or explicitly unresolved. Neither state is missing and both cannot hold together. These necessary state declarations preserve the source's test that a reference resolves to exactly one governed Principal or becomes explicitly unresolved. Actual resolver behavior and current state fidelity remain independent.

Only declared resolved scope activates the exact referencePrincipal field. The nominated Principal must be governed and retain declared identity authority. It has exact stable identifier and kind coordinates that agree with the reference metadata. A mismatched identifier or kind fails. Missing,conflicting,undeclared or empty resolved-principal nominations also fail.

Explicitly unresolved references retain minimum metadata while their total Principal selector may remain unused,unbound or have an empty outside handle. This avoids creating an imaginary identity to make a failed lookup appear complete. No global injectivity of identifiers or referents is imposed. Actual Resolution,PrincipalIdentityFidelity,KindFidelity and PrincipalIdentityAuthority queries are conditioned on declared resolved scope,so their countermodels cannot rely only on an unrelated unresolved reference.

## 6. Principal identity authority and independence

The referenced Principal remains the identity authority. A resolved nomination requires PrincipalIdentityAuthorityDeclared as a positive necessary condition. ReferenceIsPrincipal and ReferenceBecomesIdentityAuthority declarations are excluded. The reference therefore cannot replace its referent simply because a stable identifier or kind label is present.

Copying a full Principal identity record,mutating the Principal,authenticating it or replacing it are separately excluded inference/effect declarations. A legitimate minimum identifier/metadata nomination is distinct from copying the identity record. Source-owner maps must explain how that distinction applies to real payloads and governance metadata. The candidate does not inspect or duplicate actual identity contents.

Equal identifier/kind tokens provide declaration coherence rather than authentic identity equivalence. Independently grounded real outcomes remain possible;the boundary does not universally deny them. Actual no-copy,no-mutation,no-authentication,no-replacement and identity-authority outcomes remain independent targets. A supplied record may satisfy all necessary reference declarations while those real outcomes remain unproved. No Principal authority is transferred or executed by the model evaluation.

## 7. Six data classes and bounded minimization

Six constants identify stable identifier,kind,issuer,registry,route and integrity data classes. Selected references embed identifier,kind,route and integrity classes. Issuer/registry embedding agrees exactly with their presence declarations. All embedded classes are declared minimal,declared present and one of the six source-coordinate classes.

Embedded classes declared secret,credential or excess identity data are rejected. Unknown or unsupported classes also fail. A selected stable-ID class newly marked secret or credential fails even if the other fields are coherent. These are safe symbolic controls;no real credential,secret or personal identity record is accessed or constructed.

This whitelist is a proposed correspondence for primary reference data. Scope,privacy posture,owner and lifecycle can be separately governed metadata rather than copied identity contents. Owners must accept the distinction and the real content-classification criteria. A six-class shape does not prove every actual value is necessary,safe or authentic. Actual NoSecrets,NoCredentials,NoExcessIdentityData and consumer minimality remain independent outcomes rather than conclusions from a field label or flag.

## 8. Consumer-needed data and shared references

A selected ReferenceUseReference nominates exact reference and consumer fields. It is recorded,and the consumer is recorded. ConsumerNeedsFieldDeclared agrees exactly with the reference's embedded data classes for each selected use. Missing needed data or embedding a class not needed by that consumer fails. This makes minimum consumer need visible rather than inferred from a general minimal flag.

A shared reference may have multiple selected consumers when their declared needs are compatible. Required populations demonstrate different consumers using one reference. The candidate does not impose globally one consumer per reference. The exact compatible-need interpretation is an explicit proposed operational map;different projections,purposes and retention requirements need source-owner acceptance.

ConsumerNeedFidelity,MinimumDataFidelity and DataClassificationFidelity remain independently queried on selected use scope. Root ConsumerNeedMinimality is conditioned on a reference with an actual selected use. An unused optional reference cannot supply its counterexample. No source-owner minimum-need decision is fabricated from a record shape. The model retains exact declared need/embedding coherence while leaving real necessity,privacy,consumer purpose and data absence unsupported.

## 9. No credential,secret or excess identity content

A Principal Reference is not an authentication credential. It contains no reusable credential and proves no Person identity,Role,Assignment or authority grant by declaration. ReferenceContainsSecret,ReferenceContainsReusableCredential and ReferenceContainsExcessIdentityData are excluded. Source tests that no secret,credential or excess identity data is embedded contribute explicit data guards.

The safe negative models use symbolic data classes such as secretField and credentialField. They do not retrieve real passwords,tokens or identity records. The candidate does not invent a universal secret detector or claim that a string passing a schema is harmless. Real absence requires appropriate classification and accepted consumer/source correspondence.

Reference privacy is therefore separate from identity resolution,integrity and authority. A minimal identifier can be coherent while its actual privacy classification is unresolved. A nonempty integrity token can be recorded without proving a digest or authenticating a Principal. No Principal or Person Reference semantics are borrowed to turn the reference into a credential. These distinctions keep structural checks and safe symbolic examples from being presented as successful authentication or a real data-minimization assessment.

## 10. Authority decision and separate current evidence

Each selected AuthorityDecisionReference nominates exact reference,grant evidence,scope and evaluation-time fields. The decision is recorded. The evidence is separately recorded,resolved and independent of the reference. It nominates a governed Principal retaining identity authority and an exact scope equal to the decision scope. EvidenceCurrentAtDeclared relates it to the decision's evaluation time.

A resolved reference's Principal must agree with the evidence Principal. An unresolved reference does not fabricate resolution merely because independent evidence names a Principal. CurrentAt is a relation rather than an invented chronological order or one-time evidence function. Real validity intervals,revocation,currentness and authorization remain separate outcomes.

Every selected decision requires independent current grant evidence rather than inferring it from reference presence. Denial/unresolved decision interpretations remain explicit owner-review questions. The model does not execute a decision or grant permission from the evidence label. Missing separate resolution,independence,currentness,scope or resolved-Principal agreement fails. Actual grant-evidence resolution,validity,Principal/scope/time fidelity,owner authorization and effects are separately queried on selected decision scope.

## 11. Reference noninference and independent outcomes

Root boundaries exclude treating the reference as Principal,Person Reference,Role assignment,authentication credential or authority proof. They also exclude inferred Person identity,Role,Assignment,authority grant and authority from the reference. Parent meaning and Definition admission cannot grant instance effects or accept this translation.

Use boundaries exclude proving minimization from a consumer-need label,copying identity records,embedding reusable credentials,authenticating Principals and creating permission from reference use. Decision boundaries exclude using a reference as grant evidence or deriving current validity,authority,permission,authentication or external effects from declarations. Selected scope is explicit across all three carriers.

Actual outcomes remain outside primary T and are not universally prohibited. Positive controls supply them independently while preserving necessary theory. Outside objects can carry excluded flags without violating selected-scope obligations. Reference linkage may coexist with independently governed decisions and grants,which require their own evidence. No real Principal is resolved,authenticated,mutated or replaced,no credential is accessed,and no grant,permission or external action is created by this candidate.

## 12. Source account,controls and scoped queries

All24nonempty source units have exact selector and complete-character correspondence. Sixteen clauses are encoded,six explanatory and two deferred. Twelve primitive formulas cover genus,metadata,origin alternatives,resolution,minimal data,use,decision and three boundary scopes. Scientific notation,plain-language intuition and the principal-ref:def-owner example remain explanatory. Authority-scope and retained candidate claim ceiling remain deferred correspondence.

The native suite passes261controls:106T-true,147T-false and eight malformed-input rejections. Twenty-six required populations demonstrate selected/outside,identity-or-record,issuer/registry,linkage,resolved/unresolved,shared use,separate current evidence and independent authority. T and I are evaluated separately. Empty selected scopes or absent demonstrations can preserve theory while failing the episode's required population coverage.

Forty-six queries have supplied T-and-I countermodels. Seven root targets are conditioned on resolved state,issuer/registry presence or selected consumer use. Use and decision targets remain separately scoped. Sixty-six exact source-query obligations bind selectors,spans,hashes and query IDs without actual targets in T. Prepared maximum is41,174steps under unchanged limits. Source checks bind exact C65,local review/consumer and two identical5116-byte pure projections without mutation. Bounded consistency and source accounting do not accept whole-source fidelity,common meanings or whole-definition proof.

## 13. Review,DAG and continuation

All prepared and native definition producers passed. Exact source,A04/C01/E02 prerequisites,work-unit output/write scope,prior full seal and prepared full signature/population/source-clause controls were checked before native creation. No output was treated as present before its producer ran,and no successful receipt was substituted for the current model/source checks.

An illustrative reference names a stable Principal identifier,kind,issuer and route without copying an identity record. A declared resolved state nominates a governed Principal;an explicit unresolved state leaves that field unused. An authority decision uses separate current grant evidence for its exact scope and time. Those declarations can satisfy T without proving actual resolution,privacy absence or permission. A counterexample embeds a credential class or omits current evidence;necessary guards fail despite nonempty reference labels.

'''
fence=chr(96)*3
s+=fence+'''mermaid
flowchart TD
 S[Exact C65 source and Principal full9364 audit] --> A[Native preflight]
 S --> T[Sorted minimal reference Principal metadata consumer data decision and evidence vocabulary]
 A --> B[Native correspondence and IR]
 T --> B
 B --> I[Required populations and hostile controls]
 I --> C[Independent model and source checks]
 C --> R[Detailed thirteen-aspect review]
 R --> F[Fresh type checks and typed freeze]
 F --> V[Separate typed audit]
 V --> H[Current carrier and consumer inspection]
 H --> P[Qualified source maps and authority profiles]
 P --> D[Reachable dependencies]
 D --> J[Current whole inventory]
 J --> E[Six fresh delivery checks]
 E --> Q[Full delivery review and seal]
 Q --> N[Separate full delivery audit]
 N --> X[Next Constraint Cycle Safety Invariant native definition]
'''+fence+'''

The seventeen-node,seventeen-edge work DAG is acyclic and separate from semantic dependency cycles. Three fresh contract/model/source checks passed. Sixteen typed inputs are frozen and separately audited before current carrier/consumer mapping,qualified profiles,reachable dependencies,whole102draftinventory,sixfreshchecks,full review,seal and separate audit. Constraint Cycle Safety Invariant native creation follows that full Principal Reference audit. Working102/81 and last completed whole inventory101/82 remain separate until full refresh.

Twenty-one dependency meanings are separately qualified;their complete theories and authority are not imported. All9,364priorsealedfiles201sources and original183/189/201scope remain preserved. Owner acceptance,source fidelity,shared denotations,whole translation and whole proofs remain pending. Semantic readinessfalse;goalactive. The complete original episode and final aspect-by-aspect review remain required;this bounded typed packet cannot redefine success around a verified subset.
'''
for i,x in enumerate(analysis['known_losses'],1):s+='- PREF-FINDING-'+str(i).zfill(3)+': '+x+' Status: unresolved;owner review and accepted map references pending.\n\n'
s+='Actual native counts: '+json.dumps(counts,sort_keys=True)+'. Source checks: '+str(len(source['checks']))+'. Projection SHA: '+source['first_render_sha256']+'.\n'
assert len(re.findall(r'^## [0-9]+\.',s,re.M))==13 and len(s.split())>3000,len(s.split())
with (u/'REVIEW.md').open('x') as f:f.write(s)
with (u/'CONTINUATION.md').open('x') as f:f.write('''# Principal Reference typed-stage continuation

Exact current C65 native T/IR/source account/model/source and three fresh checks complete. Sixteen-input freeze and separate actual audit need terminal evidence. Native102/81 differs from last full101/82.261controls46queries7conditionedroot-targets66obligations passed;no failed prepared/native definition producer. Resolved/unresolved,conditional origins,minimum consumer-needed data,identity-authority independence and separate current evidence remain distinct.

Next current carrier/consumer mappings,qualified profiles,reachable dependencies,whole102draftinventory,sixfreshchecks,full13aspectreview,seal and separateaudit. Constraint Cycle Safety Invariant follows full PrincipalReference audit. Preserve9364priorsealedfiles201sources and original183/189/201plus121/511/797/36scope. No actual resolution,credential access,identity mutation/authentication/replacement,grant,rights or canonical/private/live/publication effects. Source fidelity,whole translation/wholeproofpending;semantic readinessfalse;goalactive.
''')
with (u/'DELIVERY-CONTEXT.md').open('x') as f:f.write('''# Principal Reference definitions-types-logic context

F05-T.cal.definition.principal-reference follows Principal full9364-file seal/separateaudit0. Exact C65 source,A04/C01/E02 receipts,SWU output/write scope,source-only29checks24units5116bytes1localupstream,prior seal,prepared full contract261controls and four native producers bound.16sorts7constants33functions150signatures206declarations;24units24mapped16encoded6explanatory2deferred26required150unresolved21directuses46queries.

261controls106Ttrue147Tfalse8malformed;66sourcequeryobligations;sevenrootqueries source-conditioned byresolved/origin/use scope. Prepared maximum41174steps;unchanged limits. Minimum data classes/consumer-needed relations,resolutionstates and separate current evidence are necessary declarations;real resolution,privacy,identity authority and grants independent. No failed prepared/native producer;private routing references metadata-only without content/meaning import.

Sixteen typed inputs are frozen/separately audited before full current carrier/dependency/inventory delivery. Working102/81 versus last full101/82 explicit. Owner maps/source fidelity/wholetranslation/wholeproofpending;semantic readinessfalse;goalactive. No actual reference resolution,Principal copying/mutation/authentication/replacement,credential access,grant,authority or canonical/private/live/publication/deployment effect. Preserve prior bytes and unrelated work.
''')
print(json.dumps({'result':'written-thirteen-aspect-PrincipalReference-review','words':len(s.split()),'aspects':13,'findings':22,'dag_nodes':17,'dag_edges':17,'source_checks':len(source['checks'])},indent=2))

