"""Independent models for exclusive edge modes,represented-subject endpoints and source authority separation."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def base_model():
 entities=['h1','h2','n1','n2','s1','s2','r1','o1','i1','u1','raw','other'];edges=['h1','h2'];domains={'Entity':entities,'Token':['empty','projected-id','local-id','relation-digest','meaning','other','*']}
 maps={'edgeOntology':lambda e:'o1','nodeOntology':lambda e:'o1','sourceNode':lambda e:'n1','targetNode':lambda e:'n2','nodeSubject':lambda e:'s2' if e=='n2' else 's1','boundRelation':lambda e:'r1','relationSourceSubject':lambda e:'s1','relationTargetSubject':lambda e:'s2','localInterpretation':lambda e:'i1','interpretationOntology':lambda e:'o1','edgeIdentity':lambda e:'local-id' if e=='h2' else 'projected-id','edgeRelationDigest':lambda e:'relation-digest','relationDigest':lambda e:'relation-digest','interpretationMeaning':lambda e:'meaning'}
 functions={n:[{'args':[e],'value':fn(e)} for e in entities] for n,fn in maps.items()};p={n:[] for n in b.SIGNATURE}
 p.update(OntologyEdge=[[e] for e in edges],GlobalProjection=[['h1']],OntologyLocalInterpretation=[['h2']],GovernedIdentityOrRecord=[[e] for e in edges],BoundedScope=[[e] for e in edges],OntologyRole=[['o1']],NodeRole=[['n1'],['n2']],SubjectRole=[['s1'],['s2']],TypedRelationRole=[['r1']],GlobalRelationRole=[['r1']],InterpretationRole=[['i1']],ConsumerRole=[['u1']],ConsumerUse=[['h1','u1'],['h2','u1']],UseInApplicability=[['h1','u1'],['h2','u1']],CurrentEdge=[['h1']])
 for n in b.QUALIFIERS:p[n]=[[e] for e in edges]
 return {'domains':domains,'constants':{'EMPTY':'empty'},'functions':functions,'predicates':p}
def setfn(m,n,args,value):next(x for x in m['functions'][n] if x['args']==args)['value']=value
def controls():
 rows=[]
 def add(id,change,T=True,I=None,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('independent-global-projected-and-ontology-local-edges',lambda m:None,I=True)
 for n in b.OUTCOMES:add('independent-outcome-'+n,lambda m,n=n:m['predicates'][n].append(['h1']))
 for n in b.QUALIFIERS:add('missing-genus-'+n,lambda m,n=n:m['predicates'][n].remove(['h1']),T=False)
 add('reverse-genus-missing-edge',lambda m:m['predicates']['OntologyEdge'].remove(['h1']),T=False)
 add('both-modes-on-projection',lambda m:m['predicates']['OntologyLocalInterpretation'].append(['h1']),T=False)
 add('both-modes-on-local',lambda m:m['predicates']['GlobalProjection'].append(['h2']),T=False)
 for n,e in [('GlobalProjection','h1'),('OntologyLocalInterpretation','h2')]:add('no-mode-'+e,lambda m,n=n,e=e:m['predicates'][n].clear(),T=False)
 for n in ['GovernedIdentityOrRecord','BoundedScope']:add('missing-'+n,lambda m,n=n:m['predicates'][n].remove(['h1']),T=False)
 add('empty-edge-identity',lambda m:setfn(m,'edgeIdentity',['h1'],'empty'),T=False)
 for n in ['sourceNode','targetNode']:add('edge-is-own-'+n,lambda m,n=n:setfn(m,n,['h1'],'h1'),T=False)
 for n in ['NodeRole','TypedRelationRole']:add('edge-role-collapse-'+n,lambda m,n=n:m['predicates'][n].append(['h1']),T=False)
 add('ontology-without-role',lambda m:m['predicates']['OntologyRole'].clear(),T=False)
 for e in ['n1','n2']:add('endpoint-without-node-role-'+e,lambda m,e=e:m['predicates']['NodeRole'].remove([e]),T=False)
 for e in ['n1','n2']:add('endpoint-ontology-mismatch-'+e,lambda m,e=e:setfn(m,'nodeOntology',[e],'other'),T=False)
 for n in ['TypedRelationRole','GlobalRelationRole']:add('bound-relation-without-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 add('edge-equals-bound-relation',lambda m:setfn(m,'boundRelation',['h1'],'h1'),T=False)
 add('empty-projection-digest',lambda m:setfn(m,'edgeRelationDigest',['h1'],'empty'),T=False)
 add('projection-digest-mismatch',lambda m:setfn(m,'relationDigest',['r1'],'other'),T=False)
 for e in ['s1','s2']:add('represented-subject-without-role-'+e,lambda m,e=e:m['predicates']['SubjectRole'].remove([e]),T=False)
 for n,e in [('relationSourceSubject','s2'),('relationTargetSubject','s1')]:add('projected-endpoint-subject-mismatch-'+n,lambda m,n=n,e=e:setfn(m,n,['r1'],e),T=False)
 add('local-without-interpretation-role',lambda m:m['predicates']['InterpretationRole'].clear(),T=False)
 add('local-interpretation-ontology-mismatch',lambda m:setfn(m,'interpretationOntology',['i1'],'other'),T=False)
 add('local-empty-meaning',lambda m:setfn(m,'interpretationMeaning',['i1'],'empty'),T=False)
 for n in ['OverridesBoundRelation','SecondWritableAuthority']:add('projection-forbidden-'+n,lambda m,n=n:m['predicates'][n].append(['h1']),T=False)
 add('local-as-global-connection',lambda m:m['predicates']['LocalIsGlobalConnection'].append(['h2']),T=False)
 for n in b.INFER_FLAGS:add('forbidden-inference-'+n,lambda m,n=n:m['predicates'][n].append(['h1']),T=False)
 add('consumer-without-role',lambda m:m['predicates']['ConsumerRole'].clear(),T=False)
 add('consumer-outside-applicability',lambda m:m['predicates']['UseInApplicability'].clear(),T=False)
 add('self-loop-not-forbidden',lambda m:(setfn(m,'targetNode',['h1'],'n1'),setfn(m,'relationTargetSubject',['r1'],'s1')),I=True)
 add('equal-identity-tokens-on-distinct-edges-not-forbidden',lambda m:setfn(m,'edgeIdentity',['h2'],'projected-id'),I=True)
 add('opaque-matching-relation-digest-not-cryptographic-proof',lambda m:(setfn(m,'edgeRelationDigest',['h1'],'*'),setfn(m,'relationDigest',['r1'],'*')),I=True)
 add('local-bound-relation-function-uninterpreted',lambda m:setfn(m,'boundRelation',['h2'],'raw'),I=True)
 add('local-global-digest-function-uninterpreted',lambda m:setfn(m,'edgeRelationDigest',['h2'],'empty'),I=True)
 add('projected-local-interpretation-function-uninterpreted',lambda m:setfn(m,'localInterpretation',['h1'],'raw'),I=True)
 add('node-may-share-represented-subject-identity',lambda m:(m['predicates']['SubjectRole'].append(['n1']),setfn(m,'nodeSubject',['n1'],'n1'),setfn(m,'relationSourceSubject',['r1'],'n1')),I=False)
 add('projected-local-is-global-flag-outside-local-guard',lambda m:m['predicates']['LocalIsGlobalConnection'].append(['h1']),I=True)
 add('local-override-flags-outside-projected-guard',lambda m:(m['predicates']['OverridesBoundRelation'].append(['h2']),m['predicates']['SecondWritableAuthority'].append(['h2'])),I=True)
 add('without-selected-consumers-theory-remains',lambda m:(m['predicates']['ConsumerUse'].clear(),m['predicates']['UseInApplicability'].clear()),I=False)
 add('nontotal-node-subject-function',lambda m:m['functions']['nodeSubject'].pop(),error='nontotal-function')
 add('ill-sorted-bound-relation-result',lambda m:setfn(m,'boundRelation',['h1'],'relation-digest'),error='ill-sorted-function-result')
 add('ill-sorted-empty-constant',lambda m:m['constants'].update(EMPTY='absent'),error='ill-sorted-constant')
 add('wrong-consumer-use-arity',lambda m:m['predicates'].update(ConsumerUse=[['h1']]),error='ill-sorted-model-tuple')
 add('duplicate-node-role-tuple',lambda m:m['predicates']['NodeRole'].append(['n1']),error='duplicate-predicate-tuple')
 add('empty-entity-domain',lambda m:m['domains'].update(Entity=[]),error='empty-or-malformed-domain')
 add('duplicate-source-node-function-tuple',lambda m:m['functions']['sourceNode'].append(copy.deepcopy(m['functions']['sourceNode'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.ontology-cut/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-OntologyEdge-model-controls/v1-candidate','status':'PASS-for-exact-authored-OntologyEdge-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent typed projected/local connection,identity,node-to-subject endpoints,declared relation digest and local scope guards. Actual versions,hashes,qualifiers,source writes,scope and owner/runtime maps pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
