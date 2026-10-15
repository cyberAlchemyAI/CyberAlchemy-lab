"""Prepare supplied finite SEI models, adversarial controls and independent outcomes."""
from pathlib import Path
import ast
p=Path(__file__).resolve().parent;dest=p/'prepared'
s='''"""Supplied SEI amendment/witness/residue models; no actual enforcement or effects."""
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
 ds={'MeaningReference':['m0','mOutside'],'MeaningIdentity':['identitySEI','identityOther','identityOutside'],'TypeReference':['invariantType','schemaType','typeOutside'],'ShapeChangeReference':['c0','c1','c2','c3','c4','cOutside'],'ShapeReference':['shape0','shape1','shape2','shape3','shape4','shape5','shapeOutside'],'AmendmentReference':['a0','a1','a2','a3','a4','aOutside'],'WitnessReference':['w0','w1','w2','w3','w4','wOutside'],'WitnessKind':['deterministic','hybrid','review','absent','kindOutside'],'ResidueReference':['r0','r1','r2','r3','r4','rOutside'],'OwnerReference':['owner0','owner1','ownerOutside'],'ScopeReference':['sharedScope','localScope','scopeOutside'],'SourceReference':['sourceD25','source0','sourceOutside'],'ReasonReference':['reason0','reason1','reason2','reason3','reason4','reasonOutside'],'DeltaReference':['delta0','delta1','delta2','delta3','delta4','deltaOutside'],'CompatibilityReference':['compatibility0','compatibility1','compatibility2','compatibility3','compatibility4','compatibilityOutside'],'RouteReference':['rollout0','rollback1','rollout2','rollback2','rollback3','rollout4','routeOutside'],'EffectReference':['effect0','effect1','effectOutside'],'EvidenceReference':['evidence0','evidence1','evidence2','evidence3','evidence4','evidenceOutside'],'Token':['empty','reference','other']}
 cs={'EMPTY':'empty','SEI_ID':'identitySEI','SHARED_SCOPE':'sharedScope','INVARIANT_TYPE':'invariantType','D25_SOURCE':'sourceD25','DETERMINISTIC':'deterministic','HYBRID':'hybrid','REVIEW':'review','ABSENT':'absent'}
 def tail(x):return 'Outside' if x.endswith('Outside') else x[-1]
 maps={'meaningIdentity':lambda x:'identitySEI' if x=='m0' else 'identityOutside','meaningScope':lambda x:'sharedScope' if x=='m0' else 'scopeOutside','meaningType':lambda x:'invariantType' if x=='m0' else 'typeOutside','meaningSource':lambda x:'sourceD25' if x=='m0' else 'sourceOutside','changeBefore':lambda x:'shape0' if x!='cOutside' else 'shapeOutside','changeAfter':lambda x:'shape'+str(int(tail(x))+1) if x!='cOutside' else 'shapeOutside','changeAmendment':lambda x:'a'+tail(x),'changeMeaning':lambda x:'m0' if x!='cOutside' else 'mOutside','amendmentOwner':lambda x:'owner0' if x!='aOutside' else 'ownerOutside','amendmentScope':lambda x:'sharedScope' if x!='aOutside' else 'scopeOutside','amendmentBefore':lambda x:'shape0' if x!='aOutside' else 'shapeOutside','amendmentAfter':lambda x:'shape'+str(int(tail(x))+1) if x!='aOutside' else 'shapeOutside','amendmentSource':lambda x:'source0' if x!='aOutside' else 'sourceOutside','amendmentRollout':lambda x:'rollout'+tail(x) if x in ['a0','a2','a4'] else 'routeOutside','amendmentRollback':lambda x:'rollback'+tail(x) if x in ['a1','a2','a3'] else 'routeOutside','witnessAmendment':lambda x:'a'+tail(x),'witnessKind':lambda x:{'0':'deterministic','1':'hybrid','2':'review','3':'absent','4':'review','Outside':'kindOutside'}[tail(x)],'witnessEvidence':lambda x:'evidence'+tail(x),'witnessResidue':lambda x:'r'+tail(x),'residueOwner':lambda x:'ownerOutside' if x=='rOutside' else 'owner1' if x=='r3' else 'owner0','residueEffect':lambda x:'effectOutside' if x=='rOutside' else 'effect1' if x=='r3' else 'effect0'}
 for n,stem in [('amendmentReason','reason'),('amendmentDelta','delta'),('amendmentCompatibility','compatibility'),('amendmentWitness','w'),('amendmentResidue','r')]:maps[n]=lambda x,stem=stem:stem+tail(x)
 for sort,n in b.HANDLES.items():maps[n]=lambda x:'reference'
 assert set(maps)==set(b.FUNCTIONS)
 funcs={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(ds[z] for z in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};preds={n:[] for n in b.SIGNATURE}
 for sort in b.SORTS:
  if sort not in ['MeaningReference','ShapeChangeReference','Token']:preds[sort+'Declared']=[[x] for x in ds[sort] if not x.endswith('Outside')]
 for n in ['MeaningApplicable','MeaningInScopeDeclared','MeaningCanonicalInstanceDeclared','MeaningInvariantClassifiedDeclared','MeaningD25RelationRecordedDeclared']:preds[n]=[['m0']]
 for n in ['ChangeApplicable','ChangeInScopeDeclared','ChangeRecordedDeclared']:preds[n]=[['c'+str(i)] for i in range(5)]
 preds.update(ChangeAffectsValidationDeclared=[['c0'],['c1'],['c2'],['c4']],ChangeAffectsAuthorityInterpretationDeclared=[['c3']],ChangeGovernsDownstreamDeclared=[['c0'],['c1'],['c2'],['c3']],ChangeEnforcementPathDeclared=[['c0'],['c1'],['c2']],ChangeResiduePathDeclared=[['c3']],ChangeImplementationBackedDeclared=[['c0'],['c1']],ChangeActualAuthority=[['c2']])
 preds.update(AmendmentRecordedDeclared=[['a'+str(i)] for i in range(5)],RolloutNamedDeclared=[['a0'],['a2'],['a4']],RollbackNamedDeclared=[['a1'],['a2'],['a3']])
 for n in ['WitnessRecordedDeclared','WitnessExplanationRecordedDeclared']:preds[n]=[['w'+str(i)] for i in range(5)]
 preds.update(WitnessPresentDeclared=[['w0'],['w1'],['w2'],['w4']],WitnessDeterministicDeclared=[['w0']],WitnessHybridDeclared=[['w1']],WitnessReviewDeclared=[['w2'],['w4']],WitnessAbsentDeclared=[['w3']],WitnessNamesValidatorDeclared=[['w0']],WitnessNamesRuntimeObservationDeclared=[['w1']],WitnessNamesFixtureDeclared=[['w1']],WitnessNamesReviewCheckDeclared=[['w2'],['w4']])
 for n in ['ResidueTypedDeclared','ResidueOwnerAssignedDeclared','ResidueEffectNamedDeclared']:preds[n]=[['r'+str(i)] for i in range(5)]
 m={'domains':ds,'constants':cs,'functions':funcs,'predicates':preds};refresh(m);return m
def controls():
 rows=[]
 def add(name,mutation=lambda m:None,T=True,I=True,error=None):
  m=base_model();mutation(m);rows.append({'case_id':name,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 def change(m,n,arg,value):setfn(m,n,arg,value);refresh(m)
 add('exact-amendment-witness-and-owned-absence-records')
 add('no-selected-changes',lambda m:m['predicates'].update(ChangeApplicable=[],ChangeInScopeDeclared=[]),I=False)
 add('only-first-change-selected',lambda m:m['predicates'].update(ChangeApplicable=[['c0']],ChangeInScopeDeclared=[['c0']]),I=False)
 def none(m):m['predicates'].update(ChangeApplicable=[],ChangeInScopeDeclared=[],MeaningApplicable=[],MeaningInScopeDeclared=[])
 add('no-selected-meaning-or-changes',none,I=False)
 add('independent-authority-not-supplied',lambda m:m['predicates'].update(ChangeActualAuthority=[]),I=False)
 add('all-actual-outcomes-independently-supplied',lambda m:[m['predicates'].update({'ChangeActual'+n:[['c'+str(i)] for i in range(5)]}) for n in b.ACTUAL],I=False)
 for n in b.ACTUAL:add('independently-supported-actual-'+n,lambda m,n=n:m['predicates']['ChangeActual'+n].append(['c0']))
 for n in b.EXCLUDED:
  add('selected-excluded-'+n,lambda m,n=n:m['predicates'][n].append(['c0']),T=False,I=None)
  add('outside-excluded-'+n,lambda m,n=n:m['predicates'][n].append(['cOutside']))
 add('both-validation-and-authority-affecting',lambda m:m['predicates']['ChangeAffectsAuthorityInterpretationDeclared'].append(['c0']))
 add('authority-affecting-only-allowed',lambda m:(m['predicates']['ChangeAffectsValidationDeclared'].remove(['c0']),m['predicates']['ChangeAffectsAuthorityInterpretationDeclared'].append(['c0'])))
 add('selected-without-affecting-either-axis',lambda m:m['predicates']['ChangeAffectsValidationDeclared'].remove(['c0']),T=False,I=None)
 add('selected-without-source-scope',lambda m:m['predicates']['ChangeInScopeDeclared'].remove(['c0']),T=False,I=None)
 add('eligible-scope-not-selected',lambda m:m['predicates']['ChangeApplicable'].remove(['c0']),T=False,I=None)
 for n,arg in [('MeaningInScopeDeclared','m0'),('MeaningCanonicalInstanceDeclared','m0'),('MeaningInvariantClassifiedDeclared','m0'),('MeaningD25RelationRecordedDeclared','m0'),('ChangeRecordedDeclared','c0'),('AmendmentRecordedDeclared','a0'),('WitnessRecordedDeclared','w0'),('WitnessExplanationRecordedDeclared','w0'),('ResidueTypedDeclared','r3'),('ResidueOwnerAssignedDeclared','r3'),('ResidueEffectNamedDeclared','r3')]:add('missing-posture-'+n+'-'+arg,lambda m,n=n,arg=arg:m['predicates'][n].remove([arg]),T=False,I=None)
 for n,val in [('meaningIdentity','identityOther'),('meaningType','schemaType'),('meaningScope','localScope'),('meaningSource','source0')]:add('wrong-normalized-meaning-'+n,lambda m,n=n,val=val:change(m,n,'m0',val),T=False,I=None)
 add('source-meaning-not-declared',lambda m:m['predicates'].update(MeaningApplicable=[],MeaningInScopeDeclared=[]),T=False,I=None)
 add('unchanged-declared-shape',lambda m:change(m,'changeAfter','c0','shape0'),T=False,I=None)
 add('amendment-endpoint-mismatch-before',lambda m:change(m,'amendmentBefore','a0','shape2'),T=False,I=None)
 add('amendment-endpoint-mismatch-after',lambda m:change(m,'amendmentAfter','a0','shape2'),T=False,I=None)
 add('witness-amendment-mismatch',lambda m:change(m,'witnessAmendment','w0','a1'),T=False,I=None)
 add('absent-residue-mismatch',lambda m:change(m,'witnessResidue','w3','r2'),T=False,I=None)
 add('no-rollout-or-rollback-route',lambda m:m['predicates']['RolloutNamedDeclared'].remove(['a0']),T=False,I=None)
 add('absent-witness-with-no-residue-path',lambda m:m['predicates']['ChangeResiduePathDeclared'].remove(['c3']),T=False,I=None)
 add('absent-witness-with-enforcement-claim',lambda m:m['predicates']['ChangeEnforcementPathDeclared'].append(['c3']),T=False,I=None)
 add('absent-witness-with-present-validator-name',lambda m:m['predicates']['WitnessNamesValidatorDeclared'].append(['w3']),T=False,I=None)
 add('downstream-shape-without-enforcement-or-residue',lambda m:m['predicates']['ChangeEnforcementPathDeclared'].remove(['c2']),T=False,I=None)
 def nongoverning(m):m['predicates']['ChangeGovernsDownstreamDeclared'].remove(['c2']);m['predicates']['ChangeEnforcementPathDeclared'].remove(['c2'])
 add('non-governing-present-review-with-no-path',nongoverning)
 add('present-witness-can-also-carry-residue',lambda m:m['predicates']['ChangeResiduePathDeclared'].append(['c0']))
 add('review-witness-implementation-backed-allowed',lambda m:m['predicates']['ChangeImplementationBackedDeclared'].append(['c2']))
 add('review-witness-instead-of-automatic-validator',lambda m:m['predicates']['ChangeImplementationBackedDeclared'].remove(['c0']))
 add('hybrid-one-named-check-cardinality-not-inferred',lambda m:m['predicates']['WitnessNamesRuntimeObservationDeclared'].remove(['w1']),I=False)
 add('multiple-named-checks-inclusive',lambda m:[m['predicates'][n].append(['w0']) for n in b.NAMED if ['w0'] not in m['predicates'][n]])
 add('present-witness-no-named-route',lambda m:m['predicates']['WitnessNamesValidatorDeclared'].remove(['w0']),T=False,I=None)
 add('unknown-selected-witness-kind',lambda m:change(m,'witnessKind','w0','kindOutside'),T=False,I=None)
 add('extra-inconsistent-witness-kind-flag',lambda m:m['predicates']['WitnessReviewDeclared'].append(['w0']),T=False,I=None)
 add('present-flag-missing',lambda m:m['predicates']['WitnessPresentDeclared'].remove(['w0']),T=False,I=None)
 add('unused-residue-owner-posture-not-required',lambda m:m['predicates']['ResidueOwnerAssignedDeclared'].remove(['r0']))
 add('unused-rollback-handle-empty',lambda m:setfn(m,'routeReferenceHandle','routeOutside','empty'))
 def shared(m):
  setfn(m,'changeAmendment','c1','a0');setfn(m,'changeAfter','c1','shape1');refresh(m)
 add('shared-amendment-record-not-forced-unique',shared,I=False)
 targets={id(b.MEANING_FIELDS):'m0',id(b.CHANGE_FIELDS):'c0',id(b.AMENDMENT_FIELDS):'a0',id(b.ROUTE_FIELDS):'a2',id(b.WITNESS_FIELDS):'w0',id(b.PRESENT_FIELDS):'w0',id(b.ABSENT_FIELDS):'w3',id(b.RESIDUE_FIELDS):'r3'}
 for fields,carrier in b.GROUPS:
  arg=targets[id(fields)]
  for n,sort in fields.items():
   add('missing-exact-binding-'+n,lambda m,n=n,arg=arg:m['predicates'].update({n+'BindingDeclared':[x for x in m['predicates'][n+'BindingDeclared'] if x[0]!=arg]}),T=False,I=None)
   alt=next(x for x in base_model()['domains'][sort] if x!=getfn(base_model(),n,arg));add('conflicting-exact-binding-'+n,lambda m,n=n,arg=arg,alt=alt:m['predicates'][n+'BindingDeclared'].append([arg,alt]),T=False,I=None)
   value=getfn(base_model(),n,arg)
   if sort not in ['MeaningReference','ShapeChangeReference']:add('undeclared-selected-target-'+n,lambda m,sort=sort,value=value:m['predicates'][sort+'Declared'].remove([value]),T=False,I=None)
 selected={'MeaningReference':'m0','MeaningIdentity':'identitySEI','TypeReference':'invariantType','ShapeChangeReference':'c0','ShapeReference':'shape0','AmendmentReference':'a0','WitnessReference':'w0','WitnessKind':'deterministic','ResidueReference':'r0','OwnerReference':'owner0','ScopeReference':'sharedScope','SourceReference':'sourceD25','ReasonReference':'reason0','DeltaReference':'delta0','CompatibilityReference':'compatibility0','RouteReference':'rollout0','EffectReference':'effect1','EvidenceReference':'evidence0'}
 for sort,n in b.HANDLES.items():add('empty-selected-handle-'+sort,lambda m,n=n,value=selected[sort]:setfn(m,n,value,'empty'),T=False,I=None)
 add('malformed-empty-domain',lambda m:m['domains'].update(ShapeChangeReference=[]),error='empty-or-malformed-domain')
 add('malformed-missing-domain',lambda m:m['domains'].pop('MeaningReference'),error='model-signature-denominator-mismatch')
 add('malformed-missing-function',lambda m:m['functions'].pop('changeBefore'),error='model-signature-denominator-mismatch')
 add('malformed-partial-function',lambda m:m['functions']['changeBefore'].pop(),error='nontotal-function')
 add('malformed-function-range',lambda m:setfn(m,'changeBefore','c0','foreign'),error='ill-sorted-function-result')
 add('malformed-function-argument',lambda m:m['functions']['changeBefore'][0].update(args=['foreign']),error='ill-sorted-model-tuple')
 add('malformed-predicate-range',lambda m:m['predicates']['ChangeApplicable'].append(['foreign']),error='ill-sorted-model-tuple')
 add('malformed-predicate-arity',lambda m:m['predicates']['amendmentOwnerBindingDeclared'].append(['a0']),error='ill-sorted-model-tuple')
 return rows
def qualify(model,ids):return {bucket:{ids[n]:value for n,value in model[bucket].items()} for bucket in ['domains','constants','functions','predicates']}
'''
old=Path('docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.representation-revision/verify_candidate.py').read_text();tail=old[old.index('def verify(write=False):'):].replace('cal.definition.projection-specification/','cal.definition.representation-revision/').replace('RepresentationRevision','SchemaEvolutionInvariant').replace('Exact declared revision/endpoints,identity/epoch/meaning preservation,changed states/digests,immutable history,explicit evidence/validation/owner/rollback and lineage exclusions checked on supplied models;actual equivalence,hashes,storage,rollback,authority and whole proof remain pending.','Exact normalized invariant,shape-change,amendment,witness alternatives,owned residue and downstream-path declarations checked on supplied models;actual enforcement,execution,owner fidelity,authority and whole proof remain pending.')
s+=tail;ast.parse(s)
with (dest/'verify_candidate.py').open('x') as f:f.write(s)
print('Prepared source-specific SEI models and adversarial mutations.')
