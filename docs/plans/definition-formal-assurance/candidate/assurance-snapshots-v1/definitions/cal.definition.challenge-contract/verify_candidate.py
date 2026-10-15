"""Independent supplied Challenge Contract specification and filing/effect models."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def base_model():
 domains={'Entity':['c1','c2','r1','r2','q1','f1','t1','t2','d1'],'Token':['empty','spec','scope','label'],'State':['before','after']};functions={}
 for n in b.FUNCTIONS:
  value='scope' if n=='scopeValue' else 'label' if n=='labelValue' else 'spec';functions[n]=[{'args':[e],'value':value} for e in domains['Entity']]
 p={n:[] for n in b.SIGNATURE};p.update(ChallengeContract=[['c1'],['c2']],ClosedMechanism=[['c1'],['c2']],VersionedMechanism=[['c1'],['c2']],PolicyBound=[['c1'],['c2']],GovernedIdentityOrRecord=[['c1'],['c2'],['q1']],BoundedScope=[['c1'],['c2'],['q1']],RouteStringAlone=[['r2']],RawDeclaredComplete=[['c1'],['r1']],FiledUnder=[['f1','c1','t1']],ActualSuspended=[['t2','after']],ActualReversed=[['t2','after']],IndependentOwnerDecisionEffect=[['d1','t2','after']],ResidueRetained=[['c1','after']],InScope=[['c1','scope'],['c2','scope']])
 for n in b.FIELDS:
  if n!='Policy':p['Defines'+n]=[['c1'],['c2']]
 return {'domains':domains,'constants':{'EMPTY':'empty'},'functions':functions,'predicates':p}
def setvalue(m,n,e,value):next(x for x in m['functions'][n] if x['args']==[e])['value']=value
def controls():
 rows=[]
 def add(id,change,T=True,I=None,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('closed-qualified-contract-filing-no-automatic-subject-effect',lambda m:None,I=True)
 for n in b.OUTCOMES+['AuthenticatedMechanism','Policy','ChallengeEvent']:add('independently-supplied-marker-'+n,lambda m,n=n:m['predicates'][n].append(['c1']),I=True)
 for n in ['ClosedMechanism','VersionedMechanism','PolicyBound']+['Defines'+n for n in b.FIELDS if n!='Policy']:add('Contract-missing-qualified-'+n,lambda m,n=n:m['predicates'][n].remove(['c1']),T=False)
 for n in b.FIELDS+['Version']:add('Contract-empty-selected-value-'+n,lambda m,n=n:setvalue(m,n.lower()+'Value','c1','empty'),T=False)
 for n in ['GovernedIdentityOrRecord','BoundedScope']:add('Contract-missing-formal-necessity-'+n,lambda m,n=n:m['predicates'][n].remove(['c1']),T=False)
 add('qualified-specification-without-Contract-reverse-iff-required',lambda m:m['predicates']['ChallengeContract'].remove(['c1']),T=False)
 add('route-alone-cannot-be-Contract',lambda m:m['predicates']['ChallengeContract'].append(['r2']),T=False)
 add('raw-completeness-cannot-force-Contract',lambda m:m['predicates']['ChallengeContract'].append(['r1']),T=False)
 def qualified(m):
  for n in ['ChallengeContract','ClosedMechanism','VersionedMechanism','PolicyBound','GovernedIdentityOrRecord','BoundedScope']+['Defines'+n for n in b.FIELDS if n!='Policy']:m['predicates'][n].append(['r1'])
 add('separate-qualified-specification-changes-classification-not-raw-fields-alone',qualified,I=False)
 add('formal-necessary-predicates-without-genus-remain-noncontract',lambda m:None,I=True)
 add('no-filed-event-alternative-partial-T-model-not-rich-I',lambda m:m['predicates'].update(FiledUnder=[]),I=False)
 def separately_effected(m):m['predicates']['ActualSuspended'].append(['t1','after']);m['predicates']['ActualReversed'].append(['t1','after']);m['predicates']['IndependentOwnerDecisionEffect'].append(['d1','t1','after'])
 add('separate-owner-decision-can-suspend-and-reverse-filed-subject',separately_effected,I=False)
 add('unresolved-residue-without-resolution',lambda m:m['predicates']['ResidueRetained'].append(['c2','before']),I=True)
 add('separate-resolution-can-coexist-with-contract',lambda m:m['predicates']['ResolutionReached'].append(['c2','after']),I=True)
 add('empty-Token-scope-value-not-connected-to-opaque-BoundedScope-predicate',lambda m:setvalue(m,'scopeValue','c1','empty'),I=False)
 add('field-values-can-alias-version-scope-label-without-accepted-denotation',lambda m:[setvalue(m,n,'c1','spec') or setvalue(m,n,'c2','spec') for n in b.FUNCTIONS],I=True)
 add('not-all-subjects-or-challengers-eligible',lambda m:m['predicates']['SubjectEligible'].append(['c1','t1']),I=True)
 add('independently-supplied-Policy-relation-no-owner-authentication',lambda m:m['predicates']['GovernedByPolicy'].append(['c1','q1']),I=True)
 add('nontotal-version-function',lambda m:m['functions']['versionValue'].pop(),error='nontotal-function')
 add('ill-sorted-field-function-result',lambda m:setvalue(m,'policyValue','c1','c1'),error='ill-sorted-function-result')
 add('ill-sorted-empty-constant',lambda m:m['constants'].update(EMPTY='absent'),error='ill-sorted-constant')
 add('wrong-filing-arity',lambda m:m['predicates'].update(FiledUnder=[['f1','c1']]),error='ill-sorted-model-tuple')
 add('duplicate-route-tuple',lambda m:m['predicates']['RouteStringAlone'].append(['r2']),error='duplicate-predicate-tuple')
 add('empty-Token-carrier',lambda m:m['domains'].update(Token=[]),error='empty-or-malformed-domain')
 add('duplicate-function-tuple',lambda m:m['functions']['policyValue'].append(copy.deepcopy(m['functions']['policyValue'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.authority-surface/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-ChallengeContract-model-controls/v1-candidate','status':'PASS-for-exact-authored-ChallengeContract-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent supplied closed versioned Policy-bound specification, route exclusion and filing/effect models. Exact field/version/Policy/owner/eligibility/timing/resolution/residue denotation, automatic-effect causal prevention and universal enforcement remain unresolved.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
