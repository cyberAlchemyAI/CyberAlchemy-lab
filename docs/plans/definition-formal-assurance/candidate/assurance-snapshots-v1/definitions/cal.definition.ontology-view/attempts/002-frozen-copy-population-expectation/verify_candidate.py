"""Independent finite exact-cut projection,item,immutable-copy,expiry and authority models."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def base_model():
 entities=['v1','v2','v3','o1','cut1','sel1','con1','con2','n1','e1','s1','r1','a1','other'];views=['v1','v2','v3'];domains={'Entity':entities,'Token':['empty','sem','gov','digest','purpose','exclusions','fresh','expiry','past','ceiling','content','source','other','*']}
 values={'viewOntology':'o1','viewCut':'cut1','viewSelectionContract':'sel1','cutOntology':'o1','itemCut':'cut1','itemSelectionContract':'sel1','viewSemanticCursor':'sem','cutSemanticCursor':'sem','viewGovernanceCursor':'gov','cutGovernanceCursor':'gov','viewEventSetDigest':'digest','cutEventSetDigest':'digest','viewPurpose':'purpose','viewExclusions':'exclusions','viewFreshness':'fresh','viewClaimCeiling':'ceiling','viewContent':'content','itemSourceDigest':'source'}
 maps={n:lambda e,value=value:value for n,value in values.items()};maps.update(viewConsumer=lambda e:'con2' if e=='v3' else 'con1',viewExpiry=lambda e:'past' if e=='v3' else 'expiry',representedCanonical=lambda e:'r1' if e=='e1' else 's1');functions={n:[{'args':[e],'value':f(e)} for e in entities] for n,f in maps.items()};p={n:[] for n in b.SIGNATURE}
 p.update(OntologyView=[[e] for e in views],GovernedIdentityOrRecord=[[e] for e in views],BoundedScope=[[e] for e in views],DerivedProjectStateRole=[[e] for e in views],OntologyRole=[['o1']],CutRole=[['cut1']],ConsistentCutRole=[['cut1']],SelectionContractRole=[['sel1']],NamedConsumerRole=[['con1']],AgentSessionRole=[['con2']],NodeRole=[['n1']],EdgeRole=[['e1']],SubjectRole=[['s1']],CanonicalRelationRole=[['r1']],ActionRole=[['a1']],SelectedNode=[[h,'n1'] for h in views],SelectedEdge=[[h,'e1'] for h in views],CutMember=[['cut1','n1'],['cut1','e1']],SelectorPermits=[['sel1','n1'],['sel1','e1']],FrozenCopy=[['v1','v2']],RecomputedView=[['v1','v2']],Expired=[['v3']],Stale=[['v3']],CurrentView=[['v1']],CurrentStateAction=[['v1','a1'],['v3','a1']],ViewUsableForAction=[['v1','a1']])
 for n in b.QUALIFIERS:p[n]=[[e] for e in views]
 return {'domains':domains,'constants':{'EMPTY':'empty'},'functions':functions,'predicates':p}
def setfn(m,n,args,value):next(x for x in m['functions'][n] if x['args']==args)['value']=value
def controls():
 rows=[]
 def add(id,change,T=True,I=None,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('exact-cut-purpose-view-with-frozen-recompute-and-expired-current-use',lambda m:None,I=True)
 for n in b.OUTCOMES:add('independent-actual-outcome-'+n,lambda m,n=n:m['predicates'][n].append(['v1']))
 for n in b.QUALIFIERS:add('missing-genus-'+n,lambda m,n=n:m['predicates'][n].remove(['v1']),T=False)
 add('reverse-genus-missing-View',lambda m:m['predicates']['OntologyView'].remove(['v1']),T=False)
 for n in ['GovernedIdentityOrRecord','BoundedScope','DerivedProjectStateRole','OntologyRole','CutRole','ConsistentCutRole','SelectionContractRole']:add('missing-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 for n in ['NamedConsumerRole','AgentSessionRole']:add('missing-consumer-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 for field in b.VIEW_FIELDS:
  if field in b.TOKEN_FUNCTIONS:add('empty-required-'+field,lambda m,field=field:setfn(m,field,['v1'],'empty'),T=False)
 for field in ['viewOntology','viewSemanticCursor','viewGovernanceCursor','viewEventSetDigest']:add('View-cut-coordinate-mismatch-'+field,lambda m,field=field:setfn(m,field,['v1'],'other'),T=False)
 for field in b.VIEW_FIELDS:add('frozen-copy-changes-'+field,lambda m,field=field:setfn(m,field,['v2'],'other'),T=False)
 for rel,item in [('SelectedNode','n1'),('SelectedEdge','e1')]:add('frozen-copy-changes-'+rel,lambda m,rel=rel,item=item:m['predicates'][rel].remove(['v2',item]),T=False)
 add('frozen-copy-is-not-a-View',lambda m:m['predicates']['FrozenCopy'].append(['v1','other']),T=False)
 for n in b.CANONICAL_ROLES:add('forbidden-canonical-role-'+n,lambda m,n=n:m['predicates'][n].append(['v1']),T=False)
 add('View-is-its-cut',lambda m:setfn(m,'viewCut',['v1'],'v1'),T=False)
 for n in ['NodeRole','EdgeRole','SubjectRole','CanonicalRelationRole']:add('missing-selected-item-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 for item in ['n1','e1']:
  for field in ['itemCut','itemSelectionContract']:add('selected-item-binding-mismatch-'+item+'-'+field,lambda m,item=item,field=field:setfn(m,field,[item],'other'),T=False)
  add('selected-item-empty-source-digest-'+item,lambda m,item=item:setfn(m,'itemSourceDigest',[item],'empty'),T=False)
  add('selected-item-not-in-cut-'+item,lambda m,item=item:m['predicates']['CutMember'].remove(['cut1',item]),T=False)
  add('selected-item-not-permitted-by-selector-'+item,lambda m,item=item:m['predicates']['SelectorPermits'].remove(['sel1',item]),T=False)
  add('selected-item-is-canonical-source-'+item,lambda m,item=item:(setfn(m,'representedCanonical',[item],item),m['predicates']['SubjectRole' if item=='n1' else 'CanonicalRelationRole'].append([item])),T=False)
  for n in ['ReplacesCanonicalIdentity','ReplacesCanonicalAuthority']:add('selected-item-'+item+'-'+n,lambda m,item=item,n=n:m['predicates'][n].append([item]),T=False)
 add('View-is-selected-canonical-subject',lambda m:(setfn(m,'representedCanonical',['n1'],'v1'),m['predicates']['SubjectRole'].append(['v1'])),T=False)
 for n in b.WIDEN_FLAGS:add('View-'+n,lambda m,n=n:m['predicates'][n].append(['v1']),T=False)
 add('View-authorizes-an-Action',lambda m:m['predicates']['ViewAuthorizesAction'].append(['v1','a1']),T=False)
 add('expired-current-state-use-allowed',lambda m:m['predicates']['ViewUsableForAction'].append(['v3','a1']),T=False)
 add('stale-only-current-state-use-allowed',lambda m:(m['predicates']['Expired'].clear(),m['predicates']['ViewUsableForAction'].append(['v3','a1'])),T=False)
 add('current-action-without-Action-role',lambda m:m['predicates']['ActionRole'].clear(),T=False)
 add('recomputation-not-a-View',lambda m:m['predicates']['RecomputedView'].append(['v1','other']),T=False)
 add('declared-recompute-different-content',lambda m:(m['predicates']['FrozenCopy'].clear(),setfn(m,'viewContent',['v2'],'other')),T=False)
 for n in b.INFER_FLAGS:add('forbidden-inference-'+n,lambda m,n=n:m['predicates'][n].append(['v1']),T=False)
 add('empty-selected-projection-satisfies-universal-theory',lambda m:(m['predicates']['SelectedNode'].clear(),m['predicates']['SelectedEdge'].clear()),I=False)
 add('named-consumer-and-Session-role-may-overlap',lambda m:m['predicates']['AgentSessionRole'].append(['con1']),I=True)
 add('opaque-cut-cursor-and-digest-tokens-permitted',lambda m:[setfn(m,n,[e],'*') for n in ['viewSemanticCursor','viewGovernanceCursor','viewEventSetDigest','cutSemanticCursor','cutGovernanceCursor','cutEventSetDigest'] for e in m['domains']['Entity']],I=True)
 add('expired-noncurrent-use-not-forbidden-by-current-action-guard',lambda m:(m['predicates']['ActionRole'].append(['other']),m['predicates']['ViewUsableForAction'].append(['v3','other'])),I=True)
 add('recompute-equivalence-does-not-freeze-consumer-expiry',lambda m:m['predicates']['RecomputedView'].append(['v1','v3']),I=True)
 add('no-declared-copy-required-by-universal-theory',lambda m:m['predicates']['FrozenCopy'].clear(),I=False)
 add('no-declared-recompute-required-by-universal-theory',lambda m:m['predicates']['RecomputedView'].clear(),I=False)
 add('no-expired-stale-marker-required-by-universal-theory',lambda m:(m['predicates']['Expired'].clear(),m['predicates']['Stale'].clear()),I=False)
 add('expired-View-without-current-use-has-no-use-witness',lambda m:m['predicates']['CurrentStateAction'].remove(['v3','a1']),I=False)
 add('named-consumer-without-Session-witness',lambda m:setfn(m,'viewConsumer',['v3'],'con1'),I=False)
 add('nonempty-time-metadata-does-not-compute-expiry',lambda m:(m['predicates']['FrozenCopy'].clear(),setfn(m,'viewExpiry',['v1'],'past')),I=True)
 add('nontotal-governance-cursor-function',lambda m:m['functions']['viewGovernanceCursor'].pop(),error='nontotal-function')
 add('ill-sorted-view-content-result',lambda m:setfn(m,'viewContent',['v1'],'v1'),error='ill-sorted-function-result')
 add('ill-sorted-empty-constant',lambda m:m['constants'].update(EMPTY='absent'),error='ill-sorted-constant')
 add('wrong-selected-node-arity',lambda m:m['predicates'].update(SelectedNode=[['v1']]),error='ill-sorted-model-tuple')
 add('duplicate-selected-node-tuple',lambda m:m['predicates']['SelectedNode'].append(['v1','n1']),error='duplicate-predicate-tuple')
 add('empty-entity-domain',lambda m:m['domains'].update(Entity=[]),error='empty-or-malformed-domain')
 add('duplicate-view-cut-function-tuple',lambda m:m['functions']['viewCut'].append(copy.deepcopy(m['functions']['viewCut'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.ontology-node/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-OntologyView-model-controls/v1-candidate','status':'PASS-for-exact-authored-OntologyView-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent typed exact-cut purpose/consumer metadata,selected item/source/identity guards,frozen and declared recomputation,expired/stale current-use rejection and no authority widening. Actual cursor/hash/time/selection/write/runtime/source-owner maps pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
