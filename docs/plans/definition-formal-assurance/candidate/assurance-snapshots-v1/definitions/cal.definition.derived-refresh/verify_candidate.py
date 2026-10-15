"""Supplied unchanged-input,generator,parity,validation and tooling models."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def setfn(m,n,arg,value):
 args=arg if isinstance(arg,list) else [arg];next(x for x in m['functions'][n] if x['args']==args)['value']=value
def getfn(m,n,*args):return next(x['value'] for x in m['functions'][n] if x['args']==list(args))
def refresh(m):
 p=m['predicates'];selected=[x[0] for x in p['RefreshApplicable']]
 for fields,carrier,objects in [(b.FACETS,'RefreshReference',selected),(b.BINDING_FIELDS,'GeneratorBindingReference',sorted({getfn(m,'refreshBinding',r) for r in selected})),(b.RECEIPT_FIELDS,'ValidationReceiptReference',sorted({getfn(m,'refreshReceipt',r) for r in selected})),(b.PARITY_FIELDS,'ParityResultReference',sorted({getfn(m,'refreshParity',r) for r in selected})),(b.CHANGE_FIELDS,'ToolingChangeReference',[x[0] for x in p['ToolingChangeInScopeDeclared']])]:
  for n in fields:p[n+'BindingDeclared']=[[x,getfn(m,n,x)] for x in objects]
def base_model():
 ds={'RefreshReference':['rMain','rUpdated','rOutside'],'InputReference':['inputMain','inputOutside'],'GeneratorReference':['gMain','gUpdated','gOutside'],'GeneratorBindingReference':['bindingMain','bindingUpdated','bindingOutside'],'ProjectionReference':['pMain','pMainRepeat','pUpdated','pUpdatedRepeat','pOutside'],'ByteStateReference':['canonicalState','mainCodeState','updatedCodeState','mainOutputState','updatedOutputState','outsideState'],'DigestReference':['canonicalDigest','mainCodeDigest','updatedCodeDigest','mainOutputDigest','updatedOutputDigest','outsideDigest'],'SemanticIdentity':['inputMeaning','generatorMeaning','outsideMeaning'],'VersionReference':['inputVersion','mainVersion','updatedVersion','outsideVersion'],'ValidationReceiptReference':['receiptMain','receiptUpdated','receiptOutside'],'ValidationContractReference':['contractMain','contractUpdated','contractOutside'],'ParityResultReference':['parityMain','parityUpdated','parityOutside'],'ToolingChangeReference':['changeMain','changeOutside'],'ToolingWorkflowReference':['workflowMain','workflowOutside'],'OwnerReference':['ownerMain','ownerOutside'],'EpochReference':['existingEpoch','outsideEpoch'],'RevisionReference':['existingRevision','outsideRevision'],'DecisionReference':['existingDecision','outsideDecision'],'SourceReference':['sourceApproved','sourceOutside'],'ScopeReference':['currentScope','outsideScope'],'TypeReference':['inputType','outputType','outsideType'],'Token':['empty','none','generatedOnly','match','reference','other']}
 cs={'EMPTY':'empty','NONE':'none','GENERATED_ONLY':'generatedOnly','MATCH':'match','CURRENT_SCOPE':'currentScope'}
 def suffix(x):return 'Outside' if x.endswith('Outside') else 'Updated' if 'Updated' in x else 'Main'
 def proj(x):return 'p'+suffix(x)
 maps={}
 maps.update(refreshInput=lambda x:'inputOutside' if suffix(x)=='Outside' else 'inputMain',refreshInputDigest=lambda x:'outsideDigest' if suffix(x)=='Outside' else 'canonicalDigest',refreshGenerator=lambda x:'g'+suffix(x),refreshBinding=lambda x:'binding'+suffix(x),refreshGeneratorIdentity=lambda x:'outsideMeaning' if suffix(x)=='Outside' else 'generatorMeaning',refreshGeneratorDigest=lambda x:'outsideDigest' if suffix(x)=='Outside' else suffix(x).lower()+'CodeDigest',refreshOutput=proj,refreshOutputDigest=lambda x:'outsideDigest' if suffix(x)=='Outside' else suffix(x).lower()+'OutputDigest',refreshParity=lambda x:'parity'+suffix(x),refreshReceipt=lambda x:'receipt'+suffix(x),refreshContract=lambda x:'contract'+suffix(x),refreshOwner=lambda x:'ownerOutside' if suffix(x)=='Outside' else 'ownerMain',refreshSource=lambda x:'sourceOutside' if suffix(x)=='Outside' else 'sourceApproved',refreshScope=lambda x:'outsideScope' if suffix(x)=='Outside' else 'currentScope',refreshEffect=lambda x:'none')
 maps.update(bindingGenerator=lambda x:'g'+suffix(x),bindingIdentity=lambda x:'outsideMeaning' if suffix(x)=='Outside' else 'generatorMeaning',bindingDigest=lambda x:'outsideDigest' if suffix(x)=='Outside' else suffix(x).lower()+'CodeDigest',bindingVersion=lambda x:'outsideVersion' if suffix(x)=='Outside' else suffix(x).lower()+'Version',bindingSource=lambda x:'sourceOutside' if suffix(x)=='Outside' else 'sourceApproved')
 maps.update(receiptRefresh=lambda x:'r'+suffix(x),receiptInput=lambda x:maps['refreshInput']('r'+suffix(x)),receiptGenerator=lambda x:'g'+suffix(x),receiptOutput=proj,receiptContract=lambda x:'contract'+suffix(x),receiptInputDigest=lambda x:maps['refreshInputDigest']('r'+suffix(x)),receiptGeneratorDigest=lambda x:maps['refreshGeneratorDigest']('r'+suffix(x)),receiptOutputDigest=lambda x:maps['refreshOutputDigest']('r'+suffix(x)),receiptParity=lambda x:'parity'+suffix(x),receiptEffect=lambda x:'none')
 maps.update(parityRefresh=lambda x:'r'+suffix(x),parityFirst=proj,paritySecond=lambda x:proj(x) if suffix(x)=='Outside' else proj(x)+'Repeat',parityFirstDigest=lambda x:maps['refreshOutputDigest']('r'+suffix(x)),paritySecondDigest=lambda x:maps['refreshOutputDigest']('r'+suffix(x)),parityResult=lambda x:'match')
 maps.update(changeBeforeGenerator=lambda x:'gMain',changeAfterGenerator=lambda x:'gUpdated',changeWorkflow=lambda x:'workflow'+suffix(x),changeOwner=lambda x:'ownerOutside' if suffix(x)=='Outside' else 'ownerMain',changeSource=lambda x:'sourceOutside' if suffix(x)=='Outside' else 'sourceApproved')
 maps.update(inputBeforeState=lambda x:'outsideState' if suffix(x)=='Outside' else 'canonicalState',inputAfterState=lambda x:'outsideState' if suffix(x)=='Outside' else 'canonicalState',inputBeforeDigest=lambda x:'outsideDigest' if suffix(x)=='Outside' else 'canonicalDigest',inputAfterDigest=lambda x:'outsideDigest' if suffix(x)=='Outside' else 'canonicalDigest',inputMeaning=lambda x:'outsideMeaning' if suffix(x)=='Outside' else 'inputMeaning',inputType=lambda x:'outsideType' if suffix(x)=='Outside' else 'inputType',inputVersion=lambda x:'outsideVersion' if suffix(x)=='Outside' else 'inputVersion',inputSource=lambda x:'sourceOutside' if suffix(x)=='Outside' else 'sourceApproved')
 maps.update(generatorIdentity=lambda x:'outsideMeaning' if suffix(x)=='Outside' else 'generatorMeaning',generatorVersion=lambda x:'outsideVersion' if suffix(x)=='Outside' else suffix(x).lower()+'Version',generatorCodeState=lambda x:'outsideState' if suffix(x)=='Outside' else suffix(x).lower()+'CodeState',generatorCodeDigest=lambda x:'outsideDigest' if suffix(x)=='Outside' else suffix(x).lower()+'CodeDigest',generatorOutputType=lambda x:'outsideType' if suffix(x)=='Outside' else 'outputType',generatedState=lambda g,i:'outsideState' if suffix(g)=='Outside' or i=='inputOutside' else suffix(g).lower()+'OutputState',stateDigest=lambda x:{'canonicalState':'canonicalDigest','mainCodeState':'mainCodeDigest','updatedCodeState':'updatedCodeDigest','mainOutputState':'mainOutputDigest','updatedOutputState':'updatedOutputDigest','outsideState':'outsideDigest'}[x])
 maps.update(projectionInput=lambda x:maps['refreshInput']('r'+suffix(x)),projectionGenerator=lambda x:'g'+suffix(x),projectionState=lambda x:'outsideState' if suffix(x)=='Outside' else suffix(x).lower()+'OutputState',projectionDigest=lambda x:maps['refreshOutputDigest']('r'+suffix(x)),projectionMeaning=lambda x:'outsideMeaning' if suffix(x)=='Outside' else 'inputMeaning',projectionType=lambda x:'outsideType' if suffix(x)=='Outside' else 'outputType',projectionEffect=lambda x:'none',projectionPolicy=lambda x:'generatedOnly',contractSource=lambda x:'sourceOutside' if suffix(x)=='Outside' else 'sourceApproved',workflowOwner=lambda x:'ownerOutside' if suffix(x)=='Outside' else 'ownerMain',workflowSource=lambda x:'sourceOutside' if suffix(x)=='Outside' else 'sourceApproved')
 for s,n in b.HANDLES.items():maps[n]=lambda x:'reference'
 assert maps.keys()==b.FUNCTIONS.keys(),(maps.keys()-b.FUNCTIONS.keys(),b.FUNCTIONS.keys()-maps.keys())
 funcs={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(ds[s] for s in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};p={n:[] for n in b.SIGNATURE}
 for s in b.SORTS:
  if s not in ['RefreshReference','Token']:p[s+'Declared']=[[x] for x in ds[s]]
 p.update(RefreshApplicable=[['rMain'],['rUpdated']],RefreshInScopeDeclared=[['rMain'],['rUpdated']],DerivedRefreshDeclared=[['rMain'],['rUpdated']],InputCanonicalDeclared=[['inputMain']],ProjectionDeclared=[[x] for x in ds['ProjectionReference']],SourceCurrentDeclared=[['sourceApproved']],SourceOwnerApprovedDeclared=[['sourceApproved']],GenerationDeclared=[['gMain','inputMain',x] for x in ['pMain','pMainRepeat']]+[['gUpdated','inputMain',x] for x in ['pUpdated','pUpdatedRepeat']],ValidationReceiptValidDeclared=[['receiptMain'],['receiptUpdated']],ValidationDeclared=[['r'+s,'p'+s,'contract'+s,'receipt'+s] for s in ['Main','Updated']],ToolingChangeInScopeDeclared=[['changeMain']],SeparateToolingWorkflowDeclared=[['changeMain','workflowMain']],ExistingEpochDeclared=[['existingEpoch']],ExistingRevisionDeclared=[['existingRevision']],ExistingDecisionDeclared=[['existingDecision']],CreatedEpochDeclared=[['rOutside','outsideEpoch']],RefreshActualToolingAuthorization=[['rUpdated']])
 m={'domains':ds,'constants':cs,'functions':funcs,'predicates':p};refresh(m);return m
def controls():
 rows=[]
 def add(name,mutation=lambda m:None,T=True,I=True,error=None):
  m=base_model();mutation(m);rows.append({'case_id':name,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 def change(m,n,arg,value):setfn(m,n,arg,value);refresh(m)
 add('exact-unchanged-input-generator-parity-validation-and-separate-tooling')
 add('no-selected-refreshes',lambda m:m['predicates'].update(RefreshApplicable=[],RefreshInScopeDeclared=[],ToolingChangeInScopeDeclared=[]),I=False)
 add('no-tooling-change-witness',lambda m:m['predicates'].update(ToolingChangeInScopeDeclared=[]),I=False)
 add('only-updated-refresh-selected',lambda m:(m['predicates'].update(RefreshApplicable=[['rUpdated']],RefreshInScopeDeclared=[['rUpdated']]),refresh(m)),I=False)
 add('only-main-refresh-selected',lambda m:(m['predicates'].update(RefreshApplicable=[['rMain']],RefreshInScopeDeclared=[['rMain']]),refresh(m)),I=False)
 add('same-output-reference-for-repeat',lambda m:(change(m,'paritySecond','parityMain','pMain'),change(m,'paritySecond','parityUpdated','pUpdated')),I=False)
 for rel,ev in [('CreatedRevisionDeclared','outsideRevision'),('CreatedDecisionDeclared','outsideDecision')]:add('independent-outside-'+rel,lambda m,rel=rel,ev=ev:m['predicates'][rel].append(['rOutside',ev]))
 for n in b.ACTUAL:add('independently-supported-actual-'+n,lambda m,n=n:m['predicates']['RefreshActual'+n].append(['rMain']),I=False)
 for n in b.EXCLUDED:add('prohibited-'+n,lambda m,n=n:m['predicates'][n].append(['rMain']),T=False,I=None)
 for fields,carrier,label in [(b.FACETS,'rMain','refresh'),(b.BINDING_FIELDS,'bindingMain','generator'),(b.RECEIPT_FIELDS,'receiptMain','receipt'),(b.PARITY_FIELDS,'parityMain','parity'),(b.CHANGE_FIELDS,'changeMain','tooling')]:
  for n,s in fields.items():
   add('missing-'+label+'-binding-'+n,lambda m,n=n:m['predicates'].update({n+'BindingDeclared':m['predicates'][n+'BindingDeclared'][1:]}),T=False,I=None)
   add('conflicting-'+label+'-binding-'+n,lambda m,n=n,s=s,carrier=carrier:m['predicates'][n+'BindingDeclared'].append([carrier,'other' if s=='Token' else m['domains'][s][-1]]),T=False,I=None)
 add('changed-byte-state-with-equal-digest',lambda m:(setfn(m,'inputAfterState','inputMain','outsideState'),setfn(m,'stateDigest','outsideState','canonicalDigest')),T=False,I=None)
 add('changed-input-digest',lambda m:setfn(m,'inputAfterDigest','inputMain','outsideDigest'),T=False,I=None)
 add('input-not-canonical',lambda m:m['predicates'].update(InputCanonicalDeclared=[]),T=False,I=None)
 add('input-source-mismatch',lambda m:setfn(m,'inputSource','inputMain','sourceOutside'),T=False,I=None)
 for rel in ['SourceCurrentDeclared','SourceOwnerApprovedDeclared','ValidationReceiptValidDeclared']:add('missing-'+rel,lambda m,rel=rel:m['predicates'].update({rel:[]}),T=False,I=None)
 for n,val in [('bindingGenerator','gUpdated'),('bindingIdentity','inputMeaning'),('bindingDigest','updatedCodeDigest'),('bindingVersion','updatedVersion'),('bindingSource','sourceOutside')]:add('generator-binding-mismatch-'+n,lambda m,n=n,val=val:change(m,n,'bindingMain',val),T=False,I=None)
 for n,val in [('generatorIdentity','inputMeaning'),('generatorVersion','updatedVersion'),('generatorCodeState','updatedCodeState'),('generatorCodeDigest','updatedCodeDigest'),('generatorOutputType','outsideType')]:add('generator-function-mismatch-'+n,lambda m,n=n,val=val:setfn(m,n,'gMain',val),T=False,I=None)
 for rel in ['ProjectionCanonicalDeclared','ProjectionDefinesCanonicalMeaningDeclared']:add('projection-forbidden-'+rel,lambda m,rel=rel:m['predicates'][rel].append(['pMain']),T=False,I=None)
 for n,val in [('projectionInput','inputOutside'),('projectionGenerator','gUpdated'),('projectionState','updatedOutputState'),('projectionDigest','updatedOutputDigest'),('projectionMeaning','outsideMeaning'),('projectionType','outsideType'),('projectionEffect','other'),('projectionPolicy','other')]:add('projection-mismatch-'+n,lambda m,n=n,val=val:setfn(m,n,'pMain',val),T=False,I=None)
 add('hidden-generated-result-wrong-state',lambda m:m['predicates']['GenerationDeclared'].append(['gMain','inputMain','pUpdated']),T=False,I=None)
 add('missing-nominated-generation',lambda m:m['predicates'].update(GenerationDeclared=m['predicates']['GenerationDeclared'][1:]),T=False,I=None)
 add('missing-second-generation',lambda m:m['predicates'].update(GenerationDeclared=[x for x in m['predicates']['GenerationDeclared'] if x[-1]!='pMainRepeat']),T=False,I=None)
 add('generated-function-wrong-state',lambda m:setfn(m,'generatedState',['gMain','inputMain'],'updatedOutputState'),T=False,I=None)
 for n,val in [('parityRefresh','rUpdated'),('parityFirst','pUpdated'),('paritySecond','pUpdatedRepeat'),('parityFirstDigest','updatedOutputDigest'),('paritySecondDigest','updatedOutputDigest'),('parityResult','none')]:add('parity-mismatch-'+n,lambda m,n=n,val=val:change(m,n,'parityMain',val),T=False,I=None)
 for n,val in [('receiptRefresh','rUpdated'),('receiptInput','inputOutside'),('receiptGenerator','gUpdated'),('receiptOutput','pUpdated'),('receiptContract','contractUpdated'),('receiptInputDigest','outsideDigest'),('receiptGeneratorDigest','updatedCodeDigest'),('receiptOutputDigest','updatedOutputDigest'),('receiptParity','parityUpdated'),('receiptEffect','match')]:add('receipt-mismatch-'+n,lambda m,n=n,val=val:change(m,n,'receiptMain',val),T=False,I=None)
 add('contract-source-mismatch',lambda m:setfn(m,'contractSource','contractMain','sourceOutside'),T=False,I=None)
 add('hidden-validation-tuple',lambda m:m['predicates']['ValidationDeclared'].append(['rMain','pMainRepeat','contractMain','receiptMain']),T=False,I=None)
 add('missing-validation-tuple',lambda m:m['predicates'].update(ValidationDeclared=m['predicates']['ValidationDeclared'][1:]),T=False,I=None)
 for rel,ev in [('CreatedEpochDeclared','existingEpoch'),('CreatedRevisionDeclared','existingRevision'),('CreatedDecisionDeclared','existingDecision')]:add('selected-refresh-creates-'+rel,lambda m,rel=rel,ev=ev:m['predicates'][rel].append(['rMain',ev]),T=False,I=None)
 for n,val in [('changeAfterGenerator','gMain'),('changeOwner','ownerOutside'),('changeSource','sourceOutside')]:add('tooling-mismatch-'+n,lambda m,n=n,val=val:change(m,n,'changeMain',val),T=False,I=None)
 for n,val in [('workflowOwner','ownerOutside'),('workflowSource','sourceOutside')]:add('workflow-mismatch-'+n,lambda m,n=n,val=val:setfn(m,n,'workflowMain',val),T=False,I=None)
 add('missing-separate-tooling-workflow',lambda m:m['predicates'].update(SeparateToolingWorkflowDeclared=[]),T=False,I=None)
 add('hidden-separate-tooling-workflow',lambda m:m['predicates']['SeparateToolingWorkflowDeclared'].append(['changeMain','workflowOutside']),T=False,I=None)
 add('refresh-scope-mismatch',lambda m:change(m,'refreshScope','rMain','outsideScope'),T=False,I=None)
 add('refresh-effect-mismatch',lambda m:change(m,'refreshEffect','rMain','match'),T=False,I=None)
 add('missing-derived-refresh-classification',lambda m:m['predicates'].update(DerivedRefreshDeclared=[]),T=False,I=None)
 add('in-scope-not-applicable',lambda m:m['predicates']['RefreshInScopeDeclared'].append(['rOutside']),T=False,I=None)
 for n in ['refreshInput','bindingGenerator','projectionState','receiptGenerator','generatedState']:add('malformed-output-'+n,lambda m,n=n:m['functions'][n][0].update(value='not-in-sort'),T=None,I=None,error='ill-sorted-function-result')
 add('malformed-empty-refresh-domain',lambda m:m['domains'].update(RefreshReference=[]),T=None,I=None,error='empty-or-malformed-domain')
 add('malformed-missing-function',lambda m:m['functions'].pop('generatedState'),T=None,I=None,error='model-signature-denominator-mismatch')
 add('malformed-duplicate-function-tuple',lambda m:m['functions']['generatedState'].append(copy.deepcopy(m['functions']['generatedState'][0])),T=None,I=None,error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.canonical-representation-invariant/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-DerivedRefresh-model-controls/v1-candidate','status':'PASS-for-exact-authored-DerivedRefresh-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Typed exact unchanged-input,generator,projection,parity,validation and tooling declarations checked on supplied finite models;actual execution,computed digests,authenticity,authority,source fidelity and whole proof remain pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
