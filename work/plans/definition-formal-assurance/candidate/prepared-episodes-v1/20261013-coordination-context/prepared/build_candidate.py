"""Prepared Coordination Context source-qualified frame, optional anchors, boundaries and identity guards."""
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


SCOPE='scope:candidate:CoordinationContext-fourteen-coordinates-optional-anchors-explicit-boundaries-identity-v1'
SORTS=['ContextReference','IdentityReference','ProductReference','ProjectReference','GoalReference','PurposeReference','ConsumerCollectionReference','IntendedUseCollectionReference','SubjectScopeReference','SourcePolicyCollectionReference','BoundedContextCollectionReference','BoundedContextVersionReference','OwnerReference','LifecycleReference','RevisionHistoryReference','ChallengeRouteReference','AnchorChangeReference','SourceViewChangeReference','SourceViewReference','Token']
CONSTANTS={'EMPTY':'Token'}
FIELDS={'contextIdentity':'IdentityReference','contextProduct':'ProductReference','contextPurpose':'PurposeReference','contextConsumers':'ConsumerCollectionReference','contextIntendedUses':'IntendedUseCollectionReference','contextSubjectScope':'SubjectScopeReference','contextSourcePolicies':'SourcePolicyCollectionReference','contextBoundedContexts':'BoundedContextCollectionReference','contextOwner':'OwnerReference','contextLifecycle':'LifecycleReference','contextRevisionHistory':'RevisionHistoryReference','contextChallengeRoute':'ChallengeRouteReference'}
OPTIONAL={'contextProject':'ProjectReference','contextGoal':'GoalReference'}
BOUNDARY_FIELDS={'boundedContextVersionOwner':'OwnerReference'}
CHANGE_FIELDS={'changeOriginalContext':'ContextReference','changeDesiredProduct':'ProductReference','changeDesiredPurpose':'PurposeReference'}
CHANGE_OPTIONAL={'changeDesiredProject':'ProjectReference','changeDesiredGoal':'GoalReference'}
SUCCESSOR_FIELDS={'changeSuccessorContext':'ContextReference'}
VIEW_FIELDS={'viewBeforeContext':'ContextReference','viewAfterContext':'ContextReference','viewBeforeSource':'SourceViewReference','viewAfterSource':'SourceViewReference'}
GROUPS=[(FIELDS,'ContextReference'),(OPTIONAL,'ContextReference'),(BOUNDARY_FIELDS,'BoundedContextVersionReference'),(CHANGE_FIELDS,'AnchorChangeReference'),(CHANGE_OPTIONAL,'AnchorChangeReference'),(SUCCESSOR_FIELDS,'AnchorChangeReference'),(VIEW_FIELDS,'SourceViewChangeReference')]
FUNCTIONS={name:([carrier],sort) for fields,carrier in GROUPS for name,sort in fields.items()}
HANDLES={sort:sort[0].lower()+sort[1:]+'Handle' for sort in SORTS if sort!='Token'}
FUNCTIONS.update({name:([sort],'Token') for sort,name in HANDLES.items()})
EXCLUDED=['ContextIsBoundedContextDeclared','ContextIsProductDeclared','ContextIsProjectDeclared','ContextIsGoalDeclared','ContextIsPromptDeclared','ContextIsSourceSelectionDeclared','ContextIsDecisionDeclared','ContextIsExecutionPermissionDeclared','ContainmentMakesBoundedContextDeclared','DirectorySuppliesIdentityDeclared','DirectorySuppliesOwnershipDeclared','ContextNominationAuthorizesExecutionDeclared']
ACTUAL=['IdentityFidelity','Durability','OwnerQualification','OwnerAuthorization','ProductResolution','ProjectResolution','GoalResolution','PurposeStability','ConsumerResolution','IntendedUseSuitability','SubjectScopeResolution','SourcePolicyEnforcement','BoundedContextResolution','IndependentBoundaryOwnership','LifecycleOperation','HistoryAuthenticity','ChallengeHandling','Creation','ExecutionPermission','SourceFidelity','ConsumerAlignment','WholeProof']
CHANGE_ACTUAL=['MaterialityCorrectness','SuccessorCreation','DesiredAnchorResolution','IdentityFidelity','HistoryAuthenticity','WholeProof']
VIEW_ACTUAL=['IdentityPreservation','ViewAuthenticity','ViewSuitability','WholeProof']
SIGNATURE={n:['ContextReference'] for n in ['ContextApplicable','ContextInScopeDeclared','ContextDurableDeclared','ContextOwnerQualifiedDeclared','ContextPurposeStableDeclared','ContextHasProjectDeclared','ContextHasGoalDeclared',*EXCLUDED,*['ContextActual'+x for x in ACTUAL]]}
SIGNATURE.update({n:['AnchorChangeReference'] for n in ['AnchorChangeApplicable','AnchorChangeInScopeDeclared','MaterialAnchorChangeDeclared','ChangeDesiredHasProjectDeclared','ChangeDesiredHasGoalDeclared',*['AnchorChangeActual'+x for x in CHANGE_ACTUAL]]})
SIGNATURE.update({n:['SourceViewChangeReference'] for n in ['SourceViewChangeApplicable','SourceViewChangeInScopeDeclared',*['SourceViewChangeActual'+x for x in VIEW_ACTUAL]]})
for sort in SORTS:
 if sort!='Token':SIGNATURE[sort+'Declared']=[sort]
for fields,carrier in GROUPS:SIGNATURE.update({name+'BindingDeclared':[carrier,sort] for name,sort in fields.items()})
SIGNATURE.update(ContextProductLinkDeclared=['ContextReference','ProductReference'],ContextProjectLinkDeclared=['ContextReference','ProjectReference'],ContextGoalLinkDeclared=['ContextReference','GoalReference'],BoundedContextCollectionContainsDeclared=['BoundedContextCollectionReference','BoundedContextVersionReference'],ContextBoundedContextLinkDeclared=['ContextReference','BoundedContextVersionReference'],IndependentBoundaryOwnershipDeclared=['ContextReference','BoundedContextVersionReference','OwnerReference'],SuccessorCoordinationIdentityDeclared=['IdentityReference','IdentityReference'])
MAP={'ContextReference':'ContextApplicable','AnchorChangeReference':'AnchorChangeApplicable','SourceViewChangeReference':'SourceViewChangeApplicable'}
def iff(a,z):return {'op':'iff','left':a,'right':z}
def member(sort):return MAP.get(sort,sort+'Declared')
def guard(sort,value):return both(pred(member(sort),value),neg(eq(fn(HANDLES[sort],value),const('EMPTY'))))
def exact(fields,value):return both(*[both(guard(sort,fn(name,value)),allof([(sort,'target')],iff(pred(name+'BindingDeclared',value,'target'),eq(var('target'),fn(name,value))))) for name,sort in fields.items()])
def selected(sort,name,body):return allof([(sort,name)],implies(pred(member(sort),name),body))
X=var('x');A=var('a');V=var('v');B=var('b')
APP=pred('ContextApplicable',X);CHANGE=pred('AnchorChangeApplicable',A);VIEW=pred('SourceViewChangeApplicable',V)
ROOT_RULE=both(allof([('ContextReference','x')],iff(APP,pred('ContextInScopeDeclared',X))),selected('ContextReference','x',both(guard('ContextReference',X),exact(FIELDS,X),pred('ContextDurableDeclared',X),pred('ContextOwnerQualifiedDeclared',X),pred('ContextPurposeStableDeclared',X))))
PRODUCT_RULE=selected('ContextReference','x',allof([('ProductReference','product')],iff(pred('ContextProductLinkDeclared',X,'product'),eq(var('product'),fn('contextProduct',X)))))
OPTIONAL_RULE=selected('ContextReference','x',both(*[both(allof([(sort,'candidate')],iff(pred('Context'+kind+'LinkDeclared',X,'candidate'),both(pred('ContextHas'+kind+'Declared',X),eq(var('candidate'),fn('context'+kind,X))))),implies(pred('ContextHas'+kind+'Declared',X),exact({'context'+kind:sort},X))) for kind,sort in [('Project','ProjectReference'),('Goal','GoalReference')]]))
BOUNDARY_RULE=selected('ContextReference','x',allof([('BoundedContextVersionReference','b')],both(iff(pred('ContextBoundedContextLinkDeclared',X,B),pred('BoundedContextCollectionContainsDeclared',fn('contextBoundedContexts',X),B)),implies(pred('ContextBoundedContextLinkDeclared',X,B),both(guard('BoundedContextVersionReference',B),exact(BOUNDARY_FIELDS,B),pred('IndependentBoundaryOwnershipDeclared',X,B,fn('boundedContextVersionOwner',B)))))))
ORIGINAL=fn('changeOriginalContext',A);SUCCESSOR=fn('changeSuccessorContext',A)
def optional_difference(kind):
 before=pred('ContextHas'+kind+'Declared',ORIGINAL);after=pred('ChangeDesiredHas'+kind+'Declared',A)
 return either(both(before,neg(after)),both(neg(before),after),both(before,after,neg(eq(fn('context'+kind,ORIGINAL),fn('changeDesired'+kind,A)))))
ANCHOR_DELTA=either(neg(eq(fn('contextProduct',ORIGINAL),fn('changeDesiredProduct',A))),neg(eq(fn('contextPurpose',ORIGINAL),fn('changeDesiredPurpose',A))),optional_difference('Project'),optional_difference('Goal'))
CHANGE_RULE=both(allof([('AnchorChangeReference','a')],iff(CHANGE,pred('AnchorChangeInScopeDeclared',A))),selected('AnchorChangeReference','a',both(guard('AnchorChangeReference',A),exact(CHANGE_FIELDS,A),*[implies(pred('ChangeDesiredHas'+kind+'Declared',A),exact({'changeDesired'+kind:sort},A)) for kind,sort in [('Project','ProjectReference'),('Goal','GoalReference')]],implies(pred('MaterialAnchorChangeDeclared',A),both(ANCHOR_DELTA,exact(SUCCESSOR_FIELDS,A),neg(eq(fn('contextIdentity',ORIGINAL),fn('contextIdentity',SUCCESSOR))),pred('SuccessorCoordinationIdentityDeclared',fn('contextIdentity',ORIGINAL),fn('contextIdentity',SUCCESSOR)),eq(fn('contextProduct',SUCCESSOR),fn('changeDesiredProduct',A)),eq(fn('contextPurpose',SUCCESSOR),fn('changeDesiredPurpose',A)),*[both(iff(pred('ContextHas'+kind+'Declared',SUCCESSOR),pred('ChangeDesiredHas'+kind+'Declared',A)),implies(pred('ChangeDesiredHas'+kind+'Declared',A),eq(fn('context'+kind,SUCCESSOR),fn('changeDesired'+kind,A)))) for kind in ['Project','Goal']])))))
VIEW_RULE=both(allof([('SourceViewChangeReference','v')],iff(VIEW,pred('SourceViewChangeInScopeDeclared',V))),selected('SourceViewChangeReference','v',both(guard('SourceViewChangeReference',V),exact(VIEW_FIELDS,V),eq(fn('contextIdentity',fn('viewBeforeContext',V)),fn('contextIdentity',fn('viewAfterContext',V))))))
BOUNDARIES=selected('ContextReference','x',both(*[neg(pred(name,X)) for name in EXCLUDED]))
THEORY={'root-fourteen-coordinate-durable-owner-frame':ROOT_RULE,'exactly-one-Product-link':PRODUCT_RULE,'optional-Project-and-Goal-cardinality':OPTIONAL_RULE,'explicit-zero-or-more-independent-boundary-links':BOUNDARY_RULE,'material-anchor-successor-identity':CHANGE_RULE,'source-view-change-preserves-identity':VIEW_RULE,'role-containment-directory-permission-boundaries':BOUNDARIES}
LOSSES=[
'C18 positive Definition admission andC17 selected source-use scopes do notaccept translation,createaContext,bindanoperational owner orauthorizeexecution.',
'Fourteen source coordinates retain twelve required andtwo optional typedprojections;descriptor namesdo notcreate newcanonicalDefinitions.',
'Exactly oneProduct andoptionalProject/Goalzeroorone areexplicitlink conditions ratherthanclaimedcontents ofnonempty handles.',
'Project andGoal referencepresence isindependent;no requirement thatboth arepresent orshare ownership isintroduced.',
'ZeroBoundedContextlinks arevalid;oneormany exactnominatedversionmembers requireexplicitlinks,declaredowners andindependent ownershiprelationships.',
'Independent BoundedContextownership isnot forceddifferentprincipal IDs,exclusive partitioning,containment hierarchy orautomaticcoordinationownership.',
'Durability,ownerqualification,stablepurpose,lifecycle,history andchallenge are necessarydeclarations,notproof ofactualpersistedidentity orboundprincipal authority.',
'Consumers,intendeduses,subjectscope andsourcepolicies staydistinctproposedcarriers;no unsupportedcollection cardinalities orcompleteconsumer universe isinvented.',
'Materiality requiresanexplicitsource-owned interpretation;not everyreference difference orsourceviewchange isclassifiedmaterial.',
'A selectedmaterialchange hasanactualdeclaredanchor delta andrequiresdistinctsuccessoridentity withmatched desiredProduct/Project/Goal/purpose.',
'Desiredanchorstate staysindependentfromsuccessorref,soinplacechangescannot erase their owncomparison.',
'Nonmaterialdeltas andno-anchor-change casesdo notacquire a mandatorysuccessor fromthiscondition;otherlegitimateidentity policies require ownerreview.',
'Sourceviewchanges preserve nominateddurableCoordinationidentity;theguard neither authenticates theview norinfers validity,suitability orsourcepolicy enforcement.',
'Successoridentity declarations do notcreate newContexts orauthenticatehistory;no globalunique-successor,latestversion orclockorder isassumed.',
'Roleexclusions preserve CoordinationversusBoundedContext,Product,Project,Goal,prompt,source selection,Decision andexecutionpermission.',
'Containment anddirectory placementcannot supplyidentity,ownership orsemanticboundary;nominalsort differencesalone do notproveaccepted denotation.',
'Actualowner/reference resolution,materiality,lifecycle,history,succession,creation andpermission remainseparatequerytargetsoutsideT.',
'C17D66 H2semantic-evidence selection andwholeContextPackage explanatoryselection retain exactrelocatedbytes andnon-effects;unselected source meanings andpackageauthority arenotimported.',
'No wholepriorProduct/Project/Goal/BoundedContext/source-policy oridentitytheory isassembledinto theprimaryinterpretation.',
'Required finitepopulations arecoveragewitnesses independentofT,notactualenumeration oracceptedshared-model consistency.',
'OriginalT/O/E/R/J artifacts,source-owner/consumer maps,cycleclassification,wholeproofs andfinalepisode reviewremainrequired afterthisstage.']
def declarations():return [{'kind':'sort','symbol_id':name,'scope':SCOPE,'domain_policy':'nonempty'} for name in SORTS]+[{'kind':'constant','symbol_id':name,'scope':SCOPE,'result_sort':sort} for name,sort in CONSTANTS.items()]+[{'kind':'total-function','symbol_id':name,'scope':SCOPE,'argument_sorts':args,'result_sort':result,'definedness_policy':None} for name,(args,result) in FUNCTIONS.items()]+[{'kind':'predicate' if len(args)==1 else 'relation','symbol_id':name,'scope':SCOPE,'argument_sorts':args} for name,args in SIGNATURE.items()]
def required_populations():
 def xw(body):return exists([('ContextReference','x')],both(APP,body))
 def aw(body):return exists([('AnchorChangeReference','a')],both(CHANGE,body))
 project=pred('ContextHasProjectDeclared',X);goal=pred('ContextHasGoalDeclared',X)
 rows={'Context':('ContextReference',xw(APP)),'OutsideContext':('ContextReference',exists([('ContextReference','x')],neg(APP))),'NeitherOptionalAnchor':('ContextReference',xw(both(neg(project),neg(goal)))),'ProjectOnly':('ContextReference',xw(both(project,neg(goal)))),'GoalOnly':('ContextReference',xw(both(neg(project),goal))),'ProjectAndGoal':('ContextReference',xw(both(project,goal))),'ZeroBoundedContexts':('BoundedContextCollectionReference',xw(neg(exists([('BoundedContextVersionReference','b')],pred('ContextBoundedContextLinkDeclared',X,B))))),'MultipleBoundedContexts':('BoundedContextVersionReference',xw(exists([('BoundedContextVersionReference','b'),('BoundedContextVersionReference','other')],both(pred('ContextBoundedContextLinkDeclared',X,B),pred('ContextBoundedContextLinkDeclared',X,'other'),neg(eq(B,var('other'))))))),'IndependentBoundarySamePrincipal':('OwnerReference',xw(exists([('BoundedContextVersionReference','b')],both(pred('ContextBoundedContextLinkDeclared',X,B),eq(fn('contextOwner',X),fn('boundedContextVersionOwner',B)),pred('IndependentBoundaryOwnershipDeclared',X,B,fn('boundedContextVersionOwner',B)))))),'WithoutActualOutcomes':('ContextReference',xw(both(*[neg(pred('ContextActual'+n,X)) for n in ACTUAL]))),'IndependentExecutionPermission':('ContextReference',xw(pred('ContextActualExecutionPermission',X))),'MaterialProductChange':('AnchorChangeReference',aw(both(pred('MaterialAnchorChangeDeclared',A),neg(eq(fn('contextProduct',ORIGINAL),fn('changeDesiredProduct',A)))))),'MaterialProjectChange':('AnchorChangeReference',aw(both(pred('MaterialAnchorChangeDeclared',A),optional_difference('Project')))),'MaterialGoalChange':('AnchorChangeReference',aw(both(pred('MaterialAnchorChangeDeclared',A),optional_difference('Goal')))),'MaterialPurposeChange':('AnchorChangeReference',aw(both(pred('MaterialAnchorChangeDeclared',A),neg(eq(fn('contextPurpose',ORIGINAL),fn('changeDesiredPurpose',A)))))),'NonmaterialDelta':('AnchorChangeReference',aw(both(neg(pred('MaterialAnchorChangeDeclared',A)),ANCHOR_DELTA))),'NoAnchorChange':('AnchorChangeReference',aw(neg(ANCHOR_DELTA))),'OutsideAnchorChange':('AnchorChangeReference',exists([('AnchorChangeReference','a')],neg(CHANGE))),'ChangeWithoutActualOutcomes':('AnchorChangeReference',aw(both(*[neg(pred('AnchorChangeActual'+n,A)) for n in CHANGE_ACTUAL]))),'SourceViewChange':('SourceViewChangeReference',exists([('SourceViewChangeReference','v')],VIEW)),'DistinctSourceViewsSameIdentity':('SourceViewChangeReference',exists([('SourceViewChangeReference','v')],both(VIEW,neg(eq(fn('viewBeforeSource',V),fn('viewAfterSource',V))),eq(fn('contextIdentity',fn('viewBeforeContext',V)),fn('contextIdentity',fn('viewAfterContext',V)))))),'OutsideSourceViewChange':('SourceViewChangeReference',exists([('SourceViewChangeReference','v')],neg(VIEW))),'ViewChangeWithoutActualOutcomes':('SourceViewChangeReference',exists([('SourceViewChangeReference','v')],both(VIEW,*[neg(pred('SourceViewChangeActual'+n,V)) for n in VIEW_ACTUAL])))}
 return rows
def query_specs():
 rows=[]
 for prefix,sort,name,app,outcomes in [('Context','ContextReference','x',APP,ACTUAL),('AnchorChange','AnchorChangeReference','a',CHANGE,CHANGE_ACTUAL),('SourceViewChange','SourceViewChangeReference','v',VIEW,VIEW_ACTUAL)]:
  for outcome in outcomes:rows.append({'query_id':prefix+'-not-Actual'+outcome,'target':allof([(sort,name)],implies(app,pred(prefix+'Actual'+outcome,name))),'witness_condition':exists([(sort,name)],both(app,neg(pred(prefix+'Actual'+outcome,name)))),'selected_in_T':False,'source_condition':'selected-'+prefix.lower(),'source_fidelity':'pending'})
 return rows
def selected_clauses(doc):
 chosen={'/voices/scientific_formal/normative_statement':(both(*THEORY.values()),['genus-differentia']),'/voices/scientific_formal/formal_expression':(both(ROOT_RULE,PRODUCT_RULE,OPTIONAL_RULE,BOUNDARY_RULE,CHANGE_RULE),['axiomatic-implicit']),'/scope/applicability':(both(ROOT_RULE,PRODUCT_RULE,OPTIONAL_RULE,BOUNDARY_RULE),['genus-differentia']),'/scope/exclusions/0':(BOUNDARIES,['operational']),'/scope/exclusions/1':(BOUNDARIES,['operational']),'/voices/scientific_formal/boundary_conditions/0':(both(BOUNDARY_RULE,BOUNDARIES),['operational']),'/voices/scientific_formal/boundary_conditions/1':(BOUNDARIES,['operational']),'/voices/scientific_formal/testable_conditions/0':(PRODUCT_RULE,['operational']),'/voices/scientific_formal/testable_conditions/1':(OPTIONAL_RULE,['operational']),'/voices/scientific_formal/testable_conditions/2':(BOUNDARY_RULE,['operational']),'/boundaries/0':(BOUNDARIES,['operational']),'/boundaries/1':(VIEW_RULE,['operational'])}
 texts=dict(co.string_leaves(doc));rows=[]
 for unit in co.inventory(doc):
  sel=unit['selector'];formula,forms=chosen.get(sel,(None,['unresolved']));disp='encoded' if formula is not None else 'explanatory' if sel.startswith('/voices/') and any(n in sel for n in ['/domain_context/','/plain_language/','/notation/']) else 'deferred';rows.append({'source_selector':sel,'start_character':0,'excerpt':texts[sel],'formula':formula,'forms':forms,'disposition':disp,'unit_id':unit['unit_id']})
 return rows

def main():
 context=json.loads((UNIT/'context.json').read_bytes());unchanged(context['sources']);external_current(context)
 snap=snapshot();r.verify(snap,ROOT);source=context['source_selection']
 assert source['definition_id']=='cal.definition.coordination-context' and source['sha256']=='547a714a9552f83985de78b2ce228421f5102c40cacf8c1edfb48ef46366a8aa'
 doc=co.source_document(snap,source);units=co.inventory(doc);clauses=[];links=[]
 reasons={'encoded':'Necessary declarations preserve the fourteen-coordinate frame, optional anchors, explicit boundary links, material-change succession and source-view identity. Actual denotations and outcomes remain independent.','explanatory':'Notation, intuition and examples explain the source without supplying semantic authority.','deferred':'Authority scope and the no-effect claim ceiling remain explicit obligations; this candidate does not discharge them.'}
 for row in selected_clauses(doc):
  cid='COORD-'+str(len(clauses)+1).zfill(3);disp=row['disposition']
  clauses.append({'clause_id':cid,'source_selector':row['source_selector'],'excerpt_sha256':r.digest(row['excerpt'].encode()),'start_character':row['start_character'],'disposition':disp,'forms':row['forms'],'roles':['definition'] if disp=='encoded' else ['explanation-example'] if disp=='explanatory' else ['unresolved'],'formal_statement':row['formula'],'rationale':reasons[disp]})
  links.append({'unit_id':row['unit_id'],'clause_id':cid,'end_character':row['start_character']+len(row['excerpt']),'excerpt':row['excerpt']})
 deps=[source_ref(snap,name) for name in context['direct_dependency_names']]
 primary=next(x['clause_id'] for x in clauses if x['source_selector']=='/voices/scientific_formal/normative_statement');req=required_populations()
 populations=[{'population_id':'POP-REQ-'+name,'carrier':carrier,'predicate_ref':None,'requirement':'required','statement':formula,'scope':SCOPE,'rationale':'Independent witnesses exercise optional anchor combinations, empty and multiple boundary links, material and nonmaterial changes, stable source-view identity and noninferential outcomes.','review_ref':None} for name,(carrier,formula) in req.items()]+[{'population_id':'POP-UNRESOLVED-'+name,'carrier':args[0],'predicate_ref':name if len(args)==1 else None,'requirement':'unresolved','statement':None,'scope':SCOPE,'rationale':'Actual populations and owner or consumer denotations remain unresolved.','review_ref':None} for name,args in SIGNATURE.items()]
 core={'source':source,'interpretation_id':'interpretation:CoordinationContext-frame-optional-boundaries-identity-v1','profile_ref':'profile:definition-assurance-partial-types-logic-v1','scope':SCOPE,'semantic_status':'candidate','source_fidelity':'pending','logic_features':['first-order','equality'],'declarations':declarations(),'clauses':clauses,'depends_on':deps,'relations':[],'assumptions':[],'populations':populations}
 findings=[{'finding_id':'COORD-FINDING-'+str(i+1).zfill(3),'description':loss,'selectors':['/voices/scientific_formal/normative_statement','/voices/scientific_formal/formal_expression','/scope/applicability'],'status':'unresolved','owner_route':'role:definition-owner with coordination, product, project, goal, bounded-context, identity, source-policy and lifecycle owners'} for i,loss in enumerate(LOSSES)]
 packet={'schema_version':'definition-assurance-correspondence/v1-candidate','upstream_schema_sha256':r.digest((IMPL/'schemas/input-envelope.json').read_bytes()),'authority_effect':'none','source_selection':'current','inventory_policy':'all-nonempty-string-leaves-in-voices-boundaries-scope-and-claim-ceiling/v1','interpretation':core,'source_units':units,'correspondence':links,'dependency_links':[{'clause_id':primary,'dependency_ref':dep,'kind':'semantic-use','rationale':'Separately qualified dependency; no accepted common carrier or whole prior theory is imported.'} for dep in deps],'dependency_closure':{'status':'unresolved','review_ref':None,'unresolved_notes':LOSSES},'assumption_links':[],'source_precedence':{'normative_voice':'/voices/scientific_formal','conflicts':findings,'review_ref':None},'review_packet':{'instances':[{'case_id':'optional-anchors-and-independent-boundary-versions','scenario':'Eight contexts cover all optional Project and Goal combinations, empty and multiple explicit boundary links, material changes of each anchor and two source-view changes.','expected_interpretation':'Necessary frame and identity declarations hold without actual ownership, execution permission, reference resolution or source fidelity inferred.','rationale':'Provide nonvacuous cardinality, independence and identity witnesses.','related_clause_ids':[primary]}],'counterexamples':[{'case_id':'material-product-change-in-place','scenario':'A selected material change records a different desired Product but nominates the original context as successor.','expected_interpretation':'The distinct-successor and matched desired-anchor conditions fail.','rationale':'Desired state is independent of the successor reference.','related_clause_ids':[primary]}],'known_losses':LOSSES,'review_status':'pending','review_ref':None}}
 account=co.check(packet,snap,required_dependencies=[x['version_ref'] for x in deps],required_conflicts=[x['finding_id'] for x in findings]);assert account['character_accounting_complete']
 for name,value in [('t.json',{'schema_version':'definition-assurance-input/v1-candidate','kind':'interpretation','authority_effect':'none','payload':core}),('correspondence.json',packet),('static-ir.json',ir.compile_interpretation(core,snap)),('correspondence-check.json',account)]:put(name,value)
 queries=query_specs();put('query-policy.json',{'authority_effect':'none','queries':queries,'targets_not_assumptions':True,'whole_definition_proof_claimed':False})
 obligations=[]
 for clause in clauses:
  if clause['disposition']=='explanatory':continue
  selector=clause['source_selector'];targets=['Context-not-ActualSourceFidelity','Context-not-ActualWholeProof']
  if selector in ['/voices/scientific_formal/normative_statement','/voices/scientific_formal/formal_expression','/scope/applicability']:
   targets+=['Context-not-ActualOwnerQualification','Context-not-ActualProductResolution','Context-not-ActualProjectResolution','Context-not-ActualGoalResolution','Context-not-ActualPurposeStability','Context-not-ActualIndependentBoundaryOwnership','AnchorChange-not-ActualMaterialityCorrectness','AnchorChange-not-ActualSuccessorCreation']
  if selector.startswith('/boundaries/') or selector.startswith('/scope/exclusions/') or '/boundary_conditions/' in selector:targets+=['Context-not-ActualExecutionPermission','Context-not-ActualOwnerAuthorization']
  if selector=='/boundaries/1':targets+=['SourceViewChange-not-ActualIdentityPreservation','SourceViewChange-not-ActualViewAuthenticity']
  if selector=='/claim_ceiling':targets+=['Context-not-ActualCreation','Context-not-ActualOwnerAuthorization','Context-not-ActualExecutionPermission']
  if selector.endswith('/testable_conditions/0'):targets+=['Context-not-ActualProductResolution']
  if selector.endswith('/testable_conditions/1'):targets+=['Context-not-ActualProjectResolution','Context-not-ActualGoalResolution']
  if selector.endswith('/testable_conditions/2'):targets+=['Context-not-ActualBoundedContextResolution','Context-not-ActualIndependentBoundaryOwnership']
  link=next(x for x in links if x['clause_id']==clause['clause_id'])
  for target in targets:
   assert target in {q['query_id'] for q in queries}
   obligations.append({'source':source,'selector':selector,'start_character':clause['start_character'],'end_character':link['end_character'],'excerpt':link['excerpt'],'excerpt_sha256':clause['excerpt_sha256'],'clause_id':clause['clause_id'],'query_id':target,'selected_in_T':False,'necessary_declaration_guard_in_T':clause['disposition']=='encoded','actual_outcome_target_in_T':False})
 put('source-query-obligation.json',{'authority_effect':'none','obligations':obligations,'source_fidelity':'pending','whole_definition_proof_claimed':False})
 counts={'source_units':len(units),'mapped_clauses':len(clauses),**{name+'_clauses':sum(x['disposition']==name for x in clauses) for name in ['encoded','explanatory','deferred']},'declarations':len(core['declarations']),'required_populations':len(req),'unresolved_populations':len(SIGNATURE),'direct_semantic_uses':len(deps),'countermodel_queries':len(queries)}
 put('denominator.json',counts)
 put('clause-analysis.json',{'authority_effect':'none','source':source,'encoded_spans':counts['encoded_clauses'],'unique_encoded_source_formula_values':len({json.dumps(x['formal_statement'],sort_keys=True) for x in clauses if x['disposition']=='encoded'}),'primitive_theory_formulas':len(THEORY),'known_losses':LOSSES,'actual_outcome_queries_assumed_in_T':False,'whole_prior_theories_imported':False,'source_precedence_reviewed':False,'mechanized_proof':False,'zero_bounded_context_links_allowed':True,'owner_principals_need_not_differ':True,'materiality_is_not_all_anchor_differences':True,'optional_project_and_goal_independent':True})
 put('comparison-selection.json',{'authority_effect':'none','separate_qualified_sources':deps,'selected_refs':[{'path':x['path'],'sha256':x['sha256']} for x in deps]+context['sources'],'comparison_assembled_into_primary_T':False,'source_precedence_reviewed':False,'external_context_refs':context['external_sources'],'source_fidelity':'pending','claim_ceiling':'Necessary frame, cardinality, independence and identity declarations only; actual ownership, reference resolution, creation, execution permission, fidelity and whole proof remain pending.'})
 c.validate(json.loads((UNIT/'t.json').read_bytes()),'interpretation');unchanged(context['sources']);external_current(context)
 print(json.dumps(counts,indent=2,sort_keys=True))
if __name__=='__main__':main()
