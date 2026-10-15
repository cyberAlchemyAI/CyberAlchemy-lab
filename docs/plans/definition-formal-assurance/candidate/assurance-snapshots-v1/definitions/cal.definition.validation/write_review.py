"""Explain actual Validation typed results with explicit partial PASS and conformance limits."""
import json,re
from pathlib import Path
u=Path(__file__).resolve().parent
def load(n):return json.loads((u/n).read_bytes())
BODY=r'''# Validation: typed candidate review

## 1. Exact current meaning and admission boundaries

The selected current meaning is cal.definition.validation@1.0.0-candidate.1 at exact digest f21ca27867379eb3389588313208a5db37cf0449b79bb5c7f644c3b9a89a2af8. It comes from candidate0007 CML-07 semantic closure and is admitted through C29. This is the selected positive Definition. C53 legacy reconstruction and C65 integrated-model admission are separate sources and are not substituted for it. Registry,authorization,manifest,candidate and exact generated projection bindings are observed independently.

The retained Definition lifecycle remains candidate-authored,and the retained candidate set has authority_effect none. C29 supplies the admission overlay without rewriting those historical bodies. It selected separately owned source-use and Definition requests. Its recorded result made S2 evaluable without executing S2,admitting identity carriers or accepting implementation bindings. That admission does not accept the present mathematical translation or establish actual runtime Conformance.

Three source references accompany the Definition:the admitted Definition JSON,the admitted Definition evaluation profile,and a retained candidate/null external D56 range. The two local origins are byte-bound. The historical external range and producer identity are not reproduced or authenticated here. Its recorded source-use selector and scoped C29 admission remain evidence of selection,not a claim that a present external producer was verified. This candidate grants no new authority or live effect.

## 2. Genus, voices and specialized Evaluation

The genus is an Evaluation of an exact subject against an exact criteria profile. It produces check outcomes and a receipt. The formal expression binds profile,subject and inputs by digest and separately denies automatic Conformance and Admission. The applicability statement adds an exact evaluation environment. Scientific-formal test conditions retain subject,profile,inputs,validator identity,outcomes and the three named result labels.

The plain-language and domain-context voices supply intuition about checking a record or implementation against an explicit profile. They do not become universal axioms of correctness,coverage,execution or authority. Complete source accounting retains those explanations and examples alongside the encoded and deferred scientific-formal statements. The candidate does not discard historical candidate wording merely because a later admission overlay exists.

Specialized Evaluation is represented through a separately sorted declared EvaluationReference. This records the necessary relationship without silently importing Evaluation's whole prior theory,its causal blockers,collect-all uniqueness policy or current carrier semantics. A meaning-aligned bridge is required to compose those theories over a shared real evaluation. That bridge remains ownerpending. The selected fragment therefore supports a partial formalization rather than a whole semantic embedding claim.

## 3. Sorts and reference distinctions

Validation,EvaluationReference,SubjectReference,CriteriaProfile,InputReference,EvaluationEnvironment,ValidatorIdentity,ReceiptReference,Context,DeclaredCheck,Outcome,OutcomeTag,Digest,CoverageScope,EvaluationMode,ConformanceProfile,ConformanceEvidenceUse and Token are separate proposed sorts. Nonempty domains are explicit in the finite interpretation. These descriptive sorts do not invent current canonical Definition identities for checks,outcome tags,digests,profiles or validators.

A Validation selects its Evaluation reference,subject,criteria profile,inputs,environment,validator,receipt and context. An Outcome selects its Validation,declared check and outcome tag. A CriteriaProfile has its own digest,coverage scope and evaluation mode. A ConformanceEvidenceUse selects a Validation,a separately declared ConformanceProfile and an exact coverage scope. These projections keep evaluation records,criteria,results,receipts and evidence-use qualifications distinct.

Equality is interpreted within a sort. Shared subjects do not identify evaluations with different inputs. Shared receipt references do not identify their evaluation records or grant authority. Total functions give outside domain members projections as well;applicability guards decide which members carry necessary source-inspired requirements. Nonempty handles establish declared reference presence without proving resolution,authenticity,global uniqueness or actual identity equivalence.

## 4. Signature and exact digest bindings

The signature explicitly declares each sort,constant,total function,predicate and relation. The EMPTY token supports selected-reference guards. PASS,FAIL and NOT_EVALUABLE are distinct local OutcomeTag constants. The broader tag domain can contain outside values;only selected included outcomes must use the named triad. Handle functions retain separately typed references rather than treating all fields as unstructured text.

Selected Validations require declared and nonempty references for all eight record projections. Their own profile,subject and input digests agree with the digests of the corresponding references. Those Digest values have declarations and nonempty handles. A different declared digest falsifies the exact binding guard. The theory does not prescribe one hash algorithm,authenticate a digest string,require implicit latest-version selection or prove present source currentness.

Each selected profile declares coverage and evaluation mode and retains a declared nonempty CoverageScope and EvaluationMode. These declarations are necessary structure,not a proof of a real mode's execution semantics or complete discovery of relevant criteria. Validator identity and evaluation environment remain explicitly recorded inputs. A validator label does not prove that code ran,and exact recorded inputs do not establish actual correctness of its checks.

## 5. Declared checks,outcomes and receipt records

Every check declared by a selected profile has at least one included outcome in its selected Validation. Included outcomes retain their own Validation and check binding,one of the three local tags,a declared nonempty check,and a nonempty outcome handle. The selected receipt records each included outcome. These guards retain the complete declared outcome record without asserting real receipt production,storage or authenticity.

Multiple outcomes for one check remain permitted. The source requires outcomes for all declared checks but does not by itself select one unique outcome per check or an aggregation policy for repeated attempts. A positive control adds another PASS outcome for a check and preserves T/I. A separate owner decision is needed for retry histories,conflicting attempts and one-final-result conventions. Evaluation's previously proposed uniqueness map is not silently inherited.

Declared evaluability is linked to the selected outcome tag:NOT_EVALUABLE corresponds to a check declared not evaluable for that Validation;PASS and FAIL correspond to a check declared evaluable. This is a proposed local denotation map. It does not prove the real check could run or that a blocker explains its failure to run. The selected Validation source does not add Evaluation's causal-blocker requirement automatically. Real evaluation and receipt correspondence remain separate obligations.

## 6. Reported PASS and limited coverage

A reported PASS requires every included outcome for every evaluable check declared by its exact profile to be PASS. A FAIL for an evaluable declared check falsifies that guard. The source also says a PASS cannot cover omitted or NOT_EVALUABLE checks. The theory therefore keeps reported PASS,per-check PASS coverage and complete PASS coverage separate. It does not promote the absence of an evaluable FAIL into whole-scope completeness.

The derived per-check coverage relation includes only declared,evaluable checks with a recorded PASS under a reported PASS. A NOT_EVALUABLE check cannot be added to that coverage relation. An undeclared check cannot be covered by that profile's PASS either. Every declared check still needs a recorded outcome,including explicit NOT_EVALUABLE results. Omitting an outcome fails the record guard rather than being hidden behind a positive overall label.

The finite fragment permits an owner-pending partial reported PASS with an uncovered NOT_EVALUABLE check. Such a record cannot declare complete PASS coverage. Whether a real evaluation mode allows that reported partial status needs accepted status and mode maps. The candidate does not claim the partial policy has been admitted. A complete PASS coverage declaration requires every declared check covered,but still does not prove that all relevant semantic,implementation or runtime checks were discovered.

## 7. Scope-qualified conformance evidence

A selected ConformanceEvidenceUse requires a selected Validation with reported PASS,an explicit context/scope-use declaration,a separately declared ConformanceProfile and a nonempty exact CoverageScope. That ConformanceProfile must be declared applicable to the bound subject and scope and must declare the exact criteria profile sufficient for that scope. Each check required by the ConformanceProfile must be covered by the Validation PASS.

This permits a proposed partial-profile record to support only a narrower explicitly qualified evidence-use map whose required checks are covered. The unrelated NOT_EVALUABLE check is not thereby covered,and the entire Validation profile is not silently equated with the Conformance scope. Subject,profile,required-check and scope mappings need owner acceptance. A changed use scope or a required uncovered check fails the necessary guard.

Those conditions are necessary declarations for a selected evidence use. They do not prove actual evidence adequacy,Conformance,Admission,Acceptance or authority. A separate governing owner may establish actual Conformance with accepted complete scope and sufficient evidence. The theory allows independently supported outcomes while denying that a reported PASS or a qualified-looking map is sufficient by itself. Receipt and consumer contracts remain independent from this logical use record.

## 8. Populations and nonvacuous witnesses

Required populations include a reported PASS without actual outcomes,outside Validation scope,complete declared PASS coverage,partial PASS with uncovered NOT_EVALUABLE,a FAIL without reported PASS,an empty declared profile without actual outcomes,shared subject with different inputs,qualified evidence use without actual outcomes,a partial-profile scoped evidence use,outside use scope,and witnesses for PASS,FAIL and NOT_EVALUABLE. Their exact native denominator is recorded below.

These requirements stop the supplied model from passing only because every selected scope is empty. They also expose limits directly. A partial-status witness does not force every evaluation to be partial. A multiple-outcome control does not force repeated results everywhere. An explicit empty-profile witness records a mathematical policy gap;its vacuous reported PASS does not establish adequacy,complete real coverage or authority. The real minimum-criteria policy remains ownerpending.

Unresolved populations preserve the full predicate and relation denominator,including actual outcomes. They do not substitute assumed outcomes for open denotations. Outside records may have empty or unresolved references and outside outcome tags because the selected scope guards do not apply to them. One finite T/I witness is evidence about this qualified partial theory,not a common-carrier model or a semantic consistency proof across all current definitions.

## 9. Positive,negative and malformed controls

The model checker reconstructs the exact interpretation,compiled IR and complete correspondence account before evaluating the supplied controls. It qualifies every symbol and validates domains,sorts,total functions,tuple arities and duplicate tuples. Missing symbols,partial functions,ill-sorted constants,malformed outcome inclusion,duplicate predicates,empty domains and duplicated function entries are rejected as malformed models. The repeated required-check tuple is another explicit malformed duplicate control.

Guard-failing controls remove record components,digests,coverage/mode declarations,check outcomes,receipt membership or exact scope qualification. They collapse local tags,bind an outcome to the wrong Validation,mislabel evaluability,report PASS over FAIL,cover a NOT_EVALUABLE or undeclared check,claim complete coverage for a partial record,and omit applicability or sufficiency declarations. These are well-formed counterexamples to particular required clauses rather than malformed input failures.

Positive controls preserve outside records,partial and empty declared profiles,repeated PASS outcomes and shared receipt references. Other controls add independently justified actual outcomes while leaving declared structure valid. The checker verifies expected T and required-population results against actual evaluation. Counts come from the native terminal report. A prepared script,intended run or convenient diagram is not substituted for successful model evidence.

## 10. Countermodels and authority independence

Each actual-outcome query asks whether selected Validation or evidence-use structure forces an actual result. The supplied T/I model keeps a relevant selected witness while making the query target false. Its explicit witness condition is separately checked. This is a countermodel to that particular entailment within the candidate signature. It is not a mechanized whole Definition proof or a categorical prohibition on legitimate outcomes.

Validation targets include actual execution,check correctness,outcome authenticity,receipt production and storage,reference resolution,currentness,semantic truth beyond checks,coverage completeness,conformance-evidence adequacy,Conformance,Admission,Acceptance,Implementation,Publication,Deployment,authority,Runtime Evidence,external effects,owner fidelity,consumer alignment and global consistency. Evidence-use targets separately include adequacy,Conformance,Admission,Acceptance,authority,Runtime Evidence,owner fidelity and consumer alignment.

Admission,Acceptance,Publication and Runtime Evidence role exclusions preserve the source's meaning separation. Actual supported outcomes may coexist when distinct contracts,evidence and governing owners justify them. No profile PASS,receipt string,current type admission or parent authority supplies instance authority by implication. Exact source-linked obligations retain the relevant negative boundaries and declaration-versus-outcome limits. No target is assumed inside T merely to make a test pass.

## 11. Source accounting and observation ceiling

All nonempty selected strings in voices,boundaries,scope and claim ceiling are inventoried. Correspondence retains exact selectors,character offsets,excerpt digests,dispositions and links. The normative statement and formal expression are split where needed to preserve the boundary between declared checking structure and unsupported actual implications. Encoded,explanatory and deferred spans cover the complete selected source characters.

The source checker observes exact current C29 selection,registry admission,authorization and manifest bytes,candidate0007's eight-definition admission and retained candidate lifecycle. It binds the source-admission table as a C29 manifest input and preserves the distinction between the source-use and Definition requests. The recorded D56 selector and target scope remain explicit. The two admitted local source origins match their exact bytes. The external historical range and whole file are not claimed reproduced or current.

Definition/v1 schema and generator bindings are checked independently. Two pure renders preserve the selected input and reproduce its projection exactly. The three scientific-formal tests contain semantic guards and non-inference requirements;they are not substituted with C53's migration-only tests. Source-query obligations bind exact excerpts to targets outside T and record whether their necessary declaration was encoded or deferred. Complete accounting and source-byte observation do not establish owner fidelity.

## 12. Dependencies,current carrier work and DAG

The exact canonical dependencies cover Definition,Artifact,Artifact Type,Contract,Evaluation,evidence,review,methods,results,sources,provenance,Validation Receipt,Conformance,authority,decisions,policy,roles,contexts,identities,invariants,event histories and typed relations. Descriptive profile/check/outcome/digest sorts do not create missing canonical identities. Comparison sources remain qualified and their whole theories are not imported into T.

Traceability is the previously sealed79th partial draft;Validation creates a working80th. A later current whole-inventory refresh must verify incremental accounting. The full scope remains183currentidentities189admittedversions201sources. Missing counterpart packets,semantic cycles,common-meaning consistency and accepted source-to-carrier/consumer maps remain open. A count of isolated per-definition witnesses cannot prove one shared real-world interpretation.

The typed stage precedes actual current carrier/profile observations,reachable dependency compilation and the whole inventory. Those are full-delivery obligations. Six fresh full checks then support the separate complete delivery review,seal and audit. The native Validation Receipt unit follows that audit. The acyclic execution DAG is distinct from the semantic dependency graph,whose cycles require independent review.

```mermaid
flowchart TD
 S[Exact C29 source and prior Traceability audit] --> A[Specialized Evaluation and exact record bindings]
 A --> T[Sorted theory evaluability PASS and scope guards]
 A --> P[Explicit complete partial empty and outside populations]
 T --> I[Interpretation and complete correspondence]
 P --> I
 I --> C[Finite controls and countermodels]
 S --> B[Exact current source and pure projections]
 C --> H[Fresh typed checks]
 B --> H
 H --> R[Typed receipt and separate audit]
 R --> E[Current carrier and consumer obligations]
 E --> Q[Reachable dependency graph]
 Q --> D[Whole current inventory]
 E --> F[Six fresh delivery checks]
 D --> F
 F --> J[Complete aspect review and seal]
 J --> V[Separate full audit]
 B --> R
```

## 13. Owner decisions and continuation

Owner review must accept or revise specialized Evaluation bridges,exact reference/digest denotations,profile coverage and mode semantics,outcome evaluability and repeated-attempt aggregation,partial reported PASS,empty-profile policy,complete declared coverage,receipt records and applicable scope/sufficiency maps. It must establish any carrier and consumer correspondence and distinguish necessary evidence-use declarations from actual Conformance and authority. Hypothetical owner labels do not provide that Decision.

The typed stage is a reproducible partial candidate. Source fidelity remains pending;semantic readiness and mechanized whole proof are false. Actual check execution,coverage discovery and external historical producer currentness remain separately bounded. The separate typed audit freezes the actual successful evidence without claiming full delivery or whole episode completion. Prior Source and Traceability seals and all earlier definition packets are preserved.

Continue with fresh typed replay,frozen receipt and separate audit before carrier/profile,dependency and whole-inventory work. Six actual fresh delivery checks precede the complete delivery review,seal and separate audit. Only then create Validation Receipt's native unit. The full episode remains active until its entire authorized scope and required final review are achieved. The eighteen findings below retain the unresolved denotation and policy decisions instead of hiding them behind passing structure.
'''
def main():
 c=load('context.json');counts=load('denominator.json');m=load('model-controls.json');s=load('source-checks.json');packet=load('correspondence.json');assert c['source_selection']['definition_id']=='cal.definition.validation' and m['control_count']==len(m['results']) and all(x['result'] for x in s['checks'])
 for stem in ['author','build','model','source']:
  x=load(stem+'-command-result.json');assert x['exit_code']==0 and not (u/x['stderr']).read_bytes()
 text=BODY+'\nActual native typed evidence: '+json.dumps({'source':c['source_selection'],'counts':counts,'controls':m['control_count'],'T_true':sum(x.get('primary_theory_satisfied') is True for x in m['results']),'T_false':sum(x.get('primary_theory_satisfied') is False for x in m['results']),'malformed':sum(x['status']=='rejected-model-structure' for x in m['results']),'source_checks':len(s['checks']),'source_query_obligations':len(load('source-query-obligation.json')['obligations']),'projection_bytes':s['projection_bytes'],'projection_sha256':s['first_render_sha256']},sort_keys=True)+'.\n\n'
 for row in packet['source_precedence']['conflicts']:text+='- '+row['finding_id']+': '+row['description']+'\n'
 assert len(re.findall(r'^## [0-9]+\.',text,re.M))==13 and len(text.split())>2500
 with (u/'REVIEW.md').open('x') as f:f.write(text)
 with (u/'CONTINUATION.md').open('x') as f:f.write('Validation typed candidate stage only. Complete fresh typed replay,freeze and separate audit before carrier/profile,dependency and whole-inventory checks,six fresh full checks,complete delivery review,seal and separate audit before native Validation Receipt. Preserve183identities189versions201sources and every prior seal. Owner fidelity,common-meaning consistency and whole proof remain pending.\n')
 with (u/'DELIVERY-CONTEXT.md').open('x') as f:f.write('Exact current C29 Validation selected from candidate0007. Retained source/lifecycle bodies are preserved;two local admitted origins are bound,historical external D56 bytes/currentness are not reproduced or authenticated. Partial PASS/NE coverage and scope-qualified conformance-evidence use are ownerpending proposed maps. No canonical/private/live writer,publication,instance admission or owner translation acceptance follows.\n')
 print(json.dumps({'review_words':len(text.split()),'aspects':13,'owner_findings':len(packet['source_precedence']['conflicts'])}))
if __name__=='__main__':main()
