"""Independent finite membership endpoint, attribution, current-member and Team-frame checks."""
import itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def base_model():
 entities=['m1','m2','m3','p1','p2','t1','t2','r1','a1','role1','work1','action1']
 domains={'Entity':entities,'State':['before','after'],'Time':['q0','q1','q2'],'Token':['member-token','Team-token','purpose-token','scope-token','owner-token','other-token']}
 functions={}
 for n,(args,result) in b.FUNCTIONS.items():
  default={'memberPerson':'p1','memberTeam':'t1','attributor':'a1','membershipIdentity':'member-token','teamIdentity':'Team-token','recordedTeamIdentity':'Team-token','teamPurpose':'purpose-token','teamScope':'scope-token','teamOwnerBoundary':'owner-token','periodStart':'q0','periodEnd':'q2'}[n]
  functions[n]=[{'args':list(xs),'value':'p2' if n=='memberPerson' and xs[0]=='m3' else default} for xs in itertools.product(*[domains[s] for s in args])]
 predicates={n:[] for n in b.SIGNATURE};predicates.update(TeamMembership=[['m1'],['m2'],['m3']],Person=[['p1'],['p2']],PersonReference=[['r1']],Team=[['t1'],['t2']],CollectiveIdentity=[['t1'],['t2']],AttributionParty=[['a1']],HasLifecycle=[['m1'],['m2'],['m3']],HasPeriod=[['m1'],['m2'],['m3']],FiniteEnd=[['m1'],['m3']],OpenEnd=[['m2']],HasPurpose=[['t1'],['t2']],HasScope=[['t1'],['t2']],HasOwnerRoute=[['t1'],['t2']],Binds=[['m1','p1','t1'],['m2','p1','t1'],['m3','p2','t1']],AttributedTo=[['m1','a1'],['m2','a1'],['m3','a1']],ReferenceDenotes=[['r1','p1']],CurrentAt=[['m1','before','q1'],['m3','after','q1']],ActiveMembership=[['m1','before'],['m3','after']],ProposedMembership=[['m2','before']],ActiveTeam=[['t1','before','q1'],['t1','after','q1']],ProposedTeam=[['t2','before']],PresentTeam=[['t1','before'],['t1','after'],['t2','before']],AllowedMembershipChange=[['t1','before','after']],RecordedMember=[['m1','p1','t1','before'],['m3','p2','t1','after']],WithinPeriod=[['m1','q1'],['m2','q1'],['m3','q1']],Before=[['q0','q1'],['q0','q2'],['q1','q2']])
 return {'domains':domains,'constants':{},'functions':functions,'predicates':predicates}
def setvalue(m,n,args,value):next(x for x in m['functions'][n] if x['args']==args)['value']=value
def controls():
 rows=[]
 def add(id,change,T=True,I=True,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('independent-memberships-singular-endpoints-proposed-Team-and-stable-change',lambda m:None)
 add('two-memberships-same-Person-Team-pair-permitted',lambda m:None)
 add('same-identity-token-does-not-merge-membership-Entities',lambda m:None)
 add('current-membership-need-not-have-active-label-in-primary-theory',lambda m:m['predicates'].update(ActiveMembership=[]))
 add('primary-currentness-not-derived-from-period-labels',lambda m:m['predicates'].update(WithinPeriod=[]))
 add('nonmembership-binding-not-globally-forbidden',lambda m:m['predicates']['Binds'].append(['a1','t2','r1']))
 add('independently-granted-exact-action-permitted',lambda m:m['predicates'].update(AuthorizedFor=[['p1','action1','before']]))
 add('independent-role-and-responsibility-permitted',lambda m:m['predicates'].update(Holds=[['p1','role1','before']],OwnsResponsibility=[['p1','work1','before']]))
 for n in b.OUTCOMES:add('independently-supported-outcome-'+n,lambda m,n=n:m['predicates'].__setitem__(n,[['m1']]))
 add('missing-Person-marker',lambda m:m['predicates'].update(Person=[]),False)
 add('missing-Team-marker',lambda m:m['predicates'].update(Team=[]),False,False)
 add('missing-lifecycle-marker',lambda m:m['predicates'].update(HasLifecycle=[]),False)
 add('missing-attribution-party-marker',lambda m:m['predicates'].update(AttributionParty=[]),False)
 add('missing-exact-attribution',lambda m:m['predicates'].update(AttributedTo=[]),False,False)
 add('missing-exact-binding',lambda m:m['predicates']['Binds'].pop(0),False)
 add('additional-Person-binding-conflicts-with-one-Person',lambda m:m['predicates']['Binds'].append(['m1','p2','t1']),False)
 add('additional-Team-binding-conflicts-with-one-Team',lambda m:m['predicates']['Binds'].append(['m1','p1','t2']),False)
 def collapse(m):setvalue(m,'memberPerson',['m1'],'m1');m['predicates']['Person'].append(['m1']);m['predicates']['Binds'][0]=['m1','m1','t1']
 add('membership-is-not-Person-endpoint',collapse,False,False)
 def collapse_team(m):setvalue(m,'memberTeam',['m1'],'m1');m['predicates']['Team'].append(['m1']);m['predicates']['Binds'][0]=['m1','p1','m1']
 add('membership-is-not-Team-endpoint',collapse_team,False,False)
 def same_endpoints(m):setvalue(m,'memberTeam',['m1'],'p1');m['predicates']['Team'].append(['p1']);m['predicates']['Binds'][0]=['m1','p1','p1']
 add('Person-and-Team-endpoint-not-collapsed',same_endpoints,False,False)
 add('membership-function-does-not-imply-PersonReference-is-Person',lambda m:setvalue(m,'memberPerson',['m1'],'r1'),False,False)
 def attr_person(m):setvalue(m,'attributor',['m1'],'p1');m['predicates']['AttributionParty'].append(['p1']);m['predicates']['AttributedTo'][0]=['m1','p1']
 add('attributor-can-be-independently-typed-Person',attr_person)
 add('multiple-attribution-links-not-globally-forbidden',lambda m:m['predicates']['AttributedTo'].append(['m1','p2']))
 add('missing-Team-collective-marker',lambda m:m['predicates'].update(CollectiveIdentity=[]),False)
 for n in ['HasPurpose','HasScope','HasOwnerRoute']:add('missing-Team-'+n,lambda m,n=n:m['predicates'].__setitem__(n,[]),False)
 add('active-Team-without-current-member',lambda m:m['predicates'].update(CurrentAt=[]),False)
 add('active-Team-current-member-wrong-state',lambda m:m['predicates']['CurrentAt'].__setitem__(0,['m1','after','q1']),False)
 add('active-Team-current-member-wrong-time',lambda m:m['predicates']['CurrentAt'].__setitem__(0,['m1','before','q2']),False)
 add('proposed-Team-no-membership-allowed',lambda m:None)
 add('proposed-Team-can-have-membership-but-rich-empty-Team-I-fails',lambda m:m['predicates'].update(ProposedTeam=[['t1','before']]),True,False)
 add('no-active-Team-primary-valid-rich-I-fails',lambda m:m['predicates'].update(ActiveTeam=[]),True,False)
 add('no-allowed-change-primary-valid-rich-I-fails',lambda m:m['predicates'].update(AllowedMembershipChange=[]),True,False)
 add('unchanged-members-primary-valid-rich-change-I-fails',lambda m:m['predicates'].update(RecordedMember=[]),True,False)
 add('same-Person-set-with-fresh-membership-records-primary-valid-rich-change-I-fails',lambda m:m['predicates'].update(RecordedMember=[['m1','p1','t1','before'],['m2','p1','t1','after']]),True,False)
 add('no-reference-resolution-primary-valid-rich-I-fails',lambda m:m['predicates'].update(ReferenceDenotes=[]),True,False)
 add('no-explicit-period-primary-valid-rich-I-fails',lambda m:m['predicates'].update(HasPeriod=[]),True,False)
 add('no-open-period-primary-valid-rich-I-fails',lambda m:m['predicates'].update(OpenEnd=[]),True,False)
 add('no-finite-period-marker-primary-valid-rich-finite-I-fails',lambda m:m['predicates'].update(FiniteEnd=[]),True,False)
 add('stable-boundary-change-cannot-change-Team-identity',lambda m:setvalue(m,'recordedTeamIdentity',['t1','after'],'other-token'),False)
 add('stable-boundary-change-requires-Team-presence',lambda m:m['predicates'].update(PresentTeam=[]),False)
 def different_scope(m):setvalue(m,'teamScope',['t1','after'],'other-token');setvalue(m,'recordedTeamIdentity',['t1','after'],'other-token')
 add('changed-scope-outside-stable-Team-frame-primary-valid-rich-I-fails',different_scope,True,False)
 def vacuous(m):m['predicates'].update(TeamMembership=[],ActiveTeam=[],AllowedMembershipChange=[])
 add('no-memberships-vacuous-primary-fails-rich-I',vacuous,True,False)
 add('nontotal-Person-selector',lambda m:m['functions']['memberPerson'].pop(),error='nontotal-function')
 add('ill-sorted-period-end',lambda m:setvalue(m,'periodEnd',['m1'],'before'),error='ill-sorted-function-result')
 add('wrong-binding-arity',lambda m:m['predicates'].update(Binds=[['m1','p1']]),error='ill-sorted-model-tuple')
 add('duplicate-currentness-tuple',lambda m:m['predicates']['CurrentAt'].append(['m1','before','q1']),error='duplicate-predicate-tuple')
 add('empty-Time-domain',lambda m:m['domains'].update(Time=[]),error='empty-or-malformed-domain')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.person/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-team-membership-model-controls/v1-candidate','status':'PASS-for-exact-authored-membership-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent authored finite Membership endpoints/attribution/active-Team/identity-frame models and seventeen targets outside T. Actual PersonReference/Human/Team/carrier/token/state/period/currentness/attribution/evidence/authority denotation, operational policy/runtime preservation, source precedence and whole-definition acceptance remain unresolved.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
