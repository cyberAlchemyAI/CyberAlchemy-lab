"""One primary carried identity; external typed references and context frames."""
import hashlib,json,sys
from pathlib import Path
UNIT=Path(__file__).resolve().parent;ROOT=UNIT.parents[6];BASE=UNIT.parents[1]
IMPL=ROOT/'craft/formalization/candidates/definition-assurance-v1';sys.path[:0]=[str(IMPL),str(BASE/'units/A04')]
import contracts as c
import ir
import resolver as r
import correspondence as co
SCOPE='scope:candidate:identity-carrier-contract-v1'
SORTS=['Carrier','Identity','DefinitionRef','OwnerRoute','LifecycleIdentity','ProvenanceRef','Link','State','AuthorityState','LocationPath']
FUNCTIONS={'carrierIdentity':(['Carrier'],'Identity'),'primarySubject':(['Carrier'],'Identity'),'subjectKindDefinition':(['Carrier'],'DefinitionRef'),
 'ownerRoute':(['Carrier'],'OwnerRoute'),'lifecycleIdentity':(['Carrier'],'LifecycleIdentity'),'linkSource':(['Link'],'Identity'),'linkTarget':(['Link'],'Identity'),
 'subjectAt':(['Carrier','State'],'Identity'),'authorityAt':(['Identity','State'],'AuthorityState'),'pathAt':(['Carrier','State'],'LocationPath'),
 'linkSourceAt':(['Link','State'],'Identity'),'linkTargetAt':(['Link','State'],'Identity')}
REQUIRED=['IdentityCarrier','CanonicalArtifact','StableSubjectIdentifier','ExplicitPrimaryIdentity','ExplicitSubjectKind','DeclaredOwnerRoute','DeclaredLifecycleIdentity']
ROLES=['SubjectDefinitionRole','DirectoryInferredIdentityRole','GraphProjectionIdentitySourceRole','RelationMembershipRole','OwnerIdentityRole','AdmissionRole']
OUTCOMES=['AdmittedCarrier','AuthorityGrant','OwnershipEstablished','SubjectCreated','RuntimeActive']
SIGNATURE={n:['Carrier'] for n in REQUIRED+ROLES+OUTCOMES}
SIGNATURE.update(ResolvableDefinition=['DefinitionRef'],IndependentIdentity=['Identity'],TypedLink=['Link'],HasProvenance=['Carrier','ProvenanceRef'],Carries=['Carrier','Identity'],Related=['Identity','Identity'],Connects=['Link','Identity','Identity'],CanonicalPresent=['Carrier','State'],ContextOnlyChange=['Carrier','State','State'],AllowedContextStep=['State','State'],ViewRemovalStep=['Carrier','State','State'],AllowedRelationStep=['Link','State','State'])
def var(n):return {'op':'var','name':n}
def pred(n,*args):return {'op':'pred','name':n,'args':[var(x) if isinstance(x,str) else x for x in args]}
def fn(n,*args):return {'op':'fn','name':n,'args':[var(x) if isinstance(x,str) else x for x in args]}
def const(n):return {'op':'const','name':n}
def both(*args):return {'op':'and','args':list(args)}
def neg(a):return {'op':'not','arg':a}
def implies(a,z):return {'op':'implies','left':a,'right':z}
def eq(a,z):return {'op':'eq','left':a,'right':z}
def quant(op,sort,name,body):return {'op':op,'sort':sort,'var':name,'body':body}
def every(body):return quant('forall','Carrier','k',body)
def witness(body):return quant('exists','Carrier','k',body)
def states(body):return quant('forall','State','s',quant('forall','State','t',body))
IC=pred('IdentityCarrier','k');PRIMARY=fn('primarySubject','k')
CORE=every(implies(IC,both(*[pred(n,'k') for n in REQUIRED[1:]],pred('Carries','k',PRIMARY),pred('IndependentIdentity',PRIMARY),pred('CanonicalPresent','k',const('initialState')),eq(fn('subjectAt','k',const('initialState')),PRIMARY))))
PRIMARY_UNIQUE=every(quant('forall','Identity','x',implies(both(IC,pred('Carries','k','x')),eq(var('x'),PRIMARY))))
COMPONENTS=every(implies(IC,both(pred('ResolvableDefinition',fn('subjectKindDefinition','k')),quant('exists','ProvenanceRef','p',pred('HasProvenance','k','p')))))
EXTERNAL_RELATIONS=every(quant('forall','Identity','y',implies(both(IC,pred('Related',PRIMARY,'y')),both(pred('IndependentIdentity','y'),quant('exists','Link','l',both(pred('TypedLink','l'),pred('Connects','l',PRIMARY,'y')))))))
LINK_BINDING=quant('forall','Link','l',implies(pred('TypedLink','l'),both(pred('Connects','l',fn('linkSource','l'),fn('linkTarget','l')),pred('IndependentIdentity',fn('linkSource','l')),pred('IndependentIdentity',fn('linkTarget','l')),eq(fn('linkSourceAt','l',const('initialState')),fn('linkSource','l')),eq(fn('linkTargetAt','l',const('initialState')),fn('linkTarget','l')))))
LINK_UNIQUE=quant('forall','Link','l',quant('forall','Identity','x',quant('forall','Identity','y',implies(both(pred('TypedLink','l'),pred('Connects','l','x','y')),both(eq(var('x'),fn('linkSource','l')),eq(var('y'),fn('linkTarget','l')))))))
CONTEXT_FRAME=every(states(implies(both(IC,pred('AllowedContextStep','s','t'),pred('ContextOnlyChange','k','s','t')),both(eq(fn('subjectAt','k','s'),fn('subjectAt','k','t')),eq(fn('authorityAt',PRIMARY,'s'),fn('authorityAt',PRIMARY,'t'))))))
VIEW_FRAME=every(states(implies(both(IC,pred('AllowedContextStep','s','t'),pred('ViewRemovalStep','k','s','t'),pred('CanonicalPresent','k','s')),both(pred('CanonicalPresent','k','t'),eq(fn('subjectAt','k','s'),fn('subjectAt','k','t'))))))
RELATION_FRAME=quant('forall','Link','l',states(implies(both(pred('TypedLink','l'),pred('AllowedRelationStep','l','s','t')),both(eq(fn('linkSourceAt','l','s'),fn('linkSourceAt','l','t')),eq(fn('linkTargetAt','l','s'),fn('linkTargetAt','l','t')),eq(fn('authorityAt',fn('linkSourceAt','l','s'),'s'),fn('authorityAt',fn('linkSourceAt','l','t'),'t')),eq(fn('authorityAt',fn('linkTargetAt','l','s'),'s'),fn('authorityAt',fn('linkTargetAt','l','t'),'t'))))))
def contrast(n):return every(implies(IC,neg(pred(n,'k'))))
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
 source=source_ref(snap,'cal.definition.identity-carrier');doc=co.source_document(snap,source);units=co.inventory(doc);texts=dict(co.string_leaves(doc))
 N='/voices/scientific_formal/normative_statement';F='/voices/scientific_formal/formal_expression';clauses=[];links=[]
 for u in units:
  sel=u['selector'];text=texts[sel];offsets=[0]
  if sel==N:offsets += [text.index('K binds'),text.index('while keeping'),text.index('Neither placement')]
  elif sel==F:offsets += [text.index('; ')+2,text.rindex('; ')+2]
  offsets.append(len(text));assert offsets==sorted(set(offsets))
  for start,end in zip(offsets,offsets[1:]):
   excerpt=text[start:end];formula=None;disposition='deferred';roles=['proof-obligation'];forms=['non-definitional']
   rationale='Exact canonical carrier/subject identity maps, semantic bindings, normative frame scope, current authority and whole fidelity require separate owner review; no target or runtime claim assumed.'
   if sel==N and start==0 or sel=='/voices/scientific_formal/boundary_conditions/0':formula=both(CORE,PRIMARY_UNIQUE)
   elif sel==N and excerpt.startswith('K binds') or sel==F and start==0:formula=both(CORE,COMPONENTS)
   elif sel=='/voices/scientific_formal/boundary_conditions/1':formula=COMPONENTS
   elif sel==N and excerpt.startswith('while keeping') or sel=='/voices/scientific_formal/testable_conditions/1':formula=both(EXTERNAL_RELATIONS,LINK_BINDING,LINK_UNIQUE);rationale='Each selected directed Related endpoint has independent identity and a separately typed Link with exact endpoint selectors; self-links remain permitted, and ordered/static maps need reviewed TypedRelation alignment.'
   elif sel==N and excerpt.startswith('Neither placement'):formula=CONTEXT_FRAME;rationale='Allowed context-only changes must preserve carried identity and subject authority; these are normative allowed-state constraints, not evidence that any live move or membership action complies.'
   elif sel=='/voices/scientific_formal/boundary_conditions/2':formula=RELATION_FRAME;rationale='Selected allowed relation changes preserve endpoint identities and authority in a shared local carrier. Authority values are uninterpreted; no actual grant, authentication or runtime trace is invented.'
   elif sel=='/voices/scientific_formal/testable_conditions/2':formula=VIEW_FRAME;rationale='Removing a declared graph/projection view through an allowed context step must preserve the existing canonical identity record and carried identity. This does not permit canonical carrier deletion or prove a live implementation.'
   elif sel in ['/scope/exclusions/0','/boundaries/0']:formula=contrast('SubjectDefinitionRole')
   elif sel=='/scope/exclusions/1':formula=both(*[contrast(n) for n in ['DirectoryInferredIdentityRole','OwnerIdentityRole','RelationMembershipRole']])
   elif sel=='/scope/exclusions/2':formula=contrast('GraphProjectionIdentitySourceRole')
   elif sel=='/boundaries/1':formula=contrast('DirectoryInferredIdentityRole')
   elif sel=='/boundaries/2':formula=both(*[contrast(n) for n in ['GraphProjectionIdentitySourceRole','RelationMembershipRole','OwnerIdentityRole','AdmissionRole']])
   elif sel=='/voices/scientific_formal/testable_conditions/0':formula=every(implies(IC,both(pred('ExplicitPrimaryIdentity','k'),pred('ExplicitSubjectKind','k'))))
   elif sel.startswith('/voices/plain_language/') or sel.startswith('/voices/domain_context/') or sel.startswith('/voices/scientific_formal/notation/'):
    disposition='explanatory';roles=['explanation-example'];forms=['non-definitional'];rationale='Subject/carrier notation, intuition and specialized Product/Project examples retained without creating subjects, relations, ownership or the complete external semantics.'
   if formula is not None:disposition='encoded';roles=['constraint'] if formula in [CONTEXT_FRAME,VIEW_FRAME,RELATION_FRAME] else ['definition'];forms=['operational'] if roles==['constraint'] else ['axiomatic-implicit']
   cid='IDC-'+str(len(clauses)+1).zfill(3);clauses.append({'clause_id':cid,'source_selector':sel,'excerpt_sha256':hashlib.sha256(excerpt.encode()).hexdigest(),'start_character':start,'disposition':disposition,'forms':forms,'roles':roles,'formal_statement':formula,'rationale':rationale});links.append({'unit_id':u['unit_id'],'clause_id':cid,'end_character':end,'excerpt':excerpt})
 def clause(sel):return next(x['clause_id'] for x in clauses if x['source_selector']==sel)
 uses=[('definition','/voices/scientific_formal/boundary_conditions/1','Subject kind resolves through exact semantic Definition meaning.'),('artifact',N,'Carrier is a canonical artifact rather than directory or generated view.'),('artifact-type',N,'Specialized carrier shape and semantic fields need an exact Artifact Type contract.'),('typed-relation','/voices/scientific_formal/testable_conditions/1','External independently identified endpoints require separately typed relation instances.'),('identity-relation',F,'Related subjects need reviewed identity relation semantics; related does not mean equal.'),('authority','/voices/scientific_formal/boundary_conditions/2','Endpoint authority preservation is distinct from a granted authority state.'),('provenance',N,'Declared provenance references require exact source/version/lineage interpretation.'),('projection-specification','/voices/scientific_formal/testable_conditions/2','Graph/view removal must not erase a canonical carried identity.')]
 deps=[source_ref(snap,'cal.definition.'+id) for id,_,_ in uses];dl=[{'clause_id':clause(sel),'dependency_ref':dep,'kind':'semantic-use','rationale':why} for (_,sel,why),dep in zip(uses,deps)]
 declarations=[{'kind':'sort','symbol_id':n,'scope':SCOPE,'domain_policy':'nonempty'} for n in SORTS]+[{'kind':'total-function','symbol_id':n,'scope':SCOPE,'argument_sorts':args,'result_sort':result,'definedness_policy':None} for n,(args,result) in FUNCTIONS.items()]+[{'kind':'constant','symbol_id':'initialState','scope':SCOPE,'result_sort':'State'}]+[{'kind':'predicate' if len(args)==1 else 'relation','symbol_id':n,'scope':SCOPE,'argument_sorts':args} for n,args in SIGNATURE.items()]
 extra={'ResolvableDefinition':pred('ResolvableDefinition',fn('subjectKindDefinition','k')),'IndependentIdentity':pred('IndependentIdentity',PRIMARY),'HasProvenance':quant('exists','ProvenanceRef','p',pred('HasProvenance','k','p')),'Carries':pred('Carries','k',PRIMARY),'CanonicalPresent':pred('CanonicalPresent','k',const('initialState'))}
 populations=[]
 for n,args in SIGNATURE.items():
  req=n in REQUIRED or n in extra;body=pred(n,'k') if n in REQUIRED else extra.get(n)
  populations.append({'population_id':'POP-'+n,'carrier':'Carrier','predicate_ref':n if args==['Carrier'] else None,'requirement':'required' if req else 'unresolved','statement':witness(both(IC,body)) if req else None,'scope':SCOPE,'rationale':'A hypothetical canonical carrier and its selected primary identity/kind/provenance prevent vacuity.' if req else 'Actual role/outcome/relation/transition populations need attributable existence or exemption; no automatic real-world witness.','review_ref':None})
 core={'interpretation_id':'interpretation:identity-carrier-contract-v1','source':source,'scope':SCOPE,'declarations':declarations,'clauses':clauses,'depends_on':deps,'relations':[],'assumptions':[],'populations':populations,'logic_features':['first-order','equality'],'semantic_status':'candidate','source_fidelity':'pending','profile_ref':'profile:identity-carrier-context-frame-candidate'}
 descriptions=[('IDC-SUBJECT-001','Unique primary identity per carrier does not establish injectivity, unique canonical carrier per subject, or separate carrier-ID/subject-ID values in actual specialized schemas.'),('IDC-RELATION-002','Related is a selected directed predicate; external Link/endpoints/authority mappings need reviewed TypedRelation and IdentityRelation alignment, including legitimate self-relations.'),('IDC-FRAME-003','Allowed context/view/relation changes and canonical presence require exact pre/post/frame scopes; finite synthetic preservation is not live compliance or unbounded trace proof.'),('IDC-COMPONENT-004','Owner/lifecycle/provenance selectors and resolvable kind must be embedded in specialized fields or external records; schema-valid fixtures do not close missing mappings.'),('IDC-ADMISSION-005','Historical source candidate/unauthored wording and selected admitted specialized contracts are distinct layers; no interpretation fidelity, subject creation or activation from source admission.'),('IDC-CLOSURE-006','Eight authored semantic uses require independent completeness and common-carrier alignment; recursive declared closure remains unresolved.')]
 findings=[{'finding_id':id,'selectors':[N,F],'description':text,'status':'unresolved','owner_route':'role:definition-owner with identity/carrier/projection/relation/authority/provenance owners must review exact maps and frame scopes.'} for id,text in descriptions];encoded=[x['clause_id'] for x in clauses if x['disposition']=='encoded']
 packet={'schema_version':'definition-assurance-correspondence/v1-candidate','authority_effect':'none','upstream_schema_sha256':r.digest((IMPL/'schemas/input-envelope.json').read_bytes()),'source_selection':'current','inventory_policy':'all-nonempty-string-leaves-in-voices-boundaries-scope-and-claim-ceiling/v1','interpretation':core,'source_units':units,'correspondence':links,'dependency_links':dl,'dependency_closure':{'status':'unresolved','review_ref':None,'unresolved_notes':['Eight declared uses lack independent completeness and meaning-aligned counterpart review.','Normative identity/authority preservation and view-removal constraints need actual carrier/transition bindings and operational evidence.']},'assumption_links':[],'source_precedence':{'normative_voice':'/voices/scientific_formal','conflicts':findings,'review_ref':None},'review_packet':{'instances':[{'case_id':'one-primary-subject-external-relation','scenario':'A canonical Product carrier names one Product identity and links to an independently identified Project; a graph view can be removed without removing the canonical Product record.','expected_interpretation':'Primary identity remains one and independent; typed external endpoint and declared context frames remain explicit.','rationale':'Relation membership and projection are not canonical identity sources.','related_clause_ids':encoded}],'counterexamples':[{'case_id':'shared-folder-or-owner-collapse','scenario':'Two carriers share a folder, label or owner and a consumer merges their subjects or deletes the canonical identity with its graph view.','expected_interpretation':'Shared context does not entail identity equality; allowed view removal must preserve an existing canonical record.','rationale':'Context and canonical subject identity carry different obligations.','related_clause_ids':encoded}],'known_losses':['No canonical carrier/subject ID injectivity or selected real-field embedding.','No unbounded preservation/trace proof or actual relation/authority behavior.','No authenticated owner/lifecycle/provenance or operational activation.','No source-owner fidelity or jointly aligned dependency theory.'],'review_status':'pending','review_ref':None}}
 account=co.check(packet,snap,required_dependencies=[x['version_ref'] for x in deps],required_conflicts=[x['finding_id'] for x in findings]);
 if not account.get('character_accounting_complete'):raise ValueError(json.dumps(account))
 typed=ir.compile_interpretation(core,snap);ir.verify_ir(typed)
 queries=[{'query_id':'Carrier-not-'+n,'target':every(implies(IC,pred(n,'k'))),'witness_condition':witness(both(IC,neg(pred(n,'k')))),'selected_in_T':False} for n in OUTCOMES]
 queries.append({'query_id':'related-does-not-merge-primary-and-target','target':every(quant('forall','Identity','y',implies(both(IC,pred('Related',PRIMARY,'y')),eq(PRIMARY,var('y'))))),'witness_condition':witness(quant('exists','Identity','y',both(pred('Related',PRIMARY,'y'),neg(eq(PRIMARY,var('y')))))),'selected_in_T':False})
 for context_name,condition in [('shared-owner',eq(fn('ownerRoute','k'),fn('ownerRoute','j'))),('shared-path',eq(fn('pathAt','k',const('initialState')),fn('pathAt','j',const('initialState'))))]:
  queries.append({'query_id':context_name+'-not-subject-identity','target':every(quant('forall','Carrier','j',implies(both(IC,pred('IdentityCarrier','j'),condition),eq(PRIMARY,fn('primarySubject','j'))))),'witness_condition':witness(quant('exists','Carrier','j',both(pred('IdentityCarrier','j'),condition,neg(eq(PRIMARY,fn('primarySubject','j')))))),'selected_in_T':False,'model_case':'two-different-subjects'})
 queries.append({'query_id':'one-primary-not-one-carrier-per-subject','target':every(quant('forall','Carrier','j',implies(both(IC,pred('IdentityCarrier','j'),eq(PRIMARY,fn('primarySubject','j'))),eq(var('k'),var('j'))))),'witness_condition':witness(quant('exists','Carrier','j',both(pred('IdentityCarrier','j'),eq(PRIMARY,fn('primarySubject','j')),neg(eq(var('k'),var('j')))))),'selected_in_T':False,'model_case':'two-carriers-one-subject'})
 counts={'source_units':len(units),'mapped_clauses':len(clauses),**{n+'_clauses':sum(x['disposition']==n for x in clauses) for n in ['encoded','explanatory','deferred']},'declarations':len(declarations),'required_populations':sum(x['requirement']=='required' for x in populations),'unresolved_populations':sum(x['requirement']=='unresolved' for x in populations),'direct_semantic_uses':len(deps),'countermodel_queries':len(queries)}
 for name,value in [('t.json',{'schema_version':'definition-assurance-input/v1-candidate','kind':'interpretation','authority_effect':'none','payload':core}),('correspondence.json',packet),('static-ir.json',typed),('correspondence-check.json',account),('clause-analysis.json',{'authority_effect':'none','source':source,'clauses':clauses,'findings':findings,'whole_definition_translation':'pending'}),('query-policy.json',{'authority_effect':'none','queries':queries,'selected_in_T':False}),('denominator.json',counts)]:put(name,value)
 print(json.dumps({'result':'candidate-authored-and-typed',**counts,'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
