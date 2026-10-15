"""Prepare source-specific Semantic Epoch finite models and independent controls."""
from pathlib import Path
import ast
p=Path(__file__).resolve().parent;dest=p/'prepared'
s='''"""Supplied epoch/assessment/selection/lineage declarations; no actual succession."""
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
 ds={'AssessmentReference':['c'+str(i) for i in range(12)]+['cOutside'],'ArtifactReference':['a'+str(i) for i in range(13)]+['aOutside'],'ArtifactIdentity':['identity0','identity1','identityOutside'],'EpochReference':['e'+str(i) for i in range(7)]+['eOutside'],'EpochIdentity':['eid'+str(i) for i in range(7)]+['eidOutside'],'MaterialMeaningReference':['mm'+str(i) for i in range(7)]+['mmOutside'],'NormativeMeaningReference':['n0','n1','n2','nOutside'],'ScopeReference':['scope0','scope1','scopeOutside'],'ExclusionSetReference':['exclusions0','exclusions1','exclusionsOutside'],'ModelReference':['model0','model1','modelOutside'],'ContractSetReference':['contracts0','contracts1','contractsOutside'],'RepresentationReference':['rep'+str(i) for i in range(7)]+['repOutside'],'OwnerReference':['owner0','owner1','ownerOutside'],'SelectionReference':['s'+str(i) for i in range(7)]+['sOutside'],'DeltaReference':['d'+str(i) for i in range(6)]+['dOutside'],'LineageReference':['l'+str(i) for i in range(6)]+['lOutside'],'EvidenceReference':['ev0','ev1','evOutside'],'Token':['empty','reference','other']}
 def index(x):return int(x[1:])
 def artifact_material(x):return 'mmOutside' if x.endswith('Outside') else 'mm'+str(index(x)) if 1<=index(x)<=5 else 'mm6' if x=='a12' else 'mm0'
 reps={'a0':'rep0','a1':'rep1','a2':'rep0','a3':'rep1','a4':'rep2','a5':'rep0','a6':'rep1','a7':'rep2','a8':'rep3','a9':'rep4','a10':'rep5','a11':'rep0','a12':'rep6','aOutside':'repOutside'}
 def epoch_artifact(x):return 'aOutside' if x.endswith('Outside') else 'a12' if x=='e6' else 'a'+str(index(x))
 def conditional(x,stem):return stem+str(index(x)) if x in ['c'+str(i) for i in range(5)] else stem+'5' if x=='c11' else stem+'Outside'
 maps={'artifactIdentity':lambda x:'identityOutside' if x.endswith('Outside') else 'identity0','artifactMaterialMeaning':artifact_material,'artifactNormativeMeaning':lambda x:'nOutside' if x.endswith('Outside') else 'n1' if x=='a1' else 'n2' if x=='a12' else 'n0','artifactScope':lambda x:'scopeOutside' if x.endswith('Outside') else 'scope1' if x=='a2' else 'scope0','artifactExclusions':lambda x:'exclusionsOutside' if x.endswith('Outside') else 'exclusions1' if x=='a3' else 'exclusions0','artifactOwnedModel':lambda x:'modelOutside' if x.endswith('Outside') else 'model1' if x=='a4' else 'model0','artifactContracts':lambda x:'contractsOutside' if x.endswith('Outside') else 'contracts1' if x=='a5' else 'contracts0','artifactRepresentation':lambda x:reps[x],'epochIdentity':lambda x:'eidOutside' if x.endswith('Outside') else 'eid'+str(index(x)),'epochArtifact':epoch_artifact,'epochMeaning':lambda x:artifact_material(epoch_artifact(x)),'epochSelection':lambda x:'sOutside' if x.endswith('Outside') else 's'+str(index(x)),'epochPredecessor':lambda x:'e0' if x not in ['e0','eOutside'] else 'eOutside','epochDelta':lambda x:'d'+str(index(x)-1) if x not in ['e0','eOutside'] else 'dOutside','epochLineage':lambda x:'l'+str(index(x)-1) if x not in ['e0','eOutside'] else 'lOutside','assessmentBefore':lambda x:'aOutside' if x.endswith('Outside') else 'a0','assessmentAfter':lambda x:'aOutside' if x.endswith('Outside') else 'a'+str(index(x)+1),'assessmentPredecessor':lambda x:'eOutside' if x.endswith('Outside') else 'e0','assessmentOwner':lambda x:'ownerOutside' if x.endswith('Outside') else 'owner0','assessmentNewEpoch':lambda x:'e'+str(index(x)+1) if x in ['c'+str(i) for i in range(5)] else 'e6' if x=='c11' else 'eOutside','assessmentDelta':lambda x:conditional(x,'d'),'assessmentLineage':lambda x:conditional(x,'l'),'assessmentSelection':lambda x:'s'+str(index(x)+1) if x in ['c'+str(i) for i in range(5)] else 's6' if x=='c11' else 'sOutside','assessmentPreservationEvidence':lambda x:'evOutside' if x.endswith('Outside') else 'ev0','selectionOwner':lambda x:'ownerOutside' if x.endswith('Outside') else 'owner0','selectionEpoch':lambda x:'eOutside' if x.endswith('Outside') else 'e'+str(index(x)),'selectionPredecessor':lambda x:'e0' if x not in ['s0','sOutside'] else 'eOutside','selectionDelta':lambda x:'d'+str(index(x)-1) if x not in ['s0','sOutside'] else 'dOutside','selectionLineage':lambda x:'l'+str(index(x)-1) if x not in ['s0','sOutside'] else 'lOutside','deltaBefore':lambda x:'mmOutside' if x.endswith('Outside') else 'mm0','deltaAfter':lambda x:'mmOutside' if x.endswith('Outside') else 'mm'+str(index(x)+1),'lineageBefore':lambda x:'eOutside' if x.endswith('Outside') else 'e0','lineageAfter':lambda x:'eOutside' if x.endswith('Outside') else 'e'+str(index(x)+1),'lineageDelta':lambda x:'dOutside' if x.endswith('Outside') else 'd'+str(index(x))}
 for sort,n in b.HANDLES.items():maps[n]=lambda x:'reference'
 assert set(maps)==set(b.FUNCTIONS)
 funcs={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(ds[z] for z in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};preds={n:[] for n in b.SIGNATURE}
 for sort in b.SORTS:
  if sort not in ['AssessmentReference','Token']:preds[sort+'Declared']=[[x] for x in ds[sort] if not x.endswith('Outside')]
 for n in ['AssessmentApplicable','AssessmentInScopeDeclared','AssessmentRecordedDeclared','AssessmentSeparatesSemanticRepresentationDeclared']:preds[n]=[['c'+str(i)] for i in range(12)]
 for n in ['AssessmentOwnerDeterminesMaterialChangeDeclared','AssessmentNewEpochDeclared','AssessmentMaterialMeaningChangedDeclared']:preds[n]=[['c'+str(i)] for i in [0,1,2,3,4,11]]
 preds['AssessmentMeaningEqualDeclared']=[['c'+str(i)] for i in range(5,11)]
 for i,n in enumerate(b.DIMENSIONS):preds[n]=[['c'+str(i)]]+([['c11']] if i==0 else [])
 preds['AssessmentRepresentationChangedDeclared']=[['c'+str(i)] for i in range(12) if reps['a'+str(i+1)]!=reps['a0']]
 preds['AssessmentByteChangedDeclared']=[['c'+str(i)] for i in [0,5,6,7,8,9,11]]
 for n,i in [('AssessmentRepresentationOnlyDeclared',5),('AssessmentSchemaOnlyDeclared',6),('AssessmentEncodingOnlyDeclared',7),('AssessmentDerivedRefreshDeclared',8)]:preds[n]=[['c'+str(i)]]
 preds.update(AssessmentPreservationClaimedDeclared=[['c5'],['c11']],EvidenceReviewableDeclared=[['ev0']],AssessmentActualAuthority=[['c1']])
 for n in ['EpochApplicable','EpochInScopeDeclared','EpochRecordedDeclared','EpochImmutableDeclared','EpochOwnerSelectedDeclared']:preds[n]=[['e'+str(i)] for i in range(7)]
 preds['ArtifactVersionedSemanticDeclared']=[['a'+str(i)] for i in range(13)]
 preds['SelectionRecordedDeclared']=[['s'+str(i)] for i in range(7)]
 for n in ['DeltaRecordedDeclared','DeltaMaterialDeclared']:preds[n]=[['d'+str(i)] for i in range(6)]
 for n in ['LineageRecordedDeclared','LineageApplicableDeclared']:preds[n]=[['l'+str(i)] for i in range(6)]
 m={'domains':ds,'constants':{'EMPTY':'empty'},'functions':funcs,'predicates':preds};refresh(m);return m
def controls():
 rows=[]
 def add(name,mutation=lambda m:None,T=True,I=True,error=None):
  m=base_model();mutation(m);rows.append({'case_id':name,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 def change(m,n,arg,value):setfn(m,n,arg,value);refresh(m)
 add('exact-owner-material-epoch-and-lineage-records')
 add('no-selected-assessments',lambda m:m['predicates'].update(AssessmentApplicable=[],AssessmentInScopeDeclared=[]),I=False)
 add('only-first-assessment-selected',lambda m:m['predicates'].update(AssessmentApplicable=[['c0']],AssessmentInScopeDeclared=[['c0']]),I=False)
 add('no-selected-epoch-or-assessment',lambda m:m['predicates'].update(AssessmentApplicable=[],AssessmentInScopeDeclared=[],EpochApplicable=[],EpochInScopeDeclared=[]),I=False)
 add('no-independent-authority-supplied',lambda m:m['predicates'].update(AssessmentActualAuthority=[]),I=False)
 add('all-actual-outcomes-independently-supplied',lambda m:[m['predicates'].update({'AssessmentActual'+n:[['c'+str(i)] for i in range(12)]}) for n in b.ACTUAL],I=False)
 for n in b.ACTUAL:add('independently-supported-actual-'+n,lambda m,n=n:m['predicates']['AssessmentActual'+n].append(['c0']))
 for n in b.EXCLUDED:
  add('selected-excluded-'+n,lambda m,n=n:m['predicates'][n].append(['c0']),T=False,I=None)
  add('outside-excluded-'+n,lambda m,n=n:m['predicates'][n].append(['cOutside']))
 add('nonmaterial-scope-reference-change-allowed',lambda m:change(m,'artifactScope','a6','scope1'))
 add('same-reference-no-change-assessment',lambda m:change(m,'assessmentAfter','c10','a0'))
 add('duplicate-epoch-identity-label-not-forced-injective',lambda m:change(m,'epochIdentity','e2','eid1'))
 add('contested-preservation-new-epoch-allowed',lambda m:m['predicates']['AssessmentPreservationClaimedDeclared'].append(['c0']))
 add('unused-successor-delta-handle-empty',lambda m:setfn(m,b.HANDLES['DeltaReference'],'dOutside','empty'))
 add('byte-change-without-successor-allowed',lambda m:m['predicates']['AssessmentByteChangedDeclared'].append(['c10']))
 add('material-change-without-byte-flag-allowed',lambda m:m['predicates']['AssessmentByteChangedDeclared'].remove(['c0']))
 add('representation-only-marked-new',lambda m:m['predicates']['AssessmentNewEpochDeclared'].append(['c5']),T=False,I=None)
 add('owner-determination-missing',lambda m:m['predicates']['AssessmentOwnerDeterminesMaterialChangeDeclared'].remove(['c0']),T=False,I=None)
 add('owner-determination-no-material-dimension',lambda m:m['predicates']['AssessmentMaterialNormativeMeaningChangedDeclared'].remove(['c0']),T=False,I=None)
 add('material-scope-no-coordinate-difference',lambda m:m['predicates']['AssessmentMaterialScopeChangedDeclared'].append(['c5']),T=False,I=None)
 add('aggregate-material-equal-with-new-epoch',lambda m:change(m,'artifactMaterialMeaning','a1','mm0'),T=False,I=None)
 add('selected-artifact-identity-changed',lambda m:change(m,'artifactIdentity','a1','identity1'),T=False,I=None)
 add('representation-change-flag-missing',lambda m:m['predicates']['AssessmentRepresentationChangedDeclared'].remove(['c0']),T=False,I=None)
 add('representation-difference-flag-on-equal-ref',lambda m:m['predicates']['AssessmentRepresentationChangedDeclared'].append(['c1']),T=False,I=None)
 add('meaning-equal-flag-on-material-successor',lambda m:m['predicates']['AssessmentMeaningEqualDeclared'].append(['c0']),T=False,I=None)
 add('material-successor-labeled-derived-refresh',lambda m:m['predicates']['AssessmentDerivedRefreshDeclared'].append(['c0']),T=False,I=None)
 add('predecessor-artifact-mismatch',lambda m:change(m,'assessmentBefore','c0','a3'),T=False,I=None)
 add('successor-reference-equals-predecessor',lambda m:change(m,'assessmentNewEpoch','c0','e0'),T=False,I=None)
 add('successor-epoch-not-applicable',lambda m:(m['predicates']['EpochApplicable'].remove(['e1']),m['predicates']['EpochInScopeDeclared'].remove(['e1'])),T=False,I=None)
 for n,arg in [('AssessmentInScopeDeclared','c0'),('AssessmentRecordedDeclared','c0'),('AssessmentSeparatesSemanticRepresentationDeclared','c0'),('EpochInScopeDeclared','e1'),('EpochRecordedDeclared','e0'),('EpochImmutableDeclared','e0'),('EpochOwnerSelectedDeclared','e0'),('ArtifactVersionedSemanticDeclared','a0'),('SelectionRecordedDeclared','s1'),('DeltaRecordedDeclared','d0'),('DeltaMaterialDeclared','d0'),('LineageRecordedDeclared','l0'),('LineageApplicableDeclared','l0'),('EvidenceReviewableDeclared','ev0')]:add('missing-selected-posture-'+n,lambda m,n=n,arg=arg:m['predicates'][n].remove([arg]),T=False,I=None)
 for n,arg,value in [('epochArtifact','e1','a2'),('epochMeaning','e1','mm2'),('epochPredecessor','e1','e2'),('epochDelta','e1','d1'),('epochLineage','e1','l1'),('epochSelection','e1','s2'),('selectionOwner','s1','owner1'),('selectionEpoch','s1','e2'),('selectionPredecessor','s1','e2'),('selectionDelta','s1','d1'),('selectionLineage','s1','l1'),('deltaBefore','d0','mm2'),('deltaAfter','d0','mm2'),('lineageBefore','l0','e2'),('lineageAfter','l0','e2'),('lineageDelta','l0','d1')]:add('inexact-selected-'+n,lambda m,n=n,arg=arg,value=value:change(m,n,arg,value),T=False,I=None)
 targets={id(b.ARTIFACT_FIELDS):'a0',id(b.EPOCH_FIELDS):'e0',id(b.EPOCH_SUCCESSOR_FIELDS):'e1',id(b.ASSESSMENT_FIELDS):'c0',id(b.ASSESSMENT_NEW_FIELDS):'c0',id(b.PRESERVATION_FIELDS):'c5',id(b.SELECTION_FIELDS):'s1',id(b.SELECTION_SUCCESSOR_FIELDS):'s1',id(b.DELTA_FIELDS):'d0',id(b.LINEAGE_FIELDS):'l0'}
 for fields,carrier in b.GROUPS:
  arg=targets[id(fields)]
  for n,sort in fields.items():
   add('missing-exact-binding-'+n,lambda m,n=n,arg=arg:m['predicates'].update({n+'BindingDeclared':[x for x in m['predicates'][n+'BindingDeclared'] if x[0]!=arg]}),T=False,I=None)
   alt=next(x for x in base_model()['domains'][sort] if x!=getfn(base_model(),n,arg));add('conflicting-exact-binding-'+n,lambda m,n=n,arg=arg,alt=alt:m['predicates'][n+'BindingDeclared'].append([arg,alt]),T=False,I=None)
   value=getfn(base_model(),n,arg);add('undeclared-selected-target-'+n,lambda m,sort=sort,value=value:m['predicates'][sort+'Declared'].remove([value]),T=False,I=None)
 selected={'AssessmentReference':'c0','ArtifactReference':'a0','ArtifactIdentity':'identity0','EpochReference':'e0','EpochIdentity':'eid0','MaterialMeaningReference':'mm0','NormativeMeaningReference':'n0','ScopeReference':'scope0','ExclusionSetReference':'exclusions0','ModelReference':'model0','ContractSetReference':'contracts0','RepresentationReference':'rep0','OwnerReference':'owner0','SelectionReference':'s1','DeltaReference':'d0','LineageReference':'l0','EvidenceReference':'ev0'}
 for sort,n in b.HANDLES.items():add('empty-selected-handle-'+sort,lambda m,n=n,value=selected[sort]:setfn(m,n,value,'empty'),T=False,I=None)
 add('malformed-empty-domain',lambda m:m['domains'].update(AssessmentReference=[]),error='empty-or-malformed-domain')
 add('malformed-missing-domain',lambda m:m['domains'].pop('EpochReference'),error='model-signature-denominator-mismatch')
 add('malformed-missing-function',lambda m:m['functions'].pop('assessmentBefore'),error='model-signature-denominator-mismatch')
 add('malformed-partial-function',lambda m:m['functions']['assessmentBefore'].pop(),error='nontotal-function')
 add('malformed-function-range',lambda m:setfn(m,'assessmentBefore','c0','foreign'),error='ill-sorted-function-result')
 add('malformed-function-argument',lambda m:m['functions']['assessmentBefore'][0].update(args=['foreign']),error='ill-sorted-model-tuple')
 add('malformed-predicate-range',lambda m:m['predicates']['AssessmentApplicable'].append(['foreign']),error='ill-sorted-model-tuple')
 add('malformed-predicate-arity',lambda m:m['predicates']['assessmentOwnerBindingDeclared'].append(['c0']),error='ill-sorted-model-tuple')
 return rows
def qualify(model,ids):return {bucket:{ids[n]:value for n,value in model[bucket].items()} for bucket in ['domains','constants','functions','predicates']}
'''
old=Path('docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.schema-evolution-invariant/verify_candidate.py').read_text()
tail=old[old.index('def verify(write=False):'):].replace('cal.definition.representation-revision/','cal.definition.schema-evolution-invariant/').replace('SchemaEvolutionInvariant','SemanticEpoch')
tail=tail.replace('Exact normalized invariant,shape-change,amendment,witness alternatives,owned residue and downstream-path declarations checked on supplied models;actual enforcement,execution,owner fidelity,authority and whole proof remain pending.','Exact immutable owner-selected epoch genus,owner/material assessment,predecessor/successor/selection/delta/lineage and representation exclusions checked on supplied models;actual materiality,owner selection,lineage,storage,authority and whole proof remain pending.')
s+=tail;ast.parse(s)
with (dest/'verify_candidate.py').open('x') as f:f.write(s)
print('Prepared source-specific Semantic Epoch model producer.')
