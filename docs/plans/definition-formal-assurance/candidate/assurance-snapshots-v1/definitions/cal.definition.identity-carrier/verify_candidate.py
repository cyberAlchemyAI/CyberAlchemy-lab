"""Independent finite carrier/subject/typed-reference/context-frame denotation."""
import itertools
import json
import build_candidate as b
import verifier as v

def load(name):return json.loads((b.UNIT/name).read_bytes())
def base_model():
    domains={sort:[sort+'-a',sort+'-b'] for sort in b.SORTS}
    domains.update(Carrier=['k','j'],Identity=['carrier-k','carrier-j','subject-a','subject-b'],State=['s0','s1'],Link=['l','m'],AuthorityState=['auth0','auth1'],LocationPath=['shared-dir','new-dir'])
    functions={}
    for n,(args,sort) in b.FUNCTIONS.items():functions[n]=[{'args':list(xs),'value':domains[sort][0]} for xs in itertools.product(*[domains[x] for x in args])]
    def setfn(n,values):
        for row in functions[n]:row['value']=values[tuple(row['args'])]
    setfn('carrierIdentity',{('k',):'carrier-k',('j',):'carrier-j'})
    setfn('primarySubject',{('k',):'subject-a',('j',):'subject-b'})
    setfn('subjectAt',{(k,s):'subject-a' if k=='k' else 'subject-b' for k,s in itertools.product(domains['Carrier'],domains['State'])})
    for n in ['linkSource','linkSourceAt']:
        for row in functions[n]:row['value']='subject-a'
    for n in ['linkTarget','linkTargetAt']:
        for row in functions[n]:row['value']='subject-b'
    predicates={n:[] for n in b.SIGNATURE}
    for n in b.REQUIRED:predicates[n]=[['k']]
    predicates.update(ResolvableDefinition=[['DefinitionRef-a']],IndependentIdentity=[['subject-a'],['subject-b']],TypedLink=[['l']],HasProvenance=[['k','ProvenanceRef-a']],Carries=[['k','subject-a']],Related=[['subject-a','subject-b']],Connects=[['l','subject-a','subject-b']],CanonicalPresent=[['k','s0'],['k','s1']],ContextOnlyChange=[['k','s0','s1']],AllowedContextStep=[['s0','s1']],ViewRemovalStep=[['k','s0','s1']],AllowedRelationStep=[['l','s0','s1']])
    return {'domains':domains,'constants':{'initialState':'s0'},'functions':functions,'predicates':predicates}
def setvalue(m,function,args,value):
    next(x for x in m['functions'][function] if x['args']==args)['value']=value
def second_carrier(m,same=False):
    for n in b.REQUIRED:m['predicates'][n].append(['j'])
    subject='subject-a' if same else 'subject-b';setvalue(m,'primarySubject',['j'],subject)
    for s in m['domains']['State']:setvalue(m,'subjectAt',['j',s],subject)
    m['predicates']['Carries'].append(['j',subject]);m['predicates']['HasProvenance'].append(['j','ProvenanceRef-a']);m['predicates']['CanonicalPresent'] += [['j','s0'],['j','s1']]
def controls():
    rows=[]
    def add(name,change,T=True,I=True,error=None):
        m=base_model();change(m);rows.append({'case_id':name,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
    add('one-primary-related-independent-target-and-preserved-context',lambda m:None)
    for n in b.REQUIRED[1:]:add('missing-'+n,lambda m,n=n:m['predicates'].__setitem__(n,[]),False,False)
    add('missing-resolvable-subject-kind',lambda m:m['predicates'].update(ResolvableDefinition=[]),False,False)
    add('missing-primary-independent-identity',lambda m:m['predicates'].update(IndependentIdentity=[['subject-b']]),False,False)
    add('missing-provenance-binding',lambda m:m['predicates'].update(HasProvenance=[]),False,False)
    add('missing-primary-carries-relation',lambda m:m['predicates'].update(Carries=[]),False,False)
    add('two-primary-subjects-on-one-carrier-fail',lambda m:m['predicates']['Carries'].append(['k','subject-b']),False)
    add('missing-initial-canonical-record',lambda m:m['predicates'].update(CanonicalPresent=[['k','s1']]),False,False)
    add('initial-state-subject-must-match-primary',lambda m:setvalue(m,'subjectAt',['k','s0'],'subject-b'),False)
    add('related-target-needs-independent-identity',lambda m:m['predicates'].update(IndependentIdentity=[['subject-a']]),False)
    add('related-target-needs-typed-link',lambda m:m['predicates'].update(TypedLink=[]),False)
    add('related-target-needs-selected-typed-endpoints',lambda m:m['predicates'].update(Connects=[]),False)
    add('typed-link-cannot-gain-different-endpoints',lambda m:m['predicates']['Connects'].append(['l','subject-a','subject-a']),False)
    add('initial-link-source-must-match-selector',lambda m:setvalue(m,'linkSourceAt',['l','s0'],'subject-b'),False)
    add('context-change-cannot-replace-subject',lambda m:setvalue(m,'subjectAt',['k','s1'],'subject-b'),False)
    add('context-change-cannot-transfer-primary-authority',lambda m:setvalue(m,'authorityAt',['subject-a','s1'],'auth1'),False)
    add('view-removal-cannot-erase-canonical-record',lambda m:m['predicates'].update(CanonicalPresent=[['k','s0']]),False)
    add('relation-change-cannot-merge-source-endpoint',lambda m:setvalue(m,'linkSourceAt',['l','s1'],'subject-b'),False)
    add('relation-change-cannot-replace-target-endpoint',lambda m:setvalue(m,'linkTargetAt',['l','s1'],'subject-a'),False)
    add('relation-change-cannot-transfer-target-authority',lambda m:setvalue(m,'authorityAt',['subject-b','s1'],'auth1'),False)
    add('two-different-subjects-may-share-owner-and-path',second_carrier)
    add('two-carriers-may-carry-one-subject-without-injectivity-policy',lambda m:second_carrier(m,True))
    add('carrier-id-and-subject-id-inequality-is-not-assumed',lambda m:setvalue(m,'carrierIdentity',['k'],'subject-a'))
    def self_link(m):
        m['predicates'].update(Related=[['subject-a','subject-a']],Connects=[['l','subject-a','subject-a']])
        setvalue(m,'linkTarget',['l'],'subject-a')
        for s in m['domains']['State']:setvalue(m,'linkTargetAt',['l',s],'subject-a')
    add('self-relation-permitted-by-selected-identity-slice',self_link)
    def extra_link(m):m['predicates']['TypedLink'].append(['m']);m['predicates']['Connects'].append(['m','subject-a','subject-b'])
    add('distinct-link-ids-may-connect-same-endpoints',extra_link)
    def no_related(m):
        for n in ['Related','TypedLink','Connects','AllowedRelationStep']:m['predicates'][n]=[]
    add('no-related-or-link-population-is-forced',no_related)
    def unallowed(m):m['predicates']['AllowedContextStep']=[];setvalue(m,'subjectAt',['k','s1'],'subject-b')
    add('unallowed-transition-not-certified-by-guarded-constraints',unallowed)
    for n in b.ROLES:add('same-local-role-contrast-'+n,lambda m,n=n:m['predicates'].__setitem__(n,[['k']]),False)
    for n in b.OUTCOMES:add('independent-outcome-'+n,lambda m,n=n:m['predicates'].__setitem__(n,[['k']]))
    add('empty-Carrier-extension-vacuous-T-not-I',lambda m:m['predicates'].update(IdentityCarrier=[]),True,False)
    add('ill-sorted-subject-selector',lambda m:setvalue(m,'primarySubject',['k'],'s0'),error='ill-sorted-function-result')
    add('nontotal-state-selector',lambda m:m['functions']['subjectAt'].pop(),error='nontotal-function')
    add('wrong-typed-link-arity',lambda m:m['predicates'].update(Connects=[['l','subject-a']]),error='ill-sorted-model-tuple')
    add('duplicate-carrier-tuple',lambda m:m['predicates']['IdentityCarrier'].append(['k']),error='duplicate-predicate-tuple')
    add('ill-sorted-initial-state-constant',lambda m:m['constants'].update(initialState='subject-a'),error='ill-sorted-constant')
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
        case=q.get('model_case')
        if case=='two-different-subjects':second_carrier(model)
        elif case=='two-carriers-one-subject':second_carrier(model,True)
        model=qualify(model,ids);e=v.Denotation(typed['declarations'],model)
        target=v.renamed(q['target'],ids);witness=v.renamed(q['witness_condition'],ids)
        b.ir.check_composed_formula(composed,target);b.ir.check_composed_formula(composed,witness)
        if q['selected_in_T'] is not False or evaluate(model)[:2]!=(True,True) or e.truth(target) is not False or e.truth(witness) is not True:raise ValueError('Target assumed or no valid countermodel: '+q['query_id'])
        queries.append({'query_id':q['query_id'],'target_false':True,'witness_condition_true':True,'model':model,'model_sha256':b.ir.digest(model),'mechanized_proof':False})
    prior=json.loads((b.BASE/'definitions/cal.definition.artifact-type/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-identity-carrier-model-controls/v1-candidate','status':'PASS-for-exact-authored-identity-carrier-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent authored finite models and nine targets outside T. Unique primary identity does not imply inverse injectivity or endpoint inequality; guarded preservation is not live compliance. No actual subject creation, relation/admission, native enumeration, source-carrier embedding, jointly aligned closure or whole Definition accepted.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
