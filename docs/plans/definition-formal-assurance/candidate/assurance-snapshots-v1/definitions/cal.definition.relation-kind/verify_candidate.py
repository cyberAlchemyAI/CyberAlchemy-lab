"""Independent Kind denotation: closed pairs, one question and associated rules."""
import itertools
import json
import build_candidate as b
import verifier as v

def load(name):return json.loads((b.UNIT/name).read_bytes())
def base_model():
    domains={'Contract':['k','j'],'Question':['membership','other-question'],'EndpointKind':['capability','product','work','project'],
             'QualifierRule':['product-rule','project-rule'],'QualifierValue':['product-role','project-role'],'VersionLabel':['v1','v2']}
    predicates={n:[] for n in b.SIGNATURE}
    for n in b.REQUIRED:predicates[n]=[['k']]
    predicates.update(DirectionalQuestion=[['membership']],ExactEndpointKind=[[x] for x in domains['EndpointKind']],Asks=[['k','membership']],
                      DeclaredPair=[['k','capability','product'],['k','work','project']],AllowedPair=[['k','capability','product'],['k','work','project']],
                      HasPairRule=[['k','capability','product','product-rule'],['k','work','project','project-rule']],
                      RuleAccepts=[['product-rule','product-role'],['project-rule','project-role']],
                      QualifierAllowed=[['k','capability','product','product-role'],['k','work','project','project-role']])
    functions={'versionLabel':[{'args':['k'],'value':'v1'},{'args':['j'],'value':'v2'}],
               'axisQuestion':[{'args':['k'],'value':'membership'},{'args':['j'],'value':'other-question'}],
               'pairRule':[{'args':[k,s,t],'value':'project-rule' if k=='k' and (s,t)==('work','project') else 'product-rule'}
                           for k,s,t in itertools.product(domains['Contract'],domains['EndpointKind'],domains['EndpointKind'])]}
    return {'domains':domains,'constants':{},'functions':functions,'predicates':predicates}
def successor(m):
    for n in b.REQUIRED:m['predicates'][n].append(['j'])
    m['functions']['axisQuestion'][1]['value']='membership';m['predicates']['Asks'].append(['j','membership'])
def controls():
    rows=[]
    def add(name,change,T=True,I=True,error=None):
        m=base_model();change(m);rows.append({'case_id':name,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
    add('one-directional-question-two-closed-pairs-no-authority',lambda m:None)
    for n in b.REQUIRED[1:]:add('missing-'+n,lambda m,n=n:m['predicates'].__setitem__(n,[]),False,False)
    add('missing-directional-question-status',lambda m:m['predicates'].update(DirectionalQuestion=[]),False,False)
    add('missing-declared-question',lambda m:m['predicates'].update(Asks=[]),False,False)
    add('second-question-on-one-kind-violates-uniqueness',lambda m:m['predicates']['Asks'].append(['k','other-question']),False)
    add('successor-kind-version-may-retain-question',successor)
    def distinct(m):
        for n in b.REQUIRED:m['predicates'][n].append(['j'])
        m['predicates']['DirectionalQuestion'].append(['other-question']);m['predicates']['Asks'].append(['j','other-question'])
    add('different-kind-questions-also-permitted',distinct)
    add('undeclared-cartesian-cross-pair-is-not-allowed',lambda m:m['predicates']['AllowedPair'].append(['k','capability','project']),False)
    add('declared-pair-cannot-silently-disappear-from-allowed',lambda m:m['predicates']['AllowedPair'].pop(),False)
    add('exact-endpoint-status-required-on-declaration',lambda m:m['predicates'].update(ExactEndpointKind=[['product'],['work'],['project']]),False)
    add('declared-reverse-is-not-forward-order',lambda m:m['predicates'].update(AllowedPair=[['k','product','capability'],['k','work','project']]),False)
    add('missing-pair-specific-rule',lambda m:m['predicates']['HasPairRule'].pop(),False)
    add('rule-for-undeclared-pair',lambda m:m['predicates']['HasPairRule'].append(['k','capability','project','product-rule']),False)
    add('different-rule-not-selected-for-this-pair',lambda m:m['predicates']['HasPairRule'].append(['k','capability','product','project-rule']),False)
    add('qualifier-accepted-by-other-pair-rule-is-not-accepted-here',lambda m:m['predicates']['QualifierAllowed'].append(['k','capability','product','project-role']),False)
    add('qualifier-does-not-license-undeclared-pair',lambda m:m['predicates']['QualifierAllowed'].append(['k','capability','project','product-role']),False)
    add('no-accepted-qualifier-population-is-forced',lambda m:m['predicates'].update(QualifierAllowed=[]))
    def shared(m):
        for row in m['functions']['pairRule']:row['value']='product-rule'
        m['predicates']['HasPairRule']=[['k','capability','product','product-rule'],['k','work','project','product-rule']]
        m['predicates']['QualifierAllowed']=[['k','capability','product','product-role'],['k','work','project','product-role']]
    add('pair-specific-associations-may-share-one-rule',shared)
    def empty_pairs(m):
        for n in ['DeclaredPair','AllowedPair','HasPairRule','QualifierAllowed']:m['predicates'][n]=[]
    add('empty-finite-pair-set-not-rejected-without-owner-population-policy',empty_pairs)
    for n in b.ROLES:add('same-role-contrast-'+n,lambda m,n=n:m['predicates'].__setitem__(n,[['k']]),False)
    for n in b.OUTCOMES:add('independent-outcome-may-coexist-'+n,lambda m,n=n:m['predicates'].__setitem__(n,[['k']]))
    add('empty-Kind-extension-vacuous-T-not-required-I',lambda m:m['predicates'].update(RelationKind=[]),True,False)
    add('ill-sorted-axis-question-function-result',lambda m:m['functions']['axisQuestion'][0].update(value='v1'),error='ill-sorted-function-result')
    add('nontotal-pair-rule-table',lambda m:m['functions']['pairRule'].pop(),error='nontotal-function')
    add('wrong-ordered-pair-arity',lambda m:m['predicates'].update(DeclaredPair=[['k','capability']]),error='ill-sorted-model-tuple')
    add('duplicate-kind-tuple',lambda m:m['predicates']['RelationKind'].append(['k']),error='duplicate-predicate-tuple')
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
        if q.get('model_case')=='successor-same-question':successor(model)
        elif q.get('model_case')=='no-accepted-qualifiers':model['predicates']['QualifierAllowed']=[]
        model=qualify(model,ids);e=v.Denotation(typed['declarations'],model)
        target=v.renamed(q['target'],ids);witness=v.renamed(q['witness_condition'],ids)
        b.ir.check_composed_formula(composed,target);b.ir.check_composed_formula(composed,witness)
        if q['selected_in_T'] is not False or evaluate(model)[:2]!=(True,True) or e.truth(target) is not False or e.truth(witness) is not True:raise ValueError('Target assumed or no valid countermodel: '+q['query_id'])
        queries.append({'query_id':q['query_id'],'target_false':True,'witness_condition_true':True,'model':model,'model_sha256':b.ir.digest(model),'mechanized_proof':False})
    prior=json.loads((b.BASE/'definitions/cal.definition.typed-relation/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-relation-kind-model-controls/v1-candidate','status':'PASS-for-exact-authored-closed-relation-kind-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent authored finite models and nine targets outside T. Closed-finite declaration statuses do not prove unbounded finiteness; no question orthogonality, actual admission, native enumeration, semantic closure or whole Definition accepted.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
