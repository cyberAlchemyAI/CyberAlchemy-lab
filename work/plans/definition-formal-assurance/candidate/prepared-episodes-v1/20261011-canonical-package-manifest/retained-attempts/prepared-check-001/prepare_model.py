from pathlib import Path
import ast
p=Path(__file__).resolve().parent;dest=p/'prepared';prev=Path('docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.canonical-package-home');old=(prev/'verify_candidate.py').read_text();head=old[:old.index('def getfn(')]
body='''def getfn(m,n,*args):return next(x['value'] for x in m['functions'][n] if x['args']==list(args))
def refresh(m):
 p=m['predicates'];g=lambda n,x:getfn(m,n,x)
 for n in b.CHANGE_FIELDS:p[n+'BindingDeclared']=[[x[0],g(n,x[0])] for x in p['ChangeInScopeDeclared']]
 p['EntryRoleDeclared']=[[x[0],g('entryRole',x[0])] for x in p['EntryInScopeDeclared']]
def base_model():
 ds={s:[] for s in b.SORTS};ds.update(ManifestReference=['manifestMain','manifestChild','manifestOutside'],HomeReference=['homeMain','homeChild','homeOutside'],AggregateReference=['aggregateMain','aggregateChild','aggregateOutside'],OwnerReference=['ownerMain','ownerChild','ownerOutside'],UnitReference=['unitMain','unitChild','unitOutside'],RecoveryReference=['recoveryMain','recoveryChild','recoveryOutside'],SurfaceReference=['surface'+str(i) for i in range(9)],EntryReference=['entry'+str(i) for i in range(10)],SurfaceRole=['role'+n for n in b.ROLE_NAMES]+['roleFuture','roleOutside'],TypeReference=['manifestType','documentType','noType','changedType','outsideType'],CarrierReference=['carrier'+str(i) for i in range(9)],ResultReference=['result'+str(i) for i in range(9)]+['resultExtra'],RegistryReference=['registryMain','registryOutside'],NestedReference=['nestedChild','nestedOutside'],RelationReference=['relationChild','relationOutside'],DirectoryReference=['directoryFacet','directoryOutside'],SemanticIdentity=['id'+str(i) for i in range(9)]+['idChanged'],ChangeReference=['changeMain','changeOutside'],PathToken=['packageSelf']+['path'+str(i) for i in range(9)]+['pathMoved','pathOutside'],Token=['empty','none','one','reference'])
 cs={'EMPTY':'empty','NONE':'none','ONE':'one','MANIFEST_TYPE':'manifestType','NO_TYPE':'noType','PACKAGE_SELF':'packageSelf',**{n:'role'+n for n in b.ROLE_NAMES}}
 ix=lambda x:int(''.join(c for c in x if c.isdigit()))
 suffix=lambda x,p:x[len(p):]
 sowner=lambda x:'Main' if ix(x)<7 else 'Child' if ix(x)==7 else 'Outside'
 es=lambda e:'surface'+str(ix(e) if ix(e)<9 else 0)
 erole=lambda e:'roleCANONICAL' if ix(e) in [0,1,7] else 'role'+b.ROLE_NAMES[ix(e)-1] if 2<=ix(e)<=6 else 'roleOutside'
 stype=lambda s:'manifestType' if ix(s) in [0,7] else 'documentType' if ix(s)==1 else 'noType'
 maps={n:(lambda m,n=n,s=s:'none' if n=='manifestEffect' else 'surface0' if n=='manifestSelf' and m=='manifestMain' else 'surface7' if n=='manifestSelf' and m=='manifestChild' else 'surface8' if n=='manifestSelf' else {'manifestHome':'home','manifestAggregate':'aggregate','manifestOwner':'owner','manifestUnit':'unit','manifestRecovery':'recovery'}[n]+suffix(m,'manifest')) for n,s in b.FACETS.items()}
 maps.update({n:(lambda h,n=n:n[len('home'):].lower()+suffix(h,'home')) for n in b.HOME_FIELDS})
 maps.update(entryManifest=lambda e:'manifest'+sowner(es(e)),entrySurface=es,entryRole=erole,entryType=lambda e:stype(es(e)),entryResult=lambda e:'result'+str(ix(e) if ix(e)<9 else 0),entryCount=lambda e:'one' if ix(e) in [0,1,7] else 'none',entryPath=lambda e:'packageSelf' if ix(e) in [0,7] else 'path'+str(ix(e) if ix(e)<9 else 0))
 maps.update(surfaceHome=lambda s:'home'+sowner(s),surfaceOwner=lambda s:'owner'+sowner(s),surfaceRecovery=lambda s:'recovery'+sowner(s),surfaceIdentity=lambda s:'id'+str(ix(s)),surfaceType=stype,surfaceCarrier=lambda s:'carrier'+str(ix(s)),resultCarrier=lambda r:'carrier'+str(ix(r)) if r!='resultExtra' else 'carrier1',resultType=lambda r:stype('surface'+str(ix(r))) if r!='resultExtra' else 'documentType',resultRegistry=lambda r:'registryMain',carrierIdentity=lambda c:'id'+str(ix(c)),carrierType=lambda c:stype('surface'+str(ix(c))),nestedParent=lambda n:'manifestMain' if n=='nestedChild' else 'manifestOutside',nestedManifest=lambda n:'manifestChild' if n=='nestedChild' else 'manifestOutside',nestedRelation=lambda n:'relationChild' if n=='nestedChild' else 'relationOutside',relationParent=lambda r:'manifestMain' if r=='relationChild' else 'manifestOutside',relationChild=lambda r:'nestedChild' if r=='relationChild' else 'nestedOutside',directoryNearest=lambda d:'manifestMain' if d=='directoryFacet' else 'manifestOutside')
 maps.update(changeSurface=lambda ch:'surface1' if ch=='changeMain' else 'surface8',changeBeforeIdentity=lambda ch:'id1' if ch=='changeMain' else 'id8',changeAfterIdentity=lambda ch:'id1' if ch=='changeMain' else 'id8',changeBeforeType=lambda ch:'documentType' if ch=='changeMain' else 'noType',changeAfterType=lambda ch:'documentType' if ch=='changeMain' else 'noType',changeBeforePath=lambda ch:'path1' if ch=='changeMain' else 'pathOutside',changeAfterPath=lambda ch:'pathMoved' if ch=='changeMain' else 'pathOutside')
 for s,n in b.HANDLES.items():maps[n]=lambda x:'reference'
 assert maps.keys()==b.FUNCTIONS.keys();functions={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(ds[s] for s in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};p={n:[] for n in b.SIGNATURE}
 for s in b.SORTS:
  if s not in ['ManifestReference','Token']:p[s+'Declared']=[[x] for x in ds[s] if not x.endswith('Outside') and x not in ['surface8','entry8','carrier8','result8','id8','path8','outsideType']]
 manifests=['manifestMain','manifestChild'];entries=['entry'+str(i) for i in range(8)]
 p['ManifestApplicable']=p['ManifestInScopeDeclared']=[[m] for m in manifests]
 for n in b.FACETS:p[n+'BindingDeclared']=[[m,maps[n](m)] for m in manifests]
 p['EntryInScopeDeclared']=[[e] for e in entries];p['GovernedDeclared']=[[maps['entrySurface'](e),maps['surfaceHome'](maps['entrySurface'](e))] for e in entries];p['EntryForDeclared']=[[maps['entryManifest'](e),maps['entrySurface'](e),e] for e in entries];p['SelfEntryDeclared']=[['manifestMain','entry0'],['manifestChild','entry7']]
 p['CanonicalCarrierDeclared']=[['surface'+str(i)] for i in [0,1,7]];p['AdmittedResolutionDeclared']=[['surface'+str(i),'result'+str(i)] for i in [0,1,7]];p['ResultAdmittedDeclared']=[['result'+str(i)] for i in [0,1,7]];p['NestedInScopeDeclared']=[['nestedChild']];p['IndependentLifecycleDeclared']=[['nestedChild']];p['NestedParentDeclared']=[['manifestMain','nestedChild','relationChild']];p['OwnManifestDeclared']=[['nestedChild','manifestChild']];p['DirectoryInScopeDeclared']=[['directoryFacet']];p['DirectoryWithoutOwnManifestDeclared']=[['directoryFacet']];p['NearestPackageDeclared']=[['directoryFacet','manifestMain']];p['DirectoryFacetOfDeclared']=[['directoryFacet','manifestMain']];p['ChangeInScopeDeclared']=[['changeMain']];p['ManifestActualAuthority']=[['manifestChild']]
 model={'domains':ds,'constants':cs,'functions':functions,'predicates':p};refresh(model);return model
def controls():
 rows=[]
 def add(name,mutation=lambda m:None,T=True,I=True,error=None):
  m=base_model();mutation(m);rows.append({'case_id':name,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 def change(m,n,arg,val):setfn(m,n,arg,val);refresh(m)
 add('exact-self-membership-roles-resolution-child-directory-and-change')
 add('no-applicable-manifests',lambda m:m['predicates'].update(ManifestApplicable=[],ManifestInScopeDeclared=[],EntryInScopeDeclared=[],NestedInScopeDeclared=[],DirectoryInScopeDeclared=[],ChangeInScopeDeclared=[]),I=False)
 add('no-independent-child-population',lambda m:m['predicates'].update(IndependentLifecycleDeclared=[]),I=False)
 add('no-unmanifested-directory-population',lambda m:m['predicates'].update(DirectoryWithoutOwnManifestDeclared=[]),I=False)
 add('no-membership-change-population',lambda m:m['predicates'].update(ChangeInScopeDeclared=[]),I=False)
 add('future-role-not-global-vocabulary-error',lambda m:change(m,'entryRole','entry2','roleFuture'),I=False)
 add('outside-directory-inference-not-scoped',lambda m:m['predicates']['DirectoryMembershipInferenceDeclared'].append(['manifestOutside']))
 add('outside-resolution-not-scoped',lambda m:m['predicates']['AdmittedResolutionDeclared'].append(['surface8','resultExtra']))
 add('membership-change-may-keep-same-path',lambda m:change(m,'changeAfterPath','changeMain','path1'),I=False)
 for n in b.ACTUAL:add('independently-supported-actual-'+n,lambda m,n=n:m['predicates']['ManifestActual'+n].append(['manifestMain']),I=False)
 for n in b.EXCLUDED:add('prohibited-'+n,lambda m,n=n:m['predicates'][n].append(['manifestMain']),T=False,I=None)
 for n,s in b.FACETS.items():
  add('missing-binding-'+n,lambda m,n=n:m['predicates'].update({n+'BindingDeclared':m['predicates'][n+'BindingDeclared'][1:]}),T=False,I=None)
  if s!='Token':add('conflicting-binding-'+n,lambda m,n=n,s=s:m['predicates'][n+'BindingDeclared'].append(['manifestMain',m['domains'][s][-1]]),T=False,I=None)
 for n,val in [('homeOwner','ownerChild'),('homeUnit','unitChild'),('homeRecovery','recoveryChild'),('homeAggregate','aggregateChild')]:add('home-field-mismatch-'+n,lambda m,n=n,val=val:setfn(m,n,'homeMain',val),T=False,I=None)
 add('unwitnessed-governed-surface',lambda m:m['predicates']['GovernedDeclared'].append(['surface8','homeMain']),T=False,I=None)
 add('missing-governed-membership-relation',lambda m:m['predicates'].update(EntryForDeclared=m['predicates']['EntryForDeclared'][1:]),T=False,I=None)
 add('hidden-duplicate-entry-for-one-surface',lambda m:(m['predicates']['EntryInScopeDeclared'].append(['entry9']),m['predicates']['EntryForDeclared'].append(['manifestMain','surface0','entry9']),setfn(m,'entryRole','entry9','roleCANONICAL'),setfn(m,'entryCount','entry9','one'),refresh(m)),T=False,I=None)
 add('duplicate-path-distinct-surfaces',lambda m:setfn(m,'entryPath','entry2','path1'),T=False,I=None)
 add('duplicate-role-relation',lambda m:m['predicates']['EntryRoleDeclared'].append(['entry2','roleFIXTURE']),T=False,I=None)
 add('missing-self-entry-relation',lambda m:m['predicates'].update(SelfEntryDeclared=[['manifestChild','entry7']]),T=False,I=None)
 add('self-entry-wrong-path',lambda m:setfn(m,'entryPath','entry0','path0'),T=False,I=None)
 add('self-entry-wrong-type',lambda m:setfn(m,'entryType','entry0','documentType'),T=False,I=None)
 add('self-entry-wrong-role',lambda m:change(m,'entryRole','entry0','roleCOMPONENT'),T=False,I=None)
 add('self-entry-wrong-count',lambda m:setfn(m,'entryCount','entry0','none'),T=False,I=None)
 add('canonical-count-one-hides-extra-result',lambda m:m['predicates']['AdmittedResolutionDeclared'].append(['surface1','resultExtra']),T=False,I=None)
 add('missing-admitted-result',lambda m:m['predicates'].update(AdmittedResolutionDeclared=[['surface0','result0'],['surface7','result7']]),T=False,I=None)
 add('unadmitted-candidate-result',lambda m:m['predicates'].update(ResultAdmittedDeclared=[['result0'],['result7']]),T=False,I=None)
 add('result-wrong-input-carrier',lambda m:setfn(m,'resultCarrier','result1','carrier0'),T=False,I=None)
 add('result-wrong-type',lambda m:setfn(m,'resultType','result1','manifestType'),T=False,I=None)
 add('result-unbound-registry',lambda m:setfn(m,'resultRegistry','result1','registryOutside'),T=False,I=None)
 add('canonical-carrier-identity-mismatch',lambda m:setfn(m,'carrierIdentity','carrier1','id2'),T=False,I=None)
 add('canonical-carrier-type-mismatch',lambda m:setfn(m,'carrierType','carrier1','manifestType'),T=False,I=None)
 add('component-claims-canonical-type',lambda m:setfn(m,'entryType','entry2','documentType'),T=False,I=None)
 add('nested-independent-without-own-manifest',lambda m:m['predicates'].update(OwnManifestDeclared=[]),T=False,I=None)
 add('nested-independent-parent-as-own-manifest',lambda m:(setfn(m,'nestedManifest','nestedChild','manifestMain'),m['predicates'].update(OwnManifestDeclared=[['nestedChild','manifestMain']])),T=False,I=None)
 add('nested-missing-parent-relation',lambda m:m['predicates'].update(NestedParentDeclared=[]),T=False,I=None)
 add('nested-relation-wrong-child',lambda m:setfn(m,'relationChild','relationChild','nestedOutside'),T=False,I=None)
 add('nearest-directory-missing-declaration',lambda m:m['predicates'].update(NearestPackageDeclared=[]),T=False,I=None)
 add('nearest-directory-conflicting-facet',lambda m:m['predicates']['DirectoryFacetOfDeclared'].append(['directoryFacet','manifestChild']),T=False,I=None)
 add('nearest-directory-unselected-package',lambda m:setfn(m,'directoryNearest','directoryFacet','manifestOutside'),T=False,I=None)
 for n,val in [('changeAfterIdentity','idChanged'),('changeAfterType','changedType')]:add('membership-changes-'+n,lambda m,n=n,val=val:change(m,n,'changeMain',val),T=False,I=None)
 add('change-before-does-not-bind-artifact',lambda m:change(m,'changeBeforeIdentity','changeMain','idChanged'),T=False,I=None)
 add('change-binding-missing',lambda m:m['predicates'].update(changeAfterIdentityBindingDeclared=[]),T=False,I=None)
 for n in ['manifestHome','entryRole','resultCarrier','nestedManifest','changeAfterType']:add('malformed-output-'+n,lambda m,n=n:m['functions'][n][0].update(value='not-in-sort'),T=None,I=None,error='sort-mismatch')
 add('malformed-empty-entry-domain',lambda m:m['domains'].update(EntryReference=[]),T=None,I=None,error='empty-sort-domain')
 add('malformed-missing-function',lambda m:m['functions'].pop('entrySurface'),T=None,I=None,error='missing-function')
 add('malformed-duplicate-function-tuple',lambda m:m['functions']['entrySurface'].append(copy.deepcopy(m['functions']['entrySurface'][0])),T=None,I=None,error='duplicate-function-tuple')
 return rows
'''
tail=old[old.index('def qualify('):].replace('cal.definition.artifact-type-resolution/delivery-manifest.json','cal.definition.canonical-package-home/delivery-manifest.json').replace('CanonicalPackageHome','CanonicalPackageManifest')
tail=tail.replace('Typed declared owner/unit/home,carrier uniqueness,manifest fields,distinct facets,typed edges,reference-only views and movement invariance checked on supplied finite models. Actual ownership,canonical source correctness,migration,consumer alignment and whole fidelity remain pending.','Typed exact manifest membership,self-entry,roles,admitted-result declarations,independent nesting,nearest-directory facets and artifact-preservation checked on supplied finite models;actual correspondence,execution,authority and whole proof remain pending.')
code=head+body+tail;ast.parse(code)
with (dest/'verify_candidate.py').open('x') as f:f.write(code)
print('Prepared CPM finite models and hostile controls;no native unit created.')
