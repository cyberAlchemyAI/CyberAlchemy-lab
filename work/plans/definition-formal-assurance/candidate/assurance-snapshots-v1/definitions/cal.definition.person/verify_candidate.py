"""Independent finite Human/associated record/membership/participation-state checks."""
import itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def base_model():
 entities=['p1','p2','a1','a2','ref1','claim1','role1','role2','m1','m2','perm1','session1','record1','team1','team2','work1','action1','human-only']
 domains={'Entity':entities,'State':['before','after'],'Token':['person-1','person-2','record-1','record-2']}
 functions={n:[{'args':list(xs),'value':'person-2' if xs[0]=='p2' else 'person-1'} for xs in itertools.product(*[domains[s] for s in args])] for n,(args,res) in b.FUNCTIONS.items()}
 for row in functions['carrierIdentity']:row['value']='record-1'
 predicates={n:[] for n in b.SIGNATURE};predicates.update(Person=[['p1'],['p2']],HumanIndividual=[['p1'],['p2'],['human-only']],Account=[['a1'],['a2']],PersonReference=[['ref1']],IdentityClaim=[['claim1']],Role=[['role1'],['role2']],Membership=[['m1'],['m2']],PermissionRecord=[['perm1']],SessionRecord=[['session1']],MachineRecord=[['record1']],Team=[['team1'],['team2']],HumanParticipant=[['p1']],WorkOwner=[['p1']],Reviewer=[['p1']],Represents=[['a1','p1','before'],['a2','p1','after']],ProjectionOf=[['ref1','p1']],ClaimAbout=[['claim1','p1']],Holds=[['p1','role1','before'],['p1','role2','after']],MemberOf=[['p1','team1','before'],['p1','team2','after']],MembershipRecord=[['m1','p1','team1','before'],['m2','p1','team2','after']],PermissionAbout=[['perm1','p1','before']],SessionAbout=[['session1','p1','before']],RecordAbout=[['record1','p1']],OwnsWork=[['p1','work1','before']],AllowedParticipationStep=[['p1','before','after']],Present=[['p1','before'],['p1','after'],['p2','before'],['p2','after']])
 return {'domains':domains,'constants':{},'functions':functions,'predicates':predicates}
def setvalue(m,n,args,value):next(x for x in m['functions'][n] if x['args']==args)['value']=value
def controls():
 rows=[]
 def add(id,change,T=True,I=True,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('Human-Person-distinct-records-two-state-participation-change',lambda m:None)
 add('Human-marker-not-converse-Person-definition',lambda m:None)
 add('multiple-participation-roles-overlap-on-one-Person',lambda m:m['predicates']['Reviewer'].append(['p2']))
 add('Person-not-HumanIndividual-rejected',lambda m:m['predicates'].update(HumanIndividual=[]),False)
 records=[('Account','Represents',['p1','p1','before']),('PersonReference','ProjectionOf',['p1','p1']),('IdentityClaim','ClaimAbout',['p1','p1']),('Role','Holds',['p1','p1','before']),('PermissionRecord','PermissionAbout',['p1','p1','before']),('SessionRecord','SessionAbout',['p1','p1','before']),('MachineRecord','RecordAbout',['p1','p1'])]
 for kind,relation,tuple in records:
  def collapse(m,kind=kind,relation=relation,tuple=tuple):m['predicates'][kind].append(['p1']);m['predicates'][relation].append(tuple)
  add('associated-'+kind+'-cannot-be-Person',collapse,False)
 for kind in ['Account','PersonReference','IdentityClaim','Role','PermissionRecord','SessionRecord','MachineRecord']:add('associated-'+kind+'-missing-role-marker',lambda m,kind=kind:m['predicates'].__setitem__(kind,[]),False)
 def mcollapse(m):m['predicates']['Membership'].append(['p1']);m['predicates']['MembershipRecord'][0]=['p1','p1','team1','before']
 add('membership-record-cannot-be-member-Person',mcollapse,False)
 def tcollapse(m):m['predicates']['Team'].append(['p1']);m['predicates']['MemberOf'][0]=['p1','p1','before'];m['predicates']['MembershipRecord'][0]=['m1','p1','p1','before']
 add('associated-Team-cannot-be-member-Person',tcollapse,False)
 add('member-of-without-membership-record',lambda m:m['predicates'].update(MembershipRecord=[]),False)
 add('membership-record-missing-typed-Membership-role',lambda m:m['predicates'].update(Membership=[]),False)
 add('membership-exact-state-mismatch',lambda m:m['predicates']['MembershipRecord'].__setitem__(0,['m1','p1','team1','after']),False)
 add('member-of-target-not-Team',lambda m:m['predicates'].update(Team=[]),False)
 add('membership-record-has-no-automatic-member-of-converse',lambda m:m['predicates'].update(MemberOf=[]),True,False)
 add('no-reference-required-by-primary-theory',lambda m:m['predicates'].update(ProjectionOf=[]),True,False)
 add('no-participation-step-primary-theory-valid-richer-I-fails',lambda m:m['predicates'].update(AllowedParticipationStep=[]),True,False)
 add('same-state-step-primary-theory-valid-richer-change-I-fails',lambda m:m['predicates'].update(AllowedParticipationStep=[['p1','before','before']]),True,False)
 add('missing-Person-after-participation-step',lambda m:m['predicates'].update(Present=[['p1','before'],['p2','before'],['p2','after']]),False)
 add('Person-recorded-identity-changes-with-participation',lambda m:setvalue(m,'recordedPersonIdentity',['p1','after'],'person-2'),False)
 add('before-recorded-identity-disagrees-with-stable-token',lambda m:setvalue(m,'recordedPersonIdentity',['p1','before'],'record-1'),False)
 add('step-subject-is-account-not-Person',lambda m:m['predicates'].update(AllowedParticipationStep=[['a1','before','after']]),False,False)
 add('carrier-and-Person-tokens-may-lexically-overlap',lambda m:setvalue(m,'carrierIdentity',['record1'],'person-1'))
 add('same-account-can-represent-two-People-no-global-injectivity',lambda m:m['predicates']['Represents'].append(['a1','p2','before']),True,False)
 add('multiple-accounts-at-one-state-permitted',lambda m:m['predicates']['Represents'].append(['a2','p1','before']))
 add('claim-assertion-does-not-replace-Person-reference-role',lambda m:m['predicates'].update(PersonReference=[]),False)
 add('reference-only-private-attribute-inference-forbidden',lambda m:m['predicates'].update(AllowedReferenceOnlyPrivateAttributes=[['ref1']]),False)
 add('independent-exact-action-authorization-permitted',lambda m:m['predicates'].update(AuthorizedFor=[['p1','action1','before']]))
 add('separately-required-successor-marker-not-universally-forbidden',lambda m:m['predicates'].update(SuccessorPersonRequired=[['p1','before','after']]))
 for n in b.OUTCOMES:add('independently-supported-world-outcome-permitted-'+n,lambda m,n=n:m['predicates'].__setitem__(n,[['p1']]))
 def noperson(m):m['predicates']['Person']=[];m['predicates']['AllowedParticipationStep']=[]
 add('no-Person-vacuous-theory-fails-connected-I',noperson,True,False)
 add('nontotal-recorded-Person-identity',lambda m:m['functions']['recordedPersonIdentity'].pop(),error='nontotal-function')
 add('ill-sorted-identity-token',lambda m:setvalue(m,'personIdentity',['p1'],'before'),error='ill-sorted-function-result')
 add('wrong-membership-record-arity',lambda m:m['predicates'].update(MembershipRecord=[['m1','p1','team1']]),error='ill-sorted-model-tuple')
 add('duplicate-membership-record-tuple',lambda m:m['predicates']['MembershipRecord'].append(['m1','p1','team1','before']),error='duplicate-predicate-tuple')
 add('empty-state-domain',lambda m:m['domains'].update(State=[]),error='empty-or-malformed-domain')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.person-reference/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-person-model-controls/v1-candidate','status':'PASS-for-exact-authored-person-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent authored finite Human/associated-record/membership/participation-frame models and seventeen targets outside T. Actual Human/carrier/token/state/record/evidence/authority/privacy denotation, operational policy/runtime preservation, source precedence and whole-definition acceptance remain unresolved.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
