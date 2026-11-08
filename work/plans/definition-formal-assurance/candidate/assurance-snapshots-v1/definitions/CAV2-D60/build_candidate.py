"""Exact CAV2-D60 Project Goal cardinality,lifecycle,membership and durable identity declarations."""
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
SCOPE='scope:candidate:CAV2-D60-Project-Goal-cardinality-lifecycle-membership-durable-identity-v1'
SORTS=['ProjectReference','IdentityReference','NameReference','PurposeReference','ScopeReference','ExclusionsCollectionReference','OwnerRoutesCollectionReference','GoalCollectionReference','EvidenceIndexReference','PurposeConnectionsCollectionReference','LifecycleStateReference','ChallengeRouteReference','GoalReference','MemberReference','ProductReference','ChangeReference','Token']
CONSTANTS={'EMPTY':'Token','PROPOSED':'LifecycleStateReference','ACTIVE':'LifecycleStateReference','DRAFT':'LifecycleStateReference'}
PROJECT_FIELDS={'projectIdentity':'IdentityReference','projectName':'NameReference','projectPurpose':'PurposeReference','projectScope':'ScopeReference','projectExclusions':'ExclusionsCollectionReference','projectOwnerRoutes':'OwnerRoutesCollectionReference','projectGoals':'GoalCollectionReference','projectEvidenceIndex':'EvidenceIndexReference','projectPurposeConnections':'PurposeConnectionsCollectionReference','projectLifecycleState':'LifecycleStateReference','projectChallengeRoute':'ChallengeRouteReference'}
GOAL_FIELDS={'goalMember':'MemberReference','goalLifecycleState':'LifecycleStateReference'}
PRODUCT_FIELDS={'productIdentity':'IdentityReference'}
CHANGE_FIELDS={'changeProject':'ProjectReference','changeBeforeIdentity':'IdentityReference','changeAfterIdentity':'IdentityReference'}
GROUPS=[(PROJECT_FIELDS,'ProjectReference'),(GOAL_FIELDS,'GoalReference'),(PRODUCT_FIELDS,'ProductReference'),(CHANGE_FIELDS,'ChangeReference')]
FUNCTIONS={n:([carrier],sort) for fields,carrier in GROUPS for n,sort in fields.items()};HANDLES={sort:sort[0].lower()+sort[1:]+'Handle' for sort in SORTS if sort!='Token'};FUNCTIONS.update({n:([sort],'Token') for sort,n in HANDLES.items()})
PROJECT_EXCLUDED=['ProjectIsProductDeclared','ProjectIsGoalDeclared','ProjectIsMethodDeclared','ProjectIsProjectSpaceDeclared','ProjectIsRepositoryDeclared','ProjectIsDirectoryDeclared','ProjectIsPlanDeclared','ProjectIsWorkPackDeclared','ProjectIsSessionDeclared','ProjectIsTeamDeclared','ProjectIsAuthorityEnvelopeDeclared','ProjectIsAuthorityDeclared','DirectoryPlacementCreatesProjectIdentityDeclared','MembershipCreatesProjectIdentityDeclared','CoordinationInheritsArtifactAuthorityDeclared','ProjectMembershipGrantsWorkPermissionDeclared','ProjectIdentityGrantsExecutionDeclared','ProjectAdmissionActivatesLifecycleDeclared']
CHANGE_EXCLUDED=['ChangeLabelGrantsAuthorityDeclared','FolderChangeCreatesProjectIdentityDeclared','ChangeGrantsWorkPermissionDeclared']
PROJECT_ACTUAL=['IdentityFidelity','NameFidelity','PurposeFidelity','ScopeFidelity','ExclusionsFidelity','OwnerRoutesValidity','GoalReferenceCompleteness','GoalStateFidelity','MembershipFidelity','EvidenceIndexFidelity','PurposeConnectionsFidelity','LifecycleFidelity','ChallengeRouteValidity','Durability','CoordinationAdequacy','Instantiation','Activation','OwnerAuthorization','ExternalWorkPermission','SourceFidelity','WholeProof']
CHANGE_ACTUAL=['SubjectFidelity','BeforeIdentityFidelity','AfterIdentityFidelity','ChangeKindFidelity','IdentityContinuity','Authority','Proof']
PRIMARY=[('Project','ProjectReference',PROJECT_EXCLUDED,PROJECT_ACTUAL),('Change','ChangeReference',CHANGE_EXCLUDED,CHANGE_ACTUAL)]
FLAGS={'Project':['ProjectApplicable','ProjectInScopeDeclared','ProjectDurableCoordinationIdentityDeclared','ProjectCoordinatesTowardPurposeDeclared'],'Change':['ChangeApplicable','ChangeInScopeDeclared']}
MEMBER_KINDS=['Goal','Owner','Evidence','Decision','Artifact','Work','Lifecycle'];CHANGE_KINDS=['Plan','Task','Folder','Tool','Implementation']
SIGNATURE={}
for prefix,sort,excluded,actual in PRIMARY:SIGNATURE.update({n:[sort] for n in FLAGS[prefix]+excluded+[prefix+'Actual'+n for n in actual]})
for sort in SORTS:
 if sort not in [x[1] for x in PRIMARY]+['Token']:SIGNATURE[sort+'Declared']=[sort]
for fields,carrier in GROUPS:SIGNATURE.update({n+'BindingDeclared':[carrier,sort] for n,sort in fields.items()})
SIGNATURE.update({'GoalCollectionContainsDeclared':['GoalCollectionReference','GoalReference'],'ProjectGoalReferenceDeclared':['ProjectReference','GoalReference'],'ProjectMemberDeclared':['ProjectReference','MemberReference'],'ExplicitProjectMembershipRelationDeclared':['ProjectReference','MemberReference'],'MembershipTransfersArtifactAuthorityDeclared':['ProjectReference','MemberReference']})
SIGNATURE.update({'MemberIs'+n+'Declared':['MemberReference'] for n in MEMBER_KINDS});SIGNATURE.update({'ChangeIs'+n+'Declared':['ChangeReference'] for n in CHANGE_KINDS})
def iff(a,z):return {'op':'iff','left':a,'right':z}
P=var('p');G=var('g');M=var('m');X=var('x');D=var('d')
MAP={'ProjectReference':'ProjectApplicable','ChangeReference':'ChangeApplicable'}
def member(sort):return MAP.get(sort,sort+'Declared')
def guard(sort,value):return both(pred(member(sort),value),neg(eq(fn(HANDLES[sort],value),const('EMPTY'))))
def exact(fields,value):return both(*[both(guard(sort,fn(n,value)),allof([(sort,'binding')],iff(pred(n+'BindingDeclared',value,'binding'),eq(var('binding'),fn(n,value))))) for n,sort in fields.items()])
def selected(sort,name,z):return allof([(sort,name)],implies(pred(member(sort),name),z))
def eligible(prefix,sort,name):return allof([(sort,name)],iff(pred(prefix+'Applicable',name),pred(prefix+'InScopeDeclared',name)))
PAPP=pred('ProjectApplicable',P);XAPP=pred('ChangeApplicable',X);GOAL_REF=pred('ProjectGoalReferenceDeclared',P,G)
ROOT_RULE=both(*[guard('LifecycleStateReference',const(n)) for n in ['PROPOSED','ACTIVE','DRAFT']],eligible('Project','ProjectReference','p'),selected('ProjectReference','p',both(guard('ProjectReference',P),exact(PROJECT_FIELDS,P),pred('ProjectDurableCoordinationIdentityDeclared',P),pred('ProjectCoordinatesTowardPurposeDeclared',P))))
GOAL_RULE=selected('ProjectReference','p',both(exists([('GoalReference','g')],GOAL_REF),allof([('GoalReference','g')],both(iff(GOAL_REF,pred('GoalCollectionContainsDeclared',fn('projectGoals',P),G)),implies(GOAL_REF,both(guard('GoalReference',G),exact(GOAL_FIELDS,G),pred('MemberIsGoalDeclared',fn('goalMember',G)),pred('ProjectMemberDeclared',P,fn('goalMember',G))))))))
def has_goal(state):return exists([('GoalReference','g')],both(GOAL_REF,eq(fn('goalLifecycleState',G),const(state))))
LIFECYCLE_RULE=selected('ProjectReference','p',both(implies(eq(fn('projectLifecycleState',P),const('PROPOSED')),either(has_goal('DRAFT'),has_goal('ACTIVE'))),implies(eq(fn('projectLifecycleState',P),const('ACTIVE')),has_goal('ACTIVE'))))
MEMBERSHIP_RULE=selected('ProjectReference','p',allof([('MemberReference','m')],both(iff(pred('ProjectMemberDeclared',P,M),pred('ExplicitProjectMembershipRelationDeclared',P,M)),implies(pred('ProjectMemberDeclared',P,M),guard('MemberReference',M)))))
IDENTITY_SEPARATION_RULE=both(selected('ProductReference','d',both(guard('ProductReference',D),exact(PRODUCT_FIELDS,D))),selected('ProjectReference','p',allof([('ProductReference','d')],implies(pred('ProductReferenceDeclared',D),neg(eq(fn('projectIdentity',P),fn('productIdentity',D)))))))
IDENTITY_CONTINUITY_RULE=both(eligible('Change','ChangeReference','x'),selected('ChangeReference','x',both(guard('ChangeReference',X),exact(CHANGE_FIELDS,X),either(*[pred('ChangeIs'+n+'Declared',X) for n in CHANGE_KINDS]),eq(fn('changeBeforeIdentity',X),fn('projectIdentity',fn('changeProject',X))),eq(fn('changeAfterIdentity',X),fn('changeBeforeIdentity',X)))))
BOUNDARIES=both(*[selected(sort,name,both(*[neg(pred(n,name)) for n in excluded])) for (prefix,sort,excluded,actual),name in zip(PRIMARY,['p','x'])],selected('ProjectReference','p',allof([('MemberReference','m')],implies(pred('ProjectMemberDeclared',P,M),neg(pred('MembershipTransfersArtifactAuthorityDeclared',P,M))))))
THEORY={'root':ROOT_RULE,'Goal-reference-cardinality-and-membership':GOAL_RULE,'lifecycle-Goal-condition':LIFECYCLE_RULE,'explicit-membership':MEMBERSHIP_RULE,'Project-Product-ID-separation':IDENTITY_SEPARATION_RULE,'identity-through-change':IDENTITY_CONTINUITY_RULE,'boundaries':BOUNDARIES}
LOSSES=[
'Exact C29 Project Definition and scoped source admission do not accept this translation,instantiate or activate a Project or authorize coordinated work.',
'Eleven Project fields nominate typed identities,scope,collections,index,connections,state and challenge route;actual contents and role meanings remain pending.',
'Every selected Project has at least one declared Goal reference;empty Goal collections fail independently of Project lifecycle.',
'Project Goal references are exactly nominated collection membership;all referenced Goals have typed state/member nominations and explicit coordination membership.',
'Proposed Project requires a draft or active nominated Goal;active Project requires an active nominated Goal. These are necessary conditions,not automatic activation.',
'A nonactive Project can retain nonactive Goal references;an active Project can also reference draft Goals while one active Goal exists.',
'Goal draft/active labels are separately qualified Project-scope state nominations;the prior Goal whole theory and real lifecycle are not imported.',
'Coordination Goal-reference membership is not automatically Goal ownership. CAV2-D59 one-Project ownership needs an accepted cross-definition map before joint assurance.',
'Membership declarations have exact explicit relation counterparts and declared nonempty member references;actual membership fidelity remains independent.',
'Owner,evidence,decision,artifact,work,lifecycle and Goal member-role tags provide scoped examples without inventing exhaustive or disjoint partitions.',
'Owner-route collections,evidence index and purpose connections are explicit specifications;no unstated member cardinality or actual resolution is inferred.',
'Project IDs differ from all nominated declared Product IDs;actual identity lineage,alias resolution and global uniqueness require accepted maps.',
'Selected plan/task/folder/tool/implementation changes nominate a selected Project and preserve its declared identity before and after the change.',
'Selected change kinds are inclusive;untagged changes are outside this selected change scope and do not fabricate a recognized change.',
'Nominal before/after equality does not prove real persistence,history order,rename lineage or implementation migration.',
'Directory placement,membership,admission and coordination labels do not create identity,activate lifecycle or inherit authority.',
'Coordinated artifact membership does not transfer its authority;independent external authorization remains possible.',
'Project is not Product,Goal,Method,project space,repository,directory,plan,work pack,session,team or authority envelope.',
'Source-body candidate labels and current C29/C30/C31 positive overlays retain separate scopes;no actual Project activation is inferred.',
'Legacy declared Project Markdown4522-4602 now differs;content-exact4852-4932 observation preserves provenance without rewriting selectors.',
'Legacy Project and identity-decision JSON moved while retaining exact hashes;observed paths do not transfer private or legacy authority.',
'Project/v1,Goal/v1,identity graph,evidence index,owner routes,purpose connections and lifecycle consumers need accepted field/member/state/identity maps.',
'Source authority-scope and migration claim ceiling remain deferred;complete character accounting does not accept source fidelity.',
'Independent partial T/I witnesses are not a shared denotation,whole translation,whole proof or completed original episode.'
]
def required_populations():
 def w(sort,name,z):return exists([(sort,name)],both(pred(member(sort),name),z))
 result={'Project':('ProjectReference',w('ProjectReference','p',PAPP)),'OutsideProject':('ProjectReference',exists([('ProjectReference','p')],neg(PAPP))),'ProposedDraftGoal':('ProjectReference',w('ProjectReference','p',both(eq(fn('projectLifecycleState',P),const('PROPOSED')),has_goal('DRAFT')))),'ProposedActiveGoal':('ProjectReference',w('ProjectReference','p',both(eq(fn('projectLifecycleState',P),const('PROPOSED')),has_goal('ACTIVE')))),'ActiveProjectActiveGoal':('ProjectReference',w('ProjectReference','p',both(eq(fn('projectLifecycleState',P),const('ACTIVE')),has_goal('ACTIVE')))),'ActiveProjectAdditionalDraftGoal':('ProjectReference',w('ProjectReference','p',both(eq(fn('projectLifecycleState',P),const('ACTIVE')),has_goal('DRAFT')))),'NonactiveProjectNonactiveGoal':('ProjectReference',w('ProjectReference','p',both(neg(eq(fn('projectLifecycleState',P),const('PROPOSED'))),neg(eq(fn('projectLifecycleState',P),const('ACTIVE'))),exists([('GoalReference','g')],both(GOAL_REF,neg(eq(fn('goalLifecycleState',G),const('ACTIVE'))),neg(eq(fn('goalLifecycleState',G),const('DRAFT')))))))),'MultipleGoalReferences':('GoalReference',exists([('ProjectReference','p'),('GoalReference','g'),('GoalReference','other')],both(PAPP,GOAL_REF,pred('ProjectGoalReferenceDeclared',P,'other'),neg(eq(G,var('other')))))),'UnusedDeclaredGoal':('GoalReference',w('GoalReference','g',neg(exists([('ProjectReference','p')],both(PAPP,GOAL_REF))))),'IndependentOwnerAuthorization':('ProjectReference',w('ProjectReference','p',pred('ProjectActualOwnerAuthorization',P))),'ActiveWithoutActualActivation':('ProjectReference',w('ProjectReference','p',both(eq(fn('projectLifecycleState',P),const('ACTIVE')),neg(pred('ProjectActualActivation',P))))),'ProjectWithoutActualOutcomes':('ProjectReference',w('ProjectReference','p',both(*[neg(pred('ProjectActual'+n,P)) for n in PROJECT_ACTUAL]))),'ProductIDCounterpart':('ProductReference',w('ProductReference','d',pred('ProductReferenceDeclared',D))),'Change':('ChangeReference',w('ChangeReference','x',XAPP)),'OutsideChange':('ChangeReference',exists([('ChangeReference','x')],neg(XAPP))),'ChangeWithoutActualContinuity':('ChangeReference',w('ChangeReference','x',neg(pred('ChangeActualIdentityContinuity',X))))}
 for kind in MEMBER_KINDS:result['MemberKind'+kind]=('MemberReference',exists([('ProjectReference','p'),('MemberReference','m')],both(PAPP,pred('ProjectMemberDeclared',P,M),pred('MemberIs'+kind+'Declared',M))))
 for kind in CHANGE_KINDS:result['IdentityPreserving'+kind+'Change']=('ChangeReference',w('ChangeReference','x',pred('ChangeIs'+kind+'Declared',X)))
 return result
def declarations():return [{'kind':'sort','symbol_id':n,'scope':SCOPE,'domain_policy':'nonempty'} for n in SORTS]+[{'kind':'constant','symbol_id':n,'scope':SCOPE,'result_sort':sort} for n,sort in CONSTANTS.items()]+[{'kind':'total-function','symbol_id':n,'scope':SCOPE,'argument_sorts':args,'result_sort':result,'definedness_policy':None} for n,(args,result) in FUNCTIONS.items()]+[{'kind':'predicate' if len(args)==1 else 'relation','symbol_id':n,'scope':SCOPE,'argument_sorts':args} for n,args in SIGNATURE.items()]
def query_specs():
 rows=[]
 for (prefix,sort,excluded,names),vn in zip(PRIMARY,['p','x']):
  value=var(vn);app=pred(prefix+'Applicable',value)
  for n in names:
   active=prefix=='Project' and n in ['Activation','GoalStateFidelity','OwnerAuthorization'];scope=both(app,eq(fn('projectLifecycleState',value),const('ACTIVE'))) if active else app;target=pred(prefix+'Actual'+n,value);rows.append({'query_id':prefix+'-not-Actual'+n,'target':allof([(sort,vn)],implies(scope,target)),'witness_condition':exists([(sort,vn)],both(scope,neg(target))),'source_condition':'declared-active-Project' if active else 'selected-'+prefix.lower(),'selected_in_T':False,'source_fidelity':'pending'})
 return rows
def selected_clauses(doc):
 chosen={'/voices/scientific_formal/normative_statement':(both(*THEORY.values()),['genus-differentia']),'/voices/scientific_formal/formal_expression':(both(ROOT_RULE,GOAL_RULE,LIFECYCLE_RULE,MEMBERSHIP_RULE),['axiomatic-implicit']),'/scope/applicability':(both(ROOT_RULE,MEMBERSHIP_RULE),['operational']),'/scope/exclusions/0':(BOUNDARIES,['operational']),'/voices/scientific_formal/boundary_conditions/0':(LIFECYCLE_RULE,['operational']),'/voices/scientific_formal/boundary_conditions/1':(LIFECYCLE_RULE,['operational']),'/voices/scientific_formal/boundary_conditions/2':(BOUNDARIES,['operational']),'/voices/scientific_formal/testable_conditions/0':(both(ROOT_RULE,GOAL_RULE),['operational']),'/voices/scientific_formal/testable_conditions/1':(IDENTITY_SEPARATION_RULE,['operational']),'/voices/scientific_formal/testable_conditions/2':(MEMBERSHIP_RULE,['operational']),'/boundaries/0':(BOUNDARIES,['operational']),'/boundaries/1':(BOUNDARIES,['operational'])}
 texts=dict(co.string_leaves(doc));rows=[]
 for unit in co.inventory(doc):
  sel=unit['selector'];formula,forms=chosen.get(sel,(None,['unresolved']));disp='encoded' if formula is not None else 'explanatory' if sel.startswith('/voices/') and any(x in sel for x in ['/domain_context/','/plain_language/','/notation/']) else 'deferred';rows.append({'source_selector':sel,'start_character':0,'excerpt':texts[sel],'formula':formula,'forms':forms,'disposition':disp,'unit_id':unit['unit_id']})
 return rows
def main():
 context=json.loads((UNIT/'context.json').read_bytes());unchanged(context['sources']);external_current(context);snap=snapshot();r.verify(snap,ROOT);source=context['source_selection'];doc=co.source_document(snap,source);units=co.inventory(doc);clauses=[];links=[]
 reasons={'encoded':'Necessary Project eleven-field,nonempty Goal reference,conditional Goal-state,membership,identity continuity and authority-separation declarations;actual outcomes remain independent.','explanatory':'Notation,plain-language intuition and domain examples remain explanatory;no actual Project identity,activation or work permission inferred.','deferred':'The authority-scope map and candidate migration ceiling remain explicit unresolved source obligations.'}
 for row in selected_clauses(doc):
  cid='PRJ-'+str(len(clauses)+1).zfill(3);disp=row['disposition'];clauses.append({'clause_id':cid,'source_selector':row['source_selector'],'excerpt_sha256':r.digest(row['excerpt'].encode()),'start_character':row['start_character'],'disposition':disp,'forms':row['forms'],'roles':['definition'] if disp=='encoded' else ['explanation-example'] if disp=='explanatory' else ['unresolved'],'formal_statement':row['formula'],'rationale':reasons[disp]});links.append({'unit_id':row['unit_id'],'clause_id':cid,'end_character':row['start_character']+len(row['excerpt']),'excerpt':row['excerpt']})
 deps=[source_ref(snap,n) for n in context['direct_dependency_names']];primary=next(x['clause_id'] for x in clauses if 'genus-differentia' in x['forms']);req=required_populations()
 populations=[{'population_id':'POP-REQ-'+n,'carrier':carrier,'predicate_ref':None,'requirement':'required','statement':z,'scope':SCOPE,'rationale':'Independent proposed/active/nonactive Projects,Goal-state alternatives,explicit typed membership and five identity-preserving change populations.','review_ref':None} for n,(carrier,z) in req.items()]+[{'population_id':'POP-UNRESOLVED-'+n,'carrier':args[0],'predicate_ref':n if len(args)==1 else None,'requirement':'unresolved','statement':None,'scope':SCOPE,'rationale':'Actual universe,source fidelity and owner/consumer denotations remain pending.','review_ref':None} for n,args in SIGNATURE.items()]
 core={'source':source,'interpretation_id':'interpretation:CAV2-D60-Project-Goal-cardinality-lifecycle-membership-durable-identity-v1','profile_ref':'profile:definition-assurance-partial-types-logic-v1','scope':SCOPE,'semantic_status':'candidate','source_fidelity':'pending','logic_features':['first-order','equality'],'declarations':declarations(),'clauses':clauses,'depends_on':deps,'relations':[],'assumptions':[],'populations':populations}
 findings=[{'finding_id':'PRJ-FINDING-'+str(i+1).zfill(3),'description':z,'selectors':['/voices/scientific_formal/normative_statement','/voices/scientific_formal/formal_expression','/scope/applicability'],'status':'unresolved','owner_route':'role:definition-owner with Project,Goal,identity,membership and lifecycle owners'} for i,z in enumerate(LOSSES)]
 packet={'schema_version':'definition-assurance-correspondence/v1-candidate','upstream_schema_sha256':r.digest((IMPL/'schemas/input-envelope.json').read_bytes()),'authority_effect':'none','source_selection':'current','inventory_policy':'all-nonempty-string-leaves-in-voices-boundaries-scope-and-claim-ceiling/v1','interpretation':core,'source_units':units,'correspondence':links,'dependency_links':[{'clause_id':primary,'dependency_ref':dep,'kind':'semantic-use','rationale':'Separately qualified semantic dependency;no prior whole theory or accepted source/consumer map imported.'} for dep in deps],'dependency_closure':{'status':'unresolved','review_ref':None,'unresolved_notes':LOSSES},'assumption_links':[],'source_precedence':{'normative_voice':'/voices/scientific_formal','conflicts':findings,'review_ref':None},'review_packet':{'instances':[{'case_id':'Project-Goal-state-membership-and-five-change-kinds','scenario':'Four selected Projects include proposed draft/active Goal cases,an active Project with an active and extra draft Goal,and a nonactive Project with a nonactive Goal. Every Goal reference has explicit coordination membership. Five selected change kinds preserve identity.','expected_interpretation':'Necessary declarations hold without real lifecycle,Goal ownership,Project activation,authority or fidelity inferred.','rationale':'Independent Goal cardinality,lifecycle conditions,membership and identity continuity.','related_clause_ids':[primary]}],'counterexamples':[{'case_id':'nonempty-Goal-collection-handle-with-no-members','scenario':'A selected Project still nominates a nonempty collection handle but every declared Goal reference is removed.','expected_interpretation':'The source at-least-one-Goal condition fails.','rationale':'A reference doesnot prove required collection contents.','related_clause_ids':[primary]}],'known_losses':LOSSES,'review_status':'pending','review_ref':None}}

 account=co.check(packet,snap,required_dependencies=[x['version_ref'] for x in deps],required_conflicts=[x['finding_id'] for x in findings]);assert account['character_accounting_complete']
 for n,z in [('t.json',{'schema_version':'definition-assurance-input/v1-candidate','kind':'interpretation','authority_effect':'none','payload':core}),('correspondence.json',packet),('static-ir.json',ir.compile_interpretation(core,snap)),('correspondence-check.json',account)]:put(n,z)
 queries=query_specs();put('query-policy.json',{'authority_effect':'none','queries':queries,'targets_not_assumptions':True,'whole_definition_proof_claimed':False});query_ids={x['query_id'] for x in queries};obligations=[]
 for clause in clauses:
  if clause['disposition']=='explanatory':continue
  targets=['Project-not-ActualSourceFidelity','Project-not-ActualExternalWorkPermission']
  if clause['source_selector'] in ['/voices/scientific_formal/normative_statement','/voices/scientific_formal/formal_expression']:targets+=['Project-not-ActualDurability','Project-not-ActualActivation','Project-not-ActualOwnerAuthorization']
  if clause['source_selector'].startswith('/voices/scientific_formal/boundary_conditions/'):targets+=['Project-not-ActualGoalStateFidelity','Project-not-ActualLifecycleFidelity']
  if clause['source_selector']=='/voices/scientific_formal/testable_conditions/0':targets+=['Project-not-ActualGoalReferenceCompleteness','Project-not-ActualOwnerRoutesValidity','Project-not-ActualChallengeRouteValidity']
  if clause['source_selector']=='/voices/scientific_formal/testable_conditions/1':targets+=['Project-not-ActualIdentityFidelity']
  if clause['source_selector']=='/voices/scientific_formal/testable_conditions/2':targets+=['Project-not-ActualMembershipFidelity']
  if clause['source_selector']=='/boundaries/1':targets+=['Project-not-ActualOwnerAuthorization','Change-not-ActualAuthority']
  link=next(x for x in links if x['clause_id']==clause['clause_id'])
  for target in targets:
   assert target in query_ids,target
   obligations.append({'source':source,'selector':clause['source_selector'],'start_character':clause['start_character'],'end_character':link['end_character'],'excerpt':link['excerpt'],'excerpt_sha256':clause['excerpt_sha256'],'clause_id':clause['clause_id'],'query_id':target,'selected_in_T':False,'necessary_declaration_guard_in_T':clause['disposition']=='encoded','actual_outcome_target_in_T':False})
 put('source-query-obligation.json',{'authority_effect':'none','obligations':obligations,'source_fidelity':'pending','whole_definition_proof_claimed':False})
 counts={'source_units':len(units),'mapped_clauses':len(clauses),**{n+'_clauses':sum(x['disposition']==n for x in clauses) for n in ['encoded','explanatory','deferred']},'declarations':len(core['declarations']),'required_populations':len(req),'unresolved_populations':len(SIGNATURE),'direct_semantic_uses':len(deps),'countermodel_queries':len(queries)};put('denominator.json',counts)
 put('clause-analysis.json',{'authority_effect':'none','source':source,'encoded_spans':counts['encoded_clauses'],'unique_encoded_source_formula_values':len({json.dumps(x['formal_statement'],sort_keys=True) for x in clauses if x['disposition']=='encoded'}),'primitive_theory_formulas':len(THEORY),'known_losses':LOSSES,'tuple':'eleven-exact-typed-Project-coordinates','Goal_collection':'exact-declared-collection-membership-and-at-least-one-Goal','lifecycle':'proposed-draft-or-active-Goal-and-active-active-Goal-necessary-conditions','membership':'exact-explicit-coordination-membership-not-accepted-Goal-ownership','identity':'Project-Product-ID-separation-and-identity-preservation-through-five-selected-change-kinds','authority':'no-directory-membership-coordination-or-admission-created-authority-or-activation','actual_outcome_queries_assumed_in_T':False,'whole_prior_theories_imported':False,'source_precedence_reviewed':False,'mechanized_proof':False})
 put('comparison-selection.json',{'authority_effect':'none','separate_qualified_sources':deps,'selected_refs':[{'path':x['path'],'sha256':x['sha256']} for x in deps]+context['sources'],'comparison_assembled_into_primary_T':False,'source_precedence_reviewed':False,'external_context_refs':context['external_sources'],'source_fidelity':'pending','claim_ceiling':'Necessary Project cardinality,lifecycle,membership and durable-identity declarations only;actual Project/Goal meanings,activation,authorization,fidelity and whole proof pending.'})
 c.validate(json.loads((UNIT/'t.json').read_bytes()),'interpretation');unchanged(context['sources']);external_current(context);print(json.dumps(counts,indent=2,sort_keys=True))
if __name__=='__main__':main()
