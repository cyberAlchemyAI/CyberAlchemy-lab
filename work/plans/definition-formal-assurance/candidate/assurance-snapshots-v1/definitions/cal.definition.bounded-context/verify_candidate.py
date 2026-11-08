"""Independent bounded context identity, map ownership, dependency and reverse index controls."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def base_model():
 entities=['c1','c2','c3','model1','model2','lang1','lang2','owner','challenge','map1','rel1','kind1','reg1','reg2','index1','index2','index3','aux','other']
 domains={'Entity':entities,'Token':['empty','id1','id2','version1','version2','scope','exclusions','contracts','lifecycle','evidence','opaque']}
 defaults={'contextModel':'model1','contextLanguage':'lang1','contextOwner':'owner','contextChallengeRoute':'challenge','relationSourceContext':'c1','relationTargetContext':'c2','relationshipKind':'kind1','indexContext':'c1','indexRegistry':'reg1','contextId':'id1','contextVersion':'version1','contextScope':'scope','contextExclusions':'exclusions','contextContracts':'contracts','contextLifecycle':'lifecycle','contextEvidence':'evidence','modelContextIdentity':'id1','languageContextIdentity':'id1'}
 maps={n:lambda e,value=value:value for n,value in defaults.items()}
 maps.update(contextModel=lambda e:'model2' if e=='c2' else 'model1',contextLanguage=lambda e:'lang2' if e=='c2' else 'lang1',contextId=lambda e:'id2' if e=='c2' else 'id1',contextVersion=lambda e:'version2' if e=='c3' else 'version1',modelContextIdentity=lambda e:'id2' if e=='model2' else 'id1',languageContextIdentity=lambda e:'id2' if e=='lang2' else 'id1',indexRegistry=lambda e:'reg2' if e=='index2' else 'reg1')
 f={n:[{'args':[e],'value':fn(e)} for e in entities] for n,fn in maps.items()}
 p={n:[] for n in b.SIGNATURE};p.update(BoundedContext=[['c1'],['c2'],['c3']],DomainModelRole=[['model1'],['model2']],LanguageRole=[['lang1'],['lang2']],OwnerRole=[['owner']],ChallengeRouteRole=[['challenge']],ContextMapRole=[['map1']],TypedRelationshipRole=[['rel1']],RelationshipKindRole=[['kind1']],MapRegistryRole=[['reg1'],['reg2']],ReverseIndexRole=[['index1'],['index2'],['index3']],DerivedProjection=[['index1'],['index2'],['index3']],MapOwnsEndpointMembership=[['map1']],MapOwnsRelationshipDirection=[['map1']],CanonicalEndpoint=[['map1','c1'],['map1','c2']],MapMember=[['map1','c1'],['map1','c2']],RelationInMap=[['map1','rel1']],CrossContextDependency=[['c1','c2']],MapInRegistry=[['reg1','map1']],IndexForContext=[['index1','c1'],['index2','c1'],['index3','c1']],LookupMembership=[['index1','map1'],['index3','map1']],RecomputedIndex=[['index1','index3']],SharedSpelling=[['c1','c2']],ContainsContext=[['c1','c3']],ImportsContext=[['c1','c3']])
 for n in b.QUALIFIERS:p[n]=[['c1'],['c2'],['c3']]
 return {'domains':domains,'constants':{'EMPTY':'empty'},'functions':f,'predicates':p}
def setfn(m,n,args,value):next(x for x in m['functions'][n] if x['args']==args)['value']=value
def controls():
 rows=[]
 def add(id,change,T=True,I=None,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('explicit-contexts-map-dependency-and-relative-reverse-index',lambda m:None,I=True)
 for n in b.OUTCOMES:add('independent-actual-outcome-'+n,lambda m,n=n:m['predicates'][n].append(['c1']))
 for n in b.QUALIFIERS:add('missing-genus-'+n,lambda m,n=n:m['predicates'][n].remove(['c1']),T=False)
 add('reverse-genus-missing-context',lambda m:m['predicates']['BoundedContext'].remove(['c1']),T=False)
 for n in ['contextId','contextVersion','contextScope','contextExclusions','contextContracts','contextLifecycle','contextEvidence']:add('empty-'+n,lambda m,n=n:setfn(m,n,['c1'],'empty'),T=False)
 for n in ['DomainModelRole','LanguageRole','OwnerRole','ChallengeRouteRole']:add('missing-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 for n,e in [('modelContextIdentity','model1'),('languageContextIdentity','lang1')]:add('wrong-context-identity-'+n,lambda m,n=n,e=e:setfn(m,n,[e],'id2'),T=False)
 add('context-is-its-language',lambda m:(setfn(m,'contextLanguage',['c1'],'c1'),m['predicates']['LanguageRole'].append(['c1'])),T=False)
 add('duplicate-identity-version-key',lambda m:setfn(m,'contextVersion',['c3'],'version1'),T=False)
 add('same-identity-distinct-version-allowed',lambda m:None,I=True)
 for n in b.FORBIDDEN+['ContextOwnsMapMembership','ContextOwnsRelationshipDirection']:add('forbidden-context-role-'+n,lambda m,n=n:m['predicates'][n].append(['c1']),T=False)
 add('context-canonical-map-backreference',lambda m:m['predicates']['CanonicalContextBackreference'].append(['c1','map1']),T=False)
 for n in ['MapOwnsEndpointMembership','MapOwnsRelationshipDirection']:add('missing-map-owner-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 add('endpoint-not-context',lambda m:(m['predicates']['CanonicalEndpoint'].append(['map1','aux']),m['predicates']['MapMember'].append(['map1','aux'])),T=False)
 add('canonical-endpoint-without-member',lambda m:m['predicates']['MapMember'].remove(['map1','c1']),T=False)
 add('map-member-without-endpoint',lambda m:m['predicates']['MapMember'].append(['map1','c3']),T=False)
 for n in ['ContextMapRole','TypedRelationshipRole','RelationshipKindRole']:add('missing-typed-relation-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 for n in ['relationSourceContext','relationTargetContext']:add('noncontext-relation-'+n,lambda m,n=n:setfn(m,n,['rel1'],'aux'),T=False)
 add('typed-relation-missing-exact-endpoint-version',lambda m:setfn(m,'relationTargetContext',['rel1'],'c3'),T=False)
 add('dependency-without-typed-relation',lambda m:m['predicates']['RelationInMap'].clear(),T=False)
 add('reverse-dependency-without-reverse-relationship',lambda m:m['predicates']['CrossContextDependency'].append(['c2','c1']),T=False)
 add('self-cross-context-dependency',lambda m:m['predicates']['CrossContextDependency'].append(['c1','c1']),T=False)
 add('dependency-to-noncontext',lambda m:m['predicates']['CrossContextDependency'].append(['c1','aux']),T=False)
 for n in ['ReverseIndexRole','DerivedProjection','MapRegistryRole']:add('missing-index-role-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 for n in ['IndependentCanonicalOwner','IndexOmissionAmendsMap']:add('index-claims-canonical-effect-'+n,lambda m,n=n:m['predicates'][n].append(['index2']),T=False)
 add('index-context-does-not-match-selected-context',lambda m:setfn(m,'indexContext',['index1'],'c2'),T=False)
 add('index-is-context',lambda m:(m['predicates']['IndexForContext'].append(['c1','c1']),m['predicates']['ReverseIndexRole'].append(['c1']),m['predicates']['DerivedProjection'].append(['c1']),m['predicates']['LookupMembership'].append(['c1','map1'])),T=False)
 add('index-omits-map-in-selected-registry',lambda m:m['predicates']['LookupMembership'].remove(['index1','map1']),T=False)
 add('index-includes-map-outside-selected-registry',lambda m:m['predicates']['LookupMembership'].append(['index2','map1']),T=False)
 add('index-includes-nonmember-map',lambda m:m['predicates']['LookupMembership'].append(['index1','other']),T=False)
 add('recomputed-index-with-distinct-registry',lambda m:m['predicates']['RecomputedIndex'].append(['index1','index2']),T=False)
 add('recomputed-index-with-distinct-context',lambda m:setfn(m,'indexContext',['index3'],'c2'),T=False)
 add('recomputed-index-without-index-context-record',lambda m:m['predicates']['IndexForContext'].remove(['index3','c1']),T=False)
 for n in b.INFER_FLAGS:add('forbidden-inference-'+n,lambda m,n=n:m['predicates'][n].append(['c1']),T=False)
 add('actual-consistency-not-forced-by-intent',lambda m:None,I=True)
 add('projection-absence-does-not-amend-canonical-member',lambda m:None,I=True)
 add('shared-spelling-does-not-assert-shared-meaning',lambda m:None,I=True)
 add('explicit-shared-meaning-permitted-separately',lambda m:m['predicates']['SharedMeaning'].append(['c1','c2']),I=False)
 add('opaque-context-version-token-allowed',lambda m:setfn(m,'contextVersion',['c1'],'opaque'),I=True)
 add('opaque-scope-lifecycle-contract-evidence-tokens-allowed',lambda m:[setfn(m,n,['c1'],'opaque') for n in ['contextScope','contextExclusions','contextContracts','contextLifecycle','contextEvidence']],I=True)
 add('no-dependencies-required-by-theory',lambda m:m['predicates']['CrossContextDependency'].clear(),I=False)
 add('no-recompute-required-by-theory',lambda m:m['predicates']['RecomputedIndex'].clear(),I=False)
 add('no-spelling-pairs-required-by-theory',lambda m:m['predicates']['SharedSpelling'].clear(),I=False)
 add('no-containment-required-by-theory',lambda m:m['predicates']['ContainsContext'].clear(),I=False)
 add('no-imports-required-by-theory',lambda m:m['predicates']['ImportsContext'].clear(),I=False)
 add('nontotal-context-model-function',lambda m:m['functions']['contextModel'].pop(),error='nontotal-function')
 add('ill-sorted-context-id-result',lambda m:setfn(m,'contextId',['c1'],'c1'),error='ill-sorted-function-result')
 add('ill-sorted-empty-constant',lambda m:m['constants'].update(EMPTY='absent'),error='ill-sorted-constant')
 add('wrong-map-membership-arity',lambda m:m['predicates'].update(MapMember=[['map1']]),error='ill-sorted-model-tuple')
 add('duplicate-context-tuple',lambda m:m['predicates']['BoundedContext'].append(['c1']),error='duplicate-predicate-tuple')
 add('empty-entity-domain',lambda m:m['domains'].update(Entity=[]),error='empty-or-malformed-domain')
 add('duplicate-context-function-tuple',lambda m:m['functions']['contextModel'].append(copy.deepcopy(m['functions']['contextModel'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.ubiquitous-language/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-BoundedContext-model-controls/v1-candidate','status':'PASS-for-exact-authored-BoundedContext-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent typed context revisions,map-owned exact endpoints,directed typed dependencies and selected-registry reverse projections. Actual consistency,coverage,owner and consumer/source-owner maps pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
