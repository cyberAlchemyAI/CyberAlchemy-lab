"""Independent supplied models for typed dual-coordinate cuts,copy/rebuild and noncanonical boundaries."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def base_model():
 entities=['h1','h2','h3','o1','other','n1','e1','se1','ge1','u1','raw'];cuts=['h1','h2','h3'];domains={'Entity':entities,'Token':['empty','semantic','governance','events','state','other','*']}
 maps={'cutOntology':lambda e:'o1','stateOntology':lambda e:'o1','eventOntology':lambda e:'o1','resultingState':lambda e:'n1','semanticCursor':lambda e:'semantic','governanceCursor':lambda e:'governance','eventSetDigest':lambda e:'events','stateDigest':lambda e:'state','eventSemanticCursor':lambda e:'semantic','eventGovernanceCursor':lambda e:'governance'}
 functions={n:[{'args':[e],'value':fn(e)} for e in entities] for n,fn in maps.items()}
 p={n:[] for n in b.SIGNATURE};p.update(OntologyCut=[[e] for e in cuts],GovernedIdentityOrRecord=[[e] for e in cuts],BoundedScope=[[e] for e in cuts],RebuildRequired=[[e] for e in cuts],OntologyRole=[['o1']],StateRole=[['n1'],['e1']],NodeStateRole=[['n1']],EdgeStateRole=[['e1']],SemanticEventRole=[['se1']],GovernanceEventRole=[['ge1']],SelectedState=[[h,s] for h in ['h1','h2'] for s in ['n1','e1']],SelectedSemanticEvent=[[h,'se1'] for h in ['h1','h2']],SelectedGovernanceEvent=[[h,'ge1'] for h in ['h1','h2']],CompatiblePositions=[['o1','semantic','governance']],ImmutableCopy=[['h1','h2']],RebuiltFrom=[['h2','h1']],ConsumerRole=[['u1']],ConsumerUse=[['h1','u1']],UseInApplicability=[['h1','u1']],CurrentCut=[['h1']])
 for n in b.QUALIFIERS:p[n]=[[e] for e in cuts]
 return {'domains':domains,'constants':{'EMPTY':'empty'},'functions':functions,'predicates':p}
def setfn(m,n,args,value):next(x for x in m['functions'][n] if x['args']==args)['value']=value
def controls():
 rows=[]
 def add(id,change,T=True,I=None,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('typed-derived-cut-dual-coordinates-copy-rebuild-and-noncanonical-boundary',lambda m:None,I=True)
 for n in b.OUTCOMES:add('independent-actual-outcome-'+n,lambda m,n=n:m['predicates'][n].append(['h1']))
 for n in b.QUALIFIERS:add('missing-cut-genus-'+n,lambda m,n=n:m['predicates'][n].remove(['h1']),T=False)
 add('reverse-genus-missing-cut',lambda m:m['predicates']['OntologyCut'].remove(['h1']),T=False)
 for n in ['GovernedIdentityOrRecord','BoundedScope','RebuildRequired']:add('missing-'+n,lambda m,n=n:m['predicates'][n].remove(['h1']),T=False)
 add('ontology-without-role',lambda m:m['predicates']['OntologyRole'].clear(),T=False)
 for n in ['semanticCursor','governanceCursor','eventSetDigest','stateDigest']:add('empty-'+n,lambda m,n=n:setfn(m,n,['h1'],'empty'),T=False)
 add('cut-incompatible-dual-position',lambda m:m['predicates']['CompatiblePositions'].clear(),T=False)
 add('state-without-role',lambda m:m['predicates']['StateRole'].remove(['n1']),T=False)
 add('state-without-node-or-edge-role',lambda m:m['predicates']['NodeStateRole'].clear(),T=False)
 add('state-ontology-mismatch',lambda m:setfn(m,'stateOntology',['n1'],'other'),T=False)
 for n,e in [('SemanticEventRole','se1'),('GovernanceEventRole','ge1')]:add('event-without-'+n,lambda m,n=n,e=e:m['predicates'][n].clear(),T=False)
 for e in ['se1','ge1']:add('event-ontology-mismatch-'+e,lambda m,e=e:setfn(m,'eventOntology',[e],'other'),T=False)
 add('semantic-event-result-not-selected-state',lambda m:setfn(m,'resultingState',['se1'],'raw'),T=False)
 add('semantic-event-incompatible-position',lambda m:setfn(m,'eventSemanticCursor',['se1'],'other'),T=False)
 add('governance-event-incompatible-semantic-position',lambda m:setfn(m,'eventSemanticCursor',['ge1'],'other'),T=False)
 add('governance-event-incompatible-governance-position',lambda m:setfn(m,'eventGovernanceCursor',['ge1'],'other'),T=False)
 add('immutable-copy-not-cut',lambda m:m['predicates']['ImmutableCopy'].append(['h1','raw']),T=False)
 add('rebuilt-result-not-cut',lambda m:m['predicates']['RebuiltFrom'].append(['raw','h1']),T=False)
 for n in ['cutOntology','semanticCursor','governanceCursor','eventSetDigest','stateDigest']:add('copy-or-rebuild-changes-'+n,lambda m,n=n:setfn(m,n,['h2'],'other'),T=False)
 for n,e in [('SelectedState','e1'),('SelectedSemanticEvent','se1'),('SelectedGovernanceEvent','ge1')]:add('copy-or-rebuild-changes-'+n,lambda m,n=n,e=e:m['predicates'][n].remove(['h2',e]),T=False)
 for n in ['CanonicalReplaySource','SilentIncompatibleMixing']:add('forbidden-'+n,lambda m,n=n:m['predicates'][n].append(['h1']),T=False)
 for n in b.INFER_FLAGS:add('forbidden-inference-'+n,lambda m,n=n:m['predicates'][n].append(['h1']),T=False)
 add('consumer-without-role',lambda m:m['predicates']['ConsumerRole'].clear(),T=False)
 add('use-outside-applicability',lambda m:m['predicates']['UseInApplicability'].clear(),T=False)
 add('empty-cut-permitted',lambda m:None,I=True)
 add('equal-coordinates-and-content-do-not-force-identity-equality',lambda m:None,I=True)
 add('node-and-edge-state-roles-may-overlap',lambda m:m['predicates']['EdgeStateRole'].append(['n1']),I=True)
 add('unselected-state-may-be-untyped',lambda m:None,I=True)
 add('selected-governance-event-result-state-not-constrained',lambda m:setfn(m,'resultingState',['ge1'],'raw'),I=True)
 add('one-event-can-have-both-kinds',lambda m:(m['predicates']['GovernanceEventRole'].append(['se1']),*[m['predicates']['SelectedGovernanceEvent'].append([h,'se1']) for h in ['h1','h2']]),I=True)
 add('opaque-cursors-and-digest-tokens-permitted',lambda m:None,I=True)
 add('explicit-copy-or-rebuild-availability-not-required',lambda m:(m['predicates']['ImmutableCopy'].clear(),m['predicates']['RebuiltFrom'].clear()),I=False)
 add('no-semantic-events-required-for-cut-genus',lambda m:m['predicates']['SelectedSemanticEvent'].clear(),I=False)
 add('no-governance-events-required-for-cut-genus',lambda m:m['predicates']['SelectedGovernanceEvent'].clear(),I=False)
 add('same-state-and-event-digest-token-permitted',lambda m:[setfn(m,'stateDigest',[h],'events') for h in ['h1','h2','h3']],I=True)
 add('same-semantic-and-governance-cursor-token-permitted',lambda m:([setfn(m,'governanceCursor',[h],'semantic') for h in ['h1','h2','h3']],setfn(m,'eventGovernanceCursor',['ge1'],'semantic'),m['predicates'].update(CompatiblePositions=[['o1','semantic','semantic']])),I=True)
 add('nontotal-cursor-function',lambda m:m['functions']['semanticCursor'].pop(),error='nontotal-function')
 add('ill-sorted-cut-ontology-function',lambda m:setfn(m,'cutOntology',['h1'],'semantic'),error='ill-sorted-function-result')
 add('ill-sorted-empty-constant',lambda m:m['constants'].update(EMPTY='absent'),error='ill-sorted-constant')
 add('wrong-compatibility-arity',lambda m:m['predicates'].update(CompatiblePositions=[['o1','semantic']]),error='ill-sorted-model-tuple')
 add('duplicate-state-tuple',lambda m:m['predicates']['SelectedState'].append(['h1','n1']),error='duplicate-predicate-tuple')
 add('empty-entity-domain',lambda m:m['domains'].update(Entity=[]),error='empty-or-malformed-domain')
 add('duplicate-ontology-function-tuple',lambda m:m['functions']['cutOntology'].append(copy.deepcopy(m['functions']['cutOntology'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.ontology/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-OntologyCut-model-controls/v1-candidate','status':'PASS-for-exact-authored-OntologyCut-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent typed cut coordinates,state/event roles,compatibility,immutable-copy/rebuild and noncanonical guards. Actual dual-cursor/hash/join/replay/owner maps pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
