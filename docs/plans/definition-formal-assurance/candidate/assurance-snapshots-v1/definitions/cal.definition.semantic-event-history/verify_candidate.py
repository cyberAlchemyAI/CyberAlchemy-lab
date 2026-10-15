"""Independent per-subject complete-state,strict-order and declared digest-link controls."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def base_model():
 entities=['h1','h2','h3','e1','e2','s1','s2','o1','u1','d1','raw'];histories=['h1','h2','h3'];domains={'Entity':entities,'Token':['empty','digest1','digest2','cursor1','cursor2','other','*']}
 maps={'historySubject':lambda e:'o1','eventSubject':lambda e:'o1','resultingSemanticState':lambda e:'s2' if e=='e2' else 's1','stateSubject':lambda e:'o1','eventDigest':lambda e:'digest2' if e=='e2' else 'digest1','previousDigest':lambda e:'digest1' if e=='e2' else 'empty','eventCursor':lambda e:'cursor2' if e=='e2' else 'cursor1'}
 functions={n:[{'args':[e],'value':fn(e)} for e in entities] for n,fn in maps.items()}
 p={n:[] for n in b.SIGNATURE};p.update(SemanticEventHistory=[[e] for e in histories],GovernedIdentityOrRecord=[[e] for e in histories],BoundedScope=[[e] for e in histories],AppendOnlyRequired=[[e] for e in histories],EntryRole=[['e1'],['e2']],SemanticStateRole=[['s1'],['s2']],CompleteSemanticStateRole=[['s1'],['s2']],OntologySubjectRole=[['o1']],Contains=[['h1','e1'],['h2','e1'],['h2','e2']],Before=[['h2','e1','e2']],PredecessorLink=[['h2','e2','e1']],RecordReplaySource=[['e1'],['e2']],SuccessorHistory=[['h1','h2']],PriorEntryRetentionRequired=[['h2','e1']],DerivedSnapshot=[['h1','d1']],DerivedView=[['h1','d1']],CalculatedSnapshotRole=[['d1']],CalculatedViewRole=[['d1']],ConsumerRole=[['u1']],ConsumerUse=[['h1','u1']],UseInApplicability=[['h1','u1']],RawIndex=[['raw']],CurrentHistory=[['h1']])
 for n in b.QUALIFIERS:p[n]=[[e] for e in histories]
 return {'domains':domains,'constants':{'EMPTY':'empty'},'functions':functions,'predicates':p}
def setfn(m,n,args,value):next(x for x in m['functions'][n] if x['args']==args)['value']=value
def third_entry(m,cyclic=False):
 m['domains']['Entity'].append('e3')
 for n,rows in m['functions'].items():rows.append({'args':['e3'],'value':next(x for x in rows if x['args']==['e2'])['value']})
 for n in ['EntryRole','RecordReplaySource']:m['predicates'][n].append(['e3'])
 m['predicates']['Contains'].append(['h2','e3']);m['predicates']['Before'] += [['h2','e2','e3'],['h2','e3','e1'] if cyclic else ['h2','e1','e3']]
def controls():
 rows=[]
 def add(id,change,T=True,I=None,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('typed-per-subject-complete-state-order-links-and-derived-boundary',lambda m:None,I=True)
 for n in b.OUTCOMES:add('independent-outcome-'+n,lambda m,n=n:m['predicates'][n].append(['h1']))
 for n in b.QUALIFIERS:add('missing-genus-'+n,lambda m,n=n:m['predicates'][n].remove(['h1']),T=False)
 add('reverse-genus-iff-missing',lambda m:m['predicates']['SemanticEventHistory'].remove(['h1']),T=False)
 for n in ['GovernedIdentityOrRecord','BoundedScope','AppendOnlyRequired']:add('missing-history-'+n,lambda m,n=n:m['predicates'][n].remove(['h1']),T=False)
 for n,e in [('EntryRole','e1'),('SemanticStateRole','s1'),('CompleteSemanticStateRole','s1'),('OntologySubjectRole','o1'),('RecordReplaySource','e1')]:add('untyped-entry-or-replay-'+n,lambda m,n=n,e=e:m['predicates'][n].remove([e]),T=False)
 add('event-subject-mismatch',lambda m:setfn(m,'eventSubject',['e1'],'raw'),T=False)
 add('resulting-state-subject-mismatch',lambda m:setfn(m,'stateSubject',['s1'],'raw'),T=False)
 for n in ['eventDigest','eventCursor']:add('empty-'+n,lambda m,n=n:setfn(m,n,['e1'],'empty'),T=False)
 add('missing-order-between-distinct-contained-entries',lambda m:m['predicates']['Before'].clear(),T=False)
 add('order-self-loop',lambda m:m['predicates']['Before'].append(['h2','e1','e1']),T=False)
 add('order-both-directions',lambda m:m['predicates']['Before'].append(['h2','e2','e1']),T=False)
 add('order-entry-outside-history',lambda m:m['predicates']['Before'].append(['h2','e1','raw']),T=False)
 add('three-entry-nontransitive-cycle',lambda m:third_entry(m,True),T=False)
 add('three-entry-strict-transitive-order',lambda m:third_entry(m),I=True)
 add('predecessor-not-earlier',lambda m:m['predicates']['PredecessorLink'].append(['h2','e1','e2']),T=False)
 add('predecessor-outside-history',lambda m:m['predicates']['PredecessorLink'].append(['h2','e2','raw']),T=False)
 add('previous-digest-link-mismatch',lambda m:setfn(m,'previousDigest',['e2'],'other'),T=False)
 add('successor-without-history-role',lambda m:m['predicates']['SemanticEventHistory'].remove(['h2']),T=False)
 add('successor-changes-subject',lambda m:(m['predicates']['OntologySubjectRole'].append(['raw']),setfn(m,'historySubject',['h3'],'raw'),m['predicates']['SuccessorHistory'].append(['h1','h3'])),T=False)
 add('missing-prior-entry-retention-requirement',lambda m:m['predicates']['PriorEntryRetentionRequired'].clear(),T=False)
 add('history-owns-Governance-decisions',lambda m:m['predicates']['OwnsGovernanceDecisions'].append(['h1']),T=False)
 for n in ['CalculatedSnapshotRole','CalculatedViewRole']:add('derived-surface-without-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 add('derived-surface-competes-as-replay-source',lambda m:m['predicates']['CompetingReplaySource'].append(['d1']),T=False)
 for n in b.INFER_FLAGS:add('forbidden-inference-'+n,lambda m,n=n:m['predicates'][n].append(['h1']),T=False)
 for n in b.ROLES:add('forbidden-sibling-collapse-'+n,lambda m,n=n:m['predicates'][n].append(['h1']),T=False)
 add('consumer-without-role',lambda m:m['predicates']['ConsumerRole'].clear(),T=False)
 add('consumer-outside-applicability',lambda m:m['predicates']['UseInApplicability'].clear(),T=False)
 add('empty-history-permitted',lambda m:None,I=True)
 add('canonical-markers-do-not-enforce-unique-history-for-subject',lambda m:None,I=True)
 add('missing-predecessor-links-permitted',lambda m:m['predicates']['PredecessorLink'].clear(),I=True)
 add('same-cursor-token-for-ordered-entries-permitted',lambda m:setfn(m,'eventCursor',['e2'],'cursor1'),I=True)
 add('opaque-nonnumeric-cursor-token-permitted',lambda m:setfn(m,'eventCursor',['e1'],'*'),I=True)
 add('opaque-matching-digest-token-permitted',lambda m:(setfn(m,'eventDigest',['e1'],'other'),setfn(m,'previousDigest',['e2'],'other')),I=True)
 add('head-previous-digest-unconstrained-without-link',lambda m:setfn(m,'previousDigest',['e1'],'other'),I=True)
 add('declared-predecessor-may-be-nonimmediate',lambda m:(third_entry(m),m['predicates']['PredecessorLink'].append(['h2','e3','e1'])),I=True)
 add('derived-snapshot-and-view-roles-may-overlap',lambda m:None,I=True)
 add('noncompeting-derived-surface-actual-use-independent',lambda m:m['predicates']['ActualReplayUsed'].append(['d1']))
 add('retention-requirement-does-not-force-successor-membership',lambda m:(m['predicates']['Contains'].remove(['h2','e1']),m['predicates']['Before'].clear(),m['predicates']['PredecessorLink'].clear()))
 add('raw-index-can-contain-entry-without-history-genus',lambda m:m['predicates']['Contains'].append(['raw','e1']),I=True)
 add('nontotal-state-function',lambda m:m['functions']['resultingSemanticState'].pop(),error='nontotal-function')
 add('ill-sorted-subject-function',lambda m:setfn(m,'historySubject',['h1'],'cursor1'),error='ill-sorted-function-result')
 add('ill-sorted-empty-constant',lambda m:m['constants'].update(EMPTY='absent'),error='ill-sorted-constant')
 add('wrong-order-arity',lambda m:m['predicates'].update(Before=[['h2','e1']]),error='ill-sorted-model-tuple')
 add('duplicate-entry-tuple',lambda m:m['predicates']['Contains'].append(['h1','e1']),error='duplicate-predicate-tuple')
 add('empty-entity-domain',lambda m:m['domains'].update(Entity=[]),error='empty-or-malformed-domain')
 add('duplicate-subject-function-tuple',lambda m:m['functions']['historySubject'].append(copy.deepcopy(m['functions']['historySubject'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.governance-event-history/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-SemanticEventHistory-model-controls/v1-candidate','status':'PASS-for-exact-authored-SemanticEventHistory-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent per-subject complete-state,strict-order and declared digest-link constraints with normative retention and noncompeting derived surfaces. Actual state/hash/cursor/storage/replay/owner maps pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
