"""Independent typed selection/disposition/order/coverage and no-effect finite controls."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def base_model():
 entities=['m1','m2','s1','s2','d1','x1','x2','x3','raw'];maps=['m1','m2'];fields=b.FIELDS+['extra'];domains={'Entity':entities,'Field':fields,'Token':['empty','spec','other','*']}
 functions={'fieldValue':[{'args':[e,f],'value':'spec'} for e,f in itertools.product(entities,fields)],**{n:[{'args':[e],'value':'spec'} for e in entities] for n in ['sourceSelectorValue','sourceDigestValue','destinationIdValue','destinationPathValue']},'dispositionSource':[{'args':[e],'value':'s2' if e=='x2' else 's1'} for e in entities]}
 p={n:[] for n in b.SIGNATURE};items=[['m1',e] for e in ['s1','s2','d1']]
 p.update(ContextMigrationManifest=[[e] for e in maps],DeclaresField=[[e,f] for e,f in itertools.product(maps+['raw'],b.FIELDS)],SourceSelected=[['m1','s1'],['m1','s2']],DispositionPresent=[['m1','x1'],['m1','x2']],DestinationProposed=[['m1','d1']],SelectedItem=copy.deepcopy(items),HasOrderPosition=copy.deepcopy(items),ValidationCovers=copy.deepcopy(items),Before=[['m1','s1','d1']],DependencyEdge=[['m1','s1','d1']],GlobCandidate=[['m1','raw']],SourceSelectionRole=[['s1'],['s2']],SourceSelectorDigestBound=[['s1'],['s2']],DestinationCandidateRole=[['d1']],DestinationIdentityPathExplicit=[['d1']],DispositionRole=[['x1'],['x2']],RollbackBeforeExecutionRequired=[[e] for e in maps],ExclusionsBeforeExecutionRequired=[[e] for e in maps],RawDeclaredComplete=[['raw']])
 for n in b.QUALIFIERS:p[n]=[[e] for e in maps]
 return {'domains':domains,'constants':{'EMPTY':'empty',**{'F_'+n:n for n in b.FIELDS}},'functions':functions,'predicates':p}
def setfield(m,e,f,value):next(x for x in m['functions']['fieldValue'] if x['args']==[e,f])['value']=value
def setfn(m,n,e,value):next(x for x in m['functions'][n] if x['args']==[e])['value']=value
def controls():
 rows=[]
 def add(id,change,T=True,I=None,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('typed-covered-manifest-empty-manifest-and-independent-items',lambda m:None,I=True)
 for n in b.OUTCOMES:add('independent-outcome-'+n,lambda m,n=n:m['predicates'][n].append(['m1']))
 for n in b.QUALIFIERS:add('missing-genus-'+n,lambda m,n=n:m['predicates'][n].remove(['m1']),T=False)
 add('reverse-genus-iff-missing',lambda m:m['predicates']['ContextMigrationManifest'].remove(['m1']),T=False)
 for n in b.FIELDS:add('missing-field-'+n,lambda m,n=n:m['predicates']['DeclaresField'].remove(['m1',n]),T=False)
 for n in ['SourceSelectionRole','SourceSelectorDigestBound']:add('source-missing-'+n,lambda m,n=n:m['predicates'][n].remove(['s1']),T=False)
 for n in ['sourceSelectorValue','sourceDigestValue']:add('source-empty-'+n,lambda m,n=n:setfn(m,n,'s1','empty'),T=False)
 for n in ['DestinationCandidateRole','DestinationIdentityPathExplicit']:add('destination-missing-'+n,lambda m,n=n:m['predicates'][n].remove(['d1']),T=False)
 for n in ['destinationIdValue','destinationPathValue']:add('destination-empty-'+n,lambda m,n=n:setfn(m,n,'d1','empty'),T=False)
 add('source-without-contained-disposition',lambda m:m['predicates']['DispositionPresent'].remove(['m1','x1']),T=False)
 add('contained-disposition-with-unselected-source',lambda m:setfn(m,'dispositionSource','x1','raw'),T=False)
 add('contained-disposition-without-role',lambda m:m['predicates']['DispositionRole'].remove(['x1']),T=False)
 add('selected-source-missing-item',lambda m:m['predicates']['SelectedItem'].remove(['m1','s1']),T=False)
 add('proposed-destination-missing-item',lambda m:m['predicates']['SelectedItem'].remove(['m1','d1']),T=False)
 add('spurious-selected-item',lambda m:m['predicates']['SelectedItem'].append(['m1','raw']),T=False)
 for n in ['HasOrderPosition','ValidationCovers']:add('selected-item-missing-'+n,lambda m,n=n:m['predicates'][n].remove(['m1','d1']),T=False)
 add('reflexive-order',lambda m:m['predicates']['Before'].append(['m1','s1','s1']),T=False)
 add('two-item-order-cycle',lambda m:m['predicates']['Before'].append(['m1','d1','s1']),T=False)
 add('missing-transitive-order',lambda m:m['predicates']['Before'].append(['m1','d1','s2']),T=False)
 add('order-unselected-endpoint',lambda m:m['predicates']['Before'].append(['m1','s1','raw']),T=False)
 add('dependency-without-before',lambda m:m['predicates']['Before'].clear(),T=False)
 add('dependency-unselected-endpoint',lambda m:m['predicates']['DependencyEdge'].append(['m1','s1','raw']),T=False)
 for n in b.NO_FLAGS:add('forbidden-inference-'+n,lambda m,n=n:m['predicates'][n].append(['m1']),T=False)
 for n in ['RollbackBeforeExecutionRequired','ExclusionsBeforeExecutionRequired']:add('missing-normative-'+n,lambda m,n=n:m['predicates'][n].remove(['m1']),T=False)
 for n in ['rollback_boundary','exclusions']:add('empty-pre-execution-'+n,lambda m,n=n:setfield(m,'m1',n,'empty'),T=False)
 for n in b.ROLES:add('forbidden-role-'+n,lambda m,n=n:m['predicates'][n].append(['m1']),T=False)
 add('empty-manifest-permitted-by-generic-candidate',lambda m:None,I=True)
 add('independent-items-need-not-be-comparable',lambda m:None,I=True)
 add('duplicate-disposition-per-source-permitted',lambda m:(m['predicates']['DispositionPresent'].append(['m1','x3']),m['predicates']['DispositionRole'].append(['x3'])),I=True)
 add('glob-looking-literal-selector-without-inference-flag',lambda m:setfn(m,'sourceSelectorValue','s1','*'),I=True)
 add('opaque-digest-token-is-not-byte-verification',lambda m:setfn(m,'sourceDigestValue','s1','other'),I=True)
 for n in ['source_repository','preimages','expected_postimages','owner_gates','residue','lifecycle']:add('declared-empty-opaque-'+n,lambda m,n=n:setfield(m,'m1',n,'empty'),I=True)
 add('field-name-constants-may-alias',lambda m:m['constants'].update(F_id='lifecycle'),I=True)
 add('extra-declared-field-permitted',lambda m:m['predicates']['DeclaresField'].append(['m1','extra']),I=True)
 add('nontotal-selector-function',lambda m:m['functions']['sourceSelectorValue'].pop(),error='nontotal-function')
 add('ill-sorted-disposition-source',lambda m:setfn(m,'dispositionSource','x1','spec'),error='ill-sorted-function-result')
 add('ill-sorted-field-constant',lambda m:m['constants'].update(F_id='absent'),error='ill-sorted-constant')
 add('wrong-before-arity',lambda m:m['predicates'].update(Before=[['m1','s1']]),error='ill-sorted-model-tuple')
 add('duplicate-selection-tuple',lambda m:m['predicates']['SourceSelected'].append(['m1','s1']),error='duplicate-predicate-tuple')
 add('empty-entity-domain',lambda m:m['domains'].update(Entity=[]),error='empty-or-malformed-domain')
 add('duplicate-selector-function-tuple',lambda m:m['functions']['sourceSelectorValue'].append(copy.deepcopy(m['functions']['sourceSelectorValue'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.context-map/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-ContextMigrationManifest-model-controls/v1-candidate','status':'PASS-for-exact-authored-ContextMigrationManifest-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent supplied selection/disposition/coverage and strict partial-order structures with no inferred migration authority. Actual value/hash/immutable-epoch/gate/execution semantics pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
