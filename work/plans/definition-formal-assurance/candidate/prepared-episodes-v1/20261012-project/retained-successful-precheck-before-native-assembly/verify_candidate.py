"""Finite Project Goal-state,membership,identity continuity and authority control models."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(name):return json.loads((b.UNIT/name).read_bytes())
def setfn(m,n,arg,value):next(x for x in m['functions'][n] if x['args']==[arg])['value']=value
def getfn(m,n,arg):return next(x['value'] for x in m['functions'][n] if x['args']==[arg])
def refresh(m):
 for fields,carrier in b.GROUPS:
  for n in fields:m['predicates'][n+'BindingDeclared']=[[x['args'][0],x['value']] for x in m['functions'][n]]
def base_model():
 ds={sort:[sort[0].lower()+sort[1:]+'0',sort[0].lower()+sort[1:]+'1',sort[0].lower()+sort[1:]+'2',sort[0].lower()+sort[1:]+'3',sort[0].lower()+sort[1:]+'Outside'] for sort in b.SORTS}
 ds.update(ProjectReference=['p0','p1','p2','p3','pOutside'],IdentityReference=['i0','i1','i2','i3','iProduct','iOutside'],GoalReference=['g0','g1','g2','g3','g4','gUnused','gOutside'],MemberReference=['mG0','mG1','mG2','mG3','mG4','mOwner','mEvidence','mDecision','mArtifact','mWork','mLifecycle','mOutside'],ProductReference=['prod0','prodOutside'],ChangeReference=['x0','x1','x2','x3','x4','xOutside'],LifecycleStateReference=['proposed','active','draft','suspended','achieved','stateOutside'],Token=['empty','ref','other']);maps={}
 def table(n,values):maps[n]=lambda x:values.get(x,ds[b.FUNCTIONS[n][1]][-1])
 for n,sort in b.PROJECT_FIELDS.items():table(n,{'p'+str(i):ds[sort][i] for i in range(4)})
 table('projectLifecycleState',{'p0':'proposed','p1':'active','p2':'suspended','p3':'proposed'});table('goalMember',{'g'+str(i):'mG'+str(i) for i in range(5)});table('goalLifecycleState',{'g0':'draft','g1':'active','g2':'achieved','g3':'active','g4':'draft'});table('productIdentity',{'prod0':'iProduct'})
 subjects={'x0':'p0','x1':'p0','x2':'p1','x3':'p1','x4':'p2'};table('changeProject',subjects)
 for n in ['changeBeforeIdentity','changeAfterIdentity']:table(n,{x:'i'+p[-1] for x,p in subjects.items()})
 for sort,n in b.HANDLES.items():maps[n]=lambda x:'ref'
 assert set(maps)==set(b.FUNCTIONS)
 funcs={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(ds[z] for z in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};preds={n:[] for n in b.SIGNATURE}
 for sort in b.SORTS:
  if sort not in [x[1] for x in b.PRIMARY]+['Token']:preds[sort+'Declared']=[[x] for x in ds[sort] if not x.endswith('Outside')]
 for n in b.FLAGS['Project']:preds[n]=[['p'+str(i)] for i in range(4)]
 for n in b.FLAGS['Change']:preds[n]=[['x'+str(i)] for i in range(5)]
 cols=ds['GoalCollectionReference'];links=[['p0','g0'],['p1','g1'],['p1','g4'],['p2','g2'],['p3','g3']];preds['ProjectGoalReferenceDeclared']=links;preds['GoalCollectionContainsDeclared']=[[cols[int(p[-1])],g] for p,g in links]
 memberships=[[p,'mG'+g[-1]] for p,g in links]+[['p0','mOwner']]+[['p1','m'+k] for k in ['Evidence','Decision','Artifact','Work','Lifecycle']];preds['ProjectMemberDeclared']=copy.deepcopy(memberships);preds['ExplicitProjectMembershipRelationDeclared']=copy.deepcopy(memberships)
 for kind in b.MEMBER_KINDS:preds['MemberIs'+kind+'Declared']=[['mG'+str(i)] for i in range(5)] if kind=='Goal' else [['m'+kind]]
 for i,kind in enumerate(b.CHANGE_KINDS):preds['ChangeIs'+kind+'Declared']=[['x'+str(i)]]
 preds['ProjectActualOwnerAuthorization']=[['p2']];m={'domains':ds,'constants':{'EMPTY':'empty','PROPOSED':'proposed','ACTIVE':'active','DRAFT':'draft'},'functions':funcs,'predicates':preds};refresh(m);return m
def controls():
 rows=[]
 def add(name,mutation=lambda m:None,T=True,I=True,error=None):
  m=base_model();mutation(m);rows.append({'case_id':name,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 def change(m,n,arg,value):setfn(m,n,arg,value);refresh(m)
 add('proposed-active-nonactive-Projects-explicit-membership-durable-changes')
 add('no-selected-Projects-or-changes',lambda m:m['predicates'].update({prefix+suffix:[] for prefix,sort,e,a in b.PRIMARY for suffix in ['Applicable','InScopeDeclared']}),I=False)
 add('no-independent-owner-authorization',lambda m:m['predicates'].update(ProjectActualOwnerAuthorization=[]),I=False)
 add('no-selected-change-records',lambda m:m['predicates'].update(ChangeApplicable=[],ChangeInScopeDeclared=[]),I=False)
 for (prefix,sort,excluded,names),target in zip(b.PRIMARY,['p1','x2']):
  for n in names:add('independently-supported-'+prefix+'-Actual'+n,lambda m,prefix=prefix,n=n,target=target:m['predicates'].update({prefix+'Actual'+n:[list(x) for x in sorted({tuple(x) for x in m['predicates'][prefix+'Actual'+n]}|{(target,)})]}),I=None)
  for n in excluded:
   add('selected-excluded-'+n,lambda m,n=n,target=target:m['predicates'][n].append([target]),T=False,I=None)
   outside=base_model()['domains'][sort][-1];add('outside-excluded-'+n,lambda m,n=n,outside=outside:m['predicates'][n].append([outside]))
 for label in ['goalMemberBindingDeclared','goalLifecycleStateBindingDeclared']:add('unused-Goal-binding-absent-'+label,lambda m,label=label:m['predicates'].update({label:[x for x in m['predicates'][label] if x[0]!='gUnused']}))
 add('unused-Goal-member-handle-empty',lambda m:setfn(m,b.HANDLES['MemberReference'],'mOutside','empty'))
 add('unused-change-handle-empty',lambda m:setfn(m,b.HANDLES['ChangeReference'],'xOutside','empty'))
 add('overlapping-change-kinds-permitted',lambda m:m['predicates']['ChangeIsTaskDeclared'].append(['x0']))
 add('evidence-and-artifact-member-role-overlap-permitted',lambda m:m['predicates']['MemberIsArtifactDeclared'].append(['mEvidence']))
 add('multiple-Goal-references-include-active-and-draft',lambda m:None)
 add('nonactive-Project-nonactive-Goal-remains-valid',lambda m:None)
 add('proposed-Project-active-Goal-valid',lambda m:None)
 add('nominal-active-Project-does-not-prove-activation',lambda m:None)
 add('name-change-preserves-identity',lambda m:change(m,'projectName','p1','nameReference0'))
 add('proposed-active-alternative-changed-to-draft-remains-valid',lambda m:change(m,'goalLifecycleState','g3','draft'),I=False)
 def remove_extra(m):
  col=getfn(m,'projectGoals','p1');m['predicates']['GoalCollectionContainsDeclared'].remove([col,'g4']);m['predicates']['ProjectGoalReferenceDeclared'].remove(['p1','g4']);m['predicates']['ProjectMemberDeclared'].remove(['p1','mG4']);m['predicates']['ExplicitProjectMembershipRelationDeclared'].remove(['p1','mG4'])
 add('remove-extra-draft-Goal-active-Goal-remains-sufficient',remove_extra,I=False)
 def empty(m):
  col=getfn(m,'projectGoals','p2');m['predicates']['GoalCollectionContainsDeclared'].remove([col,'g2']);m['predicates']['ProjectGoalReferenceDeclared'].remove(['p2','g2']);m['predicates']['ProjectMemberDeclared'].remove(['p2','mG2']);m['predicates']['ExplicitProjectMembershipRelationDeclared'].remove(['p2','mG2'])
 add('nonempty-reference-handle-with-empty-Goal-collection-rejected',empty,T=False,I=None)
 add('proposed-Goal-neither-draft-nor-active',lambda m:change(m,'goalLifecycleState','g0','achieved'),T=False,I=None)
 add('active-Project-with-only-draft-Goals',lambda m:change(m,'goalLifecycleState','g1','draft'),T=False,I=None)
 add('Goal-reference-collection-link-omitted',lambda m:m['predicates']['ProjectGoalReferenceDeclared'].remove(['p0','g0']),T=False,I=None)
 add('extra-Goal-reference-not-in-collection',lambda m:m['predicates']['ProjectGoalReferenceDeclared'].append(['p0','g2']),T=False,I=None)
 add('referenced-Goal-undeclared',lambda m:m['predicates']['GoalReferenceDeclared'].remove(['g1']),T=False,I=None)
 add('Goal-member-role-missing',lambda m:m['predicates']['MemberIsGoalDeclared'].remove(['mG1']),T=False,I=None)
 add('Goal-reference-membership-absent',lambda m:m['predicates']['ProjectMemberDeclared'].remove(['p1','mG1']),T=False,I=None)
 add('membership-without-explicit-relation',lambda m:m['predicates']['ExplicitProjectMembershipRelationDeclared'].remove(['p0','mOwner']),T=False,I=None)
 add('explicit-membership-relation-without-member-declaration',lambda m:m['predicates']['ProjectMemberDeclared'].remove(['p0','mOwner']),T=False,I=None)
 add('undeclared-member-reference',lambda m:m['predicates']['MemberReferenceDeclared'].remove(['mOwner']),T=False,I=None)
 add('membership-transfers-artifact-authority-rejected',lambda m:m['predicates']['MembershipTransfersArtifactAuthorityDeclared'].append(['p1','mArtifact']),T=False,I=None)
 add('outside-Project-membership-authority-claim-not-scoped',lambda m:m['predicates']['MembershipTransfersArtifactAuthorityDeclared'].append(['pOutside','mOutside']))
 add('Project-ID-collapses-into-Product-ID',lambda m:change(m,'projectIdentity','p1','iProduct'),T=False,I=None)
 add('change-before-identity-mismatches-Project',lambda m:change(m,'changeBeforeIdentity','x2','i2'),T=False,I=None)
 add('change-after-identity-differs',lambda m:change(m,'changeAfterIdentity','x2','i2'),T=False,I=None)
 add('change-matches-another-Project-identity',lambda m:change(m,'changeProject','x2','p2'),T=False,I=None)
 add('selected-change-without-recognized-kind',lambda m:m['predicates']['ChangeIsFolderDeclared'].remove(['x2']),T=False,I=None)
 for n,arg in [('ProjectDurableCoordinationIdentityDeclared','p1'),('ProjectCoordinatesTowardPurposeDeclared','p1')]:add('missing-'+n,lambda m,n=n,arg=arg:m['predicates'][n].remove([arg]),T=False,I=None)
 for fields,arg in [(b.PROJECT_FIELDS,'p1'),(b.GOAL_FIELDS,'g1'),(b.PRODUCT_FIELDS,'prod0'),(b.CHANGE_FIELDS,'x2')]:
  for n,sort in fields.items():
   add('missing-exact-binding-'+n,lambda m,n=n,arg=arg:m['predicates'].update({n+'BindingDeclared':[x for x in m['predicates'][n+'BindingDeclared'] if x[0]!=arg]}),T=False,I=None)
   value=getfn(base_model(),n,arg);alt=next(x for x in base_model()['domains'][sort] if x!=value);add('conflicting-exact-binding-'+n,lambda m,n=n,arg=arg,alt=alt:m['predicates'][n+'BindingDeclared'].append([arg,alt]),T=False,I=None)
   add('undeclared-selected-target-'+n,lambda m,sort=sort,value=value:m['predicates'][b.member(sort)].remove([value]),T=False,I=None)
 chosen={sort:values[0] for sort,values in base_model()['domains'].items() if sort!='Token'}
 for sort,n in b.HANDLES.items():add('empty-selected-handle-'+sort,lambda m,n=n,value=chosen[sort]:setfn(m,n,value,'empty'),T=False,I=None)
 for name,mutate,code in [('empty-domain',lambda m:m['domains'].update(ProjectReference=[]),'empty-or-malformed-domain'),('missing-domain',lambda m:m['domains'].pop('GoalReference'),'model-signature-denominator-mismatch'),('missing-function',lambda m:m['functions'].pop('projectGoals'),'model-signature-denominator-mismatch'),('partial-function',lambda m:m['functions']['projectGoals'].pop(),'nontotal-function'),('function-range',lambda m:setfn(m,'projectGoals','p0','foreign'),'ill-sorted-function-result'),('function-argument',lambda m:m['functions']['projectGoals'][0].update(args=['foreign']),'ill-sorted-model-tuple'),('predicate-range',lambda m:m['predicates']['ProjectApplicable'].append(['foreign']),'ill-sorted-model-tuple'),('predicate-arity',lambda m:m['predicates']['ProjectMemberDeclared'].append(['p0']),'ill-sorted-model-tuple')]:add('malformed-'+name,mutate,error=code)
 return rows

def qualify(model,ids):return {bucket:{ids[n]:value for n,value in model[bucket].items()} for bucket in ["domains","constants","functions","predicates"]}
