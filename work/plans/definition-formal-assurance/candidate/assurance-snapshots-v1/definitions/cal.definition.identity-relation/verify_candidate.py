"""Independent finite edge/endpoint/authority and relation-removal denotation."""
import itertools
import json
import build_candidate as b
import verifier as v

def load(name):return json.loads((b.UNIT/name).read_bytes())
def base_model():
    domains={sort:[sort+'-a',sort+'-b'] for sort in b.SORTS}
    domains.update(Relation=['r','u'],Identity=['edge-r','edge-u','a','z'],State=['s0','s1'],AuthorityState=['authority-a','authority-z'])
    functions={}
    for n,(args,sort) in b.FUNCTIONS.items():functions[n]=[{'args':list(xs),'value':domains[sort][0]} for xs in itertools.product(*[domains[x] for x in args])]
    for row in functions['relationIdentity']:row['value']='edge-r' if row['args'][0]=='r' else 'edge-u'
    for n in ['sourceEndpoint','sourceAt']:
        for row in functions[n]:row['value']='a'
    for n in ['targetEndpoint','targetAt']:
        for row in functions[n]:row['value']='z'
    for row in functions['authorityAt']:row['value']='authority-z' if row['args'][0]=='z' else 'authority-a'
    predicates={n:[] for n in b.SIGNATURE}
    for n in b.REQUIRED:predicates[n]=[['r']]
    predicates.update(ResolvableIdentity=[['a'],['z']],IndependentIdentity=[['a'],['z']],DeclaredInterpretation=[['Kind-a']],DeclaredDirection=[['Kind-a']],GeneratedProjection=[['Label-a']],HasEvidence=[['r','EvidenceRef-a']],RelationPresent=[['r','s0']],EndpointPresent=[[i,s] for i,s in itertools.product(['a','z'],['s0','s1'])],AllowedRelationStep=[['r','s0','s1']],RemovalStep=[['r','s0','s1']],DerivedLabel=[['Label-a','r']])
    return {'domains':domains,'constants':{'initialState':'s0'},'functions':functions,'predicates':predicates}
def setvalue(m,function,args,value):next(x for x in m['functions'][function] if x['args']==args)['value']=value
def controls():
    rows=[]
    def add(name,change,T=True,I=True,error=None):
        m=base_model();change(m);rows.append({'case_id':name,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
    add('governed-directed-edge-independent-authority-and-preserved-removal',lambda m:None)
    for n in b.REQUIRED[1:]:add('missing-'+n,lambda m,n=n:m['predicates'].__setitem__(n,[]),False,False)
    for n in ['HasEvidence','DeclaredInterpretation','DeclaredDirection','RelationPresent']:add('missing-'+n,lambda m,n=n:m['predicates'].__setitem__(n,[]),False,False)
    for n in ['ResolvableIdentity','IndependentIdentity']:add('target-missing-'+n,lambda m,n=n:m['predicates'].__setitem__(n,[['a']]),False,False)
    add('missing-initial-target-presence',lambda m:m['predicates']['EndpointPresent'].remove(['z','s0']),False,False)
    add('initial-source-must-match-explicit-endpoint',lambda m:setvalue(m,'sourceAt',['r','s0'],'z'),False)
    add('initial-target-must-match-explicit-endpoint',lambda m:setvalue(m,'targetAt',['r','s0'],'a'),False)
    add('edge-id-cannot-collapse-into-source-identity',lambda m:setvalue(m,'relationIdentity',['r'],'a'),False)
    add('edge-id-cannot-collapse-into-target-identity',lambda m:setvalue(m,'relationIdentity',['r'],'z'),False)
    add('allowed-change-cannot-replace-source',lambda m:setvalue(m,'sourceAt',['r','s1'],'z'),False)
    add('allowed-change-cannot-merge-target',lambda m:setvalue(m,'targetAt',['r','s1'],'a'),False)
    add('allowed-change-cannot-transfer-source-authority',lambda m:setvalue(m,'authorityAt',['a','s1'],'authority-z'),False)
    add('allowed-change-cannot-copy-source-authority-to-target',lambda m:setvalue(m,'authorityAt',['z','s1'],'authority-a'),False)
    add('removing-edge-cannot-erase-source-record',lambda m:m['predicates']['EndpointPresent'].remove(['a','s1']),False)
    add('removing-edge-cannot-erase-target-record',lambda m:m['predicates']['EndpointPresent'].remove(['z','s1']),False)
    add('derived-label-must-be-generated-projection',lambda m:m['predicates'].update(GeneratedProjection=[]),False)
    add('derived-label-cannot-become-canonical-axis',lambda m:m['predicates'].update(CanonicalAxis=[['Label-a']]),False)
    def self_link(m):
        setvalue(m,'targetEndpoint',['r'],'a')
        for s in m['domains']['State']:setvalue(m,'targetAt',['r',s],'a')
    add('self-relation-is-not-unconditionally-forbidden',self_link)
    def equal_authority(m):
        for s in m['domains']['State']:setvalue(m,'authorityAt',['z',s],'authority-a')
    add('equal-authority-may-coexist-with-distinct-endpoints',equal_authority)
    add('no-derived-label-population-is-forced',lambda m:m['predicates'].update(DerivedLabel=[],GeneratedProjection=[]))
    def outside(m):m['predicates']['AllowedRelationStep']=[];m['predicates']['EndpointPresent'].remove(['z','s1'])
    add('unallowed-endpoint-erasure-is-not-certified-by-guarded-frame',outside)
    for n in b.ROLES:add('same-local-role-contrast-'+n,lambda m,n=n:m['predicates'].__setitem__(n,[['r']]),False)
    for n in b.OUTCOMES:add('independent-outcome-'+n,lambda m,n=n:m['predicates'].__setitem__(n,[['r']]))
    add('empty-Relation-extension-vacuous-T-not-I',lambda m:m['predicates'].update(IdentityRelation=[]),True,False)
    add('ill-sorted-endpoint-selector',lambda m:setvalue(m,'sourceEndpoint',['r'],'s0'),error='ill-sorted-function-result')
    add('nontotal-authority-state-selector',lambda m:m['functions']['authorityAt'].pop(),error='nontotal-function')
    add('wrong-evidence-binding-arity',lambda m:m['predicates'].update(HasEvidence=[['r']]),error='ill-sorted-model-tuple')
    add('duplicate-edge-tuple',lambda m:m['predicates']['IdentityRelation'].append(['r']),error='duplicate-predicate-tuple')
    add('ill-sorted-initial-state',lambda m:m['constants'].update(initialState='a'),error='ill-sorted-constant')
    return rows
def qualify(model,ids):
    return {bucket:{ids[n]:value for n,value in model[bucket].items()} for bucket in ['domains','constants','functions','predicates']}
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
    prior=json.loads((b.BASE/'definitions/cal.definition.identity-carrier/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-identity-relation-model-controls/v1-candidate','status':'PASS-for-exact-authored-identity-relation-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent authored finite models and nine targets outside T. Edge role/identity, endpoint equality, authority equality and contextual inference are separate; guarded endpoint preservation is not live compliance. No actual relation/admission, native enumeration, legacy metadata embedding, jointly aligned closure or whole Definition accepted.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
