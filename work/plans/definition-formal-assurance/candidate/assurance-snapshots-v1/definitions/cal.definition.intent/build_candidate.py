"""Prepared Intent source-qualified classification, seven coordinates, explained revision and claim trace guards."""
import hashlib,json,sys
from pathlib import Path
UNIT=Path(__file__).resolve().parent;ROOT=Path.cwd();BASE=ROOT/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1'
IMPL=ROOT/'craft/formalization/candidates/definition-assurance-v1';sys.path[:0]=[str(IMPL),str(BASE/'units/A04')]
import contracts as c
import ir
import resolver as r
import correspondence as co
def var(n):return {'op':'var','name':n}
def const(n):return {'op':'const','name':n}
def pred(n,*args):return {'op':'pred','name':n,'args':[var(x) if isinstance(x,str) else x for x in args]}
def fn(n,*args):return {'op':'fn','name':n,'args':[var(x) if isinstance(x,str) else x for x in args]}
def both(*args):return {'op':'and','args':list(args)}
def either(*args):return {'op':'or','args':list(args)}
def neg(a):return {'op':'not','arg':a}
def implies(a,z):return either(neg(a),z)
def eq(a,z):return {'op':'eq','left':a,'right':z}
def bind(bindings,body):
 for op,sort,name in reversed(bindings):body={'op':op,'sort':sort,'var':name,'body':body}
 return body
def allof(bindings,body):return bind([('forall',sort,name) for sort,name in bindings],body)
def exists(bindings,body):return bind([('exists',sort,name) for sort,name in bindings],body)
def ref(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def put(n,value):
 with (UNIT/n).open('x') as out:json.dump(value,out,sort_keys=True,separators=(',',':'));out.write('\n')
 return ref(UNIT/n)
def snapshot():return json.loads((BASE/'current-snapshot.json').read_bytes())
def unchanged(refs):
 for x in refs:
  if ref(ROOT/x['path'])!=x:raise ValueError('Changed selected input '+x['path'])
def external_current(context):
 for x in context['external_sources']:
  if r.digest(Path(x['absolute_path']).read_bytes())!=x['sha256']:raise ValueError('External source drift')
def source_ref(snap,id):
 row=next(x for x in snap['current_entries'] if x['definition_id']==id)
 return {k:row[k] for k in ['definition_id','version_ref','path','sha256']}


SCOPE='scope:candidate:Intent-seven-coordinates-normalized-classification-explained-revision-claim-trace-v1'
SORTS=['IntentReference','SourceReference','PurposeReference','ScopeReference','ConstraintCollectionReference','PressureReference','OutputHypothesisReference','RevisionRouteReference','AttributorReference','MeaningReference','CoordinationScopeReference','CarrierTypeReference','SourceSectionReference','SiblingTargetReference','ChangeReference','ReasonReference','ClaimReference','TraceTargetReference','Token']
CONSTANTS={'EMPTY':'Token','NORMALIZED_MEANING':'MeaningReference','COORDINATION_SCOPE':'CoordinationScopeReference','DEFINITION_CARRIER':'CarrierTypeReference','BOUND_SOURCE_SECTION':'SourceSectionReference'}
FIELDS={'intentSource':'SourceReference','intentPurpose':'PurposeReference','intentScope':'ScopeReference','intentConstraints':'ConstraintCollectionReference','intentTargetPressure':'PressureReference','intentOutputHypothesis':'OutputHypothesisReference','intentRevisionRoute':'RevisionRouteReference'}
CLASS_FIELDS={'intentMeaning':'MeaningReference','intentOwnerScope':'CoordinationScopeReference','intentCarrierType':'CarrierTypeReference'}
CHANGE_FIELDS={'changeOriginalIntent':'IntentReference','changeDesiredHypothesis':'OutputHypothesisReference','changeAfterIntent':'IntentReference','changeRevisionRoute':'RevisionRouteReference'}
CLAIM_FIELDS={'claimIntent':'IntentReference','claimTraceTarget':'TraceTargetReference'}
GROUPS=[(FIELDS,'IntentReference'),(CLASS_FIELDS,'IntentReference'),(CHANGE_FIELDS,'ChangeReference'),(CLAIM_FIELDS,'ClaimReference')]
FUNCTIONS={name:([carrier],sort) for fields,carrier in GROUPS for name,sort in fields.items()};HANDLES={sort:sort[0].lower()+sort[1:]+'Handle' for sort in SORTS if sort!='Token'};FUNCTIONS.update({name:([sort],'Token') for sort,name in HANDLES.items()})
MODES=['Purpose','DesiredCapability','ProblemPressure','ChangeDirection']
EXCLUDED=['IntentIs'+name+'Declared' for name in ['Requirement','Artifact','Proof','MutationCommand','ScopeApproval']]+['IntentSilentlyReplacedByArtifactDeclared','IntentSilentlyReplacedByImplementationDeclared']
INFERRED=['Admission','Activation','Publication','Release','Deployment','ExternalEffect','MutationAuthority','ScopeApproval','Fulfillment']
FACETS=['GateEffects','Authority','Evidence','LaterArtifacts']
ACTUAL=['AttributionAuthenticity','SourceAuthenticity','PurposeResolution','ScopeResolution','ScopeCompliance','ConstraintEnforcement','PressureResolution','HypothesisSuitability','RevisionRouteOperation','Revisability','Traceability','NormalizedIdentityFidelity','ClassificationFidelity','SourceRelationFidelity','OwnerQualification','RoutingSuitability','Fulfillment','ClaimSupport','ArtifactAdmission','DecisionEffect','MutationAuthority','ScopeApproval','Publication','Release','Deployment','ExternalEffect','SourceFidelity','WholeProof']
CHANGE_ACTUAL=['HypothesisChangeAuthenticity','ExplanationRecorded','ExplanationAdequacy','RevisionAuthenticity','IntentContinuity','WholeProof']
CLAIM_ACTUAL=['TargetResolution','TraceAuthenticity','Satisfaction','OwnerAcceptance','DecisionEffect','EvidenceAdequacy','ScopeCompliance','WholeProof']
TRACE_KINDS=['Artifact','Decision','Residue','NextRoute']
SIGNATURE={name:['IntentReference'] for name in ['IntentApplicable','IntentInScopeDeclared','IntentAttributableDeclared','IntentRouteBoundedDeclared','IntentRevisableDeclared','IntentTraceableDeclared','CanonicalIntentDeclared',*['IntentOrientation'+name+'Declared' for name in MODES],*EXCLUDED,*['IntentTermInfers'+name+'Declared' for name in INFERRED],*['Intent'+name+'SeparatelyGovernedDeclared' for name in FACETS],*['IntentActual'+name for name in ACTUAL]]}
SIGNATURE.update({name:['ChangeReference'] for name in ['ChangeApplicable','ChangeInScopeDeclared',*['ChangeActual'+name for name in CHANGE_ACTUAL]]})
SIGNATURE.update({name:['ClaimReference'] for name in ['ClaimApplicable','ClaimInScopeDeclared','ClaimSatisfactionClaimDeclared',*['ClaimTraceKind'+name+'Declared' for name in TRACE_KINDS],*['ClaimActual'+name for name in CLAIM_ACTUAL]]})
SIGNATURE.update({name:['OutputHypothesisReference'] for name in ['HypothesisCodeOutputDeclared','HypothesisDeferredQuestionDeclared','HypothesisFinalShapeSettledDeclared']})
for sort in SORTS:
 if sort!='Token':SIGNATURE[sort+'Declared']=[sort]
for fields,carrier in GROUPS:SIGNATURE.update({name+'BindingDeclared':[carrier,sort] for name,sort in fields.items()})
SIGNATURE.update(IntentAttributionDeclared=['IntentReference','AttributorReference'],IntentOriginatesFromSectionDeclared=['IntentReference','SourceSectionReference'],IntentUsesSiblingMeaningDeclared=['IntentReference','SiblingTargetReference'],IntentExplicitSiblingReferenceDeclared=['IntentReference','SiblingTargetReference'],IntentSilentlyMergesSiblingDeclared=['IntentReference','SiblingTargetReference'],ChangeExplanationReasonDeclared=['ChangeReference','ReasonReference'],RouteRecordsChangeReasonDeclared=['RevisionRouteReference','ChangeReference','ReasonReference'],IntentTraceTargetDeclared=['IntentReference','TraceTargetReference'])
MAP={'IntentReference':'IntentApplicable','ChangeReference':'ChangeApplicable','ClaimReference':'ClaimApplicable'}
def iff(a,z):return {'op':'iff','left':a,'right':z}
def member(sort):return MAP.get(sort,sort+'Declared')
def guard(sort,value):return both(pred(member(sort),value),neg(eq(fn(HANDLES[sort],value),const('EMPTY'))))
def exact(fields,value):return both(*[both(guard(sort,fn(name,value)),allof([(sort,'target')],iff(pred(name+'BindingDeclared',value,'target'),eq(var('target'),fn(name,value))))) for name,sort in fields.items()])
def selected(sort,name,body):return allof([(sort,name)],implies(pred(member(sort),name),body))
X=var('x');C=var('c');Q=var('q');APP=pred('IntentApplicable',X);CHANGE=pred('ChangeApplicable',C);CLAIM=pred('ClaimApplicable',Q)
ROOT_RULE=both(allof([('IntentReference','x')],iff(APP,pred('IntentInScopeDeclared',X))),selected('IntentReference','x',both(guard('IntentReference',X),exact(FIELDS,X),*[pred(name,X) for name in ['IntentAttributableDeclared','IntentRouteBoundedDeclared','IntentRevisableDeclared','IntentTraceableDeclared']],either(*[pred('IntentOrientation'+name+'Declared',X) for name in MODES]),exists([('AttributorReference','attributor')],both(guard('AttributorReference',var('attributor')),pred('IntentAttributionDeclared',X,'attributor'))))))
CLASS_RULE=both(*[guard(sort,const(name)) for name,sort in CONSTANTS.items() if name!='EMPTY'],allof([('IntentReference','x')],implies(both(APP,pred('CanonicalIntentDeclared',X)),both(exact(CLASS_FIELDS,X),eq(fn('intentMeaning',X),const('NORMALIZED_MEANING')),eq(fn('intentOwnerScope',X),const('COORDINATION_SCOPE')),eq(fn('intentCarrierType',X),const('DEFINITION_CARRIER')),pred('IntentOriginatesFromSectionDeclared',X,const('BOUND_SOURCE_SECTION'))))))
SIBLING_RULE=selected('IntentReference','x',allof([('SiblingTargetReference','sibling')],both(neg(pred('IntentSilentlyMergesSiblingDeclared',X,'sibling')),implies(pred('IntentUsesSiblingMeaningDeclared',X,'sibling'),both(guard('SiblingTargetReference',var('sibling')),pred('IntentExplicitSiblingReferenceDeclared',X,'sibling'))))))
ORIGINAL=fn('changeOriginalIntent',C);AFTER=fn('changeAfterIntent',C);DESIRED=fn('changeDesiredHypothesis',C);DELTA=neg(eq(fn('intentOutputHypothesis',ORIGINAL),DESIRED))
CHANGE_RULE=both(allof([('ChangeReference','c')],iff(CHANGE,pred('ChangeInScopeDeclared',C))),selected('ChangeReference','c',both(guard('ChangeReference',C),exact(CHANGE_FIELDS,C),eq(fn('intentOutputHypothesis',AFTER),DESIRED),eq(fn('changeRevisionRoute',C),fn('intentRevisionRoute',AFTER)),implies(DELTA,exists([('ReasonReference','reason')],both(guard('ReasonReference',var('reason')),pred('ChangeExplanationReasonDeclared',C,'reason'),pred('RouteRecordsChangeReasonDeclared',fn('changeRevisionRoute',C),C,'reason')))))))
CLAIM_RULE=both(allof([('ClaimReference','q')],iff(CLAIM,pred('ClaimInScopeDeclared',Q))),selected('ClaimReference','q',both(guard('ClaimReference',Q),exact(CLAIM_FIELDS,Q),pred('ClaimSatisfactionClaimDeclared',Q),either(*[pred('ClaimTraceKind'+name+'Declared',Q) for name in TRACE_KINDS]),pred('IntentTraceTargetDeclared',fn('claimIntent',Q),fn('claimTraceTarget',Q)))))
BOUNDARIES=selected('IntentReference','x',both(*[neg(pred(name,X)) for name in EXCLUDED]))
NONINFERENCE=selected('IntentReference','x',both(*[neg(pred('IntentTermInfers'+name+'Declared',X)) for name in INFERRED]))
GOVERNANCE=selected('IntentReference','x',both(*[pred('Intent'+name+'SeparatelyGovernedDeclared',X) for name in FACETS]))
THEORY={'seven-coordinates-attribution-orientation':ROOT_RULE,'canonical-classification-and-source-relation':CLASS_RULE,'explicit-sibling-use-no-silent-merge':SIBLING_RULE,'changed-output-matched-state-and-recorded-why':CHANGE_RULE,'claimed-satisfaction-explicit-trace':CLAIM_RULE,'concept-and-silent-substitution-boundaries':BOUNDARIES,'intent-alone-does-not-infer-effects':NONINFERENCE,'gates-authority-evidence-later-artifacts-separate':GOVERNANCE}
LOSSES=[
'C53 exact Definition and58 source-use admissions are separate from immutable embedded candidate posture; neither accepts this translation or creates Intent instances.',
'C12 owner-selected normalization defaults, prototype scaffold and C53 admitted normalized Definition have different scopes and effects.',
'Canonical classification preserves semantic.intent, scope.coordination and type.definition, without equating work scope with owner scope or granting Artifact Type authority.',
'Seven proposed coordinates are necessary nominations; auxiliary attribution, change, claim and classification relations do not become new canonical Definitions.',
'Orientation purpose, desired capability, problem pressure or change direction is inclusive; there is no mandatory Capability endpoint or final output kind.',
'Attribution and source handles are nominated links; they do not authenticate the requester, source ownership or original intent.',
'Route bounds, constraints and scope remain separately interpreted; no source-independent complete scope algebra or permissions are invented.',
'Revisability and traceability are required declarations; an Intent may have no existing artifact or satisfaction claim before discovery proceeds.',
'Canonical selected records preserve the accepted source section relation; additional explicit references do not establish meaning equality or source authority transfer.',
'Canonical-record interpretation requires owner review; noncanonical selected work records are not automatically normalized Definition instances.',
'Split or reclassified sibling meaning use requires explicit reference and no silent merge; no source hierarchy, injective naming or exhaustive sibling taxonomy is imposed.',
'Desired output hypothesis is independent of the after reference, so a changed-output comparison cannot evade explanation by naming the before record as after.',
'Changed output requires a declared reason recorded in the nominated after revision route; no unique reason, timestamp order or global identity succession rule is imposed.',
'A no-output-change record may have no explanation requirement under this guard; other revisions and policies remain owner-defined.',
'Code, deferred question and unsettled or settled output hypotheses remain possible; no mandatory artifact delivery or immutable initial wording is introduced.',
'Refinement, split, rename and rejection are permitted source operations, not mandatory transitions or new automatic identity effects.',
'Satisfaction claims nominate Intent and artifact, decision, residue or next-route targets; claim links do not establish actual fulfillment or owner acceptance.',
'Kind labels and nominal carrier separation alone do not prove real conceptual non-collapse or authentic target resolution.',
'Intent is not a requirement, artifact, proof, mutation command or scope approval; independently justified effects can still exist with separate evidence and gates.',
'Actual explanation adequacy, revision authenticity, continuity, attribution, traceability, satisfaction, authority and source fidelity remain targets outside T.',
'Exact C53 selector normalization and positive source-use row preserve selected D39 bytes; unselected external meanings and private source ownership are not imported.',
'Required finite populations and countermodels establish reported candidate calculations, not actual enumeration, accepted common meaning or whole-definition proof.',
'Original T/O/E/R/J artifacts, owner and consumer reviews, dependency-cycle classification and complete final aspect explanation remain required.'
]
def declarations():return [{'kind':'sort','symbol_id':name,'scope':SCOPE,'domain_policy':'nonempty'} for name in SORTS]+[{'kind':'constant','symbol_id':name,'scope':SCOPE,'result_sort':sort} for name,sort in CONSTANTS.items()]+[{'kind':'total-function','symbol_id':name,'scope':SCOPE,'argument_sorts':args,'result_sort':result,'definedness_policy':None} for name,(args,result) in FUNCTIONS.items()]+[{'kind':'predicate' if len(args)==1 else 'relation','symbol_id':name,'scope':SCOPE,'argument_sorts':args} for name,args in SIGNATURE.items()]
def required_populations():
 def xw(body):return exists([('IntentReference','x')],both(APP,body))
 def cw(body):return exists([('ChangeReference','c')],both(CHANGE,body))
 def qw(body):return exists([('ClaimReference','q')],both(CLAIM,body))
 rows={'Intent':('IntentReference',xw(APP)),'OutsideIntent':('IntentReference',exists([('IntentReference','x')],neg(APP))),'CanonicalIntent':('IntentReference',xw(pred('CanonicalIntentDeclared',X))),'NoncanonicalIntent':('IntentReference',xw(neg(pred('CanonicalIntentDeclared',X))))}
 for mode in MODES:rows['Orientation'+mode+'Only']=('IntentReference',xw(both(pred('IntentOrientation'+mode+'Declared',X),*[neg(pred('IntentOrientation'+other+'Declared',X)) for other in MODES if other!=mode])))
 rows.update(MixedOrientation=('IntentReference',xw(both(pred('IntentOrientationPurposeDeclared',X),pred('IntentOrientationProblemPressureDeclared',X)))),WithoutActualOutcomes=('IntentReference',xw(both(*[neg(pred('IntentActual'+name,X)) for name in ACTUAL]))),IndependentMutationAuthority=('IntentReference',xw(pred('IntentActualMutationAuthority',X))),DeferredOutputHypothesis=('OutputHypothesisReference',xw(pred('HypothesisDeferredQuestionDeclared',fn('intentOutputHypothesis',X)))),CodeOutputHypothesis=('OutputHypothesisReference',xw(pred('HypothesisCodeOutputDeclared',fn('intentOutputHypothesis',X)))),UnsettledOutputHypothesis=('OutputHypothesisReference',xw(neg(pred('HypothesisFinalShapeSettledDeclared',fn('intentOutputHypothesis',X))))),SettledOutputHypothesis=('OutputHypothesisReference',xw(pred('HypothesisFinalShapeSettledDeclared',fn('intentOutputHypothesis',X)))),IntentWithoutClaims=('IntentReference',xw(neg(exists([('ClaimReference','q')],both(CLAIM,eq(fn('claimIntent',Q),X)))))),ExplicitSiblingWithoutUse=('SiblingTargetReference',xw(exists([('SiblingTargetReference','sibling')],both(pred('IntentExplicitSiblingReferenceDeclared',X,'sibling'),neg(pred('IntentUsesSiblingMeaningDeclared',X,'sibling')))))),ExplicitUsedSibling=('SiblingTargetReference',xw(exists([('SiblingTargetReference','sibling')],both(pred('IntentExplicitSiblingReferenceDeclared',X,'sibling'),pred('IntentUsesSiblingMeaningDeclared',X,'sibling'))))),Change=('ChangeReference',cw(CHANGE)),OutsideChange=('ChangeReference',exists([('ChangeReference','c')],neg(CHANGE))),ChangedOutput=('ChangeReference',cw(DELTA)),NoOutputChange=('ChangeReference',cw(neg(DELTA))),MultipleExplanationReasons=('ReasonReference',cw(exists([('ReasonReference','reason'),('ReasonReference','other')],both(pred('ChangeExplanationReasonDeclared',C,'reason'),pred('ChangeExplanationReasonDeclared',C,'other'),neg(eq(var('reason'),var('other'))))))),ChangeWithoutActualOutcomes=('ChangeReference',cw(both(*[neg(pred('ChangeActual'+name,C)) for name in CHANGE_ACTUAL]))),Claim=('ClaimReference',qw(CLAIM)),OutsideClaim=('ClaimReference',exists([('ClaimReference','q')],neg(CLAIM))),ClaimWithoutActualSatisfaction=('ClaimReference',qw(neg(pred('ClaimActualSatisfaction',Q)))),IndependentlySatisfiedClaim=('ClaimReference',qw(pred('ClaimActualSatisfaction',Q))))
 for kind in TRACE_KINDS:rows[kind+'Claim']=('TraceTargetReference',qw(pred('ClaimTraceKind'+kind+'Declared',Q)))
 return rows
def query_specs():
 rows=[]
 for prefix,sort,name,app,outcomes in [('Intent','IntentReference','x',APP,ACTUAL),('Change','ChangeReference','c',CHANGE,CHANGE_ACTUAL),('Claim','ClaimReference','q',CLAIM,CLAIM_ACTUAL)]:
  for outcome in outcomes:rows.append({'query_id':prefix+'-not-Actual'+outcome,'target':allof([(sort,name)],implies(app,pred(prefix+'Actual'+outcome,name))),'witness_condition':exists([(sort,name)],both(app,neg(pred(prefix+'Actual'+outcome,name)))),'selected_in_T':False,'source_condition':'selected-'+prefix.lower(),'source_fidelity':'pending'})
 return rows
def selected_clauses(doc):
 chosen={'/voices/scientific_formal/normative_statement':(both(ROOT_RULE,CLASS_RULE,SIBLING_RULE,CLAIM_RULE,BOUNDARIES),['genus-differentia']),'/voices/scientific_formal/formal_expression':(both(ROOT_RULE,CHANGE_RULE),['axiomatic-implicit']),'/scope/applicability':(ROOT_RULE,['genus-differentia']),'/scope/exclusions/0':(NONINFERENCE,['operational']),'/scope/exclusions/1':(SIBLING_RULE,['operational']),'/voices/scientific_formal/boundary_conditions/0':(both(BOUNDARIES,NONINFERENCE,GOVERNANCE),['operational']),'/voices/scientific_formal/testable_conditions/0':(CLASS_RULE,['operational']),'/boundaries/0':(both(BOUNDARIES,NONINFERENCE,GOVERNANCE),['operational'])}
 texts=dict(co.string_leaves(doc));rows=[]
 for unit in co.inventory(doc):
  selector=unit['selector'];formula,forms=chosen.get(selector,(None,['unresolved']));disposition='encoded' if formula is not None else 'explanatory' if selector.startswith('/voices/') and any(name in selector for name in ['/domain_context/','/plain_language/','/notation/']) else 'deferred';rows.append({'source_selector':selector,'start_character':0,'excerpt':texts[selector],'formula':formula,'forms':forms,'disposition':disposition,'unit_id':unit['unit_id']})
 return rows

def main():
 context=json.loads((UNIT/'context.json').read_bytes());unchanged(context['sources']);external_current(context);snap=snapshot();r.verify(snap,ROOT);source=context['source_selection'];assert source['definition_id']=='cal.definition.intent' and source['sha256']=='cce7b46ddc9bf4f7b42038c15da1380573e58d9bb2919d86b94a7c1738325c0b'
 doc=co.source_document(snap,source);units=co.inventory(doc);clauses=[];links=[];reasons={'encoded':'Necessary seven-coordinate, classification, attribution, explained revision, claim trace and boundary declarations; actual outcomes remain independent.','explanatory':'Notation, intuition and examples explain the selected source without becoming authority or requiring final code output.','deferred':'Authority scope, currentness/schema/projection checks and candidate no-effect ceiling are explicit independently checked source obligations.'}
 for row in selected_clauses(doc):
  cid='INTENT-'+str(len(clauses)+1).zfill(3);disposition=row['disposition'];clauses.append({'clause_id':cid,'source_selector':row['source_selector'],'excerpt_sha256':r.digest(row['excerpt'].encode()),'start_character':row['start_character'],'disposition':disposition,'forms':row['forms'],'roles':['definition'] if disposition=='encoded' else ['explanation-example'] if disposition=='explanatory' else ['unresolved'],'formal_statement':row['formula'],'rationale':reasons[disposition]});links.append({'unit_id':row['unit_id'],'clause_id':cid,'end_character':row['start_character']+len(row['excerpt']),'excerpt':row['excerpt']})
 deps=[source_ref(snap,name) for name in context['direct_dependency_names']];primary=next(row['clause_id'] for row in clauses if row['source_selector']=='/voices/scientific_formal/normative_statement');req=required_populations()
 populations=[{'population_id':'POP-REQ-'+name,'carrier':carrier,'predicate_ref':None,'requirement':'required','statement':formula,'scope':SCOPE,'rationale':'Independent canonical/noncanonical, orientation, output, change, explanation, explicit sibling, claim and noninferential outcome witnesses.','review_ref':None} for name,(carrier,formula) in req.items()]+[{'population_id':'POP-UNRESOLVED-'+name,'carrier':args[0],'predicate_ref':name if len(args)==1 else None,'requirement':'unresolved','statement':None,'scope':SCOPE,'rationale':'Actual populations and accepted owner or consumer denotations remain unresolved.','review_ref':None} for name,args in SIGNATURE.items()]
 core={'source':source,'interpretation_id':'interpretation:Intent-seven-coordinates-classification-explained-revision-trace-v1','profile_ref':'profile:definition-assurance-partial-types-logic-v1','scope':SCOPE,'semantic_status':'candidate','source_fidelity':'pending','logic_features':['first-order','equality'],'declarations':declarations(),'clauses':clauses,'depends_on':deps,'relations':[],'assumptions':[],'populations':populations}
 findings=[{'finding_id':'INTENT-FINDING-'+str(i+1).zfill(3),'description':loss,'selectors':['/voices/scientific_formal/normative_statement','/voices/scientific_formal/formal_expression','/scope/applicability'],'status':'unresolved','owner_route':'role:definition-owner with coordination, normalization, attribution, source, revision, traceability, artifact, decision and authority owners'} for i,loss in enumerate(LOSSES)]
 packet={'schema_version':'definition-assurance-correspondence/v1-candidate','upstream_schema_sha256':r.digest((IMPL/'schemas/input-envelope.json').read_bytes()),'authority_effect':'none','source_selection':'current','inventory_policy':'all-nonempty-string-leaves-in-voices-boundaries-scope-and-claim-ceiling/v1','interpretation':core,'source_units':units,'correspondence':links,'dependency_links':[{'clause_id':primary,'dependency_ref':dep,'kind':'semantic-use','rationale':'Separately qualified dependency; no accepted common carrier or whole prior theory imported.'} for dep in deps],'dependency_closure':{'status':'unresolved','review_ref':None,'unresolved_notes':LOSSES},'assumption_links':[],'source_precedence':{'normative_voice':'/voices/scientific_formal','conflicts':findings,'review_ref':None},'review_packet':{'instances':[{'case_id':'canonical-and-discovery-intents-with-traceable-hypotheses','scenario':'Eight selected Intent references cover four orientation modes, canonical and noncanonical records, code and deferred outputs, changes with recorded reasons and claims to artifact, decision, residue and next-route targets.','expected_interpretation':'Necessary nominations hold without actual attribution authenticity, explained revision, trace validity, satisfaction or authority inferred.','rationale':'Nonvacuous coverage distinguishes original orientation, output hypothesis, revised state and claim.','related_clause_ids':[primary]}],'counterexamples':[{'case_id':'changed-hypothesis-without-recorded-why','scenario':'A selected change nominates a different desired output and a matching after record but removes the revision route explanation.','expected_interpretation':'The necessary recorded-why guard fails.','rationale':'Desired state is separate from the after reference; no in-place comparison can erase the change.','related_clause_ids':[primary]}],'known_losses':LOSSES,'review_status':'pending','review_ref':None}}
 account=co.check(packet,snap,required_dependencies=[row['version_ref'] for row in deps],required_conflicts=[row['finding_id'] for row in findings]);assert account['character_accounting_complete']
 for name,value in [('t.json',{'schema_version':'definition-assurance-input/v1-candidate','kind':'interpretation','authority_effect':'none','payload':core}),('correspondence.json',packet),('static-ir.json',ir.compile_interpretation(core,snap)),('correspondence-check.json',account)]:put(name,value)
 queries=query_specs();put('query-policy.json',{'authority_effect':'none','queries':queries,'targets_not_assumptions':True,'whole_definition_proof_claimed':False});obligations=[]
 for clause in clauses:
  if clause['disposition']=='explanatory':continue
  selector=clause['source_selector'];targets=['Intent-not-ActualSourceFidelity','Intent-not-ActualWholeProof']
  if selector in ['/voices/scientific_formal/normative_statement','/scope/applicability']:targets+=['Intent-not-ActualAttributionAuthenticity','Intent-not-ActualRoutingSuitability','Intent-not-ActualRevisability','Intent-not-ActualTraceability','Intent-not-ActualNormalizedIdentityFidelity','Intent-not-ActualSourceRelationFidelity','Claim-not-ActualSatisfaction','Claim-not-ActualTargetResolution']
  if selector=='/voices/scientific_formal/formal_expression':targets+=['Intent-not-ActualPurposeResolution','Intent-not-ActualScopeResolution','Intent-not-ActualConstraintEnforcement','Intent-not-ActualHypothesisSuitability','Change-not-ActualHypothesisChangeAuthenticity','Change-not-ActualExplanationRecorded','Change-not-ActualExplanationAdequacy','Change-not-ActualRevisionAuthenticity','Change-not-ActualIntentContinuity']
  if selector.startswith('/boundaries/') or selector.startswith('/scope/exclusions/') or '/boundary_conditions/' in selector:targets+=['Intent-not-ActualMutationAuthority','Intent-not-ActualScopeApproval','Intent-not-ActualFulfillment','Intent-not-ActualArtifactAdmission','Claim-not-ActualOwnerAcceptance']
  if selector.endswith('/testable_conditions/0'):targets+=['Intent-not-ActualClassificationFidelity','Intent-not-ActualNormalizedIdentityFidelity']
  if selector.endswith('/testable_conditions/1'):targets+=['Intent-not-ActualSourceAuthenticity','Intent-not-ActualSourceRelationFidelity']
  if selector.endswith('/testable_conditions/2') or selector.endswith('/testable_conditions/3'):targets+=['Intent-not-ActualClassificationFidelity','Intent-not-ActualClaimSupport']
  if selector=='/claim_ceiling':targets+=['Intent-not-ActualArtifactAdmission','Intent-not-ActualMutationAuthority','Intent-not-ActualPublication','Intent-not-ActualRelease','Intent-not-ActualDeployment','Intent-not-ActualExternalEffect']
  link=next(row for row in links if row['clause_id']==clause['clause_id'])
  for target in targets:
   assert target in {row['query_id'] for row in queries};obligations.append({'source':source,'selector':selector,'start_character':clause['start_character'],'end_character':link['end_character'],'excerpt':link['excerpt'],'excerpt_sha256':clause['excerpt_sha256'],'clause_id':clause['clause_id'],'query_id':target,'selected_in_T':False,'necessary_declaration_guard_in_T':clause['disposition']=='encoded','actual_outcome_target_in_T':False})
 put('source-query-obligation.json',{'authority_effect':'none','obligations':obligations,'source_fidelity':'pending','whole_definition_proof_claimed':False})
 counts={'source_units':len(units),'mapped_clauses':len(clauses),**{name+'_clauses':sum(row['disposition']==name for row in clauses) for name in ['encoded','explanatory','deferred']},'declarations':len(core['declarations']),'required_populations':len(req),'unresolved_populations':len(SIGNATURE),'direct_semantic_uses':len(deps),'countermodel_queries':len(queries)};put('denominator.json',counts)
 put('clause-analysis.json',{'authority_effect':'none','source':source,'encoded_spans':counts['encoded_clauses'],'unique_encoded_source_formula_values':len({json.dumps(row['formal_statement'],sort_keys=True) for row in clauses if row['disposition']=='encoded'}),'primitive_theory_formulas':len(THEORY),'known_losses':LOSSES,'actual_outcome_queries_assumed_in_T':False,'whole_prior_theories_imported':False,'source_precedence_reviewed':False,'mechanized_proof':False,'canonical_classification_conditional':True,'work_scope_not_owner_scope':True,'desired_hypothesis_independent_from_after':True,'multiple_reasons_allowed':True,'no_existing_claim_required':True,'deferred_output_allowed':True,'automatic_fulfillment_or_mutation_permission':False,'universal_successor_identity_policy_added':False})
 put('comparison-selection.json',{'authority_effect':'none','separate_qualified_sources':deps,'selected_refs':[{'path':row['path'],'sha256':row['sha256']} for row in deps]+context['sources'],'comparison_assembled_into_primary_T':False,'source_precedence_reviewed':False,'external_context_refs':context['external_sources'],'normalization_context':context['normalization_context'],'source_fidelity':'pending','claim_ceiling':'Necessary classification, seven-coordinate nomination, explained output revision and explicit claim trace guards only; actual outcomes, source fidelity, accepted maps and whole proof remain pending.'})
 c.validate(json.loads((UNIT/'t.json').read_bytes()),'interpretation');unchanged(context['sources']);external_current(context);print(json.dumps(counts,indent=2,sort_keys=True))
if __name__=='__main__':main()
