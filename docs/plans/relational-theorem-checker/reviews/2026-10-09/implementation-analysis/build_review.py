#!/usr/bin/env python3
"""Author review-only artifacts; preserve implementation and accepted evidence."""
from pathlib import Path
import hashlib,json,re,copy
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'craft/formalization').is_dir())
BASE=ROOT/'craft/formalization/candidates/relational-theorem-checker/v1'
PARENT=HERE.parent

def load(p):return json.loads(p.read_text())
def dump(n,x):(HERE/n).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def binding(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def link(p,line=None):return '['+p.name+']('+str(p)+((':'+str(line)) if line else '')+')'

# Selected production definitions; generated snapshots, embedded witnesses and unnamed instances excluded.
MODULES={
'formal/core/RelationalInput.lean':('F0 input model','I08,I09','Keep the bounded three-kind input model. Source interpretation and cross-snapshot identity belong to separately bound successor contracts.'),
'formal/core/RelationalSemantics.lean':('F0 semantic predicates','I07,I08,I09','Retain exact endpoint/version/evidence equalities and local identity uniqueness. A valid candidate edge need not be a member; a graph observation requires membership.'),
'formal/semantic-logic/v1/SemanticLogic.lean':('Semantic logic','I07,I08','Retain assertion-validity and admission-independence meanings. A member-source observation is a separate definition; supplied receipt presence does not prove atomic execution.'),
'registry/RegistryChecker.lean':('Structural registry','I08,I11','Retain closed structural checks. Nonempty qualifier strings and declared relation text do not supply typed interpretations, assessment truth or runtime effects.'),
'formal/reference-checker/l0/ReferenceChecker.lean':('F0 reference checks','I07,I08','Keep independently stated F0 targets. Instance success concerns candidate validity; graph/addition success concerns the full selected invariant and creates no effect.'),
'inference/derivations/InferenceCore.lean':('Typed positive inference','I01,I03,I10','Retain generic finite Horn meaning. Add a separately checked producer profile for sealed observations and bind transport normalization to the stronger executable profile.'),
'inference/derivations/DerivationSoundness.lean':('Certificate semantics','I01,I07,I12','Retain exact ordered replay from initial leaves. Positive query derivation does not prove complete closure or external truth of supplied ordinary facts.'),
'inference/closure/ClosureAdequacy.lean':('Finite complete closure','I06,I12','Retain independent validity, enumeration completeness, saturation and no-extra-fact evidence. Partial execution cannot issue nonderivability or complete readiness.'),
'inference/protected/ProtectedLineage.lean':('Independent root lineage','I01,I08','Retain exact four-coordinate independent-root lineage. Sealed source observations need an orthogonal producer policy; ordinary information cannot supply new roots.'),
'inference/independence/ModelSemantics.lean':('Countermodels','I12','Retain actual checked witnesses. A finite model may contain extra truths beyond least closure; non-entailment refutes one implication and is not universal falsity.'),
'inference/integration/RuleConservativity.lean':('Rule extension meaning','I02,I10,I12','Retain fixed-domain one-step old-body/fresh-head expansion as a special case. Recursion needs a new finite closure construction and every-old-model expansion proof.'),
'evolution/preservation/Preservation.lean':('Registry preservation','I08,I12','Retain universal old-language equivalence under exact fresh-extension hypotheses. Sample compatibility and richer semantic-profile validity are separate claims.'),
'evolution/models/ConservativeExpansion.lean':('Registry models','I08,I12','Retain structural expansion and old reduct. Empty interpretation of new kinds can suffice for expansion; inhabited use requires separate witnesses.'),
'relation-stress/v1/implementation/StressTypes.lean':('Stress profile types','I04,I05,I08','Retain the separately typed profile. Legacy qualifier strings need explicit source interpretations; known condition labels do not establish active or fulfilled obligations.'),
'relation-stress/v1/implementation/DelegationSemantics.lean':('Direct delegation meaning','I04,I07,I08','Retain direct temporal/action/scope/gate checks and restriction monotonicity. Proposed-edge effectiveness and recorded representation are separate; permitted chains remain unknown.'),
'relation-stress/v1/implementation/ObligationSemantics.lean':('Inherited norms','I04,I05','Retain exact origin and conformance independence. Distinguish potential inherited norms/conflicts, condition-activated obligations, and independently evidenced fulfillment.'),
'relation-stress/v1/implementation/StressCheckers.lean':('Stress executable definitions','I05,I06,I12','Retain the limited checker claims. Preflight expensive products; graph validity, requested-query evidence and completeness are composed obligations, not implied by every certificate.'),
'workflow/proof-verifier/Verifier.lean':('Proof verifier trust boundary','I10','Retain exact trusted-definition and axiom/dependency checks and fresh pinned-kernel replay. Add v2 trusted catalogs explicitly; this remains same-kernel replay, not a second implementation.')}
# Name-specific corrections override the family review where the boundary differs.
SPECIAL={
'formal/core/RelationalInput.lean#InferenceRule':'This is an input placeholder, not executed typed Horn Rule. Mark its distinct purpose explicitly.',
'formal/core/RelationalInput.lean#AdmissionRoot':'F0 carries subject/decision/token, not inference effect/scope/epoch. Require an exact independent mapping or leave unsupported.',
'formal/core/RelationalInput.lean#NodeRef':'Id/version is locally exact but does not itself bind immutable content/kind across snapshots. Qualify that contract in S15.',
'formal/core/RelationalInput.lean#Assessment':'Mode-specific irrelevant fields are unconstrained. Define canonical successor records and contextual conflict keys; accepted truth remains supplied.',
'formal/core/RelationalSemantics.lean#InventoryValid':'Local uniqueness prevents token ambiguity; distinct-token assessments for one evaluation key need a successor conflict/selection policy.',
'formal/core/RelationalSemantics.lean#QualifierValid':'Nonempty arbitrary effect/scope strings are shape checks. Interpreted enums and source meaning require a selected adapter.',
'formal/semantic-logic/v1/SemanticLogic.lean#ConformsAt':'Intentionally evaluates a valid assertion without requiring membership. Define MemberConformance separately; do not rewrite this accepted meaning.',
'inference/derivations/InferenceCore.lean#ValueSort':'There is no kind sort. Encode node-kind names as checked text literals for the first v2 profile; include them in captured domain.',
'inference/derivations/InferenceCore.lean#Key.Valid':'Only nonempty key strings, not cryptographic verification. Bind actual canonical identity and exact-byte hash checks outside the logical core.',
'inference/derivations/InferenceCore.lean#Role':'Projection sealing is orthogonal to authority root roles. Ordinary does not mean authorized to invent domain observations.',
'inference/derivations/InferenceCore.lean#RuleValid':'Generic validity allows ordinary heads. The v2 producer policy must forbid sealed ConformsTo/TargetKind heads, including constant-only rules.',
'inference/derivations/InferenceCore.lean#InitialValid':'Ordinary seeds are assumed truth in v1. The v2 profile must reject caller-supplied sealed observations and check exact projector leaves.',
'inference/derivations/InferenceCore.lean#TheoryValid':'Frontend requires exact mandatory CORE and id/version-unique rules; this generic predicate does not. State stricter transport-profile hypotheses rather than claiming full equivalence.',
'inference/derivations/InferenceCore.lean#Term':'Constant-only and nullary positive rules can be meaningful. Do not add a blanket prohibition; check producer policy instead.',
'inference/derivations/InferenceCore.lean#Closed':'A weaker closure class without the typed/root truth constraints of SemanticModel. Keep the model class explicit in APIs and statements.',
'inference/closure/ClosureAdequacy.lean#choices':'Enumerates d^k lists before sort filtering. Preflight a safe bound without allocation; retain this reference for typed-enumerator equivalence.',
'inference/closure/ClosureAdequacy.lean#saturate':'getD [] is covered by the sufficient-fuel theorem for this exact fuel choice. Do not reuse that default as a general timeout policy.',
'inference/integration/RuleConservativity.lean#FreshHeadExtension':'added_bodies permits only old predicates. Recursive fresh bodies require a new contract; preserve old rules, facts, domain, roots and producer policy.',
'inference/integration/RuleConservativity.lean#SemanticModel':'Old ordinary models may contain extra truths beyond initial projection. Existential view equality belongs to initial inventory, not arbitrary old models.',
'relation-stress/v1/implementation/DelegationSemantics.lean#AllAccepted':'Empty required gates are vacuously accepted. This is coherent unless a source requirement explicitly mandates a gate; avoid blind hardening.',
'relation-stress/v1/implementation/DelegationSemantics.lean#DelegationValid':'Empty actions/scopes can mean no effective authority. Define empty-list intent explicitly rather than requiring nonempty lists generically.',
'relation-stress/v1/implementation/DelegationSemantics.lean#InterpretationKnown':'Vacuously true with no matching delegation. Preserve the checker’s preceding DelegationResolved guard.',
'relation-stress/v1/implementation/DelegationSemantics.lean#Effective':'No Recorded premise is intentional for a proposed-edge evaluation. Observed representation must additionally prove membership and source mapping.',
'relation-stress/v1/implementation/ObligationSemantics.lean#Matches':'Matching condition strings and interpreted=true do not evaluate the condition. ActiveNorm requires a separate exact holds assessment.',
'relation-stress/v1/implementation/ObligationSemantics.lean#Derives':'Propagation and same-fact forward are already equivalent to Origin. This is not general hierarchy propagation or arbitrary Horn recursion.',
'relation-stress/v1/implementation/ObligationSemantics.lean#GraphValid':'Conformance rows have no contextual key uniqueness or opposite-status rule. Choose a versioned assessment selection/conflict policy.',
'relation-stress/v1/implementation/ObligationSemantics.lean#ContractValid':'Opposite require/forbid norms are allowed intentionally. Detect potential conflicts without invalidating the whole contract by default.',
'relation-stress/v1/implementation/ObligationSemantics.lean#ConflictPair':'A potential same-condition conflict. Actual conflict additionally requires both activated norms in the exact evaluation context; permit does not erase conflict.',
'relation-stress/v1/implementation/StressCheckers.lean#workUnits':'Computes candidateFacts and closure before budget comparison. Introduce early upper bounds and measured stage time/work/allocation ceilings.',
'relation-stress/v1/implementation/StressCheckers.lean#checkInheritance':'yes means bounded interpretation/matching checks passed. It does not mean conflict-free, conformant, activated or fulfilled.',
'relation-stress/v1/implementation/StressCheckers.lean#CertificateValid':'Checks Origin of listed steps and replay shape, not GraphValid, a requested query or closure completeness. Empty claim can be valid; composed API must add required obligations.',
'relation-stress/v1/implementation/StressCheckers.lean#closure':'Potential-norm origin enumeration with deduplication, not arbitrary Horn saturation or checked condition activation.',
'workflow/proof-verifier/Verifier.lean#audit':'Approved imports and trusted catalogs are hardcoded. Generate v2 catalogs from independently fixed statement types before allowing new submissions.'}
DECL=re.compile(r'^(?:(?:private|noncomputable|partial|unsafe)\s+)*(def|abbrev|inductive|structure)\s+([A-Za-z0-9_.]+)',re.M)
def extract(p):
 text=p.read_text().split('namespace Witnesses')[0];matches=list(DECL.finditer(text));rows=[]
 for i,m in enumerate(matches):
  end=matches[i+1].start() if i+1<len(matches) else len(text)
  # Exact declaration excerpt stops at next instance/theorem/namespace or print; no fixture semantics folded in.
  body=re.split(r'\n(?:instance|theorem|namespace|end |#print)',text[m.start():end],maxsplit=1)[0].strip()
  rows.append((m.group(1),m.group(2),text[:m.start()].count('\n')+1,body))
 return rows
FINDINGS=[
('I01','Seal semantic observation producers','Prospective design gap','ConformsTo and TargetKind are ordinary fresh predicates in the proposal. Generic RuleValid and normalization permit ordinary heads and ordinary seeds. A valid derivation can therefore establish logical consequence without establishing graph-source meaning. Current captured workflow rejects these new heads; this is not a reproduced v1 false acceptance. Seal observation producers separately from authority root roles.','S16','inference/derivations/InferenceCore.lean','abbrev RuleValid'),
('I02','Move baseline/profile design before integration','Implementation dependency gap','Classifier baseline(), integration capture() and bundle execution_profile() bind the captured empty-rule graph and ReviewSignal vocabulary. S06 asks for nonempty old baselines before S09 introduces successor baseline design. Specify registered baseline/profile/catalog contracts earlier; S09 should qualify application.','S15','inference/integration/integration.py','def capture'),
('I03','Specify target-kind encoding and finite domain','Prospective definition gap','ValueSort has no kind sort. TargetKind(reference,contract) needs a checked text literal in the domain and an independent node-kind projection. New targets/scopes/kind values cannot silently satisfy domain_same during rule-only expansion.','S00,S02,S15','inference/derivations/InferenceCore.lean','inductive ValueSort'),
('I04','Define contextual assessment keys and contradictions','Semantic contract gap','Unique tokens do not define how different assessments for the same condition/context disagree. Stress conformance rows permit accepted=true and accepted=false. Require consistent selected evaluations for an exact key, or report an explicit conflict/invalid diagnostic blocking positive projection. Missing stays unknown; issuer truth remains assumed.','S04,S07','relation-stress/v1/implementation/ObligationSemantics.lean','abbrev GraphValid'),
('I05','Separate potential norms, activation and fulfillment','Meaning gap','Matches compares condition labels and interpreted flags. Origin and closure propagate norms without condition evaluation; ConflictPair compares a same-condition require/forbid pair. These are potential norms/conflicts. ActiveNorm requires an exact holds assessment; fulfillment requires separate action evidence.','S04,S07','relation-stress/v1/implementation/ObligationSemantics.lean','abbrev Matches'),
('I06','Protect resource budgets before broadening runtime','Implementation/resource gap','choices constructs d^k candidates before sort filtering. Stress workUnits computes candidateFacts and closure before checking budget. Finite termination and post-computation logical budgets do not establish time or RSS ceilings. Add early conservative bounds and measured stage ceilings before rich runtime integration.','S17,S11,S12','relation-stress/v1/implementation/StressCheckers.lean','def workUnits'),
('I07','Separate candidate validity from observed membership','Definition-composition gap','InstanceValid, ConformsAt and delegation Effective intentionally evaluate a supplied candidate without Recorded membership. Origin requires membership. Keep candidate meanings and define separate observed predicates requiring exact membership/support at projection leaves. Do not strengthen accepted definitions globally.','S00,S02,S16','formal/semantic-logic/v1/SemanticLogic.lean','abbrev ConformsAt'),
('I08','Give source interpretations and data transitions their own task','Implementation/profile gap','Registry qualifiers are closed nonempty strings. F0 uses three kinds and a single conformance evidence token; registry uses plural evidence references and broader pair sets. Stress adds actions, conditions and assessments absent from legacy qualifiers. Rich baseline capture and source/fact/domain changes need distinct change classes and obligations.','S18,S15,S05,S07','registry/RegistryChecker.lean','abbrev QualifierValid'),
('I09','Bind reference meaning across snapshots','Identity contract gap','Graph invariants give local id/version uniqueness, not global immutability of content or kind. Existing byte bindings detect selected drift but do not authenticate issuers. Qualify immutable ref-to-content/kind bindings across snapshots or require a changed revision; reject same-reference substitution.','S15,S18,S09','formal/core/RelationalInput.lean','structure NodeRef'),
('I10','Version generic theory and executable profile separately','Integration contract gap','Frontend requires exact mandatory CORE and unique rule id/version; TheoryValid checks a more general logical theory. The verifier has a fixed import list and trusted catalogs. Specify stronger executable profile and checked mapping, update trusted catalogs from independent statement types, and retain decoder/generator trust limits.','S15,S05,S06,S10','inference/profile/frontend.py','def normalize'),
('I11','Resolve source wording before stronger theorem claims','Source-definition improvement','Each captured source was inspected. fulfills-request operational text says fulfillment while its question says intended fulfillment. successor-of specifies supersedes but leaves actual lifecycle/currentness policy outside generic strings. Role/posture declarations often mix intent, attempt and result. Fix independently reviewed meanings before promoting any stronger claim.','S00,S01,S18','registry/normalized-registry.json','relation.fulfills-request'),
('I12','Expose exact claim and model class in outcomes','API/definition gap','Derivation proves one query; checked closure proves profile-relative nonderivability; a countermodel refutes one implication. Stress certificates check listed Origins and shape, not GraphValid, a requested query or completeness. Closed, ModelValid and SemanticModel differ. Compose exact required obligations and name the result claim accurately.','S08,S10','relation-stress/v1/implementation/StressCheckers.lean','abbrev CertificateValid')]

PROPOSED=[
('MemberConformance','Inv(G), assertion membership and independent ConformsAt','S00,S02','A valid but unrecorded edge cannot support an observed fact.'),
('ConformsTo','reference × reference × scope; exact assessment-backed member conformance','S00,S02,S16','Sealed initial observation; no caller facts or rule heads.'),
('TargetKind','reference × text; exact node kind through a checked vocabulary map','S00,S02,S15','Independent sound/complete projection; kind text literal must be in captured domain.'),
('ExistentialConformanceView','Unary Conforms matches rich observations in projected initial inventory','S02,S18','No new rule writing old Conforms; not equality for arbitrary old models.'),
('SupportSet','Exact graph/assertion/assessment/profile witnesses for a deduplicated observation','S02,S16','Retain multiple supports; prove validity and source-support completeness.'),
('ProducerPolicy','Sealed observations versus derived ordinary information, orthogonal to root Role','S00,S15,S16','Every initial source and rule head authorized by exact selected profile.'),
('RegisteredBaseline','Bound graph/registry/theory/source/interpretation/epoch/policy/toolchain/catalog snapshot','S15','Independently qualify before use; displayed version is not readiness.'),
('BaselineTransition','Named richer-snapshot change with explicit fact/domain/assessment differences','S18,S09','Distinct from fixed-domain rule-only expansion; no reused incompatible receipts.'),
('RecursiveFreshExtension','Fixed domain/roots/old rules/facts with positive fresh derived ordinary heads','S03','Every-old-model expansion, finite stabilization, no unseeded facts.'),
('EvaluationKey','Profile, condition revision, exact context/snapshot, relevant endpoints and epoch','S00,S04','Consistent selected status; evaluator/interpretation identity bound.'),
('ConditionStatus','holds, does-not-hold, unknown; inconsistent selection gives conflict diagnostic','S04','No absence-as-false; no contradictory evidence projects holds.'),
('PotentialNorm','Inherited interpreted norm with exact Origin support','S00,S04,S07','No claim of true condition, subject conformance or fulfillment.'),
('ActiveNorm','PotentialNorm plus exact checked ConditionHolds in its context','S04,S07','False, unknown or mismatched context cannot activate; supplied truth explicit.'),
('ActiveConflict','Active require and active forbid at same subject/action/scope/evaluation context','S04,S07','Separate potential conflict; permit neither erases conflict nor grants authority.'),
('ClaimScope','Observed/candidate; query derivation/complete closure/model counterexample','S08,S10','No advertised guarantee beyond actually satisfied obligations.'),
('ResourceEnvelope','Early conservative bounds and measured stage work/time/allocation ceilings','S17,S11','Exhaustion is unknown and blocks closure, absence and readiness.'),
('SourceInterpretation','Exact qualifier/source/context-to-typed witness for a selected fragment','S04,S18','No guessed strings; extra fields mapped, assumed or explicitly unsupported.')]

definitions=[]
for relative,(category,refs,family) in MODULES.items():
 p=BASE/relative
 for kind,name,line,body in extract(p):
  id=relative+'#'+name
  definitions.append({'id':id,'category':category,'name':name,'declaration_kind':kind,'source':binding(p),'line':line,'definition_excerpt':body,'definition_excerpt_sha256':hashlib.sha256(body.encode()).hexdigest(),'analysis':SPECIAL.get(id,family),'finding_refs':refs.split(','),'review_status':'reviewed','disposition':'retain accepted meaning; add scoped contracts/controls where required'})
assert set(SPECIAL)<=set(d['id'] for d in definitions)
meanings={r.split('|')[0]:r.split('|')[1:] for r in (HERE/'definition-meanings.txt').read_text().strip().splitlines()}
assert {d['name'] for d in definitions}==set(meanings), ('meaning coverage gap', {d['name'] for d in definitions}^set(meanings))
for d in definitions:
 d['meaning'],d['boundary_question']=meanings[d['name']]

registry=load(BASE/'registry/normalized-registry.json');relations=[]
for raw in (HERE/'relation-notes.txt').read_text().strip().splitlines():
 name,current,gap,improvement,controls,refs,tasks=raw.split('|')
 k=next(k for k in registry['kinds'] if k['id']=='relation.'+name);p=ROOT/k['source']['path'];assert binding(p)==k['source'];payload=load(p)['payload']
 assert all(payload[f]==k[f] for f in ['unique_question','operational_effect','forbidden_inferences'])
 relations.append({'id':k['id'],'source':k['source'],'declared_version':k['version'],'endpoint_pairs':k['pairs'],'qualifier_fields':k['fields'],'qualifier_contract':payload['qualifier_contract'],'unique_question':payload['unique_question'],'operational_effect':payload['operational_effect'],'forbidden_inferences':k['forbidden_inferences'],'current_coverage':current,'gap':gap,'proposed_improvement':improvement,'controls':controls,'finding_refs':refs.split(','),'task_refs':tasks.split(','),'review_status':'reviewed','semantic_expansion_authorized':False})
assert len(relations)==41 and {r['id'] for r in relations}=={k['id'] for k in registry['kinds']}
findings=[]
for id,title,status,analysis,tasks,path,selector in FINDINGS:
 p=BASE/path;line=next(i for i,l in enumerate(p.read_text().splitlines(),1) if selector in l)
 findings.append({'id':id,'title':title,'classification':status,'analysis':analysis,'task_refs':tasks.split(','),'source':binding(p),'selector':selector,'line':line})
plan=copy.deepcopy(load(PARENT/'plan-proposal.json'))
plan.update(schema='relational.implementation-informed-plan/v2-candidate',supersedes_for_proposal_only=binding(PARENT/'plan-proposal.json'),review_inventory='definition-inventory.json',findings='findings.json',optimization_optional=True)
tasks={t['id']:t for t in plan['tasks']}
new_specs=[
('S15','N0','Specify registered baselines, profiles and obligation catalogs',['S01'],['I02','I03','I09','I10'],['BaselineContract.lean','baseline.schema.json','profile.schema.json','obligation-catalog.json','baseline-controls.json'],[
'Define graph, registry, theory, source, interpretation, policy, toolchain and epoch identity; distinguish canonical object identity from exact byte bindings.',
'Specify selected immutable reference-to-content/kind policy and independently checked baseline registration, without organizational admission.',
'Define producer-aware profiles, exact independent theorem catalogs and change-to-required-obligation selection; counts are generated, not caller-selected.',
'Specify stronger executable profile versus generic theory mapping and unsupported/mixed change handling.'],['Nonempty old rules','Same reference changed content/kind','Caller-shrunken catalog','Old receipt substituted for new profile','New kind/scope outside domain'],[
'Valid nonempty old-rule baselines can be represented without relaxed proof requirements.',
'Each supported change has an exact generated obligation inventory and checked manifest binding.',
'Same-reference semantic substitution and stale catalogs/toolchain are rejected.']),
('S16','N0','Prove sealed observations and supported derivation leaves',['S02','S15'],['I01','I07'],['ProducerPolicy.lean','SupportedObservations.lean','SupportLineage.lean','sealed-producer-controls.json'],[
'Define sealed source observations and permitted derived ordinary signals as orthogonal to root roles.',
'Reject caller seeds and rule heads for sealed predicates; accept observations only from an exact checked projector.',
'Prove source observation membership/derivability corresponds to independently defined member-source meaning with valid support leaves.',
'Preserve root lineage separately; allow derived informational heads only under the selected producer policy.'],['Constant-only semantic head','Caller-injected kind/conformance','Nonmember valid edge','Multiple source supports','Derived signal reads sealed observation'],[
'ConformsTo and TargetKind cannot be fabricated by caller seeds or ordinary rules in this profile.',
'Exact source-support and producer-coverage statements are independently audited.',
'Derived signals remain useful without becoming independent roots.']),
('S17','N1','Establish early grounding bounds and runtime feasibility',['S03','S04','S15','S16'],['I06'],['ResourceContract.lean','preflight-bounds.json','feasibility-probe.json','budget-controls.json'],[
'Calculate conservative substitution, atom-universe, stress candidate and conflict-pair bounds before product allocation.',
'Instrument small bounded reference probes with declared stage ceilings; distinguish estimates from observations.',
'If the reference exceeds the intended envelope, select a smaller explicit profile or bring necessary equivalence work forward before broadening runtime.',
'Define unknown resource-exhaustion outputs; partial closure cannot supply absence or readiness.'],['Large variable count with tiny input','Small graph and huge domain','Budget exceeded before allocation','Proof replay timeout','Overconservative bound'],[
'Feasibility and exhaustion contracts exist before rich runtime integration.',
'Over-budget inputs stop before expensive products; stage counters substantiate behavior.',
'No unsupported throughput or wall-clock completion guarantee is issued.']),
('S18','N1','Qualify source interpretations and richer baseline transitions',['S02','S04','S15','S16'],['I03','I08','I09','I11'],['SourceInterpretation.lean','BaselineTransition.lean','source-map.json','transition-controls.json'],[
'Map exact selected fields into independent meanings, accounting for evidence lists, endpoint fragments, opaque qualifiers and additional stress inputs.',
'Separate rule-only extension from graph, initial-fact, domain, assessment and interpretation changes.',
'Prove the declared initial projection/view relationship for richer migration; do not claim fixed domain or every-old-model expansion when hypotheses differ.',
'Qualify selected richer baseline and source/interpretation bindings; preserve unselected semantics as unsupported.'],['Multiple evidence tokens','Registry pair outside F0','New scope/kind literal','Opaque period','Changed interpretation at same source','Same reference changed content'],[
'Selected mappings have independently checked witnesses and explicit field coverage.',
'Richer transitions satisfy their distinct declared change class and theorem/validation targets.',
'All relation improvements are selected or deferred; review does not discharge unsupported meanings.'])]
for id,layer,title,deps,refs,outputs,algorithm,cases,criteria in new_specs:
 scope=plan['implementation_namespace']+'/'+id.lower()+'/'
 t={'id':id,'layer':layer,'title':title,'status':'proposed','depends_on':deps,'change_refs':['C01','C10'],'implementation_finding_refs':refs,'inputs':['S00 independent definitions and required statement types','Current source/implementation review and exact predecessor evidence'],'outputs':outputs,'write_scope':scope,'algorithm':algorithm,'edge_cases':cases,'acceptance_criteria':criteria,'validation':['Pinned Lean exact statement/proof audit for formal guarantees; no custom axioms or sorry.','Execute named meaningful positive/negative/context/drift controls and bind exact evidence.'],'authority_effect':'none'}
 t['working_units']=[{'id':'SWU-'+id,'parent':id,'title':title,'write_scope':scope,'evidence':outputs,'verification':t['validation']}];tasks[id]=t
corrections={
'S00':(['I01','I03','I04','I05','I07','I11','I12'],['Define candidate validity versus member observation, potential/active/fulfilled norm meanings, exact evaluation keys and conflicts.','Fix checked text encoding for node kinds, sealed producer policy and exact model/claim scope.']),
'S01':(['I08','I11'],['Classify every individual source review and select/defer each improvement against literal source text.']),
'S02':(['I03','I07','I08'],['Prove independent node-kind projection and kind-vocabulary/domain membership; nonmember validity cannot create a source fact.']),
'S03':(['I01','I02','I10'],['Preserve old rules/facts exactly; allow only declared fresh derived ordinary heads and retain sealed observation producer restrictions.']),
'S04':(['I04','I05','I08'],['Fix evaluation keys and consistent selected statuses; contradictory holds/does-not-hold blocks positive projection.','Prove potential inheritance independently of condition evaluation; active norms/conflicts require exact holds evidence.']),
'S05':(['I01','I02','I03','I06','I08','I10'],['Use earlier baseline/profile/catalog, sealed producer checks, qualified mappings and early work ceilings.','Version transport mapping and trusted import/statement catalog together; do not conflate tested decoder with proved equivalence.']),
'S06':(['I01','I02','I06','I10'],['Consume registered nonempty baselines/generated catalogs; replace captured ReviewSignal/CORE assumptions only in the new selected profile.']),
'S07':(['I04','I05','I08'],['Expose PotentialNorm, ActiveNorm and ActiveConflict distinctly; keep inheritance and conformance independent.','Select exact contextual evaluations; block contradictory/mismatched evidence without executing arbitrary condition strings.']),
'S08':(['I07','I11','I12'],['Label observed/candidate, supplied/proved, potential/active/fulfilled and exact model classes; distinguish complete versus partial evidence.']),
'S09':(['I02','I09'],['Consume previously specified baseline/profile schema; qualify two-step application with fresh evidence after each transition.']),
'S10':(['I01','I04','I05','I10','I12'],['Include sealed producer attacks, contradictory context status, inactive potential norms, model-class mismatch and limited certificate claims.']),
'S11':(['I06'],['Extend early S17 feasibility measurements to full qualified end-to-end costs.']),
'S12':(['I06'],['Optimize only a measured need; retain qualified reference fallback inside the declared envelope.']),
'S13':(['I01','I04','I05','I12'],['Include producer attacks, conflicting conditions, inactive potential norms and richer baseline transitions in pilot.']),
'S14':(['I11','I12'],['Keep source-meaning decisions, proof validity and actual human feedback separately assessed.'])}
for id,(refs,steps) in corrections.items():tasks[id]['implementation_finding_refs']=refs;tasks[id]['algorithm']+=steps
# Updated task acceptance checks for the newly discovered boundaries.
extra_checks={
 'S00':['Independent source-faithful and generic model classes are named; no observation truth is defined as checker success.'],
 'S02':['Target-kind projection has independently fixed soundness/completeness and exact vocabulary/domain targets.'],
 'S03':['Only declared derived heads are allowed; old rules and initial facts are byte/meaning bound and unchanged.'],
 'S04':['Contradictory selected evaluations cannot project holds; potential and active norm/conflict statements are distinct.'],
 'S05':['Caller/rule-injected sealed facts, profile/catalog substitution and over-budget preflight controls are rejected.'],
 'S07':['Unknown/false/conflicting conditions cannot activate norms; potential norm output remains available under its own meaning.'],
 'S08':['Each explanation names its exact model class, claimed query/closure scope and source versus supplied-truth leaves.'],
 'S09':['Same-reference content/kind substitution and old-baseline receipt reuse are blocked.'],
 'S10':['The limited stress certificate cannot be reported as whole-graph or complete-query qualification.']}
for id,criteria in extra_checks.items():
 tasks[id]['acceptance_criteria']+=criteria
 tasks[id]['validation']+=['Execute the new boundary controls listed in the acceptance criteria and retain exact scoped outcomes.']
 tasks[id]['working_units'][0]['verification']=tasks[id]['validation']
tasks['S04']['edge_cases']+=['Opposite selected statuses at same exact evaluation key','Same condition name at different context or revision','Potential norm with false or missing condition']
tasks['S05']['edge_cases']+=['Caller seed or rule head for a sealed observation','Reference kind/content substitution','Preflight budget refuses before Cartesian construction']

# Finish-to-start dependency corrections.
tasks['S03']['depends_on']=['S16']
tasks['S17']['depends_on']=['S02','S15','S16']
tasks['S05']['depends_on']=['S17','S18']
tasks['S06']['depends_on']=['S03','S05']
tasks['S07']['depends_on']=['S04','S05','S18']
tasks['S09']['outputs']=[o for o in tasks['S09']['outputs'] if o!='successor-baseline.schema.json']+['baseline-registration-qualification.json']
tasks['S09']['working_units'][0]['evidence']=tasks['S09']['outputs']
tasks['S13']['depends_on']=['S11']
tasks['S13']['conditional_dependencies']=[{'task':'S12','when':'optimized evaluator selected','otherwise':'use qualified reference within envelope'}]
ordered=[];remaining=list(tasks)
while remaining:
 ready=[id for id in remaining if set(tasks[id]['depends_on'])<=set(ordered)]
 assert ready,'cycle';ordered+=ready;remaining=[id for id in remaining if id not in ready]
plan['tasks']=[tasks[id] for id in ordered];plan['edge_count']=sum(len(t['depends_on']) for t in plan['tasks']);plan['conditional_edge_count']=1
plan['minimum_release_tasks']=['S00','S01','S02','S15','S16','S17','S18','S05','S08']
plan['release_policy']='Contextual observations/explanations may be reviewed after minimum_release_tasks and all their ancestors. Other profile integration/application/pilot follow their dependencies. Optimization is conditional; reference must fit declared measured limits.'
plan['deferred']+=['Full business semantics of every registry relation; source review does not authorize implementing all suggested profiles','Unqualified mixed graph/rule/domain changes','Arbitrary producers of sealed source observations']
extra_paths=['inference/profile/frontend.py','inference/integration/integration.py','evolution/proposals/classifier.py','workflow/evidence/bundle_contract.py','workflow/application-adapter/adapter.py','registry/build_registry.py']
allpaths={ROOT/d['source']['path'] for d in definitions}|{ROOT/r['source']['path'] for r in relations}|{ROOT/f['source']['path'] for f in findings}|{BASE/p for p in extra_paths}|{PARENT/'plan-proposal.json',PARENT/'DESIGN-PROPOSAL.md',BASE/'registry/normalized-registry.json'}
sources=[binding(p) for p in sorted(allpaths)]
dump('definition-inventory.json',{'schema':'relational.definition-review/v2-candidate','status':'authored-review-not-theorem-evidence','date':'2026-10-09','scope':'41 captured source relations; every explicit declaration in 18 selected production model/checker modules, excluding embedded witnesses; 17 successor concepts. Not generated/fixture modules, unnamed instances or every Python utility.','modules':list(MODULES),'formal_definitions':definitions,'relations':relations,'proposed_definitions':[{'name':n,'meaning':m,'task_refs':t.split(','),'required_boundary':b} for n,m,t,b in PROPOSED]})
dump('source-bindings.json',{'sources':sources,'inherited_audit':binding(PARENT/'baseline-audit.json'),'parent_snapshot_bindings':[binding(p) for p in sorted(PARENT.iterdir()) if p.is_file()]})
dump('findings.json',{'status':'proposal-only','findings':findings,'inherited_findings':'../findings-and-changes.json','inherited_changes':'C01-C10 retained; I01-I12 refine scopes/dependencies'})
dump('revised-plan.json',plan)
dump('swu-manifest.json',{'status':'proposed','units':[u for t in plan['tasks'] for u in t['working_units']]})
lines=['# Review of model and semantic definitions','','Date: 2026-10-09. These are source-bound design reviews, not newly checked theorems. Retained definitions keep their original meaning; improvements belong to successor profiles.','','Scope: '+str(len(definitions))+' explicit declarations in '+str(len(MODULES))+' selected production modules, 41 source relations in the companion review, and 17 proposed concepts. Generated/fixture modules, unnamed instances and general Python utilities are excluded.','','A definition can be correct for its purpose while insufficient for a stronger claim. Candidate-edge validity intentionally omits membership. Horn soundness assumes initial fact truth. Inherited norms do not require true conditions. The successor must compose these boundaries explicitly.','']
for relative,(category,refs,family) in MODULES.items():
 lines+=['## '+category,'',link(BASE/relative),'',family,'']
 for d in definitions:
  if d['source']['path']==str((BASE/relative).relative_to(ROOT)):
   lines+=['### '+d['name'],'','**Meaning:** '+d['meaning'],'','**Boundary to check:** '+d['boundary_question'],'','Exact current definition, '+link(BASE/relative,d['line'])+':','','```lean',d['definition_excerpt'],'```','','**Review:** '+d['analysis'],'','**Disposition:** retain this definition for its current claim. Findings: '+', '.join(d['finding_refs'])+'. Any stronger claim needs the linked profile obligations.','']
lines+=['## Successor definitions to fix first','','| Definition | Proposed meaning | Required boundary | Tasks |','|---|---|---|---|']
for n,m,t,b in PROPOSED:lines.append('| `'+n+'` | '+m+' | '+b+' | '+t+' |')
(HERE/'DEFINITION-REVIEW.md').write_text('\n'.join(lines)+'\n')
lines=['# Review of each captured relation definition','','All 41 selected sources were inspected and checked against their exact source hashes and the normalized registry. Each card distinguishes declaration, interpretation and theorem coverage. Source versions, all endpoint pairs and qualifier contracts are preserved in definition-inventory.json. These suggestions add no runtime semantics and discharge no unsupported item.','','Only selected F0 meanings and the two separately typed stress profiles have the semantic coverage described here. Each proposed control still needs execution under its selected successor profile.','']
for i,r in enumerate(relations,1):
 lines+=['## '+str(i)+'. '+r['id'].removeprefix('relation.'),'',link(ROOT/r['source']['path']),'','**Source question:** '+r['unique_question'],'','**Declared effect:** '+r['operational_effect'],'','**Endpoint policy:** '+str(len(r['endpoint_pairs']))+' exact pairs in the inventory. **Required qualifiers:** '+', '.join('`'+f+'`' for f in r['qualifier_fields'])+'.','','**Current coverage:** '+r['current_coverage'],'','**Gap:** '+r['gap'],'','**Improvement:** '+r['proposed_improvement'],'','**Required controls:** '+r['controls'],'','**Keep independent:** '+', '.join(r['forbidden_inferences'])+'.','','**Plan:** '+', '.join(r['task_refs'])+'. **Findings:** '+', '.join(r['finding_refs'])+'.','']
(HERE/'RELATION-REVIEW.md').write_text('\n'.join(lines)+'\n')
lines=['# Revised implementation plan','','Status: proposed, not executed. This revision refines the earlier 15-task proposal into '+str(len(plan['tasks']))+' tasks, '+str(plan['edge_count'])+' required edges and one conditional optimization edge. Original 33 accepted tasks and pending human R06/G4 remain unchanged.','','Formalization remains first. Four new prerequisite tasks establish registered baselines/profiles, sealed observations, early resource feasibility and explicit source/data transitions before runtime integration. Optional optimization no longer blocks the reference pilot.','','```mermaid','flowchart TD']
for t in plan['tasks']:lines.append('  '+t['id']+'["'+t['id']+' '+t['title'].replace('"',"'")+'"]')
for t in plan['tasks']:
 for dep in t['depends_on']:lines.append('  '+dep+' --> '+t['id'])
lines+=['  S12 -. "if optimized evaluator selected" .-> S13','```','','## Corrected task scopes','','| Task | Prerequisites | Concrete revised boundary |','|---|---|---|']
for t in plan['tasks']:lines.append('| '+t['id']+' '+t['title']+' | '+(', '.join(t['depends_on']) or 'First step')+' | '+' '.join(t['algorithm'][-2:])+' |')
lines+=['','## Delivery and scheduling','','The contextual observation/explanation milestone requires '+', '.join(plan['minimum_release_tasks'])+' and all their ancestors. The shared S04/S18 work fixes selected interpretation and transition contracts, not a universal condition language. Runtime recursion and stress integration follow their own S06/S07 tasks.','','S17 establishes early feasibility. S11 measures the full qualified workflow. S12 executes only for a measured optimization need; a qualified reference implementation can proceed from S11 to S13 within declared limits. If S17 already shows the reference cannot fit the intended envelope, bring necessary equivalence work forward in a separate revision before widening runtime guards.','','No duration or throughput promise follows from this DAG. Each completed task needs real independent predecessor evidence. A plan receipt is not implementation evidence and a machine pass is not human assessment.','','See '+link(HERE/'WORK-PACK.md')+' for inputs, algorithms, edge cases, acceptance criteria, verification and owned working unit for each task.']
(HERE/'REVISED-PLAN.md').write_text('\n'.join(lines)+'\n')
lines=['# Detailed revised work pack','','All tasks are proposed. Write scopes are future v2 namespaces; this review creates no v2 implementation. Inherited C01–C10 and new I01–I12 remain traceable in revised-plan.json.','']
for t in plan['tasks']:
 lines+=['## '+t['id']+' — '+t['title'],'','Dependencies: '+(', '.join(t['depends_on']) or 'none; formalization first')+'. Layer: '+t['layer']+'. Working unit: `SWU-'+t['id']+'`.','','Write scope: `'+t['write_scope']+'`. Findings: '+', '.join(t.get('implementation_finding_refs',[]))+'.','']
 for label,key in [('Inputs','inputs'),('Outputs','outputs'),('Algorithm','algorithm'),('Edge cases','edge_cases'),('Acceptance criteria','acceptance_criteria'),('Verification','validation')]:lines+=['### '+label,'']+['- '+s for s in t[key]]+['']
(HERE/'WORK-PACK.md').write_text('\n'.join(lines)+'\n')
lines=['# Implementation-informed review','','The successor direction remains useful: preserve contextual conformance, support finite ordinary recursion, and map the two stress relations into checked profiles. The implementation shows four missing prerequisite tasks and tighter definition boundaries before runtime integration.','','These findings distinguish prospective design holes from v1 failures. The current workflow intentionally supports its captured empty-rule/ReviewSignal profile. Nothing here establishes a false v1 admission. Original accepted artifacts are preserved; R06/G4 still need actual human assessment.','','## A concrete semantic producer gap','','Suppose the graph supports `ConformsTo(A, ContractA, Scope1)` but no assertion about ContractB. A generic positive rule `Conforms(A) → ConformsTo(A, ContractB, Scope1)` can be well typed if its constants are in the domain and the target predicate is ordinary. A derivation proves consequence of that rule. It does not prove an assessment for ContractB exists. The current generic normalizer accepts this ordinary-rule shape; the current captured workflow blocks its new head. The successor must seal observation producers while permitting rules to derive separately defined informational signals.','','A second example: `require Ship` under condition `ApprovalGranted` becomes a potential inherited norm in the stress profile without a condition assessment. That is coherent inheritance meaning. Calling it active requires an exact holds witness. Calling it fulfilled requires separate action evidence.','','## Findings and required changes','']
for f in findings:lines+=['### '+f['id']+' — '+f['title'],'',f['classification']+'. '+f['analysis'],'','Evidence: '+link(ROOT/f['source']['path'],f['line'])+'. Tasks: '+', '.join(f['task_refs'])+'.','']
lines+=['## What remains useful','','Retain exact endpoint/version/evidence checks, generic positive derivation and complete-closure theorems, independent root lineage, checked countermodels and universal structural preservation. No blanket cycle ban, mandatory gate, global single-assessment restriction or new negation is proposed. Instead each successor profile declares its permitted producers, interpretation, model class and change classes.','','## Review package','','- '+link(HERE/'DEFINITION-REVIEW.md')+': every selected current production declaration and the 17 proposed concepts.','- '+link(HERE/'RELATION-REVIEW.md')+': all 41 relation sources with specific gaps, improvements and controls.','- '+link(HERE/'DESIGN-AMENDMENTS.md')+': exact producer, condition, source, baseline and API boundaries.','- '+link(HERE/'REVISED-PLAN.md')+': corrected DAG and delivery milestones.','- '+link(HERE/'WORK-PACK.md')+': detailed work for each task.','','## Verification ceiling','','The package validator checks exhaustive inventory coverage within the declared module selection, exact current source bytes, preserved accepted evidence, finding/task traceability and DAG dependencies. A readonly probe exercises current Python normalization. No successor Lean proof, performance qualification, runtime API or human assessment is created by this review. See validation-report.json and probe-report.json for exact results.']
(HERE/'REVIEW.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'formal_definitions':len(definitions),'modules':len(MODULES),'relations':len(relations),'proposed_concepts':len(PROPOSED),'tasks':len(plan['tasks']),'required_edges':plan['edge_count'],'sources':len(sources)}))
