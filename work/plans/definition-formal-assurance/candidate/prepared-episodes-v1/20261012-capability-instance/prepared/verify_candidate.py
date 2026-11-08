import copy,itertools,json
import build_candidate as b
import verifier as v
# Unexecuted prepared model-construction code. Evaluate only after Project audit0.
def load(name):return json.loads((b.UNIT/name).read_bytes())
def setfn(m,n,arg,value):next(x for x in m['functions'][n] if x['args']==[arg])['value']=value
def getfn(m,n,arg):return next(x['value'] for x in m['functions'][n] if x['args']==[arg])
def refresh(m):
 for fields,carrier in b.GROUPS:
  for n in fields:m['predicates'][n+'BindingDeclared']=[[x['args'][0],x['value']] for x in m['functions'][n]]
 m['predicates']['OwnerLocalToCoordinationContextDeclared']=[[getfn(m,'instanceLocalOwner',i),getfn(m,'instanceCoordinationContext',i)] for i in ['ci0','ci1','ci2','ci3']]
 m['predicates']['ParentClaimAtLaneDeclared']=[[i,getfn(m,'instanceParentLane',i),getfn(m,'instanceParentAuthorityClaim',i)] for i in ['ci0','ci1','ci2','ci3']]
 m['predicates']['InstanceClaimAtLaneDeclared']=[[i,getfn(m,'instanceLocalLane',i),getfn(m,'instanceAuthorityClaim',i)] for i in ['ci0','ci1','ci2','ci3']]
def base_model():
 ds={sort:[sort[0].lower()+sort[1:]+str(i) for i in range(4)]+[sort[0].lower()+sort[1:]+'Outside'] for sort in b.SORTS}
 ds.update(InstanceReference=['ci0','ci1','ci2','ci3','ciOutside'],
  IdentityReference=['id0','id1','id2','id3','parentID0','parentID1','identityOutside'],
  ProductCapabilityVersionReference=['v0','v1','vUnused','vOutside'],
  ProductCapabilityReference=['parent0','parent1','parentOutside'],
  BoundedContextReference=['bc0','bc1','bc2','bc3','bcOutside'],
  AuthorityClaimReference=['claimParent0','claimParent1','claimInstance0','claimInstance1','claimOutside'],
  AuthorityLaneReference=['parentLane','instanceLane','laneOutside'],
  RecursionContractReference=['r0','r1','r2','r3','rUnused','rOutside'],
  BudgetReference=['budget0','budget1','budgetUnused','budgetOutside'],
  StopRuleReference=['stop0','stop1','stop2','stopUnused','stopOutside'],
  Token=['empty','ref','other'])
 maps={}
 def table(n,values):maps[n]=lambda x:values.get(x,ds[b.FUNCTIONS[n][1]][-1])
 for n,sort in b.INSTANCE_FIELDS.items():
  table(n,{'ci'+str(i):ds[sort][min(i,len(ds[sort])-2)] for i in range(4)})
 table('instanceIdentity',{'ci'+str(i):'id'+str(i) for i in range(4)})
 table('instanceCapabilityVersion',{'ci0':'v0','ci1':'v1','ci2':'v0','ci3':'v1'})
 table('instanceParentAuthorityClaim',{'ci0':'claimParent0','ci1':'claimParent1','ci2':'claimParent0','ci3':'claimParent1'})
 table('instanceAuthorityClaim',{'ci0':'claimInstance0','ci1':'claimInstance1','ci2':'claimInstance0','ci3':'claimInstance1'})
 table('instanceRecursionContract',{'ci'+str(i):'r'+str(i) for i in range(4)})
 table('instanceLocalOwner',{'ci'+str(i):ds['LocalOwnerReference'][i] for i in range(4)})
 table('instanceParentLane',{'ci'+str(i):'parentLane' for i in range(4)})
 table('instanceLocalLane',{'ci'+str(i):'instanceLane' for i in range(4)})
 table('versionParentCapability',{'v0':'parent0','v1':'parent1'})
 table('parentCapabilityIdentity',{'parent0':'parentID0','parent1':'parentID1'})
 table('recursionBudget',{'r0':'budget0','r2':'budget1'})
 table('recursionStopRule',{'r1':'stop0','r2':'stop1','r3':'stop2'})
 for sort,n in b.HANDLES.items():maps[n]=lambda x:'ref'
 assert set(maps)==set(b.FUNCTIONS)
 funcs={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(ds[z] for z in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()}
 preds={n:[] for n in b.SIGNATURE}
 for sort in b.SORTS:
  if sort not in ['InstanceReference','Token']:preds[sort+'Declared']=[[x] for x in ds[sort] if not x.endswith('Outside')]
 for n in ['InstanceApplicable','InstanceInScopeDeclared','InstanceOwnerLocalDeclared','InstanceCoordinationContextDeclared','InstanceSemanticContextsDeclared','InstanceClaimsSeparatedDeclared']:preds[n]=[['ci'+str(i)] for i in range(4)]
 preds['InstanceRealizationDeclared']=[['ci0'],['ci2'],['ci3']]
 preds['InstanceSpecializationDeclared']=[['ci1'],['ci2']]
 preds['RecursionHasBudgetDeclared']=[['r0'],['r2']]
 preds['RecursionHasStopDeclared']=[['r1'],['r2'],['r3']]
 links=[['ci0','bc0'],['ci1','bc1'],['ci2','bc1'],['ci2','bc2'],['ci3','bc3']]
 preds['InstanceSemanticContextReferenceDeclared']=links
 preds['BoundedContextCollectionContainsDeclared']=[[next(x['value'] for x in funcs['instanceBoundedContexts'] if x['args']==[i]),c] for i,c in links]
 preds['InstanceActualAuthority']=[['ci3']]
 preds['InstanceActualConformance']=[['ci1']]
 preds['ParentCapabilityActualAuthority']=[['parent0']]
 m={'domains':ds,'constants':{'EMPTY':'empty','PARENT_LANE':'parentLane','INSTANCE_LANE':'instanceLane'},'functions':funcs,'predicates':preds}
 refresh(m);return m
def controls():
 rows=[]
 def add(name,mutation=lambda m:None,T=True,I=True,error=None):
  m=base_model();mutation(m)
  rows.append({'case_id':name,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 def change(m,n,arg,value):setfn(m,n,arg,value);refresh(m)
 add('realization-specialization-owner-context-claims-budget-stop-and-handoff')
 add('no-selected-instance',lambda m:m['predicates'].update(InstanceApplicable=[],InstanceInScopeDeclared=[]),I=False)
 add('no-independent-actual-authority',lambda m:m['predicates'].update(InstanceActualAuthority=[]),I=False)
 add('no-actual-conformance-population',lambda m:m['predicates'].update(InstanceActualConformance=[]),I=False)
 add('no-parent-actual-authority-population',lambda m:m['predicates'].update(ParentCapabilityActualAuthority=[]),I=False)
 add('independent-second-parent-actual-authority',lambda m:m['predicates']['ParentCapabilityActualAuthority'].append(['parent1']))
 for n in b.ACTUAL:
  add('independently-supported-Actual'+n,lambda m,n=n:m['predicates']['InstanceActual'+n].append(['ci2']))
 for n in b.EXCLUDED:
  add('selected-excluded-'+n,lambda m,n=n:m['predicates'][n].append(['ci0']),T=False,I=None)
  add('outside-excluded-'+n,lambda m,n=n:m['predicates'][n].append(['ciOutside']))
 add('realization-specialization-overlap-removed-but-genus-preserved',lambda m:m['predicates']['InstanceSpecializationDeclared'].remove(['ci2']),I=False)
 def remove_extra(m):
  col=getfn(m,'instanceBoundedContexts','ci2')
  m['predicates']['InstanceSemanticContextReferenceDeclared'].remove(['ci2','bc2'])
  m['predicates']['BoundedContextCollectionContainsDeclared'].remove([col,'bc2'])
 add('single-semantic-context-remains-sufficient',remove_extra,I=False)
 add('recursion-overlap-removed-budget-remains-sufficient',lambda m:m['predicates']['RecursionHasStopDeclared'].remove(['r2']),I=False)
 add('unused-parent-version-binding-absent',lambda m:m['predicates'].update(versionParentCapabilityBindingDeclared=[x for x in m['predicates']['versionParentCapabilityBindingDeclared'] if x[0]!='vUnused']))
 add('budget-only-unused-stop-binding-absent',lambda m:m['predicates'].update(recursionStopRuleBindingDeclared=[x for x in m['predicates']['recursionStopRuleBindingDeclared'] if x[0]!='r0']))
 add('stop-only-unused-budget-binding-absent',lambda m:m['predicates'].update(recursionBudgetBindingDeclared=[x for x in m['predicates']['recursionBudgetBindingDeclared'] if x[0]!='r1']))
 add('unused-version-handle-empty',lambda m:setfn(m,b.HANDLES['ProductCapabilityVersionReference'],'vUnused','empty'))
 add('unused-parent-handle-empty',lambda m:setfn(m,b.HANDLES['ProductCapabilityReference'],'parentOutside','empty'))
 add('unused-recursion-handle-empty',lambda m:setfn(m,b.HANDLES['RecursionContractReference'],'rUnused','empty'))
 add('budget-only-unused-stop-handle-empty',lambda m:setfn(m,b.HANDLES['StopRuleReference'],'stopOutside','empty'))
 add('stop-only-unused-budget-handle-empty',lambda m:setfn(m,b.HANDLES['BudgetReference'],'budgetOutside','empty'))
 def remove_genus(m):
  m['predicates']['InstanceRealizationDeclared'].remove(['ci0'])
 add('selected-instance-neither-realization-nor-specialization',remove_genus,T=False,I=None)
 for n in ['InstanceOwnerLocalDeclared','InstanceCoordinationContextDeclared','InstanceSemanticContextsDeclared','InstanceClaimsSeparatedDeclared']:
  add('missing-'+n,lambda m,n=n:m['predicates'][n].remove(['ci0']),T=False,I=None)
 add('owner-does-not-have-nominated-local-context-relation',lambda m:m['predicates']['OwnerLocalToCoordinationContextDeclared'].remove([getfn(m,'instanceLocalOwner','ci0'),getfn(m,'instanceCoordinationContext','ci0')]),T=False,I=None)
 def empty_context(m):
  col=getfn(m,'instanceBoundedContexts','ci0')
  m['predicates']['InstanceSemanticContextReferenceDeclared'].remove(['ci0','bc0'])
  m['predicates']['BoundedContextCollectionContainsDeclared'].remove([col,'bc0'])
 add('nonempty-context-collection-handle-with-no-semantic-context',empty_context,T=False,I=None)
 add('semantic-context-member-not-in-nominated-collection',lambda m:m['predicates']['InstanceSemanticContextReferenceDeclared'].append(['ci0','bc2']),T=False,I=None)
 add('nominated-collection-member-without-instance-context-relation',lambda m:m['predicates']['InstanceSemanticContextReferenceDeclared'].remove(['ci0','bc0']),T=False,I=None)
 add('nominated-semantic-context-undeclared',lambda m:m['predicates']['BoundedContextReferenceDeclared'].remove(['bc0']),T=False,I=None)
 add('instance-identity-collapses-into-parent',lambda m:change(m,'instanceIdentity','ci0','parentID0'),T=False,I=None)
 add('instance-local-lane-collapses-into-parent-lane',lambda m:change(m,'instanceLocalLane','ci0','parentLane'),T=False,I=None)
 add('missing-parent-claim-lane-binding',lambda m:m['predicates']['ParentClaimAtLaneDeclared'].remove(['ci0','parentLane','claimParent0']),T=False,I=None)
 add('extra-parent-claim-at-wrong-lane',lambda m:m['predicates']['ParentClaimAtLaneDeclared'].append(['ci0','instanceLane','claimParent0']),T=False,I=None)
 add('missing-instance-claim-lane-binding',lambda m:m['predicates']['InstanceClaimAtLaneDeclared'].remove(['ci0','instanceLane','claimInstance0']),T=False,I=None)
 def remove_recursion(m):
  m['predicates']['RecursionHasBudgetDeclared'].remove(['r0'])
 add('selected-recursion-has-neither-budget-nor-stop',remove_recursion,T=False,I=None)
 fields_and_subjects=[(b.INSTANCE_FIELDS,'ci0'),(b.OWNER_FIELDS,'ci0'),(b.LANE_FIELDS,'ci0'),(b.VERSION_FIELDS,'v0'),(b.PARENT_FIELDS,'parent0'),({'recursionBudget':'BudgetReference'},'r0'),({'recursionStopRule':'StopRuleReference'},'r1')]
 for fields,arg in fields_and_subjects:
  for n,sort in fields.items():
   add('missing-exact-binding-'+n,lambda m,n=n,arg=arg:m['predicates'].update({n+'BindingDeclared':[x for x in m['predicates'][n+'BindingDeclared'] if x[0]!=arg]}),T=False,I=None)
   value=getfn(base_model(),n,arg);alt=next(x for x in base_model()['domains'][sort] if x!=value)
   add('conflicting-exact-binding-'+n,lambda m,n=n,arg=arg,alt=alt:m['predicates'][n+'BindingDeclared'].append([arg,alt]),T=False,I=None)
   add('undeclared-selected-target-'+n,lambda m,sort=sort,value=value:m['predicates'][b.member(sort)].remove([value]),T=False,I=None)
 chosen={sort:values[0] for sort,values in base_model()['domains'].items() if sort!='Token'}
 for sort,n in b.HANDLES.items():
  add('empty-selected-handle-'+sort,lambda m,n=n,value=chosen[sort]:setfn(m,n,value,'empty'),T=False,I=None)
 for name,mutate,code in [
  ('empty-domain',lambda m:m['domains'].update(InstanceReference=[]),'empty-or-malformed-domain'),
  ('missing-domain',lambda m:m['domains'].pop('StopRuleReference'),'model-signature-denominator-mismatch'),
  ('missing-function',lambda m:m['functions'].pop('instanceCapabilityVersion'),'model-signature-denominator-mismatch'),
  ('partial-function',lambda m:m['functions']['instanceTerminalHandoff'].pop(),'nontotal-function'),
  ('function-range',lambda m:setfn(m,'instanceTerminalHandoff','ci0','foreign'),'ill-sorted-function-result'),
  ('function-argument',lambda m:m['functions']['instanceTerminalHandoff'][0].update(args=['foreign']),'ill-sorted-model-tuple'),
  ('predicate-range',lambda m:m['predicates']['InstanceApplicable'].append(['foreign']),'ill-sorted-model-tuple'),
  ('predicate-arity',lambda m:m['predicates']['ParentClaimAtLaneDeclared'].append(['ci0','parentLane']),'ill-sorted-model-tuple')]:
  add('malformed-'+name,mutate,error=code)
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
    prior=json.loads((b.BASE/'definitions/CAV2-D60/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-CapabilityInstance-model-controls/v1-candidate','status':'PASS-for-exact-authored-CapabilityInstance-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Necessary owner-local exact-version instance tuple,context,parent identity,claim-lane andrecursion/handoff guards checked on supplied models;actual realization,adoption,construction,conformance,authority,fidelity andwhole proof pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
