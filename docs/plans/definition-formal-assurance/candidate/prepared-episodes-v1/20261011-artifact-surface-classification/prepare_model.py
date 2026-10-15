from pathlib import Path
import ast
root=Path.cwd();life=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.artifact-lifetime';p=Path(__file__).resolve().parent/'prepared'
code='''"""Supplied package role,self-entry and exact declared type-resolution models."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def setfn(m,n,arg,value):
 args=arg if isinstance(arg,list) else [arg];next(x for x in m['functions'][n] if x['args']==args)['value']=value
def base_model():
 ds={'PackageReference':['pPrimary','pAuthority','pOutside'],'GovernedFileReference':['fManifest','fInstance','fComponent','fGenerated','fEvidence','fFixture','fTransient','fOutside'],'SurfaceRole':['role'+n for n in b.ROLE_NAMES]+['roleOutside'],'RegistryReference':['rCurrent','rOutside'],'ArtifactTypeReference':['tManifest','tOther','tOutside'],'ArtifactTypeKey':['keyManifest','keyOther','keyOutside'],'PackageHomeReference':['hDeclared','hOutside'],'Token':['empty','reference','differentReference']}
 constants={'EMPTY':'empty','CANONICAL_MANIFEST_TYPE':'keyManifest',**{n:'role'+n for n in b.ROLE_NAMES}};role_map={'fManifest':'INSTANCE','fInstance':'INSTANCE','fComponent':'COMPONENT','fGenerated':'GENERATED','fEvidence':'EVIDENCE','fFixture':'FIXTURE','fTransient':'TRANSIENT'};maps={'packageHome':lambda p:'hOutside' if p=='pOutside' else 'hDeclared','packageRegistry':lambda p:'rOutside' if p=='pOutside' else 'rCurrent','packageManifestFile':lambda p:'fOutside' if p=='pOutside' else 'fManifest','selectedRole':lambda p,f:'roleOutside' if p=='pOutside' or f=='fOutside' else 'role'+role_map[f],'selectedResolvedType':lambda p,f:'tManifest' if f=='fManifest' else 'tOther' if f!='fOutside' else 'tOutside','typeKey':lambda t:'key'+t[1:]}
 for s,n in b.HANDLES.items():maps[n]=lambda x:'reference'
 assert maps.keys()==b.FUNCTIONS.keys();functions={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(ds[s] for s in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};predicates={n:[] for n in b.SIGNATURE}
 predicates['PackageApplicable']=[['pPrimary'],['pAuthority']];predicates['PackageInScopeDeclared']=copy.deepcopy(predicates['PackageApplicable'])
 for s in b.SORTS:
  if s not in ['PackageReference','Token']:predicates[s+'Declared']=[[x] for x in ds[s][:-1]]
 governed=[['pPrimary',f] for f in ds['GovernedFileReference'][:-1]]+[['pAuthority','fManifest']]
 predicates.update(CanonicalPackageHomeDeclared=[[p,'hDeclared'] for p in ['pPrimary','pAuthority']],GovernedDeclared=governed,RoleAssignmentDeclared=[[p,f,maps['selectedRole'](p,f)] for p,f in governed],CanonicalSubjectDeclared=[['pPrimary','fManifest'],['pPrimary','fInstance'],['pAuthority','fManifest']],ManifestSelfEntryDeclared=[[p,'fManifest'] for p in ['pPrimary','pAuthority']],ArtifactTypeAdmittedDeclared=[['rCurrent','tManifest'],['rCurrent','tOther']],ResolvedTypeDeclared=[['rCurrent','fManifest','tManifest'],['rCurrent','fInstance','tOther']],SurfaceActualAuthority=[['pAuthority']])
 return {'domains':ds,'constants':constants,'functions':functions,'predicates':predicates}
def controls():
 rows=[]
 def add(id,mutate,T=True,I=None,error=None):
  m=base_model();mutate(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('six-explicit-roles-self-entry-one-resolved-type-and-independent-authority',lambda m:None,I=True)
 for n in b.ACTUAL:
  if n=='Authority':continue
  add('independently-supported-actual-'+n,lambda m,n=n:m['predicates']['SurfaceActual'+n].append(['pAuthority']),I=True)
 add('selected-empty-package-handle',lambda m:setfn(m,b.HANDLES['PackageReference'],'pPrimary','empty'),T=False)
 add('outside-empty-package-handle',lambda m:setfn(m,b.HANDLES['PackageReference'],'pOutside','empty'),I=True)
 for n,s,value in [('packageHome','PackageHomeReference','hDeclared'),('packageRegistry','RegistryReference','rCurrent'),('packageManifestFile','GovernedFileReference','fManifest')]:
  add('missing-package-facet-'+n,lambda m,s=s,value=value:m['predicates'][s+'Declared'].remove([value]),T=False)
  add('empty-package-facet-'+n,lambda m,s=s,value=value:setfn(m,b.HANDLES[s],value,'empty'),T=False)
 add('package-scope-disagreement',lambda m:m['predicates']['PackageInScopeDeclared'].remove(['pPrimary']),T=False)
 add('package-home-qualification-not-declared',lambda m:m['predicates']['CanonicalPackageHomeDeclared'].remove(['pPrimary','hDeclared']),T=False)
 add('manifest-self-entry-marker-absent',lambda m:m['predicates']['ManifestSelfEntryDeclared'].remove(['pPrimary','fManifest']),T=False)
 add('manifest-omitted-from-governed-files',lambda m:m['predicates']['GovernedDeclared'].remove(['pPrimary','fManifest']),T=False)
 add('manifest-is-not-canonical-instance-role',lambda m:setfn(m,'selectedRole',['pPrimary','fManifest'],'roleCOMPONENT'),T=False)
 add('manifest-wrong-exact-type-key',lambda m:setfn(m,'typeKey','tManifest','keyOther'),T=False)
 add('manifest-wrong-nominated-type',lambda m:setfn(m,'selectedResolvedType',['pPrimary','fManifest'],'tOther'),T=False)
 for n in b.ROLE_NAMES:
  add('recognized-role-not-declared-'+n,lambda m,n=n:m['predicates']['SurfaceRoleDeclared'].remove(['role'+n]),T=False)
 for n in b.ROLE_NAMES[1:]:add('role-constant-collapsed-'+n,lambda m,n=n:m['constants'].update({n:'roleINSTANCE'}),T=False)
 add('unknown-seventh-role-declared',lambda m:m['predicates']['SurfaceRoleDeclared'].append(['roleOutside']),T=False)
 add('unknown-role-selected',lambda m:setfn(m,'selectedRole',['pPrimary','fComponent'],'roleOutside'),T=False)
 for f in base_model()['domains']['GovernedFileReference'][:-1]:
  role=next(x[2] for x in base_model()['predicates']['RoleAssignmentDeclared'] if x[:2]==['pPrimary',f])
  add('missing-explicit-role-assignment-'+f,lambda m,f=f,role=role:m['predicates']['RoleAssignmentDeclared'].remove(['pPrimary',f,role]),T=False)
 add('two-distinct-explicit-role-assignments',lambda m:m['predicates']['RoleAssignmentDeclared'].append(['pPrimary','fComponent','roleGENERATED']),T=False)
 add('changed-role-function-without-exact-declaration',lambda m:setfn(m,'selectedRole',['pPrimary','fComponent'],'roleGENERATED'),T=False)
 for f in ['fComponent','fGenerated','fEvidence','fFixture','fTransient']:add('noncanonical-role-claims-canonical-subject-'+f,lambda m,f=f:m['predicates']['CanonicalSubjectDeclared'].append(['pPrimary',f]),T=False)
 for f in ['fManifest','fInstance']:add('canonical-instance-subject-marker-missing-'+f,lambda m,f=f:m['predicates']['CanonicalSubjectDeclared'].remove(['pPrimary',f]),T=False)
 for t in ['tManifest','tOther']:
  add('canonical-type-ref-not-declared-'+t,lambda m,t=t:m['predicates']['ArtifactTypeReferenceDeclared'].remove([t]),T=False)
  add('canonical-type-admission-not-declared-'+t,lambda m,t=t:m['predicates']['ArtifactTypeAdmittedDeclared'].remove(['rCurrent',t]),T=False)
 add('canonical-type-empty-handle',lambda m:setfn(m,b.HANDLES['ArtifactTypeReference'],'tOther','empty'),T=False)
 add('canonical-type-key-not-declared',lambda m:m['predicates']['ArtifactTypeKeyDeclared'].remove(['keyManifest']),T=False)
 add('canonical-type-key-empty-handle',lambda m:setfn(m,b.HANDLES['ArtifactTypeKey'],'keyManifest','empty'),T=False)
 add('missing-canonical-type-resolution',lambda m:m['predicates']['ResolvedTypeDeclared'].remove(['rCurrent','fInstance','tOther']),T=False)
 add('two-distinct-canonical-type-results',lambda m:m['predicates']['ResolvedTypeDeclared'].append(['rCurrent','fInstance','tManifest']),T=False)
 add('unknown-nominated-canonical-type',lambda m:setfn(m,'selectedResolvedType',['pPrimary','fInstance'],'tOutside'),T=False)
 add('changed-nominee-without-corresponding-resolution',lambda m:setfn(m,'selectedResolvedType',['pPrimary','fInstance'],'tManifest'),T=False)
 def changed_registry(m,complete):
  m['predicates']['RegistryReferenceDeclared'].append(['rOutside']);setfn(m,'packageRegistry','pPrimary','rOutside')
  if complete:
   m['predicates']['ArtifactTypeAdmittedDeclared'] += [['rOutside',t] for t in ['tManifest','tOther']];m['predicates']['ResolvedTypeDeclared'] += [['rOutside','fManifest','tManifest'],['rOutside','fInstance','tOther']]
 add('changed-registry-without-exact-resolution-and-admission',lambda m:changed_registry(m,False),T=False)
 add('changed-registry-with-exact-declared-correspondence',lambda m:changed_registry(m,True),I=True)
 add('type-reference-key-injectivity-not-invented',lambda m:setfn(m,'typeKey','tOther','keyManifest'),I=True)
 add('selected-transient-canonical-dependency-is-rejected',lambda m:m['predicates']['CanonicalDependencyDeclared'].append(['pPrimary','fTransient']),T=False)
 add('nontransient-dependency-declaration-is-not-actual-satisfaction',lambda m:m['predicates']['CanonicalDependencyDeclared'].append(['pPrimary','fEvidence']),I=True)
 add('outside-transient-dependency-unconstrained',lambda m:m['predicates']['CanonicalDependencyDeclared'].append(['pOutside','fTransient']),I=True)
 add('outside-file-canonical-subject-claim-outside-selected-membership',lambda m:m['predicates']['CanonicalSubjectDeclared'].append(['pPrimary','fOutside']),I=True)
 add('outside-file-handle-can-be-empty',lambda m:setfn(m,b.HANDLES['GovernedFileReference'],'fOutside','empty'),I=True)
 add('file-handle-change-does-not-determine-role',lambda m:setfn(m,b.HANDLES['GovernedFileReference'],'fComponent','differentReference'),I=True)
 add('unselected-registry-extra-resolution-does-not-affect-selected-one',lambda m:m['predicates']['ResolvedTypeDeclared'].append(['rOutside','fInstance','tOutside']),I=True)
 add('role-result-is-an-artifact-type',lambda m:setfn(m,'selectedRole',['pPrimary','fManifest'],'tManifest'),error='ill-sorted-function-result')
 add('missing-symbol',lambda m:m['predicates'].pop('GovernedDeclared'),error='model-signature-denominator-mismatch')
 add('nontotal-role-function',lambda m:m['functions']['selectedRole'].pop(),error='nontotal-function')
 add('ill-sorted-manifest-type-constant',lambda m:m['constants'].update(CANONICAL_MANIFEST_TYPE='fManifest'),error='ill-sorted-constant')
 add('wrong-resolution-arity',lambda m:m['predicates'].update(ResolvedTypeDeclared=[['rCurrent','fManifest']]),error='ill-sorted-model-tuple')
 add('duplicate-governed-tuple',lambda m:m['predicates']['GovernedDeclared'].append(['pPrimary','fManifest']),error='duplicate-predicate-tuple')
 add('empty-role-domain',lambda m:m['domains'].update(SurfaceRole=[]),error='empty-or-malformed-domain')
 add('duplicate-function-tuple',lambda m:m['functions']['selectedRole'].append(copy.deepcopy(m['functions']['selectedRole'][0])),error='duplicate-function-tuple')
 return rows
'''
tail='def qualify(model,ids):'+(life/'verify_candidate.py').read_text().split('def qualify(model,ids):',1)[1];tail=tail.replace('cal.definition.artifact/delivery-manifest.json','cal.definition.artifact-lifetime/delivery-manifest.json').replace('ArtifactLifetime-model-controls','ArtifactSurface-model-controls').replace('authored-ArtifactLifetime-models','authored-ArtifactSurface-models');tail=tail.replace('Typed lifespan,kind defaults,owner-noted overrides and scoped live,historical,quoted assertion declarations checked on supplied models. Actual preservation,truth,chronology,override authority,owner fidelity and consumer alignment remain pending.','Typed package roles,explicit role assignments,manifest self-entry and unique declared type resolution checked on supplied models. Actual enumeration,classification,resolution,admission,canonical-subject legitimacy,Conformance,owner fidelity and consumer alignment remain pending.')
code+=tail;ast.parse(code);q=p/'verify_candidate.py';assert not q.exists();q.write_text(code);print('Surface authored models and meaningful structural/guard controls prepared; not a native proof or unit.')
