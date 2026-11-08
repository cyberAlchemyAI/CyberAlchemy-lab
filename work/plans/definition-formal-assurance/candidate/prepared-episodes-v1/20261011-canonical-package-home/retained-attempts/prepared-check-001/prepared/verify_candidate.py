"""Supplied Registry entry,binding,overlay and discriminator models."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def setfn(m,n,arg,value):
 args=arg if isinstance(arg,list) else [arg];next(x for x in m['functions'][n] if x['args']==args)['value']=value
def getfn(m,n,*args):return next(x['value'] for x in m['functions'][n] if x['args']==list(args))
def refresh(m):
 p=m['predicates'];get=lambda n,*args:getfn(m,n,*args)
 for n in b.MOVEMENT_FACETS:
  p[(n+'BindingDeclared') if n!='movementAggregate' else 'MovementAggregateBindingDeclared']=[[x[0],get(n,x[0])] for x in p['MovementInScopeDeclared']]
 p['FacetKindBindingDeclared']=[[x[0],get('facetKind',x[0])] for x in p['FacetInScopeDeclared']]
def base_model():
 ds={s:[] for s in b.SORTS};ds.update(AggregateReference=['aggMain','aggSecond','aggOutside'],HomeReference=['homeMain','homeSecond','homeOutside'],CarrierReference=['carrierMain','carrierSecond','carrierOutside'],OwnerReference=['ownerMain','ownerSecond','ownerOutside'],UnitReference=['unitMain','unitSecond','unitOutside'],RecoveryBoundaryReference=['recoveryMain','recoverySecond','recoveryOutside'],ManifestReference=['manifestMain','manifestSecond','manifestOutside'],FacetReference=['facet'+str(i) for i in range(8)]+['facetOutside'],FacetKind=['kind'+n for n in b.KIND_NAMES]+['kindFuture','kindOutside'],SemanticIdentity=['idMain','idSecond']+['idFacet'+str(i) for i in range(8)]+['idChanged','idOutside'],AuthorityScope=['authorityMain','authoritySecond']+['authorityFacet'+str(i) for i in range(8)]+['authorityChanged','authorityOutside'],TypedRelationReference=['relation'+str(i) for i in range(8)]+['relationOutside'],GlobalViewReference=['viewReference','viewProjection','viewOutside'],LocationReference=['locationMain','locationMoved','locationOutside'],ContextReference=['contextMain','contextSecond','contextChanged','contextOutside'],MovementReference=['movePlain','moveDecision','moveOutside'],Token=['empty','none','reference','differentReference'])
 cs={'EMPTY':'empty','NONE':'none',**{n:'kind'+n for n in b.KIND_NAMES}}
 def suffix(x,prefix):return x[len(prefix):]
 def byagg(prefix,a):return prefix+suffix(a,'agg')
 def fagg(f):return 'aggOutside' if f=='facetOutside' else 'aggMain' if int(suffix(f,'facet'))<7 else 'aggSecond'
 maps={n:(lambda a,n=n,s=s:'none' if n=='aggregateEffect' else 'locationMain' if n=='aggregateLocation' and a!='aggOutside' else byagg({'aggregateHome':'home','aggregateOwner':'owner','aggregateUnit':'unit','aggregateRecovery':'recovery','aggregateManifest':'manifest','aggregateLocation':'location','aggregateIdentity':'id','aggregateContext':'context','aggregateAuthority':'authority'}[n],a)) for n,s in b.FACETS.items()}
 maps.update(homeOwner=lambda h:'owner'+suffix(h,'home'),homeUnit=lambda h:'unit'+suffix(h,'home'),homeRecovery=lambda h:'recovery'+suffix(h,'home'),unitRecovery=lambda u:'recovery'+suffix(u,'unit'),carrierAggregate=lambda c:'agg'+suffix(c,'carrier'),carrierHome=lambda c:'home'+suffix(c,'carrier'),manifestAggregate=lambda m:'agg'+suffix(m,'manifest'),manifestOwner=lambda m:'owner'+suffix(m,'manifest'),manifestUnit=lambda m:'unit'+suffix(m,'manifest'),facetAggregate=fagg,facetHome=lambda f:byagg('home',fagg(f)),facetOwner=lambda f:byagg('owner',fagg(f)),facetUnit=lambda f:byagg('unit',fagg(f)),facetIdentity=lambda f:'idFacet'+suffix(f,'facet') if f!='facetOutside' else 'idOutside',facetAuthority=lambda f:'authorityFacet'+suffix(f,'facet') if f!='facetOutside' else 'authorityOutside',facetContext=lambda f:byagg('context',fagg(f)),facetKind=lambda f:'kindOutside' if f=='facetOutside' else 'kind'+b.KIND_NAMES[int(suffix(f,'facet'))%7],facetRelation=lambda f:'relation'+suffix(f,'facet'),relationFacet=lambda r:'facet'+suffix(r,'relation'),relationAggregate=lambda r:fagg('facet'+suffix(r,'relation')))
 maps['movementAggregate']=lambda m:'aggOutside' if m=='moveOutside' else 'aggMain'
 for family,prefix in [('Identity','id'),('Context','context'),('Authority','authority'),('Location','location')]:
  maps['movementBefore'+family]=lambda m,prefix=prefix:prefix+('Outside' if m=='moveOutside' else 'Main')
  maps['movementAfter'+family]=lambda m,prefix=prefix,family=family:prefix+'Outside' if m=='moveOutside' else 'locationMoved' if family=='Location' else prefix+'Changed' if m=='moveDecision' else prefix+'Main'
 for s,n in b.HANDLES.items():maps[n]=lambda x:'reference'
 assert maps.keys()==b.FUNCTIONS.keys();functions={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(ds[s] for s in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};p={n:[] for n in b.SIGNATURE};aggregates=['aggMain','aggSecond']
 for s in b.SORTS:
  if s not in ['AggregateReference','Token']:p[s+'Declared']=[[x] for x in ds[s] if not x.endswith('Outside')]
 p['HomeApplicable']=p['AggregateInScopeDeclared']=[[a] for a in aggregates]
 for n in b.FACETS:p[n+'BindingDeclared']=[[a,maps[n](a)] for a in aggregates]
 p['HomeInScopeDeclared']=[['homeMain'],['homeSecond']];p['HomeForAggregateDeclared']=[[a,maps['aggregateHome'](a)] for a in aggregates]
 for n in ['homeOwner','homeUnit','homeRecovery']:p[n+'BindingDeclared']=[[h,maps[n](h)] for h in ['homeMain','homeSecond']]
 p['UnitRecoveryBindingDeclared']=[[u,maps['unitRecovery'](u)] for u in ['unitMain','unitSecond']]
 p['CarrierInScopeDeclared']=[['carrierMain'],['carrierSecond']];p['CarrierInAggregateDeclared']=[[c,maps['carrierAggregate'](c)] for c in ['carrierMain','carrierSecond']];p['CanonicalAtDeclared']=[[c,maps['carrierHome'](c)] for c in ['carrierMain','carrierSecond']]
 for n in ['manifestAggregate','manifestOwner','manifestUnit']:p[n[0].upper()+n[1:]+'BindingDeclared']=[[x,maps[n](x)] for x in ['manifestMain','manifestSecond']]
 p['FacetInScopeDeclared']=[[f] for f in ds['FacetReference'][:-1]];p['FacetMemberDeclared']=[[maps['facetAggregate'](f),f] for f in ds['FacetReference'][:-1]];p['FacetAggregateEdgeDeclared']=[[f,maps['facetAggregate'](f),maps['facetRelation'](f)] for f in ds['FacetReference'][:-1]]
 p['ViewInScopeDeclared']=[['viewReference'],['viewProjection']];p['ViewReferencesCarrierDeclared']=[['viewReference','carrierMain']];p['ViewProjectsCarrierDeclared']=[['viewProjection','carrierMain']];p['MovementInScopeDeclared']=[['movePlain'],['moveDecision']];p['SemanticDecisionDeclared']=[['moveDecision']];p['HomeActualAuthority']=[['aggSecond']]
 model={'domains':ds,'constants':cs,'functions':functions,'predicates':p};refresh(model);return model

def controls():
 rows=[]
 def add(name,mutation=lambda m:None,T=True,I=True,error=None):
  m=base_model();mutation(m);rows.append({'case_id':name,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 def coherent_fn(m,n,arg,value):setfn(m,n,arg,value);refresh(m)
 add('necessary-owner-unit-carrier-facet-index-and-movement-declarations')
 add('no-applicable-aggregate',lambda m:m['predicates'].update(HomeApplicable=[],AggregateInScopeDeclared=[],CarrierInScopeDeclared=[],CarrierInAggregateDeclared=[],FacetInScopeDeclared=[],FacetMemberDeclared=[],MovementInScopeDeclared=[]),I=False)
 add('absent-canonical-carrier-population',lambda m:m['predicates'].update(CarrierInScopeDeclared=[],CarrierInAggregateDeclared=[]),I=False)
 add('absent-view-scope-populations',lambda m:m['predicates'].update(ViewInScopeDeclared=[]),I=False)
 add('absent-no-decision-movement-population',lambda m:m['predicates'].update(MovementInScopeDeclared=[['moveDecision']]),I=False)
 add('decision-gated-change-permitted',lambda m:m['predicates'].update(SemanticDecisionDeclared=[['movePlain'],['moveDecision']]),I=False)
 add('authority-decision-gated-change-permitted',lambda m:(m['predicates'].update(AuthorityDecisionDeclared=[['movePlain']]),coherent_fn(m,'movementAfterAuthority','movePlain','authorityChanged')),I=False)
 add('future-facet-kind-not-global-vocabulary-error',lambda m:coherent_fn(m,'facetKind','facet0','kindFuture'),I=False)
 add('matching-owner-unit-outside-governed-candidate-domain-ignored',lambda m:(setfn(m,'homeOwner','homeOutside','ownerMain'),setfn(m,'homeUnit','homeOutside','unitMain')))
 add('outside-canonical-at-and-path-inferences-ignored',lambda m:(m['predicates']['CanonicalAtDeclared'].append(['carrierOutside','homeOutside']),m['predicates']['PathOwnerInferenceDeclared'].append(['aggOutside'])))
 add('same-facet-id-across-independent-aggregates-not-global-injectivity',lambda m:setfn(m,'facetIdentity','facet7','idFacet0'))
 for name in b.ACTUAL:add('independently-supported-actual-'+name,lambda m,name=name:m['predicates']['HomeActual'+name].append(['aggMain']),I=False)
 for n in b.EXCLUDED:add('prohibited-'+n,lambda m,n=n:m['predicates'][n].append(['aggMain']),T=False,I=None)
 for n,s in b.FACETS.items():
  add('missing-binding-'+n,lambda m,n=n:m['predicates'].update({n+'BindingDeclared':m['predicates'][n+'BindingDeclared'][1:]}),T=False,I=None)
  if s!='Token':add('conflicting-binding-'+n,lambda m,n=n,s=s:m['predicates'][n+'BindingDeclared'].append(['aggMain',m['domains'][s][-1]]),T=False,I=None)
 add('aggregate-home-empty-reference',lambda m:setfn(m,b.HANDLES['HomeReference'],'homeMain','empty'),T=False,I=None)
 add('home-owner-mismatch',lambda m:setfn(m,'homeOwner','homeMain','ownerSecond'),T=False,I=None)
 add('home-unit-mismatch',lambda m:setfn(m,'homeUnit','homeMain','unitSecond'),T=False,I=None)
 add('unit-recovery-mismatch',lambda m:setfn(m,'unitRecovery','unitMain','recoverySecond'),T=False,I=None)
 add('extra-governed-home-hidden-by-selector',lambda m:(m['predicates']['HomeInScopeDeclared'].append(['homeOutside']),m['predicates']['HomeReferenceDeclared'].append(['homeOutside']),setfn(m,'homeOwner','homeOutside','ownerMain'),setfn(m,'homeUnit','homeOutside','unitMain')),T=False,I=None)
 add('missing-home-for-aggregate-relation',lambda m:m['predicates'].update(HomeForAggregateDeclared=[['aggSecond','homeSecond']]),T=False,I=None)
 add('carrier-second-home-hidden-by-selector',lambda m:m['predicates']['CanonicalAtDeclared'].append(['carrierMain','homeSecond']),T=False,I=None)
 add('carrier-no-canonical-home-relation',lambda m:m['predicates'].update(CanonicalAtDeclared=[['carrierSecond','homeSecond']]),T=False,I=None)
 add('carrier-home-does-not-carry-aggregate',lambda m:setfn(m,'carrierHome','carrierMain','homeSecond'),T=False,I=None)
 add('missing-carrier-aggregate-member',lambda m:m['predicates'].update(CarrierInAggregateDeclared=[['carrierSecond','aggSecond']]),T=False,I=None)
 for n in ['manifestAggregate','manifestOwner','manifestUnit']:
  add('manifest-incorrect-'+n,lambda m,n=n:setfn(m,n,'manifestMain',m['domains'][b.FUNCTIONS[n][1]][1]),T=False,I=None)
  field=n[0].upper()+n[1:]+'BindingDeclared';add('manifest-missing-'+n,lambda m,field=field:m['predicates'].update({field:m['predicates'][field][1:]}),T=False,I=None)
 add('colocated-facet-identities-collapsed',lambda m:setfn(m,'facetIdentity','facet1','idFacet0'),T=False,I=None)
 add('colocated-facet-authority-scopes-collapsed',lambda m:setfn(m,'facetAuthority','facet1','authorityFacet0'),T=False,I=None)
 add('facet-collapsed-with-aggregate-identity',lambda m:setfn(m,'facetIdentity','facet0','idMain'),T=False,I=None)
 add('facet-wrong-home',lambda m:setfn(m,'facetHome','facet0','homeSecond'),T=False,I=None)
 add('facet-different-lifecycle-owner-colocated',lambda m:setfn(m,'facetOwner','facet0','ownerSecond'),T=False,I=None)
 add('facet-independent-unit-colocated',lambda m:setfn(m,'facetUnit','facet0','unitSecond'),T=False,I=None)
 add('facet-missing-typed-edge',lambda m:m['predicates'].update(FacetAggregateEdgeDeclared=m['predicates']['FacetAggregateEdgeDeclared'][1:]),T=False,I=None)
 add('typed-edge-wrong-target',lambda m:setfn(m,'relationAggregate','relation0','aggSecond'),T=False,I=None)
 add('global-view-duplicates-canonical-carrier',lambda m:m['predicates']['ViewContainsCanonicalCopyDeclared'].append(['viewReference','carrierMain']),T=False,I=None)
 for suffix,value in [('Identity','idChanged'),('Context','contextChanged'),('Authority','authorityChanged')]:add('no-decision-movement-changes-'+suffix,lambda m,suffix=suffix,value=value:coherent_fn(m,'movementAfter'+suffix,'movePlain',value),T=False,I=None)
 add('movement-aggregate-binding-missing',lambda m:m['predicates'].update(MovementAggregateBindingDeclared=[['moveDecision','aggMain']]),T=False,I=None)
 add('movement-before-identity-not-bound-to-aggregate',lambda m:coherent_fn(m,'movementBeforeIdentity','movePlain','idChanged'),T=False,I=None)
 for n,s in [('aggregateHome','HomeReference'),('aggregateOwner','OwnerReference'),('aggregateUnit','UnitReference'),('facetRelation','TypedRelationReference'),('movementAfterIdentity','SemanticIdentity')]:add('malformed-total-output-'+n,lambda m,n=n:m['functions'][n][0].update(value='not-in-sort'),T=None,I=None,error='sort-mismatch')
 add('malformed-empty-home-domain',lambda m:m['domains'].update(HomeReference=[]),T=None,I=None,error='empty-sort-domain')
 add('malformed-missing-function',lambda m:m['functions'].pop('homeOwner'),T=None,I=None,error='missing-function')
 add('malformed-duplicate-function-tuple',lambda m:m['functions']['homeOwner'].append(copy.deepcopy(m['functions']['homeOwner'][0])),T=None,I=None,error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.artifact-type-resolution/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-CanonicalPackageHome-model-controls/v1-candidate','status':'PASS-for-exact-authored-CanonicalPackageHome-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Typed declared owner/unit/home,carrier uniqueness,manifest fields,distinct facets,typed edges,reference-only views and movement invariance checked on supplied finite models. Actual ownership,canonical source correctness,migration,consumer alignment and whole fidelity remain pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
