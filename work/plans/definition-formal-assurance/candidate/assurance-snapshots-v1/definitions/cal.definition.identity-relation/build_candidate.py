"""Explicit governed identity edge; independent endpoints and preservation frames."""
import hashlib,json,sys
from pathlib import Path
UNIT=Path(__file__).resolve().parent;ROOT=UNIT.parents[6];BASE=UNIT.parents[1]
IMPL=ROOT/'craft/formalization/candidates/definition-assurance-v1';sys.path[:0]=[str(IMPL),str(BASE/'units/A04')]
import contracts as c
import ir
import resolver as r
import correspondence as co
SCOPE='scope:candidate:identity-relation-contract-v1'
SORTS=['Relation','Identity','Kind','OwnerRoute','EvidenceRef','Lifecycle','State','AuthorityState','Label','Location']
FUNCTIONS={'relationIdentity':(['Relation'],'Identity'),'sourceEndpoint':(['Relation'],'Identity'),'targetEndpoint':(['Relation'],'Identity'),'relationKind':(['Relation'],'Kind'),'ownerRoute':(['Relation'],'OwnerRoute'),'lifecycle':(['Relation'],'Lifecycle'),'sourceAt':(['Relation','State'],'Identity'),'targetAt':(['Relation','State'],'Identity'),'authorityAt':(['Identity','State'],'AuthorityState'),'endpointOwner':(['Identity'],'OwnerRoute'),'endpointPath':(['Identity'],'Location')}
REQUIRED=['IdentityRelation','SeparatelyGoverned','TypedEdge','ExplicitRelationIdentity','ExplicitKind','ExplicitEndpoints','DeclaredOwner','DeclaredLifecycle']
ROLES=['EndpointIdentityRole','AuthorityTransferRole','EqualityRole','ContextInferenceRole','CanonicalAxisRole']
OUTCOMES=['AdmittedRelation','AuthorityGranted','EndpointAdmitted','RuntimeActive','BoundedContextEstablished']
SIGNATURE={n:['Relation'] for n in REQUIRED+ROLES+OUTCOMES}
SIGNATURE.update(ResolvableIdentity=['Identity'],IndependentIdentity=['Identity'],DeclaredInterpretation=['Kind'],DeclaredDirection=['Kind'],GeneratedProjection=['Label'],CanonicalAxis=['Label'],HasEvidence=['Relation','EvidenceRef'],RelationPresent=['Relation','State'],EndpointPresent=['Identity','State'],AllowedRelationStep=['Relation','State','State'],RemovalStep=['Relation','State','State'],DerivedLabel=['Label','Relation'])
def var(n):return {'op':'var','name':n}
def pred(n,*args):return {'op':'pred','name':n,'args':[var(x) if isinstance(x,str) else x for x in args]}
def fn(n,*args):return {'op':'fn','name':n,'args':[var(x) if isinstance(x,str) else x for x in args]}
def const(n):return {'op':'const','name':n}
def both(*args):return {'op':'and','args':list(args)}
def neg(a):return {'op':'not','arg':a}
def implies(a,z):return {'op':'implies','left':a,'right':z}
def eq(a,z):return {'op':'eq','left':a,'right':z}
def quant(op,sort,name,body):return {'op':op,'sort':sort,'var':name,'body':body}
def every(body):return quant('forall','Relation','r',body)
def witness(body):return quant('exists','Relation','r',body)
def states(body):return quant('forall','State','s',quant('forall','State','t',body))
IR=pred('IdentityRelation','r');SOURCE=fn('sourceEndpoint','r');TARGET=fn('targetEndpoint','r');INITIAL=const('initialState')
CORE=every(implies(IR,both(*[pred(n,'r') for n in REQUIRED[1:]],quant('exists','EvidenceRef','e',pred('HasEvidence','r','e')),pred('RelationPresent','r',INITIAL),eq(fn('sourceAt','r',INITIAL),SOURCE),eq(fn('targetAt','r',INITIAL),TARGET))))
ENDPOINTS=every(implies(IR,both(*[pred(n,end) for n in ['ResolvableIdentity','IndependentIdentity'] for end in [SOURCE,TARGET]],pred('EndpointPresent',SOURCE,INITIAL),pred('EndpointPresent',TARGET,INITIAL))))
KIND=every(implies(IR,both(pred('DeclaredInterpretation',fn('relationKind','r')),pred('DeclaredDirection',fn('relationKind','r')))))
RELATION_ID=every(implies(IR,both(neg(eq(fn('relationIdentity','r'),SOURCE)),neg(eq(fn('relationIdentity','r'),TARGET)),neg(pred('EndpointIdentityRole','r')))))
FRAME=every(states(implies(both(IR,pred('AllowedRelationStep','r','s','t')),both(eq(fn('sourceAt','r','s'),fn('sourceAt','r','t')),eq(fn('targetAt','r','s'),fn('targetAt','r','t')),eq(fn('authorityAt',fn('sourceAt','r','s'),'s'),fn('authorityAt',fn('sourceAt','r','t'),'t')),eq(fn('authorityAt',fn('targetAt','r','s'),'s'),fn('authorityAt',fn('targetAt','r','t'),'t'))))))
REMOVAL=every(states(implies(both(IR,pred('AllowedRelationStep','r','s','t'),pred('RemovalStep','r','s','t'),pred('EndpointPresent',fn('sourceAt','r','s'),'s'),pred('EndpointPresent',fn('targetAt','r','s'),'s')),both(pred('EndpointPresent',fn('sourceAt','r','t'),'t'),pred('EndpointPresent',fn('targetAt','r','t'),'t')))))
LABELS=every(quant('forall','Label','label',implies(both(IR,pred('DerivedLabel','label','r')),both(pred('GeneratedProjection','label'),neg(pred('CanonicalAxis','label'))))))
def contrast(n):return every(implies(IR,neg(pred(n,'r'))))
def ref(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def put(n,value):
 with (UNIT/n).open('x') as out:json.dump(value,out,indent=2,sort_keys=True);out.write('\n')
 return ref(UNIT/n)
def snapshot():return json.loads((BASE/'current-snapshot.json').read_bytes())
def unchanged(refs):
 for x in refs:
  if ref(ROOT/x['path'])!=x:raise ValueError('Changed selected input: '+x['path'])
def source_ref(snap,id):
 row=next(x for x in snap['current_entries'] if x['definition_id']==id)
 return {k:row[k] for k in ['definition_id','version_ref','path','sha256']}
def main():
 context=json.loads((UNIT/'context.json').read_bytes());unchanged(context['sources']);snap=snapshot();r.verify(snap,ROOT)
 source=source_ref(snap,'cal.definition.identity-relation');doc=co.source_document(snap,source);units=co.inventory(doc);texts=dict(co.string_leaves(doc));N='/voices/scientific_formal/normative_statement';F='/voices/scientific_formal/formal_expression';clauses=[];links=[]
 for u in units:
  sel=u['selector'];text=texts[sel];offsets=[0]
  if sel==N:offsets += [text.index('It preserves'),text.index('and dependent')]
  elif sel==F:offsets += [text.index('; ')+2]
  offsets.append(len(text));assert offsets==sorted(set(offsets))
  for start,end in zip(offsets,offsets[1:]):
   excerpt=text[start:end];formula=None;disposition='deferred';roles=['proof-obligation'];forms=['non-definitional'];rationale='Exact edge/endpoint/kind/owner/evidence/lifecycle representation and shared meanings remain reviewed obligations; no world relation, authority, classification or target is assumed.'
   if sel==N and start==0 or sel==F and start==0 or sel=='/voices/scientific_formal/testable_conditions/0':formula=CORE
   elif sel==N and excerpt.startswith('It preserves'):formula=FRAME;rationale='Allowed relation transitions preserve selected endpoint identities and authority states; normative constraint is not live operational compliance or an authority grant.'
   elif sel=='/voices/scientific_formal/boundary_conditions/0':formula=ENDPOINTS
   elif sel=='/voices/scientific_formal/boundary_conditions/1':formula=KIND
   elif sel=='/voices/scientific_formal/testable_conditions/1':formula=REMOVAL;rationale='A selected allowed removal starting with independently present endpoints preserves their presence; no canonical deletion or runtime operation is performed.'
   elif sel=='/boundaries/0':formula=RELATION_ID;rationale='Candidate common Identity carrier distinguishes the edge identity from both endpoint identities. Exact namespaces and stronger literal string policy need owner embedding review; it does not require source!=target.'
   elif sel=='/boundaries/1' or sel=='/scope/exclusions/1':formula=both(*[contrast(n) for n in ROLES[1:]])
   elif sel in ['/scope/exclusions/0','/voices/scientific_formal/boundary_conditions/2']:formula=contrast('ContextInferenceRole')
   elif sel=='/boundaries/2':formula=LABELS;rationale='Convenience labels derived from a selected relation are generated projections, not canonical classification axes; actual projection derivation and classification meaning remain reviewed.'
   elif sel.startswith('/voices/plain_language/') or sel.startswith('/voices/domain_context/') or sel.startswith('/voices/scientific_formal/notation/'):
    disposition='explanatory';roles=['explanation-example'];forms=['non-definitional'];rationale='Intuition, directed-edge notation and legacy Craft graph examples retained without inferring actual edges, admitted vocabulary, endpoint equality or shared authority.'
   if formula is not None:disposition='encoded';roles=['constraint'] if formula in [FRAME,REMOVAL] else ['definition'];forms=['operational'] if roles==['constraint'] else ['axiomatic-implicit']
   cid='IDR-'+str(len(clauses)+1).zfill(3);clauses.append({'clause_id':cid,'source_selector':sel,'excerpt_sha256':hashlib.sha256(excerpt.encode()).hexdigest(),'start_character':start,'disposition':disposition,'forms':forms,'roles':roles,'formal_statement':formula,'rationale':rationale});links.append({'unit_id':u['unit_id'],'clause_id':cid,'end_character':end,'excerpt':excerpt})
 def clause(sel):return next(x['clause_id'] for x in clauses if x['source_selector']==sel)
 uses=[('definition',N,'Meaning belongs to an exact semantic source, not a convenience label.'),('governed-model',N,'Separately governed edge/owner/evidence/lifecycle require reviewed shared governance meanings.'),('typed-relation',N,'Typed edge contract and exact endpoint metadata need common-carrier alignment, not a presumed alias.'),('relation-kind','/voices/scientific_formal/boundary_conditions/1','Kind interpretation and ordered direction require a selected semantic contract.'),('identity-carrier','/voices/scientific_formal/boundary_conditions/0','Both endpoints resolve independently through canonical identities.'),('authority',F,'Endpoint authority need not be equal and cannot transfer through membership.'),('evidence',N,'Explicit edge evidence does not prove validity or admission by itself.'),('projection-specification','/boundaries/2','Derived convenience/reverse labels remain generated views rather than canonical axes.')]
 deps=[source_ref(snap,'cal.definition.'+id) for id,_,_ in uses];dl=[{'clause_id':clause(sel),'dependency_ref':dep,'kind':'semantic-use','rationale':why} for (_,sel,why),dep in zip(uses,deps)]
 declarations=[{'kind':'sort','symbol_id':n,'scope':SCOPE,'domain_policy':'nonempty'} for n in SORTS]+[{'kind':'total-function','symbol_id':n,'scope':SCOPE,'argument_sorts':args,'result_sort':result,'definedness_policy':None} for n,(args,result) in FUNCTIONS.items()]+[{'kind':'constant','symbol_id':'initialState','scope':SCOPE,'result_sort':'State'}]+[{'kind':'predicate' if len(args)==1 else 'relation','symbol_id':n,'scope':SCOPE,'argument_sorts':args} for n,args in SIGNATURE.items()]
 extra={'HasEvidence':quant('exists','EvidenceRef','e',pred('HasEvidence','r','e')),'ResolvableIdentity':both(pred('ResolvableIdentity',SOURCE),pred('ResolvableIdentity',TARGET)),'IndependentIdentity':both(pred('IndependentIdentity',SOURCE),pred('IndependentIdentity',TARGET)),'DeclaredInterpretation':pred('DeclaredInterpretation',fn('relationKind','r')),'DeclaredDirection':pred('DeclaredDirection',fn('relationKind','r')),'RelationPresent':pred('RelationPresent','r',INITIAL),'EndpointPresent':both(pred('EndpointPresent',SOURCE,INITIAL),pred('EndpointPresent',TARGET,INITIAL))};populations=[]
 for n,args in SIGNATURE.items():
  req=n in REQUIRED or n in extra;body=pred(n,'r') if n in REQUIRED else extra.get(n)
  populations.append({'population_id':'POP-'+n,'carrier':'Relation','predicate_ref':n if args==['Relation'] else None,'requirement':'required' if req else 'unresolved','statement':witness(both(IR,body)) if req else None,'scope':SCOPE,'rationale':'One hypothetical edge and its independently resolved components prevent vacuity.' if req else 'Actual role/outcome/transition/label populations need attributable existence or exemption; no automatic world relation or authority.','review_ref':None})
 core={'interpretation_id':'interpretation:identity-relation-contract-v1','source':source,'scope':SCOPE,'declarations':declarations,'clauses':clauses,'depends_on':deps,'relations':[],'assumptions':[],'populations':populations,'logic_features':['first-order','equality'],'semantic_status':'candidate','source_fidelity':'pending','profile_ref':'profile:identity-relation-directed-edge-candidate'}
 descriptions=[('IDR-IDENTITY-001','Separate governed edge role and common-carrier edge/endpoint inequality need exact namespace mapping; no universal source-target inequality or actual ID admission inferred.'),('IDR-AUTHORITY-002','Endpoint authority equality is not entailed; preservation constrains selected allowed states, not world authority truth or principal authentication.'),('IDR-KIND-003','Declared interpretation/direction and legacy graph kinds need exact reviewed RelationKind/pair mappings; no inverse edge from a reverse label.'),('IDR-METADATA-004','Per-edge owner/evidence/lifecycle versus graph aggregate fields need embedding review; graph schema and local semantic checks cannot fill missing maps.'),('IDR-FRAME-005','Relation removal must preserve endpoint presence with exact frame/allowed-action scope; bounded simulations do not prove live or unbounded compliance.'),('IDR-CLOSURE-006','Eight declared semantic uses, source/admission layers and shared meanings need independent review; no alias to TypedRelation or combined-theory assurance.')]
 findings=[{'finding_id':id,'selectors':[N,F],'description':text,'status':'unresolved','owner_route':'role:definition-owner with identity/relation/kind/authority/evidence/projection owners must review exact maps.'} for id,text in descriptions];encoded=[x['clause_id'] for x in clauses if x['disposition']=='encoded']
 packet={'schema_version':'definition-assurance-correspondence/v1-candidate','authority_effect':'none','upstream_schema_sha256':r.digest((IMPL/'schemas/input-envelope.json').read_bytes()),'source_selection':'current','inventory_policy':'all-nonempty-string-leaves-in-voices-boundaries-scope-and-claim-ceiling/v1','interpretation':core,'source_units':units,'correspondence':links,'dependency_links':dl,'dependency_closure':{'status':'unresolved','review_ref':None,'unresolved_notes':['Eight authored uses lack independent completeness and exact cross-definition meanings.','Legacy graph edge representation may omit per-edge metadata; canonical identity namespaces and authority/frame policies require review.']},'assumption_links':[],'source_precedence':{'normative_voice':'/voices/scientific_formal','conflicts':findings,'review_ref':None},'review_packet':{'instances':[{'case_id':'explicit-directed-edge-independent-authority','scenario':'A governed Product-to-Project edge selects an interpreted directed Kind and independent endpoints whose authority states differ.','expected_interpretation':'Endpoint identity/authority stay independent; an allowed relation removal preserves endpoint records.','rationale':'A typed relation is not equality or a grant.','related_clause_ids':encoded}],'counterexamples':[{'case_id':'shared-owner-reverse-label-shortcut','scenario':'A graph consumer invents a reverse edge from a label/shared owner, or copies authority/deletes an endpoint when removing an edge.','expected_interpretation':'Context does not create an edge; allowed changes preserve identity/authority/presence; derived labels are views.','rationale':'Relationship, representation and authority are separate obligations.','related_clause_ids':encoded}],'known_losses':['No whole alias/alignment with TypedRelation or exact admitted vocabulary.','No reviewed legacy per-edge metadata/common-identity embedding.','No actual relation/admission/authority/runtime effect.','No unbounded endpoint-preservation proof or independently complete closure.'],'review_status':'pending','review_ref':None}}
 account=co.check(packet,snap,required_dependencies=[x['version_ref'] for x in deps],required_conflicts=[x['finding_id'] for x in findings])
 if not account.get('character_accounting_complete'):raise ValueError(json.dumps(account))
 typed=ir.compile_interpretation(core,snap);ir.verify_ir(typed)
 queries=[{'query_id':'Relation-not-'+n,'target':every(implies(IR,pred(n,'r'))),'witness_condition':witness(both(IR,neg(pred(n,'r')))),'selected_in_T':False} for n in OUTCOMES]
 for name,equality in [('endpoint-identity',eq(SOURCE,TARGET)),('endpoint-authority',eq(fn('authorityAt',SOURCE,INITIAL),fn('authorityAt',TARGET,INITIAL)))]:queries.append({'query_id':'relation-not-'+name+'-equality','target':every(implies(IR,equality)),'witness_condition':witness(both(IR,neg(equality))),'selected_in_T':False})
 for name,function in [('shared-owner','endpointOwner'),('shared-path','endpointPath')]:
  context_eq=eq(fn(function,'a'),fn(function,'z'));connected=quant('exists','Relation','r',both(IR,eq(SOURCE,var('a')),eq(TARGET,var('z'))));eligible=both(pred('ResolvableIdentity','a'),pred('ResolvableIdentity','z'),context_eq)
  queries.append({'query_id':name+'-not-inferred-directed-edge','target':quant('forall','Identity','a',quant('forall','Identity','z',implies(eligible,connected))),'witness_condition':quant('exists','Identity','a',quant('exists','Identity','z',both(eligible,neg(connected)))),'selected_in_T':False})
 counts={'source_units':len(units),'mapped_clauses':len(clauses),**{n+'_clauses':sum(x['disposition']==n for x in clauses) for n in ['encoded','explanatory','deferred']},'declarations':len(declarations),'required_populations':sum(x['requirement']=='required' for x in populations),'unresolved_populations':sum(x['requirement']=='unresolved' for x in populations),'direct_semantic_uses':len(deps),'countermodel_queries':len(queries)}
 for name,value in [('t.json',{'schema_version':'definition-assurance-input/v1-candidate','kind':'interpretation','authority_effect':'none','payload':core}),('correspondence.json',packet),('static-ir.json',typed),('correspondence-check.json',account),('clause-analysis.json',{'authority_effect':'none','source':source,'clauses':clauses,'findings':findings,'whole_definition_translation':'pending'}),('query-policy.json',{'authority_effect':'none','queries':queries,'selected_in_T':False}),('denominator.json',counts)]:put(name,value)
 print(json.dumps({'result':'candidate-authored-and-typed',**counts,'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
