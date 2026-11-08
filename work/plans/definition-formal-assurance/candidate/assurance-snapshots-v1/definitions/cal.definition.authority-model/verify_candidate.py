"""Independent finite Model routing/necessity controls, without assumed approval."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def base_model():
 domains={'Entity':['m1','m2','c1','c2','v1','v2','s1','s2'],'State':['before','after'],'Token':['empty','kind','posture','route1','route2','allowed','blocked','gate1','gate2','validation','rules']}
 functions={}
 for n in b.FIELDS:
  functions[n+'Value']=[{'args':[m,x],'value':('route2' if m=='m2' else 'route1') if n=='ownerRoute' else ('gate2' if m=='m2' else 'gate1') if n=='gate' else {'kind':'kind','posture':'posture','allowedUse':'allowed','blockedUse':'blocked','validationSurface':'validation','nonCollapseRules':'rules'}[n]} for m,x in itertools.product(domains['Entity'],repeat=2)]
 p={n:[] for n in b.SIGNATURE};p.update(AuthorityModel=[['m1'],['m2']],GovernedStructure=[['m1'],['m2']],Candidate=[['c1'],['c2']],Movement=[['v1'],['v2']],AuthoritySurface=[['s1'],['s2']],NamesPostures=[['m1'],['m2']],NamesGates=[['m1'],['m2']],NamesLayerBoundaries=[['m1'],['m2']],MappedCandidate=[['m1','c1'],['m1','c2'],['m2','c1']],Coordinates=[['m1','s1'],['m2','s2']],DeclaredPromotionKind=[['m1','kind'],['m2','kind']],OwnsPromotionRoute=[['m1','kind','route1'],['m2','kind','route2']],MovementContext=[['m1','c1','v1'],['m1','c2','v2']],AdmissibleMovement=[['v1']],CrossesEvidenceOrModelToLocalAuthority=[['v1']],RequiresPromotionGate=[['v1']],RecordedGateVerdict=[['v1','route1','gate1'],['v2','route1','gate1']],AllowedUseCovers=[['v1','allowed'],['v2','allowed']])
 return {'domains':domains,'constants':{'EMPTY':'empty'},'functions':functions,'predicates':p}
def setvalue(m,n,args,value):next(x for x in m['functions'][n] if x['args']==args)['value']=value
def controls():
 rows=[]
 def add(id,change,T=True,I=None,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('context-qualified-routing-and-required-gate-without-actual-approval',lambda m:None,I=True)
 for n in b.OUTCOMES:add('independent-world-marker-'+n,lambda m,n=n:m['predicates'][n].append(['m1']),I=True)
 add('recorded-verdict-may-independently-be-positive',lambda m:m['predicates']['PositiveVerdict'].append(['v1']),I=False)
 add('required-gate-may-independently-be-performed',lambda m:m['predicates']['GatePerformed'].append(['v1']),I=False)
 add('actual-promotion-marker-independently-permitted',lambda m:m['predicates']['ActualPromotion'].append(['v1']),I=False)
 for n in b.FIELDS:add('empty-context-qualified-'+n,lambda m,n=n:setvalue(m,n+'Value',['m1','c1'],'empty'),T=False)
 add('Model-not-governed-structure',lambda m:m['predicates']['GovernedStructure'].remove(['m1']),T=False)
 add('mapped-object-not-Candidate',lambda m:m['predicates']['Candidate'].remove(['c1']),T=False)
 for n in ['NamesPostures','NamesGates','NamesLayerBoundaries']:add('missing-'+n,lambda m,n=n:m['predicates'][n].remove(['m1']),T=False)
 add('no-coordinated-typed-surface',lambda m:m['predicates']['Coordinates'].remove(['m1','s1']),T=False)
 add('declared-promotion-kind-without-owner-route',lambda m:m['predicates']['OwnsPromotionRoute'].remove(['m1','kind','route1']),T=False)
 add('empty-promotion-owner-route',lambda m:m['predicates'].update(OwnsPromotionRoute=[['m1','kind','empty'],['m2','kind','route2']]),T=False)
 add('admissible-missing-recorded-verdict',lambda m:m['predicates']['RecordedGateVerdict'].remove(['v1','route1','gate1']),T=False)
 add('admissible-missing-use-coverage',lambda m:m['predicates']['AllowedUseCovers'].remove(['v1','allowed']),T=False)
 add('verdict-wrong-model-owner-route',lambda m:m['predicates'].update(RecordedGateVerdict=[['v1','route2','gate1'],['v2','route1','gate1']]),T=False)
 add('verdict-wrong-model-gate',lambda m:m['predicates'].update(RecordedGateVerdict=[['v1','route1','gate2'],['v2','route1','gate1']]),T=False)
 add('coverage-wrong-allowed-use',lambda m:m['predicates'].update(AllowedUseCovers=[['v1','blocked'],['v2','allowed']]),T=False)
 add('crossing-without-required-promotion-gate',lambda m:m['predicates'].update(RequiresPromotionGate=[]),T=False)
 add('necessary-conditions-do-not-force-admissibility',lambda m:m['predicates'].update(AdmissibleMovement=[]),I=False)
 add('same-candidate-can-have-one-route-as-alternative-model',lambda m:setvalue(m,'ownerRouteValue',['m2','c1'],'route1'),I=False)
 add('undeclared-kind-obligation-vacuous-with-rich-route-witness-failing',lambda m:m['predicates'].update(DeclaredPromotionKind=[]),I=False)
 def no_models(m):m['predicates'].update(AuthorityModel=[])
 add('no-Model-vacuous-theory-fails-required-witnesses',no_models,I=False)
 add('unmapped-context-not-universal-world-rule',lambda m:m['predicates']['AdmissibleMovement'].append(['s2']),I=True)
 add('unmapped-crossing-not-universal-world-rule',lambda m:m['predicates']['CrossesEvidenceOrModelToLocalAuthority'].append(['s2']),I=True)
 add('nontotal-routing-function',lambda m:m['functions']['kindValue'].pop(),error='nontotal-function')
 add('ill-sorted-routing-result',lambda m:setvalue(m,'kindValue',['m1','c1'],'m1'),error='ill-sorted-function-result')
 add('ill-sorted-empty-sentinel',lambda m:m['constants'].update(EMPTY='absent'),error='ill-sorted-constant')
 add('wrong-context-relation-arity',lambda m:m['predicates'].update(MovementContext=[['m1','c1']]),error='ill-sorted-model-tuple')
 add('duplicate-context-tuple',lambda m:m['predicates']['MappedCandidate'].append(['m1','c1']),error='duplicate-predicate-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.authority-boundary/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-AuthorityModel-model-controls/v1-candidate','status':'PASS-for-exact-authored-AuthorityModel-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent supplied Model context-qualified routing/naming and necessary movement/promotion-gate models. Actual positive verdict, sufficient approval, executed gate, exact tuple, noncollapse, complete route enumeration and owner fidelity remain unresolved.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
