"""Supplied exact Identity Lineage tuple,kind,contract and non-effect declaration models."""
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
 ds={'LineageReference':['l'+str(i) for i in range(6)]+['lOutside'],'LineageIdReference':['lid'+str(i) for i in range(6)]+['lidOutside'],'KindDefinitionReference':['productKind','contextKind','otherKind','kindOutside'],'EpochReference':['e'+str(i) for i in range(12)]+['eOutside'],'IdentityReference':['id'+str(i) for i in range(9)]+['idOutside'],'NameReference':['old0','new0','name1','name2','name3','name4','old1','new1','name5','nameOutside'],'LineageKindReference':['renameKind','successorKind','otherLineageKind','lineageKindOutside'],'DecisionReference':['d'+str(i) for i in range(6)]+['dOutside'],'OwnerReference':['owner0','owner1','ownerOutside'],'EvidenceReference':['ev0','ev1','evOutside'],'NonEffectsReference':['nonEffects0','nonEffects1','nonEffectsOutside'],'ContractReference':['productContract','contextContract','generalContract','contractOutside'],'ScopeReference':['productScope','contextScope','generalScope','scopeOutside'],'Token':['empty','reference','other']}
 def suffix(x):return 'Outside' if x.endswith('Outside') else x[-1]
 def mapn(n,values):return lambda x:values.get(x,ds[b.FUNCTIONS[n][1]][-1])
 maps={'lineageIdentifier':lambda x:'lid'+suffix(x),'lineageSubjectKind':mapn('lineageSubjectKind',{'l0':'productKind','l1':'contextKind','l2':'productKind','l3':'productKind','l4':'productKind','l5':'productKind'}),'lineagePredecessor':mapn('lineagePredecessor',{'l'+str(i):'e'+str(2*i) for i in range(6)}),'lineageSuccessor':mapn('lineageSuccessor',{'l'+str(i):'e'+str(2*i+1) for i in range(6)}),'lineageKind':mapn('lineageKind',{'l0':'renameKind','l1':'successorKind','l2':'otherLineageKind','l3':'otherLineageKind','l4':'renameKind','l5':'successorKind'}),'lineageOwnerDecision':lambda x:'d'+suffix(x),'lineageEvidence':mapn('lineageEvidence',{'l'+str(i):'ev0' if i<3 else 'ev1' for i in range(6)}),'lineageNonEffects':mapn('lineageNonEffects',{'l'+str(i):'nonEffects0' if i<3 else 'nonEffects1' for i in range(6)}),'lineageContract':mapn('lineageContract',{'l0':'productContract','l1':'contextContract','l2':'productContract','l3':'productContract','l4':'generalContract','l5':'generalContract'}),'epochIdentity':mapn('epochIdentity',{'e0':'id0','e1':'id0','e2':'id1','e3':'id2','e4':'id3','e5':'id3','e6':'id4','e7':'id5','e8':'id6','e9':'id6','e10':'id7','e11':'id8'}),'epochName':mapn('epochName',{'e0':'old0','e1':'new0','e2':'name1','e3':'name1','e4':'name2','e5':'name3','e6':'name4','e7':'name4','e8':'old1','e9':'new1','e10':'name5','e11':'name5'}),'epochSubjectKind':mapn('epochSubjectKind',{'e'+str(i):'contextKind' if i in [2,3,9,11] else 'productKind' for i in range(12)}),'decisionOwner':mapn('decisionOwner',{'d'+str(i):'owner0' if i<3 else 'owner1' for i in range(6)}),'contractSubjectKind':mapn('contractSubjectKind',{'productContract':'productKind','contextContract':'contextKind','generalContract':'productKind'}),'contractScope':mapn('contractScope',{'productContract':'productScope','contextContract':'contextScope','generalContract':'generalScope'})}
 for sort,n in b.HANDLES.items():maps[n]=lambda x:'reference'
 assert set(maps)==set(b.FUNCTIONS)
 funcs={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(ds[z] for z in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};preds={n:[] for n in b.SIGNATURE}
 for sort in b.SORTS:
  if sort not in ['LineageReference','Token']:preds[sort+'Declared']=[[x] for x in ds[sort] if not x.endswith('Outside')]
 for n in ['LineageApplicable','LineageInScopeDeclared','LineageGovernedDeclared','LineageTypedDeclared','LineageImmutableDeclared','LineageEvidenceBackedDeclared','LineageContinuityRecordDeclared','LineageExactEndpointsResolvedDeclared']:preds[n]=[['l'+str(i)] for i in range(6)]
 preds.update(LineageSameIdentityRenameDeclared=[['l0'],['l4']],LineageSuccessorIdentityDeclared=[['l1'],['l5']],LineageOtherKindDeclared=[['l2'],['l3']],LineageGeneralizedContractSelectedDeclared=[['l4'],['l5']],LineageActualAuthority=[['l1']],KindSameIdentityRenameDeclared=[['renameKind']],KindSuccessorIdentityDeclared=[['successorKind']],KindOtherDeclared=[['otherLineageKind']],KindProductDeclared=[['productKind']],KindContextDeclared=[['contextKind']],ContractRecordedDeclared=[['productContract'],['contextContract'],['generalContract']],ContractContextSpecificDeclared=[['contextContract']],ContractGeneralizedDeclared=[['generalContract']],ContractAdmissionRecordedDeclared=[['generalContract']],DecisionRecordedDeclared=[['d'+str(i)] for i in range(6)],ContractCoversSubjectKindDeclared=[['generalContract','productKind'],['generalContract','contextKind']])
 m={'domains':ds,'constants':{'EMPTY':'empty'},'functions':funcs,'predicates':preds};refresh(m);return m
def controls():
 rows=[]
 def add(name,mutation=lambda m:None,T=True,I=True,error=None):
  m=base_model();mutation(m);rows.append({'case_id':name,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 def change(m,n,arg,value):setfn(m,n,arg,value);refresh(m)
 add('exact-rename-successor-other-and-kind-specific-generalized-lineages')
 add('no-selected-lineages',lambda m:m['predicates'].update(LineageApplicable=[],LineageInScopeDeclared=[]),I=False)
 add('only-first-lineage-selected',lambda m:m['predicates'].update(LineageApplicable=[['l0']],LineageInScopeDeclared=[['l0']]),I=False)
 add('no-independent-authority',lambda m:m['predicates'].update(LineageActualAuthority=[]),I=False)
 add('all-actual-outcomes-independently-supplied',lambda m:[m['predicates'].update({'LineageActual'+n:[['l'+str(i)] for i in range(6)]}) for n in b.ACTUAL],I=False)
 for n in b.ACTUAL:
  arg='l4' if n in ['GeneralizedContractAdmission','GeneralizedContractApplicability'] else 'l1' if n=='SuccessorIdentity' else 'l0'
  add('independently-supported-actual-'+n,lambda m,n=n,arg=arg:m['predicates']['LineageActual'+n].append([arg]))
 for n in b.EXCLUDED:
  add('selected-excluded-'+n,lambda m,n=n:m['predicates'][n].append(['l0']),T=False,I=None)
  add('outside-excluded-'+n,lambda m,n=n:m['predicates'][n].append(['lOutside']))
 for n in b.RENAME_EXCLUDED:
  add('rename-excluded-'+n,lambda m,n=n:m['predicates'][n].append(['l0']),T=False,I=None)
  add('outside-rename-exclusion-'+n,lambda m,n=n:m['predicates'][n].append(['lOutside']))
  add('nonrename-not-subjected-to-rename-only-exclusion-'+n,lambda m,n=n:m['predicates'][n].append(['l2']))
 add('other-kind-same-endpoint-reference-allowed',lambda m:change(m,'lineageSuccessor','l2','e4'))
 add('successor-name-change-independent',lambda m:change(m,'epochName','e3','new0'),I=True)
 add('general-contract-anchor-kind-independent-of-covered-endpoints',lambda m:change(m,'contractSubjectKind','generalContract','otherKind'))
 add('specific-contract-admission-flag-not-forced',lambda m:m['predicates']['ContractAdmissionRecordedDeclared'].append(['productContract']))
 add('outside-epoch-empty-handle-allowed',lambda m:setfn(m,b.HANDLES['EpochReference'],'eOutside','empty'))
 for n,arg in [('LineageInScopeDeclared','l0'),('LineageGovernedDeclared','l0'),('LineageTypedDeclared','l0'),('LineageImmutableDeclared','l0'),('LineageEvidenceBackedDeclared','l0'),('LineageContinuityRecordDeclared','l0'),('LineageExactEndpointsResolvedDeclared','l0'),('DecisionRecordedDeclared','d0'),('ContractRecordedDeclared','productContract'),('ContractAdmissionRecordedDeclared','generalContract'),('KindContextDeclared','contextKind')]:
  add('missing-selected-'+n,lambda m,n=n,arg=arg:m['predicates'][n].remove([arg]),T=False,I=None)
 for n,arg in [('LineageSameIdentityRenameDeclared','l0'),('LineageSuccessorIdentityDeclared','l1'),('LineageOtherKindDeclared','l2'),('LineageGeneralizedContractSelectedDeclared','l4')]:add('missing-root-kind-or-generalization-'+n,lambda m,n=n,arg=arg:m['predicates'][n].remove([arg]),T=False,I=None)
 for n,arg in [('KindSameIdentityRenameDeclared','renameKind'),('KindSuccessorIdentityDeclared','successorKind'),('KindOtherDeclared','otherLineageKind')]:add('missing-kind-classifier-'+n,lambda m,n=n,arg=arg:m['predicates'][n].remove([arg]),T=False,I=None)
 add('overlapping-rename-and-successor-kind',lambda m:(m['predicates']['KindSuccessorIdentityDeclared'].append(['renameKind']),m['predicates']['LineageSuccessorIdentityDeclared'].extend([['l0'],['l4']])),T=False,I=None)
 add('rename-changes-identity',lambda m:change(m,'epochIdentity','e1','id1'),T=False,I=None)
 add('rename-does-not-change-name',lambda m:change(m,'epochName','e1','old0'),T=False,I=None)
 add('successor-retains-same-identity',lambda m:change(m,'epochIdentity','e3','id1'),T=False,I=None)
 add('kind-specific-predecessor-kind-mismatch',lambda m:change(m,'epochSubjectKind','e0','contextKind'),T=False,I=None)
 add('kind-specific-successor-kind-mismatch',lambda m:change(m,'epochSubjectKind','e1','contextKind'),T=False,I=None)
 add('kind-specific-contract-kind-mismatch',lambda m:change(m,'contractSubjectKind','productContract','contextKind'),T=False,I=None)
 add('Context-contract-assigned-to-Product-by-analogy',lambda m:m['predicates']['ContractContextSpecificDeclared'].append(['productContract']),T=False,I=None)
 add('Context-kind-also-marked-Product',lambda m:m['predicates']['KindProductDeclared'].append(['contextKind']),T=False,I=None)
 add('general-contract-missing-covered-Product-kind',lambda m:m['predicates']['ContractCoversSubjectKindDeclared'].remove(['generalContract','productKind']),T=False,I=None)
 add('general-contract-missing-covered-Context-kind',lambda m:m['predicates']['ContractCoversSubjectKindDeclared'].remove(['generalContract','contextKind']),T=False,I=None)
 add('general-contract-classifier-disagrees',lambda m:m['predicates']['ContractGeneralizedDeclared'].remove(['generalContract']),T=False,I=None)
 targets={id(b.LINEAGE_FIELDS):'l0',id(b.EPOCH_FIELDS):'e0',id(b.DECISION_FIELDS):'d0',id(b.CONTRACT_FIELDS):'productContract'}
 for fields,carrier in b.GROUPS:
  arg=targets[id(fields)]
  for n,sort in fields.items():
   add('missing-exact-binding-'+n,lambda m,n=n,arg=arg:m['predicates'].update({n+'BindingDeclared':[x for x in m['predicates'][n+'BindingDeclared'] if x[0]!=arg]}),T=False,I=None)
   value=getfn(base_model(),n,arg);alt=next(x for x in base_model()['domains'][sort] if x!=value)
   add('conflicting-exact-binding-'+n,lambda m,n=n,arg=arg,alt=alt:m['predicates'][n+'BindingDeclared'].append([arg,alt]),T=False,I=None)
   declared='LineageApplicable' if sort=='LineageReference' else sort+'Declared'
   add('undeclared-selected-target-'+n,lambda m,declared=declared,value=value:m['predicates'][declared].remove([value]),T=False,I=None)
 selected={'LineageReference':'l0','LineageIdReference':'lid0','KindDefinitionReference':'productKind','EpochReference':'e0','IdentityReference':'id0','NameReference':'old0','LineageKindReference':'renameKind','DecisionReference':'d0','OwnerReference':'owner0','EvidenceReference':'ev0','NonEffectsReference':'nonEffects0','ContractReference':'productContract','ScopeReference':'productScope'}
 for sort,n in b.HANDLES.items():add('empty-selected-handle-'+sort,lambda m,n=n,value=selected[sort]:setfn(m,n,value,'empty'),T=False,I=None)
 add('malformed-empty-domain',lambda m:m['domains'].update(LineageReference=[]),error='empty-or-malformed-domain')
 add('malformed-missing-domain',lambda m:m['domains'].pop('EpochReference'),error='model-signature-denominator-mismatch')
 add('malformed-missing-function',lambda m:m['functions'].pop('lineagePredecessor'),error='model-signature-denominator-mismatch')
 add('malformed-partial-function',lambda m:m['functions']['lineagePredecessor'].pop(),error='nontotal-function')
 add('malformed-function-range',lambda m:setfn(m,'lineagePredecessor','l0','foreign'),error='ill-sorted-function-result')
 add('malformed-function-argument',lambda m:m['functions']['lineagePredecessor'][0].update(args=['foreign']),error='ill-sorted-model-tuple')
 add('malformed-predicate-range',lambda m:m['predicates']['LineageApplicable'].append(['foreign']),error='ill-sorted-model-tuple')
 add('malformed-predicate-arity',lambda m:m['predicates']['ContractCoversSubjectKindDeclared'].append(['generalContract']),error='ill-sorted-model-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.actor/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-IdentityLineage-model-controls/v1-candidate','status':'PASS-for-exact-authored-IdentityLineage-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Exact immutable typed evidence-backed lineage tuple,kind-specific/generalized contracts,endpoint and rename/successor declarations checked on supplied models;real continuity,immutable storage,identity/name/kind fidelity,owner authority,contract admission,evidence and whole proof pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
