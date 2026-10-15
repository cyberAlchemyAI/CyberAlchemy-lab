from pathlib import Path
root=Path.cwd();a=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.artifact';p=Path('/tmp/cal-artifact-lifetime-types-first-20261011/prepared')
body='''"""Supplied lifespan,owner-note and scoped assertion-record models."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def setfn(m,n,arg,value):
 args=arg if isinstance(arg,list) else [arg];next(x for x in m['functions'][n] if x['args']==args)['value']=value
def base_model():
 ds={s:[s.lower()+'A',s.lower()+'Outside'] for s in b.SORTS};ds.update(LifetimeAssignment=['aEExpl','aEQuiet','aPQuoted','aPTemporal','aOverride','aEAuthority','aPAuthority','aOutside'],ArtifactReference=['f'+n[1:] for n in ['aEExpl','aEQuiet','aPQuoted','aPTemporal','aOverride','aEAuthority','aPAuthority','aOutside']],CanonicalKind=['kE','kP','kOutside'],Durability=['dE','dP','dOutside'],OwnerNoteReference=['nOverride','nAbsent','nOutside'],AssertionRecord=['rEPos','rENeg','rQPos','rQNeg','rOld','rNew','rOutside'],AssertionSign=['positive','negative','signOutside'],AssertionUse=['live','historical','quoted','useOutside'],TimePoint=['tOld','tNow','tOutside'],SupersessionDeclarationReference=['sTemporal','sOutside'],Token=['empty','reference'])
 constants={'EMPTY':'empty','EPHEMERAL':'dE','PERENNIAL':'dP','POSITIVE':'positive','NEGATIVE':'negative','LIVE':'live','HISTORICAL':'historical','QUOTED':'quoted'};selected=ds['LifetimeAssignment'][:-1];maps={}
 for n,s in b.FIELDS.items():maps[n]=lambda a,s=s:ds[s][-1] if a=='aOutside' else ds[s][0]
 maps.update(assignmentArtifact=lambda a:'f'+a[1:],assignmentKind=lambda a:'kOutside' if a=='aOutside' else 'kP' if a in ['aPQuoted','aPTemporal','aOverride','aPAuthority'] else 'kE',assignmentDurability=lambda a:'dOutside' if a=='aOutside' else 'dP' if a in ['aPQuoted','aPTemporal','aPAuthority'] else 'dE',kindDefaultDurability=lambda k:'dP' if k=='kP' else 'dE' if k=='kE' else 'dOutside',assignmentOwnerNote=lambda a:'nOverride' if a=='aOverride' else 'nAbsent',noteArtifact=lambda n:'fOverride' if n=='nOverride' else 'fOutside',noteOwner=lambda n:ds['OwnerReference'][0],noteDurability=lambda n:'dE',recordArtifact=lambda r:'fEExpl' if r in ['rEPos','rENeg'] else 'fPQuoted' if r in ['rQPos','rQNeg'] else 'fPTemporal' if r in ['rOld','rNew'] else 'fOutside',recordProposition=lambda r:ds['PropositionReference'][0],recordSign=lambda r:'negative' if r in ['rENeg','rQNeg','rNew'] else 'positive',recordUse=lambda r:'quoted' if r in ['rQPos','rQNeg'] else 'historical' if r=='rOld' else 'live',recordTime=lambda r:'tOld' if r=='rOld' else 'tNow',recordContext=lambda r:ds['Context'][0],supersessionArtifact=lambda s:'fPTemporal',supersessionOld=lambda s:'rOld',supersessionNew=lambda s:'rNew',supersessionOrder=lambda s:ds['TemporalOrderReference'][0])
 for s,n in b.HANDLES.items():maps[n]=lambda x:'reference'
 assert maps.keys()==b.FUNCTIONS.keys();functions={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(ds[s] for s in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};predicates={n:[] for n in b.SIGNATURE}
 for n in ['LifetimeApplicable','LifetimeInScopeDeclared','LifetimeFacetsExplicitDeclared','IntendedLifespanDeclared']:predicates[n]=[[a] for a in selected]
 for s in b.SORTS:
  if s not in ['LifetimeAssignment','Token']:predicates[s+'Declared']=[[x] for x in ds[s][:-1]]
 predicates.update(CanonicalArtifactApplicabilityDeclared=[[x] for x in ds['ArtifactReference'][:-1]],KindDefaultDurabilityDeclared=[['kE'],['kP']],OwnerNotedOverrideDeclared=[['nOverride']],AssertionRecordInScopeDeclared=[[r] for r in ds['AssertionRecord'][:-1]],SupersessionInScopeDeclared=[['sTemporal']],ScopedEarlierDeclared=[['tOld','tNow',ds['TemporalOrderReference'][0]]],LifetimeActualAuthority=[['aEAuthority'],['aPAuthority']])
 return {'domains':ds,'constants':constants,'functions':functions,'predicates':predicates}
def controls():
 rows=[]
 def add(id,mutate,T=True,I=None,error=None):
  m=base_model();mutate(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('lifespan-default-override-orthogonality-live-and-temporal-witnesses',lambda m:None,I=True)
 for n in b.ACTUAL:
  def independent(m,n=n):
   if ['aEAuthority'] not in m['predicates']['LifetimeActual'+n]:m['predicates']['LifetimeActual'+n].append(['aEAuthority'])
  add('independently-supported-actual-'+n,independent,I=True)
 for n,s in b.FIELDS.items():
  value=next(x['value'] for x in base_model()['functions'][n] if x['args']==['aEExpl'])
  add('missing-lifespan-facet-'+n,lambda m,s=s,value=value:m['predicates'][s+'Declared'].remove([value]),T=False)
  add('empty-lifespan-facet-'+n,lambda m,s=s,value=value:setfn(m,b.HANDLES[s],value,'empty'),T=False)
 add('selected-empty-assignment-handle',lambda m:setfn(m,b.HANDLES['LifetimeAssignment'],'aEExpl','empty'),T=False)
 add('outside-empty-assignment-handle',lambda m:setfn(m,b.HANDLES['LifetimeAssignment'],'aOutside','empty'),I=True)
 add('selected-scope-disagreement',lambda m:m['predicates']['LifetimeInScopeDeclared'].remove(['aEExpl']),T=False)
 add('lifespan-facets-not-explicit',lambda m:m['predicates']['LifetimeFacetsExplicitDeclared'].remove(['aEExpl']),T=False)
 add('canonical-applicability-not-declared',lambda m:m['predicates']['CanonicalArtifactApplicabilityDeclared'].remove(['fEExpl']),T=False)
 add('intended-lifespan-not-declared',lambda m:m['predicates']['IntendedLifespanDeclared'].remove(['aEExpl']),T=False)
 add('kind-default-not-declared',lambda m:m['predicates']['KindDefaultDurabilityDeclared'].remove(['kP']),T=False)
 add('kind-default-unknown-tag',lambda m:setfn(m,'kindDefaultDurability','kP','dOutside'),T=False)
 add('effective-unknown-tag',lambda m:setfn(m,'assignmentDurability','aOverride','dOutside'),T=False)
 add('current-two-value-set-cannot-grow-by-declaration',lambda m:m['predicates']['DurabilityDeclared'].append(['dOutside']),T=False)
 add('durability-constants-must-differ',lambda m:m['constants'].update(PERENNIAL='dE'),T=False)
 add('selected-override-note-not-declared',lambda m:m['predicates']['OwnerNotedOverrideDeclared'].clear(),T=False)
 add('selected-override-reference-not-declared',lambda m:m['predicates']['OwnerNoteReferenceDeclared'].remove(['nOverride']),T=False)
 add('selected-override-note-empty',lambda m:setfn(m,b.HANDLES['OwnerNoteReference'],'nOverride','empty'),T=False)
 for n,value in [('noteArtifact','fEExpl'),('noteOwner',base_model()['domains']['OwnerReference'][-1]),('noteDurability','dP')]:add('changed-owner-note-binding-'+n,lambda m,n=n,value=value:setfn(m,n,'nOverride',value),T=False)
 add('default-branch-needs-no-override-note',lambda m:setfn(m,'assignmentOwnerNote','aEQuiet','nOutside'),I=True)
 add('no-owner-note-for-effective-change',lambda m:setfn(m,'assignmentDurability','aPQuoted','dE'),T=False)
 add('unselected-kind-default-is-unconstrained',lambda m:setfn(m,'kindDefaultDurability','kOutside','dP'),I=True)
 for n,s in b.RECORD_FIELDS.items():
  value=next(x['value'] for x in base_model()['functions'][n] if x['args']==['rEPos'])
  add('missing-assertion-field-'+n,lambda m,s=s,value=value:m['predicates'][s+'Declared'].remove([value]),T=False)
  add('empty-assertion-field-'+n,lambda m,s=s,value=value:setfn(m,b.HANDLES[s],value,'empty'),T=False)
 add('selected-record-reference-not-declared',lambda m:m['predicates']['AssertionRecordDeclared'].remove(['rEPos']),T=False)
 add('unknown-assertion-use',lambda m:setfn(m,'recordUse','rEPos','useOutside'),T=False)
 add('unknown-assertion-sign',lambda m:setfn(m,'recordSign','rEPos','signOutside'),T=False)
 add('positive-negative-tags-cannot-collapse',lambda m:m['constants'].update(NEGATIVE='positive'),T=False)
 add('live-historical-tags-cannot-collapse',lambda m:m['constants'].update(HISTORICAL='live'),T=False)
 def quote_live(m):
  setfn(m,'recordUse','rQPos','live');setfn(m,'recordUse','rQNeg','live')
 add('perennial-live-simultaneous-opposition-is-rejected',quote_live,T=False)
 def separate_time(m):quote_live(m);setfn(m,'recordTime','rQPos','tOld')
 add('different-time-is-not-simultaneous-opposition',separate_time)
 def separate_context(m):
  quote_live(m);extra=m['domains']['Context'][-1];m['predicates']['ContextDeclared'].append([extra]);setfn(m,'recordContext','rQPos',extra)
 add('different-context-is-not-scoped-opposition',separate_context)
 def different_proposition(m):
  quote_live(m);extra=m['domains']['PropositionReference'][-1];m['predicates']['PropositionReferenceDeclared'].append([extra]);setfn(m,'recordProposition','rQPos',extra)
 add('different-proposition-is-not-opposition',different_proposition)
 add('ephemeral-opposition-is-permitted-without-classical-truth-collision',lambda m:None,I=True)
 add('ephemeral-without-opposition-is-also-permitted',lambda m:setfn(m,'recordUse','rENeg','historical'),I=False)
 add('quoted-opposed-records-are-permitted-for-perennial',lambda m:None,I=True)
 add('historical-opposition-remains-distinct-from-live',lambda m:setfn(m,'recordSign','rOld','negative'),I=False)
 add('assertion-record-outside-guards-may-have-empty-handle',lambda m:setfn(m,b.HANDLES['AssertionRecord'],'rOutside','empty'),I=True)
 add('supersession-ref-not-declared',lambda m:m['predicates']['SupersessionDeclarationReferenceDeclared'].clear(),T=False)
 add('supersession-order-ref-not-declared',lambda m:m['predicates']['TemporalOrderReferenceDeclared'].clear(),T=False)
 add('supersession-order-not-explicit',lambda m:m['predicates']['ScopedEarlierDeclared'].clear(),T=False)
 add('supersession-old-is-new',lambda m:setfn(m,'supersessionOld','sTemporal','rNew'),T=False)
 add('supersession-old-still-live',lambda m:setfn(m,'recordUse','rOld','live'),T=False)
 add('supersession-old-quoted-is-not-retired-history',lambda m:setfn(m,'recordUse','rOld','quoted'),T=False)
 add('supersession-new-quoted-is-not-replacement-assertion',lambda m:setfn(m,'recordUse','rNew','quoted'),T=False)
 add('supersession-unbound-subject',lambda m:setfn(m,'supersessionArtifact','sTemporal','fEQuiet'),T=False)
 add('supersession-old-other-artifact',lambda m:setfn(m,'recordArtifact','rOld','fEQuiet'),T=False)
 add('supersession-new-other-artifact',lambda m:setfn(m,'recordArtifact','rNew','fEQuiet'),T=False)
 add('supersession-same-time',lambda m:setfn(m,'recordTime','rOld','tNow'),T=False)
 for n,s in [('recordProposition','PropositionReference'),('recordContext','Context')]:
  def changed(m,n=n,s=s):extra=m['domains'][s][-1];m['predicates'][s+'Declared'].append([extra]);setfn(m,n,'rOld',extra)
  add('supersession-changed-'+n,changed,T=False)
 add('supersession-new-may-later-be-historical',lambda m:setfn(m,'recordUse','rNew','historical'),I=False)
 add('no-global-order-or-transitivity-is-inferred',lambda m:m['predicates']['ScopedEarlierDeclared'].append(['tNow','tOld',m['domains']['TemporalOrderReference'][0]]),I=True)
 add('durability-result-is-authority-kind',lambda m:setfn(m,'assignmentDurability','aEExpl',m['domains']['AuthorityKind'][0]),error='ill-sorted-function-result')
 add('missing-symbol',lambda m:m['predicates'].pop('LifetimeApplicable'),error='model-signature-denominator-mismatch')
 add('nontotal-function',lambda m:m['functions']['assignmentArtifact'].pop(),error='nontotal-function')
 add('ill-sorted-constant',lambda m:m['constants'].update(EPHEMERAL='aEExpl'),error='ill-sorted-constant')
 add('wrong-temporal-relation-arity',lambda m:m['predicates'].update(ScopedEarlierDeclared=[['tOld','tNow']]),error='ill-sorted-model-tuple')
 add('duplicate-selected-tuple',lambda m:m['predicates']['LifetimeApplicable'].append(['aEExpl']),error='duplicate-predicate-tuple')
 add('empty-context-domain',lambda m:m['domains'].update(Context=[]),error='empty-or-malformed-domain')
 add('duplicate-function-tuple',lambda m:m['functions']['assignmentArtifact'].append(copy.deepcopy(m['functions']['assignmentArtifact'][0])),error='duplicate-function-tuple')
 return rows
'''
tail=(a/'verify_candidate.py').read_text().split('def qualify(model,ids):',1)[1]
tail='def qualify(model,ids):'+tail
for x,y in [('cal.definition.validation/delivery-manifest.json','cal.definition.artifact/delivery-manifest.json'),('Artifact-model-controls','ArtifactLifetime-model-controls'),('authored-Artifact-models','authored-ArtifactLifetime-models')]:tail=tail.replace(x,y)
tail=tail.replace('Typed record facets,exact declared origin tuples,kind-derived classification and separately supported assurance declarations checked on supplied models. Actual execution,truth,verification,authority,owner fidelity and consumer alignment remain pending.','Typed lifespan,kind defaults,owner-noted overrides and scoped live,historical,quoted assertion declarations checked on supplied models. Actual preservation,truth,chronology,override authority,owner fidelity and consumer alignment remain pending.')
(p/'verify_candidate.py').write_text(body+tail)
