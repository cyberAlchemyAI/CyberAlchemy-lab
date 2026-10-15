"""Supplied Actor classification and attribution declaration controls; no concrete classification."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def setfn(m,n,arg,value):
 args=arg if isinstance(arg,list) else [arg];next(x for x in m['functions'][n] if x['args']==args)['value']=value
def getfn(m,n,*args):return next(x['value'] for x in m['functions'][n] if x['args']==list(args))
def refresh(m):
 for fields,carrier in b.GROUPS:
  for n in fields:m['predicates'][n+'BindingDeclared']=[[x['args'][0],x['value']] for x in m['functions'][n]]
def base_model():
 ds={'ActorReference':['a0','a1','a2','aOutside'],'ConcreteUseReference':['u0','u1','u2','uOutside'],'AttributionReference':['t0','t1','t2','tOutside'],'SubjectReference':['s0','s1','s2','s3','s4','sOutside'],'IdentityReference':['id0','id1','id2','idOutside'],'OwnerReference':['owner0','owner1','ownerOutside'],'LifecycleReference':['life0','life1','life2','lifeOutside'],'AuthorityReference':['auth0','auth1','auth2','authOutside'],'ScopeReference':['scope0','scope1','scope2','schemeGlobal','schemeLocal','scopeOutside'],'SchemeReference':['scheme0','scheme1','schemeOutside'],'AssignmentReference':['assignment0','assignment1','assignment2','assignmentOutside'],'ClassificationValueReference':['v0','v1','v2','vOutside'],'ActivityReference':['activity0','activity1','activityOutside'],'Token':['empty','reference','other']}
 def mapn(n,values):return lambda x:values.get(x,ds[b.FUNCTIONS[n][1]][-1])
 maps={
 'actorScope':mapn('actorScope',{'a0':'scope0','a1':'scope1','a2':'scope2'}),
 'subjectIdentity':mapn('subjectIdentity',{'s0':'id0','s3':'id0','s1':'id1','s4':'id1','s2':'id2'}),
 'subjectOwner':mapn('subjectOwner',{'s0':'owner0','s3':'owner0','s1':'owner1','s4':'owner1','s2':'owner0'}),
 'subjectLifecycle':mapn('subjectLifecycle',{'s0':'life0','s3':'life0','s1':'life1','s4':'life1','s2':'life2'}),
 'subjectAuthority':mapn('subjectAuthority',{'s0':'auth0','s3':'auth0','s1':'auth1','s4':'auth1','s2':'auth2'}),
 'useActor':mapn('useActor',{'u0':'a0','u1':'a1','u2':'a0'}),
 'useSubject':mapn('useSubject',{'u0':'s0','u1':'s1','u2':'s2'}),
 'useScheme':mapn('useScheme',{'u0':'scheme0','u1':'scheme0','u2':'scheme1'}),
 'useAssignment':mapn('useAssignment',{'u0':'assignment0','u1':'assignment1','u2':'assignment2'}),
 'schemeScope':mapn('schemeScope',{'scheme0':'schemeGlobal','scheme1':'schemeLocal'}),
 'assignmentActor':mapn('assignmentActor',{'assignment0':'a0','assignment1':'a1','assignment2':'a0'}),
 'assignmentSubject':mapn('assignmentSubject',{'assignment0':'s0','assignment1':'s1','assignment2':'s2'}),
 'assignmentScheme':mapn('assignmentScheme',{'assignment0':'scheme0','assignment1':'scheme0','assignment2':'scheme1'}),
 'assignmentValue':mapn('assignmentValue',{'assignment0':'v0','assignment1':'v1','assignment2':'v0'}),
 'valueActor':mapn('valueActor',{'v0':'a0','v1':'a1','v2':'a2'}),
 'attributionUse':mapn('attributionUse',{'t0':'u0','t1':'u1','t2':'u2'}),
 'attributionBeforeSubject':mapn('attributionBeforeSubject',{'t0':'s0','t1':'s1','t2':'s2'}),
 'attributionAfterSubject':mapn('attributionAfterSubject',{'t0':'s3','t1':'s4','t2':'s2'}),
 'attributionActivity':mapn('attributionActivity',{'t0':'activity0','t1':'activity0','t2':'activity1'})}
 for sort,n in b.HANDLES.items():maps[n]=lambda x:'reference'
 assert set(maps)==set(b.FUNCTIONS)
 funcs={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(ds[z] for z in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};preds={n:[] for n in b.SIGNATURE}
 for sort in b.SORTS:
  if sort not in ['ActorReference','ConcreteUseReference','AttributionReference','Token']:preds[sort+'Declared']=[[x] for x in ds[sort] if not x.endswith('Outside')]
 for n in ['ActorApplicable','ActorInScopeDeclared','ActorGovernedParticipantIdentityDeclared','ActorAbstractParticipationClassificationDeclared','ActorParticipationAttributableDeclared','ActorBoundedScopeDeclared']:preds[n]=[['a0'],['a1'],['a2']]
 preds.update(ActorIdentityBackedDeclared=[['a0'],['a2']],ActorRecordBackedDeclared=[['a1'],['a2']],ActorActualAuthority=[['a1']])
 for n in ['UseApplicable','UseInScopeDeclared','UseRecordedDeclared','UseExactClassificationResolvedDeclared']:preds[n]=[['u0'],['u1'],['u2']]
 for n in ['AttributionApplicable','AttributionInScopeDeclared','AttributionRecordedDeclared','AttributionExactActivityNamedDeclared']:preds[n]=[['t0'],['t1'],['t2']]
 for n in ['SubjectIndependentlyIdentifiedDeclared','SubjectGovernedDeclared']:preds[n]=[['s'+str(i)] for i in range(5)]
 preds['SchemeRecordedDeclared']=[['scheme0'],['scheme1']];preds['AssignmentRecordedDeclared']=[['assignment0'],['assignment1'],['assignment2']];preds['ValueActorClassificationDeclared']=[['v0'],['v1']];preds['ActivityRecordedDeclared']=[['activity0'],['activity1']]
 m={'domains':ds,'constants':{'EMPTY':'empty'},'functions':funcs,'predicates':preds};refresh(m);return m
def controls():
 rows=[]
 def add(name,mutation=lambda m:None,T=True,I=True,error=None):
  m=base_model();mutation(m);rows.append({'case_id':name,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 def change(m,n,arg,value):setfn(m,n,arg,value);refresh(m)
 add('abstract-and-concrete-Actor-exact-classification-preserved-attribution')
 add('no-selected-Actors-uses-attributions',lambda m:m['predicates'].update(ActorApplicable=[],ActorInScopeDeclared=[],UseApplicable=[],UseInScopeDeclared=[],AttributionApplicable=[],AttributionInScopeDeclared=[]),I=False)
 add('abstract-Actors-without-concrete-use-or-attribution',lambda m:m['predicates'].update(UseApplicable=[],UseInScopeDeclared=[],AttributionApplicable=[],AttributionInScopeDeclared=[]),I=False)
 add('concrete-use-without-attribution',lambda m:m['predicates'].update(AttributionApplicable=[],AttributionInScopeDeclared=[]),I=False)
 add('no-independent-Actor-authority',lambda m:m['predicates'].update(ActorActualAuthority=[]),I=False)
 for prefix,names,selected in [('Actor',b.ACTOR_ACTUAL,['a0','a1','a2']),('Use',b.USE_ACTUAL,['u0','u1','u2']),('Attribution',b.ATTR_ACTUAL,['t0','t1','t2'])]:
  add('all-'+prefix+'-actual-outcomes-independently-supplied',lambda m,prefix=prefix,names=names,selected=selected:[m['predicates'].update({prefix+'Actual'+n:[[x] for x in selected]}) for n in names],I=False)
  for n in names:add('independently-supported-'+prefix+'-Actual'+n,lambda m,prefix=prefix,n=n,arg=selected[0]:m['predicates'][prefix+'Actual'+n].append([arg]))
 for names,arg,outside in [(b.ROOT_EXCLUDED,'a0','aOutside'),(b.USE_EXCLUDED,'u0','uOutside'),(b.ATTR_EXCLUDED,'t0','tOutside')]:
  for n in names:
   add('selected-excluded-'+n,lambda m,n=n,arg=arg:m['predicates'][n].append([arg]),T=False,I=None)
   add('outside-excluded-'+n,lambda m,n=n,outside=outside:m['predicates'][n].append([outside]))
 add('shared-scheme-and-separate-Actor-scope-allowed',lambda m:change(m,'schemeScope','scheme0','scope2'))
 add('one-subject-reference-before-and-after-allowed',lambda m:change(m,'attributionAfterSubject','t0','s0'))
 add('inclusive-identity-or-record-two-identity-only-witnesses-preserved',lambda m:(m['predicates']['ActorRecordBackedDeclared'].append(['a0']),m['predicates']['ActorRecordBackedDeclared'].remove(['a2'])))
 add('abstract-Actor-no-actual-kind-or-activity-required',lambda m:m['predicates']['ActorActualAgent'].append(['a1']))
 add('outside-subject-empty-handle-allowed',lambda m:setfn(m,b.HANDLES['SubjectReference'],'sOutside','empty'))
 for n,arg in [('ActorGovernedParticipantIdentityDeclared','a0'),('ActorAbstractParticipationClassificationDeclared','a0'),('ActorParticipationAttributableDeclared','a0'),('ActorBoundedScopeDeclared','a0'),('ActorInScopeDeclared','a0'),('UseInScopeDeclared','u0'),('UseRecordedDeclared','u0'),('UseExactClassificationResolvedDeclared','u0'),('SubjectIndependentlyIdentifiedDeclared','s0'),('SubjectGovernedDeclared','s0'),('SchemeRecordedDeclared','scheme0'),('AssignmentRecordedDeclared','assignment0'),('ValueActorClassificationDeclared','v0'),('AttributionInScopeDeclared','t0'),('AttributionRecordedDeclared','t0'),('AttributionExactActivityNamedDeclared','t0'),('ActivityRecordedDeclared','activity0')]:
  add('missing-selected-'+n,lambda m,n=n,arg=arg:m['predicates'][n].remove([arg]),T=False,I=None)
 add('neither-identity-nor-record-backed-Actor',lambda m:m['predicates']['ActorIdentityBackedDeclared'].remove(['a0']),T=False,I=None)
 for n,value in [('assignmentActor','a1'),('assignmentSubject','s1'),('assignmentScheme','scheme1'),('assignmentValue','v1')]:add('classification-nomination-mismatch-'+n,lambda m,n=n,value=value:change(m,n,'assignment0',value),T=False,I=None)
 add('classification-value-nominates-other-Actor',lambda m:change(m,'valueActor','v0','a1'),T=False,I=None)
 add('attribution-before-subject-not-use-subject',lambda m:change(m,'attributionBeforeSubject','t0','s3'),T=False,I=None)
 for n,value in [('subjectIdentity','id1'),('subjectOwner','owner1'),('subjectLifecycle','life1'),('subjectAuthority','auth1')]:add('attribution-changes-subject-coordinate-'+n,lambda m,n=n,value=value:change(m,n,'s3',value),T=False,I=None)
 targets={id(b.ACTOR_FIELDS):'a0',id(b.SUBJECT_FIELDS):'s0',id(b.USE_FIELDS):'u0',id(b.SCHEME_FIELDS):'scheme0',id(b.ASSIGNMENT_FIELDS):'assignment0',id(b.VALUE_FIELDS):'v0',id(b.ATTRIBUTION_FIELDS):'t0'}
 for fields,carrier in b.GROUPS:
  arg=targets[id(fields)]
  for n,sort in fields.items():
   add('missing-exact-binding-'+n,lambda m,n=n,arg=arg:m['predicates'].update({n+'BindingDeclared':[x for x in m['predicates'][n+'BindingDeclared'] if x[0]!=arg]}),T=False,I=None)
   value=getfn(base_model(),n,arg);alt=next(x for x in base_model()['domains'][sort] if x!=value)
   add('conflicting-exact-binding-'+n,lambda m,n=n,arg=arg,alt=alt:m['predicates'][n+'BindingDeclared'].append([arg,alt]),T=False,I=None)
   declared={'ActorReference':'ActorApplicable','ConcreteUseReference':'UseApplicable','AttributionReference':'AttributionApplicable'}.get(sort,sort+'Declared')
   add('undeclared-selected-target-'+n,lambda m,declared=declared,value=value:m['predicates'][declared].remove([value]),T=False,I=None)
 selected={'ActorReference':'a0','ConcreteUseReference':'u0','AttributionReference':'t0','SubjectReference':'s0','IdentityReference':'id0','OwnerReference':'owner0','LifecycleReference':'life0','AuthorityReference':'auth0','ScopeReference':'scope0','SchemeReference':'scheme0','AssignmentReference':'assignment0','ClassificationValueReference':'v0','ActivityReference':'activity0'}
 for sort,n in b.HANDLES.items():add('empty-selected-handle-'+sort,lambda m,n=n,value=selected[sort]:setfn(m,n,value,'empty'),T=False,I=None)
 add('malformed-empty-domain',lambda m:m['domains'].update(ActorReference=[]),error='empty-or-malformed-domain')
 add('malformed-missing-domain',lambda m:m['domains'].pop('SubjectReference'),error='model-signature-denominator-mismatch')
 add('malformed-missing-function',lambda m:m['functions'].pop('actorScope'),error='model-signature-denominator-mismatch')
 add('malformed-partial-function',lambda m:m['functions']['actorScope'].pop(),error='nontotal-function')
 add('malformed-function-range',lambda m:setfn(m,'actorScope','a0','foreign'),error='ill-sorted-function-result')
 add('malformed-function-argument',lambda m:m['functions']['actorScope'][0].update(args=['foreign']),error='ill-sorted-model-tuple')
 add('malformed-predicate-range',lambda m:m['predicates']['ActorApplicable'].append(['foreign']),error='ill-sorted-model-tuple')
 add('malformed-predicate-arity',lambda m:m['predicates']['useSubjectBindingDeclared'].append(['u0']),error='ill-sorted-model-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.withdrawal-record/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-Actor-model-controls/v1-candidate','status':'PASS-for-exact-authored-Actor-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Exact abstract/concrete Actor classification,independent governed subjects,Scheme/Assignment/value coherence,activity attribution and preserved identity/owner/lifecycle/authority declarations checked on supplied models;actual classification,agency,ownership,permission,authority,successful action,fidelity and whole proof pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
