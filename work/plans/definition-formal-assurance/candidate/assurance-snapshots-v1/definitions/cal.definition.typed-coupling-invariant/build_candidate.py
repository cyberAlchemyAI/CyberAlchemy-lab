"""Scoped reliance requires an explicit typed representation; representation grants nothing."""
import hashlib,json,sys
from pathlib import Path
UNIT=Path(__file__).resolve().parent;ROOT=UNIT.parents[6];BASE=UNIT.parents[1]
IMPL=ROOT/'craft/formalization/candidates/definition-assurance-v1';sys.path[:0]=[str(IMPL),str(BASE/'units/A04')]
import contracts as c
import ir
import resolver as r
import correspondence as co
SCOPE='scope:candidate:typed-coupling-reliance-v1'
SORTS=['Use','Object','Relation','Kind','OwnerRoute','EvidenceRef','ReviewEffect','Scope']
FUNCTIONS={'useSource':(['Use'],'Object'),'useTarget':(['Use'],'Object'),'useScope':(['Use'],'Scope'),'relationSource':(['Relation'],'Object'),'relationTarget':(['Relation'],'Object'),'relationScope':(['Relation'],'Scope'),'relationKind':(['Relation'],'Kind'),'relationOwner':(['Relation'],'OwnerRoute')}
RELIANCE=['DecisionReliesOnConstraintOrChange','ValidationReliesOnConstraintOrChange','PromotionReliesOnConstraintOrChange','ImplementationReliesOnConstraintOrChange']
REQUIRED=['TypedRelation','NamedSource','NamedTarget','ExplicitDirection','ExplicitKind','ExplicitOwner']
OUTCOMES=['ActuallyPromoted','ActuallyValidated','Admitted','AuthorityGranted','RuntimeActivated','Published']
SIGNATURE={n:['Use'] for n in RELIANCE+['ReliedCoupling','NonOrthogonal','Orthogonal']}
SIGNATURE.update({n:['Relation'] for n in REQUIRED+OUTCOMES})
SIGNATURE.update(Represents=['Use','Relation'],HasEvidence=['Relation','EvidenceRef'],HasReviewEffect=['Relation','ReviewEffect'],ValidationEffectDescription=['ReviewEffect'],PromotionEffectDescription=['ReviewEffect'],NamedKind=['Kind'])
def var(n):return {'op':'var','name':n}
def pred(n,*args):return {'op':'pred','name':n,'args':[var(x) if isinstance(x,str) else x for x in args]}
def fn(n,*args):return {'op':'fn','name':n,'args':[var(x) if isinstance(x,str) else x for x in args]}
def both(*args):return {'op':'and','args':list(args)}
def either(*args):return {'op':'or','args':list(args)}
def neg(a):return {'op':'not','arg':a}
def implies(a,z):return {'op':'implies','left':a,'right':z}
def iff(a,z):return {'op':'iff','left':a,'right':z}
def eq(a,z):return {'op':'eq','left':a,'right':z}
def quant(op,sort,name,body):return {'op':op,'sort':sort,'var':name,'body':body}
def every(body):return quant('forall','Use','u',body)
def witness(body):return quant('exists','Use','u',body)
RELIED=pred('ReliedCoupling','u')
TRIGGER=every(iff(RELIED,either(*[pred(n,'u') for n in RELIANCE])))
NONORTHOGONAL=every(implies(RELIED,pred('NonOrthogonal','u')))
SEPARATION=every(implies(pred('Orthogonal','u'),neg(pred('NonOrthogonal','u'))))
EVIDENCE=quant('exists','EvidenceRef','e',pred('HasEvidence','r','e'))
EFFECT=quant('exists','ReviewEffect','eff',both(pred('HasReviewEffect','r','eff'),either(pred('ValidationEffectDescription','eff'),pred('PromotionEffectDescription','eff'))))
VECTOR=both(*[pred(n,'r') for n in REQUIRED],pred('NamedKind',fn('relationKind','r')),EVIDENCE,EFFECT,eq(fn('useSource','u'),fn('relationSource','r')),eq(fn('useTarget','u'),fn('relationTarget','r')),eq(fn('useScope','u'),fn('relationScope','r')))
REPRESENTATION=every(implies(RELIED,quant('exists','Relation','r',both(pred('Represents','u','r'),VECTOR))))
def ref(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def put(n,value):
 with (UNIT/n).open('x') as out:json.dump(value,out,indent=2,sort_keys=True);out.write('\n')
 return ref(UNIT/n)
def snapshot():return json.loads((BASE/'current-snapshot.json').read_bytes())
def unchanged(refs):
 for x in refs:
  if ref(ROOT/x['path'])!=x:raise ValueError('Changed selected input: '+x['path'])
def external_current(context):
 for x in context['external_sources']:
  if r.digest(Path(x['absolute_path']).read_bytes())!=x['sha256']:raise ValueError('Selected external byte drift')
def source_ref(snap,id):
 row=next(x for x in snap['current_entries'] if x['definition_id']==id)
 return {k:row[k] for k in ['definition_id','version_ref','path','sha256']}
def main():
 context=json.loads((UNIT/'context.json').read_bytes());unchanged(context['sources']);external_current(context);snap=snapshot();r.verify(snap,ROOT)
 source=source_ref(snap,'cal.definition.typed-coupling-invariant');doc=co.source_document(snap,source);units=co.inventory(doc);texts=dict(co.string_leaves(doc));N='/voices/scientific_formal/normative_statement';F='/voices/scientific_formal/formal_expression';clauses=[];links=[]
 for u in units:
  sel=u['selector'];text=texts[sel];offsets=[0]
  if sel==N:offsets.append(text.index('Bound source-semantic basis:'))
  elif sel in ['/boundaries/0','/voices/scientific_formal/boundary_conditions/0']:
   offsets.append(text.index('A typed relation is also not automatic promotion;'))
  offsets.append(len(text));assert offsets==sorted(set(offsets))
  for start,end in zip(offsets,offsets[1:]):
   excerpt=text[start:end];formula=None;disposition='deferred';roles=['proof-obligation'];forms=['non-definitional'];why='Normalized historical classification/identity/carrier/owner/source-selection commitments need exact mappings and fidelity review; source admission does not prove them.'
   if sel==N and start>0:formula=both(TRIGGER,NONORTHOGONAL,REPRESENTATION);why='Selected use relies on a constraint/co-change in one of four reasoning/operation roles. Its representation must carry the exact ordered endpoints, scope and explicit typed vector. This is a scoped normative constraint, not observed compliance.'
   elif sel in ['/boundaries/0','/voices/scientific_formal/boundary_conditions/0'] and start==0:formula=both(TRIGGER,NONORTHOGONAL,SEPARATION);why='Scope is reliance on constraining/changing together, not every nearby or related idea. Orthogonal and nonorthogonal are explicit selected predicates, never missing-record defaults.'
   elif sel=='/scope/applicability':formula=REPRESENTATION;why='Maturity/promotion, schema/contract, route/authority, provenance/trust and owner-lane examples motivate exact coupling representation. The generic rule is encoded; individual semantic bridges remain dependencies and review obligations.'
   elif sel.startswith('/voices/plain_language/') or sel.startswith('/voices/domain_context/') or sel.startswith('/voices/scientific_formal/notation/'):
    disposition='explanatory';roles=['explanation-example'];why='Plain wire analogy, stable identifier and historical framework examples explain the selected candidate without creating a coupling, adopting a proof or validating the claimed history.'
   elif sel in ['/boundaries/0','/voices/scientific_formal/boundary_conditions/0'] and start>0:why='Representation is the minimum prerequisite for review, not an automatic promotion. Non-entailment is checked with targets outside the theory; actual review readiness and effect semantics remain unresolved.'
   if formula is not None:disposition='encoded';roles=['constraint'];forms=['axiomatic-implicit']
   cid='TCI-'+str(len(clauses)+1).zfill(3);clauses.append({'clause_id':cid,'source_selector':sel,'excerpt_sha256':hashlib.sha256(excerpt.encode()).hexdigest(),'start_character':start,'disposition':disposition,'forms':forms,'roles':roles,'formal_statement':formula,'rationale':why});links.append({'unit_id':u['unit_id'],'clause_id':cid,'end_character':end,'excerpt':excerpt})
 def clause(sel):return next(x['clause_id'] for x in clauses if x['source_selector']==sel and (sel!=N or x['start_character']>0))
 uses=[('definition',N,'Exact concept identity and accepted source relations must not collapse by labels.'),('invariant',N,'Must-hold scoped constraint differs from actual compliance or proof.'),('typed-relation',N,'Representation vector, ordered endpoints and owner/evidence need reviewed carrier alignment.'),('relation-kind',N,'Named Kind and direction require a reviewed exact question/signature.'),('classification-orthogonality-invariant','/scope/applicability','Orthogonal axes and an actual coupling must be distinguished in the selected meaning.'),('validation','/boundaries/0','Validation reliance and description of validation effect are not validation results.'),('authority-promotion','/boundaries/0','Promotion reliance/effect description is not promotion authority or an actual promotion.'),('effect',N,'Review effect has validation/promotion role; neutral none and runtime effects require exact semantic policy.'),('evidence',N,'Explicit evidence metadata is not proof of a coupling or permission.'),('authority','/scope/applicability','Route/authority examples are reviewed bridges, not authority transfer.')]
 deps=[source_ref(snap,'cal.definition.'+id) for id,_,_ in uses];dl=[{'clause_id':clause(sel),'dependency_ref':dep,'kind':'semantic-use','rationale':why} for (_,sel,why),dep in zip(uses,deps)]
 declarations=[{'kind':'sort','symbol_id':n,'scope':SCOPE,'domain_policy':'nonempty'} for n in SORTS]+[{'kind':'total-function','symbol_id':n,'scope':SCOPE,'argument_sorts':args,'result_sort':res,'definedness_policy':None} for n,(args,res) in FUNCTIONS.items()]+[{'kind':'predicate' if len(args)==1 else 'relation','symbol_id':n,'scope':SCOPE,'argument_sorts':args} for n,args in SIGNATURE.items()]
 populations=[{'population_id':'POP-ReliedCoupling','carrier':'Use','predicate_ref':'ReliedCoupling','requirement':'required','statement':witness(RELIED),'scope':SCOPE,'rationale':'A hypothetical relied coupling prevents vacuous satisfaction; it asserts no live instance.','review_ref':None}]
 for n,args in SIGNATURE.items():
  if n=='ReliedCoupling':continue
  populations.append({'population_id':'POP-'+n,'carrier':args[0],'predicate_ref':n if len(args)==1 else None,'requirement':'unresolved','statement':None,'scope':SCOPE,'rationale':'Individual role/metadata/outcome populations need attributable scope and existence/exemption review; required vector follows existential representative of the relied-use witness.','review_ref':None})
 core={'interpretation_id':'interpretation:typed-coupling-reliance-v1','source':source,'scope':SCOPE,'declarations':declarations,'clauses':clauses,'depends_on':deps,'relations':[],'assumptions':[],'populations':populations,'logic_features':['first-order','equality'],'semantic_status':'candidate','source_fidelity':'pending','profile_ref':'profile:typed-coupling-explicit-review-vector-candidate'}
 descriptions=[('TCI-TRIGGER-001','Reliance, nonorthogonality and exact selected scope need review; neither adjacency nor any arbitrary relation creates a value coupling.'),('TCI-EFFECT-002','Validation or promotion effect is required source metadata; neutral none, qualifiers, containing policy and explicit top-level effect need reviewed mapping.'),('TCI-MAP-003','TypedRelation/RelationKind/Invariant and normalized type.invariant identity/owner axes require reviewed mappings; artifact kind Definition is not a live invariant.'),('TCI-DIRECTION-004','Ordered endpoints and scope embedding are exact; distinct endpoint inequality and injective relation mappings are not invented.'),('TCI-NOAUTO-005','Representing a coupling is not validation, promotion, authority, admission or execution; query targets stay outside T.'),('TCI-CLOSURE-006','Ten authored semantic dependencies do not prove completeness, shared-meaning consistency, absence of constraining cycles or source fidelity.')]
 findings=[{'finding_id':id,'selectors':[N,F],'description':text,'status':'unresolved','owner_route':'role:definition-owner with invariant/typed-relation/relation-kind/effect/validation/promotion owners'} for id,text in descriptions];encoded=[x['clause_id'] for x in clauses if x['disposition']=='encoded']
 packet={'schema_version':'definition-assurance-correspondence/v1-candidate','authority_effect':'none','upstream_schema_sha256':r.digest((IMPL/'schemas/input-envelope.json').read_bytes()),'source_selection':'current','inventory_policy':'all-nonempty-string-leaves-in-voices-boundaries-scope-and-claim-ceiling/v1','interpretation':core,'source_units':units,'correspondence':links,'dependency_links':dl,'dependency_closure':{'status':'unresolved','review_ref':None,'unresolved_notes':['Ten authored dependencies lack independently complete denominator and shared meaning.','Effect/scope vector may be distributed across relation payload, qualifiers and governance policies; exact embedding pending.']},'assumption_links':[],'source_precedence':{'normative_voice':'/voices/scientific_formal','conflicts':findings,'review_ref':None},'review_packet':{'instances':[{'case_id':'schema-constrains-promotion-decision','scenario':'A promotion decision relies on one schema constraining an artifact contract.','expected_interpretation':'One explicit scoped typed relation names ordered endpoints, Kind, owner, evidence and validation/promotion review effect; it does not itself promote anything.','rationale':'Reliance triggers representation, not outcome.','related_clause_ids':encoded}],'counterexamples':[{'case_id':'prose-or-adjacency-instead-of-explicit-coupling','scenario':'A consumer relies on a remembered connection but has no exact typed representative.','expected_interpretation':'Selected constraint fails; unrelated orthogonal ideas require no new coupling.','rationale':'Missing representation is visible without forcing every related idea to couple.','related_clause_ids':encoded}],'known_losses':['No authenticated live decision reliance or proof of actual invariant compliance.','No reviewed mapping from generic review effect to current relation qualifiers or policy records.','No normalized invariant type carrier or owner/source fidelity approval.','No independently complete semantic closure or forbidden-cycle proof.'],'review_status':'pending','review_ref':None}}
 account=co.check(packet,snap,required_dependencies=[x['version_ref'] for x in deps],required_conflicts=[x['finding_id'] for x in findings])
 if not account.get('character_accounting_complete'):raise ValueError(json.dumps(account))
 typed=ir.compile_interpretation(core,snap);ir.verify_ir(typed)
 qbase=both(RELIED,pred('Represents','u','r'),VECTOR)
 queries=[{'query_id':'represented-coupling-not-'+n,'target':every(quant('forall','Relation','r',implies(qbase,pred(n,'r')))),'witness_condition':witness(quant('exists','Relation','r',both(qbase,neg(pred(n,'r'))))),'selected_in_T':False} for n in OUTCOMES]
 queries.append({'query_id':'ordinary-typed-relation-not-relied-coupling','target':quant('forall','Relation','r',implies(pred('TypedRelation','r'),quant('exists','Use','u',both(RELIED,pred('Represents','u','r'))))),'witness_condition':quant('exists','Relation','r',both(pred('TypedRelation','r'),neg(quant('exists','Use','u',both(RELIED,pred('Represents','u','r')))))),'selected_in_T':False})
 counts={'source_units':len(units),'mapped_clauses':len(clauses),**{n+'_clauses':sum(x['disposition']==n for x in clauses) for n in ['encoded','explanatory','deferred']},'declarations':len(declarations),'required_populations':sum(x['requirement']=='required' for x in populations),'unresolved_populations':sum(x['requirement']=='unresolved' for x in populations),'direct_semantic_uses':len(deps),'countermodel_queries':len(queries)}
 for name,value in [('t.json',{'schema_version':'definition-assurance-input/v1-candidate','kind':'interpretation','authority_effect':'none','payload':core}),('correspondence.json',packet),('static-ir.json',typed),('correspondence-check.json',account),('clause-analysis.json',{'authority_effect':'none','source':source,'clauses':clauses,'findings':findings,'whole_definition_translation':'pending'}),('query-policy.json',{'authority_effect':'none','queries':queries,'selected_in_T':False}),('denominator.json',counts)]:put(name,value)
 print(json.dumps({'result':'candidate-authored-and-typed',**counts,'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
