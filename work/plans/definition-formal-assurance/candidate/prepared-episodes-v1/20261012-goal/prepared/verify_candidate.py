"""Finite Goal/project/condition/evidence/owner-history models and rejection controls."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(name):return json.loads((b.UNIT/name).read_bytes())
def setfn(m,n,arg,value):next(x for x in m['functions'][n] if x['args']==[arg])['value']=value
def getfn(m,n,arg):return next(x['value'] for x in m['functions'][n] if x['args']==[arg])
def refresh(m):
 for fields,carrier in b.GROUPS:
  for n in fields:m['predicates'][n+'BindingDeclared']=[[x['args'][0],x['value']] for x in m['functions'][n]]
def base_model():
 ds={sort:[sort[0].lower()+sort[1:]+'0',sort[0].lower()+sort[1:]+'1',sort[0].lower()+sort[1:]+'2',sort[0].lower()+sort[1:]+'Outside'] for sort in b.SORTS}
 ds.update(GoalReference=['g0','g1','g2','gOutside'],ProjectReference=['p0','p1','p2','pOutside'],OwnerRouteReference=['r0','r1','r2','rOutside'],OwnerReference=['o0','o1','o2','oOutside'],ConditionReference=['c0','c1','c2','c3','cOutside'],EvidenceReference=['e0','e1','e2','e3','eOutside'],TransitionReference=['t0','t1','tOutside'],LifecycleStateReference=['planned','active','achieved','stateOutside'],Token=['empty','ref','other']);maps={}
 def table(n,values):maps[n]=lambda x:values.get(x,ds[b.FUNCTIONS[n][1]][-1])
 for n,sort in b.GOAL_FIELDS.items():table(n,{'g'+str(i):ds[sort][i] for i in range(3)})
 table('goalProject',{'g0':'p0','g1':'p1','g2':'p0'});table('goalLifecycleState',{'g0':'planned','g1':'achieved','g2':'planned'});table('routeOwner',{'r0':'o0','r1':'o1','r2':'o2'});table('goalAchievementTransition',{'g1':'t1'});table('goalCurrentTransition',{'g1':'t1'})
 table('transitionGoal',{'t0':'g1','t1':'g1'});table('transitionOwner',{'t0':'o1','t1':'o1'});table('transitionFrom',{'t0':'planned','t1':'active'});table('transitionTo',{'t0':'active','t1':'achieved'});table('transitionEvidence',{'t0':'e3','t1':'e3'})
 for sort,n in b.HANDLES.items():maps[n]=lambda x:'ref'
 assert set(maps)==set(b.FUNCTIONS)
 funcs={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(ds[z] for z in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};preds={n:[] for n in b.SIGNATURE}
 for sort in b.SORTS:
  if sort not in [x[1] for x in b.PRIMARY]+['Token']:preds[sort+'Declared']=[[x] for x in ds[sort] if not x.endswith('Outside')]
 for n in ['GoalApplicable','GoalInScopeDeclared','GoalDurableAttributableOutcomeDeclared','GoalDesiredFutureOutcomeDeclared']:preds[n]=[['g0'],['g1'],['g2']]
 preds['GoalAchievedDeclared']=[['g1']];preds['GoalHasCurrentTransitionDeclared']=[['g1']]
 for n in b.FLAGS['Transition']:preds[n]=[['t0'],['t1']]
 collections=ds['SuccessConditionCollectionReference'];preds['CollectionRequiredConditionDeclared']=[[collections[0],'c0'],[collections[1],'c1'],[collections[1],'c2']];preds['GoalRequiredConditionDeclared']=[['g0','c0'],['g1','c1'],['g1','c2']]
 preds['AdequateEvidenceDeclared']=[['g0','c0','e0'],['g1','c1','e1'],['g1','c2','e1'],['g1','c2','e2'],['g1','c3','e2']];preds['EvidenceSupportsConditionDeclared']=[['e0','g0','c0'],['e1','g1','c1'],['e1','g1','c2'],['e2','g1','c2'],['e2','g1','c3']];preds['EvidenceResolvedDeclared']=[['e0'],['e1'],['e2'],['e3']];preds['OwnerRecordsTransitionDeclared']=[['o1','t0'],['o1','t1']];preds['GoalActualOwnerAuthorization']=[['g2']]
 m={'domains':ds,'constants':{'EMPTY':'empty','ACHIEVED':'achieved'},'functions':funcs,'predicates':preds};refresh(m);return m
def controls():
 rows=[]
 def add(name,mutation=lambda m:None,T=True,I=True,error=None):
  m=base_model();mutation(m);rows.append({'case_id':name,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 def change(m,n,arg,value):setfn(m,n,arg,value);refresh(m)
 add('pending-achieved-empty-condition-Goals-and-owner-evidenced-history')
 add('no-selected-Goals-transitions',lambda m:m['predicates'].update({prefix+suffix:[] for prefix,sort,e,a in b.PRIMARY for suffix in ['Applicable','InScopeDeclared']}),I=False)
 add('no-independent-owner-authorization',lambda m:m['predicates'].update(GoalActualOwnerAuthorization=[]),I=False)
 def pending_only(m):
  setfn(m,'goalLifecycleState','g1','planned');refresh(m);m['predicates'].update(GoalAchievedDeclared=[],GoalHasCurrentTransitionDeclared=[],TransitionApplicable=[],TransitionInScopeDeclared=[])
 add('pending-Goals-without-fabricated-transitions',pending_only,I=False)
 for (prefix,sort,excluded,names),target in zip(b.PRIMARY,['g1','t1']):
  for n in names:add('independently-supported-'+prefix+'-Actual'+n,lambda m,prefix=prefix,n=n,target=target:m['predicates'].update({prefix+'Actual'+n:[list(x) for x in sorted({tuple(x) for x in m['predicates'][prefix+'Actual'+n]}|{(target,)})]}),I=None)
  for n in excluded:
   add('selected-excluded-'+n,lambda m,n=n,target=target:m['predicates'][n].append([target]),T=False,I=None)
   outside=base_model()['domains'][sort][-1];add('outside-excluded-'+n,lambda m,n=n,outside=outside:m['predicates'][n].append([outside]))
 add('pending-unused-achievement-binding-absent',lambda m:m['predicates'].update(goalAchievementTransitionBindingDeclared=[x for x in m['predicates']['goalAchievementTransitionBindingDeclared'] if x[0]!='g0']))
 add('pending-unused-current-transition-binding-absent',lambda m:m['predicates'].update(goalCurrentTransitionBindingDeclared=[x for x in m['predicates']['goalCurrentTransitionBindingDeclared'] if x[0]!='g0']))
 add('unused-transition-handle-empty',lambda m:setfn(m,b.HANDLES['TransitionReference'],'tOutside','empty'))
 add('unused-condition-handle-empty',lambda m:setfn(m,b.HANDLES['ConditionReference'],'cOutside','empty'))
 add('Goal-may-have-deadline-without-being-deadline',lambda m:m['predicates']['GoalHasDeadlineDeclared'].append(['g0']))
 add('two-Goals-share-Project',lambda m:None)
 add('historical-transition-does-not-equal-current-state',lambda m:None)
 add('evidence-readiness-does-not-achieve-pending-Goal',lambda m:None)
 add('empty-declared-condition-collection-does-not-auto-achieve',lambda m:None)
 add('one-evidence-item-supports-multiple-conditions',lambda m:None)
 add('nonrequired-condition-support-permitted',lambda m:None)
 add('remove-one-alternative-adequate-evidence-still-sufficient',lambda m:m['predicates']['AdequateEvidenceDeclared'].remove(['g1','c2','e2']),I=False)
 add('all-evidence-for-one-required-condition-missing',lambda m:m['predicates'].update(AdequateEvidenceDeclared=[x for x in m['predicates']['AdequateEvidenceDeclared'] if x[:2]!=['g1','c2']]),T=False,I=None)
 add('one-adequacy-label-lacks-support',lambda m:m['predicates']['EvidenceSupportsConditionDeclared'].remove(['e1','g1','c1']),T=False,I=None)
 add('required-evidence-unresolved',lambda m:m['predicates']['EvidenceResolvedDeclared'].remove(['e1']),T=False,I=None)
 add('owner-transition-evidence-unresolved',lambda m:m['predicates']['EvidenceResolvedDeclared'].remove(['e3']),T=False,I=None)
 add('owner-does-not-record-achievement-transition',lambda m:m['predicates']['OwnerRecordsTransitionDeclared'].remove(['o1','t1']),T=False,I=None)
 add('owner-does-not-record-historical-change',lambda m:m['predicates']['OwnerRecordsTransitionDeclared'].remove(['o1','t0']),T=False,I=None)
 add('second-required-condition-undeclared',lambda m:m['predicates']['ConditionReferenceDeclared'].remove(['c2']),T=False,I=None)
 add('required-condition-collection-link-omitted',lambda m:m['predicates']['GoalRequiredConditionDeclared'].remove(['g1','c2']),T=False,I=None)
 add('extra-required-condition-not-in-collection',lambda m:m['predicates']['GoalRequiredConditionDeclared'].append(['g1','c3']),T=False,I=None)
 add('Goal-project-second-binding-rejected',lambda m:m['predicates']['goalProjectBindingDeclared'].append(['g1','p0']),T=False,I=None)
 add('achieved-label-state-mismatch',lambda m:m['predicates']['GoalAchievedDeclared'].remove(['g1']),T=False,I=None)
 add('pending-label-cannot-fabricate-achievement',lambda m:m['predicates']['GoalAchievedDeclared'].append(['g0']),T=False,I=None)
 for n,row in [('EvidencePerformsGoalAchievementDecisionDeclared',['e1','g1']),('PassingCheckAchievesGoalDeclared',['e0','g0'])]:add('selected-evidence-decision-overclaim-'+n,lambda m,n=n,row=row:m['predicates'][n].append(row),T=False,I=None)
 add('outside-Goal-evidence-decision-claim-not-scoped',lambda m:m['predicates']['EvidencePerformsGoalAchievementDecisionDeclared'].append(['eOutside','gOutside']))
 for n,arg,value in [('goalAchievementTransition','g1','t0'),('goalCurrentTransition','g1','t0'),('transitionGoal','t1','g0'),('transitionOwner','t1','o0'),('transitionTo','t1','active'),('transitionFrom','t0','active')]:add('wrong-exact-coordinate-'+n,lambda m,n=n,arg=arg,value=value:change(m,n,arg,value),T=False,I=None)
 for n,arg in [('GoalDurableAttributableOutcomeDeclared','g1'),('GoalDesiredFutureOutcomeDeclared','g1'),('TransitionLifecycleChangeDeclared','t1')]:add('missing-'+n,lambda m,n=n,arg=arg:m['predicates'][n].remove([arg]),T=False,I=None)
 targets=[(b.GOAL_FIELDS,'g1'),(b.ROUTE_FIELDS,'r1'),(b.ACHIEVEMENT_FIELDS,'g1'),(b.CURRENT_FIELDS,'g1'),(b.TRANSITION_FIELDS,'t1')]
 for fields,arg in targets:
  for n,sort in fields.items():
   add('missing-exact-binding-'+n,lambda m,n=n,arg=arg:m['predicates'].update({n+'BindingDeclared':[x for x in m['predicates'][n+'BindingDeclared'] if x[0]!=arg]}),T=False,I=None)
   value=getfn(base_model(),n,arg);alt=next(x for x in base_model()['domains'][sort] if x!=value);add('conflicting-exact-binding-'+n,lambda m,n=n,arg=arg,alt=alt:m['predicates'][n+'BindingDeclared'].append([arg,alt]),T=False,I=None)
   add('undeclared-selected-target-'+n,lambda m,sort=sort,value=value:m['predicates'][b.member(sort)].remove([value]),T=False,I=None)
 selected={sort:values[0] for sort,values in base_model()['domains'].items() if sort!='Token'}
 for sort,n in b.HANDLES.items():add('empty-selected-handle-'+sort,lambda m,n=n,value=selected[sort]:setfn(m,n,value,'empty'),T=False,I=None)
 for name,mutate,code in [('empty-domain',lambda m:m['domains'].update(GoalReference=[]),'empty-or-malformed-domain'),('missing-domain',lambda m:m['domains'].pop('ProjectReference'),'model-signature-denominator-mismatch'),('missing-function',lambda m:m['functions'].pop('goalProject'),'model-signature-denominator-mismatch'),('partial-function',lambda m:m['functions']['goalProject'].pop(),'nontotal-function'),('function-range',lambda m:setfn(m,'goalProject','g0','foreign'),'ill-sorted-function-result'),('function-argument',lambda m:m['functions']['goalProject'][0].update(args=['foreign']),'ill-sorted-model-tuple'),('predicate-range',lambda m:m['predicates']['GoalApplicable'].append(['foreign']),'ill-sorted-model-tuple'),('predicate-arity',lambda m:m['predicates']['AdequateEvidenceDeclared'].append(['g1']),'ill-sorted-model-tuple')]:add('malformed-'+name,mutate,error=code)
 return rows
def qualify(model,ids):return {bucket:{ids[n]:value for n,value in model[bucket].items()} for bucket in ['domains','constants','functions','predicates']}
def verify(write=False):
    context=load('context.json');b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT)
    runtime=v.f.current_bindings();bindings=[b.ref(p) for p in [b.UNIT/'build_candidate.py',b.UNIT/'verify_candidate.py',b.IMPL/'verifier.py',b.IMPL/'ir.py',b.IMPL/'contracts.py',b.BASE/'units/A04/correspondence.py']]
    core=load('t.json')['payload'];typed=load('static-ir.json');packet=load('correspondence.json');counts=load('denominator.json')
    if not b.r.same_json(typed,b.ir.compile_interpretation(core,snap)) or not b.r.same_json(packet['interpretation'],core):raise ValueError('Substituted interpretation/IR')
    account=b.co.check(packet,snap,required_dependencies=[x['version_ref'] for x in core['depends_on']],required_conflicts=[x['finding_id'] for x in packet['source_precedence']['conflicts']])
    if not account['character_accounting_complete'] or not b.r.same_json(account,load('correspondence-check.json')):raise ValueError('Incomplete source account')
    if core['assumptions'] or packet['assumption_links'] or core['source_fidelity']!='pending':raise ValueError('Assumed target or owner fidelity')
    T=[x for x in typed['clauses'] if x['disposition']=='encoded'];I=[x for x in typed['populations'] if x['requirement']=='required']
    if len(T)!=counts['encoded_clauses'] or len(I)!=counts['required_populations']:raise ValueError('Changed theory/population denominator')
    ids={x['symbol_id']:b.ir.qualified(core['source'],core['scope'],x['symbol_id']) for x in core['declarations']}
    def evaluate(model):
        e=v.Denotation(typed['declarations'],model)
        tc=[{'clause_id':x['clause_id'],'truth':e.truth(x['formal_statement'])} for x in T]
        pc=[{'population_id':x['population_id'],'truth':e.truth(x['statement'])} for x in I]
        return all(x['truth'] for x in tc),all(x['truth'] for x in pc),tc,pc
    results=[]
    for case in controls():
        model=qualify(case['model'],ids)
        try:
            t,i,tc,pc=evaluate(model)
            if case['expected_error'] is not None or t!=case['expected_T'] or (case['expected_I'] is not None and i!=case['expected_I']):raise ValueError('Wrong authored control: '+case['case_id']+' '+str((t,i)))
            result={'case_id':case['case_id'],'status':'independently-evaluated-authored-model','model':model,'model_sha256':b.ir.digest(model),
                    'primary_theory_satisfied':t,'required_population_satisfied':i,'primary_clause_results':tc,'population_results':pc}
        except v.VerificationFault as error:
            if error.code!=case['expected_error']:raise
            result={'case_id':case['case_id'],'status':'rejected-model-structure','code':error.code,'model':model,'model_sha256':b.ir.digest(model)}
        results.append(result)
    queries=[];composed=b.ir.compose([typed])
    for q in load('query-policy.json')['queries']:
        model=base_model()
        model=qualify(model,ids);e=v.Denotation(typed['declarations'],model)
        target=v.renamed(q['target'],ids);witness=v.renamed(q['witness_condition'],ids)
        b.ir.check_composed_formula(composed,target);b.ir.check_composed_formula(composed,witness)
        if q['selected_in_T'] is not False or evaluate(model)[:2]!=(True,True) or e.truth(target) is not False or e.truth(witness) is not True:raise ValueError('Target assumed or no valid countermodel: '+q['query_id'])
        queries.append({'query_id':q['query_id'],'target_false':True,'witness_condition_true':True,'model':model,'model_sha256':b.ir.digest(model),'mechanized_proof':False})
    prior=json.loads((b.BASE/'definitions/CAV2-D32/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-Goal-model-controls/v1-candidate','status':'PASS-for-exact-authored-Goal-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Necessary Goal ten-field/exact-Project/universal-condition-evidence/owner-lifecycle declarations checked on supplied models;actual Goal achievement,evidence adequacy,owner authorization,lifecycle/project fidelity and whole proof pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
