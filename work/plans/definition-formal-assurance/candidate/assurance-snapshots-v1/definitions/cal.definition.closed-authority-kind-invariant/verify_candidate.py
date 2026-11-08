"""Independent finite scoped authority-kind norm and owner-addition controls."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def base_model():
 domains={'Artifact':['a1','a2','a3','a4'],'Kind':['kDefinition','kNew','kOther'],'Enumeration':['e1','e2'],'State':['before','after'],'Decision':['d1','d2'],'Owner':['o1','o2'],'Token':['EMPTY','lifecycle','owner-route','kind-label']}
 functions={n:[] for n in b.FUNCTIONS}
 for n,(args,result) in b.FUNCTIONS.items():
  for values in itertools.product(*(domains[x] for x in args)):
   value={'a1':'kDefinition','a2':'kDefinition','a3':'kNew','a4':'kOther'}[values[0]] if n=='kindOfArtifact' else {'lifecycleValue':'lifecycle','ownerRouteValue':'owner-route','kindLabelValue':'kind-label'}[n]
   functions[n].append({'args':list(values),'value':value})
 predicates={n:[] for n in b.SIGNATURE};predicates.update(AuthorityKindEnumeration=[['e1']],ClosedEnumeration=[['e1',s] for s in domains['State']],Member=[['kDefinition','e1','before'],['kDefinition','e1','after'],['kNew','e1','after']],RawKindLabel=[['kOther'],['kNew']],RegisteredSuccessorState=[['e1','before','after']],AmendsKind=[['d1','kNew','e1','before','after']],AuthorizedOwnerDecision=[['d1','o1','e1','before','after'],['d2','o1','e1','before','after']],ApprovedAdditionProposal=[['d2','kOther','e1','before','after']],DeclaredLifecycle=[['kNew','e1','after'],['kOther','e1','after']],DeclaredOwnerRoute=[['kNew','e1','after'],['kOther','e1','after']],SourceDefinitionPromoted=[['e1','after']])
 for a in domains['Artifact']:
  k=next(x['value'] for x in functions['kindOfArtifact'] if x['args']==[a])
  for s in domains['State']:
   if [k,'e1',s] in predicates['Member']:predicates['GovernedByOwnLadderOwner'].append([a,'e1',s])
   else:predicates['Blocked'].append([a,'e1',s])
   for n in ['MayAcquireAuthority','MayExerciseAuthority']:predicates[n].append([a,'e2',s])
 predicates['Blocked'] += [['a1','e1','before'],['a3','e1','after']]
 for n in ['MayAcquireAuthority','MayExerciseAuthority']:predicates[n].append(['a1','e1','after'])
 return {'domains':domains,'constants':{'EMPTY':'EMPTY'},'functions':functions,'predicates':predicates}
def controls():
 rows=[]
 def add(id,change=lambda m:None,t=True,i=True,error=None):
  model=base_model();change(model);rows.append({'case_id':id,'model':model,'expected_T':t,'expected_I':i,'expected_error':error})
 def remove(m,n,row):m['predicates'][n].remove(row)
 def append(m,n,row):m['predicates'][n].append(row)
 def function(m,n,args,value):next(x for x in m['functions'][n] if x['args']==args).update(value=value)
 add('scoped-closed-table-default-deny-owner-addition-no-automatic-grant')
 for n,row in [('ActualAuthorityGranted',['a1','e1','after']),('ActualArtifactAdmitted',['a1']),('ActualKindTableAdmitted',['e1']),('SourceOwnerAccepted',['e1']),('ActualRuntimeActivated',['e1']),('ActualExternalEffect',['a1']),('ActualOwnerGateSucceeded',['d1','e1','after']),('ReviewModeEnacted',['e1','after']),('DeterministicEnforcement',['e1','after'])]:add('independently-supplied-outcome-'+n,lambda m,n=n,row=row:append(m,n,row),True,n not in ['ReviewModeEnacted','DeterministicEnforcement'])
 add('actual-authority-at-normatively-blocked-context',lambda m:append(m,'ActualAuthorityAcquired',['a3','e1','before']) or append(m,'ActualAuthorityExercised',['a3','e1','before']))
 add('known-kind-not-automatically-unblocked',lambda m:None)
 add('unknown-kind-missing-blocked',lambda m:remove(m,'Blocked',['a3','e1','before']),False,True)
 for n in ['MayAcquireAuthority','MayExerciseAuthority']:add('unknown-kind-forbidden-permission-'+n,lambda m,n=n:append(m,n,['a3','e1','before']),False,True)
 for s in ['before','after']:add('selected-table-missing-closed-marker-'+s,lambda m,s=s:remove(m,'ClosedEnumeration',['e1',s]),False,True)
 add('known-kind-missing-own-ladder-owner-route',lambda m:remove(m,'GovernedByOwnLadderOwner',['a1','e1','before']),False,None)
 for n,row in [('DeclaredLifecycle',['kNew','e1','after']),('DeclaredOwnerRoute',['kNew','e1','after']),('AmendsKind',['d1','kNew','e1','before','after']),('AuthorizedOwnerDecision',['d1','o1','e1','before','after'])]:add('added-kind-missing-'+n,lambda m,n=n,row=row:remove(m,n,row),False,None)
 for n in ['lifecycleValue','ownerRouteValue']:add('added-kind-empty-'+n,lambda m,n=n:function(m,n,['kNew','e1','after'],'EMPTY'),False,None)
 add('amendment-for-other-table-does-not-transfer',lambda m:remove(m,'AuthorizedOwnerDecision',['d1','o1','e1','before','after']) or append(m,'AuthorizedOwnerDecision',['d1','o1','e2','before','after']),False,None)
 add('amendment-for-other-state-pair-does-not-transfer',lambda m:remove(m,'AuthorizedOwnerDecision',['d1','o1','e1','before','after']) or append(m,'AuthorizedOwnerDecision',['d1','o1','e1','after','before']),False,None)
 add('amendment-for-other-kind-does-not-transfer',lambda m:remove(m,'AmendsKind',['d1','kNew','e1','before','after']) or append(m,'AmendsKind',['d1','kOther','e1','before','after']),False,None)
 add('unregistered-membership-change-not-covered-by-addition-guard',lambda m:m['predicates'].update(RegisteredSuccessorState=[],AmendsKind=[],AuthorizedOwnerDecision=[]),True,False)
 add('no-recognized-authority-table-vacuous-theory-rich-populations-fail',lambda m:m['predicates'].update(AuthorityKindEnumeration=[]),True,False)
 add('non-authority-enumeration-permission-not-globally-denied',lambda m:None)
 add('owner-route-label-not-connected-to-Owner-sort-denotation',lambda m:remove(m,'AuthorizedOwnerDecision',['d1','o1','e1','before','after']) or append(m,'AuthorizedOwnerDecision',['d1','o2','e1','before','after']))
 def alias(m):
  for n in ['lifecycleValue','ownerRouteValue','kindLabelValue']:
   for x in m['functions'][n]:x['value']='kind-label'
 add('lifecycle-owner-route-kind-label-Tokens-can-alias',alias)
 add('kind-label-Token-unused-by-membership-predicate',lambda m:function(m,'kindLabelValue',['kNew','e1','after'],'EMPTY'))
 add('existing-known-kind-lifecycle-field-not-connected-to-opaque-routing',lambda m:function(m,'lifecycleValue',['kDefinition','e1','before'],'EMPTY'))
 def removal(m):
  remove(m,'Member',['kDefinition','e1','after'])
  for a in ['a1','a2']:append(m,'Blocked',[a,'e1','after'])
  for n in ['MayAcquireAuthority','MayExerciseAuthority']:remove(m,n,['a1','e1','after'])
 add('kind-removal-not-covered-by-addition-only-owner-rule',removal)
 add('same-State-values-for-distinct-records-no-temporal-order-proof',lambda m:append(m,'RegisteredSuccessorState',['e1','after','after']))
 add('listed-kind-can-have-permission-after-own-independent-qualification',lambda m:append(m,'MayAcquireAuthority',['a3','e1','after']) or append(m,'MayExerciseAuthority',['a3','e1','after']),True,False)
 add('separate-owner-proposal-without-applied-membership',lambda m:None)
 add('nontotal-kind-function',lambda m:m['functions']['kindOfArtifact'].pop(),None,None,'nontotal-function')
 add('ill-sorted-kind-function-result',lambda m:function(m,'kindOfArtifact',['a1'],'a1'),None,None,'ill-sorted-function-result')
 add('ill-sorted-empty-constant',lambda m:m['constants'].update(EMPTY='before'),None,None,'ill-sorted-constant')
 add('wrong-membership-arity',lambda m:append(m,'Member',['kNew','e1']),None,None,'ill-sorted-model-tuple')
 add('duplicate-owner-decision-tuple',lambda m:append(m,'AuthorizedOwnerDecision',['d1','o1','e1','before','after']),None,None,'duplicate-predicate-tuple')
 add('empty-Kind-domain',lambda m:m['domains'].update(Kind=[]),None,None,'empty-or-malformed-domain')
 add('duplicate-function-tuple',lambda m:m['functions']['kindOfArtifact'].append(copy.deepcopy(m['functions']['kindOfArtifact'][0])),None,None,'duplicate-function-tuple')
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
        model=next(x['model'] for x in controls() if x['case_id']==q['countermodel_case_id']) if 'countermodel_case_id' in q else base_model()
        model=qualify(model,ids);e=v.Denotation(typed['declarations'],model)
        target=v.renamed(q['target'],ids);witness=v.renamed(q['witness_condition'],ids)
        b.ir.check_composed_formula(composed,target);b.ir.check_composed_formula(composed,witness)
        if q['selected_in_T'] is not False or evaluate(model)[:2]!=(True,True) or e.truth(target) is not False or e.truth(witness) is not True:raise ValueError('Target assumed or no valid countermodel: '+q['query_id'])
        queries.append({'query_id':q['query_id'],'target_false':True,'witness_condition_true':True,'model':model,'model_sha256':b.ir.digest(model),'mechanized_proof':False})
    prior=json.loads((b.BASE/'definitions/cal.definition.challenge-event/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-ClosedAuthorityKindInvariant-model-controls/v1-candidate','status':'PASS-for-exact-authored-ClosedAuthorityKindInvariant-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent supplied scoped closed-kind membership, normative unknown-kind permission denial and necessary owner-gated registered additions. Table/state/kind/owner/permission denotation, actual authority and universal runtime or temporal enforcement remain unresolved.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
