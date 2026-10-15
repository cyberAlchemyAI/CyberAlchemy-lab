from pathlib import Path
import ast
p=Path(__file__).resolve().parent/'prepared';old=Path('docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.artifact-type-registry/verify_candidate.py').read_text();head=old[:old.index('NAMES=')]
model='''NAMES=['Main','Accepted','Expired','Super','Authority','Typed','Outside']
def base_model():
 ds={s:[s+'Value',s+'Outside'] for s in b.SORTS}
 ds.update(RequestReference=['q'+n for n in NAMES],SubjectIntentReference=['subjectMain','subjectTyped','subjectOutside'],ArtifactTypeReference=['typeProposed','typeOutput','typeOutside'],IdentityKey=['key'+n for n in NAMES]+['keySubjectMain','keySubjectTyped','keySubjectOutside','keyTypeProposed','keyTypeOutput','keyTypeOutside'],DependencySetReference=['depsPopulated','depsEmpty','depsOutside'],DependencyReference=['depOne','depOutside'],ComponentReference=['componentDraft','componentOutside'],Token=['empty','none','reference','differentReference'])
 constants={'EMPTY':'empty','NONE':'none'}
 maps={n:(lambda q,s=s:s+'Outside' if q=='qOutside' else s+'Value') for n,s in b.FACETS.items()}
 maps.update(requestSubject=lambda q:'subjectTyped' if q=='qTyped' else 'subjectOutside' if q=='qOutside' else 'subjectMain',requestProposedType=lambda q:'typeOutside' if q=='qOutside' else 'typeProposed',requestDependencies=lambda q:'depsPopulated' if q=='qMain' else 'depsOutside' if q=='qOutside' else 'depsEmpty',requestIdentity=lambda q:'key'+q[1:],subjectIdentity=lambda s:'keySubject'+s[len('subject'):],typeIdentity=lambda t:'keyType'+t[len('type'):],requestAuthorityEffect=lambda q:'none')
 for s,n in b.HANDLES.items():maps[n]=lambda x:'reference'
 assert maps.keys()==b.FUNCTIONS.keys();functions={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(ds[s] for s in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};predicates={n:[] for n in b.SIGNATURE};selected=ds['RequestReference'][:-1]
 for s in b.SORTS:
  if s not in ['RequestReference','Token']:predicates[s+'Declared']=[[x] for x in ds[s] if not x.endswith('Outside')]
 for n in ['RequestApplicable','RequestInScopeDeclared','CandidateIntakeDeclared','IntakeCreationDeclared']:predicates[n]=[[q] for q in selected]
 for n,s in b.FACETS.items():predicates[n+'BindingDeclared']=[[q,maps[n](q)] for q in selected]
 subjects=['subjectMain','subjectTyped'];reg='RegistryReferenceValue';res='ResolutionObservationValue';ana='CompatibilityAnalysisValue'
 predicates.update(ResolutionBindingDeclared=[[res,reg,s] for s in subjects],UnresolvedResultDeclared=[[res]],CompatibilityBindingDeclared=[[ana,s] for s in subjects],ExactReuseRejectedDeclared=[[ana]],DependencySetMemberDeclared=[['depsPopulated','depOne']],RequestDependencyMemberDeclared=[['qMain','depOne']],SubjectAuthoredDeclared=[['subjectTyped']],ExactTypeExistsDeclared=[['subjectTyped']],DraftComponentDeclared=[['qMain','componentDraft']],AttachmentDeclared=[['qMain','componentDraft']],CandidateOutputDeclared=[['qAccepted','typeOutput']],CandidateTypePostureDeclared=[['typeOutput']],RequestAcceptedDeclared=[['qAccepted']],ResolvedDeclared=[['qExpired']],ReplacedDeclared=[['qSuper']],ExpiredDeclared=[['qExpired']],SupersededDeclared=[['qSuper']],RequestActualAuthority=[['qAuthority']])
 return {'domains':ds,'constants':constants,'functions':functions,'predicates':predicates}
def controls():
 rows=[]
 def add(id,mutate,T=True,I=None,error=None):
  m=base_model();mutate(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('complete-intake-with-separated-output-and-terminal-alternatives',lambda m:None,I=True)
 for n in b.ACTUAL:
  if n!='Authority':add('independently-supported-actual-'+n,lambda m,n=n:m['predicates']['RequestActual'+n].append(['qAuthority']),I=True)
 add('selected-empty-request-handle',lambda m:setfn(m,b.HANDLES['RequestReference'],'qMain','empty'),T=False)
 add('outside-empty-request-handle',lambda m:setfn(m,b.HANDLES['RequestReference'],'qOutside','empty'),I=True)
 add('selected-scope-disagreement',lambda m:m['predicates']['RequestInScopeDeclared'].remove(['qMain']),T=False)
 add('selected-candidate-intake-missing',lambda m:m['predicates']['CandidateIntakeDeclared'].remove(['qMain']),T=False)
 for n,s in b.FACETS.items():
  value=next(x['value'] for x in base_model()['functions'][n] if x['args']==['qMain'])
  add('missing-facet-declaration-'+n,lambda m,s=s,value=value:m['predicates'][s+'Declared'].remove([value]),T=False)
  add('empty-facet-handle-'+n,lambda m,s=s,value=value:setfn(m,b.HANDLES[s],value,'empty'),T=False)
  add('missing-exact-binding-'+n,lambda m,n=n,value=value:m['predicates'][n+'BindingDeclared'].remove(['qMain',value]),T=False)
  alternate=next(x for x in base_model()['domains'][s] if x!=value)
  add('conflicting-extra-binding-'+n,lambda m,n=n,alternate=alternate:m['predicates'][n+'BindingDeclared'].append(['qMain',alternate]),T=False)
 for n,arg in [('requestIdentity','qMain'),('subjectIdentity','subjectMain'),('typeIdentity','typeProposed')]:
  add('identity-key-empty-'+n,lambda m,n=n,arg=arg:setfn(m,b.HANDLES['IdentityKey'],next(x['value'] for x in m['functions'][n] if x['args']==[arg]),'empty'),T=False)
 add('request-collapses-with-subject',lambda m:setfn(m,'requestIdentity','qMain','keySubjectMain'),T=False)
 add('request-collapses-with-proposed-type',lambda m:setfn(m,'requestIdentity','qMain','keyTypeProposed'),T=False)
 add('shared-request-identity-alias-policy-unresolved',lambda m:setfn(m,'requestIdentity','qTyped','keyMain'),I=True)
 add('creation-declaration-missing',lambda m:m['predicates']['IntakeCreationDeclared'].remove(['qMain']),T=False)
 add('resolution-observation-binding-missing',lambda m:m['predicates']['ResolutionBindingDeclared'].remove(['ResolutionObservationValue','RegistryReferenceValue','subjectMain']),T=False)
 add('unresolved-result-missing',lambda m:m['predicates']['UnresolvedResultDeclared'].clear(),T=False)
 add('compatibility-subject-binding-missing',lambda m:m['predicates']['CompatibilityBindingDeclared'].remove(['CompatibilityAnalysisValue','subjectMain']),T=False)
 add('rejected-exact-reuse-missing',lambda m:m['predicates']['ExactReuseRejectedDeclared'].clear(),T=False)
 add('eligible-current-match-disqualifies-intake',lambda m:m['predicates']['AdmittedCurrentMatchDeclared'].append(['RegistryReferenceValue','DiscriminatorPathValue','DiscriminatorValueValue','typeProposed']),T=False)
 add('unrelated-registry-match-permitted',lambda m:m['predicates']['AdmittedCurrentMatchDeclared'].append(['RegistryReferenceOutside','DiscriminatorPathValue','DiscriminatorValueValue','typeProposed']),I=True)
 add('unrelated-discriminator-match-permitted',lambda m:m['predicates']['AdmittedCurrentMatchDeclared'].append(['RegistryReferenceValue','DiscriminatorPathOutside','DiscriminatorValueValue','typeProposed']),I=True)
 def change_registry(m):
  setfn(m,'requestRegistry','qMain','RegistryReferenceOutside');m['predicates']['RegistryReferenceDeclared'].append(['RegistryReferenceOutside']);next(x for x in m['predicates']['requestRegistryBindingDeclared'] if x[0]=='qMain')[1]='RegistryReferenceOutside'
 add('changed-registry-without-matching-observation',change_registry,T=False)
 add('declared-authority-effect',lambda m:setfn(m,'requestAuthorityEffect','qMain','reference'),T=False)
 add('none-collapses-with-empty',lambda m:m['constants'].update(NONE='empty'),T=False)
 for n in ['ConsumedAsSubjectDeclared','AdmissionRequestDeclared','SelfRegistrationDeclared','SelfAdmissionDeclared','ConvenienceWideningDeclared']:add('forbidden-'+n,lambda m,n=n:m['predicates'][n].append(['qMain']),T=False)
 add('request-satisfies-subject-dependency',lambda m:m['predicates']['SatisfiesSubjectDependencyDeclared'].append(['qMain','subjectMain','depOne']),T=False)
 add('dependency-for-unrelated-subject-permitted',lambda m:m['predicates']['SatisfiesSubjectDependencyDeclared'].append(['qMain','subjectOutside','depOne']),I=True)
 add('subject-authored-before-exact-type-exists',lambda m:m['predicates']['SubjectAuthoredDeclared'].append(['subjectMain']),T=False)
 add('exact-type-exists-declaration-missing',lambda m:m['predicates']['ExactTypeExistsDeclared'].clear(),T=False)
 add('unused-exact-type-exists-is-not-admission',lambda m:m['predicates']['ExactTypeExistsDeclared'].append(['subjectMain']),I=True)
 add('draft-component-no-attachment',lambda m:m['predicates']['AttachmentDeclared'].clear(),T=False)
 add('draft-component-is-admitted-contract',lambda m:m['predicates']['AdmittedContractComponentDeclared'].append(['componentDraft']),T=False)
 add('unrelated-component-admission-marker-permitted',lambda m:m['predicates']['AdmittedContractComponentDeclared'].append(['componentOutside']),I=True)
 add('draft-component-marker-missing-population-loss',lambda m:m['predicates']['DraftComponentDeclared'].clear(),I=False)
 add('accepted-request-without-candidate-output',lambda m:m['predicates']['CandidateOutputDeclared'].clear(),T=False)
 add('candidate-output-lacks-candidate-posture',lambda m:m['predicates']['CandidateTypePostureDeclared'].clear(),T=False)
 add('candidate-output-claims-admission',lambda m:m['predicates']['TypeAdmittedDeclared'].append(['typeOutput']),T=False)
 add('output-collapses-with-request',lambda m:setfn(m,'typeIdentity','typeOutput','keyAccepted'),T=False)
 add('output-collapses-with-intended-subject',lambda m:setfn(m,'typeIdentity','typeOutput','keySubjectMain'),T=False)
 def extra_output(m):
  m['predicates']['CandidateOutputDeclared'].append(['qAccepted','typeProposed']);m['predicates']['CandidateTypePostureDeclared'].append(['typeProposed'])
 add('multiple-separate-candidate-outputs-permitted',extra_output,I=True)
 add('request-not-accepted-population-loss',lambda m:m['predicates']['RequestAcceptedDeclared'].clear(),I=False)
 add('resolved-without-expiry-or-supersession',lambda m:m['predicates']['ExpiredDeclared'].clear(),T=False)
 add('replaced-without-expiry-or-supersession',lambda m:m['predicates']['SupersededDeclared'].clear(),T=False)
 add('rejected-without-expiry-or-supersession',lambda m:m['predicates']['RejectedDeclared'].append(['qMain']),T=False)
 add('terminal-can-have-both-expiry-and-supersession',lambda m:m['predicates']['SupersededDeclared'].append(['qExpired']),I=False)
 add('unterminated-expiry-marker-no-chronology-invented',lambda m:m['predicates']['ExpiredDeclared'].append(['qMain']),I=True)
 add('owner-treatment-selection-declaration-not-real-selection',lambda m:m['predicates']['OwnerTreatmentSelectedDeclared'].append(['qMain']),I=True)
 add('missing-exact-dependency-member',lambda m:m['predicates']['RequestDependencyMemberDeclared'].clear(),T=False)
 add('extra-unbound-dependency-member',lambda m:m['predicates']['RequestDependencyMemberDeclared'].append(['qAccepted','depOne']),T=False)
 add('dependency-reference-not-declared',lambda m:m['predicates']['DependencyReferenceDeclared'].clear(),T=False)
 add('outside-request-forbidden-marker-unconstrained',lambda m:m['predicates']['ConsumedAsSubjectDeclared'].append(['qOutside']),I=True)
 add('wrong-facet-result-sort',lambda m:setfn(m,'requestSubject','qMain','typeProposed'),error='ill-sorted-function-result')
 add('missing-signature-symbol',lambda m:m['predicates'].pop('CandidateOutputDeclared'),error='model-signature-denominator-mismatch')
 add('nontotal-request-selector',lambda m:m['functions']['requestRegistry'].pop(),error='nontotal-function')
 add('ill-sorted-none-constant',lambda m:m['constants'].update(NONE='qMain'),error='ill-sorted-constant')
 add('wrong-resolution-binding-arity',lambda m:m['predicates'].update(ResolutionBindingDeclared=[['ResolutionObservationValue','RegistryReferenceValue']]),error='ill-sorted-model-tuple')
 add('duplicate-request-binding',lambda m:m['predicates']['requestSubjectBindingDeclared'].append(['qMain','subjectMain']),error='duplicate-predicate-tuple')
 add('empty-component-domain',lambda m:m['domains'].update(ComponentReference=[]),error='empty-or-malformed-domain')
 add('duplicate-selector-function-tuple',lambda m:m['functions']['requestRegistry'].append(copy.deepcopy(m['functions']['requestRegistry'][0])),error='duplicate-function-tuple')
 return rows
'''
tail=old[old.index('def qualify('):];tail=tail.replace('cal.definition.artifact-surface-classification/delivery-manifest.json','cal.definition.artifact-type-registry/delivery-manifest.json').replace('ArtifactTypeRegistry','ArtifactTypeRequest').replace('Typed exact Registry entry bindings,reference-only declarations,decision overlays,historical visibility and at-most-one current discriminator results checked on supplied models. Actual bytes,selector validity,decision authority,admission,resolution,owner fidelity and consumer alignment remain pending.','Typed unmatched Request declarations,exact field and identity bindings,zero matches,separate candidate output and terminal alternatives checked on supplied models. Actual resolver execution,compatibility correctness,owner selection,subject authorship,admission,consumer alignment and whole fidelity remain pending.')
code=head+model+tail;ast.parse(code)
with (p/'verify_candidate.py').open('x') as f:f.write(code)
print('Prepared Request models and controls; no native unit created.')
