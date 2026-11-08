"""Independent exact-binding and immutable-revision Event controls; actual time/byte maps pending."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def base_model():
 domains={'Entity':['e1','e2','e3','p1','p2','r1','r2','c1','c2','s1','s2','d1','q1','q2'],'Token':['empty','ground','evidence','payload','open','responded','scope','label'],'State':['before','after']};functions={}
 for n,(args,result) in b.FUNCTIONS.items():
  rows=[]
  for values in itertools.product(*[domains[x] for x in args]):
   e=values[0]
   value=('r2' if e=='e3' else 'r1') if n=='subjectRevisionValue' else 'c1' if n=='contractValue' else ('p2' if e=='e3' else 'd1' if e=='q1' else 'p1') if n=='challengerValue' else ('e1' if e=='r2' else 's1') if n=='subjectOfRevisionValue' else 'before' if n=='initialRecordState' else 'payload' if n=='recordPayloadValue' else {'groundValue':'ground','evidenceValue':'evidence','scopeValue':'scope','labelValue':'label'}[n]
   rows.append({'args':list(values),'value':value})
  functions[n]=rows
 p={n:[] for n in b.SIGNATURE};events=['e1','e2','e3'];p.update(ChallengeEvent=[[e] for e in events],ImmutableRecord=[[e] for e in events+['q1']],AttributableRecord=[[e] for e in events+['q1']],ExactSubjectRevision=[['r1'],['r2']],ExactChallengeContract=[['c1']],ChallengeContract=[['c1']],GroundsStated=[[e] for e in events+['q1']],EvidenceStated=[[e] for e in events+['q1']],GovernedIdentityOrRecord=[[e] for e in events+['q2']],BoundedScope=[[e] for e in events+['q2']],RawDeclaredComplete=[['q1']],Decision=[['d1']],EligibleToContest=[['p1','r1','c1'],['p2','r1','c1'],['p2','r2','c1']],RecordedContestation=[['e1','p1'],['e1','p2'],['e2','p1'],['e3','p2'],['q1','d1']],ContestsRevision=[['e1','r1'],['e2','r1'],['e3','r2'],['q1','r1']],UnderContract=[[e,'c1'] for e in events+['q1']],EventRecordedAt=[[e,t] for e in events for t in domains['State']],ResponseProjection=[['e1','before','open'],['e1','after','responded']],IndependentOwnerDecisionEffect=[['d1','s2','after']],ActualSubjectEffect=[['s2','after']])
 return {'domains':domains,'constants':{'EMPTY':'empty'},'functions':functions,'predicates':p}
def setvalue(m,n,args,value):next(x for x in m['functions'][n] if x['args']==args)['value']=value
def controls():
 rows=[]
 def add(id,change,T=True,I=None,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('exact-immutable-events-with-independent-response-and-other-event-target',lambda m:None,I=True)
 for n in b.OUTCOMES+['AuthenticatedChallenger','TruthOfGrounds','EvidenceAccepted','ChallengeContract']:add('independently-supplied-marker-'+n,lambda m,n=n:m['predicates'][n].append(['e1']),I=True)
 for n in ['ImmutableRecord','AttributableRecord','GroundsStated','EvidenceStated','GovernedIdentityOrRecord','BoundedScope']:add('Event-missing-required-'+n,lambda m,n=n:m['predicates'][n].remove(['e1']),T=False)
 add('selected-revision-not-exact',lambda m:m['predicates']['ExactSubjectRevision'].remove(['r1']),T=False)
 add('selected-Contract-not-exact',lambda m:m['predicates']['ExactChallengeContract'].remove(['c1']),T=False)
 add('selected-Contract-not-Contract',lambda m:m['predicates']['ChallengeContract'].remove(['c1']),T=False)
 add('selected-challenger-not-eligible-for-exact-context',lambda m:m['predicates']['EligibleToContest'].remove(['p1','r1','c1']),T=False)
 add('eligibility-under-another-revision-does-not-transfer',lambda m:m['predicates'].update(EligibleToContest=[['p1','r2','c1'],['p2','r1','c1'],['p2','r2','c1']]),T=False)
 add('selected-challenger-contestation-not-recorded',lambda m:m['predicates']['RecordedContestation'].remove(['e1','p1']),T=False)
 add('selected-revision-relation-missing',lambda m:m['predicates']['ContestsRevision'].remove(['e1','r1']),T=False)
 add('selected-Contract-relation-missing',lambda m:m['predicates']['UnderContract'].remove(['e1','c1']),T=False)
 for n in ['groundValue','evidenceValue']:add('stated-field-empty-'+n,lambda m,n=n:setvalue(m,n,['e1'],'empty'),T=False)
 add('qualified-exact-record-without-Event-reverse-iff-required',lambda m:m['predicates']['ChallengeEvent'].remove(['e1']),T=False)
 add('raw-declared-fields-not-sufficient-for-Event',lambda m:m['predicates']['ChallengeEvent'].append(['q1']),T=False)
 add('extra-subject-revision-violates-one-exact-revision',lambda m:m['predicates']['ContestsRevision'].append(['e1','r2']),T=False)
 add('extra-Contract-violates-one-exact-Contract',lambda m:m['predicates']['UnderContract'].append(['e1','c2']),T=False)
 add('initial-record-state-must-be-recorded',lambda m:m['predicates']['EventRecordedAt'].remove(['e1','before']),T=False)
 add('recorded-state-payload-change-violates-immutability',lambda m:setvalue(m,'recordPayloadValue',['e1','after'],'responded'),T=False)
 def unrecorded_change(m):m['predicates']['EventRecordedAt'].remove(['e1','after']);setvalue(m,'recordPayloadValue',['e1','after'],'responded')
 add('unrecorded-state-payload-change-not-covered-by-recorded-state-guard',unrecorded_change,I=False)
 add('initial-State-label-not-proven-first-in-temporal-order',lambda m:setvalue(m,'initialRecordState',['e1'],'after'),I=False)
 for n in ['ContradictionFinding','Resolution','Decision','AutomaticLifecycleTransition']:add('Event-cannot-collapse-to-'+n,lambda m,n=n:m['predicates'][n].append(['e1']),T=False)
 add('Event-cannot-be-its-own-challenged-subject',lambda m:setvalue(m,'subjectOfRevisionValue',['r1'],'e1'),T=False)
 def selfrevision(m):
  setvalue(m,'subjectRevisionValue',['e1'],'e1');m['predicates']['ExactSubjectRevision'].append(['e1']);m['predicates']['ContestsRevision'].remove(['e1','r1']);m['predicates']['ContestsRevision'].append(['e1','e1']);m['predicates']['EligibleToContest'].append(['p1','e1','c1'])
 add('Event-cannot-be-its-own-revision',selfrevision,T=False)
 add('multiple-recorded-challengers-not-forbidden-by-selected-one-exact-targets',lambda m:None,I=True)
 add('Event-can-be-another-Events-challenged-subject',lambda m:None,I=True)
 add('separate-response-resolution-does-not-make-Event-a-resolution-object',lambda m:m['predicates']['ResolvedResponse'].append(['e2','after']),I=True)
 add('separate-owner-decision-can-affect-challenged-subject',lambda m:m['predicates']['IndependentOwnerDecisionEffect'].append(['d1','s1','after']) or m['predicates']['ActualSubjectEffect'].append(['s1','after']),I=True)
 add('empty-scope-value-not-constrained-by-opaque-bounded-scope',lambda m:setvalue(m,'scopeValue',['e1'],'empty'),I=False)
 def alias(m):
  for n in ['groundValue','evidenceValue','scopeValue','labelValue']:
   for e in ['e1','e2']:setvalue(m,n,[e],'payload')
 add('opaque-ground-evidence-scope-label-values-can-alias',alias,I=True)
 add('no-response-projection-alternative-T-model-rich-I-fails',lambda m:m['predicates'].update(ResponseProjection=[]),I=False)
 add('nontotal-payload-function',lambda m:m['functions']['recordPayloadValue'].pop(),error='nontotal-function')
 add('ill-sorted-revision-function-result',lambda m:setvalue(m,'subjectRevisionValue',['e1'],'absent'),error='ill-sorted-function-result')
 add('ill-sorted-empty-constant',lambda m:m['constants'].update(EMPTY='absent'),error='ill-sorted-constant')
 add('wrong-eligibility-arity',lambda m:m['predicates'].update(EligibleToContest=[['p1','r1']]),error='ill-sorted-model-tuple')
 add('duplicate-recorded-contestation',lambda m:m['predicates']['RecordedContestation'].append(['e1','p1']),error='duplicate-predicate-tuple')
 add('empty-State-carrier',lambda m:m['domains'].update(State=[]),error='empty-or-malformed-domain')
 add('duplicate-function-tuple',lambda m:m['functions']['contractValue'].append(copy.deepcopy(m['functions']['contractValue'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.challenge-contract/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-ChallengeEvent-model-controls/v1-candidate','status':'PASS-for-exact-authored-ChallengeEvent-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent supplied exact contestation, per-event unique revision/Contract and recorded-state payload equality models. Real eligibility/attribution, exact Entity/version/byte/state/temporal coverage, independent response/disposition and universal enforcement remain unresolved.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
