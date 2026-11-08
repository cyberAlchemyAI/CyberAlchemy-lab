"""Independent complete-observation,exact-join and normative-retention finite controls."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def base_model():
 entities=['h1','h2','h3','e1','e2','s1','s2','t1','u1','c1','raw'];histories=['h1','h2','h3'];domains={'Entity':entities,'Token':['empty','id','digest','cursor','other','*']}
 maps={'resultingGovernanceState':lambda e:'s2' if e=='e2' else 's1','semanticEvent':lambda e:'t1',**{n:lambda e,val=val:val for n,val in [('joinedSemanticId','id'),('joinedSemanticDigest','digest'),('joinedSemanticCursor','cursor'),('semanticId','id'),('semanticDigest','digest'),('semanticCursor','cursor')]}}
 functions={n:[{'args':[e],'value':fn(e)} for e in entities] for n,fn in maps.items()}
 p={n:[] for n in b.SIGNATURE};p.update(GovernanceEventHistory=[[e] for e in histories],GovernedIdentityOrRecord=[[e] for e in histories],BoundedScope=[[e] for e in histories],ObservesGovernanceState=[[e] for e in histories],AppendOnlyRequired=[[e] for e in histories],EntryRole=[['e1'],['e2']],GovernanceStateRole=[['s1'],['s2']],CompleteGovernanceStateRole=[['s1'],['s2']],SemanticEventRole=[['t1']],UpstreamEvidenceRole=[['c1']],Contains=[['h1','e1'],['h2','e1'],['h2','e2']],UpstreamEvidence=[['e1','c1'],['e2','c1']],SuccessorHistory=[['h1','h2']],PriorEntryRetentionRequired=[['h2','e1']],ConsumerRole=[['u1']],ConsumerUse=[['h1','u1']],UseInApplicability=[['h1','u1']],RawIndex=[['raw']],CurrentHistory=[['h1']])
 for n in b.QUALIFIERS:p[n]=[[e] for e in histories]
 return {'domains':domains,'constants':{'EMPTY':'empty'},'functions':functions,'predicates':p}
def setfn(m,n,args,value):next(x for x in m['functions'][n] if x['args']==args)['value']=value
def controls():
 rows=[]
 def add(id,change,T=True,I=None,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('typed-complete-observations-exact-join-and-normative-retention',lambda m:None,I=True)
 for n in b.OUTCOMES:add('independent-outcome-'+n,lambda m,n=n:m['predicates'][n].append(['h1']))
 for n in b.QUALIFIERS:add('missing-genus-'+n,lambda m,n=n:m['predicates'][n].remove(['h1']),T=False)
 add('reverse-genus-iff-missing',lambda m:m['predicates']['GovernanceEventHistory'].remove(['h1']),T=False)
 for n in ['GovernedIdentityOrRecord','BoundedScope','ObservesGovernanceState','AppendOnlyRequired']:add('missing-history-'+n,lambda m,n=n:m['predicates'][n].remove(['h1']),T=False)
 for n,e in [('EntryRole','e1'),('GovernanceStateRole','s1'),('CompleteGovernanceStateRole','s1'),('SemanticEventRole','t1'),('UpstreamEvidenceRole','c1')]:add('untyped-observation-'+n,lambda m,n=n,e=e:m['predicates'][n].remove([e]),T=False)
 add('observation-without-upstream-evidence',lambda m:m['predicates']['UpstreamEvidence'].remove(['e1','c1']),T=False)
 for name in ['Id','Digest','Cursor']:
  add('mismatched-semantic-'+name,lambda m,name=name:setfn(m,'joinedSemantic'+name,['e1'],'other'),T=False)
  add('empty-matching-semantic-'+name,lambda m,name=name:(setfn(m,'joinedSemantic'+name,['e1'],'empty'),setfn(m,'semantic'+name,['t1'],'empty'),setfn(m,'joinedSemantic'+name,['e2'],'empty')),T=False)
 add('successor-without-history-role',lambda m:m['predicates']['GovernanceEventHistory'].remove(['h2']),T=False)
 add('missing-prior-entry-retention-requirement',lambda m:m['predicates']['PriorEntryRetentionRequired'].clear(),T=False)
 for n in ['OriginatesPolicy','ReplacesPolicy','OriginatesChallengeDecision','ReplacesChallengeDecision','OriginatesAdmissionDecision','ReplacesAdmissionDecision','OriginatesOtherAuthorityDecision','ReplacesOtherAuthorityDecision']:add('forbidden-history-decision-authorship-'+n,lambda m,n=n:m['predicates'][n].append(['h1']),T=False)
 for n in b.INFER_FLAGS:add('forbidden-inference-'+n,lambda m,n=n:m['predicates'][n].append(['h1']),T=False)
 for n in b.ROLES:add('forbidden-sibling-collapse-'+n,lambda m,n=n:m['predicates'][n].append(['h1']),T=False)
 add('consumer-without-role',lambda m:m['predicates']['ConsumerRole'].clear(),T=False)
 add('consumer-outside-applicability',lambda m:m['predicates']['UseInApplicability'].clear(),T=False)
 add('empty-history-permitted',lambda m:None,I=True)
 add('two-observations-of-one-semantic-event-permitted',lambda m:None,I=True)
 add('shared-upstream-evidence-permitted',lambda m:None,I=True)
 add('canonical-history-marker-does-not-enforce-unique-stream',lambda m:None,I=True)
 add('opaque-cursor-token-not-a-positive-integer',lambda m:(setfn(m,'joinedSemanticCursor',['e1'],'*'),setfn(m,'joinedSemanticCursor',['e2'],'*'),setfn(m,'semanticCursor',['t1'],'*')),I=True)
 add('opaque-digest-token-not-byte-authentication',lambda m:(setfn(m,'joinedSemanticDigest',['e1'],'other'),setfn(m,'joinedSemanticDigest',['e2'],'other'),setfn(m,'semanticDigest',['t1'],'other')),I=True)
 add('retention-requirement-does-not-force-successor-membership',lambda m:m['predicates']['Contains'].remove(['h2','e1']))
 add('raw-index-may-have-history-entry-without-genus',lambda m:m['predicates']['Contains'].append(['raw','e1']),I=True)
 add('semantic-patch-marker-not-imported-from-carrier',lambda m:m['predicates']['SemanticPatchAuthority'].append(['h1']),I=True)
 add('extra-retention-relation-permitted',lambda m:m['predicates']['PriorEntryRetentionRequired'].append(['h2','raw']),I=True)
 add('nontotal-state-function',lambda m:m['functions']['resultingGovernanceState'].pop(),error='nontotal-function')
 add('ill-sorted-semantic-function',lambda m:setfn(m,'semanticEvent',['e1'],'id'),error='ill-sorted-function-result')
 add('ill-sorted-empty-constant',lambda m:m['constants'].update(EMPTY='absent'),error='ill-sorted-constant')
 add('wrong-history-entry-arity',lambda m:m['predicates'].update(Contains=[['h1']]),error='ill-sorted-model-tuple')
 add('duplicate-entry-tuple',lambda m:m['predicates']['Contains'].append(['h1','e1']),error='duplicate-predicate-tuple')
 add('empty-entity-domain',lambda m:m['domains'].update(Entity=[]),error='empty-or-malformed-domain')
 add('duplicate-semantic-function-tuple',lambda m:m['functions']['semanticEvent'].append(copy.deepcopy(m['functions']['semanticEvent'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.context-view/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-GovernanceEventHistory-model-controls/v1-candidate','status':'PASS-for-exact-authored-GovernanceEventHistory-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent complete-state and exact-join markers,upstream evidence and normative retention. Actual state/hash/evidence/persistence/owner maps pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
