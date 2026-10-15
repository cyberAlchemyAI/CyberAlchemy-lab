"""Prepare source-specific View-Bearing Concept models and counterexamples."""
from pathlib import Path
import ast
p=Path(__file__).resolve().parent;dest=p/'prepared'
s='''"""Supplied declared View-Bearing Concept models; no view/tree creation or authority effect."""
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
 ds={'MeaningReference':['m0','mOutside'],'ConceptReference':['c0','c1','cTerm','cOutside'],'EvidenceReference':['evidence0','evidence1','evidenceOutside'],'LifecycleReference':['life0','life1','lifeOutside'],'OwnerRouteReference':['owner0','owner1','ownerOutside'],'ReuseSurfaceReference':['reuse0','reuse1','reuseOutside'],'ChallengeRouteReference':['challenge0','challenge1','challengeOutside'],'ViewReference':['v0','v1','vExtra','vIncomplete','vOutside'],'ReadingSetReference':['readings0','readings1','readingsOutside'],'MoveSetReference':['moves0','moves1','movesOutside'],'ReadingReference':['reading0','reading1','readingOutside'],'AuthorityMoveReference':['move0','move1','moveOutside'],'SemanticIdentity':['normalizedIdentity','identityOutside'],'SemanticKind':['definitionKind','kindOutside'],'TypeReference':['definitionType','typeOutside'],'ScopeReference':['sharedScope','scopeOutside'],'SourceReference':['d44','sourceOutside'],'Token':['empty','none','reference','other']}
 cs={'EMPTY':'empty','NONE':'none','NORMALIZED_IDENTITY':'normalizedIdentity','NORMALIZED_KIND':'definitionKind','NORMALIZED_TYPE':'definitionType','NORMALIZED_SCOPE':'sharedScope','D44_SOURCE':'d44'}
 def concept_component(x,stem):return stem+('0' if x=='c0' else '1' if x=='c1' else 'Outside')
 maps={n:(lambda x,good=cs[const],bad=ds[b.MEANING_FIELDS[n]][-1]:good if x=='m0' else bad) for n,const in [('meaningIdentity','NORMALIZED_IDENTITY'),('meaningKind','NORMALIZED_KIND'),('meaningType','NORMALIZED_TYPE'),('meaningScope','NORMALIZED_SCOPE'),('meaningSource','D44_SOURCE'),('meaningEffect','NONE')]}
 maps.update(conceptMeaning=lambda x:'mOutside' if x=='cOutside' else 'm0',conceptEvidence=lambda x:concept_component(x,'evidence'),conceptLifecycle=lambda x:concept_component(x,'life'),conceptOwnerRoute=lambda x:'owner0' if x=='cTerm' else concept_component(x,'owner'),conceptReuseSurface=lambda x:concept_component(x,'reuse'),conceptChallengeRoute=lambda x:concept_component(x,'challenge'),conceptView=lambda x:{'c0':'v0','c1':'v1','cTerm':'vIncomplete','cOutside':'vOutside'}[x],viewAllowedReadings=lambda x:'readings1' if x=='v1' else 'readings0' if x in ['v0','vExtra'] else 'readingsOutside',viewForbiddenMoves=lambda x:'moves1' if x=='v1' else 'moves0' if x in ['v0','vExtra'] else 'movesOutside')
 for sort,n in b.HANDLES.items():maps[n]=lambda x:'reference'
 assert maps.keys()==b.FUNCTIONS.keys()
 funcs={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(ds[s] for s in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};preds={n:[] for n in b.SIGNATURE}
 for sort in b.SORTS:
  if sort not in ['ConceptReference','MeaningReference','Token']:preds[sort+'Declared']=[[x] for x in ds[sort] if not x.endswith('Outside')]
 preds.update(MeaningApplicable=[['m0']],MeaningInScopeDeclared=[['m0']],MeaningCanonicalInstanceDeclared=[['m0']],AcceptedSourceRelationsDeclared=[['m0']],ConceptApplicable=[['c0'],['c1'],['cTerm']],ConceptInScopeDeclared=[['c0'],['c1'],['cTerm']],ViewBearingConceptDeclared=[['c0'],['c1']],LoadBearingConceptDeclared=[['c0'],['c1']],OrdinaryNarrativeUnsafeDeclared=[['c0'],['c1']],GovernedViewNeededDeclared=[['c0'],['c1']],TermFallbackDeclared=[['cTerm']],CandidateFallbackDeclared=[['cTerm']],LocalConceptFallbackDeclared=[['cTerm']],AttachedViewDeclared=[['c0','v0'],['c0','vExtra'],['c1','v1']],AllowedReadingMemberDeclared=[['readings0','reading0'],['readings0','reading1'],['readings1','reading1']],ForbiddenMoveMemberDeclared=[['moves0','move0'],['moves1','move1']],ConceptActualAuthority=[['c1']])
 for n in b.CONDITIONS:preds[n]=[['c0'],['c1']]
 preds['OwnerRouteAvailableDeclared'].append(['cTerm'])
 for n in ['ViewGovernedDeclared','AllowedReadingsExplicitDeclared','ForbiddenAuthorityMovesExplicitDeclared','ViewInspectableDeclared','ViewUsableDeclared','ViewBoundedContextDeclared']:preds[n]=[['v0'],['v1'],['vExtra']]
 for n,values in [('Evidence',['v0']),('Relations',['v0']),('Lifecycle',['v1']),('OwnerRoute',['v1']),('Reuse',['vExtra']),('Challenge',['vExtra'])]:preds['ViewHelpsPreserve'+n+'Declared']=[[x] for x in values]
 m={'domains':ds,'constants':cs,'functions':funcs,'predicates':preds};refresh(m);return m
def controls():
 rows=[]
 def add(name,mutation=lambda m:None,T=True,I=True,error=None):
  m=base_model();mutation(m);rows.append({'case_id':name,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 def change(m,n,arg,value):setfn(m,n,arg,value);refresh(m)
 def fallback(m,n,missing=None):
  m['predicates'][n].remove(['c0']);m['predicates']['ViewBearingConceptDeclared'].remove(['c0']);m['predicates']['TermFallbackDeclared'].append(['c0'])
  if missing:m['predicates'][missing].remove(['v0'])
 def one_role(m,role):
  for n in b.PRESERVES:m['predicates']['ViewHelpsPreserve'+n+'Declared']=[['v0'],['v1'],['vExtra']] if n==role else []
 add('view-bearing-and-ordinary-concepts')
 add('no-selected-concepts',lambda m:m['predicates'].update(ConceptApplicable=[],ConceptInScopeDeclared=[]),I=False)
 add('ordinary-term-only-selected',lambda m:m['predicates'].update(ConceptApplicable=[['cTerm']],ConceptInScopeDeclared=[['cTerm']]),I=False)
 add('no-selected-meanings-or-concepts',lambda m:m['predicates'].update(MeaningApplicable=[],MeaningInScopeDeclared=[],ConceptApplicable=[],ConceptInScopeDeclared=[]),I=False)
 add('all-meanings-noncanonical',lambda m:m['predicates'].update(MeaningCanonicalInstanceDeclared=[]),I=False)
 add('noncanonical-meaning-without-accepted-source-declaration',lambda m:m['predicates'].update(MeaningCanonicalInstanceDeclared=[],AcceptedSourceRelationsDeclared=[]),I=False)
 add('ordinary-concept-may-be-ontology-branch',lambda m:m['predicates']['ConceptIsOntologyBranchDeclared'].append(['cTerm']))
 add('outside-claims-do-not-constrain-selected-concepts',lambda m:m['predicates']['ViewClaimsToDecideAuthorityDeclared'].append(['cOutside']))
 add('outside-view-posture-not-attached',lambda m:m['predicates']['ViewPretendsToDecideAuthorityDeclared'].append(['vOutside']))
 add('explicit-empty-allowed-reading-sets',lambda m:m['predicates'].update(AllowedReadingMemberDeclared=[]),I=False)
 add('explicit-empty-forbidden-move-sets',lambda m:m['predicates'].update(ForbiddenMoveMemberDeclared=[]),I=False)
 add('one-allowed-reading-still-complete',lambda m:m['predicates']['AllowedReadingMemberDeclared'].remove(['readings0','reading1']))
 add('no-additional-attached-view',lambda m:m['predicates']['AttachedViewDeclared'].remove(['c0','vExtra']),I=False)
 add('shared-reading-and-move-sets',lambda m:(setfn(m,'viewAllowedReadings','v1','readings0'),setfn(m,'viewForbiddenMoves','v1','moves0'),refresh(m)))
 add('same-view-can-serve-two-concepts',lambda m:(setfn(m,'conceptView','c1','v0'),m['predicates']['AttachedViewDeclared'].remove(['c1','v1']),m['predicates']['AttachedViewDeclared'].append(['c1','v0']),refresh(m)))
 for n in b.PRESERVES:add('one-preservation-role-'+n,lambda m,n=n:one_role(m,n),I=False)
 for n in b.CONDITIONS:
  add('missing-condition-but-still-view-bearing-'+n,lambda m,n=n:m['predicates'][n].remove(['c0']),T=False,I=None)
  add('coordinated-ordinary-fallback-'+n,lambda m,n=n:fallback(m,n),I=False)
 add('missing-field-with-coordinated-fallback',lambda m:fallback(m,'DistinctEvidenceDeclared','AllowedReadingsExplicitDeclared'),I=False)
 add('all-five-conditions-but-classification-absent',lambda m:m['predicates']['ViewBearingConceptDeclared'].remove(['c0']),T=False,I=None)
 add('no-fallback-for-ordinary-concept',lambda m:[m['predicates'].update({n:[]}) for n in ['TermFallbackDeclared','CandidateFallbackDeclared','LocalConceptFallbackDeclared']],T=False,I=None)
 for n in b.ACTUAL:add('independently-supported-actual-'+n,lambda m,n=n:m['predicates']['ConceptActual'+n].append(['c0']),I=False)
 for n in b.EXCLUDED:add('prohibited-'+n,lambda m,n=n:m['predicates'][n].append(['c0']),T=False,I=None)
 for n in ['LoadBearingConceptDeclared','OrdinaryNarrativeUnsafeDeclared','GovernedViewNeededDeclared']:add('missing-selected-genus-'+n,lambda m,n=n:m['predicates'][n].remove(['c0']),T=False,I=None)
 for n in ['ViewGovernedDeclared','AllowedReadingsExplicitDeclared','ForbiddenAuthorityMovesExplicitDeclared','ViewInspectableDeclared','ViewUsableDeclared','ViewBoundedContextDeclared']:add('missing-view-obligation-'+n,lambda m,n=n:m['predicates'][n].remove(['v0']),T=False,I=None)
 add('five-conditions-with-missing-reading-field',lambda m:m['predicates']['AllowedReadingsExplicitDeclared'].remove(['v0']),T=False,I=None)
 add('canonical-meaning-source-relations-unaccepted',lambda m:m['predicates']['AcceptedSourceRelationsDeclared'].remove(['m0']),T=False,I=None)
 add('meaning-sibling-silently-merged',lambda m:m['predicates']['MeaningSilentlyMergedDeclared'].append(['m0']),T=False,I=None)
 add('selected-view-pretends-authority',lambda m:m['predicates']['ViewPretendsToDecideAuthorityDeclared'].append(['v0']),T=False,I=None)
 add('additional-view-pretends-authority',lambda m:m['predicates']['ViewPretendsToDecideAuthorityDeclared'].append(['vExtra']),T=False,I=None)
 add('missing-nominated-view-link',lambda m:m['predicates']['AttachedViewDeclared'].remove(['c0','v0']),T=False,I=None)
 add('hidden-incomplete-attached-view',lambda m:m['predicates']['AttachedViewDeclared'].append(['c0','vIncomplete']),T=False,I=None)
 add('hidden-outside-attached-view',lambda m:m['predicates']['AttachedViewDeclared'].append(['c0','vOutside']),T=False,I=None)
 add('hidden-undeclared-reading-member',lambda m:m['predicates']['AllowedReadingMemberDeclared'].append(['readings0','readingOutside']),T=False,I=None)
 add('hidden-undeclared-forbidden-move',lambda m:m['predicates']['ForbiddenMoveMemberDeclared'].append(['moves0','moveOutside']),T=False,I=None)
 add('no-preservation-role-for-view',lambda m:[m['predicates']['ViewHelpsPreserve'+n+'Declared'].remove(['v0']) for n in ['Evidence','Relations']],T=False,I=None)
 add('one-of-two-preservation-roles-removed',lambda m:m['predicates']['ViewHelpsPreserveRelationsDeclared'].remove(['v0']),I=False)
 for fields,carrier in b.GROUPS:
  for n,sort in fields.items():
   arg={'MeaningReference':'m0','ConceptReference':'c0','ViewReference':'vExtra'}[carrier]
   add('missing-exact-binding-'+n,lambda m,n=n,arg=arg:m['predicates'].update({n+'BindingDeclared':[x for x in m['predicates'][n+'BindingDeclared'] if x[0]!=arg]}),T=False,I=None)
   alt=next(x for x in base_model()['domains'][sort] if x!=getfn(base_model(),n,arg));add('conflicting-exact-binding-'+n,lambda m,n=n,arg=arg,alt=alt:m['predicates'][n+'BindingDeclared'].append([arg,alt]),T=False,I=None)
   if sort!='Token':add('empty-reference-handle-'+n,lambda m,n=n,arg=arg,sort=sort:setfn(m,b.HANDLES[sort],getfn(m,n,arg),'empty'),T=False,I=None)
   else:add('empty-token-'+n,lambda m,n=n,arg=arg:change(m,n,arg,'empty'),T=False,I=None)
 for n,sort in b.MEANING_FIELDS.items():
  value='other' if sort=='Token' else base_model()['domains'][sort][-1];add('normalized-classification-mismatch-'+n,lambda m,n=n,value=value:change(m,n,'m0',value),T=False,I=None)
 for n,sort in b.CONCEPT_FIELDS.items():
  value=base_model()['domains'][sort][-1];add('undeclared-concept-component-'+n,lambda m,n=n,value=value:change(m,n,'c0',value),T=False,I=None)
 for n,arg in [('conceptMeaning','c0'),('conceptView','c0'),('conceptOwnerRoute','c0'),('viewAllowedReadings','v0'),('meaningIdentity','m0')]:add('ill-sorted-result-'+n,lambda m,n=n,arg=arg:setfn(m,n,arg,'ill-sorted'),T=None,I=None,error='ill-sorted-function-result')
 add('empty-concept-domain',lambda m:m['domains'].update(ConceptReference=[]),T=None,I=None,error='empty-or-malformed-domain')
 add('missing-function-denominator',lambda m:m['functions'].pop('conceptView'),T=None,I=None,error='model-signature-denominator-mismatch')
 add('duplicate-function-tuple',lambda m:m['functions']['conceptView'].append(copy.deepcopy(m['functions']['conceptView'][0])),T=None,I=None,error='duplicate-function-tuple')
 return rows
def qualify(model,ids):return {bucket:{ids[n]:value for n,value in model[bucket].items()} for bucket in ['domains','constants','functions','predicates']}
'''
old=Path('docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.generated-output/verify_candidate.py').read_text();tail=old[old.index('def verify(write=False):'):].replace('cal.definition.four-facet-artifact-invariant','cal.definition.generated-output').replace('GeneratedOutput','ProjectionSpecification').replace('Typed exact input,generator,run,lineage,parity and conditional canonical-contract declarations checked on supplied models;actual execution,contract authenticity,authority,fidelity and whole proof remain pending.','Typed normalized Meaning,five-condition classification,governed attached-view fields,possibly empty reading/move sets,preservation alternatives and independent authority checked on supplied models;actual preservation,usefulness,owner fidelity and whole proof remain pending.')
s+=tail;ast.parse(s)
with (dest/'verify_candidate.py').open('x') as f:f.write(s)
old=Path('docs/plans/definition-formal-assurance/candidate/prepared-episodes-v1/20261011-generated-output/check_prepared.py').read_text();check=old.replace('cal.definition.generated-output','cal.definition.projection-specification').replace("'OutputReference'","'ConceptReference'").replace('prepared-go-precheck','prepared-ps-precheck')
with (p/'check_prepared.py').open('x') as f:f.write(check)
cap=Path('docs/plans/definition-formal-assurance/candidate/prepared-episodes-v1/20261011-generated-output/capture_precheck.py').read_text()
with (p/'capture_precheck.py').open('x') as f:f.write(cap)
print('Prepared View-Bearing Concept models, hostile controls and independent prepared check')
