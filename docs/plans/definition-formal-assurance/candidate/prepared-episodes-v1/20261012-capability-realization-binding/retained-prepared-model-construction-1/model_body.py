import copy,itertools,json
import build_candidate as b
import verifier as v
def load(name):return json.loads((b.UNIT/name).read_bytes())
def getfn(m,n,arg):return next(x['value'] for x in m['functions'][n] if x['args']==[arg])
def setfn(m,n,arg,value):next(x for x in m['functions'][n] if x['args']==[arg])['value']=value
def refresh(m):
 for fields,carrier in b.GROUPS:
  for name in fields:m['predicates'][name+'BindingDeclared']=[[x['args'][0],x['value']] for x in m['functions'][name]]
 selected=[x[0] for x in m['predicates']['BindingApplicable']]
 m['predicates']['BindingImplementationMemberDeclared']=[[binding,member] for binding in selected for collection,member in m['predicates']['ImplementationCollectionContainsDeclared'] if collection==getfn(m,'bindingImplementationRevisions',binding)]
 m['predicates']['CanonicalAuthorityForAssociationDeclared']=[list(x) for x in sorted({(getfn(m,'bindingAssociation',binding),getfn(m,'bindingCanonicalAuthority',binding)) for binding in selected})]
 m['predicates']['ProjectionForBindingDeclared']=[[binding,getfn(m,'bindingProjection',binding)] for binding in selected if [binding] in m['predicates']['BindingHasProjectionDeclared']]
 m['predicates']['EvidenceForPurposeDeclared']=[[binding,m['constants'][role+'_ROLE'],getfn(m,field,binding)] for binding in selected for role,field in b.EVIDENCE_FIELDS.items()]
def base_model():
 ds={sort:[sort[0].lower()+sort[1:]+'0',sort[0].lower()+sort[1:]+'1',sort[0].lower()+sort[1:]+'Outside'] for sort in b.SORTS}
 ds.update(BindingRevisionReference=['b0','b1','b2','b3','b4','b5','bUnused','bOutside'],CapabilityRevisionReference=['cap0','cap1','capUnused','capOutside'],ImplementationCollectionReference=['col0','colMulti','colAlias','col3','colUnused','colOutside'],ImplementationRevisionReference=['im0','im1','im2','imUnused','imOutside'],AdoptionPostureReference=['posture0','posture1','postureOutside'],AssociationReference=['assoc0','assocUnused','assocOutside'],CanonicalAuthorityReference=['auth0','auth1','authOutside'],EvidenceCollectionReference=['eShared','eSeparate','eOutside'],EvidenceRoleReference=['adoptionRole','conformanceRole','deploymentRole','outcomeRole','roleOutside'],ProjectionReference=['p0','p1','pUnused','pOutside'],DigestReference=['digest0','digest1','digestUnused','digestOutside'],ChangeReference=['cCap','cImpl','cPosture','cSame','cOutside'],Token=['empty','ref','other'])
 maps={}
 def table(name,values):maps[name]=lambda x:values.get(x,ds[b.FUNCTIONS[name][1]][-1])
 bindings=['b'+str(i) for i in range(6)]
 for name,sort in b.FIELDS.items():table(name,{x:ds[sort][i%(len(ds[sort])-1)] for i,x in enumerate(bindings)})
 table('bindingCapabilityRevision',{'b0':'cap0','b1':'cap1','b2':'cap0','b3':'cap0','b4':'cap1','b5':'cap0'})
 table('bindingImplementationRevisions',{'b0':'col0','b1':'colMulti','b2':'colAlias','b3':'col3','b4':'col0','b5':'col0'})
 table('bindingAdoptionPosture',{x:'posture1' if x in ['b1','b5'] else 'posture0' for x in bindings})
 for name in ['bindingConformanceEvidence','bindingAdoptionEvidence','bindingDeploymentEvidence','bindingOutcomeEvidence']:table(name,{x:'eShared' for x in bindings})
 table('bindingAssociation',{x:'assoc0' for x in bindings});table('bindingCanonicalAuthority',{x:'auth0' for x in bindings})
 table('bindingProjection',{'b1':'p0','b2':'p1'});table('bindingDigest',{'b1':'digest0','b2':'digest1'})
 table('associationCanonicalAuthority',{'assoc0':'auth0','assocUnused':'auth1'})
 table('projectionBinding',{'p0':'b1','p1':'b2'});table('projectionAssociation',{'p0':'assoc0','p1':'assoc0'});table('projectionDigest',{'p0':'digest0','p1':'digest1'})
 table('changeOriginalBinding',{x:'b0' for x in ['cCap','cImpl','cPosture','cSame']})
 table('changeDesiredCapability',{'cCap':'cap1','cImpl':'cap0','cPosture':'cap0','cSame':'cap0'})
 table('changeDesiredImplementations',{'cCap':'col0','cImpl':'col3','cPosture':'col0','cSame':'colAlias'})
 table('changeDesiredAdoptionPosture',{'cCap':'posture0','cImpl':'posture0','cPosture':'posture1','cSame':'posture0'})
 table('changeSuccessorBinding',{'cCap':'b4','cImpl':'b3','cPosture':'b5'})
 for sort,name in b.HANDLES.items():maps[name]=lambda x:'ref'
 assert set(maps)==set(b.FUNCTIONS)
 funcs={name:[{'args':list(args),'value':maps[name](*args)} for args in itertools.product(*(ds[sort] for sort in sorts))] for name,(sorts,result) in b.FUNCTIONS.items()}
 predicates={name:[] for name in b.SIGNATURE}
 for sort in b.SORTS:
  if sort!='Token':predicates[sort+'Declared']=[[x] for x in ds[sort] if not x.endswith('Outside')]
 for name in ['BindingApplicable','BindingInScopeDeclared','BindingLifecycleBearingDeclared','BindingCanonicalAssociationDeclared','BindingGovernedDeclared','BindingBoundedDeclared']:predicates[name]=[[x] for x in bindings]
 predicates['BindingHasProjectionDeclared']=[['b1'],['b2']]
 for name in ['ProjectionApplicable','ProjectionInScopeDeclared','ProjectionReadOnlyDeclared']:predicates[name]=[['p0'],['p1']]
 for name in ['ChangeApplicable','ChangeInScopeDeclared']:predicates[name]=[[x] for x in ['cCap','cImpl','cPosture','cSame']]
 predicates['CapabilityRevisionExactDeclared']=[[x] for x in ['cap0','cap1','capUnused']]
 predicates['ImplementationRevisionExactDeclared']=[[x] for x in ['im0','im1','im2','imUnused']]
 predicates['ImplementationCollectionContainsDeclared']=[['col0','im0'],['colMulti','im0'],['colMulti','im1'],['colAlias','im0'],['col3','im2']]
 predicates['SuccessorBindingRevisionDeclared']=[['b0','b4'],['b0','b3'],['b0','b5']]
 predicates['BindingActualAuthorityEffect']=[['b5']];predicates['BindingActualConformance']=[['b2']]
 constants={'EMPTY':'empty','ADOPTION_ROLE':'adoptionRole','CONFORMANCE_ROLE':'conformanceRole','DEPLOYMENT_ROLE':'deploymentRole','OUTCOME_ROLE':'outcomeRole'}
 m={'domains':ds,'constants':constants,'functions':funcs,'predicates':predicates};refresh(m);return m
def controls():
 rows=[]
 def add(name,mutate=lambda m:None,T=True,I=True,error=None):
  m=base_model();mutate(m);rows.append({'case_id':name,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 def change(m,name,arg,value):setfn(m,name,arg,value);refresh(m)
 add('exact-association-members-authority-evidence-projection-and-changes')
 def empty_scope(m):
  for name in ['BindingApplicable','BindingInScopeDeclared','ProjectionApplicable','ProjectionInScopeDeclared','ChangeApplicable','ChangeInScopeDeclared']:m['predicates'][name]=[]
  refresh(m)
 add('no-selected-bindings-projections-or-changes',empty_scope,I=False)
 add('no-independent-authority-effect-population',lambda m:m['predicates'].update(BindingActualAuthorityEffect=[]),I=False)
 add('no-conformance-population',lambda m:m['predicates'].update(BindingActualConformance=[]),I=False)
 def no_projection(m):
  for name in ['BindingHasProjectionDeclared','ProjectionApplicable','ProjectionInScopeDeclared']:m['predicates'][name]=[]
  refresh(m)
 add('optional-projections-all-absent',no_projection,I=False)
 add('no-selected-changes',lambda m:m['predicates'].update(ChangeApplicable=[],ChangeInScopeDeclared=[]),I=False)
 def single_only(m):m['predicates']['ImplementationCollectionContainsDeclared'].remove(['colMulti','im1']);refresh(m)
 add('all-endpoint-collections-singleton',single_only,I=False)
 def distinct_evidence(m):
  for x in ['b'+str(i) for i in range(6)]:setfn(m,'bindingConformanceEvidence',x,'eSeparate')
  refresh(m)
 add('separate-evidence-contents-permitted',distinct_evidence,I=False)
 for prefix,outcomes,subject in [('Binding',b.ACTUAL,'b3'),('Projection',b.PROJECTION_ACTUAL,'p1'),('Change',b.CHANGE_ACTUAL,'cPosture')]:
  for n in outcomes:add('independently-supported-'+prefix+'Actual'+n,lambda m,n=n,prefix=prefix,subject=subject:m['predicates'][prefix+'Actual'+n].append([subject]))
 for n in b.EXCLUDED:
  add('selected-excluded-'+n,lambda m,n=n:m['predicates'][n].append(['b0']),T=False,I=None)
  add('outside-excluded-'+n,lambda m,n=n:m['predicates'][n].append(['bOutside']))
 for n in ['BindingLifecycleBearingDeclared','BindingCanonicalAssociationDeclared','BindingGovernedDeclared','BindingBoundedDeclared']:
  add('missing-'+n,lambda m,n=n:m['predicates'][n].remove(['b0']),T=False,I=None)
 add('capability-revision-not-declared-exact',lambda m:m['predicates']['CapabilityRevisionExactDeclared'].remove(['cap0']),T=False,I=None)
 add('implementation-revision-not-declared-exact',lambda m:m['predicates']['ImplementationRevisionExactDeclared'].remove(['im0']),T=False,I=None)
 def empty_members(m):m['predicates']['ImplementationCollectionContainsDeclared']=[x for x in m['predicates']['ImplementationCollectionContainsDeclared'] if x[0]!='col0'];refresh(m)
 add('nonempty-collection-handle-with-no-endpoints',empty_members,T=False,I=None)
 add('member-not-in-nominated-collection',lambda m:m['predicates']['BindingImplementationMemberDeclared'].append(['b0','im2']),T=False,I=None)
 add('nominated-member-missing-Binding-counterpart',lambda m:m['predicates']['BindingImplementationMemberDeclared'].remove(['b0','im0']),T=False,I=None)
 add('missing-single-canonical-authority',lambda m:m['predicates']['CanonicalAuthorityForAssociationDeclared'].remove(['assoc0','auth0']),T=False,I=None)
 add('second-canonical-authority-for-association',lambda m:m['predicates']['CanonicalAuthorityForAssociationDeclared'].append(['assoc0','auth1']),T=False,I=None)
 add('nominated-authority-mismatches-association',lambda m:change(m,'associationCanonicalAuthority','assoc0','auth1'),T=False,I=None)
 def collapsed_roles(m):m['constants']['ADOPTION_ROLE']=m['constants']['CONFORMANCE_ROLE'];refresh(m)
 add('evidence-purpose-role-collapsed',collapsed_roles,T=False,I=None)
 add('missing-adoption-evidence-purpose-binding',lambda m:m['predicates']['EvidenceForPurposeDeclared'].remove(['b0','adoptionRole','eShared']),T=False,I=None)
 add('extra-wrong-evidence-purpose-binding',lambda m:m['predicates']['EvidenceForPurposeDeclared'].append(['b0','roleOutside','eShared']),T=False,I=None)
 add('projection-missing-readonly-declaration',lambda m:m['predicates']['ProjectionReadOnlyDeclared'].remove(['p0']),T=False,I=None)
 add('projection-second-writable-authority',lambda m:m['predicates']['ProjectionSecondWritableAuthorityDeclared'].append(['p0']),T=False,I=None)
 add('projection-digest-differs',lambda m:change(m,'projectionDigest','p0','digestUnused'),T=False,I=None)
 add('second-projection-for-selected-Binding',lambda m:m['predicates']['ProjectionForBindingDeclared'].append(['b1','p1']),T=False,I=None)
 add('projection-relation-without-nomination',lambda m:m['predicates']['ProjectionForBindingDeclared'].append(['b0','pUnused']),T=False,I=None)
 add('projection-points-to-other-Binding',lambda m:change(m,'projectionBinding','p0','b2'),T=False,I=None)
 add('projection-association-mismatch',lambda m:change(m,'projectionAssociation','p0','assocUnused'),T=False,I=None)
 for change_name in ['cCap','cImpl','cPosture']:
  add('changed-state-inplace-successor-'+change_name,lambda m,change_name=change_name:change(m,'changeSuccessorBinding',change_name,'b0'),T=False,I=None)
 add('missing-required-successor-relation',lambda m:m['predicates']['SuccessorBindingRevisionDeclared'].remove(['b0','b4']),T=False,I=None)
 add('wrong-successor-intended-state',lambda m:change(m,'changeSuccessorBinding','cCap','b1'),T=False,I=None)
 add('Capability-change-removed-no-successor-required',lambda m:change(m,'changeDesiredCapability','cCap','cap0'),I=False)
 add('Implementation-member-change-removed-no-successor-required',lambda m:change(m,'changeDesiredImplementations','cImpl','colAlias'),I=False)
 add('posture-change-removed-no-successor-required',lambda m:change(m,'changeDesiredAdoptionPosture','cPosture','posture0'),I=False)
 add('no-change-successor-reference-may-be-original',lambda m:change(m,'changeSuccessorBinding','cSame','b0'))
 add('no-change-unused-successor-binding-absent',lambda m:m['predicates'].update(changeSuccessorBindingBindingDeclared=[x for x in m['predicates']['changeSuccessorBindingBindingDeclared'] if x[0]!='cSame']))
 add('without-projection-unused-projection-binding-absent',lambda m:m['predicates'].update(bindingProjectionBindingDeclared=[x for x in m['predicates']['bindingProjectionBindingDeclared'] if x[0]!='b0']))
 add('without-projection-unused-digest-binding-absent',lambda m:m['predicates'].update(bindingDigestBindingDeclared=[x for x in m['predicates']['bindingDigestBindingDeclared'] if x[0]!='b0']))
 add('unused-digest-handle-empty',lambda m:setfn(m,b.HANDLES['DigestReference'],'digestOutside','empty'))
 add('unused-projection-handle-empty',lambda m:setfn(m,b.HANDLES['ProjectionReference'],'pUnused','empty'))
 add('unused-Capability-revision-handle-empty',lambda m:setfn(m,b.HANDLES['CapabilityRevisionReference'],'capUnused','empty'))
 add('unused-Implementation-revision-handle-empty',lambda m:setfn(m,b.HANDLES['ImplementationRevisionReference'],'imUnused','empty'))
 selected=[(b.FIELDS,'b0'),(b.PROJECTION_FIELDS,'b1'),(b.ASSOCIATION_FIELDS,'assoc0'),(b.PROJECTION_RECORD_FIELDS,'p0'),(b.CHANGE_FIELDS,'cCap'),(b.SUCCESSOR_FIELDS,'cCap')]
 for fields,arg in selected:
  for name,sort in fields.items():
   value=getfn(base_model(),name,arg);alt=next(x for x in base_model()['domains'][sort] if x!=value)
   add('missing-exact-binding-'+name,lambda m,name=name,arg=arg:m['predicates'].update({name+'BindingDeclared':[x for x in m['predicates'][name+'BindingDeclared'] if x[0]!=arg]}),T=False,I=None)
   add('conflicting-exact-binding-'+name,lambda m,name=name,arg=arg,alt=alt:m['predicates'][name+'BindingDeclared'].append([arg,alt]),T=False,I=None)
   if sort not in b.MAP:add('undeclared-selected-target-'+name,lambda m,sort=sort,value=value:m['predicates'][sort+'Declared'].remove([value]),T=False,I=None)
   add('empty-selected-handle-'+name,lambda m,sort=sort,value=value:setfn(m,b.HANDLES[sort],value,'empty'),T=False,I=None)
 for name,mutation,error in [('empty-domain',lambda m:m['domains'].update(BindingRevisionReference=[]),'empty-or-malformed-domain'),('missing-domain',lambda m:m['domains'].pop('DigestReference'),'model-signature-denominator-mismatch'),('missing-function',lambda m:m['functions'].pop('bindingCapabilityRevision'),'model-signature-denominator-mismatch'),('partial-function',lambda m:m['functions']['bindingOwner'].pop(),'nontotal-function'),('function-range',lambda m:setfn(m,'bindingOwner','b0','foreign'),'ill-sorted-function-result'),('predicate-arity',lambda m:m['predicates']['EvidenceForPurposeDeclared'].append(['b0','adoptionRole']),'ill-sorted-model-tuple'),('predicate-range',lambda m:m['predicates']['BindingApplicable'].append(['foreign']),'ill-sorted-model-tuple'),('missing-constant',lambda m:m['constants'].pop('ADOPTION_ROLE'),'model-signature-denominator-mismatch')]:
  add('malformed-'+name,mutation,error=error)
 return rows
def qualify(model,ids):return {bucket:{ids[name]:value for name,value in model[bucket].items()} for bucket in ['domains','constants','functions','predicates']}
