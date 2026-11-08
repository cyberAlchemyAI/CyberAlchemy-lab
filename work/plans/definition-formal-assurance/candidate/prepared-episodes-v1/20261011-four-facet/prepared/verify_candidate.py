"""Supplied four-facet,surface,view and typed-residue models."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def setfn(m,n,arg,value):
 args=arg if isinstance(arg,list) else [arg];next(x for x in m['functions'][n] if x['args']==args)['value']=value
def getfn(m,n,*args):return next(x['value'] for x in m['functions'][n] if x['args']==list(args))
def refresh(m):
 for fields,carrier in b.GROUPS:
  for n in fields:m['predicates'][n+'BindingDeclared']=[[x['args'][0],x['value']] for x in m['functions'][n]]
def base_model():
 ds={'ActionReference':['aMixed','aResidue','aOutside'],'InvariantReference':['invariantMain','invariantOutside'],'BindingReference':['bMK','bMS','bMH','bMM','bRK','bRS','bRH','bRM','bExtraM','bOutside'],'FacetTag':['facetK','facetS','facetH','facetM','facetOther'],'SurfaceReference':['sK','sS','sH','sM','sOutside'],'ClassificationReference':['classificationMain','classificationOutside'],'CatalogReference':['catalogMain','catalogOutside'],'SchemaReference':['schemaMain','schemaOutside'],'HumanViewReference':['humanMain','humanOutside'],'MachineViewReference':['machineMain','machineOutside'],'ResidueReference':['rMixedM','rRK','rRS','rRH','rRM','rOutside'],'ReasonReference':['reasonMissing','reasonImpossible','reasonDeferred','reasonOutside'],'OwnerRouteReference':['ownerMain','ownerOutside'],'EvidenceReference':['evidenceMain','evidenceOutside'],'ActionEffect':['continue','defer','block','otherEffect'],'PromotionEffect':['noPromotionEffect','declaredPromotionEffect','otherPromotionEffect'],'SourceReference':['sourceApproved','sourceD21','sourceOutside'],'ScopeReference':['currentScope','sharedScope','outsideScope'],'SemanticIdentity':['mixedIdentity','residueIdentity','outsideIdentity','invariantIdentity','methodIdentity','siblingIdentity','kindIdentity'],'TypeReference':['actionType','invariantType','outsideType'],'Token':['empty','none','bound','created','residue','missing','impossible','deferred','reference','detail','other']}
 cs={'EMPTY':'empty','NONE':'none','BOUND':'bound','CREATED':'created','RESIDUE':'residue','MISSING':'missing','IMPOSSIBLE':'impossible','DEFERRED':'deferred','K':'facetK','S':'facetS','H':'facetH','M':'facetM','TARGET_INVARIANT':'invariantMain','INVARIANT_ID':'invariantIdentity','METHOD_ID':'methodIdentity','SIBLING_ID':'siblingIdentity','CURRENT_SCOPE':'currentScope','SHARED_SCOPE':'sharedScope','INVARIANT_TYPE':'invariantType','D21_SOURCE':'sourceD21','CONTINUE':'continue','DEFER':'defer','BLOCK':'block','NO_PROMOTION_EFFECT':'noPromotionEffect'}
 def outside(x):return x.endswith('Outside')
 def facet(x):return 'facetM' if x=='bExtraM' or x=='rMixedM' else 'facetOther' if outside(x) else 'facet'+x[-1]
 def action(x):return 'aOutside' if outside(x) else 'aResidue' if x.startswith('bR') or x.startswith('rR') else 'aMixed'
 def record_residue(x):return 'rOutside' if outside(x) else 'r'+x[1:] if x.startswith('bR') else 'rMixedM'
 maps={}
 maps.update(actionInvariant=lambda x:'invariantOutside' if outside(x) else 'invariantMain',actionOwnerRoute=lambda x:'ownerOutside' if outside(x) else 'ownerMain',actionSource=lambda x:'sourceOutside' if outside(x) else 'sourceApproved',actionScope=lambda x:'outsideScope' if outside(x) else 'currentScope',actionIdentity=lambda x:'outsideIdentity' if outside(x) else 'residueIdentity' if x=='aResidue' else 'mixedIdentity',actionType=lambda x:'outsideType' if outside(x) else 'actionType',actionEffect=lambda x:'none',invariantIdentity=lambda x:'methodIdentity' if outside(x) else 'invariantIdentity',invariantScope=lambda x:'outsideScope' if outside(x) else 'sharedScope',invariantType=lambda x:'invariantType',invariantSource=lambda x:'sourceD21')
 maps.update(actionBinding=lambda a,f:'bOutside' if outside(a) or f=='facetOther' else ('bR' if a=='aResidue' else 'bM')+f[-1],bindingAction=action,bindingFacet=facet,bindingMode=lambda x:'residue' if x.startswith('bR') or x=='bMM' else 'created' if x=='bMS' else 'bound',bindingSurface=lambda x:'sOutside' if outside(x) else 's'+facet(x)[-1],bindingResidue=record_residue,bindingSource=lambda x:'sourceOutside' if outside(x) else 'sourceApproved')
 maps.update(surfaceOwnerRoute=lambda x:'ownerOutside' if outside(x) else 'ownerMain',surfaceSource=lambda x:'sourceOutside' if outside(x) else 'sourceApproved',surfaceClassification=lambda x:'classificationOutside' if outside(x) else 'classificationMain',surfaceSchema=lambda x:'schemaOutside' if outside(x) else 'schemaMain',surfaceHuman=lambda x:'humanOutside' if outside(x) else 'humanMain',surfaceMachine=lambda x:'machineOutside' if outside(x) else 'machineMain',surfaceCreator=lambda x:'aOutside' if outside(x) else 'aMixed')
 maps.update(classificationKind=lambda x:'outsideIdentity' if outside(x) else 'kindIdentity',classificationCatalog=lambda x:'catalogOutside' if outside(x) else 'catalogMain',classificationSource=lambda x:'sourceOutside' if outside(x) else 'sourceApproved',catalogSource=lambda x:'sourceOutside' if outside(x) else 'sourceApproved',schemaShape=lambda x:'detail',schemaSource=lambda x:'sourceOutside' if outside(x) else 'sourceApproved')
 maps.update(humanPurpose=lambda x:'detail',humanStatus=lambda x:'detail',humanTrustBoundary=lambda x:'detail',humanBlockers=lambda x:'none',humanResidue=lambda x:'none',humanNextRoute=lambda x:'ownerOutside' if outside(x) else 'ownerMain',humanEvidence=lambda x:'evidenceOutside' if outside(x) else 'evidenceMain',humanSource=lambda x:'sourceOutside' if outside(x) else 'sourceApproved')
 maps.update(machineIdentifier=lambda x:'outsideIdentity' if outside(x) else 'mixedIdentity',machineKind=lambda x:'kindIdentity',machineSchema=lambda x:'schemaOutside' if outside(x) else 'schemaMain',machineClassification=lambda x:'classificationOutside' if outside(x) else 'classificationMain',machineTruthSource=lambda x:'sourceOutside' if outside(x) else 'sourceApproved',machineValidatorProofHandle=lambda x:'reference',machineProjectionStatus=lambda x:'detail',machineResidue=lambda x:'none',machineNamedChecks=lambda x:'detail')
 maps.update(residueAction=action,residueFacet=facet,residueReason=lambda x:'reasonOutside' if outside(x) else 'reasonDeferred' if x=='rRS' else 'reasonImpossible' if x=='rRM' else 'reasonMissing',residueOwnerRoute=lambda x:'ownerOutside' if outside(x) else 'ownerMain',residueEvidence=lambda x:'evidenceOutside' if outside(x) else 'evidenceMain',residueActionEffect=lambda x:'block' if x in ['rMixedM','rRM'] else 'defer' if x=='rRS' else 'continue',residuePromotionEffect=lambda x:'declaredPromotionEffect' if x=='rMixedM' else 'noPromotionEffect',residueSource=lambda x:'sourceOutside' if outside(x) else 'sourceApproved',reasonKind=lambda x:'impossible' if x=='reasonImpossible' else 'deferred' if x=='reasonDeferred' else 'missing',reasonDetail=lambda x:'detail')
 for sort,n in b.HANDLES.items():maps[n]=lambda x:'reference'
 assert maps.keys()==b.FUNCTIONS.keys(),(maps.keys()-b.FUNCTIONS.keys(),b.FUNCTIONS.keys()-maps.keys())
 funcs={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(ds[s] for s in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};p={n:[] for n in b.SIGNATURE}
 for sort in b.SORTS:
  if sort not in ['ActionReference','Token']:p[sort+'Declared']=[[x] for x in ds[sort]]
 p.update(ActionApplicable=[['aMixed'],['aResidue']],ActionInScopeDeclared=[['aMixed'],['aResidue']],FourFacetSatisfiedDeclared=[['aMixed'],['aResidue']],RequiredFacetDeclared=[[x] for x in ['facetK','facetS','facetH','facetM']],BindingRecordForDeclared=[[a,f,maps['actionBinding'](a,f)] for a in ['aMixed','aResidue'] for f in ['facetK','facetS','facetH','facetM']]+[['aMixed','facetM','bExtraM']],ExistingBoundSurfaceDeclared=[['bMK','sK'],['bMH','sH'],['bExtraM','sM']],CreatedSurfaceDeclared=[['bMK','sK'],['bMS','sS']],TypedResidueForDeclared=[['bMM','rMixedM']]+[['bR'+f,'rR'+f] for f in ['K','S','H','M']],SurfaceGovernedDeclared=[[x] for x in ds['SurfaceReference']],SurfaceCreatedByDeclared=[['sK','aMixed'],['sS','aMixed']],PromotionAskedDeclared=[['aMixed']],SourceCurrentDeclared=[['sourceApproved']],SourceOwnerApprovedDeclared=[['sourceApproved']],ActionActualAuthority=[['aMixed']])
 m={'domains':ds,'constants':cs,'functions':funcs,'predicates':p};refresh(m);return m
def controls():
 rows=[]
 def add(name,mutation=lambda m:None,T=True,I=True,error=None):
  m=base_model();mutation(m);rows.append({'case_id':name,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 def change(m,n,arg,value):setfn(m,n,arg,value);refresh(m)
 add('four-facets-mixed-surfaces-and-all-residue-exploration')
 add('no-applicable-actions',lambda m:m['predicates'].update(ActionApplicable=[],ActionInScopeDeclared=[]),I=False)
 add('only-all-residue-action-selected',lambda m:m['predicates'].update(ActionApplicable=[['aResidue']],ActionInScopeDeclared=[['aResidue']]),I=False)
 add('only-mixed-action-selected',lambda m:m['predicates'].update(ActionApplicable=[['aMixed']],ActionInScopeDeclared=[['aMixed']]),I=False)
 add('no-promotion-request',lambda m:m['predicates'].update(PromotionAskedDeclared=[]),I=False)
 add('no-overlap-created-path',lambda m:m['predicates'].update(CreatedSurfaceDeclared=[['bMS','sS']]),I=False)
 add('no-extra-complete-binding-record',lambda m:m['predicates'].update(BindingRecordForDeclared=[x for x in m['predicates']['BindingRecordForDeclared'] if x[-1]!='bExtraM']),I=False)
 add('outside-authority-inference-not-scoped',lambda m:m['predicates']['FacetMethodGrantsAuthorityDeclared'].append(['aOutside']))
 add('bound-and-created-coexist-on-one-record',lambda m:None)
 for n in b.ACTUAL:add('independently-supported-actual-'+n,lambda m,n=n:m['predicates']['ActionActual'+n].append(['aResidue']),I=False)
 for n in b.EXCLUDED:add('prohibited-'+n,lambda m,n=n:m['predicates'][n].append(['aMixed']),T=False,I=None)
 add('required-residue-as-fifth-facet',lambda m:m['predicates']['RequiredFacetDeclared'].append(['facetOther']),T=False,I=None)
 add('silent-missing-schema-record',lambda m:m['predicates'].update(BindingRecordForDeclared=[x for x in m['predicates']['BindingRecordForDeclared'] if x[:2]!=['aMixed','facetS']]),T=False,I=None)
 add('hidden-invalid-additional-binding',lambda m:m['predicates']['BindingRecordForDeclared'].append(['aMixed','facetK','bOutside']),T=False,I=None)
 add('wrong-nominated-binding',lambda m:setfn(m,'actionBinding',['aMixed','facetS'],'bOutside'),T=False,I=None)
 add('missing-typed-residue',lambda m:m['predicates'].update(TypedResidueForDeclared=m['predicates']['TypedResidueForDeclared'][1:]),T=False,I=None)
 for fields,carrier in b.GROUPS:
  for n,sort in fields.items():
   arg={'ActionReference':'aMixed','InvariantReference':'invariantMain','BindingReference':'bMM' if n=='bindingResidue' else 'bMK','SurfaceReference':{'surfaceClassification':'sK','surfaceSchema':'sS','surfaceHuman':'sH','surfaceMachine':'sM','surfaceCreator':'sK'}.get(n,'sK'),'ClassificationReference':'classificationMain','SchemaReference':'schemaMain','HumanViewReference':'humanMain','MachineViewReference':'machineMain','ResidueReference':'rMixedM','ReasonReference':'reasonMissing'}[carrier]
   add('missing-exact-binding-'+n,lambda m,n=n,arg=arg:m['predicates'].update({n+'BindingDeclared':[x for x in m['predicates'][n+'BindingDeclared'] if x[0]!=arg]}),T=False,I=None)
   alt='other' if sort=='Token' else next(x for x in base_model()['domains'][sort] if x!=getfn(base_model(),n,arg))
   add('conflicting-exact-binding-'+n,lambda m,n=n,arg=arg,alt=alt:m['predicates'][n+'BindingDeclared'].append([arg,alt]),T=False,I=None)
 for n,val in [('actionScope','outsideScope'),('actionInvariant','invariantOutside'),('actionEffect','other')]:add('action-mismatch-'+n,lambda m,n=n,val=val:change(m,n,'aMixed',val),T=False,I=None)
 for n,val in [('invariantIdentity','siblingIdentity'),('invariantScope','outsideScope'),('invariantType','actionType'),('invariantSource','sourceApproved')]:add('invariant-target-mismatch-'+n,lambda m,n=n,val=val:change(m,n,'invariantMain',val),T=False,I=None)
 for n,val in [('bindingAction','aResidue'),('bindingFacet','facetM'),('bindingMode','other'),('bindingSource','sourceOutside')]:add('record-mismatch-'+n,lambda m,n=n,val=val:change(m,n,'bMK',val),T=False,I=None)
 add('hidden-bound-surface',lambda m:m['predicates']['ExistingBoundSurfaceDeclared'].append(['bMK','sOutside']),T=False,I=None)
 add('hidden-created-surface',lambda m:m['predicates']['CreatedSurfaceDeclared'].append(['bMS','sOutside']),T=False,I=None)
 add('hidden-residue-link',lambda m:m['predicates']['TypedResidueForDeclared'].append(['bMM','rOutside']),T=False,I=None)
 add('surface-no-governed-binding',lambda m:m['predicates'].update(SurfaceGovernedDeclared=[]),T=False,I=None)
 add('created-surface-wrong-creator',lambda m:change(m,'surfaceCreator','sS','aResidue'),T=False,I=None)
 add('hidden-creator',lambda m:m['predicates']['SurfaceCreatedByDeclared'].append(['sS','aResidue']),T=False,I=None)
 add('catalog-source-mismatch',lambda m:setfn(m,'catalogSource','catalogMain','sourceOutside'),T=False,I=None)
 for n,arg in [('classificationSource','classificationMain'),('schemaSource','schemaMain'),('humanSource','humanMain'),('machineTruthSource','machineMain'),('surfaceSource','sK')]:add('view-source-mismatch-'+n,lambda m,n=n,arg=arg:change(m,n,arg,'sourceOutside'),T=False,I=None)
 for n,arg in [('schemaShape','schemaMain'),('humanPurpose','humanMain'),('humanStatus','humanMain'),('humanTrustBoundary','humanMain'),('humanBlockers','humanMain'),('humanResidue','humanMain'),('machineValidatorProofHandle','machineMain'),('machineProjectionStatus','machineMain'),('machineResidue','machineMain'),('machineNamedChecks','machineMain'),('reasonDetail','reasonMissing')]:add('silent-empty-description-'+n,lambda m,n=n,arg=arg:change(m,n,arg,'empty'),T=False,I=None)
 for n,val in [('residueAction','aResidue'),('residueFacet','facetK'),('residueSource','sourceOutside'),('residueActionEffect','otherEffect'),('residuePromotionEffect','noPromotionEffect')]:add('typed-residue-mismatch-'+n,lambda m,n=n,val=val:change(m,n,'rMixedM',val),T=False,I=None)
 add('untyped-reason-kind',lambda m:change(m,'reasonKind','reasonMissing','other'),T=False,I=None)
 add('missing-promotion-effect-binding',lambda m:m['predicates'].update(residuePromotionEffectBindingDeclared=[x for x in m['predicates']['residuePromotionEffectBindingDeclared'] if x[0]!='rMixedM']),T=False,I=None)
 add('missing-source-currentness',lambda m:m['predicates'].update(SourceCurrentDeclared=[]),T=False,I=None)
 add('missing-source-owner-approval',lambda m:m['predicates'].update(SourceOwnerApprovedDeclared=[]),T=False,I=None)
 add('missing-method-classification',lambda m:m['predicates'].update(FourFacetSatisfiedDeclared=[]),T=False,I=None)
 for n in ['actionInvariant','actionBinding','surfaceSchema','residueActionEffect','machineSchema']:add('malformed-output-'+n,lambda m,n=n:m['functions'][n][0].update(value='not-in-sort'),T=None,I=None,error='ill-sorted-function-result')
 add('malformed-empty-action-domain',lambda m:m['domains'].update(ActionReference=[]),T=None,I=None,error='empty-or-malformed-domain')
 add('malformed-missing-function',lambda m:m['functions'].pop('actionBinding'),T=None,I=None,error='model-signature-denominator-mismatch')
 add('malformed-duplicate-function-tuple',lambda m:m['functions']['actionBinding'].append(copy.deepcopy(m['functions']['actionBinding'][0])),T=None,I=None,error='duplicate-function-tuple')
 return rows
def mval(sort):return base_model()['domains'][sort][-1]
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
    prior=json.loads((b.BASE/'definitions/cal.definition.derived-refresh/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-FourFacetArtifactInvariant-model-controls/v1-candidate','status':'PASS-for-exact-authored-FourFacetArtifactInvariant-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Typed four-facet bind/create/residue,continuation,named checks and promotion-effect declarations checked on supplied finite models;actual creation,checks,authority,source fidelity and whole proof remain pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
