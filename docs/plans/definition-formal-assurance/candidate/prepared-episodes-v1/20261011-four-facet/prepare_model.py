"""Prepare finite four-facet controls,overlap and typed-residue witnesses."""
from pathlib import Path
import ast
p=Path(__file__).resolve().parent;dest=p/'prepared';prev=Path('docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.derived-refresh');old=(prev/'verify_candidate.py').read_text();head=old[:old.index('def refresh(')].replace('Supplied unchanged-input,generator,parity,validation and tooling models.','Supplied four-facet,surface,view and typed-residue models.')
body='''def refresh(m):
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
'''
tail=old[old.index('def qualify('):].replace('cal.definition.canonical-representation-invariant/delivery-manifest.json','cal.definition.derived-refresh/delivery-manifest.json').replace('DerivedRefresh','FourFacetArtifactInvariant').replace('Typed exact unchanged-input,generator,projection,parity,validation and tooling declarations checked on supplied finite models;actual execution,computed digests,authenticity,authority,source fidelity and whole proof remain pending.','Typed four-facet bind/create/residue,continuation,named checks and promotion-effect declarations checked on supplied finite models;actual creation,checks,authority,source fidelity and whole proof remain pending.')
code=head+body+tail;ast.parse(code)
with (dest/'verify_candidate.py').open('x') as f:f.write(code)
prior=p.with_name('20261011-derived-refresh')
for n in ['check_prepared.py','capture_precheck.py']:
 s=(prior/n).read_text().replace('cal.definition.derived-refresh','cal.definition.four-facet-artifact-invariant').replace('prepared-dr','prepared-ffa').replace("'RefreshReference'","'ActionReference'")
 with (p/n).open('x') as f:f.write(s)
print('Prepared four-facet models and exact source precheck.')
