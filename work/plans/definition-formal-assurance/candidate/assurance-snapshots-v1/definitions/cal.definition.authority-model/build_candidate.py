"""Authority Model context-qualified routing and movement necessities; actual approval remains separate."""
import hashlib,json,sys
from pathlib import Path
UNIT=Path(__file__).resolve().parent;ROOT=UNIT.parents[6];BASE=UNIT.parents[1]
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
 with (UNIT/n).open('x') as out:json.dump(value,out,indent=2,sort_keys=True);out.write('\n')
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
SCOPE='scope:candidate:AuthorityModel-context-qualified-routing-and-movement-necessities-v1'
SORTS=['Entity','State','Token']
FIELDS=['kind','posture','ownerRoute','allowedUse','blockedUse','gate','validationSurface','nonCollapseRules']
FUNCTIONS={n+'Value':(['Entity','Entity'],'Token') for n in FIELDS}
OUTCOMES=['Ontology','Schema','Decision','AccessControl','Proof','UniversalConstitution','PromotionLicense','ActualAuthority','ActualApproval','TruthEstablished','ActualRuntimeEffect']
SIGNATURE={n:['Entity'] for n in ['AuthorityModel','GovernedStructure','Candidate','Movement','AuthoritySurface','NamesPostures','NamesGates','NamesLayerBoundaries','AdmissibleMovement','CrossesEvidenceOrModelToLocalAuthority','RequiresPromotionGate','GatePerformed','PositiveVerdict','ActualPromotion',*OUTCOMES]}
SIGNATURE.update(MappedCandidate=['Entity','Entity'],Coordinates=['Entity','Entity'],DeclaredPromotionKind=['Entity','Token'],OwnsPromotionRoute=['Entity','Token','Token'],MovementContext=['Entity','Entity','Entity'],RecordedGateVerdict=['Entity','Token','Token'],AllowedUseCovers=['Entity','Token'])
EMPTY=const('EMPTY');MODEL=pred('AuthorityModel','m');MAPPED=pred('MappedCandidate','m','x')
ROUTING=allof([('Entity','m')],implies(MODEL,both(pred('GovernedStructure','m'),allof([('Entity','x')],implies(MAPPED,both(pred('Candidate','x'),*[neg(eq(fn(n+'Value','m','x'),EMPTY)) for n in FIELDS]))))))
NAMING=allof([('Entity','m')],implies(MODEL,both(exists([('Entity','s')],both(pred('AuthoritySurface','s'),pred('Coordinates','m','s'))),pred('NamesPostures','m'),pred('NamesGates','m'),pred('NamesLayerBoundaries','m'),allof([('Token','k')],implies(pred('DeclaredPromotionKind','m','k'),exists([('Token','r')],both(neg(eq(var('r'),EMPTY)),pred('OwnsPromotionRoute','m','k','r'))))))))
# Guard ordering changes evaluation cost without narrowing selected model domains.
def movement_rule(conclusion,extra=None):
 return allof([('Entity','m')],implies(MODEL,allof([('Entity','x')],implies(MAPPED,allof([('Entity','v')],implies(both(pred('MovementContext','m','x','v'),*([] if extra is None else [extra])),conclusion))))))
NECESSITY=movement_rule(implies(pred('AdmissibleMovement','v'),both(pred('RecordedGateVerdict','v',fn('ownerRouteValue','m','x'),fn('gateValue','m','x')),pred('AllowedUseCovers','v',fn('allowedUseValue','m','x')))))
PROMOTION=movement_rule(pred('RequiresPromotionGate','v'),pred('CrossesEvidenceOrModelToLocalAuthority','v'))
THEORY=[ROUTING,NAMING,NECESSITY,PROMOTION]
def main():
 context=json.loads((UNIT/'context.json').read_bytes());unchanged(context['sources']);external_current(context);snap=snapshot();r.verify(snap,ROOT);source=source_ref(snap,'cal.definition.authority-model');doc=co.source_document(snap,source);units=co.inventory(doc);texts=dict(co.string_leaves(doc));N='/voices/scientific_formal/normative_statement';F='/voices/scientific_formal/formal_expression'
 selections=[(N,'An authority model is the governed structure that classifies candidate material by\nauthority kind, reliance posture, owner route, admissible movement, gate\nvocabulary, validation surface, and non-collapse rule so CyberAlchemy v2 can\ndecide what may count for which purpose',ROUTING),
 (N,'An authority model must name the authority surfaces it coordinates, the route\nthat owns each kind of promotion, the states or postures a candidate may occupy,\nthe gates that control movement between states, and the boundary conditions that\nprevent one authority layer from overriding another.',NAMING),
 (F,"Movement is admissible only when the responsible `owner_route` records a gate\nverdict and the candidate's `allowed_use` covers the intended downstream effect.",NECESSITY),
 (F,'If a candidate crosses from evidence or model into local authority, the model\nrequires a promotion gate rather than implied authority by proximity.',PROMOTION)]
 clauses=[];links=[]
 for unit in units:
  sel=unit['selector'];text=texts[sel];cuts={0,len(text)}
  for selector,excerpt,formula in selections:
   if sel==selector:start=text.index(excerpt);cuts.update([start,start+len(excerpt)])
  for start,end in zip(sorted(cuts),sorted(cuts)[1:]):
   excerpt=text[start:end];statement=None;disposition='deferred';forms=['unresolved'];roles=['unresolved'];why='Exact tuple equality, complete kind/posture/owner/use/gate/validation/noncollapse meanings, operational movement, actual owner decisions and precedence remain unresolved.'
   for selector,selected,formula in selections:
    if sel==selector and excerpt==selected:statement=formula;disposition='encoded';forms=['axiomatic-implicit'];roles=['definition'];why='Selected context-qualified classification/naming or necessary movement/promotion-gate requirement. Recorded verdict need not be positive; necessary conditions do not imply sufficient approval. Naming boundary rules does not prove they prevent overrides. No actual movement created.'
   if statement is None and (sel.startswith('/voices/plain_language/') or sel.startswith('/voices/domain_context/') or sel.startswith('/voices/scientific_formal/notation/')):disposition='explanatory';roles=['explanation-example'];why='Source intuition and referenced legacy model remain contextual; whole referenced document not imported into theory.'
   cid='AMO-'+str(len(clauses)+1).zfill(3);clauses.append({'clause_id':cid,'source_selector':sel,'excerpt_sha256':r.digest(excerpt.encode()),'start_character':start,'disposition':disposition,'forms':forms,'roles':roles,'formal_statement':statement,'rationale':why});links.append({'unit_id':unit['unit_id'],'clause_id':cid,'end_character':end,'excerpt':excerpt})
 target_id=next(x['clause_id'] for x in clauses if x['formal_statement']==ROUTING)
 uses=[('definition','Normalized scaffold and D41 source precedence require review.'),('authority','Routing descriptions and actual governing standing remain distinct.'),('authority-claim','Field completeness and claimed permissions are not approval.'),('authority-boundary','Actual owner/scope/effect constraints need separate meaning alignment.'),('authority-surface','Coordinated surfaces require explicit denotation.'),('authority-promotion','Requires a promotion gate does not mean actual promotion performed.'),('gate','Recorded verdict is not necessarily successful; gate execution distinct.'),('policy','Movement and promotion policies require owner decisions.'),('constitution','Scoped governing rules cannot be replaced by model proximity.'),('ontology','Authority modeled in ontology is not governing authority.'),('ontology-node','Graph representation does not approve movement.'),('ontology-view','Views do not replace source or owner.'),('schema','Shape validity is separate from semantic and governing acceptance.'),('evidence','Evidence does not silently become authority.'),('validation','Validation surfaces and success do not grant authority.'),('validation-receipt','Recorded validation results require independent meaning/effect maps.'),('decision','Owners make actual promotion decisions; necessary conditions are not decisions.'),('artifact-type','Current carriers are separate comparison evidence, not Model tuple instances.'),('typed-relation','Endpoint metadata does not establish semantic closure.'),('relation-kind','Catalog vocabulary cannot silently close authority kinds.'),('classification-orthogonality-invariant','Kind/posture/use/gate/validation/noncollapse axes stay distinct.'),('identity-carrier','Equal tuple fields do not identify Model or candidate entities.'),('identity-relation','Contexts do not merge identities.'),('context','Model/candidate/purpose/surface/state mappings require explicit review.'),('discipline','Recurring practice does not create semantic or governing authority.'),('research-inquiry','Research posture does not grant implementation authority.'),('governance-event-history','Actual transitions and currentness require governed history.'),('semantic-event-history','Meaning changes remain separately reviewable.'),('parent-instance-authority-separation-invariant','Parent/model authority is not automatically instance authority.'),('closed-authority-kind-invariant','Referenced legacy closed-kind table is not imported as Lab closure.')]
 deps=[source_ref(snap,'cal.definition.'+id) for id,_ in uses];dl=[{'clause_id':target_id,'dependency_ref':dep,'kind':'semantic-use','rationale':why} for (_,why),dep in zip(uses,deps)]
 declarations=[{'kind':'sort','symbol_id':n,'scope':SCOPE,'domain_policy':'nonempty'} for n in SORTS]+[{'kind':'constant','symbol_id':'EMPTY','scope':SCOPE,'result_sort':'Token'}]+[{'kind':'total-function','symbol_id':n,'scope':SCOPE,'argument_sorts':args,'result_sort':result,'definedness_policy':None} for n,(args,result) in FUNCTIONS.items()]+[{'kind':'predicate' if len(args)==1 else 'relation','symbol_id':n,'scope':SCOPE,'argument_sorts':args} for n,args in SIGNATURE.items()]
 required={'AuthorityModel':exists([('Entity','m')],MODEL),'MappedCandidate':exists([('Entity','m'),('Entity','x')],both(MODEL,MAPPED)),
 'AdmissibleMovement':exists([('Entity','v')],pred('AdmissibleMovement','v')),
 'TwoModelContextsSameCandidateDifferentOwnerRoutes':exists([('Entity','m'),('Entity','z')],both(MODEL,pred('AuthorityModel','z'),neg(eq(var('m'),var('z'))),exists([('Entity','x')],both(MAPPED,pred('MappedCandidate','z','x'),neg(eq(fn('ownerRouteValue','m','x'),fn('ownerRouteValue','z','x'))))))),
 'NamedSurface':exists([('Entity','m'),('Entity','s')],both(MODEL,pred('AuthoritySurface','s'),pred('Coordinates','m','s'))),
 'DeclaredPromotionRoute':exists([('Entity','m'),('Token','k'),('Token','r')],both(MODEL,pred('DeclaredPromotionKind','m','k'),pred('OwnsPromotionRoute','m','k','r'),neg(eq(var('r'),EMPTY)))),
 'RecordedNonpositiveVerdict':exists([('Entity','v')],both(pred('AdmissibleMovement','v'),neg(pred('PositiveVerdict','v')))),
 'RequiredPromotionGateNotPerformed':exists([('Entity','v')],both(pred('RequiresPromotionGate','v'),neg(pred('GatePerformed','v')))),
 'NecessaryConditionsNotSufficient':exists([('Entity','v')],both(pred('Movement','v'),neg(pred('AdmissibleMovement','v')),exists([('Token','r'),('Token','g'),('Token','a')],both(pred('RecordedGateVerdict','v','r','g'),pred('AllowedUseCovers','v','a'))))),
 'NoActualPromotionFromRequirement':exists([('Entity','v')],both(pred('RequiresPromotionGate','v'),neg(pred('ActualPromotion','v'))))}
 populations=[{'population_id':'POP-'+n,'carrier':'Entity','predicate_ref':n if n in SIGNATURE and len(SIGNATURE[n])==1 else None,'requirement':'required','statement':statement,'scope':SCOPE,'rationale':'Selected finite non-vacuity and implication-strength witnesses; no world existence, source fidelity, permission or actual movement implied.','review_ref':None} for n,statement in required.items()]
 for n,args in SIGNATURE.items():
  if n in required:continue
  populations.append({'population_id':'POP-'+n,'carrier':args[0],'predicate_ref':n if len(args)==1 else None,'requirement':'unresolved','statement':None,'scope':SCOPE,'rationale':'Real population, context, naming and operational denotation/exemption remain unresolved.','review_ref':None})
 core={'interpretation_id':'interpretation:AuthorityModel-context-qualified-routing-and-movement-necessities-v1','source':source,'scope':SCOPE,'declarations':declarations,'clauses':clauses,'depends_on':deps,'relations':[],'assumptions':[],'populations':populations,'logic_features':['first-order','equality'],'semantic_status':'candidate','source_fidelity':'pending','profile_ref':'profile:AuthorityModel-separate-movement-approval-and-context-candidate'}
 descriptions=[('AMO-PRECEDENCE-001','Normalized source, D41 tuple/necessity, referenced full document and source voices need reviewed precedence.'),('AMO-DENOTATION-002','Eight total context-qualified Token projections are selected maps, not accepted tuple equality or resolved real kinds/routes/sets.'),('AMO-NAMING-003','Named surfaces/postures/gates/boundaries and declared promotion kinds do not prove complete enumeration or override prevention.'),('AMO-VERDICT-004','Source requires a recorded verdict, not an explicit positive verdict; stronger acceptance stays separate.'),('AMO-SUFFICIENCY-005','Necessary verdict and allowed-use coverage do not imply movement approved or permitted.'),('AMO-PROMOTION-006','Requires promotion gate does not prove that gate ran, owners approved or local authority changed.'),('AMO-NONCOLLAPSE-007','Universal noncollapse, temporal transitions, real boundaries and source/carrier alignment remain unresolved.'),('AMO-CLOSURE-008','Thirty authored semantic uses and contextual legacy tables do not establish reviewed meaning-aligned closure.')]
 findings=[{'finding_id':id,'selectors':[N,F],'description':why,'status':'unresolved','owner_route':'role:definition-owner with authority/promotion/gate/model/carrier owners'} for id,why in descriptions]
 packet={'schema_version':'definition-assurance-correspondence/v1-candidate','authority_effect':'none','upstream_schema_sha256':r.digest((IMPL/'schemas/input-envelope.json').read_bytes()),'source_selection':'current','inventory_policy':'all-nonempty-string-leaves-in-voices-boundaries-scope-and-claim-ceiling/v1','interpretation':core,'source_units':units,'correspondence':links,'dependency_links':dl,'dependency_closure':{'status':'unresolved','review_ref':None,'unresolved_notes':['Authored dependencies and declared candidate contexts require independent complete edge and meaning review.','Actual promotion, owner decisions, noncollapse and temporal movement not encoded as automatic approval.']},'assumption_links':[],'source_precedence':{'normative_voice':'/voices/scientific_formal','conflicts':findings,'review_ref':None},'review_packet':{'instances':[{'case_id':'two-models-route-same-candidate-differently','scenario':'Same selected candidate has different owner-route Tokens under two Model Entities.','expected_interpretation':'Routing functions are context-qualified; neither model automatically approves the candidate.','rationale':'Source context and route identity need reviewed alignment.','related_clause_ids':[target_id]}],'counterexamples':[{'case_id':'recorded-verdict-or-complete-routing-proves-approval','scenario':'A recorded negative verdict or complete eight-field tuple is treated as actual approval.','expected_interpretation':'Only selected necessary conditions are enforced; independent approval and executed gate remain absent.','rationale':'Only-when and requires do not establish sufficient approval or world effect.','related_clause_ids':[target_id]}],'known_losses':[x[1] for x in descriptions],'review_status':'pending','review_ref':None}}
 account=co.check(packet,snap,required_dependencies=[x['version_ref'] for x in deps],required_conflicts=[x['finding_id'] for x in findings]);assert account['character_accounting_complete'];typed=ir.compile_interpretation(core,snap);ir.verify_ir(typed)
 queries=[]
 def query(id,bindings,guard,conclusion):queries.append({'query_id':id,'target':allof(bindings,implies(guard,conclusion)),'witness_condition':exists(bindings,both(guard,neg(conclusion))),'selected_in_T':False})
 for n in OUTCOMES:query('Model-not-'+n,[('Entity','m')],MODEL,pred(n,'m'))
 query('Admissible-not-positive-verdict',[('Entity','v')],pred('AdmissibleMovement','v'),pred('PositiveVerdict','v'))
 query('Admissible-not-actual-approval',[('Entity','v')],pred('AdmissibleMovement','v'),pred('ActualApproval','v'))
 query('Required-gate-not-performed',[('Entity','v')],pred('RequiresPromotionGate','v'),pred('GatePerformed','v'))
 query('Required-gate-not-actual-promotion',[('Entity','v')],pred('RequiresPromotionGate','v'),pred('ActualPromotion','v'))
 query('Recorded-verdict-and-coverage-not-sufficient',[('Entity','v'),('Token','r'),('Token','g'),('Token','a')],both(pred('RecordedGateVerdict','v','r','g'),pred('AllowedUseCovers','v','a')),pred('AdmissibleMovement','v'))
 query('Same-candidate-not-global-owner-route',[('Entity','m'),('Entity','z'),('Entity','x')],both(MODEL,pred('AuthorityModel','z'),MAPPED,pred('MappedCandidate','z','x')),eq(fn('ownerRouteValue','m','x'),fn('ownerRouteValue','z','x')))
 counts={'source_units':len(units),'mapped_clauses':len(clauses),**{n+'_clauses':sum(x['disposition']==n for x in clauses) for n in ['encoded','explanatory','deferred']},'declarations':len(declarations),'required_populations':len(required),'unresolved_populations':len(populations)-len(required),'direct_semantic_uses':len(deps),'countermodel_queries':len(queries)}
 for n,x in [('t.json',{'schema_version':'definition-assurance-input/v1-candidate','kind':'interpretation','authority_effect':'none','payload':core}),('correspondence.json',packet),('static-ir.json',typed),('correspondence-check.json',account),('clause-analysis.json',{'authority_effect':'none','clauses':clauses,'findings':findings,'whole_definition_translation':'pending'}),('query-policy.json',{'authority_effect':'none','queries':queries}),('denominator.json',counts)]:put(n,x)
 put('comparison-selection.json',{'authority_effect':'none','Model_source':source,'separate_qualified_sources':[source_ref(snap,'cal.definition.'+id) for id in ['authority','authority-claim','authority-boundary','authority-promotion','gate','closed-authority-kind-invariant','parent-instance-authority-separation-invariant']],'selected_refs':[ref(BASE/'definitions/cal.definition.authority-boundary'/n) for n in ['t.json','static-ir.json','REVIEW.md','delivery-manifest.json']],'external_context_refs':context['external_sources'][1:],'comparison_assembled_into_primary_T':False,'source_precedence_reviewed':False,'source_fidelity':'pending','claim_ceiling':'Separate qualified sources and full legacy Model document inspected as comparison, not admitted or merged into primary theory. Eight projections are not accepted tuple/world denotation.'})
 c.validate(json.loads((UNIT/'t.json').read_bytes()),'interpretation');unchanged(context['sources']);external_current(context);print(json.dumps(counts,indent=2,sort_keys=True))
if __name__=='__main__':main()
