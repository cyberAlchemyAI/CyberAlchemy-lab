"""Independent Boundary explicit-binding and scoped decision iff models; authenticated/time semantics separate."""
import itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def base_model():
 domains={'Entity':['b1','b2','b3','p1','p2','r1','r2','d1','d2','d3','x1','x2','e1','e2'],'State':['before','after'],'Token':['empty','scope-one','scope-two','challenge']};functions={}
 for n,(args,_) in b.FUNCTIONS.items():
  rows=[]
  for e in domains['Entity']:
   if n=='ownerRole':value='r2' if e=='b2' else 'r1'
   elif n=='boundPrincipal':value='p1'
   elif n=='decisionTarget':value='x2' if e=='d2' else 'x1'
   elif n=='decisionEffect':value='e2' if e in ['d2','d3'] else 'e1'
   elif n=='scopeValue':value='scope-two' if e=='b2' else 'scope-one'
   else:value='challenge'
   rows.append({'args':[e],'value':value})
  functions[n]=rows
 p={n:[] for n in b.SIGNATURE};p.update(AuthorityBoundary=[['b1'],['b2'],['b3']],Role=[['r1'],['r2']],Principal=[['p1'],['p2']],GovernanceDecision=[['d1'],['d2'],['d3']],GovernedTarget=[['x1'],['x2']],EffectKind=[['e1'],['e2']],ExplicitBoundary=[['b1'],['b2'],['b3']],OwnerScopedLimit=[['b1'],['b2'],['b3']],HoldsRole=[['p1','r1'],['p1','r2'],['p2','r1']],ScopeContains=[['b1','x1'],['b2','x2']],AllowedEffect=[['b1','e1'],['b1','e2'],['b2','e2']],ExcludedEffect=[['b1','e2']],MayDecide=[['p1','d1','b1'],['p2','d1','b1'],['p1','d2','b2']],RevokedBoundary=[['b1','after']],EffectiveAt=[['b2','before']],SelectedCheckpoint=[['b3']])
 for n in b.FIELDS:p['Explicit'+n]=[['b1'],['b2'],['b3']]
 return {'domains':domains,'constants':{'EMPTY':'empty'},'functions':functions,'predicates':p}
def setvalue(m,n,args,value):next(x for x in m['functions'][n] if x['args']==args)['value']=value
def recompute(m):
 p=m['predicates'];value=lambda n,e:next(x['value'] for x in m['functions'][n] if x['args']==[e]);p['MayDecide']=[[a[0],d[0],z[0]] for a in p['Principal'] for d in p['GovernanceDecision'] for z in p['AuthorityBoundary'] if [a[0],value('ownerRole',z[0])] in p['HoldsRole'] and [z[0],value('decisionTarget',d[0])] in p['ScopeContains'] and [z[0],value('decisionEffect',d[0])] in p['AllowedEffect'] and [z[0],value('decisionEffect',d[0])] not in p['ExcludedEffect']]
def controls():
 rows=[]
 def add(id,change,T=True,I=True,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('explicit-Boundary-scoped-iff-not-actual-authenticated-effective-permission',lambda m:None)
 for n in b.OUTCOMES:add('independent-world-fact-'+n,lambda m,n=n:m['predicates'][n].append(['b1']))
 add('independent-authenticated-Boundary-marker-permitted',lambda m:m['predicates']['AuthenticatedBoundary'].append(['b1']))
 add('independent-actual-authorization-permitted',lambda m:m['predicates']['ActualAuthorizedDecision'].append(['p1','d1','b1']))
 add('independent-actual-execution-permitted',lambda m:m['predicates']['ActualExecutedDecision'].append(['p1','d1','b1','after']))
 for n in b.FIELDS:add('Boundary-missing-explicit-'+n,lambda m,n=n:m['predicates']['Explicit'+n].remove(['b1']),False,True)
 for n in ['ExplicitBoundary','OwnerScopedLimit']:add('Boundary-missing-'+n,lambda m,n=n:m['predicates'][n].remove(['b1']),False,True)
 add('owner-function-result-not-Role',lambda m:m['predicates']['Role'].remove(['r1']),False,True)
 add('binding-function-result-not-Principal',lambda m:m['predicates']['Principal'].remove(['p1']),False,True)
 add('empty-scope-value',lambda m:setvalue(m,'scopeValue',['b1'],'empty'),False,False)
 add('empty-challenge-value',lambda m:setvalue(m,'challengeValue',['b1'],'empty'),False,True)
 add('MayDecide-without-role-holding',lambda m:m['predicates']['HoldsRole'].remove(['p1','r1']),False,False)
 add('MayDecide-without-target-membership',lambda m:m['predicates']['ScopeContains'].remove(['b1','x1']),False,True)
 add('MayDecide-without-allowed-effect',lambda m:m['predicates']['AllowedEffect'].remove(['b1','e1']),False,True)
 add('MayDecide-with-excluded-effect',lambda m:m['predicates']['ExcludedEffect'].append(['b1','e1']),False,True)
 add('eligible-but-MAY-not-DECIDE-reverse-iff-required',lambda m:m['predicates']['MayDecide'].remove(['p1','d1','b1']),False,True)
 add('excluded-over-allowed-precedence',lambda m:m['predicates']['MayDecide'].append(['p1','d3','b1']),False,True)
 add('wrong-owner-role-second-boundary',lambda m:m['predicates']['MayDecide'].append(['p2','d2','b2']),False,True)
 add('wrong-target-scope-second-boundary',lambda m:m['predicates']['MayDecide'].append(['p1','d1','b2']),False,True)
 add('MayDecide-subject-not-Principal',lambda m:m['predicates']['MayDecide'].append(['b1','d1','b1']),False,True)
 add('MayDecide-object-not-GovernanceDecision',lambda m:m['predicates']['MayDecide'].append(['p1','x1','b1']),False,True)
 add('MayDecide-context-not-Boundary',lambda m:m['predicates']['MayDecide'].append(['p1','d1','x1']),False,True)
 def allowed_without_required(m):m['predicates']['AllowedEffect'].append(['b3','e1']);m['predicates']['ScopeContains'].append(['b3','x1']);recompute(m)
 add('empty-allowed-Boundary-can-gain-selected-set-rich-empty-witness-fails',allowed_without_required,True,False)
 def no_second_actor(m):m['predicates']['HoldsRole'].remove(['p2','r1']);recompute(m)
 add('all-eligible-actors-can-match-binding-rich-different-actor-witness-fails',no_second_actor,True,False)
 add('no-revocation-marker-still-source-T',lambda m:m['predicates'].update(RevokedBoundary=[]),True,False)
 def no_boundary(m):m['predicates'].update(AuthorityBoundary=[],MayDecide=[])
 add('no-Boundary-vacuous-T-fails-rich-I',no_boundary,True,False)
 add('nontotal-owner-function',lambda m:m['functions']['ownerRole'].pop(),error='nontotal-function')
 add('ill-sorted-owner-result',lambda m:setvalue(m,'ownerRole',['b1'],'scope-one'),error='ill-sorted-function-result')
 add('ill-sorted-empty-sentinel',lambda m:m['constants'].update(EMPTY='absent'),error='ill-sorted-constant')
 add('wrong-MayDecide-arity',lambda m:m['predicates'].update(MayDecide=[['p1','d1']]),error='ill-sorted-model-tuple')
 add('duplicate-role-holding',lambda m:m['predicates']['HoldsRole'].append(['p1','r1']),error='duplicate-predicate-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.authority-claim/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-AuthorityBoundary-model-controls/v1-candidate','status':'PASS-for-exact-authored-AuthorityBoundary-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent supplied Boundary explicit binding/scoped two-direction MayDecide iff models and seventeen outside-T targets. Actor equality to bound principal, current effectivity/revocation, actual owner/role/scope/effect authentication, exact tuple, workflow noninterference and universal operational proof remain separate pending semantics.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
