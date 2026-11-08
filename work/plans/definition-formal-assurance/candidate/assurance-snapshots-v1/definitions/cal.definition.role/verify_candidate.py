"""Independent supplied Role models; expected relationships and holders remain separate."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def base_model():
 domains={'Entity':['r1','r2','r3','p1','p2','t1','m1','a1','a2','a3','d1','k1','action1'],'State':['before','after'],'Token':['empty','scope','other-scope','expectations','eligibility','identity-shared','identity-r2','default']}
 functions={}
 for n,(args,_) in b.FUNCTIONS.items():
  rows=[]
  for xs in itertools.product(*[domains[sort] for sort in args]):
   entity=xs[0];value={'scopeToken':'other-scope' if entity=='r2' else 'scope','expectationToken':'expectations','eligibilityToken':'eligibility','roleIdentity':'identity-shared' if entity in ['r1','r3'] else 'identity-r2' if entity=='r2' else 'default','recordedIdentity':'identity-shared' if entity in ['r1','r3'] else 'identity-r2' if entity=='r2' else 'default'}[n]
   rows.append({'args':list(xs),'value':value})
  functions[n]=rows
 predicates={n:[] for n in b.SIGNATURE}
 for n in ['Role','ReusablePosition','HasExpectationDescription','HasEligibilityDescription']:predicates[n]=[[r] for r in ['r1','r2','r3']]
 predicates.update(Person=[['p1'],['p2']],Team=[['t1']],TeamMembership=[['m1']],RoleAssignment=[['a1'],['a2'],['a3']],ResponsibilityDescription=[['d1']],AuthorityRelationSpecification=[['k1']],ResponsibilityRecord=[['d1']],Action=[['action1']],DescribesExpectedResponsibility=[['r1','d1'],['r2','d1'],['r3','d1']],EligibleAuthorityRelationship=[['r1','k1'],['r2','k1'],['r3','k1']],HasRole=[['p1','r1','before'],['p2','r1','after'],['t1','r1','after']],AssignedAt=[['a1','p1','r1','before'],['a2','p2','r1','after'],['a3','t1','r1','after']])
 return {'domains':domains,'constants':{'EMPTY':'empty'},'functions':functions,'predicates':predicates}
def setvalue(m,n,args,value):next(x for x in m['functions'][n] if x['args']==args)['value']=value
def controls():
 rows=[]
 def add(id,change,T=True,I=True,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('reusable-position-unassigned-Role-and-distinct-Person-Team-holders',lambda m:None)
 add('distinct-Role-Entities-share-description-scope-and-identity-token',lambda m:None)
 add('Role-Person-overlap-not-globally-forbidden-by-target-projection',lambda m:m['predicates']['Person'].append(['r1']))
 for n in b.OUTCOMES:add('independently-supported-world-fact-'+n,lambda m,n=n:m['predicates'].__setitem__(n,[['r1']]))
 add('independent-exact-Role-action-grant-permitted',lambda m:m['predicates'].update(ActualGrant=[['r1','action1','before']]))
 add('independent-holder-action-authorization-permitted',lambda m:m['predicates'].update(AuthorizedFor=[['p1','action1','before']]))
 add('independent-actual-responsibility-ownership-permitted',lambda m:m['predicates'].update(ResponsibilityOwnedBy=[['p1','d1','before']]))
 add('no-membership-population-required-by-Role-target',lambda m:m['predicates'].update(TeamMembership=[]))
 add('Assignment-markers-absent-not-complete-assignment-theory',lambda m:m['predicates'].update(RoleAssignment=[]))
 add('no-Action-population-required-by-Role-target-or-rich-I',lambda m:m['predicates'].update(Action=[]))
 add('one-assignment-token-can-bind-extra-Person-without-importing-singularity',lambda m:m['predicates']['AssignedAt'].append(['a1','p2','r1','before']))
 for n in ['ReusablePosition','HasExpectationDescription','HasEligibilityDescription']:add('missing-'+n+'-marker',lambda m,n=n:m['predicates'].__setitem__(n,[]),False,True)
 add('empty-scope-sentinel-invalid',lambda m:setvalue(m,'scopeToken',['r1'],'empty'),False,False)
 add('expectation-target-needs-description-type',lambda m:m['predicates'].update(ResponsibilityDescription=[]),False,True)
 add('eligibility-target-needs-specification-type',lambda m:m['predicates'].update(AuthorityRelationSpecification=[]),False,True)
 add('descriptive-markers-without-links-primary-valid-rich-I-fails',lambda m:m['predicates'].update(DescribesExpectedResponsibility=[],EligibleAuthorityRelationship=[]),True,False)
 add('no-holder-projection-primary-valid-rich-I-fails',lambda m:m['predicates'].update(HasRole=[]),True,False)
 add('no-Person-marker-primary-valid-rich-I-fails',lambda m:m['predicates'].update(Person=[]),True,False)
 add('no-Team-marker-primary-valid-rich-I-fails',lambda m:m['predicates'].update(Team=[]),True,False)
 add('one-Role-primary-valid-rich-shared-Role-I-fails',lambda m:m['predicates'].update(Role=[['r1']]),True,False)
 def same_scope(m):
  for row in m['functions']['scopeToken']:row['value']='scope'
 add('all-Role-scopes-same-primary-valid-rich-different-scope-I-fails',same_scope,True,False)
 add('no-shared-description-pair-primary-valid-rich-I-fails',lambda m:setvalue(m,'expectationToken',['r3'],'default'),True,False)
 def same_holders(m):m['predicates']['HasRole']=[['p1','r1','before'],['p1','r1','after'],['t1','r1','before'],['t1','r1','after']]
 add('fresh-assignment-records-same-holder-set-no-rich-change-witness',same_holders,True,False)
 add('recorded-Role-identity-change-primary-valid-no-universal-frame-imposed',lambda m:setvalue(m,'recordedIdentity',['r1','after'],'default'),True,False)
 add('no-Role-vacuous-primary-fails-rich-I',lambda m:m['predicates'].update(Role=[]),True,False)
 add('nontotal-scope-function',lambda m:m['functions']['scopeToken'].pop(),error='nontotal-function')
 add('ill-sorted-scope-result',lambda m:setvalue(m,'scopeToken',['r1'],'p1'),error='ill-sorted-function-result')
 add('ill-sorted-empty-sentinel',lambda m:m['constants'].update(EMPTY='unknown-token'),error='ill-sorted-constant')
 add('wrong-assignment-projection-arity',lambda m:m['predicates'].update(AssignedAt=[['a1','p1','r1']]),error='ill-sorted-model-tuple')
 add('duplicate-eligibility-tuple',lambda m:m['predicates']['EligibleAuthorityRelationship'].append(['r1','k1']),error='duplicate-predicate-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.team/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-Role-model-controls/v1-candidate','status':'PASS-for-exact-authored-Role-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent supplied Role-position/description/eligibility/holder models and sixteen targets outside T. No actual intension, Person/Team/Reference/entity/record/assignment/grant/history denotation, inherited Team adoption, global disjointness, operational or source-fidelity proof.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
