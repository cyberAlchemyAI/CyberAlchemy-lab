"""Context identity, typed anchors, kind/cardinality and normative-change boundaries."""
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
SCOPE='scope:candidate:Context-durable-identity-exact-anchors-and-normative-refresh-successor-v1'
SORTS=['Entity','Field','Kind','Lifecycle','Token']
FIELDS=['id','kind','product_ref','project_ref','goal_ref','purpose','bounded_context_refs','consumer_refs','intended_uses','subject_scope','source_policy_refs','owner_route','lifecycle_state','revision_history','challenge_route']
KINDS=['PRODUCT','PROJECT','GOAL'];LIFECYCLES=['DRAFT','ACTIVE','SUPERSEDED','RETIRED']
CONSTANTS={'EMPTY':'Token','CONTEXT_ID':'Token',**{'F_'+n:'Field' for n in FIELDS},**{n:'Kind' for n in KINDS},**{n:'Lifecycle' for n in LIFECYCLES}}
FUNCTIONS={'fieldValue':(['Entity','Field'],'Token'),'normalizedIdValue':(['Entity'],'Token'),'contextKindValue':(['Entity'],'Kind'),'contextLifecycleValue':(['Entity'],'Lifecycle')}
QUALIFIERS=['Durable','IdentityBearing','OwnerQualified','RelevanceInterpretationBoundary','OneDeclaredPurpose']
ROLES=['ProductRole','ProductThesisRole','ProjectRole','GoalRole','ProjectSpaceRole','BoundedContextRole','LanguageRole','RegistryRole','SourceSelectionRole','RequestRole','ContextViewRole','SnapshotRole','ContextPackRole','SessionRole','PromptRole','EventLedgerRole','AuthorityEnvelopeRole','OwnerDecisionRole','ExecutionPermissionRole']
OUTCOMES=['ActualAuthority','ActualAdmission','TruthEstablished','ProofEstablished','SourceOwnerAccepted','RuntimeActivated','ExternalEffect','ActualPublication','ActualRelease','ActualDeployment','ResolverContractAccepted']
SIGNATURE={n:['Entity'] for n in ['Context',*QUALIFIERS,*ROLES,*OUTCOMES,'CanonicalInstance','NormalizedDefinitionKind','ContextResolutionScope','DefinitionCarrier','PreservesExactD66Relation','SilentSiblingIdentityMerge','RawDeclaredComplete','ConsumerRole','SourceTrue','SourceCurrent','SourceAuthoritative','SourceAccepted','SourceExecutable','ContextCurrent','ValidatorPassed','ConsumerUnderstood','ConsumerUsed','DefinitionTermAdmitted','ActiveProject','ActiveGoal']}
SIGNATURE.update(DeclaresField=['Entity','Field'],ProductRef=['Entity','Entity'],ProjectRef=['Entity','Entity'],GoalRef=['Entity','Entity'],GoalBelongsProject=['Entity','Entity'],ConsumerRef=['Entity','Entity'],BoundedContextRef=['Entity','Entity'],SourceRelevant=['Entity','Entity'],CurrentViewFor=['Entity','Entity'],PreservingRefreshEvent=['Entity','Entity'],MaterialAnchorChange=['Entity','Entity'],SameIdentityRequired=['Entity','Entity'],SuccessorContextRequired=['Entity','Entity'],SupersedeEarlierRequired=['Entity','Entity'],ActualIdentityStable=['Entity','Entity'],ActualSuccessorCreated=['Entity','Entity'],ActualEarlierSuperseded=['Entity','Entity'])
CTX=pred('Context','c')
def field(n,c='c'):return fn('fieldValue',c,const('F_'+n))
def allowed(value,names):return either(*[eq(value,const(n)) for n in names])
def distinct(names):return both(*[neg(eq(const(a),const(z))) for i,a in enumerate(names) for z in names[i+1:]])
def refs(n,c='c'):return exists([('Entity','x')],pred(n,c,'x'))
def atmost(n):return allof([('Entity','c')],implies(CTX,allof([('Entity','x')],implies(pred(n,'c','x'),allof([('Entity','y')],implies(pred(n,'c','y'),eq(var('x'),var('y'))))))))
NORMALIZED=allof([('Entity','c')],implies(CTX,both(pred('NormalizedDefinitionKind','c'),pred('ContextResolutionScope','c'),pred('DefinitionCarrier','c'),eq(fn('normalizedIdValue','c'),const('CONTEXT_ID')))))
CANONICAL=allof([('Entity','c')],implies(pred('CanonicalInstance','c'),both(CTX,pred('PreservesExactD66Relation','c'),neg(pred('SilentSiblingIdentityMerge','c')))))
GENUS=allof([('Entity','c')],{'op':'iff','left':CTX,'right':both(*[pred(n,'c') for n in QUALIFIERS])})
DECLARATION=allof([('Entity','c')],implies(CTX,allof([('Field','f')],implies(allowed(var('f'),['F_'+n for n in FIELDS]),pred('DeclaresField','c','f')))))
ONE_PRODUCT=allof([('Entity','c')],implies(CTX,exists([('Entity','x')],both(pred('ProductRef','c','x'),allof([('Entity','y')],implies(pred('ProductRef','c','y'),eq(var('x'),var('y'))))))))
PROJECT_ATMOST=atmost('ProjectRef');GOAL_ATMOST=atmost('GoalRef')
KIND_ENUM=allof([('Entity','c')],implies(CTX,both(allowed(fn('contextKindValue','c'),KINDS),distinct(KINDS))))
LIFECYCLE_ENUM=allof([('Entity','c')],implies(CTX,both(allowed(fn('contextLifecycleValue','c'),LIFECYCLES),distinct(LIFECYCLES))))
KIND_BINDINGS=allof([('Entity','c')],implies(CTX,both(implies(eq(fn('contextKindValue','c'),const('PRODUCT')),both(neg(refs('ProjectRef')),neg(refs('GoalRef')))),implies(eq(fn('contextKindValue','c'),const('PROJECT')),both(refs('ProjectRef'),neg(refs('GoalRef')))),implies(eq(fn('contextKindValue','c'),const('GOAL')),both(refs('ProjectRef'),refs('GoalRef'),allof([('Entity','p')],implies(pred('ProjectRef','c','p'),allof([('Entity','g')],implies(pred('GoalRef','c','g'),pred('GoalBelongsProject','g','p'))))))))))
REFERENCE_ROLES=allof([('Entity','c')],implies(CTX,allof([('Entity','x')],both(*[implies(pred(rel,'c','x'),pred(role,'x')) for rel,role in [('ProductRef','ProductRole'),('ProjectRef','ProjectRole'),('GoalRef','GoalRole'),('ConsumerRef','ConsumerRole'),('BoundedContextRef','BoundedContextRole')]]))))
CONSUMERS=allof([('Entity','c')],implies(CTX,refs('ConsumerRef')))
STABILITY=allof([('Entity','c'),('Entity','e')],implies(both(CTX,pred('PreservingRefreshEvent','c','e')),pred('SameIdentityRequired','c','e')))
SUCCESSOR=allof([('Entity','c'),('Entity','e')],implies(both(CTX,pred('MaterialAnchorChange','c','e')),pred('SuccessorContextRequired','c','e')))
SUPERSESSION=allof([('Entity','c'),('Entity','e')],implies(both(CTX,pred('MaterialAnchorChange','c','e')),pred('SupersedeEarlierRequired','c','e')))
NONCOLLAPSE=allof([('Entity','c')],implies(CTX,both(*[neg(pred(n,'c')) for n in ROLES])))
BOUNDED_NONCOLLAPSE=allof([('Entity','c')],implies(CTX,neg(pred('BoundedContextRole','c'))))
ANCHORS=both(ONE_PRODUCT,PROJECT_ATMOST,GOAL_ATMOST,KIND_BINDINGS,REFERENCE_ROLES)
THEORY=[NORMALIZED,CANONICAL,GENUS,DECLARATION,ONE_PRODUCT,PROJECT_ATMOST,GOAL_ATMOST,KIND_ENUM,LIFECYCLE_ENUM,KIND_BINDINGS,REFERENCE_ROLES,CONSUMERS,STABILITY,SUCCESSOR,SUPERSESSION,NONCOLLAPSE]
def main():
 context=json.loads((UNIT/'context.json').read_bytes());unchanged(context['sources']);external_current(context);snap=snapshot();r.verify(snap,ROOT);source=source_ref(snap,'cal.definition.context');doc=co.source_document(snap,source);units=co.inventory(doc);texts=dict(co.string_leaves(doc));N='/voices/scientific_formal/normative_statement';F='/voices/scientific_formal/formal_expression';formal=texts[F];norm=texts[N]
 target=norm.split('Target-specific normative meaning:\n\n')[1].split('\n\n')[0];basis=norm.split('Bound source-semantic basis:\n\n')[1];genus=basis.split('\n\n')[0];anchor=basis.split('\n\n')[1];refresh=basis.split('\n\n')[2];stable,changed=refresh.split(' A material\nchange',1);changed='A material\nchange'+changed
 tuple_text=formal.split('Context =\n')[1].split('\n\n')[0];tuple_text='Context =\n'+tuple_text
 kind_conditions='kind = product => project_ref = null and goal_ref = null\nkind = project => project_ref != null and goal_ref = null\nkind = goal =>\n  project_ref != null\n  and goal_ref != null\n  and belongs_to(goal_ref, project_ref)'
 chosen=[(N,norm.split('\n\n')[0],both(NORMALIZED,CANONICAL),['axiomatic-implicit']),(N,target,both(GENUS,ANCHORS,CONSUMERS),['genus-differentia','axiomatic-implicit']),(N,genus,GENUS,['genus-differentia']),(N,anchor,ANCHORS,['axiomatic-implicit']),(N,stable,STABILITY,['axiomatic-implicit','operational']),(N,changed,both(SUCCESSOR,SUPERSESSION),['axiomatic-implicit','operational']),(F,tuple_text,DECLARATION,['axiomatic-implicit']),(F,'kind in { product, project, goal }',KIND_ENUM,['finite-enumeration']),(F,'lifecycle_state in { draft, active, superseded, retired }',LIFECYCLE_ENUM,['finite-enumeration']),(F,'|product_ref| = 1',ONE_PRODUCT,['axiomatic-implicit']),(F,'|project_ref| <= 1',PROJECT_ATMOST,['axiomatic-implicit']),(F,'|goal_ref| <= 1',GOAL_ATMOST,['axiomatic-implicit']),(F,'|consumer_refs| >= 1',CONSUMERS,['axiomatic-implicit']),(F,kind_conditions,KIND_BINDINGS,['axiomatic-implicit']),(F,'material_change(product_ref, project_ref, goal_ref, purpose) =>\n  successor_context_required',SUCCESSOR,['axiomatic-implicit','operational']),(F,'Context =/= BoundedContext',BOUNDED_NONCOLLAPSE,['axiomatic-implicit'])]+[(sel,texts[sel].split('\n\n')[0],NONCOLLAPSE,['axiomatic-implicit']) for sel in ['/boundaries/0','/voices/scientific_formal/boundary_conditions/0']]
 clauses=[];links=[]
 for unit in units:
  sel=unit['selector'];text=texts[sel];cuts={0,len(text)}
  for selector,excerpt,_,_ in chosen:
   if selector==sel:start=text.index(excerpt);cuts.update([start,start+len(excerpt)])
  points=sorted(cuts)
  for start,end in zip(points,points[1:]):
   excerpt=text[start:end];statement=None;disposition='deferred';forms=['unresolved'];roles=['unresolved'];why='Actual Product/Project/Goal/reference/owner and view/resolver/source-epoch meaning,materiality and universal temporal identity preservation remain unaccepted.'
   for selector,selected,formula,selected_forms in chosen:
    if sel==selector and excerpt==selected:statement=formula;disposition='encoded';forms=selected_forms;roles=['definition'];why='Candidate qualified genus,normalized axes,15 declared fields,exact/at-most anchors,kind/lifecycle tags,consumer existence and normative stable/successor/supersession requirements. Distinct enum-tag interpretation is explicit and pending owner acceptance; no actual grant or transition follows.'
   if statement is None and (sel.startswith('/voices/plain_language/') or sel.startswith('/voices/domain_context/') or sel.startswith('/voices/scientific_formal/notation/')):disposition='explanatory';roles=['explanation-example'];why='Selected intuition,examples and DDD/Registry context do not import a resolver,consumer understanding,reference ownership or active runtime.'
   cid='CTX-'+str(len(clauses)+1).zfill(3);clauses.append({'clause_id':cid,'source_selector':sel,'excerpt_sha256':r.digest(excerpt.encode()),'start_character':start,'disposition':disposition,'forms':forms,'roles':roles,'formal_statement':statement,'rationale':why});links.append({'unit_id':unit['unit_id'],'clause_id':cid,'end_character':end,'excerpt':excerpt})
 names=['definition','product','product-thesis','bounded-context','context-request','context-view','context-profile','context-lineage-record','context-map','context-migration-manifest','coordination-context','semantic-epoch','representation-revision','ubiquitous-language','artifact-type-registry','source','projection-specification','session-memory','agent-session','identity-carrier','identity-relation','classification','classification-scheme','classification-orthogonality-invariant','authority','authority-claim','authority-boundary','authority-surface','authority-promotion','decision','decision-scope','evidence','residue','typed-relation','relation-kind','validation','validation-receipt','canonical-representation-invariant','semantic-event-history','governance-event-history']
 deps=[source_ref(snap,'cal.definition.'+n) for n in names]+[source_ref(snap,n) for n in ['CAV2-D59','CAV2-D60']];primary=next(x['clause_id'] for x in clauses if x['formal_statement']==GENUS);dl=[{'clause_id':primary,'dependency_ref':dep,'kind':'semantic-use','rationale':'Exact authored use requires independently reviewed meaning/role/reference alignment; source lineage and labels do not merge identities.'} for dep in deps]
 declarations=[{'kind':'sort','symbol_id':n,'scope':SCOPE,'domain_policy':'nonempty'} for n in SORTS]+[{'kind':'constant','symbol_id':n,'scope':SCOPE,'result_sort':sort} for n,sort in CONSTANTS.items()]+[{'kind':'total-function','symbol_id':n,'scope':SCOPE,'argument_sorts':args,'result_sort':result,'definedness_policy':None} for n,(args,result) in FUNCTIONS.items()]+[{'kind':'predicate' if len(args)==1 else 'relation','symbol_id':n,'scope':SCOPE,'argument_sorts':args} for n,args in SIGNATURE.items()]
 def ctxkind(k):return exists([('Entity','c')],both(CTX,eq(fn('contextKindValue','c'),const(k))))
 required={'Context':exists([('Entity','c')],CTX),'ProductContext':ctxkind('PRODUCT'),'ProjectContext':ctxkind('PROJECT'),'GoalContext':ctxkind('GOAL'),'RawDeclaredWithoutContext':exists([('Entity','c')],both(pred('RawDeclaredComplete','c'),neg(CTX))),'ZeroBoundedContextRefs':exists([('Entity','c')],both(CTX,neg(refs('BoundedContextRef')))),'MultipleConsumers':exists([('Entity','c'),('Entity','x'),('Entity','y')],both(CTX,pred('ConsumerRef','c','x'),pred('ConsumerRef','c','y'),neg(eq(var('x'),var('y'))))),
 'DistinctSameAnchorContexts':exists([('Entity','c'),('Entity','d')],both(CTX,pred('Context','d'),neg(eq(var('c'),var('d'))),eq(fn('contextKindValue','c'),fn('contextKindValue','d')),eq(field('purpose'),field('purpose','d')),allof([('Entity','x')],both(*[{'op':'iff','left':pred(n,'c','x'),'right':pred(n,'d','x')} for n in ['ProductRef','ProjectRef','GoalRef']])))),
 'StableRefreshRequirementWithoutActualGuarantee':exists([('Entity','c'),('Entity','e')],both(CTX,pred('PreservingRefreshEvent','c','e'),pred('SameIdentityRequired','c','e'),neg(pred('ActualIdentityStable','c','e')))),
 'MaterialChangeRequirementsWithoutActualSuccessor':exists([('Entity','c'),('Entity','e')],both(CTX,pred('MaterialAnchorChange','c','e'),pred('SuccessorContextRequired','c','e'),pred('SupersedeEarlierRequired','c','e'),neg(pred('ActualSuccessorCreated','c','e')),neg(pred('ActualEarlierSuperseded','c','e')))),
 'RelevantSourceWithoutTruth':exists([('Entity','c'),('Entity','s')],both(CTX,pred('SourceRelevant','c','s'),neg(pred('SourceTrue','s')))),
 'CurrentViewWithoutCurrentContext':exists([('Entity','c'),('Entity','v')],both(CTX,pred('CurrentViewFor','v','c'),neg(pred('ContextCurrent','c')))),
 'ValidatorPassedWithoutConsumerUnderstanding':exists([('Entity','c')],both(CTX,pred('ValidatorPassed','c'),neg(pred('ConsumerUnderstood','c')),neg(pred('ConsumerUsed','c'))))}
 populations=[{'population_id':'POP-'+n,'carrier':'Entity','predicate_ref':n if n in SIGNATURE and len(SIGNATURE[n])==1 else None,'requirement':'required','statement':statement,'scope':SCOPE,'rationale':'Supplied qualified static kind/cardinality/identity and nonentailment witness; actual source/reference/owner/trace semantics unaccepted.','review_ref':None} for n,statement in required.items()]+[{'population_id':'POP-'+n,'carrier':args[0],'predicate_ref':n if len(args)==1 else None,'requirement':'unresolved','statement':None,'scope':SCOPE,'rationale':'Actual population and role/reference/owner/consumer/epoch/lifecycle denotation remain pending.','review_ref':None} for n,args in SIGNATURE.items() if n not in required]
 core={'interpretation_id':'interpretation:Context-exact-anchors-and-normative-identity-change-v1','source':source,'scope':SCOPE,'declarations':declarations,'clauses':clauses,'depends_on':deps,'relations':[],'assumptions':[],'populations':populations,'logic_features':['first-order','equality'],'semantic_status':'candidate','source_fidelity':'pending','profile_ref':'profile:Context-qualified-anchors-and-hypothetical-refresh-successor-v1'}
 losses=['Normalized Definition header,genus iff and source/formal/target precedence need owner review; ContextRequest/View siblings remain distinct.','15 declared fields,kind/lifecycle function values and Product/Project/Goal reference sets need accepted actual-record/reference maps.','Exactly one Product,optional at-most-one Project/Goal and Goal membership need actual qualified identity/role resolution.','Three kind/four lifecycle constants have explicit candidate distinctness; enum identity and current lifecycle/status axes require review.','Consumer and zero-or-more DDD references do not merge source ownership,domain models or imply correct consumer understanding/use.','Materiality and preserving-refresh predicates carry normative requirements,not actual identity stability,successor creation,supersession or universal temporal proofs.','Source relevance,current View,active Context,passing validator and admitted Definition cannot substitute for truth,currentness,authority,Project/Goal activation,instance/resolver admission or actual effects.','All42 authored uses and shared meaning completeness remain independently reviewable; missing ProjectSpace/Language/Registry/snapshot/pack source maps are unresolved,not silently inferred.']
 findings=[{'finding_id':'CTX-FINDING-'+str(i+1).zfill(3),'selectors':[N,F,'/boundaries/0','/scope/applicability'],'description':why,'status':'unresolved','owner_route':'role:definition-owner with Context,Product,Project,Goal,resolver,consumer and lifecycle owners'} for i,why in enumerate(losses)]
 packet={'schema_version':'definition-assurance-correspondence/v1-candidate','authority_effect':'none','upstream_schema_sha256':r.digest((IMPL/'schemas/input-envelope.json').read_bytes()),'source_selection':'current','inventory_policy':'all-nonempty-string-leaves-in-voices-boundaries-scope-and-claim-ceiling/v1','interpretation':core,'source_units':units,'correspondence':links,'dependency_links':dl,'dependency_closure':{'status':'unresolved','review_ref':None,'unresolved_notes':losses},'assumption_links':[],'source_precedence':{'normative_voice':'/voices/scientific_formal','conflicts':findings,'review_ref':None},'review_packet':{'instances':[{'case_id':'three-kinds-with-exact-qualified-anchor-sets','scenario':'Supplied product,project and goal Contexts use one Product,conditional optional refs and a Goal belonging to the selected Project.','expected_interpretation':'Static reference-set cardinality and normative change requirements without actual resolution or effects.','rationale':'Candidate denotation is not an owner/resolver/trace approval.','related_clause_ids':[primary]}],'counterexamples':[{'case_id':'current-view-and-field-record-not-context-currentness','scenario':'A current View or passed validator is mistaken for current Context,source truth or successful consumer use.','expected_interpretation':'Those entailments have independent negative witnesses.','rationale':'Source explicitly separates identities and authority axes.','related_clause_ids':[primary]}],'known_losses':losses,'review_status':'pending','review_ref':None}}
 account=co.check(packet,snap,required_dependencies=[x['version_ref'] for x in deps],required_conflicts=[x['finding_id'] for x in findings])
 if not account.get('character_accounting_complete'):raise ValueError('Incomplete/malformed correspondence '+json.dumps(account))
 for n,z in [('t.json',{'schema_version':'definition-assurance-input/v1-candidate','kind':'interpretation','authority_effect':'none','payload':core}),('correspondence.json',packet),('static-ir.json',ir.compile_interpretation(core,snap)),('correspondence-check.json',account)]:put(n,z)
 put('clause-analysis.json',{'authority_effect':'none','source':source,'encoded_spans':sum(x['disposition']=='encoded' for x in clauses),'unique_encoded_source_formula_values':len({json.dumps(x['formal_statement'],sort_keys=True) for x in clauses if x['disposition']=='encoded'}),'primitive_theory_formulas':len(THEORY),'source_precedence_reviewed':False,'mechanized_proof':False,'known_losses':losses,'nonnegative_bounded_ref_cardinality':'Unbounded finite relation extension permits zero references; printed >=0 is retained deferred as a tautological cardinality clause,not an actual DDD meaning proof.'})
 queries=[]
 def q(id,target,witness):queries.append({'query_id':id,'target':target,'witness_condition':witness,'selected_in_T':False,'source_fidelity':'pending'})
 for n in OUTCOMES:q('Context-does-not-entail-'+n,allof([('Entity','c')],implies(CTX,pred(n,'c'))),required['Context'])
 for n in ['SourceTrue','SourceCurrent','SourceAuthoritative','SourceAccepted','SourceExecutable']:q('source-relevance-does-not-entail-'+n,allof([('Entity','c'),('Entity','s')],implies(both(CTX,pred('SourceRelevant','c','s')),pred(n,'s'))),required['RelevantSourceWithoutTruth'])
 q('current-View-not-current-Context',allof([('Entity','c'),('Entity','v')],implies(both(CTX,pred('CurrentViewFor','v','c')),pred('ContextCurrent','c'))),required['CurrentViewWithoutCurrentContext'])
 q('active-Context-not-source-truth-or-authority',allof([('Entity','c'),('Entity','s')],implies(both(CTX,eq(fn('contextLifecycleValue','c'),const('ACTIVE')),pred('SourceRelevant','c','s')),either(pred('SourceTrue','s'),pred('SourceAuthoritative','s')))),required['RelevantSourceWithoutTruth'])
 for n in ['ActualAdmission','ResolverContractAccepted','RuntimeActivated','ActualPublication','ActualRelease','ActualDeployment','ExternalEffect']:q('admitted-Definition-term-not-instance-'+n,allof([('Entity','c')],implies(both(CTX,pred('DefinitionTermAdmitted','c')),pred(n,'c'))),required['Context'])
 for n in ['ConsumerUnderstood','ConsumerUsed']:q('validator-pass-not-'+n,allof([('Entity','c')],implies(both(CTX,pred('ValidatorPassed','c')),pred(n,'c'))),required['ValidatorPassedWithoutConsumerUnderstanding'])
 for rel,flag in [('ProjectRef','ActiveProject'),('GoalRef','ActiveGoal')]:q('active-Context-not-'+flag,allof([('Entity','c'),('Entity','x')],implies(both(CTX,eq(fn('contextLifecycleValue','c'),const('ACTIVE')),pred(rel,'c','x')),pred(flag,'x'))),required['GoalContext'])
 q('raw-fields-not-Context-genus',allof([('Entity','c')],implies(pred('RawDeclaredComplete','c'),CTX)),required['RawDeclaredWithoutContext'])
 q('stable-refresh-requirement-not-actual-identity-guarantee',allof([('Entity','c'),('Entity','e')],implies(both(CTX,pred('PreservingRefreshEvent','c','e')),pred('ActualIdentityStable','c','e'))),required['StableRefreshRequirementWithoutActualGuarantee'])
 for n in ['ActualSuccessorCreated','ActualEarlierSuperseded']:q('material-change-not-actual-'+n,allof([('Entity','c'),('Entity','e')],implies(both(CTX,pred('MaterialAnchorChange','c','e')),pred(n,'c','e'))),required['MaterialChangeRequirementsWithoutActualSuccessor'])
 put('query-policy.json',{'authority_effect':'none','queries':queries,'targets_not_assumptions':True,'whole_definition_proof_claimed':False})
 counts={'source_units':len(units),'mapped_clauses':len(clauses),**{n+'_clauses':sum(x['disposition']==n for x in clauses) for n in ['encoded','explanatory','deferred']},'declarations':len(declarations),'required_populations':len(required),'unresolved_populations':sum(x['requirement']=='unresolved' for x in populations),'direct_semantic_uses':len(deps),'countermodel_queries':len(queries)};put('denominator.json',counts)
 comp=[source_ref(snap,'cal.definition.'+n) for n in ['product','product-thesis','bounded-context','context-request','context-view','context-profile','context-lineage-record','coordination-context','semantic-epoch','identity-relation']]+[source_ref(snap,n) for n in ['CAV2-D59','CAV2-D60']]
 put('comparison-selection.json',{'authority_effect':'none','separate_qualified_sources':comp,'selected_refs':[{'path':x['path'],'sha256':x['sha256']} for x in comp]+[ref(BASE/'definitions/cal.definition.contestability-policy'/n) for n in ['t.json','static-ir.json','REVIEW.md','delivery-manifest.json']],'comparison_assembled_into_primary_T':False,'source_precedence_reviewed':False,'external_context_refs':[],'source_fidelity':'pending','claim_ceiling':'Exact distinct Context/Product/Project/Goal/DDD/sibling/epoch identities; no D66 sibling merge,actual reference resolution,consumer use or temporal effect imported.'})
 c.validate(json.loads((UNIT/'t.json').read_bytes()),'interpretation');unchanged(context['sources']);external_current(context);print(json.dumps(counts,indent=2,sort_keys=True))
if __name__=='__main__':main()
