"""Supplied exact Generated Output declaration models;no generator execution."""
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
 ds={'OutputReference':['o0','o1','oOutside'],'InputSetReference':['inputsMain','inputsOutside'],'InputReference':['inputA','inputB','inputOutside'],'GeneratorReference':['generatorMain','generatorOutside'],'RunReference':['run0First','run0Second','run1First','run1Second','runExtra','runOutside'],'LineageReference':['lineage0','lineage1','lineageExtra','lineageOutside'],'ParityReference':['parity0','parity1','parityOutside'],'ArtifactTypeContractReference':['contractAllowed','contractOutside'],'ByteStateReference':['inputStateA','inputStateB','generatorCode','outputState','outsideState'],'DigestReference':['digestA','digestB','generatorDigest','outputDigest','outsideDigest'],'SemanticIdentity':['identity0','identity1','inputIdentityA','inputIdentityB','generatorIdentity','outsideIdentity'],'VersionReference':['definitionVersion','inputVersion','generatorVersion','contractVersion','outsideVersion'],'OwnerReference':['ownerMain','ownerOutside'],'SourceReference':['sourceDefinition','sourceMain','sourceOutside'],'ScopeReference':['currentScope','outsideScope'],'TypeReference':['outputType','inputType','outsideType'],'Token':['empty','none','match','reference','canonicalClause','detail','other']}
 cs={'EMPTY':'empty','NONE':'none','MATCH':'match','CURRENT_SCOPE':'currentScope','CURRENT_DEFINITION_VERSION':'definitionVersion','CURRENT_SOURCE':'sourceDefinition'}
 def outside(x):return x.endswith('Outside')
 def out(x):return 'oOutside' if outside(x) else 'o1' if x.endswith('1') or x.startswith('run1') else 'o0'
 maps={}
 maps.update(outputIdentity=lambda x:'outsideIdentity' if outside(x) else 'identity1' if x=='o1' else 'identity0',outputDefinitionVersion=lambda x:'definitionVersion',outputOwner=lambda x:'ownerOutside' if outside(x) else 'ownerMain',outputSource=lambda x:'sourceOutside' if outside(x) else 'sourceDefinition',outputScope=lambda x:'outsideScope' if outside(x) else 'currentScope',outputType=lambda x:'outsideType' if outside(x) else 'outputType',outputEffect=lambda x:'none',outputInputSet=lambda x:'inputsOutside' if outside(x) else 'inputsMain',outputGenerator=lambda x:'generatorOutside' if outside(x) else 'generatorMain',outputGeneratorIdentity=lambda x:'outsideIdentity' if outside(x) else 'generatorIdentity',outputGeneratorVersion=lambda x:'outsideVersion' if outside(x) else 'generatorVersion',outputGeneratorDigest=lambda x:'outsideDigest' if outside(x) else 'generatorDigest',outputState=lambda x:'outsideState' if outside(x) else 'outputState',outputDigest=lambda x:'outsideDigest' if outside(x) else 'outputDigest',outputFirstRun=lambda x:'runOutside' if outside(x) else 'run1First' if x=='o1' else 'run0First',outputSecondRun=lambda x:'runOutside' if outside(x) else 'run1Second' if x=='o1' else 'run0Second',outputLineage=lambda x:'lineageOutside' if outside(x) else 'lineage1' if x=='o1' else 'lineage0',outputParity=lambda x:'parityOutside' if outside(x) else 'parity1' if x=='o1' else 'parity0',outputTypeContract=lambda x:'contractOutside' if outside(x) else 'contractAllowed')
 maps.update(inputSetNominee=lambda x:'inputOutside' if outside(x) else 'inputA',inputSetSource=lambda x:'sourceOutside' if outside(x) else 'sourceMain',inputIdentity=lambda x:'outsideIdentity' if outside(x) else 'inputIdentityB' if x=='inputB' else 'inputIdentityA',inputType=lambda x:'outsideType' if outside(x) else 'inputType',inputVersion=lambda x:'outsideVersion' if outside(x) else 'inputVersion',inputOwner=lambda x:'ownerOutside' if outside(x) else 'ownerMain',inputSource=lambda x:'sourceOutside' if outside(x) else 'sourceMain',inputState=lambda x:'outsideState' if outside(x) else 'inputStateB' if x=='inputB' else 'inputStateA',inputDigest=lambda x:'outsideDigest' if outside(x) else 'digestB' if x=='inputB' else 'digestA')
 maps.update(generatorIdentity=lambda x:'outsideIdentity' if outside(x) else 'generatorIdentity',generatorVersion=lambda x:'outsideVersion' if outside(x) else 'generatorVersion',generatorOwner=lambda x:'ownerOutside' if outside(x) else 'ownerMain',generatorSource=lambda x:'sourceOutside' if outside(x) else 'sourceMain',generatorCodeState=lambda x:'outsideState' if outside(x) else 'generatorCode',generatorCodeDigest=lambda x:'outsideDigest' if outside(x) else 'generatorDigest',generatorOutputType=lambda x:'outsideType' if outside(x) else 'outputType')
 maps.update(runGenerator=lambda x:'generatorOutside' if outside(x) else 'generatorMain',runInputSet=lambda x:'inputsOutside' if outside(x) else 'inputsMain',runState=lambda x:'outsideState' if outside(x) else 'outputState',runDigest=lambda x:'outsideDigest' if outside(x) else 'outputDigest',runSource=lambda x:'sourceOutside' if outside(x) else 'sourceDefinition')
 maps.update(lineageOutput=out,lineageInputSet=lambda x:'inputsOutside' if outside(x) else 'inputsMain',lineageGenerator=lambda x:'generatorOutside' if outside(x) else 'generatorMain',lineageGeneratorDigest=lambda x:'outsideDigest' if outside(x) else 'generatorDigest',lineageSource=lambda x:'sourceOutside' if outside(x) else 'sourceDefinition')
 maps.update(parityOutput=out,parityFirstRun=lambda x:'runOutside' if outside(x) else 'run1First' if x=='parity1' else 'run0First',paritySecondRun=lambda x:'runOutside' if outside(x) else 'run1Second' if x=='parity1' else 'run0Second',parityFirstDigest=lambda x:'outsideDigest' if outside(x) else 'outputDigest',paritySecondDigest=lambda x:'outsideDigest' if outside(x) else 'outputDigest',parityResult=lambda x:'match',paritySource=lambda x:'sourceOutside' if outside(x) else 'sourceDefinition',contractType=lambda x:'outsideType' if outside(x) else 'outputType',contractVersion=lambda x:'outsideVersion' if outside(x) else 'contractVersion',contractOwner=lambda x:'ownerOutside' if outside(x) else 'ownerMain',contractSource=lambda x:'sourceOutside' if outside(x) else 'sourceMain',contractCanonicalClause=lambda x:'canonicalClause',generatedState=lambda g,i:'outsideState' if outside(g) or outside(i) else 'outputState',stateDigest=lambda x:{'inputStateA':'digestA','inputStateB':'digestB','generatorCode':'generatorDigest','outputState':'outputDigest','outsideState':'outsideDigest'}[x])
 for sort,n in b.HANDLES.items():maps[n]=lambda x:'reference'
 assert maps.keys()==b.FUNCTIONS.keys()
 funcs={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(ds[s] for s in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};preds={n:[] for n in b.SIGNATURE}
 for sort in b.SORTS:
  if sort not in ['OutputReference','Token']:preds[sort+'Declared']=[[x] for x in ds[sort]]
 preds.update(OutputApplicable=[['o0'],['o1']],OutputInScopeDeclared=[['o0'],['o1']],GeneratedOutputDeclared=[['o0'],['o1']],OutputCanonicalDeclared=[['o1']],InputMemberDeclared=[['inputsMain','inputA'],['inputsMain','inputB']],InputCanonicalDeclared=[['inputA'],['inputB']],GeneratorGovernedDeclared=[['generatorMain']],RunForOutputDeclared=[['o0','run0First'],['o0','run0Second'],['o0','runExtra'],['o1','run1First'],['o1','run1Second']],LineageForOutputDeclared=[['o0','lineage0'],['o0','lineageExtra'],['o1','lineage1']],ParityForOutputDeclared=[['o0','parity0'],['o1','parity1']],OutputContractDeclared=[['o0','contractAllowed'],['o1','contractAllowed']],ContractAdmittedDeclared=[['contractAllowed']],ContractAllowsCanonicalDeclared=[['contractAllowed']],SourceCurrentDeclared=[['sourceDefinition'],['sourceMain']],SourceOwnerApprovedDeclared=[['sourceDefinition'],['sourceMain']],OutputActualAuthority=[['o1']])
 m={'domains':ds,'constants':cs,'functions':funcs,'predicates':preds};refresh(m);return m
def controls():
 rows=[]
 def add(name,mutation=lambda m:None,T=True,I=True,error=None):
  m=base_model();mutation(m);rows.append({'case_id':name,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 def change(m,n,arg,value):setfn(m,n,arg,value);refresh(m)
 add('noncanonical-and-explicit-contract-canonical-outputs')
 add('no-selected-outputs',lambda m:m['predicates'].update(OutputApplicable=[],OutputInScopeDeclared=[]),I=False)
 add('only-noncanonical-output-selected',lambda m:m['predicates'].update(OutputApplicable=[['o0']],OutputInScopeDeclared=[['o0']]),I=False)
 add('only-canonical-output-selected',lambda m:m['predicates'].update(OutputApplicable=[['o1']],OutputInScopeDeclared=[['o1']]),I=False)
 add('all-selected-outputs-noncanonical',lambda m:m['predicates'].update(OutputCanonicalDeclared=[]),I=False)
 add('both-selected-outputs-canonical-permitted',lambda m:m['predicates'].update(OutputCanonicalDeclared=[['o0'],['o1']]),I=False)
 add('one-exact-canonical-input',lambda m:m['predicates'].update(InputMemberDeclared=[['inputsMain','inputA']]),I=False)
 add('no-additional-run-record',lambda m:m['predicates'].update(RunForOutputDeclared=[x for x in m['predicates']['RunForOutputDeclared'] if x[-1]!='runExtra']),I=False)
 add('no-additional-lineage-record',lambda m:m['predicates'].update(LineageForOutputDeclared=[x for x in m['predicates']['LineageForOutputDeclared'] if x[-1]!='lineageExtra']),I=False)
 def same_runs(m):
  for o,p in [('o0','parity0'),('o1','parity1')]:setfn(m,'outputSecondRun',o,getfn(m,'outputFirstRun',o));setfn(m,'paritySecondRun',p,getfn(m,'parityFirstRun',p))
  refresh(m)
 add('same-run-reference-not-two-distinct-runs',same_runs,I=False)
 add('outside-second-authority-not-scoped',lambda m:m['predicates']['OutputIsSecondSemanticAuthorityDeclared'].append(['oOutside']))
 for n in b.ACTUAL:add('independently-supported-actual-'+n,lambda m,n=n:m['predicates']['OutputActual'+n].append(['o0']),I=False)
 for n in b.EXCLUDED:add('prohibited-'+n,lambda m,n=n:m['predicates'][n].append(['o0']),T=False,I=None)
 for name,predicate,item in [('missing-nominated-input','InputMemberDeclared',['inputsMain','inputA']),('extra-input-not-canonical','InputCanonicalDeclared',['inputB']),('missing-generator-governed','GeneratorGovernedDeclared',['generatorMain']),('missing-first-run','RunForOutputDeclared',['o0','run0First']),('missing-lineage','LineageForOutputDeclared',['o0','lineage0']),('missing-parity','ParityForOutputDeclared',['o0','parity0']),('canonical-contract-link-missing','OutputContractDeclared',['o1','contractAllowed']),('canonical-contract-not-admitted','ContractAdmittedDeclared',['contractAllowed']),('canonical-contract-no-permission','ContractAllowsCanonicalDeclared',['contractAllowed']),('source-not-current','SourceCurrentDeclared',['sourceMain']),('source-not-owner-approved','SourceOwnerApprovedDeclared',['sourceMain'])]:add(name,lambda m,predicate=predicate,item=item:m['predicates'][predicate].remove(item),T=False,I=None)
 for fields,carrier in b.GROUPS:
  for n,sort in fields.items():
   arg={'OutputReference':'o1' if n=='outputTypeContract' else 'o0','InputSetReference':'inputsMain','InputReference':'inputB','GeneratorReference':'generatorMain','RunReference':'runExtra','LineageReference':'lineageExtra','ParityReference':'parity0','ArtifactTypeContractReference':'contractAllowed'}[carrier]
   add('missing-exact-binding-'+n,lambda m,n=n,arg=arg:m['predicates'].update({n+'BindingDeclared':[x for x in m['predicates'][n+'BindingDeclared'] if x[0]!=arg]}),T=False,I=None)
   alt=next(x for x in base_model()['domains'][sort] if x!=getfn(base_model(),n,arg));add('conflicting-exact-binding-'+n,lambda m,n=n,arg=arg,alt=alt:m['predicates'][n+'BindingDeclared'].append([arg,alt]),T=False,I=None)
   if sort!='Token':add('empty-reference-handle-'+n,lambda m,n=n,arg=arg,sort=sort:setfn(m,b.HANDLES[sort],getfn(m,n,arg),'empty'),T=False,I=None)
   else:add('empty-token-'+n,lambda m,n=n,arg=arg:change(m,n,arg,'empty'),T=False,I=None)
 for n,arg,value in [('outputDefinitionVersion','o0','outsideVersion'),('outputScope','o0','outsideScope'),('outputEffect','o0','other'),('outputSource','o0','sourceOutside'),('outputGeneratorIdentity','o0','outsideIdentity'),('outputGeneratorVersion','o0','outsideVersion'),('outputGeneratorDigest','o0','outsideDigest'),('outputState','o0','outsideState'),('outputDigest','o0','outsideDigest'),('inputDigest','inputB','outsideDigest'),('generatorCodeDigest','generatorMain','outsideDigest'),('generatorOutputType','generatorMain','outsideType'),('runGenerator','runExtra','generatorOutside'),('runInputSet','runExtra','inputsOutside'),('runState','runExtra','outsideState'),('runDigest','runExtra','outsideDigest'),('runSource','runExtra','sourceOutside'),('lineageOutput','lineageExtra','o1'),('lineageInputSet','lineageExtra','inputsOutside'),('lineageGenerator','lineageExtra','generatorOutside'),('lineageGeneratorDigest','lineageExtra','outsideDigest'),('lineageSource','lineageExtra','sourceOutside'),('parityOutput','parity0','o1'),('parityFirstRun','parity0','run1First'),('paritySecondRun','parity0','run1Second'),('parityFirstDigest','parity0','outsideDigest'),('paritySecondDigest','parity0','outsideDigest'),('parityResult','parity0','other'),('paritySource','parity0','sourceOutside'),('contractType','contractAllowed','outsideType')]:add('typed-field-mismatch-'+n,lambda m,n=n,arg=arg,value=value:change(m,n,arg,value),T=False,I=None)
 add('hidden-invalid-run',lambda m:m['predicates']['RunForOutputDeclared'].append(['o0','runOutside']),T=False,I=None)
 add('hidden-invalid-lineage',lambda m:m['predicates']['LineageForOutputDeclared'].append(['o0','lineageOutside']),T=False,I=None)
 add('hidden-invalid-parity',lambda m:m['predicates']['ParityForOutputDeclared'].append(['o0','parityOutside']),T=False,I=None)
 add('hidden-invalid-canonical-contract',lambda m:m['predicates']['OutputContractDeclared'].append(['o1','contractOutside']),T=False,I=None)
 add('hidden-invalid-canonical-input',lambda m:m['predicates']['InputMemberDeclared'].append(['inputsMain','inputOutside']),T=False,I=None)
 for n,arg in [('outputInputSet','o0'),('outputGenerator','o0'),('outputFirstRun','o0'),('outputLineage','o0'),('outputTypeContract','o1')]:add('ill-sorted-result-'+n,lambda m,n=n,arg=arg:setfn(m,n,arg,'ill-sorted'),T=None,I=None,error='ill-sorted-function-result')
 add('empty-output-domain',lambda m:m['domains'].update(OutputReference=[]),T=None,I=None,error='empty-or-malformed-domain')
 add('missing-function-denominator',lambda m:m['functions'].pop('outputGenerator'),T=None,I=None,error='model-signature-denominator-mismatch')
 add('duplicate-function-tuple',lambda m:m['functions']['outputInputSet'].append(copy.deepcopy(m['functions']['outputInputSet'][0])),T=None,I=None,error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.four-facet-artifact-invariant/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-GeneratedOutput-model-controls/v1-candidate','status':'PASS-for-exact-authored-GeneratedOutput-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Typed exact input,generator,run,lineage,parity and conditional canonical-contract declarations checked on supplied models;actual execution,contract authenticity,authority,fidelity and whole proof remain pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
