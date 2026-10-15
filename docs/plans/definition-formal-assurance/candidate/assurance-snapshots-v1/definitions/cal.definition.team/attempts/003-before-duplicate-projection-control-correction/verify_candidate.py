"""Independent finite Team/neighbor/owner/current-member/boundary-frame controls."""
import itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def base_model():
 entities=['t1','t2','t3','p1','p2','m1','m2','m3','m4','route1','role1','res1','authority1','action1','product1','project1','goal1','organization1']
 domains={'Entity':entities,'State':['before','after'],'Time':['q0','q1','q2'],'Token':['empty','purpose','scope','owner-route','boundary','Team-one','Team-two','Team-three','other']}
 functions={}
 for n,(args,result) in b.FUNCTIONS.items():
  default={'observationTime':'q0','purpose':'purpose','scopeToken':'scope','ownerRouteToken':'owner-route','ownerRouteRecord':'route1','ownerBoundary':'boundary','identity':'other','recordedPurpose':'purpose','recordedScope':'scope','recordedOwnerBoundary':'boundary','recordedIdentity':'other'}[n]
  functions[n]=[{'args':list(xs),'value':{'t1':'Team-one','t2':'Team-two','t3':'Team-three'}.get(xs[0],default) if n in ['identity','recordedIdentity'] else 'q1' if n=='observationTime' and xs[0]=='after' else default} for xs in itertools.product(*[domains[s] for s in args])]
 predicates={n:[] for n in b.SIGNATURE};predicates.update(Team=[['t1'],['t2'],['t3']],CollectiveIdentity=[['t1'],['t2'],['t3']],Actor=[['t1']],Action=[['action1']],Person=[['p1'],['p2']],TeamMembership=[['m1'],['m2'],['m3'],['m4']],ResponsibilityRecord=[['res1']],HasLifecycle=[['t1'],['t2'],['t3']],HasChallengeRoute=[['t1'],['t2'],['t3']],OwnerRouteRecord=[['route1']],RoleRecord=[['role1']],AuthorityEnvelope=[['authority1']],ProductRecord=[['product1']],ProjectRecord=[['project1']],GoalRecord=[['goal1']],OrganizationRecord=[['organization1']],OwnerQualifiedBy=[['t1','route1'],['t2','route1'],['t3','route1']],Binds=[['m1','p1','t1'],['m2','p1','t1'],['m3','p2','t1'],['m4','p1','t3']],CurrentAt=[['m1','before','q0'],['m3','after','q1'],['m4','before','q0']],ActiveTeam=[['t1','before','q0'],['t1','after','q1']],ProposedTeam=[['t2','before']],Present=[['t1','before'],['t1','after'],['t2','before'],['t3','before']],MembershipProjection=[['t1','m1','before'],['t1','m2','before'],['t1','m3','after'],['t1','m2','after'],['t3','m4','before']],AllowedMembershipChange=[['t1','before','after']],Holds=[['t1','role1','before']],OwnsResponsibility=[['t1','res1','before']],AuthorityProjection=[['t1','authority1','before']])
 return {'domains':domains,'constants':{'EMPTY':'empty'},'functions':functions,'predicates':predicates}
def setvalue(m,n,args,value):next(x for x in m['functions'][n] if x['args']==args)['value']=value
def controls():
 rows=[]
 def add(id,change,T=True,I=True,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('qualified-collective-active-current-change-proposed-empty-and-Actor-overlap',lambda m:None)
 add('two-distinct-Teams-share-current-Person-set-and-boundary-triple',lambda m:None)
 add('stale-listed-membership-does-not-block-separate-current-witness',lambda m:None)
 add('Team-can-act-as-Actor-without-being-Role-or-grant',lambda m:m['predicates']['Actor'].append(['t3']))
 for n in b.OUTCOMES:add('independently-supported-world-fact-'+n,lambda m,n=n:m['predicates'].__setitem__(n,[['t1']]))
 add('independent-exact-action-authorization-allowed',lambda m:m['predicates'].update(AuthorizedFor=[['t1','action1','before']]))
 add('independent-responsibility-authority-grant-allowed',lambda m:m['predicates'].update(GrantForResponsibility=[['res1']]))
 for n in b.NEIGHBORS:add('Team-cannot-be-neighbor-record-'+n,lambda m,n=n:m['predicates'][n].append(['t1']),False)
 for n in ['CollectiveIdentity','HasLifecycle','HasChallengeRoute']:add('missing-Team-'+n,lambda m,n=n:m['predicates'].__setitem__(n,[]),False)
 for n in ['purpose','scopeToken','ownerRouteToken','ownerBoundary']:add('empty-selected-Team-'+n,lambda m,n=n:setvalue(m,n,['t1'],'empty'),False)
 add('owner-route-record-missing-type',lambda m:m['predicates'].update(OwnerRouteRecord=[]),False)
 add('recorded-owner-qualification-missing',lambda m:m['predicates'].update(OwnerQualifiedBy=[]),False,False)
 add('owner-route-record-cannot-be-Team',lambda m:setvalue(m,'ownerRouteRecord',['t1'],'t1'),False)
 for relation,kind in [('MembershipProjection','TeamMembership'),('Holds','RoleRecord'),('OwnsResponsibility','ResponsibilityRecord'),('AuthorityProjection','AuthorityEnvelope')]:
  def collapse(m,relation=relation,kind=kind):m['predicates'][kind].append(['t1']);m['predicates'][relation].append(['t1','t1','before'])
  add('associated-'+kind+'-does-not-collapse-into-Team',collapse,False)
  add('associated-'+kind+'-needs-typed-record',lambda m,kind=kind:m['predicates'].__setitem__(kind,[]),False,False if kind=='TeamMembership' else True)
 add('active-Team-needs-current-membership',lambda m:m['predicates'].update(CurrentAt=[]),False,False)
 add('active-Team-current-witness-wrong-time',lambda m:m['predicates']['CurrentAt'].__setitem__(0,['m1','before','q1']),False,False)
 add('active-Team-current-witness-wrong-state',lambda m:m['predicates']['CurrentAt'].__setitem__(0,['m1','after','q0']),False,False)
 add('active-Team-needs-Person-marker',lambda m:m['predicates'].update(Person=[]),False)
 add('active-Team-cannot-be-its-own-current-Person',lambda m:m['predicates'].update(Person=[['t1'],['p1'],['p2']],Binds=[['m1','t1','t1'],['m2','p1','t1'],['m3','p2','t1'],['m4','p1','t3']]),False,False)
 add('active-Team-needs-presence',lambda m:m['predicates'].update(Present=[]),False)
 add('no-active-Team-primary-valid-rich-I-fails',lambda m:m['predicates'].update(ActiveTeam=[]),True,False)
 add('proposed-Team-can-have-members-but-rich-empty-proposal-I-fails',lambda m:m['predicates'].update(ProposedTeam=[['t1','before']]),True,False)
 add('no-proposal-primary-valid-rich-I-fails',lambda m:m['predicates'].update(ProposedTeam=[]),True,False)
 add('no-Actor-overlap-primary-valid-rich-I-fails',lambda m:m['predicates'].update(Actor=[]),True,False)
 add('no-Role-holding-primary-valid-rich-I-fails',lambda m:m['predicates'].update(Holds=[]),True,False)
 add('no-responsibility-owning-primary-valid-rich-I-fails',lambda m:m['predicates'].update(OwnsResponsibility=[]),True,False)
 add('same-observation-time-primary-valid-rich-distinct-time-I-fails',lambda m:setvalue(m,'observationTime',['after'],'q0'),True,False)
 add('no-Action-population-primary-and-rich-I-valid',lambda m:m['predicates'].update(Action=[]))
 add('no-allowed-change-primary-valid-rich-I-fails',lambda m:m['predicates'].update(AllowedMembershipChange=[]),True,False)
 def same_people(m):m['predicates']['MembershipProjection'][2]=['t1','m2','after'];m['predicates']['CurrentAt'][1]=['m2','after','q1']
 add('fresh-record-same-current-Person-set-primary-valid-rich-change-I-fails',same_people,True,False)
 add('no-current-shared-set-Team-projection-primary-valid-rich-I-fails',lambda m:m['predicates']['MembershipProjection'].pop(),True,False)
 add('stable-membership-step-cannot-change-Team-identity',lambda m:setvalue(m,'recordedIdentity',['t1','after'],'other'),False)
 def scope_changes(m):setvalue(m,'recordedScope',['t1','after'],'other');setvalue(m,'recordedIdentity',['t1','after'],'other')
 add('changed-scope-outside-stable-frame-primary-valid-rich-I-fails',scope_changes,True,False)
 def collision(m):setvalue(m,'identity',['t3'],'Team-one');setvalue(m,'recordedIdentity',['t3','before'],'Team-one');setvalue(m,'recordedIdentity',['t3','after'],'Team-one')
 add('same-identity-token-does-not-equate-Team-Entities',collision)
 add('membership-record-can-bind-extra-Person-without-importing-complete-membership-theory',lambda m:m['predicates']['Binds'].append(['m2','p2','t1']))
 def no_teams(m):m['predicates'].update(Team=[],ActiveTeam=[],AllowedMembershipChange=[])
 add('no-Team-vacuous-primary-fails-rich-I',no_teams,True,False)
 add('nontotal-purpose-function',lambda m:m['functions']['purpose'].pop(),error='nontotal-function')
 add('ill-sorted-owner-route-result',lambda m:setvalue(m,'ownerRouteRecord',['t1'],'purpose'),error='ill-sorted-function-result')
 add('ill-sorted-empty-sentinel',lambda m:m['constants'].update(EMPTY='unknown-token'),error='ill-sorted-constant')
 add('wrong-membership-binding-arity',lambda m:m['predicates'].update(Binds=[['m1','p1']]),error='ill-sorted-model-tuple')
 add('duplicate-current-membership-tuple',lambda m:m['predicates']['CurrentAt'].append(['m1','before','q0']),error='duplicate-predicate-tuple')
 add('empty-Token-domain',lambda m:m['domains'].update(Token=[]),error='empty-or-malformed-domain')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.team-membership/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-Team-model-controls/v1-candidate','status':'PASS-for-exact-authored-Team-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent authored finite Team/owner/neighbor-record/current-member/stable-boundary models and eighteen targets outside T. Actual collective/PersonReference/Human/carrier/token/state/currentness/owner/purpose/scope/evidence/authority denotation, operational policy/runtime preservation, source precedence and whole-definition acceptance remain unresolved.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
