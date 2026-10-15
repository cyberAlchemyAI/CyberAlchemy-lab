"""Independent finite checks of exact answer binding, display tokens and stability."""
import itertools,json
import build_candidate as b
import verifier as v
def load(name):return json.loads((b.UNIT/name).read_bytes())
def base_model():
 domains={sort:[sort+'-a',sort+'-b'] for sort in b.SORTS};domains.update(Value=['v1','v2'],Axis=['a1','a2'],SchemeVersion=['sv1','sv2'],CommonToken=['id1','id2','label','new-label'],MeaningToken=['m1','m2'],DefinitionVersion=['selected-def','answer-def','successor-def'],PolicyRef=['policy','other-policy'],State=['before','after'],Use=['use'])
 functions={n:[{'args':list(xs),'value':domains[res][0]} for xs in itertools.product(*[domains[s] for s in args])] for n,(args,res) in b.FUNCTIONS.items()}
 for n in ['axisAt','identityAt','meaningAt']:
  for row in functions[n]:row['value']={'axisAt':'a','identityAt':'id','meaningAt':'m'}[n]+row['args'][0][-1]
 for row in functions['labelAt']:row['value']='new-label' if row['args']==['v1','after'] else 'label'
 for row in functions['definitionAt']:row['value']='answer-def'
 predicates={n:[] for n in b.SIGNATURE}
 for n in ['ClassificationValue','GovernedRecord','BoundedScope','GovernedAllowedAnswer','HasMeaningContract','HasApplicabilityContract','HasExclusionsContract','HasMappingsContract']:predicates[n]=[['v1'],['v2']]
 predicates.update(PresentValue=[list(xs) for xs in itertools.product(['v1','v2'],['before','after'])],Binding=[[val,axis,'sv1',s] for val,axis in [('v1','a1'),('v2','a2')] for s in ['before','after']],AxisDeclaredIn=[['a1','sv1'],['a2','sv1']],AllowedAnswer=[['v1','a1','sv1'],['v2','a2','sv1']],DeclaredPolicy=[['v1','policy'],['v2','policy']],AllowedLabelChange=[['v1','before','after']],UsesClassificationValue=[['use']])
 return {'domains':domains,'constants':{'selectedDefinition':'selected-def'},'functions':functions,'predicates':predicates}
def setvalue(m,n,args,value):next(x for x in m['functions'][n] if x['args']==args)['value']=value
def controls():
 rows=[]
 def add(name,change,T=True,I=True,error=None):
  m=base_model();change(m);rows.append({'case_id':name,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('same-display-label-distinct-axes-identities-meanings-with-pure-change',lambda m:None)
 add('governed-identity-alternative-to-record-valid',lambda m:m['predicates'].update(GovernedRecord=[],GovernedIdentity=[['v1'],['v2']]))
 add('neither-governed-record-nor-identity-rejected',lambda m:m['predicates'].update(GovernedRecord=[]),False)
 for n in ['BoundedScope','GovernedAllowedAnswer','HasMeaningContract','HasApplicabilityContract','HasExclusionsContract','HasMappingsContract']:add('missing-'+n,lambda m,n=n:m['predicates'].__setitem__(n,[['v1']]),False)
 for n in b.POLICIES:add('undeclared-'+n+'-policy',lambda m,n=n:setvalue(m,n+'Policy',['v2'],'other-policy'),False)
 add('axis-not-declared-in-exact-scheme',lambda m:m['predicates'].update(AxisDeclaredIn=[['a1','sv1']]),False)
 add('answer-not-allowed-under-exact-axis-and-version',lambda m:m['predicates'].update(AllowedAnswer=[['v1','a2','sv1'],['v2','a2','sv1']]),False)
 add('missing-present-value-binding',lambda m:m['predicates']['Binding'].remove(['v1','a1','sv1','before']),False)
 add('two-axis-bindings-for-one-present-value-rejected',lambda m:m['predicates']['Binding'].append(['v1','a2','sv1','before']),False)
 add('two-scheme-bindings-for-one-present-value-rejected',lambda m:m['predicates']['Binding'].append(['v1','a1','sv2','before']),False)
 add('binding-asserted-for-nonpresent-value',lambda m:m['predicates']['PresentValue'].remove(['v2','before']),False)
 add('label-only-coalescence-does-not-follow-common-display',lambda m:m['predicates'].update(AllowedLabelOnlyCoalescence=[['v1','v2','before']]),False)
 add('reverse-label-only-coalescence-also-rejected',lambda m:m['predicates'].update(AllowedLabelOnlyCoalescence=[['v2','v1','before']]),False)
 def other_version(m):
  for row in m['functions']['schemeAt']:
   if row['args'][0]=='v2':row['value']='sv2'
  m['predicates']['AxisDeclaredIn']=[['a1','sv1'],['a2','sv2']];m['predicates']['AllowedAnswer']=[['v1','a1','sv1'],['v2','a2','sv2']]
  for row in m['predicates']['Binding']:
   if row[0]=='v2':row[2]='sv2'
 add('same-label-across-exact-versions-allowed-with-separate-bindings',other_version)
 for n,value in [('axisAt','a2'),('schemeAt','sv2'),('identityAt','id2'),('meaningAt','m2'),('definitionAt','successor-def')]:add('claimed-pure-display-change-alters-'+n,lambda m,n=n,value=value:setvalue(m,n,['v1','after'],value),False)
 add('claimed-display-change-deletes-value',lambda m:m['predicates']['PresentValue'].remove(['v1','after']),False)
 add('display-change-requires-present-input',lambda m:m['predicates']['PresentValue'].remove(['v1','before']),False)
 def no_op(m):setvalue(m,'labelAt',['v1','after'],'label')
 add('permitted-noop-does-not-satisfy-required-display-variation',no_op,True,False)
 def literal_id_label(m):
  for s in ['before','after']:setvalue(m,'identityAt',['v1',s],'label')
 add('identity-token-may-lexically-match-display-without-label-key-rule',literal_id_label)
 def distinct_policy(m):
  for val in ['v1','v2']:setvalue(m,'mappingPolicy',[val],'other-policy')
  m['predicates']['DeclaredPolicy'] += [['v1','other-policy'],['v2','other-policy']]
 add('separate-policy-reference-permitted-not-mandatory',distinct_policy)
 def successor_use(m):setvalue(m,'useDefinition',['use'],'successor-def');m['predicates']['AdmittedDefinitionSuccessor']=[['successor-def']]
 add('use-resolves-separately-admitted-definition-successor',successor_use)
 add('same-term-label-not-unadmitted-definition-successor',lambda m:setvalue(m,'useDefinition',['use'],'successor-def'),False)
 add('no-display-action-vacuous-frame-fails-required-action-I',lambda m:m['predicates'].update(AllowedLabelChange=[]),True,False)
 add('no-definition-use-vacuous-T-fails-required-use-I',lambda m:m['predicates'].update(UsesClassificationValue=[]),True,False)
 def different_labels(m):setvalue(m,'labelAt',['v2','before'],'id2');setvalue(m,'labelAt',['v2','after'],'id2')
 add('no-colliding-label-witness-fails-selected-nonvacuity-I',different_labels,True,False)
 def same_meaning(m):
  for s in ['before','after']:setvalue(m,'meaningAt',['v2',s],'m1')
 add('same-meaning-not-forbidden-universally-but-fails-distinction-witness-I',same_meaning,True,False)
 def no_values(m):
  for n in ['ClassificationValue','PresentValue','Binding','AllowedLabelChange']:m['predicates'][n]=[]
 add('no-values-vacuous-T-fails-connected-I',no_values,True,False)
 for n in b.OUTCOMES:add('separately-supported-outcome-allowed-'+n,lambda m,n=n:m['predicates'].__setitem__(n,[['v1'],['v2']]))
 add('nontotal-identity-selector',lambda m:m['functions']['identityAt'].pop(),error='nontotal-function')
 add('ill-sorted-axis-result',lambda m:setvalue(m,'axisAt',['v1','after'],'v2'),error='ill-sorted-function-result')
 add('duplicate-present-value-tuple',lambda m:m['predicates']['PresentValue'].append(['v1','before']),error='duplicate-predicate-tuple')
 add('malformed-binding-arity',lambda m:m['predicates'].update(Binding=[['v1','a1','sv1']]),error='ill-sorted-model-tuple')
 add('ill-sorted-selected-definition-constant',lambda m:m['constants'].update(selectedDefinition='sv1'),error='ill-sorted-constant')
 return rows
def qualify(model,ids):return {bucket:{ids[n]:value for n,value in model[bucket].items()} for bucket in ['domains','constants','functions','predicates']}
def verify(write=False):
    context=load('context.json');b.unchanged(context['sources']);snap=b.snapshot();b.r.verify(snap,b.ROOT)
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
            if case['expected_error'] is not None or (t,i)!=(case['expected_T'],case['expected_I']):raise ValueError('Wrong authored control: '+case['case_id']+' '+str((t,i)))
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
    prior=json.loads((b.BASE/'definitions/cal.definition.classification-scheme/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-classification-value-model-controls/v1-candidate','status':'PASS-for-exact-authored-classification-value-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent authored finite versioned-answer models and nine targets outside T. Exact answer/axis/version binding, common-carrier display/identity tokens and selected stable display-change frames are checked; no owner fidelity, world value correctness, immutable-assignment implementation, statistical independence, native enumeration or whole-definition acceptance.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
