"""Explain Principal's thirteen formalization aspects and exact staged delivery DAG."""
from pathlib import Path
import json,re
p=Path(__file__).resolve().parent;u=Path('docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.principal');load=lambda n:json.loads((u/n).read_bytes());context=load('context.json');counts=load('denominator.json');analysis=load('clause-analysis.json');model=load('model-controls.json');source=load('source-checks.json');fresh=load('fresh-types-logic-results.json');assert all(x['exit_code']==0 and not (u/x['stderr']).read_bytes() for x in fresh)
s='''# Principal: definitions,types and logic review

Principal is formalized as a governed identity recognized within an exact authentication,authorization,ownership or accountability boundary. Reference use nominates one exact governed Principal identity and issuer boundary. Represented subjects preserve independent identity and lifecycle. Consequential authorization requires an exact current grant applicable to its Principal and scope. Recognition,reference,representation and authorization remain separate structures before carrier implementation or real identity/permission evaluation.

Native creation followed Identity Lineage's full9,251-file seal and separate actual audit0. Every prior sealed file and201sourcefiles remain hash verified. Working native drafts now number101among183currentidentities,leaving82withoutT. Last completed whole inventory remains100partialdrafts83missing until Principal full delivery. Original183identities189versions201sources and121tasks511planningedges797SWUs36frontiers stay exact. Source-owner accepted whole translations and whole-definition proofs remain zero;source fidelity and shared meaning maps remain pending. The full episode and final review stay active.

## 1. Exact source and C65 admission

The selected source is cal.definition.principal@1.0.0-candidate.1,SHA60180d24ef3e83c517ea8f51f5ab863801c248ac80d19864353b58f70aaad794. Its current admission is CAL-DECISION-0065-INTEGRATED-LAB-DEFINITION-MODEL-ADMISSION. Exact selection fixes the positive meaning under review. It does not replace the Definition with a nearby Principal carrier,authentication protocol,Actor example or runtime configuration.

The source checker binds C65 decision,authorization,exact candidate,selected Definition digest and validation receipt. Current183identity189versionsnapshot verification is separate from historical admission counts. C65 admitted exact Definition bytes while leaving carrier,instance,relation,consumer and runtime effects separate. Its admission does not create a Principal,resolve an issuer,execute authorization,issue a grant or accept this formal translation.

The retained body remains review-only under the positive admission overlay. The embedded actor-model-review remains candidate-unadmitted with exact local bytes. The integrated-model consumer is observed rather than activated. Routing evidence grants no effect authority. Private read-first material is bound only by path/hash metadata;its content and meaning are not imported into primary theory or copied into these public source artifacts. Canonical source meaning remains the exact selected Definition.

## 2. Sorted signature and qualified symbols

Fifteen nonempty sorts are proposed:PrincipalReference,PrincipalIdentityReference,BoundaryReference,IssuerReference,ScopeReference,PrincipalUseReference,RepresentationReference,SubjectReference,SubjectIdentityReference,LifecycleReference,SubjectKindReference,AuthorizationReference,GrantReference,TimeReference and Token. EMPTY is one Token constant. Twenty field selectors and fourteen reference-handle functions give34totalfunctions. There are157predicate/relation signatures and207declarations.

The vocabulary separates Principal meaning from Principal identity,issuer and recognition boundary. Reference use,represented subject and authorization have independent carriers. Principal and represented-subject identity coordinates use separate sorts. Grant and time are also distinct. Descriptive sort names do not create new canonical Definitions or claim that a real identity or grant exists.

Each selected field requires a declared target,nonempty handle and exact BindingDeclared relation matching the selector. Totality provides well-sorted finite values without authenticating their referents. Symbols are qualified by exact source version and candidate scope. Same-looking type names in another packet do not establish shared denotation or import a whole theory. Missing,conflicting,undeclared and empty selected nominations fail independently. Outside and unused optional values remain possible under their own scope ceilings.

## 3. Governed recognized identity genus

PrincipalApplicable is equivalent to PrincipalInScopeDeclared. A selected Principal nominates exact identity,boundary,scope and issuer references. It is declared governed,recognized and bounded. Its nominated identity is declared governed. Identity-backed or record-backed criterion is inclusive:one alternative or both can hold. The source-owner correspondence between the abbreviated formal expression and the positive identity genus remains an explicit finding.

Recognition is represented as necessary declaration structure rather than a successful authentication or authorization operation. A supplied recognized flag does not prove that an issuer accepted a real subject or that a boundary is authentic. Actual RecognizedIdentity,BoundaryRecognition,IssuerAuthenticity and IdentityResolution remain independent targets with supplied countermodel evidence.

An abstract selected Principal may have no modeled reference use,representation or authorization. The required populations demonstrate that case. The finite model does not enumerate every real Principal or impose a universal one-Principal-per-person rule. Principal identity does not become Person identity,Actor classification,Agent capability,Team membership or a Role. Legitimate independently grounded facts remain possible while classification-derived authority and rights are excluded.

## 4. Recognition alternatives and issuer boundary

A selected Principal's nominated boundary is recorded and has exact issuer and scope fields. At least one authentication,authorization,ownership or accountability recognition alternative holds. The alternatives are inclusive. A boundary may serve authorization and ownership together,and another recognition alternative may be added without violating theory. No unsupported disjoint four-kind taxonomy is imposed.

The Principal issuer equals its nominated boundary's issuer by declaration. This keeps the source's issuer-boundary relationship exact instead of allowing a reference to silently select a different recognition context. A mismatched issuer fails. Actual issuer authenticity and boundary resolution remain independent;nonempty tokens and recorded flags do not supply signed issuer evidence or a live resolver.

Principal scope and boundary scope remain separate exact nominations. The source does not require universal equality between identity governance scope and every recognition boundary scope. A positive control changes boundary scope independently. Accepted scope correspondence must still explain the intended governance boundary. Recognition by an authorization boundary also does not issue a grant or establish permission merely from the boundary kind.

## 5. Exact Principal reference use

A selected PrincipalUseReference nominates one Principal,one Principal identity and one issuer boundary. UseApplicable is equivalent to UseInScopeDeclared. Recorded posture and exact-resolution declaration are required. The nominated identity equals the selected Principal's identity,and the use's issuer boundary equals the Principal's nominated boundary. A mismatch in either coordinate fails.

These exact nominations represent the source's test that every Principal reference resolves to one governed identity and issuer boundary. They do not execute a lookup,authenticate a reference or impose global uniqueness of all Principals and boundaries. Multiple reference uses may legitimately nominate one governed identity,while different contexts can preserve independent recognized identities. Accepted maps must establish what resolution and identity equality mean.

UseActualIdentityResolution,IssuerResolution,BoundaryAuthenticity,IdentityFidelity and OneIdentityResolution remain independently queried on selected use scope. An absent optional use cannot serve as their counterexample. Reference completeness does not create Role,capability,ownership,permission or authority. Each invalid-inference declaration is separately excluded. The candidate therefore retains the precise reference-versus-referent distinction without reducing a Principal reference to a free text label or claiming operational authentication.

## 6. Independently represented subjects

RepresentationReference links a selected Principal to exact before and after subject references. Selected representations are recorded and require governed subject records. Each subject separately nominates identity,lifecycle and kind. Principal identity and represented-subject identity are distinct typed coordinates;the representation does not merge them or equate a recognized Principal with the represented Person,Team,service or Agent.

Before and after subject identity and lifecycle coordinates must agree. Changing either coordinate fails even when the Principal and boundary labels remain exact. Subject references may differ when those coordinates are preserved. A positive control also uses the same subject reference before and after. These equalities preserve necessary structure while actual subject independence,identity continuity and lifecycle fidelity remain unresolved.

The model does not invent an owner or authority-transfer rule from a representation. Nor does it globally equate represented subjects that share a Principal or a kind. Actual SubjectIdentityPreservation,LifecyclePreservation,SubjectIndependence and SubjectResolution are separate outcomes. Their countermodels contain selected representations with coherent declarations while leaving real preservation unsupported. Source owners must accept how before/after records and subject identity/lifecycle map to actual governed subjects.

## 7. Subject-kind independence and legitimate overlap

Person,Team,service and Agent kind predicates are separately available. The representation's subject-kind field is exact and nonempty,but the source does not require every possible governed subject to lie in a closed four-kind universe. A different declared kind can retain the same identity and lifecycle. Named kinds preserve their own semantic responsibilities rather than forming an implicit authority hierarchy.

Subject kind may change while identity and lifecycle coordinates agree. A positive control changes an after-subject kind from Person to Agent;another uses a different declared kind. Those model observations do not claim real identity equivalence between a person and a machine. They expose the absence of an unsupported kind-preservation axiom and retain the need for accepted classification maps.

Principal identity does not prove Person identity,Agent capability,Role assignment or unrestricted authority. The source's illustrative human Principal authorizing a Definition admission while a machine Agent performs a file update remains explanatory. It does not admit a Person or Agent instance,issue permission,transfer identity or execute an action. Legitimate independent subtype/classification overlap remains possible without being inferred from recognition or reference labels.

## 8. Authorization and evaluation-time scope

A selected authorization nominates exact Principal,scope and evaluation-time references and is declared recorded. AuthorizationApplicable is equivalent to AuthorizationInScopeDeclared. Consequential status is a separate declaration. The model distinguishes consequential and nonconsequential selected authorizations rather than treating every reference or recognition event as an executed consequence.

Evaluation time is an explicit proposed reference used to express current grant applicability. No timestamp parser,clock ordering,expiry arithmetic or real current instant is invented. A TimeReference can be structurally coherent while real time/currentness remains unsupported. Source-owner interpretation must account for validity intervals,revocation,issuer evidence and the precise scope of the consequential activity.

Authorization scope remains distinct from Principal identity scope and recognition-boundary scope. The source requires exact grant and scope rather than a universal equality between all these nominations. The candidate does not turn a broad recognized identity into permission for every action. A consequential authorization with the wrong scope or evaluation time fails when the nominated grant does not apply. Actual authorization,scope fidelity,permission,authority and external effects remain separate outcomes.

## 9. Exact current grant for consequential authorization

Consequential authorization activates the exact grant guard. The authorizationGrant field must nominate an exact declared nonempty grant. AuthorizationExactCurrentGrantDeclared,GrantRecordedDeclared and an exact grant issuer field must hold. GrantCurrentAtDeclared must relate that grant to the authorization's evaluation time. Applicability relations must also connect it to the authorization's selected Principal and exact scope.

Removing currentness,Principal applicability or scope applicability fails. A grant reference or current label cannot substitute for any missing relation. Ten actual authorization queries are conditioned on selected consequential scope. Their countermodels therefore include consequential authorizations and complete necessary grant declarations while leaving actual grant resolution,currentness,issuer authenticity,applicability,permission and authority unsupported.

Unused nonconsequential grant selectors remain total without fabricating a real grant. A positive control removes an unused grant binding;another leaves the outside grant handle empty. Selected consequential guards remain strict. A recorded current-grant declaration is not an authentic issuer decision or proof of executed authorization. It preserves the source's necessary exactness while leaving actual authority and consumer enforcement to accepted maps and evidence.

## 10. Grant cardinality and issuer independence

Grant applicability to Principal and scope are relations. Currentness is a grant/time relation. A grant can apply to more than one Principal,scope or evaluation time without an unsupported global cardinality restriction. Positive controls add each kind of applicability while preserving theory and required populations. The record's exact nomination does not mean a real grant is universally single-Principal,single-scope or valid at one instant only.

Grant issuer is separately typed from the Principal recognition issuer. No equality between them is required. The baseline demonstrates a different issuer;another positive control permits the same issuer. Delegation and independent issuer authority require accepted scope maps. Forcing identity-recognition issuer and every grant issuer to be identical would add a rule absent from the source and prevent legitimate separately governed grants.

Exact reference and applicability declarations do not prove an actual grant's content,currentness or authority. The model does not authorize anything or claim that a grant crosses every recognition boundary. Nor does added declared applicability supply an unbounded permission. The source's only-through-exact-grants boundary remains visible in consequential authorization structure,while real grant authority and all permission outcomes stay independent.

## 11. Noninference,rights and effect boundaries

Root boundaries exclude proving Person identity,Agent capability or Role assignment from Principal identity. They also exclude identity-derived ownership,permission,authority and unrestricted authority. Principal is not silently equated with Person,Actor,Agent,Team or Role. Parent meaning and Definition admission do not grant instance authority or accept this translation.

Use boundaries exclude identity or issuer authentication from reference presence and rights from a use label. Representation boundaries exclude subject identity merging,lifecycle changes,authority transfer and inferred Person/Agent identity. Authorization boundaries exclude identity-derived authorization,grant-label authenticity/currentness,scope-label applicability,authority beyond selected scope and actual effects from declarations.

These are scoped invalid-inference declarations rather than universal prohibitions on independently supported real outcomes. Positive controls supply each actual outcome independently while preserving T. Outside objects can carry excluded flags without violating selected scope. No actual Principal is recognized,no issuer is authenticated,no authorization is executed,and no grant,Role,permission or ownership is created by this candidate. Scope and effect authority remain separate from the formal model's structural consistency.

## 12. Source account,controls and queries

All24nonempty source units are accounted at exact selectors and complete character spans. Sixteen clauses are encoded,six explanatory and two deferred. Thirteen primitive formulas cover genus,use,representation,preservation,authorization,conditional grant and four boundary scopes. Scientific notation,plain-language intuition and the human Principal/machine Agent example remain explanatory. Authority-scope and retained candidate claim ceiling remain deferred correspondence.

The native suite passes270controls:115T-true,147T-false and eight malformed-input rejections. Twenty-six required populations demonstrate selected/outside scopes,inclusive identity-or-record,recognition alternatives and overlap,exact reference use,represented subject preservation,consequential/nonconsequential authorization,issuer independence and independent authority. T and I are evaluated separately. Empty selected scopes or missing demonstration populations can preserve necessary theory while failing the required coverage.

Forty-eight queries have supplied T-and-I countermodels. Principal,use,representation and consequential authorization have separate relevant scopes. Ten authorization targets require consequential selection. Sixty-three source-query obligations bind exact selectors,spans,clause hashes and query IDs without placing actual targets in T. Prepared checks reached17,964steps under unchanged limits. Native source checking verifies C65,local review/consumer and two identical4698-byte pure projections without mutation. These checks support bounded evidence and cannot accept source fidelity,common meaning alignment or whole-definition proof.

## 13. Review,DAG and continuation

No prepared/native definition producer failure occurred. The initial compressed routing request had no lexical match;the corrected spaced governance request passed route,context and effect gates. The initial request and non-authorizing receipts remain retained. User authorization covers the reversible candidate work;no owner decision,grant or governance enforcement runtime is inferred from routing evidence.

An illustrative Principal reference resolves by declaration to a governed identity and exact issuer boundary. Its represented subject retains independent identity and lifecycle. A consequential authorization nominates a current applicable grant and exact scope,possibly from a different issuer. Those declarations can satisfy T while actual authentication,Person identity,capability,Role,permission and authority remain unsupported. A counterexample removes currentness or changes scope;necessary grant guards fail despite intact identity labels.

'''
fence=chr(96)*3
s+=fence+'''mermaid
flowchart TD
 S[Exact C65 source and Identity Lineage full9251 audit] --> A[Native preflight]
 S --> T[Sorted Principal identity issuer recognition subject authorization and grant vocabulary]
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
 N --> X[Next Principal Reference native definition]
'''+fence+'''

The seventeen-node,seventeen-edge work DAG is acyclic and separate from semantic dependency cycles. Three fresh contract/model/source checks passed. Sixteen typed inputs are frozen and separately audited before current carrier/consumer inspection,qualified profiles,reachable dependencies,the whole101draftinventory,sixfreshchecks,full review,seal and separate audit. Principal Reference native creation follows that full Principal audit. Working101/82 differs from last completed whole inventory100/83 until full refresh.

Twenty-four dependency meanings remain separately qualified;their complete theories and authority are not imported. All9,251priorsealedfiles201sources and original183/189/201scope stay preserved. Source fidelity,shared meanings,consumer alignment,whole translation and whole proofs remain pending. The full original episode and its final aspect-by-aspect review remain required. This bounded typed packet cannot redefine completion around a verified subset or turn reference declarations into real authority.
'''
for i,x in enumerate(analysis['known_losses'],1):s+='- PRIN-FINDING-'+str(i).zfill(3)+': '+x+' Status: unresolved;owner review and accepted map references pending.\n\n'
s+='Actual native counts: '+json.dumps(counts,sort_keys=True)+'. Source checks: '+str(len(source['checks']))+'. Projection SHA: '+source['first_render_sha256']+'.\n'
assert len(re.findall(r'^## [0-9]+\.',s,re.M))==13 and len(s.split())>3000,len(s.split())
with (u/'REVIEW.md').open('x') as f:f.write(s)
with (u/'CONTINUATION.md').open('x') as f:f.write('''# Principal typed-stage continuation

Exact C65 native T/IR/source account/model/source and three fresh checks are complete. Sixteen-input freeze and separate actual audit need their own terminal results. Native101/82 differs from last full100/83.270controls48scopedqueries63obligations;ten authorization targets require selected consequential scope. No failed prepared/native definition producer. Initial ARE lexical no-match retained;corrected governance route/context/effect gates grant no authority.

Next current carrier/consumer mappings,qualified profiles,reachable dependencies,whole101draftinventory,sixfreshchecks,full13aspectreview,seal and separateaudit. Principal Reference native work follows full Principal audit. Preserve9251priorsealedfiles201sources and original183/189/201plus121/511/797/36scope. No actual recognition,authorization,grant,authority transfer,canonical/private/live/publication effects. Owner maps,source fidelity,whole translation and whole proofs pending;semantic readinessfalse;goalactive.
''')
with (u/'DELIVERY-CONTEXT.md').open('x') as f:f.write('''# Principal definitions-types-logic context

F05-T.cal.definition.principal follows IdentityLineage full9251-file seal/separate audit0. Exact C65 source,A04/C01/E02 receipts,SWU output/write scope,source-only29checks24units4698bytes1localupstream,prior seal,prepared full contract270controls and four native producers bound.15sorts1constant34functions157signatures207declarations;24units24mapped16encoded6explanatory2deferred26required157unresolved24directuses48queries.

270controls115Ttrue147Tfalse8malformed;63sourcequeryobligations. Root/use/representation/consequential-authorization query scopes separate;ten targets condition on consequential authorization. Prepared maximum17964steps;unchanged limits. Private routing read-first references are hash-bound metadata only;no private content/meaning imported. Initial ARE no-match preserved;corrected route/context/effect gates non-authorizing. No prepared/native producer failures.

Sixteen typed inputs are frozen and separately audited before full delivery. Current working101/82 versus last full100/83 explicit. Owner maps,source fidelity,whole translation and whole proof pending;semantic readinessfalse;goalactive. No actual recognition,identity creation,authorization,grant,rights or canonical/private/live/publication/deployment effect. Preserve every prior file/source byte and unrelated work.
''')
print(json.dumps({'result':'written-thirteen-aspect-Principal-review','words':len(s.split()),'aspects':13,'findings':22,'dag_nodes':17,'dag_edges':17,'source_checks':len(source['checks'])},indent=2))

