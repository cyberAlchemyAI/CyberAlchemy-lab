"""Finite Promotion lifecycle and version/event separation controls; actual authority remains absent."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def base_model():
 domains={'Entity':['c1','c2','l1','l2','p1','p2','a1','a2','k1','i1'],'Domain':['origin','other','third'],'Version':['v1','v2'],'Token':['empty','stages','gates','owner','stop'],'State':['source','candidate','review','promoted','pressure']};functions={}
 for n,(args,result) in b.FUNCTIONS.items():
  rows=[]
  for e in domains['Entity']:
   if n=='originOwner':value='origin'
   elif n=='eventCandidate':value='c2' if e in ['p2','a1','a2'] else 'c1'
   elif n=='eventVersion':value='v2' if e=='p1' else 'v1'
   elif n=='eventDomain':value='other' if e in ['a1','a2'] else 'origin'
   else:value={'stagesValue':'stages','perStageGatesValue':'gates','ownerRouteValue':'owner','stopRuleValue':'stop'}[n]
   rows.append({'args':[e],'value':value})
  functions[n]=rows
 p={n:[] for n in b.SIGNATURE};p.update(AuthorityPromotionLifecycle=[['l1'],['l2']],ValidLifecycle=[['l1']],AuthorityBearingKind=[['k1']],LifecycleBearingKind=[['k1']],InputOrTerminalKind=[['i1']],GeneralizedForCAV2=[['c1','origin']],ExercisedIn=[['c1','origin'],['c1','other'],['c2','origin'],['c2','other']],IndependentlyOwned=[['other']],MateriallyDistinct=[['other','origin']],ChallengeReviewed=[['c1'],['c2']],CAV2OwnerPromoted=[['c1'],['c2']],PromotedInCAV2=[['c1','v1'],['c2','v1']],CAV2AuthorityCreated=[['c1','v1'],['c2','v1']],OriginRetainsAuthority=[['c1','origin'],['c2','origin']],AdoptedByDomain=[['c2','v1','other']],AdoptionEvent=[['a1']],AdoptionFor=[['a1','c2','v1','other']],SeparateDomainOwnerDecision=[['a1']],DomainOwnerDecides=[['a1','other']],ProvenanceEvent=[['p1'],['p2']],UpstreamProvenanceFor=[['p1','c1'],['p2','c2']],SeparatelyOwnedEvents=[['p2','a1']],PromotedVersionEvent=[['a2','c1','v1']],ActivatedBySeparateDecision=[['c2','v1','other']],AtStage=[['c1','promoted']],TransitionsTo=[['c1','source','candidate'],['c1','candidate','review'],['c1','review','promoted']])
 for n in b.FIELDS:p['Names'+n[0].upper()+n[1:]]=[['l1'],['l2']]
 return {'domains':domains,'constants':{'EMPTY':'empty'},'functions':functions,'predicates':p}
def setvalue(m,n,e,value):next(x for x in m['functions'][n] if x['args']==[e])['value']=value
def controls():
 rows=[]
 def add(id,change,T=True,I=None,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('version-exact-promotion-separate-adoption-no-world-effects',lambda m:None,I=True)
 for n in b.OUTCOMES:add('independently-supplied-marker-'+n,lambda m,n=n:m['predicates'][n].append(['l1']),I=True)
 for n in ['PermanentAdapter','SynchronizedCrosswalk','MappingOwner','LiveCoupling']:add('independent-coupling-not-created-by-source-events-'+n,lambda m,n=n:m['predicates'][n].append(['c2']),I=True)
 for n in b.FIELDS:
  add('valid-lifecycle-missing-named-'+n,lambda m,n=n:m['predicates']['Names'+n[0].upper()+n[1:]].remove(['l1']),T=False)
  add('valid-lifecycle-empty-'+n+'-projection',lambda m,n=n:setvalue(m,n+'Value','l1','empty'),T=False)
 add('valid-object-not-Lifecycle',lambda m:m['predicates']['AuthorityPromotionLifecycle'].remove(['l1']),T=False)
 add('wrong-origin-domain-binding',lambda m:setvalue(m,'originOwner','c1','third'),T=False)
 add('missing-origin-exercise',lambda m:m['predicates']['ExercisedIn'].remove(['c1','origin']),T=False)
 add('missing-independent-other-owner',lambda m:m['predicates'].update(IndependentlyOwned=[]),T=False)
 add('missing-material-distinction-formal-AND-not-prose-OR',lambda m:m['predicates'].update(MateriallyDistinct=[]),T=False)
 add('missing-other-domain-exercise',lambda m:m['predicates']['ExercisedIn'].remove(['c1','other']),T=False)
 add('missing-challenge-review',lambda m:m['predicates']['ChallengeReviewed'].remove(['c1']),T=False)
 add('missing-CAV2-owner-promotion',lambda m:m['predicates']['CAV2OwnerPromoted'].remove(['c1']),T=False)
 add('lifecycle-kind-not-authority-bearing',lambda m:m['predicates'].update(AuthorityBearingKind=[]),T=False)
 add('input-or-terminal-kind-lifecycle-collapse',lambda m:m['predicates']['LifecycleBearingKind'].append(['i1']),T=False)
 add('promotion-missing-exact-version-local-standing',lambda m:m['predicates']['CAV2AuthorityCreated'].remove(['c1','v1']),T=False)
 add('other-version-standing-does-not-replace-exact-version',lambda m:m['predicates'].update(CAV2AuthorityCreated=[['c1','v2'],['c2','v1']]),T=False)
 add('promotion-erases-origin-standing',lambda m:m['predicates']['OriginRetainsAuthority'].remove(['c1','origin']),T=False)
 add('promotion-rewrites-origin',lambda m:m['predicates']['OriginRewrittenByPromotion'].append(['c1','origin']),T=False)
 for d in ['origin','other','third']:add('promotion-automatically-activates-'+d,lambda m,d=d:m['predicates']['ActivatedByPromotion'].append(['c1','v1',d]),T=False)
 add('adoption-without-separate-event',lambda m:m['predicates'].update(AdoptionEvent=[]),T=False)
 add('adoption-without-separate-owner-decision',lambda m:m['predicates'].update(SeparateDomainOwnerDecision=[]),T=False)
 add('adoption-without-selected-domain-owner',lambda m:m['predicates'].update(DomainOwnerDecides=[]),T=False)
 add('adoption-event-wrong-candidate',lambda m:setvalue(m,'eventCandidate','a1','c1'),T=False)
 add('adoption-event-wrong-version',lambda m:setvalue(m,'eventVersion','a1','v2'),T=False)
 add('adoption-event-wrong-domain',lambda m:setvalue(m,'eventDomain','a1','origin'),T=False)
 add('adoption-event-missing-exact-tuple',lambda m:m['predicates'].update(AdoptionFor=[]),T=False)
 add('paired-upstream-record-not-ProvenanceEvent',lambda m:m['predicates']['ProvenanceEvent'].remove(['p2']),T=False)
 add('paired-events-not-separately-owned',lambda m:m['predicates'].update(SeparatelyOwnedEvents=[]),T=False)
 def collapsed(m):
  p=m['predicates'];p['AdoptionEvent'].append(['p2']);p['AdoptionFor'].append(['p2','c2','v1','other']);p['SeparateDomainOwnerDecision'].append(['p2']);p['DomainOwnerDecides'].append(['p2','other']);p['SeparatelyOwnedEvents'].append(['p2','p2']);setvalue(m,'eventDomain','p2','other')
 add('provenance-and-adoption-same-event',collapsed,T=False)
 add('complete-generalization-requirements-with-no-generalization',lambda m:m['predicates'].update(GeneralizedForCAV2=[]),I=False)
 add('complete-lifecycle-fields-with-no-valid-lifecycle',lambda m:m['predicates'].update(ValidLifecycle=[]),I=False)
 add('no-input-kind-is-an-alternative-theory-model-not-rich-I',lambda m:m['predicates'].update(InputOrTerminalKind=[]),I=False)
 add('no-independent-activation-is-an-alternative-model',lambda m:m['predicates'].update(ActivatedBySeparateDecision=[]),I=False)
 add('independent-activation-in-another-domain-does-not-follow-promotion',lambda m:m['predicates']['ActivatedBySeparateDecision'].append(['c1','v1','third']),I=True)
 def same_domain(m):m['predicates']['IndependentlyOwned'].append(['origin']);m['predicates']['MateriallyDistinct'].append(['origin','origin']);m['predicates']['ExercisedIn'].remove(['c1','other'])
 add('unreviewed-distinction-predicate-does-not-force-domain-disequality',same_domain,I=True)
 add('nontotal-owner-projection',lambda m:m['functions']['originOwner'].pop(),error='nontotal-function')
 add('ill-sorted-version-projection',lambda m:setvalue(m,'eventVersion','a1','origin'),error='ill-sorted-function-result')
 add('ill-sorted-empty-sentinel',lambda m:m['constants'].update(EMPTY='absent'),error='ill-sorted-constant')
 add('wrong-adoption-tuple-arity',lambda m:m['predicates'].update(AdoptionFor=[['a1','c2','v1']]),error='ill-sorted-model-tuple')
 add('duplicate-exercise-tuple',lambda m:m['predicates']['ExercisedIn'].append(['c1','origin']),error='duplicate-predicate-tuple')
 add('empty-Domain-carrier',lambda m:m['domains'].update(Domain=[]),error='empty-or-malformed-domain')
 add('duplicate-function-tuple',lambda m:m['functions']['originOwner'].append(copy.deepcopy(m['functions']['originOwner'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.authority-model/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-AuthorityPromotion-model-controls/v1-candidate','status':'PASS-for-exact-authored-AuthorityPromotion-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent supplied lifecycle/generalization/local-version/separate-adoption-event models. Prose OR versus formal AND, complete staged paths, exact tuple, causal/owner/event/version denotation, universal enforcement and real promotion remain unresolved.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
