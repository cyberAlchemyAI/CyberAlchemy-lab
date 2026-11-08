"""Source-bound Artifact Type contract, semantic bindings and distinct identities."""
import hashlib,json,sys
from pathlib import Path
UNIT=Path(__file__).resolve().parent;ROOT=UNIT.parents[6];BASE=UNIT.parents[1]
IMPL=ROOT/'craft/formalization/candidates/definition-assurance-v1';sys.path[:0]=[str(IMPL),str(BASE/'units/A04')]
import contracts as c
import ir
import resolver as r
import correspondence as co
SCOPE='scope:candidate:artifact-type-contract-v1'
SORTS=['Contract','ArtifactKind','DefinitionRef','MachineSchema','Direction','ProjectionContract','ValidationContract','OwnerRoute','LifecyclePosture','ClaimCeiling','VersionLabel','Identity','Instance']
FUNCTIONS={'contractIdentity':(['Contract'],'Identity'),'versionLabel':(['Contract'],'VersionLabel'),'artifactKind':(['Contract'],'ArtifactKind'),
 'machineSchema':(['Contract'],'MachineSchema'),'canonicalDirection':(['Contract'],'Direction'),'projectionContract':(['Contract'],'ProjectionContract'),
 'validationContract':(['Contract'],'ValidationContract'),'ownerRoute':(['Contract'],'OwnerRoute'),'lifecyclePosture':(['Contract'],'LifecyclePosture'),
 'claimCeiling':(['Contract'],'ClaimCeiling'),'instanceIdentity':(['Instance'],'Identity')}
REQUIRED=['ArtifactType','VersionedContract','OneArtifactKind']
ROLES=['ArtifactInstanceRole','SubjectDefinitionRole','SchemaAloneRole','AdmissionDecisionRole','ValidatorExecutionRole','AuthorityGrantRole']
OUTCOMES=['Registered','AdmittedType','AuthorityEffect','DefinesSubjectMeaning','ValidationPassed','ConformanceEstablished','RuntimeActive','SelfDescribed']
SIGNATURE={n:['Contract'] for n in REQUIRED+ROLES+OUTCOMES+['ValidNewRegistration']}
COMPONENTS={'ClosedSchema':('MachineSchema','machineSchema'),'PinnedSchema':('MachineSchema','machineSchema'),
 'ExplicitCanonicalDirection':('Direction','canonicalDirection'),'DeterministicProjection':('ProjectionContract','projectionContract'),
 'DeclaredValidationRules':('ValidationContract','validationContract'),'DeclaredOwnerRoute':('OwnerRoute','ownerRoute'),
 'DeclaredLifecyclePosture':('LifecyclePosture','lifecyclePosture'),'DeclaredClaimCeiling':('ClaimCeiling','claimCeiling')}
SIGNATURE.update({n:[sort] for n,(sort,_) in COMPONENTS.items()})
SIGNATURE.update(ResolvableDefinition=['DefinitionRef'],AdmittedDefinition=['DefinitionRef'],ArtifactInstance=['Instance'],
 BindsDefinition=['Contract','DefinitionRef'],BindsKind=['Contract','ArtifactKind'])
def var(n):return {'op':'var','name':n}
def pred(n,*args):return {'op':'pred','name':n,'args':[var(x) if isinstance(x,str) else x for x in args]}
def fn(n,*args):return {'op':'fn','name':n,'args':[var(x) if isinstance(x,str) else x for x in args]}
def both(*args):return {'op':'and','args':list(args)}
def neg(a):return {'op':'not','arg':a}
def implies(a,z):return {'op':'implies','left':a,'right':z}
def eq(a,z):return {'op':'eq','left':a,'right':z}
def quant(op,sort,name,body):return {'op':op,'sort':sort,'var':name,'body':body}
def every(body):return quant('forall','Contract','t',body)
def witness(body):return quant('exists','Contract','t',body)
AT=pred('ArtifactType','t')
CORE=every(implies(AT,both(pred('VersionedContract','t'),pred('OneArtifactKind','t'),pred('BindsKind','t',fn('artifactKind','t')))))
KIND_UNIQUE=every(quant('forall','ArtifactKind','k',implies(both(AT,pred('BindsKind','t','k')),eq(var('k'),fn('artifactKind','t')))))
SEMANTIC_BINDING=every(implies(AT,quant('exists','DefinitionRef','d',pred('BindsDefinition','t','d'))))
COMPONENT_CONTRACT=every(implies(AT,both(*[pred(n,fn(function,'t')) for n,(_,function) in COMPONENTS.items()])))
REGISTRATION=every(implies(pred('ValidNewRegistration','t'),quant('exists','DefinitionRef','d',both(pred('BindsDefinition','t','d'),pred('ResolvableDefinition','d')))))
ADMISSION_GATE=every(quant('forall','DefinitionRef','d',implies(both(AT,pred('AdmittedType','t'),pred('BindsDefinition','t','d')),pred('AdmittedDefinition','d'))))
IDENTITY_SEPARATION=every(quant('forall','Instance','i',implies(both(AT,pred('ArtifactInstance','i')),neg(eq(fn('contractIdentity','t'),fn('instanceIdentity','i'))))))
def contrast(n):return every(implies(AT,neg(pred(n,'t'))))
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
 source=source_ref(snap,'cal.definition.artifact-type');doc=co.source_document(snap,source);units=co.inventory(doc);texts=dict(co.string_leaves(doc))
 N='/voices/scientific_formal/normative_statement';F='/voices/scientific_formal/formal_expression'
 clauses=[];links=[]
 for u in units:
  sel=u['selector'];text=texts[sel];offsets=[0]
  if sel==N:offsets += [text.index('T binds'),text.index('Registration of T')]
  elif sel==F:offsets += [text.index('; ')+2,text.rindex('; ')+2]
  offsets.append(len(text))
  if offsets!=sorted(set(offsets)):raise ValueError('Unordered span split')
  for start,end in zip(offsets,offsets[1:]):
   excerpt=text[start:end];formula=None;disposition='deferred';roles=['proof-obligation'];forms=['non-definitional']
   rationale='Semantic binding, representation, projection, actual lifecycle/ownership, authority and whole correspondence remain separately reviewed; no target or world-truth assumption selected.'
   if sel==N and start==0:
    formula=both(CORE,KIND_UNIQUE);rationale='One versioned contract has one selected artifact kind. Different contract versions may govern the same kind; no global kind injectivity or exact carrier embedding inferred.'
   elif sel==N and excerpt.startswith('T binds'):
    formula=both(SEMANTIC_BINDING,COMPONENT_CONTRACT);rationale='At least one bound semantic Definition and named contract-component statuses are necessary. Closed/pinned/deterministic are declared semantic predicates, not proofs of arbitrary JSON closure or generator behavior.'
   elif sel==F and start==0:
    formula=COMPONENT_CONTRACT;rationale='Named total component selectors give a typed tuple view; domain elements, schema digest encoding and operational implementations need reviewed representation maps.'
   elif sel==F and excerpt.startswith('valid_new_registration') or sel=='/voices/scientific_formal/testable_conditions/0':
    formula=REGISTRATION;rationale='Every valid new registration has a resolvable bound Definition. This necessary condition is neither sufficient registration validity nor an assertion of actual registration or admission.'
   elif sel=='/voices/scientific_formal/boundary_conditions/0':
    formula=IDENTITY_SEPARATION;rationale='Common Identity carrier supports a genuine inequality between each selected type contract and each artifact instance. Private nominal sorts alone would not establish this distinction.'
   elif sel=='/voices/scientific_formal/boundary_conditions/2':
    formula=ADMISSION_GATE;rationale='Each Definition bound by an admitted Artifact Type must be admitted. Candidate bindings are permitted before Type admission; admitted Definitions alone never imply Type admission.'
   elif sel in ['/scope/exclusions/0','/boundaries/0']:formula=contrast('ArtifactInstanceRole')
   elif sel=='/scope/exclusions/1':formula=contrast('SubjectDefinitionRole')
   elif sel=='/scope/exclusions/2':formula=both(*[contrast(n) for n in ['AdmissionDecisionRole','ValidatorExecutionRole','AuthorityGrantRole']])
   elif sel=='/boundaries/1':formula=contrast('SchemaAloneRole')
   elif sel.startswith('/voices/plain_language/') or sel.startswith('/voices/domain_context/') or sel.startswith('/voices/scientific_formal/notation/'):
    disposition='explanatory';roles=['explanation-example'];forms=['non-definitional'];rationale='Intuition, exact-version notation and workspace examples retained without installing a type, granting authority or assuming the complete external meaning.'
   if formula is not None:disposition='encoded';roles=['definition'];forms=['axiomatic-implicit']
   cid='ATY-'+str(len(clauses)+1).zfill(3);clauses.append({'clause_id':cid,'source_selector':sel,'excerpt_sha256':hashlib.sha256(excerpt.encode()).hexdigest(),'start_character':start,'disposition':disposition,'forms':forms,'roles':roles,'formal_statement':formula,'rationale':rationale});links.append({'unit_id':u['unit_id'],'clause_id':cid,'end_character':end,'excerpt':excerpt})
 def clause(sel):return next(x['clause_id'] for x in clauses if x['source_selector']==sel)
 uses=[('definition',N,'Bound Definition versions supply subject meaning; this operational contract does not redefine it.'),('schema',N,'Closed machine representation and digest need exact Schema meaning and reviewed encoding.'),('artifact','/boundaries/0','Contract and instance use a shared identity distinction without merging their lifecycle.'),('validation',N,'Declared rules and validation execution/outcomes are different.'),('authority','/scope/exclusions/2','Registration, shape and projection cannot supply an authority grant.'),('identity-carrier','/voices/scientific_formal/boundary_conditions/0','Type/instance identity requires an explicit common carrier and subject binding.'),('projection-specification',N,'Canonical direction and deterministic human projection need an exact transformation contract.'),('conformance','/boundaries/2','Registration and validation do not automatically establish conformance.')]
 deps=[source_ref(snap,'cal.definition.'+id) for id,_,_ in uses];dl=[{'clause_id':clause(sel),'dependency_ref':dep,'kind':'semantic-use','rationale':why} for (_,sel,why),dep in zip(uses,deps)]
 declarations=[{'kind':'sort','symbol_id':n,'scope':SCOPE,'domain_policy':'nonempty'} for n in SORTS]+[{'kind':'total-function','symbol_id':n,'scope':SCOPE,'argument_sorts':args,'result_sort':result,'definedness_policy':None} for n,(args,result) in FUNCTIONS.items()]+[{'kind':'predicate' if len(args)==1 else 'relation','symbol_id':n,'scope':SCOPE,'argument_sorts':args} for n,args in SIGNATURE.items()]
 populations=[]
 for n,args in SIGNATURE.items():
  req=n in REQUIRED or n in COMPONENTS or n=='BindsDefinition';body=pred(n,'t') if n in REQUIRED else pred(n,fn(COMPONENTS[n][1],'t')) if n in COMPONENTS else quant('exists','DefinitionRef','d',pred(n,'t','d')) if n=='BindsDefinition' else None
  populations.append({'population_id':'POP-'+n,'carrier':'Contract','predicate_ref':n if args==['Contract'] else None,'requirement':'required' if req else 'unresolved','statement':witness(both(AT,body)) if req else None,'scope':SCOPE,'rationale':'A hypothetical Artifact Type with its required contract components prevents vacuity.' if req else 'Actual registration, admission, instance, reference, role and outcome populations need owner-reviewed existence/exemption; no default world witness.','review_ref':None})
 core={'interpretation_id':'interpretation:artifact-type-contract-v1','source':source,'scope':SCOPE,'declarations':declarations,'clauses':clauses,'depends_on':deps,'relations':[],'assumptions':[],'populations':populations,'logic_features':['first-order','equality'],'semantic_status':'candidate','source_fidelity':'pending','profile_ref':'profile:artifact-type-closed-registration-candidate'}
 descriptions=[('ATY-MEANING-001','Exact Definition reference resolution and subject meaning are not supplied by the Type schema.'),('ATY-COMPONENT-002','Component selectors/statuses require reviewed JSON/carrier embedding; pinned digest and deterministic tags are not unbounded behavior proofs.'),('ATY-IDENTITY-003','Shared local Identity inequalities are meaningful in this slice; canonical identity/carrier mappings and related subject scopes need review.'),('ATY-REGISTRATION-004','New-registration necessary condition does not retrofit admitted v1; valid registration, declaration, schema validity, admission and activation need separate policies.'),('ATY-ADMISSION-005','Source historical candidate wording, immutable descriptor posture and current registry decision overlays remain separate; no interpretation fidelity from source admission.'),('ATY-CLOSURE-006','Eight authored dependencies require independent completeness, carrier alignment and cycle interpretation; no whole theory or self-application proof.')]
 findings=[{'finding_id':id,'selectors':[N,F],'description':text,'status':'unresolved','owner_route':'role:definition-owner with artifact-type/schema/projection/identity/governance owners must review exact semantics.'} for id,text in descriptions]
 encoded=[x['clause_id'] for x in clauses if x['disposition']=='encoded']
 packet={'schema_version':'definition-assurance-correspondence/v1-candidate','authority_effect':'none','upstream_schema_sha256':r.digest((IMPL/'schemas/input-envelope.json').read_bytes()),'source_selection':'current','inventory_policy':'all-nonempty-string-leaves-in-voices-boundaries-scope-and-claim-ceiling/v1','interpretation':core,'source_units':units,'correspondence':links,'dependency_links':dl,'dependency_closure':{'status':'unresolved','review_ref':None,'unresolved_notes':['Eight declared uses are not independently complete or jointly aligned.','Projection determinism, machine closure, referenced subject truth and actual registration/admission require separate evidence.']},'assumption_links':[],'source_precedence':{'normative_voice':'/voices/scientific_formal','conflicts':findings,'review_ref':None},'review_packet':{'instances':[{'case_id':'typed-contract-with-candidate-meaning','scenario':'A versioned file contract binds a resolvable candidate Definition and exact representation/projection/validation/owner/lifecycle/ceiling components.','expected_interpretation':'Candidate authoring is possible; Type admission remains false until all semantic bindings and an actual owner decision qualify.','rationale':'Representation and lifecycle are separate claims.','related_clause_ids':encoded}],'counterexamples':[{'case_id':'shape-or-registry-shortcut','scenario':'A registration passes its schema and renders a page, then a consumer treats that as admission or canonical subject meaning.','expected_interpretation':'The selected theory supplies no such entailment; targets remain outside T.','rationale':'A passing bounded check is not an authority act.','related_clause_ids':encoded}],'known_losses':['No complete subject-meaning, instance carrier or transformation embedding.','No unbounded projection determinism or universal closed-schema proof.','No owner fidelity, dependency completeness or joint semantic closure.','No actual registration, admission, conformance or runtime effect.'],'review_status':'pending','review_ref':None}}
 account=co.check(packet,snap,required_dependencies=[x['version_ref'] for x in deps],required_conflicts=[x['finding_id'] for x in findings]);assert account['character_accounting_complete']
 typed=ir.compile_interpretation(core,snap);ir.verify_ir(typed)
 queries=[]
 for n in ['Registered','AdmittedType','AuthorityEffect','DefinesSubjectMeaning','ValidationPassed','ConformanceEstablished','RuntimeActive']:
  queries.append({'query_id':'Type-not-'+n,'target':every(implies(AT,pred(n,'t'))),'witness_condition':witness(both(AT,neg(pred(n,'t')))),'selected_in_T':False})
 for premise,result in [('Registered','AdmittedType'),('ValidationPassed','ConformanceEstablished'),('SelfDescribed','AdmittedType')]:
  queries.append({'query_id':premise+'-not-'+result,'target':every(implies(pred(premise,'t'),pred(result,'t'))),'witness_condition':witness(both(pred(premise,'t'),neg(pred(result,'t')))),'selected_in_T':False,'model_case':premise})
 queries.append({'query_id':'admitted-bound-meaning-not-Type-admission','target':every(implies(both(AT,quant('forall','DefinitionRef','d',implies(pred('BindsDefinition','t','d'),pred('AdmittedDefinition','d')))),pred('AdmittedType','t'))),'witness_condition':witness(both(AT,quant('forall','DefinitionRef','d',implies(pred('BindsDefinition','t','d'),pred('AdmittedDefinition','d'))),neg(pred('AdmittedType','t')))),'selected_in_T':False,'model_case':'admitted-meanings'})
 counts={'source_units':len(units),'mapped_clauses':len(clauses),**{n+'_clauses':sum(x['disposition']==n for x in clauses) for n in ['encoded','explanatory','deferred']},'declarations':len(declarations),'required_populations':sum(x['requirement']=='required' for x in populations),'unresolved_populations':sum(x['requirement']=='unresolved' for x in populations),'direct_semantic_uses':len(deps),'countermodel_queries':len(queries)}
 for name,value in [('t.json',{'schema_version':'definition-assurance-input/v1-candidate','kind':'interpretation','authority_effect':'none','payload':core}),('correspondence.json',packet),('static-ir.json',typed),('correspondence-check.json',account),('clause-analysis.json',{'authority_effect':'none','source':source,'clauses':clauses,'findings':findings,'whole_definition_translation':'pending'}),('query-policy.json',{'authority_effect':'none','queries':queries,'selected_in_T':False}),('denominator.json',counts)]:put(name,value)
 print(json.dumps({'result':'candidate-authored-and-typed',**counts,'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
