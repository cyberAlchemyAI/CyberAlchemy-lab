"""Independent finite Responsibility modal-description models; no actual duty/fulfillment/authority proof."""
import itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def base_model():
 domains={'Entity':['q1','q2','q3','p1','t1','role1','o1','o2','action1'],'State':['before','after'],'Token':['empty','scope','other-scope','identity','other-identity']};functions={}
 for n,(args,_) in b.FUNCTIONS.items():functions[n]=[{'args':list(xs),'value':('other-scope' if xs[0]=='q3' else 'scope') if n=='scopeToken' else ('identity' if xs[0] in ['q1','q2'] else 'other-identity')} for xs in itertools.product(*[domains[s] for s in args])]
 p={n:[] for n in b.SIGNATURE}
 for n in ['Responsibility','Obligation','OwnerQualified']:p[n]=[[x] for x in ['q1','q2','q3']]
 p.update(DeclaredOutcome=[['o1'],['o2']],Person=[['p1']],Team=[['t1']],Role=[['role1']],Action=[['action1']],HasDeclaredOutcome=[['q1','o1'],['q1','o2'],['q2','o1'],['q3','o1']],AccountableBy=[['q1','p1'],['q1','t1']],ActiveAt=[['q1','before']],NeedsPerform=[['q1','o1'],['q2','o1']],NeedsMaintain=[['q1','o1'],['q2','o1'],['q3','o1']],NeedsAnswerFor=[['q1','o1']],NeedsRoute=[['q1','o1'],['q1','o2'],['q3','o1']])
 return {'domains':domains,'constants':{'EMPTY':'empty'},'functions':functions,'predicates':p}
def setvalue(m,n,args,value):next(x for x in m['functions'][n] if x['args']==args)['value']=value
def controls():
 rows=[]
 def add(id,change,T=True,I=True,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('unfulfilled-obligations-many-modes-outcomes-and-accountable-actors',lambda m:None)
 add('Role-Responsibility-overlap-not-globally-excluded-by-partial-target',lambda m:m['predicates']['Role'].append(['q1']))
 add('Person-Team-overlap-not-globally-excluded',lambda m:m['predicates']['Team'].append(['p1']))
 for n in b.OUTCOMES:add('independent-world-fact-'+n,lambda m,n=n:m['predicates'].__setitem__(n,[['q1']]))
 add('independent-exact-grant-can-coexist',lambda m:m['predicates'].update(GrantAt=[['q1','action1','before']]))
 add('independent-accountable-actor-authorization-can-coexist',lambda m:m['predicates'].update(AuthorizedAt=[['p1','action1','before']]))
 for n in ['ActualPerformed','ActualMaintained','ActualAnsweredFor','ActualRouted']:add('some-independent-'+n+'-can-coexist',lambda m,n=n:m['predicates'].__setitem__(n,[['q1','o1']]))
 for n in ['Obligation','OwnerQualified']:add('missing-'+n+'-marker',lambda m,n=n:m['predicates'].__setitem__(n,[]),False,True)
 add('missing-DeclaredOutcome-type',lambda m:m['predicates'].update(DeclaredOutcome=[]),False,True)
 add('missing-declared-outcome-links',lambda m:m['predicates'].update(HasDeclaredOutcome=[]),False,False)
 add('undeclared-mode-target',lambda m:m['predicates']['NeedsPerform'].append(['q1','action1']),False,True)
 add('empty-scope-invalid-and-breaks-selected-shared-scope-I',lambda m:setvalue(m,'scopeToken',['q1'],'empty'),False,False)
 for n in b.MODES:add('missing-'+n+'-still-valid-other-mode-but-rich-I-fails',lambda m,n=n:m['predicates'].__setitem__(n,[]),True,False)
 def no_modes(m):
  for n in b.MODES:m['predicates'][n]=[]
 add('no-obligation-mode-invalid',no_modes,False,False)
 add('no-Responsibility-vacuous-T-fails-rich-I',lambda m:m['predicates'].update(Responsibility=[]),True,False)
 add('no-accountability-valid-T-fails-rich-I',lambda m:m['predicates'].update(AccountableBy=[]),True,False)
 add('all-Responsibility-fulfilled-valid-T-fails-unfulfilled-rich-I',lambda m:m['predicates'].update(Fulfilled=[['q1'],['q2'],['q3']]),True,False)
 add('all-outcomes-achieved-valid-T-fails-unachieved-rich-I',lambda m:m['predicates'].update(OutcomeAchieved=[['o1'],['o2']]),True,False)
 add('no-active-label-required-by-target-or-rich-I',lambda m:m['predicates'].update(ActiveAt=[]))
 add('nontotal-scope-function',lambda m:m['functions']['scopeToken'].pop(),error='nontotal-function')
 add('ill-sorted-scope-result',lambda m:setvalue(m,'scopeToken',['q1'],'p1'),error='ill-sorted-function-result')
 add('ill-sorted-empty-sentinel',lambda m:m['constants'].update(EMPTY='absent'),error='ill-sorted-constant')
 add('wrong-mode-arity',lambda m:m['predicates'].update(NeedsPerform=[['q1']]),error='ill-sorted-model-tuple')
 add('duplicate-declared-outcome-tuple',lambda m:m['predicates']['HasDeclaredOutcome'].append(['q1','o1']),error='duplicate-predicate-tuple')
 add('empty-Entity-domain',lambda m:m['domains'].update(Entity=[]),error='empty-or-malformed-domain')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.role-assignment/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-Responsibility-model-controls/v1-candidate','status':'PASS-for-exact-authored-Responsibility-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent supplied Responsibility obligation/modal-description models and sixteen targets outside T. No actual owner/outcome/duty/scope/accountability/completion/entity/history denotation, inherited Authority adoption, deontic/temporal/operational or source-fidelity proof.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
