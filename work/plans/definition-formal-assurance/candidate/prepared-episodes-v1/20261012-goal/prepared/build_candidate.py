"""Exact CAV2-D59 Goal single Project,universal required evidence and owner lifecycle declarations."""
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
SCOPE='scope:candidate:CAV2-D59-Goal-one-Project-universal-evidence-owner-lifecycle-v1'
SORTS=['GoalReference','IdentityReference','ProjectReference','OutcomeReference','RationaleReference','ScopeReference','ExclusionsCollectionReference','OwnerRouteReference','OwnerReference','SuccessConditionCollectionReference','EvidenceRequirementsCollectionReference','LifecycleStateReference','ConditionReference','EvidenceReference','TransitionReference','Token']
CONSTANTS={'EMPTY':'Token','ACHIEVED':'LifecycleStateReference'}
GOAL_FIELDS={'goalIdentity':'IdentityReference','goalProject':'ProjectReference','goalOutcome':'OutcomeReference','goalRationale':'RationaleReference','goalScope':'ScopeReference','goalExclusions':'ExclusionsCollectionReference','goalOwnerRoute':'OwnerRouteReference','goalSuccessConditions':'SuccessConditionCollectionReference','goalEvidenceRequirements':'EvidenceRequirementsCollectionReference','goalLifecycleState':'LifecycleStateReference'}
ROUTE_FIELDS={'routeOwner':'OwnerReference'}
ACHIEVEMENT_FIELDS={'goalAchievementTransition':'TransitionReference'}
CURRENT_FIELDS={'goalCurrentTransition':'TransitionReference'}
TRANSITION_FIELDS={'transitionGoal':'GoalReference','transitionOwner':'OwnerReference','transitionFrom':'LifecycleStateReference','transitionTo':'LifecycleStateReference','transitionEvidence':'EvidenceReference'}
GROUPS=[(GOAL_FIELDS,'GoalReference'),(ROUTE_FIELDS,'OwnerRouteReference'),(ACHIEVEMENT_FIELDS,'GoalReference'),(CURRENT_FIELDS,'GoalReference'),(TRANSITION_FIELDS,'TransitionReference')]
FUNCTIONS={n:([carrier],sort) for fields,carrier in GROUPS for n,sort in fields.items()};HANDLES={sort:sort[0].lower()+sort[1:]+'Handle' for sort in SORTS if sort!='Token'};FUNCTIONS.update({n:([sort],'Token') for sort,n in HANDLES.items()})
GOAL_EXCLUDED=['GoalIsIntentDeclared','GoalIsProjectDeclared','GoalIsProductDeclared','GoalIsMethodDeclared','GoalIsPlanDeclared','GoalIsTaskDeclared','GoalIsWorkPackDeclared','GoalIsEvidenceDeclared','GoalIsDeadlineDeclared','GoalIsExecutionAuthorityDeclared','GoalProjectIdentityMergedDeclared','ActivityAutomaticallyAchievesGoalDeclared','ProgressAutomaticallyAchievesGoalDeclared','ValidationAutomaticallyAchievesGoalDeclared','AgentAssertionAutomaticallyAchievesGoalDeclared','GoalMembershipGrantsWorkPermissionDeclared','GoalIdentityGrantsExecutionDeclared']
TRANSITION_EXCLUDED=['TransitionLabelProvesOwnerAuthorizationDeclared','TransitionEvidencePerformsOwnerDecisionDeclared','TransitionGrantsWorkPermissionDeclared']
GOAL_ACTUAL=['IdentityFidelity','ProjectMembershipFidelity','OutcomeFidelity','RationaleFidelity','ScopeFidelity','OwnerRouteValidity','ConditionCompleteness','EvidenceRequirementsFidelity','RequiredEvidenceAdequacy','OwnerAuthorization','LifecycleFidelity','Achievement','Durability','ExternalWorkPermission','SourceFidelity','WholeProof']
TRANSITION_ACTUAL=['SubjectFidelity','OwnerRecordValidity','OwnerAuthorization','EvidenceAdequacy','LifecycleChangeFidelity','HistoricalOrderFidelity','Authority','Proof']
PRIMARY=[('Goal','GoalReference',GOAL_EXCLUDED,GOAL_ACTUAL),('Transition','TransitionReference',TRANSITION_EXCLUDED,TRANSITION_ACTUAL)]
FLAGS={'Goal':['GoalApplicable','GoalInScopeDeclared','GoalDurableAttributableOutcomeDeclared','GoalDesiredFutureOutcomeDeclared','GoalAchievedDeclared','GoalHasCurrentTransitionDeclared','GoalHasDeadlineDeclared'],'Transition':['TransitionApplicable','TransitionInScopeDeclared','TransitionLifecycleChangeDeclared']}
SIGNATURE={}
for prefix,sort,excluded,actual in PRIMARY:SIGNATURE.update({n:[sort] for n in FLAGS[prefix]+excluded+[prefix+'Actual'+n for n in actual]})
for sort in SORTS:
 if sort not in [x[1] for x in PRIMARY]+['Token']:SIGNATURE[sort+'Declared']=[sort]
for fields,carrier in GROUPS:SIGNATURE.update({n+'BindingDeclared':[carrier,sort] for n,sort in fields.items()})
SIGNATURE.update({'CollectionRequiredConditionDeclared':['SuccessConditionCollectionReference','ConditionReference'],'GoalRequiredConditionDeclared':['GoalReference','ConditionReference'],'AdequateEvidenceDeclared':['GoalReference','ConditionReference','EvidenceReference'],'EvidenceSupportsConditionDeclared':['EvidenceReference','GoalReference','ConditionReference'],'EvidenceResolvedDeclared':['EvidenceReference'],'OwnerRecordsTransitionDeclared':['OwnerReference','TransitionReference'],'EvidencePerformsGoalAchievementDecisionDeclared':['EvidenceReference','GoalReference'],'PassingCheckAchievesGoalDeclared':['EvidenceReference','GoalReference']})
def iff(a,z):return {'op':'iff','left':a,'right':z}
G=var('g');T=var('t');C=var('c');E=var('e')
MAP={'GoalReference':'GoalApplicable','TransitionReference':'TransitionApplicable'}
def member(sort):return MAP.get(sort,sort+'Declared')
def guard(sort,value):return both(pred(member(sort),value),neg(eq(fn(HANDLES[sort],value),const('EMPTY'))))
def exact(fields,value):return both(*[both(guard(sort,fn(n,value)),allof([(sort,'binding')],iff(pred(n+'BindingDeclared',value,'binding'),eq(var('binding'),fn(n,value))))) for n,sort in fields.items()])
def selected(sort,name,z):return allof([(sort,name)],implies(pred(member(sort),name),z))
def eligible(prefix,sort,name):return allof([(sort,name)],iff(pred(prefix+'Applicable',name),pred(prefix+'InScopeDeclared',name)))
GAPP=pred('GoalApplicable',G);TAPP=pred('TransitionApplicable',T);OWNER=fn('routeOwner',fn('goalOwnerRoute',G));REQUIRED=pred('GoalRequiredConditionDeclared',G,C)
def adequate(goal,condition,evidence):return both(guard('EvidenceReference',evidence),pred('AdequateEvidenceDeclared',goal,condition,evidence),pred('EvidenceSupportsConditionDeclared',evidence,goal,condition),pred('EvidenceResolvedDeclared',evidence))
ALL_EVIDENCE=allof([('ConditionReference','c')],implies(REQUIRED,exists([('EvidenceReference','e')],adequate(G,C,E))))
ROOT_RULE=both(guard('LifecycleStateReference',const('ACHIEVED')),eligible('Goal','GoalReference','g'),selected('GoalReference','g',both(guard('GoalReference',G),exact(GOAL_FIELDS,G),exact(ROUTE_FIELDS,fn('goalOwnerRoute',G)),pred('GoalDurableAttributableOutcomeDeclared',G),pred('GoalDesiredFutureOutcomeDeclared',G),iff(pred('GoalAchievedDeclared',G),eq(fn('goalLifecycleState',G),const('ACHIEVED'))))))
CONDITION_RULE=selected('GoalReference','g',allof([('ConditionReference','c')],both(iff(REQUIRED,pred('CollectionRequiredConditionDeclared',fn('goalSuccessConditions',G),C)),implies(REQUIRED,guard('ConditionReference',C)))))
EVIDENCE_RULE=selected('GoalReference','g',allof([('ConditionReference','c'),('EvidenceReference','e')],implies(both(REQUIRED,pred('AdequateEvidenceDeclared',G,C,E)),adequate(G,C,E))))
TG=fn('transitionGoal',T);TO=fn('transitionOwner',T);TE=fn('transitionEvidence',T)
TRANSITION_RULE=both(eligible('Transition','TransitionReference','t'),selected('TransitionReference','t',both(guard('TransitionReference',T),exact(TRANSITION_FIELDS,T),pred('TransitionLifecycleChangeDeclared',T),neg(eq(fn('transitionFrom',T),fn('transitionTo',T))),eq(TO,fn('routeOwner',fn('goalOwnerRoute',TG))),pred('OwnerRecordsTransitionDeclared',TO,T),pred('EvidenceResolvedDeclared',TE))))
AT=fn('goalAchievementTransition',G)
ACHIEVEMENT_RULE=selected('GoalReference','g',implies(pred('GoalAchievedDeclared',G),both(ALL_EVIDENCE,exact(ACHIEVEMENT_FIELDS,G),eq(fn('transitionGoal',AT),G),eq(fn('transitionOwner',AT),OWNER),eq(fn('transitionTo',AT),const('ACHIEVED')),pred('OwnerRecordsTransitionDeclared',OWNER,AT))))
CT=fn('goalCurrentTransition',G)
CURRENT_RULE=selected('GoalReference','g',implies(pred('GoalHasCurrentTransitionDeclared',G),both(exact(CURRENT_FIELDS,G),eq(fn('transitionGoal',CT),G),eq(fn('transitionTo',CT),fn('goalLifecycleState',G)))))
BOUNDARIES=both(*[selected(sort,name,both(*[neg(pred(n,name)) for n in excluded])) for (prefix,sort,excluded,actual),name in zip(PRIMARY,['g','t'])],selected('GoalReference','g',allof([('EvidenceReference','e')],implies(pred('EvidenceReferenceDeclared',E),both(neg(pred('EvidencePerformsGoalAchievementDecisionDeclared',E,G)),neg(pred('PassingCheckAchievesGoalDeclared',E,G)))))))
THEORY={'root':ROOT_RULE,'required-condition-membership':CONDITION_RULE,'adequate-support':EVIDENCE_RULE,'owner-lifecycle-transition':TRANSITION_RULE,'achievement-only-if':ACHIEVEMENT_RULE,'selected-current-transition':CURRENT_RULE,'boundaries':BOUNDARIES}
LOSSES=[
'Exact C29 Goal Definition admission and scoped source use do not accept this translation,instantiate or achieve a Goal or authorize work.',
'Ten Goal fields are explicit typed nominations;Goal,Project,Product,Method,Intent,plan,task,work pack,evidence,deadline and authority retain separate roles.',
'Exact Project binding is single-valued per selected Goal;multiple Goals for the same Project and independent Goal/Project owners are not prohibited.',
'Goal identity,outcome,rationale,scope,exclusions,owner route and collection references require accepted denotations beyond nonempty labels.',
'Declared required conditions are exactly the nominated collection membership;actual completeness of all real required conditions remains pending.',
'The source does not state minimum collection cardinalities;empty declared condition collections remain possible while nonempty/multiple-condition populations are requested independently.',
'Achievement implies adequate declared support for every declared required condition;one insufficient condition blocks the declared achieved state.',
'Evidence may support multiple conditions and multiple evidence items may support one condition;no one-to-one evidence assignment is invented.',
'Declared support,resolution and adequacy do not prove actual evidence truth,sufficiency,retention or owner acceptance.',
'Goal owner route resolves to a typed owner nomination;actual route validity and owner authorization remain independent.',
'Selected lifecycle-change records have distinct from/to state nominations,owner-recorded evidence and the Goal owner;no noop change is invented.',
'Historical transitions need not equal the current Goal state;only an explicitly selected current transition must agree with it.',
'A declared achieved Goal nominates an owner-recorded transition to achieved;pending Goals leave unused achievement/current-transition fields unbound.',
'Evidence readiness alone does not select achieved or fabricate a transition;the only-if guard is not a sufficient-condition converse.',
'Achieved state/reference classification is a declaration-level nomination,not actual Goal achievement or complete lifecycle fidelity.',
'Activity,progress,validation,PASS,evidence possession and agent assertions do not perform the Goal owner achievement decision.',
'Goal membership,identity and transition labels do not grant work/execution authority;independent owner authorization or external work permission remains possible.',
'Source-body candidate admission labels and historical chain evidence remain separate from C29 exact scoped source admission and later C30/C31 positive effects.',
'Legacy declared Goal Markdown lines4443-4521 differ at the relocated current file;exact selected bytes at4773-4851 preserve the admitted digest without rewriting the selector.',
'The legacy Goal whole JSON also moved and retains its bound digest;content identity does not transfer legacy/private authority or prove Goal achievement.',
'Goal/v1,Project/identity graph,assessment,evidence and lifecycle consumers need accepted Project,condition,owner,evidence and transition maps.',
'Complete source accounting and finite T/I models do not prove shared denotations,source fidelity,whole translation,whole proof or episode completion.'
]
def required_populations():
 def w(sort,name,z):return exists([(sort,name)],both(pred(member(sort),name),z))
 return {'Goal':('GoalReference',w('GoalReference','g',GAPP)),'OutsideGoal':('GoalReference',exists([('GoalReference','g')],neg(GAPP))),'DeclaredAchievedGoal':('GoalReference',w('GoalReference','g',pred('GoalAchievedDeclared',G))),'DeclaredPendingGoal':('GoalReference',w('GoalReference','g',neg(pred('GoalAchievedDeclared',G)))),'MultipleGoalsSameProject':('GoalReference',exists([('GoalReference','g'),('GoalReference','other')],both(GAPP,pred('GoalApplicable','other'),neg(eq(G,var('other'))),eq(fn('goalProject',G),fn('goalProject','other'))))),'MultipleRequiredConditions':('ConditionReference',exists([('GoalReference','g'),('ConditionReference','c'),('ConditionReference','other')],both(GAPP,REQUIRED,pred('GoalRequiredConditionDeclared',G,'other'),neg(eq(C,var('other')))))),'EmptyDeclaredConditions':('GoalReference',w('GoalReference','g',neg(exists([('ConditionReference','c')],REQUIRED)))),'EvidenceReadyPendingGoal':('GoalReference',w('GoalReference','g',both(neg(pred('GoalAchievedDeclared',G)),ALL_EVIDENCE,exists([('ConditionReference','c')],REQUIRED)))),'SharedEvidenceAcrossConditions':('EvidenceReference',exists([('GoalReference','g'),('ConditionReference','c'),('ConditionReference','other'),('EvidenceReference','e')],both(GAPP,REQUIRED,pred('GoalRequiredConditionDeclared',G,'other'),neg(eq(C,var('other'))),adequate(G,C,E),adequate(G,var('other'),E)))),'AlternativeEvidenceForCondition':('EvidenceReference',exists([('GoalReference','g'),('ConditionReference','c'),('EvidenceReference','e'),('EvidenceReference','other')],both(GAPP,REQUIRED,neg(eq(E,var('other'))),adequate(G,C,E),adequate(G,C,var('other'))))),'AchievedWithoutActualAchievement':('GoalReference',w('GoalReference','g',both(pred('GoalAchievedDeclared',G),neg(pred('GoalActualAchievement',G))))),'IndependentOwnerAuthorization':('GoalReference',w('GoalReference','g',pred('GoalActualOwnerAuthorization',G))),'GoalWithoutActualOutcomes':('GoalReference',w('GoalReference','g',both(*[neg(pred('GoalActual'+n,G)) for n in GOAL_ACTUAL]))),'Transition':('TransitionReference',w('TransitionReference','t',TAPP)),'OutsideTransition':('TransitionReference',exists([('TransitionReference','t')],neg(TAPP))),'HistoricalTransitionDifferentFromCurrentState':('TransitionReference',w('TransitionReference','t',neg(eq(fn('transitionTo',T),fn('goalLifecycleState',TG))))),'SelectedCurrentTransition':('GoalReference',w('GoalReference','g',pred('GoalHasCurrentTransitionDeclared',G))),'NoSelectedCurrentTransition':('GoalReference',w('GoalReference','g',neg(pred('GoalHasCurrentTransitionDeclared',G)))),'TransitionWithoutActualOwnerAuthorization':('TransitionReference',w('TransitionReference','t',neg(pred('TransitionActualOwnerAuthorization',T)))),'OwnerEvidenceDifferentFromConditionEvidence':('EvidenceReference',exists([('GoalReference','g'),('ConditionReference','c'),('EvidenceReference','e')],both(GAPP,pred('GoalAchievedDeclared',G),REQUIRED,adequate(G,C,E),neg(eq(E,fn('transitionEvidence',AT))))))}
def declarations():return [{'kind':'sort','symbol_id':n,'scope':SCOPE,'domain_policy':'nonempty'} for n in SORTS]+[{'kind':'constant','symbol_id':n,'scope':SCOPE,'result_sort':sort} for n,sort in CONSTANTS.items()]+[{'kind':'total-function','symbol_id':n,'scope':SCOPE,'argument_sorts':args,'result_sort':result,'definedness_policy':None} for n,(args,result) in FUNCTIONS.items()]+[{'kind':'predicate' if len(args)==1 else 'relation','symbol_id':n,'scope':SCOPE,'argument_sorts':args} for n,args in SIGNATURE.items()]
def query_specs():
 rows=[]
 for (prefix,sort,excluded,names),vn in zip(PRIMARY,['g','t']):
  value=var(vn);app=pred(prefix+'Applicable',value)
  for n in names:
   conditioned=prefix=='Goal' and n in ['Achievement','RequiredEvidenceAdequacy','OwnerAuthorization'];scope=both(app,pred('GoalAchievedDeclared',value)) if conditioned else app;target=pred(prefix+'Actual'+n,value);label='declared-achieved-Goal' if conditioned else 'selected-'+prefix.lower();rows.append({'query_id':prefix+'-not-Actual'+n,'target':allof([(sort,vn)],implies(scope,target)),'witness_condition':exists([(sort,vn)],both(scope,neg(target))),'source_condition':label,'selected_in_T':False,'source_fidelity':'pending'})
 return rows
def selected_clauses(doc):
 chosen={'/voices/scientific_formal/normative_statement':(both(*THEORY.values()),['genus-differentia']),'/voices/scientific_formal/formal_expression':(both(ROOT_RULE,CONDITION_RULE,ACHIEVEMENT_RULE),['axiomatic-implicit']),'/scope/applicability':(ROOT_RULE,['operational']),'/scope/exclusions/0':(BOUNDARIES,['operational']),'/scope/exclusions/1':(BOUNDARIES,['operational']),'/voices/scientific_formal/boundary_conditions/0':(ROOT_RULE,['operational']),'/voices/scientific_formal/boundary_conditions/1':(BOUNDARIES,['operational']),'/voices/scientific_formal/testable_conditions/0':(ROOT_RULE,['operational']),'/voices/scientific_formal/testable_conditions/1':(TRANSITION_RULE,['operational']),'/voices/scientific_formal/testable_conditions/2':(BOUNDARIES,['operational']),'/boundaries/0':(BOUNDARIES,['operational']),'/boundaries/1':(BOUNDARIES,['operational'])}
 texts=dict(co.string_leaves(doc));rows=[]
 for unit in co.inventory(doc):
  sel=unit['selector'];formula,forms=chosen.get(sel,(None,['unresolved']));disp='encoded' if formula is not None else 'explanatory' if sel.startswith('/voices/') and any(x in sel for x in ['/domain_context/','/plain_language/','/notation/']) else 'deferred';rows.append({'source_selector':sel,'start_character':0,'excerpt':texts[sel],'formula':formula,'forms':forms,'disposition':disp,'unit_id':unit['unit_id']})
 return rows
def main():
 context=json.loads((UNIT/'context.json').read_bytes());unchanged(context['sources']);external_current(context);snap=snapshot();r.verify(snap,ROOT);source=context['source_selection'];doc=co.source_document(snap,source);units=co.inventory(doc);clauses=[];links=[]
 reasons={'encoded':'Necessary Goal ten-field,exact-Project,universal declared required-condition evidence and owner-lifecycle declarations. Actual achievement,evidence adequacy,owner authorization and lifecycle fidelity remain independent.','explanatory':'Notation,plain-language intuition and domain examples are explanatory;no actual Goal achievement or work permission inferred.','deferred':'The authority-scope map and candidate migration ceiling remain explicit unresolved source obligations.'}
 for row in selected_clauses(doc):
  cid='GOL-'+str(len(clauses)+1).zfill(3);disp=row['disposition'];clauses.append({'clause_id':cid,'source_selector':row['source_selector'],'excerpt_sha256':r.digest(row['excerpt'].encode()),'start_character':row['start_character'],'disposition':disp,'forms':row['forms'],'roles':['definition'] if disp=='encoded' else ['explanation-example'] if disp=='explanatory' else ['unresolved'],'formal_statement':row['formula'],'rationale':reasons[disp]});links.append({'unit_id':row['unit_id'],'clause_id':cid,'end_character':row['start_character']+len(row['excerpt']),'excerpt':row['excerpt']})
 deps=[source_ref(snap,n) for n in context['direct_dependency_names']];primary=next(x['clause_id'] for x in clauses if 'genus-differentia' in x['forms']);req=required_populations()
 populations=[{'population_id':'POP-REQ-'+n,'carrier':carrier,'predicate_ref':None,'requirement':'required','statement':z,'scope':SCOPE,'rationale':'Independent pending/achieved,shared-Project,condition/evidence alternatives,owner/history and current-transition populations.','review_ref':None} for n,(carrier,z) in req.items()]+[{'population_id':'POP-UNRESOLVED-'+n,'carrier':args[0],'predicate_ref':n if len(args)==1 else None,'requirement':'unresolved','statement':None,'scope':SCOPE,'rationale':'Actual universe,source fidelity and owner/consumer denotations remain pending.','review_ref':None} for n,args in SIGNATURE.items()]
 core={'source':source,'interpretation_id':'interpretation:CAV2-D59-Goal-one-Project-universal-evidence-owner-lifecycle-v1','profile_ref':'profile:definition-assurance-partial-types-logic-v1','scope':SCOPE,'semantic_status':'candidate','source_fidelity':'pending','logic_features':['first-order','equality'],'declarations':declarations(),'clauses':clauses,'depends_on':deps,'relations':[],'assumptions':[],'populations':populations}
 findings=[{'finding_id':'GOL-FINDING-'+str(i+1).zfill(3),'description':z,'selectors':['/voices/scientific_formal/normative_statement','/voices/scientific_formal/formal_expression','/scope/applicability'],'status':'unresolved','owner_route':'role:definition-owner with Goal,Project,evidence,owner-route and lifecycle owners'} for i,z in enumerate(LOSSES)]
 packet={'schema_version':'definition-assurance-correspondence/v1-candidate','upstream_schema_sha256':r.digest((IMPL/'schemas/input-envelope.json').read_bytes()),'authority_effect':'none','source_selection':'current','inventory_policy':'all-nonempty-string-leaves-in-voices-boundaries-scope-and-claim-ceiling/v1','interpretation':core,'source_units':units,'correspondence':links,'dependency_links':[{'clause_id':primary,'dependency_ref':dep,'kind':'semantic-use','rationale':'Separately qualified semantic dependency;no prior whole theory or accepted source/consumer map imported.'} for dep in deps],'dependency_closure':{'status':'unresolved','review_ref':None,'unresolved_notes':LOSSES},'assumption_links':[],'source_precedence':{'normative_voice':'/voices/scientific_formal','conflicts':findings,'review_ref':None},'review_packet':{'instances':[{'case_id':'pending-and-achieved-Goals-owner-history-universal-evidence','scenario':'Three Goals have exact Project bindings;two share a Project. A pending Goal has ready evidence but no achievement transition. A declared achieved Goal has two required conditions with shared/alternative evidence and an owner-recorded current transition. Its earlier historical transition differs from current state.','expected_interpretation':'Necessary declarations hold without real Goal achievement,owner authorization,evidence adequacy,condition completeness or work permission inferred.','rationale':'Exactly-one Project per Goal,all declared condition coverage and owner lifecycle record remain distinct from actual outcomes.','related_clause_ids':[primary]}],'counterexamples':[{'case_id':'one-required-condition-with-no-adequate-evidence','scenario':'Every evidence alternative for one declared required condition is removed while the Goal still declares achieved.','expected_interpretation':'Universal required-condition coverage fails.','rationale':'A partial success cannot satisfy every required condition.','related_clause_ids':[primary]}],'known_losses':LOSSES,'review_status':'pending','review_ref':None}}

 account=co.check(packet,snap,required_dependencies=[x['version_ref'] for x in deps],required_conflicts=[x['finding_id'] for x in findings]);assert account['character_accounting_complete']
 for n,z in [('t.json',{'schema_version':'definition-assurance-input/v1-candidate','kind':'interpretation','authority_effect':'none','payload':core}),('correspondence.json',packet),('static-ir.json',ir.compile_interpretation(core,snap)),('correspondence-check.json',account)]:put(n,z)
 queries=query_specs();put('query-policy.json',{'authority_effect':'none','queries':queries,'targets_not_assumptions':True,'whole_definition_proof_claimed':False});query_ids={x['query_id'] for x in queries};obligations=[]
 for clause in clauses:
  if clause['disposition']=='explanatory':continue
  targets=['Goal-not-ActualSourceFidelity','Goal-not-ActualExternalWorkPermission']
  if clause['source_selector'] in ['/voices/scientific_formal/normative_statement','/voices/scientific_formal/formal_expression']:targets+=['Goal-not-ActualAchievement','Goal-not-ActualRequiredEvidenceAdequacy','Goal-not-ActualOwnerAuthorization']
  if clause['source_selector'] in ['/boundaries/1','/voices/scientific_formal/boundary_conditions/0']:targets+=['Goal-not-ActualProjectMembershipFidelity']
  if clause['source_selector']=='/voices/scientific_formal/boundary_conditions/1':targets+=['Transition-not-ActualOwnerRecordValidity']
  if clause['source_selector']=='/voices/scientific_formal/testable_conditions/0':targets+=['Goal-not-ActualConditionCompleteness','Goal-not-ActualEvidenceRequirementsFidelity']
  if clause['source_selector']=='/voices/scientific_formal/testable_conditions/1':targets+=['Transition-not-ActualOwnerAuthorization','Transition-not-ActualEvidenceAdequacy','Goal-not-ActualLifecycleFidelity']
  if clause['source_selector']=='/voices/scientific_formal/testable_conditions/2':targets+=['Goal-not-ActualOwnerAuthorization']
  link=next(x for x in links if x['clause_id']==clause['clause_id'])
  for target in targets:
   assert target in query_ids,target
   obligations.append({'source':source,'selector':clause['source_selector'],'start_character':clause['start_character'],'end_character':link['end_character'],'excerpt':link['excerpt'],'excerpt_sha256':clause['excerpt_sha256'],'clause_id':clause['clause_id'],'query_id':target,'selected_in_T':False,'necessary_declaration_guard_in_T':clause['disposition']=='encoded','actual_outcome_target_in_T':False})
 put('source-query-obligation.json',{'authority_effect':'none','obligations':obligations,'source_fidelity':'pending','whole_definition_proof_claimed':False})
 counts={'source_units':len(units),'mapped_clauses':len(clauses),**{n+'_clauses':sum(x['disposition']==n for x in clauses) for n in ['encoded','explanatory','deferred']},'declarations':len(core['declarations']),'required_populations':len(req),'unresolved_populations':len(SIGNATURE),'direct_semantic_uses':len(deps),'countermodel_queries':len(queries)};put('denominator.json',counts)
 put('clause-analysis.json',{'authority_effect':'none','source':source,'encoded_spans':counts['encoded_clauses'],'unique_encoded_source_formula_values':len({json.dumps(x['formal_statement'],sort_keys=True) for x in clauses if x['disposition']=='encoded'}),'primitive_theory_formulas':len(THEORY),'known_losses':LOSSES,'tuple':'ten-exact-typed-Goal-coordinate-nominations','Project':'exact-single-valued-Project-binding-with-multiple-Goals-per-Project-permitted','conditions':'exact-declared-collection-membership-and-universal-required-condition-evidence','achievement':'only-if-every-declared-required-condition-supported-and-owner-recorded-transition-to-achieved','lifecycle':'owner-evidenced-distinct-state-change-and-conditional-current-state-selection-not-global-history-equality','authority':'no-evidence/PASS/progress/agent-assertion-achievement-or-execution-authority','actual_outcome_queries_assumed_in_T':False,'whole_prior_theories_imported':False,'source_precedence_reviewed':False,'mechanized_proof':False})
 put('comparison-selection.json',{'authority_effect':'none','separate_qualified_sources':deps,'selected_refs':[{'path':x['path'],'sha256':x['sha256']} for x in deps]+context['sources'],'comparison_assembled_into_primary_T':False,'source_precedence_reviewed':False,'external_context_refs':context['external_sources'],'source_fidelity':'pending','claim_ceiling':'Necessary Goal,Project,universal declared condition-evidence and owner-lifecycle declarations only;actual achievement,adequacy,authorization,completeness,fidelity and whole proof pending.'})
 c.validate(json.loads((UNIT/'t.json').read_bytes()),'interpretation');unchanged(context['sources']);external_current(context);print(json.dumps(counts,indent=2,sort_keys=True))
if __name__=='__main__':main()
